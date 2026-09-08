import { readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';

const base = 'https://shunshou.miaowu.org';
const token = readFileSync(new URL('../shortcuts/private-access-code.txt', import.meta.url), 'utf8').trim();
const results = [];
function request(path, { auth = true, body, method } = {}) {
  const args = ['-sS', '--connect-timeout', '10', '--max-time', '55', '--config', '-', '-w', '\n%{http_code}', base + path];
  if (method) args.push('-X', method);
  if (body !== undefined) args.push('-H', 'Content-Type: application/json', '--data-binary', typeof body === 'string' ? body : JSON.stringify(body));
  const output = execFileSync('curl', args, {
    input: auth ? `header = ${JSON.stringify(`Authorization: Bearer ${token}`)}\n` : '',
    maxBuffer: 2 * 1024 * 1024,
  });
  const split = output.lastIndexOf(10);
  return { status: Number(output.subarray(split + 1).toString()), body: output.subarray(0, split) };
}
function check(name, run) {
  try { results.push({ name, ...run() }); }
  catch { results.push({ name, passed: false, error: 'Transport or response validation failed' }); }
  console.log(JSON.stringify(results.at(-1)));
}
check('public homepage', () => {
  const r = request('/', { auth: false });
  const html = r.body.toString();
  return { status: r.status, passed: r.status === 200 && html.includes('安装快捷指令') && html.includes('href="/shunshou.shortcut"') && !html.includes(token) };
});
for (const [name, path, options, expected] of [
  ['health without token', '/api/health', { auth: false }, 401],
  ['health authorized', '/api/health', {}, 200],
  ['resolve without token', '/api/resolve', { auth: false, body: {} }, 401],
  ['missing URL', '/api/resolve', { body: {} }, 400],
  ['invalid JSON', '/api/resolve', { body: '{' }, 400],
  ['SSRF rejection', '/api/resolve', { body: { url: 'http://127.0.0.1/' } }, 400],
  ['oversized body', '/api/resolve', { body: 'x'.repeat(4097) }, 413],
  ['method guard', '/api/resolve', { method: 'GET' }, 405],
  ['private file not public', '/.env.production.local', { auth: false }, 404],
]) check(name, () => { const r = request(path, options); return { status: r.status, passed: r.status === expected }; });
for (const id of ['DZsVvmmkqXA', 'DZwITAaBfBE']) check(`Reel ${id}`, () => {
  const r = request('/api/resolve', { body: { url: `https://www.instagram.com/reel/${id}/`, quality: '720p' } });
  const data = JSON.parse(r.body);
  const items = data.items || [];
  const safe = items.length > 0 && items.every(item => {
    const u = new URL(item.url);
    return u.protocol === 'https:' && !u.username && !u.password && /\.(cdninstagram\.com|fbcdn\.net)$/.test(u.hostname)
      && item.mimeType === 'video/mp4' && !JSON.stringify(item.downloadHeaders).includes(token);
  });
  return { status: r.status, code: data.code, itemCount: items.length, passed: r.status === 200 && data.status === 'ok' && safe };
});
for (const name of ['shunshou', 'shunshou-check']) check(`signed shortcut ${name}`, () => {
  const r = request(`/${name}.shortcut`, { auth: false });
  const local = readFileSync(new URL('../shortcuts/build/shunshou.shortcut', import.meta.url));
  const unsigned = readFileSync(new URL('../shortcuts/build/shunshou.unsigned.shortcut', import.meta.url), 'utf8');
  const hash = value => createHash('sha256').update(value).digest('hex');
  return { status: r.status, bytes: r.body.length, passed: r.status === 200 && hash(r.body) === hash(local) && unsigned.includes(base) && !unsigned.includes(token) };
});
const report = { checkedAt: new Date().toISOString(), base, commit: execFileSync('git', ['rev-parse', 'HEAD'], { encoding: 'utf8' }).trim(),
  passed: results.every(r => r.passed), results, deviceAcceptance: 'Pending actual iPhone installation, CDN download and WeChat playback' };
writeFileSync(new URL('./production-acceptance.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
if (!report.passed) process.exitCode = 1;
