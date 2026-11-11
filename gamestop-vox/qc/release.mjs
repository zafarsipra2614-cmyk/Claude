// Release: audit → render → poster → verify the MP4 → copy the deliverable.
//
// The deliverable (gamestop_short_squeeze.mp4) is only replaced when
//   1. the layout audit (qc/fitcheck.mjs) is clean, and
//   2. every audited frame, pulled back out of the rendered MP4, matches the
//      still the audit judged — so what ships is exactly what was checked.
//
//   npm run release
import { execFileSync, spawnSync } from "node:child_process";
import { copyFileSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import path from "node:path";

const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const out = (p) => path.join(root, "out", p);
const run = (cmd, args, label) => {
  console.log(`\n▸ ${label}`);
  // long renders print far more than spawnSync's 1 MB default buffer, which kills the child
  const r = spawnSync(cmd, args, { cwd: root, stdio: ["ignore", "pipe", "pipe"], encoding: "utf8", maxBuffer: 1 << 30 });
  const text = `${r.stdout}${r.stderr}`
    .split("\n")
    .filter((l) => l.trim() && !/memory|docker|lower amount|\[Tab|Rendered|Encoded|Bundl/i.test(l))
    .join("\n");
  if (text) console.log(text);
  if (r.status !== 0) {
    // on failure, show the raw tail: the filter above must never hide the cause
    console.error(`${r.stdout}${r.stderr}`.split("\n").filter((l) => !/Rendered|Encoded|Bundling/.test(l)).slice(-40).join("\n"));
    console.error(`✗ ${label} failed (exit ${r.status}${r.signal ? `, signal ${r.signal}` : ""}) — deliverable not updated`);
    process.exit(1);
  }
};

run("node", ["qc/fitcheck.mjs"], "layout audit");
run("npx", ["remotion", "render", "src/index.ts", "GameStopSequence", out("final.mp4"), "--log=error"], "render");
run("python3", [path.join(process.env.HOME, ".claude/skills/vox-skill/scripts/pick_thumbnail.py"), out("final.mp4"), out("thumbnail.png"), "--embed"], "poster frame");

// --- verify: decode the audited frames from the MP4 in one pass
console.log("\n▸ verify MP4 against audited stills");
const frames = JSON.parse(readFileSync(out("qc/frames.json"), "utf8"));
const dir = out("qc/mp4");
rmSync(dir, { recursive: true, force: true });
mkdirSync(dir, { recursive: true });
const select = frames.map((f) => `eq(n\\,${f})`).join("+");
execFileSync("ffmpeg", ["-v", "error", "-i", out("final.mp4"), "-map", "0:v:0", "-vf", `select=${select}`, "-vsync", "0", path.join(dir, "m%03d.png")]);

const py = `
import json, sys
import numpy as np
from PIL import Image
frames = json.loads(sys.argv[1]); qc = sys.argv[2]; bad = []; worst = 0
for i, f in enumerate(frames):
    a = np.asarray(Image.open(f"{qc}/f{f}.png").convert("RGB"), dtype=np.int16)
    b = np.asarray(Image.open(f"{qc}/mp4/m{i+1:03d}.png").convert("RGB"), dtype=np.int16)
    if a.shape != b.shape:
        bad.append(f"frame {f}: size {b.shape} != {a.shape}"); continue
    d = np.abs(a - b).max(axis=2)
    mean, big = float(d.mean()), float((d > 48).mean())
    worst = max(worst, mean)
    # codec noise is a small even haze; a layout change is a large local difference
    if mean > 6 or big > 0.004:
        bad.append(f"frame {f}: mean diff {mean:.2f}, {big*100:.2f}% of pixels changed")
print(json.dumps({"checked": len(frames), "worst_mean": round(worst, 2), "bad": bad}))
`;
const res = JSON.parse(execFileSync("python3", ["-I", "-c", py, JSON.stringify(frames), out("qc")], { encoding: "utf8" }));
writeFileSync(out("qc/release.json"), JSON.stringify(res, null, 1));
if (res.bad.length) {
  console.error(`✗ MP4 does not match the audited frames — deliverable not updated:\n${res.bad.join("\n")}`);
  process.exit(1);
}
console.log(`MP4 matches all ${res.checked} audited frames (worst mean diff ${res.worst_mean}/255)`);

copyFileSync(out("final.mp4"), path.join(root, "gamestop_short_squeeze.mp4"));
copyFileSync(out("thumbnail.png"), path.join(root, "thumbnail.png"));
console.log("\n✓ released gamestop_short_squeeze.mp4");
