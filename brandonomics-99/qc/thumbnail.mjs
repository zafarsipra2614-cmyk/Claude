// YouTube thumbnail: render the Thumbnail composition (settled frame), run the
// same in-page layout audit on it, export 1280×720 JPEG under 2 MB.
//   node qc/thumbnail.mjs  ->  youtube_thumbnail.jpg
import { bundle } from "@remotion/bundler";
import { renderStill, selectComposition } from "@remotion/renderer";
import { execFileSync } from "node:child_process";
import { mkdirSync, statSync } from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
mkdirSync(path.join(root, "out/qc"), { recursive: true });
const serveUrl = await bundle({ entryPoint: path.join(root, "src/index.ts"), publicDir: path.join(root, "public"), onProgress: () => {} });
const composition = await selectComposition({ serveUrl, id: "Thumbnail", logLevel: "error" });
const problems = [];
let ran = false;
const png = path.join(root, "out/qc/thumbnail_full.png");
await renderStill({
  serveUrl,
  composition,
  frame: composition.durationInFrames - 1,
  output: png,
  logLevel: "error",
  onBrowserLog: (log) => {
    if (log.text.startsWith("FITCHECK")) ran = true;
    if (log.text.startsWith("FIT ")) problems.push(log.text.replace(/^FIT frame=\d+ /, ""));
  },
});
if (!ran) { console.error("fit check did not run"); process.exit(2); }
if (problems.length) { console.log(`FIT PROBLEMS (${problems.length}):\n` + problems.join("\n")); process.exit(1); }
const jpg = path.join(root, "youtube_thumbnail.jpg");
execFileSync("ffmpeg", ["-y", "-v", "error", "-i", png, "-vf", "scale=1280:720:flags=lanczos", "-q:v", "2", jpg]);
const kb = Math.round(statSync(jpg).size / 1024);
if (kb > 2000) { console.error(`thumbnail is ${kb} KB, over YouTube's 2 MB limit`); process.exit(1); }
console.log(`thumbnail: layout clean, wrote youtube_thumbnail.jpg (1280×720, ${kb} KB)`);
