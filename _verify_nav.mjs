import fs from 'fs';
import path from 'path';

const dir = decodeURIComponent(path.dirname(new URL(import.meta.url).pathname));

// Expected: file -> { step, progress, nextFile, prevFile }
const expect = {
  'step-01-project-setup.html': { step: 1, progress: 13, next: 'step-02-timeline.html', prev: 'step-08-reports.html' },
  'step-02-timeline.html':      { step: 2, progress: 43, next: 'step-03-arrival-ullage.html', prev: 'step-01-project-setup.html' },
  'step-03-arrival-ullage.html':{ step: 3, progress: 50, next: 'step-04-shore-tank.html', prev: 'step-02-timeline.html' },
  'step-04-shore-tank.html':    { step: 4, progress: 60, next: 'step-05-rob.html', prev: 'step-03-arrival-ullage.html' },
  'step-05-rob.html':           { step: 5, progress: 69, next: 'step-06-vef.html', prev: 'step-04-shore-tank.html' },
  'step-06-vef.html':           { step: 6, progress: 81, next: 'step-07-comparison.html', prev: 'step-05-rob.html' },
  'step-07-comparison.html':    { step: 7, progress: 88, next: 'step-08-reports.html', prev: 'step-06-vef.html' },
  'step-08-reports.html':       { step: 8, progress: 100, next: 'step-01-project-setup.html', prev: 'step-07-comparison.html' },
};

let ok = true;

for (const [file, exp] of Object.entries(expect)) {
  const html = fs.readFileSync(path.join(dir, file), 'utf8');
  const issues = [];

  // 1. active step in workflow list
  const activeRe = /<li[^>]*class="[^"]*active[^"]*"[^>]*>\s*<a\s+href="([^"]+)"/i;
  const am = html.match(activeRe);
  if (!am) {
    issues.push('no active workflow item found');
  } else {
    const activeHref = am[1].split('/').pop();
    // map href to step number via known filenames
    const hrefToStep = {
      'step-01-project-setup.html':1,'step-02-timeline.html':2,'step-03-arrival-ullage.html':3,
      'step-04-shore-tank.html':4,'step-05-rob.html':5,'step-06-vef.html':6,
      'step-07-comparison.html':7,'step-08-reports.html':8,
    };
    const activeStep = hrefToStep[activeHref];
    if (activeStep !== exp.step) issues.push(`active step=${activeStep} expected ${exp.step}`);
  }

  // 2. progress bar width (read from aria-label to avoid matching CSS width:100%)
  const pm = html.match(/aria-label="整体完成度 (\d+)%"/);
  if (pm) {
    const pct = parseInt(pm[1], 10);
    if (pct !== exp.progress) issues.push(`progress=${pct}% expected ${exp.progress}%`);
  } else {
    issues.push('progress value not found');
  }

  // 3. all 8 nav links present
  const navFiles = ['step-01-project-setup.html','step-02-timeline.html','step-03-arrival-ullage.html',
    'step-04-shore-tank.html','step-05-rob.html','step-06-vef.html','step-07-comparison.html','step-08-reports.html'];
  for (const nf of navFiles) {
    if (!html.includes(nf)) issues.push(`missing nav link ${nf}`);
  }

  // 4. footer next-step link
  const footerRe = /href="(step-\d+[a-z-]+\.html)"[^>]*>\s*(下|下一步|下一环节|继续|完成|查看报告|生成报告)/i;
  const fm = html.match(/href="(step-\d+[a-z-]+\.html)"[^>]*>\s*下一[步环节]/i)
           || html.match(/href="(step-\d+[a-z-]+\.html)"[^>]*>\s*(继续|完成|查看|生成)/i);
  if (fm) {
    const fh = fm[1];
    if (fh !== exp.next) issues.push(`footer next=${fh} expected ${exp.next}`);
  }

  const status = issues.length === 0 ? 'OK' : 'ISSUES';
  if (issues.length) ok = false;
  console.log(`[${file}] step ${exp.step} progress ${exp.progress}% -> ${status}` + (issues.length? ' : '+issues.join('; '):''));
}

console.log('\n=== NAV RESULT: ' + (ok ? 'ALL CONSISTENT' : 'INCONSISTENCIES FOUND') + ' ===');
process.exit(ok ? 0 : 1);
