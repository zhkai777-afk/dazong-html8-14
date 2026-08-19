import fs from 'fs';
import vm from 'vm';
import path from 'path';

const dir = decodeURIComponent(path.dirname(new URL(import.meta.url).pathname));
const read = (f) => fs.readFileSync(path.join(dir, f), 'utf8');

function extractArray(html, name) {
  const re = new RegExp('(const\\s+' + name + '\\s*=\\s*\\[[\\s\\S]*?\\n\\s*\\];)', 'm');
  const m = html.match(re);
  return m ? m[1] : null;
}
function extractFn(html, name) {
  // match `const NAME =` or `function NAME(`
  const startRe = new RegExp('(const\\s+' + name + '\\s*=|function\\s+' + name + '\\s*\\()');
  const sm = html.match(startRe);
  if (!sm) return null;
  const after = html.slice(sm.index);
  // find body start: after first '{' OR after '=>' for arrow
  let i = after.indexOf('=>');
  let braceMode = false;
  if (i === -1) {
    // function declaration: find first '{'
    i = after.indexOf('{');
    braceMode = true;
  } else {
    i += 2;
    while (i < after.length && /\s/.test(after[i])) i++;
    if (after[i] === '{') braceMode = true;
  }
  if (braceMode) {
    let depth = 0, j = i;
    for (; j < after.length; j++) {
      if (after[j] === '{') depth++;
      else if (after[j] === '}') { depth--; if (depth === 0) { j++; break; } }
    }
    return after.slice(0, j);
  } else {
    // expression body: read to end of line
    const nl = after.indexOf('\n', i);
    const end = nl === -1 ? after.length : nl;
    return after.slice(0, end).trim();
  }
}

// Slice from a start marker up to (but excluding) an end marker line — robust for functions whose
// brace-scanner would over-capture (e.g. makeShoreMeasurement preceding shoreReadings).
function extractUntil(html, startRe, endRe) {
  const si = html.search(startRe);
  if (si === -1) return null;
  const ei = html.search(endRe);
  if (ei === -1 || ei < si) return html.slice(si);
  return html.slice(si, ei);
}

// Run helpers + array + compute expression as ONE combined script (avoids vm lexical-scoping across calls)
function runInSandbox(helpersSrc, arraySrc, computeExpr) {
  const ctx = { Intl, Math, console };
  vm.createContext(ctx);
  // keep trailing ';' so statements are properly separated (no ASI hazard with following '(')
  const combined = [helpersSrc || '', arraySrc, '(' + computeExpr + ')'].filter(Boolean).join('\n');
  try {
    return vm.runInContext(combined, ctx);
  } catch (e) {
    if (/makeShoreMeasurement|shoreComputed|not defined|already declared/.test(e.message)) {
      console.error('  [DEBUG combined head]', combined.slice(0, 160).replace(/\n/g, '⏎'));
      console.error('  [DEBUG combined tail]', combined.slice(-160).replace(/\n/g, '⏎'));
      console.error('  [DEBUG has makeShoreMeasurement def]', /function makeShoreMeasurement/.test(combined));
    }
    throw e;
  }
}

// Compute a headline number from a given file using a common compute formula
function headline(file, arrayName, computeExpr, helperFns = [], extraBlock = null) {
  const html = read(file);
  const arr = extractArray(html, arrayName);
  if (!arr) throw new Error(`array ${arrayName} not found in ${file}`);
  const helpers = helperFns.map(fn => extractFn(html, fn)).filter(Boolean).join('\n');
  const block = extraBlock ? extractUntil(html, extraBlock.start, extraBlock.end) : null;
  const prelude = [block, helpers].filter(Boolean).join('\n');
  return runInSandbox(prelude, arr, computeExpr);
}

const cases = [
  {
    label: 'arrivalGsv (抵港 GSV)', array: 'readings', agg: 'step-07-comparison.html', src: 'step-03-arrival-ullage.html',
    expr: 'readings.reduce((s,r)=>{const gov=Math.max(r.tov-r.freeWater,0);return s+gov*r.vcf;},0)',
  },
  {
    label: 'shoreReceived (岸收 GSV)', array: 'shoreReadings', agg: 'step-07-comparison.html', src: 'step-04-shore-tank.html',
    helpers: ['round3', 'shoreComputed'],
    extraBlock: { start: /function makeShoreMeasurement/, end: /const shoreReadings/ },
    expr: 'shoreReadings.reduce((s,r)=>{const o=shoreComputed(r.open),c=shoreComputed(r.close);return s+(c.gsv-o.gsv);},0)',
  },
  {
    label: 'robGsv (ROB GSV)', array: 'robReadings', agg: 'step-07-comparison.html', src: 'step-05-rob.html',
    expr: 'robReadings.reduce((s,r)=>s+r.liquidVolume*r.vcf+r.nonLiquidVolume,0)',
  },
  {
    label: 'averageVef (VEF 均值)', array: 'vefVoyages', agg: 'step-07-comparison.html', src: 'step-06-vef.html',
    expr: 'vefVoyages.filter(r=>r.included).reduce((s,r)=>s+r.vef,0)/vefVoyages.filter(r=>r.included).length',
  },
];

let allOk = true;
console.log('--- CROSS-FILE HEADLINE NUMBER CONSISTENCY ---');
for (const c of cases) {
  try {
    const srcVal = headline(c.src, c.array, c.expr, c.helpers || [], c.extraBlock);
    const aggVal = headline(c.agg, c.array, c.expr, c.helpers || [], c.extraBlock);
    const diff = Math.abs(srcVal - aggVal);
    const ok = diff < 1e-6;
    if (!ok) allOk = false;
    console.log(`  [${c.label}] src=${srcVal.toFixed(4)}  agg=${aggVal.toFixed(4)}  Δ=${diff.toExponential(2)} -> ${ok ? 'MATCH' : 'MISMATCH'}`);
  } catch (e) {
    allOk = false;
    console.log(`  [${c.label}] ERROR: ${e.message}`);
  }
}

// Also verify step-08 uses the same aggregates as step-07
console.log('\n--- STEP-08 vs STEP-07 AGGREGATE CONSISTENCY ---');
try {
  const s07arrival = headline('step-07-comparison.html', 'readings', 'readings.reduce((s,r)=>{const gov=Math.max(r.tov-r.freeWater,0);return s+gov*r.vcf;},0)');
  const s08arrival = headline('step-08-reports.html', 'readings', 'readings.reduce((s,r)=>{const gov=Math.max(r.tov-r.freeWater,0);return s+gov*r.vcf;},0)');
  const ok = Math.abs(s07arrival - s08arrival) < 1e-6;
  if (!ok) allOk = false;
  console.log(`  [arrivalGsv] step07=${s07arrival.toFixed(4)} step08=${s08arrival.toFixed(4)} -> ${ok ? 'MATCH' : 'MISMATCH'}`);
} catch (e) { allOk = false; console.log('  [arrivalGsv] ERROR: ' + e.message); }

console.log('\n=== DATA RESULT: ' + (allOk ? 'ALL CONSISTENT' : 'INCONSISTENCIES FOUND') + ' ===');
process.exit(allOk ? 0 : 1);
