/*
 * Archive photos and newspaper clippings: the documentary layer.
 *
 * - Photos come from cinematic-film's Wikimedia Commons fetcher (public domain / CC only,
 *   licences recorded, credits written for the video description); see
 *   references/voiceover-mode.md "Archive photos".
 * - The halftone screen follows gbro-collage-info's collage.css (multiplied radial dots),
 *   https://github.com/pyang5166/gbro-collage-info, MIT.
 */
import React from "react";
import { Img, staticFile } from "remotion";
import { C, DROP, Label, PLAYFAIR, PT_SERIF, Rise } from "./lib";
import { tornClip } from "../shared/pieces";

export const NEWSPRINT = "#ECE6D8";

/** gbro's halftone screen: multiplied ink dots over a photo or a panel. */
export const Halftone: React.FC<{ dot?: number; pitch?: number; alpha?: number }> = ({ dot = 1.15, pitch = 4, alpha = 0.55 }) => (
  <div
    aria-hidden
    style={{
      position: "absolute",
      inset: 0,
      mixBlendMode: "multiply",
      backgroundImage: `radial-gradient(rgba(20,18,14,${alpha}) ${dot}px, transparent ${dot + 0.15}px)`,
      backgroundSize: `${pitch}px ${pitch}px`,
      pointerEvents: "none",
    }}
  />
);

/**
 * An archival photo mounted as a paper print: white border, two tape strips, the red
 * offset stroke, a halftone screen, and a caption with its credit on the mount.
 * `src` is a path under public/ (e.g. "archive/P01.jpg"); `credit` comes from credits.md.
 */
export const ArchivePhoto: React.FC<{
  src: string;
  start: number;
  left: number;
  top: number;
  width: number;
  height: number;
  caption?: string;
  credit: string;
  rotate?: number;
  halftone?: boolean;
  tone?: "mono" | "sepia" | "colour";
  stroke?: number;
  exit?: number;
  name?: string;
}> = ({ src, start, left, top, width, height, caption, credit, rotate = -1.2, halftone = true, tone = "mono", stroke = -18, exit, name }) => {
  const MOUNT = 18;
  const CAP = caption ? 78 : 48;
  const filter = tone === "mono" ? "grayscale(1) contrast(1.15) brightness(1.03)" : tone === "sepia" ? "grayscale(1) sepia(0.45) contrast(1.1)" : "contrast(1.05) saturate(0.9)";
  return (
    <Rise start={start} dur={28} dist={260} left={left} top={top} width={width} height={height + CAP} rotate={rotate} exit={exit} z={13} style={{ filter: "none" }}>
      <div aria-hidden style={{ position: "absolute", inset: 0, background: C.red, transform: `translate(${stroke}px, 10px)` }} />
      <div data-fit={name ?? `archive ${src}`} style={{ position: "absolute", inset: 0, background: "#F7F4EC", padding: MOUNT, paddingBottom: 12, boxSizing: "border-box", filter: DROP }}>
        <div style={{ position: "relative", width: width - 2 * MOUNT, height: height - MOUNT, overflow: "hidden", background: "#CFC8BA" }}>
          <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", filter }} />
          {halftone ? <Halftone /> : null}
        </div>
        <div style={{ marginTop: 10, overflow: "hidden" }}>
          {caption ? <div style={{ fontFamily: PT_SERIF, fontStyle: "italic", fontSize: 24, lineHeight: 1.2, color: C.inkDeep, whiteSpace: "nowrap" }}>{caption}</div> : null}
          <Label size={14} spacing={2} style={{ marginTop: 6 }}>{credit}</Label>
        </div>
      </div>
      {/* tape */}
      {[
        { left: width * 0.12, rot: -8 },
        { left: width * 0.72, rot: 6 },
      ].map((t, i) => (
        <div key={i} aria-hidden style={{ position: "absolute", left: t.left, top: -16, width: width * 0.16, height: 34, background: "rgba(232,221,190,0.82)", transform: `rotate(${t.rot}deg)`, boxShadow: "0 2px 4px rgba(55,45,31,0.18)" }} />
      ))}
    </Rise>
  );
};

/**
 * A torn newspaper clipping: newsprint with a halftone screen, a small masthead and date,
 * a serif headline (with an optional highlighted phrase) and a few lines of body copy.
 * Use for "the papers said…", a study's press coverage, a dated event. Write real copy
 * from the script; never invent a quotation or attribute one to a real paper.
 */
export const NewsClipping: React.FC<{
  start: number;
  left: number;
  top: number;
  width: number;
  height: number;
  masthead: string;
  date?: string;
  headline: string;
  highlight?: string;
  body?: string;
  rotate?: number;
  exit?: number;
  name?: string;
}> = ({ start, left, top, width, height, masthead, date, headline, highlight, body, rotate = 1.2, exit, name }) => {
  const parts = highlight && headline.includes(highlight) ? headline.split(highlight) : [headline];
  return (
    <Rise start={start} dur={28} dist={260} left={left} top={top} width={width} height={height} rotate={rotate} exit={exit} z={13} style={{ filter: "none" }}>
      <div aria-hidden style={{ position: "absolute", inset: 0, background: C.red, clipPath: tornClip(width % 29, 20, 1.6), transform: "translate(-18px, 10px)" }} />
      <div
        data-fit={name ?? `clipping ${masthead}`}
        style={{ position: "absolute", inset: 0, background: NEWSPRINT, clipPath: tornClip((width + 7) % 31, 20, 1.6), filter: DROP, padding: "30px 38px", boxSizing: "border-box", color: C.inkDeep, overflow: "hidden" }}
      >
        <Halftone dot={1.2} pitch={7} alpha={0.1} />
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", borderBottom: `2px solid ${C.inkDeep}`, paddingBottom: 8 }}>
          <div style={{ fontFamily: PLAYFAIR, fontWeight: 700, fontSize: 30 }}>{masthead}</div>
          {date ? <Label size={14} spacing={3} color={C.inkDeep}>{date}</Label> : null}
        </div>
        <div style={{ fontFamily: PLAYFAIR, fontWeight: 700, fontSize: 52, lineHeight: 1.08, marginTop: 16, letterSpacing: -0.5 }}>
          {parts.length === 2 ? (
            <>
              {parts[0]}
              <span style={{ position: "relative", display: "inline-block" }}>
                <span aria-hidden data-mark style={{ position: "absolute", left: -4, right: -4, top: "16%", bottom: "6%", background: C.amber, zIndex: -1 }} />
                {highlight}
              </span>
              {parts[1]}
            </>
          ) : (
            headline
          )}
        </div>
        {body ? <div style={{ fontFamily: PT_SERIF, fontSize: 20, lineHeight: 1.35, marginTop: 16, textAlign: "justify", opacity: 0.8 }}>{body}</div> : null}
      </div>
    </Rise>
  );
};
