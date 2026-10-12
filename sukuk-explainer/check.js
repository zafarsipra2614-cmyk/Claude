const { chromium } = require('playwright');
const path = require('path'), fs = require('fs');
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.goto('file://' + path.resolve('scene.html')); await p.evaluate(() => window.ready);
  const info = await p.evaluate(() => {
    const out = { total: window.TOTAL, lines: window.LINES, acts: window.ACTS, texts: window.TEXTS, over: [] };
    for (let t = 0; t < window.TOTAL; t += 0.05) { const v = visibleWords(t); if (v.n > 7) out.over.push([+t.toFixed(2), v.n, v.names.join(' | ')]); }
    return out;
  });
  fs.writeFileSync('timeline.json', JSON.stringify({ total: info.total, lines: info.lines }, null, 1));
  console.log('TOTAL', info.total.toFixed(2));
  info.lines.forEach(l => console.log(l.i, 'slot', l.slot.toFixed(2), 'voice', l.v0.toFixed(2), '-', l.v1.toFixed(2), 'end', l.end.toFixed(2)));
  { let g = []; for (const o of info.over) { const L = g[g.length - 1]; if (L && o[0] - L[1] < 0.06 && L[2] === o[2]) L[1] = o[0]; else g.push([o[0], o[0], o[2], o[1]]); } console.log('>7 words spans:', g.length); g.forEach(x => console.log('  ', x[0], '-', x[1], x[3], x[2])); }
  const acts = info.acts.filter(a => !a[2].startsWith('flow')).sort((a, b) => a[0] - b[0]);
  for (let i = 1; i < acts.length; i++) if (acts[i][0] < acts[i - 1][1] - 1e-6) console.log('OVERLAP', acts[i - 1], acts[i]);
  for (const t of info.texts) if (t.e0 < 1e8 && t.e0 - t.t1 < 0.3 * t.words) console.log('SHORT HOLD', t);
  for (const t of info.texts) if (t.t1 > 1e8) console.log('NEVER DRAWN', t.id);
  const times = (process.argv[2] || '').split(',').filter(Boolean).map(Number);
  fs.mkdirSync('frames', { recursive: true });
  for (const t of times) { await p.evaluate(t => seek(t), t); await p.screenshot({ path: `frames/k_${t.toFixed(1)}.png` }); }
  await b.close();
})();
