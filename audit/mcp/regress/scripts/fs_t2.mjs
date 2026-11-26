import { validatePath } from './package/dist/lib.js';
const root = process.cwd();
const A = [root + '/sandbox/allowed'];
const cases = [
  ['legit',           root + '/sandbox/allowed/ok.txt'],
  ['dotdot-escape',   root + '/sandbox/allowed/../../etc/passwd'],
  ['symlink-dir-etc', root + '/sandbox/allowed/etc/passwd'],
  ['symlink-file-tmp',root + '/sandbox/allowed/secret'],
  ['inner-symlink',   root + '/sandbox/allowed/inner'],
  ['new-file',        root + '/sandbox/allowed/new.txt'],
  ['proc-self-env',   '/proc/self/environ'],
];
for (const [name, p] of cases) {
  try { const r = await validatePath(p, A, 'read'); console.log(name.padEnd(18), 'ALLOWED ->', r.replace(root,'.')); }
  catch (e) { console.log(name.padEnd(18), 'DENIED  ->', String(e.message).slice(0,95)); }
}
