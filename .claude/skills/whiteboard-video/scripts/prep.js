#!/usr/bin/env node
/*
  Prepare a project's line-art images for drawing.

  node prep.js <project>

  For every image in <project>/assets/ (svg, png, jpg) without an up-to-date <name>.strokes.json,
  renders SVGs to a PNG (longest side about 1100 px) in headless Chrome, then runs trace.py to turn the
  ink into marker strokes. scenes.js then draws the image with IMG('<name>', x, y, width, at, dur).
*/
const fs = require("fs"), path = require("path"), os = require("os");
const { execFileSync } = require("child_process");
const puppeteer = require("puppeteer-core");
const { findChrome } = require("./chrome");

const project = path.resolve(process.argv[2] || ".");
const dir = path.join(project, "assets");
if (!fs.existsSync(dir)) { console.log("no assets/ folder, nothing to prepare"); process.exit(0); }
const files = fs.readdirSync(dir).filter(f => /\.(svg|png|jpe?g)$/i.test(f) && !/\.(ink|shadow)\.png$/i.test(f));   // generated line-art and shadow layers

(async () => {
  let browser;
  for (const f of files) {
    const src = path.join(dir, f), name = f.replace(/\.[^.]+$/, ""), out = path.join(dir, name + ".strokes.json");
    if (fs.existsSync(out) && fs.statSync(out).mtimeMs > fs.statSync(src).mtimeMs
        && JSON.parse(fs.readFileSync(out, "utf8")).outline) continue;      // older traces (no sketch/ink/colour stages) are redone
    let png = src, scale = 1;
    if (/\.svg$/i.test(f)) {
      browser = browser || await puppeteer.launch({ executablePath: findChrome(), headless: "new", args: [...(process.getuid && process.getuid() === 0 ? ["--no-sandbox"] : []), "--allow-file-access-from-files"] });
      const page = await browser.newPage();
      await page.goto("file://" + src);
      const { w, h } = await page.evaluate(() => {
        const s = document.querySelector("svg"), vb = s.viewBox.baseVal;
        return vb && vb.width ? { w: vb.width, h: vb.height } : { w: s.width.baseVal.value, h: s.height.baseVal.value };
      });
      scale = Math.max(w, h) / 1100;
      const pw = Math.round(w / scale), ph = Math.round(h / scale);
      await page.setViewport({ width: pw, height: ph });
      await page.evaluate((pw, ph) => {
        const s = document.querySelector("svg");
        s.setAttribute("width", pw); s.setAttribute("height", ph);
        s.style.background = "transparent"; s.style.display = "block"; document.documentElement.style.background = "transparent";
      }, pw, ph);
      png = path.join(os.tmpdir(), `wbv-${name}-${process.pid}.png`);
      await page.screenshot({ path: png, omitBackground: true });
      await page.close();
    }
    execFileSync("python3", [path.join(__dirname, "trace.py"), png, out, "--scale", String(scale), "--label", f], { stdio: "inherit" });
    if (png !== src) fs.rmSync(png, { force: true });
  }
  if (browser) await browser.close();
})();
