#!/usr/bin/env node
/*
  Build an Open Peeps character (hand-drawn people by Pablo Stanley, CC0) as an SVG for IMG().

  node peep.js <out.svg> '{"body":"PointingUp","face":"SmileBig","hair":"Long","accessory":"GlassRound","accent":"#4D96FF"}'
  "accent" draws the body (clothes and their outlines) in that colour; the head stays black.
  node peep.js <out.svg> '{"cast":"man2","body":"Coffee","face":"Calm","accent":"#4D96FF"}'   a ready-made person
  node peep.js            list the cast and every body, face, hair, facial hair and accessory

  The SVG is cropped tightly around the figure. Then run prep.js on the project.
*/
const fs = require("fs");
const React = require("react"), { renderToStaticMarkup } = require("react-dom/server");
const peeps = require("react-peeps"), Peep = peeps.default;
const puppeteer = require("puppeteer-core");
const { findChrome } = require("./chrome");

// House style: no expressions that show teeth (or fangs). Use the suggested face instead.
const TEETH = { Concerned: "Solemn or ConcernedFear", Explaining: "Smile or Awe", Hectic: "Fear", LoveGrin: "Smile",
  LoveGrinTeeth: "Smile", Rage: "VeryAngry", SmileBig: "Smile, Cute or CheersNM", SmileLol: "Cute or CheersNM",
  SmileTeeth: "Smile", Monster: "Suspicious", Cyclops: "Suspicious" };
// Ready-made cast: the same person across poses. Mix men and women; alternate who leads from video to video.
const CAST = {
  man1: { hair: "ShortWavy" }, man2: { hair: "Short", facialHair: "Goatee" },
  man3: { hair: "Afro", facialHair: "FullMedium" }, man4: { hair: "BaldSides", facialHair: "Full", accessory: "GlassRound" },
  woman1: { hair: "Long" }, woman2: { hair: "BunCurly", accessory: "GlassRound" },
  woman3: { hair: "MediumBangs" }, woman4: { hair: "Hijab" },
};
const [, , out, spec] = process.argv;
if (!out) {
  const k = o => Object.keys(o).join(", ");
  console.log("cast:            " + Object.entries(CAST).map(([n, v]) => `${n} (${Object.values(v).join(", ")})`).join("; "));
  console.log("bust bodies:     " + k(peeps.BustPose));
  console.log("standing bodies: " + k(peeps.StandingPose));
  console.log("sitting bodies:  " + k(peeps.SittingPose));
  console.log("faces:           " + Object.keys(peeps.Face).filter(f => !TEETH[f]).join(", ") + "   (faces showing teeth are not allowed)");
  console.log("hair:            " + k(peeps.Hair));
  console.log("facial hair:     " + k(peeps.FacialHair));
  console.log("accessories:     " + k(peeps.Accessories));
  process.exit(0);
}
let o = JSON.parse(spec || "{}");
if (o.cast) { if (!CAST[o.cast]) { console.error(`unknown cast "${o.cast}": ${Object.keys(CAST).join(", ")}`); process.exit(1); }
  const { cast, ...rest } = o; o = { ...CAST[cast], ...rest }; }
const big = { x: -1200, y: -1200, width: 3200, height: 4200 };
if (TEETH[o.face]) { console.error(`face "${o.face}" shows teeth, which the house style does not allow. Use ${TEETH[o.face]} instead.`); process.exit(1); }
const { accent, ...props } = o;
const draw = ink => renderToStaticMarkup(React.createElement(Peep, { strokeColor: ink, backgroundColor: "#ffffff", viewBox: big, ...props }));
let svg = draw("#1f2328");
if (accent) {
  // brand accent: the body (clothes and their outlines) in the accent colour, the head stays black
  const bodyOf = m => { const i = m.indexOf("<g", m.indexOf("<g") + 2), j = m.indexOf("</g>", i);   // inside the wrapper group: the body first, then the head
    let depth = 0, k = i; while (k < m.length) { if (m.startsWith("<g", k)) depth++; if (m.startsWith("</g>", k) && --depth === 0) return [i, k + 4]; k++; } return [i, j]; };
  const blue = draw(accent), [bi, bj] = bodyOf(blue), [ki, kj] = bodyOf(svg);
  svg = svg.slice(0, ki) + blue.slice(bi, bj) + svg.slice(kj);
}
svg = svg.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ');
(async () => {
  const browser = await puppeteer.launch({ executablePath: findChrome(), headless: "new",
    args: process.getuid && process.getuid() === 0 ? ["--no-sandbox"] : [] });
  const page = await browser.newPage();
  await page.setContent(`<html><body style="margin:0">${svg}</body></html>`);
  const b = await page.evaluate(() => { const r = document.querySelector("svg > g").getBBox(); return { x: r.x, y: r.y, w: r.width, h: r.height }; });
  await browser.close();
  const pad = 12, vb = `${(b.x - pad).toFixed(0)} ${(b.y - pad).toFixed(0)} ${(b.w + 2 * pad).toFixed(0)} ${(b.h + 2 * pad).toFixed(0)}`;
  svg = svg.replace(/viewBox="[^"]*"/, `viewBox="${vb}" width="${(b.w + 2 * pad).toFixed(0)}" height="${(b.h + 2 * pad).toFixed(0)}"`);
  fs.writeFileSync(out, svg);
  console.log(`${out}: ${(b.w + 2 * pad).toFixed(0)} x ${(b.h + 2 * pad).toFixed(0)}`);
})();
