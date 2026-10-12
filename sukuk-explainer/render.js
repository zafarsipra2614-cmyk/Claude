// Renders scene.html at 60fps with 3 subframes per frame; ffmpeg tmix blends them for motion blur.
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path'), fs = require('fs');
const FPS = 60, SUB = 3, WORKERS = +(process.argv[2] || 4), OUT = 'render';
(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const total = JSON.parse(fs.readFileSync('timeline.json')).total;
  const frames = Math.ceil(total * FPS), per = Math.ceil(frames / WORKERS);
  const browser = await chromium.launch();
  const job = async (w) => {
    const f0 = w * per, f1 = Math.min(frames, f0 + per);
    const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
    await page.goto('file://' + path.resolve('scene.html')); await page.evaluate(() => window.ready);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-c:v', 'png', '-framerate', String(FPS * SUB), '-i', '-',
      '-vf', `tmix=frames=${SUB},select='eq(mod(n\\,${SUB})\\,${SUB - 1})',setpts=N/${FPS}/TB`, '-r', String(FPS),
      '-c:v', 'libx264', '-preset', 'medium', '-crf', '16', '-pix_fmt', 'yuv420p', `${OUT}/seg${w}.mp4`], { stdio: ['pipe', 'inherit', 'inherit'] });
    const done = new Promise(r => ff.on('close', r));
    for (let f = f0; f < f1; f++) {
      for (let k = 0; k < SUB; k++) {
        const t = (f + (k - (SUB - 1) / 2) / SUB) / FPS; // subframes centred on the frame time
        await page.evaluate(t => seek(Math.max(0, t)), t);
        const buf = await page.screenshot({ type: 'png' });
        if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      }
      if (w === 0 && f % 600 === 0) console.log('worker0 frame', f - f0, '/', f1 - f0, new Date().toISOString());
    }
    ff.stdin.end(); await done; await page.close();
  };
  await Promise.all([...Array(WORKERS).keys()].map(job));
  await browser.close();
  fs.writeFileSync(`${OUT}/list.txt`, [...Array(WORKERS).keys()].map(w => `file 'seg${w}.mp4'`).join('\n'));
  console.log('done', frames, 'frames');
})();
