import { randomBytes } from 'node:crypto';
import { existsSync, writeFileSync, readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const cwd = fileURLToPath(new URL('../services/resolver/', import.meta.url));
const path = `${cwd}.env.production.local`;
if (!existsSync(path)) {
  writeFileSync(path, `API_TOKENS=${randomBytes(32).toString('hex')}\n`, { mode: 0o600 });
}
if (process.argv.includes('--access-file')) {
  const token = readFileSync(path, 'utf8').trim().split('=')[1];
  writeFileSync(fileURLToPath(new URL('../shortcuts/private-access-code.txt', import.meta.url)), `${token}\n`, {mode:0o600});
  console.log('Private access-code file prepared; do not publish it.');
}
if (process.argv.includes('--upload')) {
  const token = readFileSync(path, 'utf8').trim().split('=')[1];
  const result = spawnSync('vercel', ['env', 'add', 'API_TOKENS', 'production', '--sensitive', '--scope', 'joey-huangs-projects'], {
    cwd, input: token, encoding: 'utf8', stdio: ['pipe', 'pipe', 'pipe'],
  });
  process.stdout.write(result.stdout.replaceAll(token, '[redacted]'));
  process.stderr.write(result.stderr.replaceAll(token, '[redacted]'));
  process.exitCode = result.status ?? 1;
} else {
  console.log('Private token prepared locally; value not printed.');
}
