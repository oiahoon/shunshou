import { readFileSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const cwd = fileURLToPath(new URL('../services/resolver/', import.meta.url));
const token = readFileSync(`${cwd}.env.production.local`, 'utf8').trim().split('=')[1];
const base = 'https://shunshou-resolver.vercel.app';
const r = spawnSync(`${cwd}.venv/bin/python`, ['smoke.py'], {
  cwd, env:{...process.env,SMOKE_API_TOKEN:token,RESOLVER_BASE_URL:base,SMOKE_HEALTH:'1',SMOKE_PROXY:'http://127.0.0.1:7897',SMOKE_PROBE:'1',RESOLVER_PROXY:'http://127.0.0.1:7897'},
  encoding:'utf8',timeout:150000,
});
process.stdout.write(r.stdout ?? '');
if(r.status !== 0) { console.error('Cloud verification client failed.'); process.exit(1); }
