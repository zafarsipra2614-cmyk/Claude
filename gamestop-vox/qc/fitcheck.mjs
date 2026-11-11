// Layout QC: render each scene's fullest frame, collect FIT errors that the
// in-page checker (FitCheck in src/scenes/kit.tsx) logs, write a contact sheet.
// Exits 1 if anything spills out of its box.  Usage: node qc/fitcheck.mjs [frames...]
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { execFileSync } from "node:child_process";
import { mkdirSync } from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const frames = process.argv.slice(2).map(Number);
const FRAMES = frames.length ? frames : [165, 345, 479, 665, 975, 1185, 1360, 1645, 1840];
mkdirSync(path.join(root, "out/qc"), { recursive: true });

const serveUrl = await bundle({ onProgress: () => {}, entryPoint: path.join(root, "src/index.ts"), publicDir: path.join(root, "public") });
const composition = await selectComposition({ serveUrl, id: "GameStopSequence", logLevel: "error" });
const problems = new Set();
let ran = 0;
for (const frame of FRAMES) {
  await renderStill({
    serveUrl,
    composition,
    frame,
    output: path.join(root, `out/qc/f${frame}.png`),
    logLevel: "error",
    onBrowserLog: (log) => {
      if (log.type === "error" && !log.text.startsWith("FIT")) problems.add(`[global frame ${frame}] browser error: ${log.text}`);
      if (log.text.startsWith("FIT ")) problems.add(`[global frame ${frame}] ${log.text.replace(/^FIT frame=\d+ /, "")}`);
      if (log.text.startsWith("FITCHECK")) ran++;
    },
  });
}
const args = [], filt = [];
FRAMES.forEach((f, i) => { args.push("-i", path.join(root, `out/qc/f${f}.png`)); filt.push(`[${i}:v]scale=640:-1[v${i}]`); });
const rows = [];
for (let r = 0; r * 3 < FRAMES.length; r++) {
  const cells = [0, 1, 2].map((c) => r * 3 + c).filter((i) => i < FRAMES.length);
  filt.push(cells.length > 1 ? `${cells.map((i) => `[v${i}]`).join("")}hstack=inputs=${cells.length},pad=1920:ih[r${r}]` : `[v${cells[0]}]pad=1920:ih[r${r}]`);
  rows.push(`[r${r}]`);
}
if (rows.length > 1) filt.push(`${rows.join("")}vstack=inputs=${rows.length}`);
try {
  if (FRAMES.length > 1) execFileSync("ffmpeg", ["-y", "-v", "error", ...args, "-filter_complex", filt.join(";"), ...(rows.length > 1 ? [] : ["-map", "[r0]"]), path.join(root, "out/qc/sheet.png")], { stdio: "pipe" });
} catch (e) {
  console.error("contact sheet failed:", String(e.stderr || e).split("\n")[0]);
}

if (ran === 0) { console.error("fit check did not run in the page"); process.exit(2); }
if (problems.size) { console.log("FIT PROBLEMS:\n" + [...problems].join("\n")); process.exit(1); }
console.log(`fit check: clean (${FRAMES.length} frames)`);
