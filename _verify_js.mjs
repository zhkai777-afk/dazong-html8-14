import fs from 'fs';
import vm from 'vm';
import path from 'path';

const dir = decodeURIComponent(path.dirname(new URL(import.meta.url).pathname));
const files = [
  'step-01-project-setup.html',
  'step-02-timeline.html',
  'step-03-arrival-ullage.html',
  'step-04-shore-tank.html',
  'step-05-rob.html',
  'step-06-vef.html',
  'step-07-comparison.html',
  'step-08-reports.html',
];

let allOk = true;

for (const f of files) {
  const full = path.join(dir, f);
  const html = fs.readFileSync(full, 'utf8');
  // Extract every <script>...</script> block (non-module, inline)
  const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  let blockIdx = 0;
  let fileOk = true;
  let found = 0;
  while ((m = re.exec(html)) !== null) {
    blockIdx++;
    const code = m[1];
    if (!code.trim()) {
      console.log(`  [${f}] script block #${blockIdx}: EMPTY (skipped)`);
      continue;
    }
    found++;
    try {
      // compile-only: throws on syntax error, does not execute (no DOM needed)
      new vm.Script(code, { filename: `${f}#${blockIdx}` });
      console.log(`  [${f}] script block #${blockIdx}: OK (${code.length} chars)`);
    } catch (e) {
      fileOk = false;
      allOk = false;
      console.log(`  [${f}] script block #${blockIdx}: SYNTAX ERROR -> ${e.message}`);
    }
  }
  if (found === 0) {
    console.log(`  [${f}] NO inline script blocks found`);
  }
  if (!fileOk) console.log(`>>> ${f} FAILED`);
}

console.log('\n=== RESULT: ' + (allOk ? 'ALL JS SYNTAX OK' : 'SYNTAX ERRORS FOUND') + ' ===');
process.exit(allOk ? 0 : 1);
