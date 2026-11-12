// Render foley (and optionally a music bed) with papercut-explainer's Web Audio engine.
//
// Based on papercut-explainer's library/audio/render.mjs (https://github.com/0xS4N4TG/papercut-explainer,
// MIT, (c) 2026 sanat), changed for long films: no protocol timeout (a 5-minute bed takes
// longer than puppeteer's default 180 s), and the music bed is rendered only when asked for.
//
//   node vo/render_foley.mjs <papercut-lib> <cues.json> <out-dir> [bed-preset]
//   cues.json: {"dur": seconds, "cues": [{"t": seconds, "type": "<sfx name>"}]}
//   writes <out-dir>/sfx_<name>.wav (one short clip per distinct sound; build_audio.py
//   places them on the cues), and <out-dir>/music.wav when a bed preset is given.
//   Needs puppeteer-core (devDependency) and Chromium (CHROME_PATH).
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import path from "node:path";

const [lib, cuesPath, outDir, bedName] = process.argv.slice(2);
if (!lib || !cuesPath || !outDir) {
  console.error("usage: node vo/render_foley.mjs <papercut-lib> <cues.json> <out-dir> [bed-preset]");
  process.exit(2);
}
const audio = path.join(lib, "audio");
const cues = JSON.parse(readFileSync(cuesPath, "utf8"));
const types = [...new Set(cues.cues.map((c) => c.type))];
const missing = types.filter((t) => !existsSync(path.join(audio, "sfx", `${t}.js`)));
if (missing.length) {
  console.error(`no papercut SFX named: ${missing.join(", ")} (see ${path.join(audio, "CATALOG.md")})`);
  process.exit(1);
}
// the engine needs a bed definition even for the fx-only pass; use the requested one or any preset
const bedFile = path.join(audio, "beds", `${bedName || "marimba-F-108"}.json`);
if (!existsSync(bedFile)) {
  console.error(`no papercut bed preset ${bedName} (see ${path.join(audio, "beds")})`);
  process.exit(1);
}
const bed = JSON.parse(readFileSync(bedFile, "utf8"));
const js = [readFileSync(path.join(audio, "engine.js"), "utf8"), ...types.map((t) => readFileSync(path.join(audio, "sfx", `${t}.js`), "utf8"))].join("\n");

const chromePath = process.env.CHROME_PATH;
if (!chromePath || !existsSync(chromePath)) {
  console.error("set CHROME_PATH to a Chrome/Chromium binary");
  process.exit(1);
}
const puppeteer = createRequire(path.resolve("package.json"))("puppeteer-core");
const browser = await puppeteer.launch({
  executablePath: chromePath,
  headless: true,
  protocolTimeout: 0, // long films: no limit on the offline render
  args: process.getuid?.() === 0 ? ["--no-sandbox"] : [],
});
try {
  const page = await browser.newPage();
  page.on("console", (m) => {
    if (m.type() === "error") console.error("[page]", m.text());
  });
  await page.setContent(`<!doctype html><meta charset="utf-8"><script>${js}</script>`);
  mkdirSync(outDir, { recursive: true });
  // Each distinct sound is rendered ONCE as a short clip (sfx_<name>.wav) and placed at
  // its cue times by build_audio.py: rendering a whole film-length fx track in the
  // browser takes ~10 min for 5 min of film; clips take seconds.
  for (const t of types) {
    const clip = { dur: 3, cues: [{ t: 0, type: t }] };
    const b64 = await page.evaluate((c, o, b) => window.renderScore(c, o, b), clip, "fx", bed);
    writeFileSync(path.join(outDir, `sfx_${t}.wav`), Buffer.from(b64, "base64"));
  }
  if (bedName) {
    const b64 = await page.evaluate((c, o, b) => window.renderScore(c, o, b), cues, "music", bed);
    writeFileSync(path.join(outDir, "music.wav"), Buffer.from(b64, "base64"));
  }
} finally {
  await browser.close();
}
console.log(`${types.length} sfx types, ${cues.cues.length} cues, ${cues.dur.toFixed(1)} s${bedName ? `, bed ${bedName}` : ""}`);
