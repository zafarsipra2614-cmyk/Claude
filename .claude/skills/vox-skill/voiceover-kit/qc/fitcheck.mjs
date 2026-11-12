// Layout audit. Renders a settled frame after every cue in src/shared/timing.ts
// (each new element, once it has landed) plus every scene's last frame, and
// collects the FIT errors the in-page checker (FitCheck, src/scenes/kit.tsx)
// logs: CONTAIN (spills out of its box / the frame), COVERED (text hidden
// under something), OVERLAP (text on text, box on box). Writes a contact sheet
// and out/qc/frames.json. Exits 1 on any problem.
//   node qc/fitcheck.mjs            full audit
//   node qc/fitcheck.mjs 480 975    just these frames
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { execFileSync } from "node:child_process";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
mkdirSync(path.join(root, "out/qc"), { recursive: true });
const frames = process.argv.slice(2).map(Number);
const auditFrames = () => {
  const ts = readFileSync(path.join(root, "src/shared/timing.ts"), "utf8");
  const block = (name) => ts.split(`export const ${name} = {`)[1].split("} as const")[0];
  const durations = [...block("D").matchAll(/^\s+(\w+): (\d+),/gm)].map((m) => Number(m[2]));
  const starts = durations.map((_, i) => durations.slice(0, i).reduce((a, b) => a + b, 0));
  const T = Number((ts.match(/export const T = (\d+)/) || [0, 0])[1]); // transition overlap
  const set = new Set();
  const names = [...block("D").matchAll(/^\s+(\w+): (\d+),/gm)].map((m) => m[1]);
  for (const m of block("CUE").matchAll(/"([^".]+)\.[^"]+": (-?\d+),/g)) {
    const sc = /^s\d+$/.test(m[1]) ? Number(m[1].slice(1)) - 1 : names.indexOf(m[1]);
    if (sc < 0) throw new Error(`cue for unknown scene ${m[1]}`);
    set.add(starts[sc] + Math.min(Math.max(Number(m[2]) + 32, T + 4), durations[sc] - 2));
  }
  durations.forEach((d, i) => set.add(starts[i] + d - 2));
  return [...set].sort((a, b) => a - b);
};
const FRAMES = frames.length ? frames : auditFrames();
writeFileSync(path.join(root, "out/qc/frames.json"), JSON.stringify(FRAMES));
console.log(`auditing ${FRAMES.length} frames`);

const serveUrl = await bundle({ onProgress: () => {}, entryPoint: path.join(root, "src/index.ts"), publicDir: path.join(root, "public") });
const VIDEO = JSON.parse(readFileSync(path.join(root, "package.json"), "utf8")).video;
const composition = await selectComposition({ serveUrl, id: VIDEO.composition, logLevel: "error" });
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
const SHEET = FRAMES.length > 9 ? FRAMES.filter((f, i) => i % Math.ceil(FRAMES.length / 9) === 0).slice(0, 9) : FRAMES;
const args = [], filt = [];
SHEET.forEach((f, i) => { args.push("-i", path.join(root, `out/qc/f${f}.png`)); filt.push(`[${i}:v]scale=640:-1[v${i}]`); });
const rows = [];
for (let r = 0; r * 3 < SHEET.length; r++) {
  const cells = [0, 1, 2].map((c) => r * 3 + c).filter((i) => i < SHEET.length);
  filt.push(cells.length > 1 ? `${cells.map((i) => `[v${i}]`).join("")}hstack=inputs=${cells.length},pad=1920:ih[r${r}]` : `[v${cells[0]}]pad=1920:ih[r${r}]`);
  rows.push(`[r${r}]`);
}
if (rows.length > 1) filt.push(`${rows.join("")}vstack=inputs=${rows.length}`);
try {
  if (SHEET.length > 1) execFileSync("ffmpeg", ["-y", "-v", "error", ...args, "-filter_complex", filt.join(";"), ...(rows.length > 1 ? [] : ["-map", "[r0]"]), path.join(root, "out/qc/sheet.png")], { stdio: "pipe" });
} catch (e) {
  console.error("contact sheet failed:", String(e.stderr || e).split("\n")[0]);
}

if (ran === 0) { console.error("fit check did not run in the page"); process.exit(2); }
if (problems.size) {
  console.log(`FIT PROBLEMS (${problems.size}):\n` + [...problems].sort().join("\n"));
  process.exit(1);
}
console.log(`fit check: clean (${FRAMES.length} frames)`);
