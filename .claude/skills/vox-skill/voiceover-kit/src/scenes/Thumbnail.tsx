import React from "react";
import { tornClip } from "../shared/pieces";
import { C, DROP, Frame, Label, PLAYFAIR, PT_SERIF, Tag } from "./lib";

/*
 * TEMPLATE (from the .99 film) — rewrite the masthead, headline, body copy,
 * figure and tags for each film; keep the structure.
 *
 * YouTube thumbnail in the newspaper-collage register: a torn newsprint page
 * carrying the headline, with the price tags clipped on beside it. Rendered as
 * a still (frame 60, everything settled), audited, exported at 1280×720 by
 * qc/thumbnail.mjs.
 */
export const THUMB_FRAME = 60;

const NEWSPRINT = "#ECE6D8";
const PAGE = { left: 820, top: 46, width: 1040, height: 990 };

const BODY =
  "A price ending in nine feels cheaper than a price one cent higher, mostly when that cent changes the first digit. " +
  "In a national clothing catalog, a dress sold more at $39 than at $34. Cars at 79,900 miles sold for about $210 more " +
  "than cars that had just crossed 80,000. Luxury brands refuse the nine altogether.";

export const Thumbnail: React.FC = () => (
  <Frame push={0}>
    {/* the page: red offset, then newsprint with a halftone screen */}
    <div style={{ position: "absolute", ...PAGE, transform: "rotate(1.6deg)", zIndex: 10 }}>
      <div aria-hidden style={{ position: "absolute", inset: 0, background: C.red, clipPath: tornClip(17, 22, 1.6), transform: "translate(-22px, 12px)" }} />
      <div
        data-fit="newspaper page"
        style={{
          position: "absolute",
          inset: 0,
          background: NEWSPRINT,
          backgroundImage: "radial-gradient(rgba(22,17,13,0.10) 1.3px, transparent 1.6px)",
          backgroundSize: "7px 7px",
          clipPath: tornClip(23, 22, 1.6),
          filter: DROP,
          padding: "44px 56px",
          boxSizing: "border-box",
          color: C.inkDeep,
        }}
      >
        <div style={{ textAlign: "center", fontFamily: PLAYFAIR, fontWeight: 700, fontSize: 66, letterSpacing: 1, lineHeight: 1.1 }}>The Price Times</div>
        <div style={{ height: 3, background: C.inkDeep, margin: "14px 0 4px" }} />
        <div style={{ height: 1.5, background: C.inkDeep }} />
        <div style={{ display: "flex", justifyContent: "space-between", margin: "10px 0 0" }}>
          <Label size={16} spacing={4} color={C.inkDeep}>VOL. 99</Label>
          <Label size={16} spacing={4} color={C.inkDeep}>CONSUMER PSYCHOLOGY</Label>
          <Label size={16} spacing={4} color={C.inkDeep}>PRICE 99¢</Label>
        </div>
        <div style={{ height: 1.5, background: C.inkDeep, margin: "10px 0 30px" }} />
        <div style={{ fontFamily: PLAYFAIR, fontWeight: 700, fontSize: 124, lineHeight: 1.1, letterSpacing: -2 }}>
          Why does
          <br />
          everything end
          <br />
          in{" "}
          <span style={{ position: "relative", display: "inline-block", padding: "0 10px" }}>
            {/* amber highlighter, then the red marker ring: deliberate marks on the words */}
            <span aria-hidden data-mark style={{ position: "absolute", left: -4, right: -4, top: "18%", bottom: "6%", background: C.amber, transform: "rotate(-1.5deg)", zIndex: -1 }} />
            <span style={{ color: C.red }}>.99?</span>
            <svg aria-hidden data-mark viewBox="0 0 300 160" preserveAspectRatio="none" style={{ position: "absolute", left: -22, top: 4, width: "calc(100% + 44px)", height: "calc(100% + 4px)", overflow: "visible" }}>
              <ellipse cx={150} cy={80} rx={146} ry={74} fill="none" stroke={C.red} strokeWidth={7} transform="rotate(-3 150 80)" />
            </svg>
          </span>
        </div>
        <div style={{ height: 1.5, background: C.inkDeep, margin: "26px 0 20px", opacity: 0.6 }} />
        <div style={{ display: "flex", gap: 40 }}>
          <div style={{ flex: 1, fontFamily: PT_SERIF, fontSize: 23, lineHeight: 1.36, textAlign: "justify", opacity: 0.8 }}>{BODY}</div>
          {/* Fig. 1: the dress test, as a newsprint figure */}
          <div style={{ width: 300, flexShrink: 0 }}>
            <div style={{ height: 196, display: "flex", alignItems: "flex-end", gap: 22, padding: "0 18px", borderBottom: `3px solid ${C.inkDeep}`, boxSizing: "border-box" }}>
              {[
                { h: 120, p: "$34", red: false },
                { h: 168, p: "$39", red: true },
                { h: 120, p: "$44", red: false },
              ].map((b) => (
                <div key={b.p} style={{ flex: 1, height: b.h, background: b.red ? C.red : C.inkDeep }} />
              ))}
            </div>
            <div style={{ display: "flex", gap: 22, padding: "8px 18px 0", boxSizing: "border-box" }}>
              {["$34", "$39", "$44"].map((p) => (
                <div key={p} style={{ flex: 1, textAlign: "center", fontFamily: PT_SERIF, fontWeight: 700, fontSize: 20 }}>{p}</div>
              ))}
            </div>
            <div style={{ fontFamily: PT_SERIF, fontStyle: "italic", fontSize: 18, lineHeight: 1.3, marginTop: 10 }}>Fig. 1 — The same dress sold a third more at $39.</div>
          </div>
        </div>
      </div>
    </div>
    {/* the tags, clipped onto the collage beside the page */}
    <Tag x={130} y={170} w={450} price="$10.00" start={0} strikeAt={0} rot={6} string={false} tracking={0} name="thumb old price" />
    <Tag x={36} y={540} w={780} price="$9.99" tone="red" start={0} hl={[2, 3, 4]} rot={-6} string={false} tracking={0} name="thumb hero price" layer="over" z={24} />
  </Frame>
);
