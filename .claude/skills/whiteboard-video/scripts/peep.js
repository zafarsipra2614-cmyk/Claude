#!/usr/bin/env node
/*
  Build an Open Peeps character (hand-drawn people by Pablo Stanley, CC0) as an SVG for IMG().

  node peep.js <out.svg> '{"body":"PointingUp","face":"SmileBig","hair":"Long","accessory":"GlassRound","accent":"#4D96FF"}'
  "accent" draws the body (clothes and their outlines) in that colour; the head stays black.
  node peep.js            list every body, face, hair, facial hair and accessory

  The SVG is cropped tightly around the figure. Then run prep.js on the project.
*/
const fs = require("fs");
const React = require("react"), { renderToStaticMarkup } = require("react-dom/server");
const peeps = require("react-peeps"), Peep = peeps.default;
const puppeteer = require("puppeteer-core");
const { findChrome } = require("./chrome");

const [, , out, spec] = process.argv;
if (!out) {
  const k = o => Object.keys(o).join(", ");
  console.log("bust bodies:     " + k(peeps.BustPose));
  console.log("standing bodies: " + k(peeps.StandingPose));
  console.log("sitting bodies:  " + k(peeps.SittingPose));
  console.log("faces:           " + k(peeps.Face));
  console.log("hair:            " + k(peeps.Hair));
  console.log("facial hair:     " + k(peeps.FacialHair));
  console.log("accessories:     " + k(peeps.Accessories));
  process.exit(0);
}
const o = JSON.parse(spec || "{}");
const big = { x: -1200, y: -1200, width: 3200, height: 4200 };
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
