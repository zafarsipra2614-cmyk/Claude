import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig, spring } from "remotion";
import { C, DROP, Grain, Paper } from "../shared/system";
import { ARIAL, PaperBand, Stamp, Strike, Typewriter, tornClip } from "../shared/pieces";
import { PLAYFAIR, PT_SERIF, TYPEWRITER } from "../shared/fonts";
import { CUE } from "../shared/timing";
import { FitCheck, Kicker, Label, Pt, Rise, along, clamp, pathOf, ramp } from "./kit";

const BG = "background.jpg";

const Frame: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <AbsoluteFill data-frame style={{ backgroundColor: C.paper, overflow: "hidden" }}>
    <Paper asset={BG} />
    {children}
    <Grain />
    <FitCheck />
  </AbsoluteFill>
);

/* ------------------------------------------------------------------ */
/* 1. HOOK — two stacks of share certificates; one is taller than it   */
/*    should be able to be.                                             */
/* ------------------------------------------------------------------ */

const Certificate: React.FC<{ excess?: boolean; seed: number }> = ({ excess, seed }) => (
  <div
    data-fit="certificate"
    style={{
      width: "100%",
      height: "100%",
      background: C.card,
      border: `3px solid ${excess ? C.red : "rgba(26,26,26,0.55)"}`,
      outline: `1px solid ${excess ? C.red : "rgba(26,26,26,0.35)"}`,
      outlineOffset: -9,
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 26px",
      boxSizing: "border-box",
      transform: `rotate(${((seed * 37) % 7) * 0.25 - 0.8}deg)`,
    }}
  >
    <div style={{ fontFamily: PLAYFAIR, fontSize: 22, letterSpacing: 3, color: excess ? C.red : C.inkDeep }}>
      SHARE CERTIFICATE
    </div>
    <div style={{ fontFamily: PT_SERIF, fontSize: 18, color: excess ? C.red : "rgba(22,17,13,0.6)" }}>№ {1000 + seed * 17}</div>
  </div>
);

export const HookScene: React.FC = () => {
  const STEP = 50;
  const H = 46;
  const BASE = 150;
  const leftStart = 6;
  const rightStart = CUE["s1.stackB"];
  const frame = useCurrentFrame();
  return (
    <Frame>
      {Array.from({ length: 10 }).map((_, i) => (
        <Rise key={`a${i}`} start={leftStart + i * 3} dur={22} dist={260} left={330} bottom={BASE + i * STEP} width={470} height={H} z={10 + i}>
          <Certificate seed={i} />
        </Rise>
      ))}
      {Array.from({ length: 14 }).map((_, i) => (
        <Rise key={`b${i}`} start={rightStart + i * 4} dur={22} dist={260} left={1120} bottom={BASE + i * STEP} width={470} height={H} z={10 + i}>
          <Certificate seed={i + 20} excess={i >= 10} />
        </Rise>
      ))}
      {/* the 100% line both stacks share */}
      <div
        style={{
          position: "absolute",
          left: 250,
          width: interpolate(ramp(frame, CUE["s1.labelA"], CUE["s1.labelA"] + 20), [0, 1], [0, 1420]),
          bottom: BASE + 10 * STEP - 2,
          borderTop: `4px dashed ${C.ink}`,
          opacity: 0.55,
          zIndex: 30,
        }}
      />
      <Stamp startFrame={CUE["s1.question"]} x={0} y={-330} rotate={-3} title="HOW?" width={260} zIndex={32} />
      <PaperBand startFrame={0} endFrame={26} height={210} bottom={-60}>
        <div style={{ position: "absolute", left: 425, top: 62, width: 400, textAlign: "center" }}>
          <Label size={30} color={C.ink} spacing={4}>AVAILABLE TO TRADE</Label>
        </div>
        <div style={{ position: "absolute", left: 1215, top: 62, width: 400, textAlign: "center" }}>
          <Label size={30} color={C.red} spacing={4}>ALREADY SOLD</Label>
        </div>
      </PaperBand>
    </Frame>
  );
};

/* ------------------------------------------------------------------ */
/* 2. STORE — a mall storefront, stamped by Wall Street.               */
/* ------------------------------------------------------------------ */

const GameCases: React.FC<{ seed: number }> = ({ seed }) => {
  const colors = [C.ink, C.orange, C.amber, C.red, "#6B6257"];
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "flex-end", height: 92 }}>
      {Array.from({ length: 9 }).map((_, i) => (
        <div
          key={i}
          style={{
            width: 34,
            height: 78 + ((i * seed) % 3) * 6,
            background: colors[(i + seed) % colors.length],
            boxShadow: "inset 4px 0 0 rgba(255,255,255,0.18)",
          }}
        />
      ))}
    </div>
  );
};

const ReasonIcon: React.FC<{ kind: string }> = ({ kind }) => (
  <svg width={76} height={76} viewBox="0 0 76 76">
    {kind === "download" ? (
      <g stroke={C.ink} strokeWidth={7} fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d="M 38 8 L 38 44 M 22 30 L 38 46 L 54 30" />
        <path d="M 10 50 L 10 66 L 66 66 L 66 50" />
      </g>
    ) : kind === "mall" ? (
      <g>
        <path d="M 6 66 L 6 30 L 38 10 L 70 30 L 70 66 Z" fill={C.ink} />
        <rect x={30} y={42} width={16} height={24} fill={C.card} />
        <path d="M 52 40 L 52 60 M 45 53 L 52 60 L 59 53" stroke={C.red} strokeWidth={6} fill="none" strokeLinecap="round" strokeLinejoin="round" />
      </g>
    ) : (
      <g stroke={C.red} strokeWidth={7} fill="none" strokeLinecap="round" strokeLinejoin="round">
        <path d="M 8 14 L 30 38 L 44 28 L 68 60" />
        <path d="M 50 60 L 68 60 L 68 42" />
      </g>
    )}
  </svg>
);

/** One of the reasons the market had written the company off. */
const ReasonCard: React.FC<{ start: number; top: number; icon: string; title: [string, string]; sub: string; figure?: string }> = ({ start, top, icon, title, sub, figure }) => (
  <Rise start={start} dur={26} dist={240} left={80} top={top} width={420} height={176} rotate={[-1, 0.8, -0.6][Math.round(top / 200) % 3]} z={14}>
    <div data-fit="reason card" style={{ position: "absolute", inset: 0, background: C.card, padding: "24px 26px", boxSizing: "border-box", display: "flex", gap: 22, alignItems: "center", overflow: "hidden" }}>
      <ReasonIcon kind={icon} />
      <div style={{ minWidth: 0 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 28, lineHeight: 1.08, color: C.ink, whiteSpace: "nowrap" }}>
          {title[0]}
          <br />
          {title[1]}
        </div>
        {figure ? (
          <div style={{ fontFamily: ARIAL, fontSize: 46, color: C.red, marginTop: 6, lineHeight: 1 }}>{figure}</div>
        ) : (
          <div style={{ fontFamily: PT_SERIF, fontSize: 24, color: "rgba(22,17,13,0.72)", marginTop: 8, whiteSpace: "nowrap" }}>{sub}</div>
        )}
      </div>
    </div>
  </Rise>
);

export const StoreScene: React.FC = () => {
  const frame = useCurrentFrame();
  const sign = ramp(frame, CUE["s2.sign"], CUE["s2.sign"] + 10);
  const flicker = frame > CUE["s2.stamp"] ? (Math.floor(frame / 5) % 4 === 0 ? 0.45 : 1) : 1;
  return (
    <Frame>
      <Kicker start={CUE["s2.caption"]} text="WALL STREET'S VERDICT" sub="A MALL RETAILER IN THE STREAMING ERA" />
      <Rise start={CUE["s2.store"] + 4} dur={34} left={560} top={290} width={1000} height={620} rotate={-0.6} stroke={{ x: 26, y: 10 }}>
        <div data-fit="storefront" style={{ position: "absolute", inset: 0, background: "#2A241D" }} />
        {/* sign band */}
        <div
          style={{
            position: "absolute",
            left: 0,
            right: 0,
            top: 0,
            height: 130,
            background: C.inkDeep,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            borderBottom: `8px solid ${C.red}`,
          }}
        >
          <div style={{ fontFamily: ARIAL, fontSize: 88, letterSpacing: 4, color: C.paper, opacity: sign * flicker }}>GAMESTOP</div>
        </div>
        {/* two windows and a door */}
        {[40, 610].map((x, w) => (
          <div key={x} style={{ position: "absolute", left: x, top: 170, width: 350, height: 400, background: "#F0ECE2", border: "6px solid #14100C" }}>
            {[0, 1, 2].map((r) => (
              <div key={r} style={{ position: "absolute", left: 22, top: 22 + r * 124, borderBottom: "6px solid #8B7F6F", paddingBottom: 2 }}>
                <GameCases seed={w * 3 + r + 1} />
              </div>
            ))}
          </div>
        ))}
        <div style={{ position: "absolute", left: 420, top: 200, width: 160, height: 420, background: "#14100C", border: "6px solid #3A3229" }}>
          <div style={{ position: "absolute", right: 18, top: 200, width: 10, height: 50, background: C.amber }} />
        </div>
      </Rise>
      <Stamp startFrame={CUE["s2.stamp"]} x={650} y={-330} rotate={-6} title="DYING" sub="CONSENSUS" width={420} zIndex={30} />
      {/* floor shadow so the store stands on something */}
      <div style={{ position: "absolute", left: 520, top: 900, width: 1100, height: 60, borderRadius: "50%", background: "radial-gradient(ellipse at center, rgba(55,45,31,0.32), transparent 70%)", zIndex: 9 }} />
      <ReasonCard start={CUE["s2.r1"]} top={300} icon="download" title={["GAMES WENT", "DIGITAL"]} sub="downloads replace discs" />
      <ReasonCard start={CUE["s2.r2"]} top={505} icon="mall" title={["MALL TRAFFIC", "FALLING"]} sub="fewer shoppers walk in" />
      <ReasonCard start={CUE["s2.r3"]} top={710} icon="loss" title={["NET LOSS", "FISCAL 2019"]} sub="" figure="$471M" />
    </Frame>
  );
};

/* ------------------------------------------------------------------ */
/* 3. MECHANISM — borrow, sell, buy back. Then the 140% bar.           */
/* ------------------------------------------------------------------ */

const StepCard: React.FC<{ n: string; title: string; sub: string; highlight?: number }> = ({ n, title, sub, highlight = 0 }) => (
  <div data-fit="step card" style={{ width: "100%", height: "100%", background: C.card, padding: "34px 34px", boxSizing: "border-box", clipPath: tornClip(Number(n) * 5, 14, 1.6) }}>
    <div style={{ fontFamily: ARIAL, fontSize: 96, color: C.red, lineHeight: 1 }}>{n}</div>
    <div style={{ fontFamily: ARIAL, fontSize: 58, letterSpacing: -1, color: C.ink, marginTop: 18, whiteSpace: "nowrap" }}>{title}</div>
    <div style={{ position: "relative", display: "inline-block", marginTop: 16 }}>
      <span
        aria-hidden
        style={{ position: "absolute", left: -6, right: -6, top: "12%", bottom: "4%", background: C.amber, transformOrigin: "left center", transform: `scaleX(${highlight})` }}
      />
      <span style={{ position: "relative", fontFamily: PT_SERIF, fontSize: 30, color: C.inkDeep }}>{sub}</span>
    </div>
  </div>
);

export const MechanismScene: React.FC = () => {
  const frame = useCurrentFrame();
  const out = CUE["s3.cardsOut"];
  const hl = ramp(frame, CUE["s3.less"], CUE["s3.less"] + 14, Easing.out(Easing.cubic));
  const arrowA = ramp(frame, CUE["s3.sell"] - 6, CUE["s3.sell"] + 8);
  const arrowB = ramp(frame, CUE["s3.buyback"] - 6, CUE["s3.buyback"] + 8);
  const arrowsOut = 1 - ramp(frame, out, out + 12);

  // bars: 100% float vs 140% sold short
  const UNIT = 4.2; // px per percent
  const BASE = 200;
  const floatGrow = ramp(frame, CUE["s3.barFloat"], CUE["s3.barFloat"] + 26, Easing.out(Easing.cubic));
  const shortT = ramp(frame, CUE["s3.barShort"], CUE["s3.countEnd"], Easing.out(Easing.cubic));
  const pct = Math.round(140 * shortT);
  const over = ramp(frame, CUE["s3.overflow"], CUE["s3.overflow"] + 16, Easing.out(Easing.cubic));
  const barsOn = frame >= CUE["s3.barFloat"] - 2;

  const cards = [
    { n: "1", title: "BORROW", sub: "shares from a lender", at: CUE["s3.borrow"], x: 150 },
    { n: "2", title: "SELL", sub: "them at today's price", at: CUE["s3.sell"], x: 720 },
    { n: "3", title: "BUY BACK", sub: "later — for less", at: CUE["s3.buyback"], x: 1290 },
  ];
  return (
    <Frame>
      <Kicker start={6} text="THE SHORT SALE" sub="HOW A HEDGE FUND BETS ON A FALL" />
      {cards.map((c, i) => (
        <Rise key={`ex${c.n}`} start={c.at + 12} dur={24} dist={160} left={c.x + 10} top={700} width={460} height={110} rotate={[0.8, -0.6, 0.5][i]} exit={out + i * 3} z={13}>
          <div data-fit="example chip" style={{ position: "absolute", inset: 0, background: i === 2 ? C.ink : C.paper, border: `4px solid ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "center", gap: 16, padding: "0 22px", boxSizing: "border-box" }}>
            <Label size={22} spacing={3} color={i === 2 ? "rgba(239,235,224,0.75)" : undefined}>{["EXAMPLE", "SELL AT", "BUY AT $10"][i]}</Label>
            <div style={{ fontFamily: ARIAL, fontSize: 42, color: i === 2 ? C.amber : C.ink, whiteSpace: "nowrap" }}>{["1 SHARE", "$20", "KEEP $10"][i]}</div>
          </div>
        </Rise>
      ))}
      {cards.map((c, i) => (
        <Rise key={c.n} start={c.at} dur={28} left={c.x} top={330} width={480} height={330} rotate={[-1, 0.6, -0.4][i]} exit={out + i * 3}>
          <StepCard n={c.n} title={c.title} sub={c.sub} highlight={i === 2 ? hl : 0} />
        </Rise>
      ))}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 20, opacity: arrowsOut }}>
        {[
          { x: 638, t: arrowA },
          { x: 1208, t: arrowB },
        ].map((a) => (
          <g key={a.x}>
            <path d={`M ${a.x} 500 L ${a.x + 70} 500`} stroke={C.red} strokeWidth={9} strokeLinecap="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - a.t} />
            <path d={`M ${a.x + 50} 482 L ${a.x + 72} 500 L ${a.x + 50} 518`} stroke={C.red} strokeWidth={9} strokeLinecap="round" strokeLinejoin="round" fill="none" opacity={a.t > 0.9 ? 1 : 0} />
          </g>
        ))}
      </svg>

      {barsOn ? (
        <>
          {/* float bar */}
          <div style={{ position: "absolute", left: 560, bottom: BASE, width: 300, height: 100 * UNIT * floatGrow, background: C.ink, zIndex: 14, filter: DROP }} />
          {/* short bar, the first 100% in orange, the excess in red */}
          <div style={{ position: "absolute", left: 1060, bottom: BASE, width: 300, height: Math.min(pct, 100) * UNIT, background: C.orange, zIndex: 14, filter: DROP }} />
          <div
            style={{
              position: "absolute",
              left: 1060,
              bottom: BASE + 100 * UNIT,
              width: 300,
              height: Math.max(0, pct - 100) * UNIT,
              background: C.red,
              zIndex: 14,
              backgroundImage: "repeating-linear-gradient(-45deg, rgba(255,255,255,0.18) 0 10px, transparent 10px 22px)",
            }}
          />
          <div style={{ position: "absolute", left: 560, width: 300, bottom: BASE + 100 * UNIT * floatGrow + 18, textAlign: "center", zIndex: 21, opacity: floatGrow }}>
            <div style={{ fontFamily: ARIAL, fontSize: 64, color: C.ink }}>100%</div>
          </div>
          <div style={{ position: "absolute", left: 1060, width: 300, bottom: BASE + pct * UNIT + 18, textAlign: "center", zIndex: 21, opacity: shortT > 0 ? 1 : 0 }}>
            <div style={{ fontFamily: ARIAL, fontSize: 78, color: C.red, fontVariantNumeric: "tabular-nums" }}>~{pct}%</div>
          </div>
          {/* 100% line runs across both bars */}
          <div style={{ position: "absolute", left: 500, width: 920 * over, bottom: BASE + 100 * UNIT, borderTop: `5px dashed ${C.ink}`, zIndex: 18, opacity: 0.7 }} />
          <div style={{ position: "absolute", left: 1400, bottom: BASE + 100 * UNIT + 40, opacity: over, zIndex: 21 }}>
            <Label size={28} color={C.red} spacing={3}>MORE THAN EXISTS</Label>
            <Label size={22} spacing={3} style={{ marginTop: 8 }}>TO BE BOUGHT BACK</Label>
          </div>
        </>
      ) : null}

      <PaperBand startFrame={0} endFrame={24} height={240} bottom={-50} rotate={-0.5}>
        {barsOn ? (
          <>
            <div style={{ position: "absolute", left: 620, top: 66, width: 300, textAlign: "center", opacity: floatGrow }}>
              <Label size={26} color={C.ink} spacing={4}>FLOAT</Label>
            </div>
            <div style={{ position: "absolute", left: 1120, top: 66, width: 300, textAlign: "center", opacity: shortT > 0 ? 1 : 0 }}>
              <Label size={26} color={C.red} spacing={4}>SOLD SHORT</Label>
            </div>
          </>
        ) : null}
      </PaperBand>
      <div style={{ position: "absolute", right: 70, bottom: 26, zIndex: 26, opacity: barsOn ? 0.6 : 0 }}>
        <Label size={18} spacing={3}>SHORT INTEREST AS % OF FLOAT · MID-JANUARY 2021 · WIDELY REPORTED ESTIMATE</Label>
      </div>
    </Frame>
  );
};

/* ------------------------------------------------------------------ */
/* 4. FORUM — the forum card, then the feedback loop it spotted.       */
/* ------------------------------------------------------------------ */

const Node: React.FC<{ x: number; y: number; at: number; text: string; red?: boolean }> = ({ x, y, at, text, red }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - at, fps, config: { damping: 13, mass: 0.6, stiffness: 170 }, durationInFrames: 24 });
  const o = interpolate(frame, [at, at + 6], [0, 1], clamp);
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        top: y,
        transform: `translate(-50%, -50%) scale(${interpolate(s, [0, 1], [0.6, 1])}) rotate(${red ? 1 : -1}deg)`,
        opacity: o,
        background: red ? C.red : C.ink,
        color: C.paper,
        padding: "22px 30px",
        fontFamily: ARIAL,
        fontSize: 36,
        letterSpacing: 1,
        whiteSpace: "nowrap",
        filter: DROP,
        zIndex: 22,
      }}
    >
      {text}
    </div>
  );
};

/** Each lap of the loop leaves the price a step higher. */
const PriceLadder: React.FC<{ start: number }> = ({ start }) => {
  const frame = useCurrentFrame();
  const H = [36, 62, 96, 136, 184];
  const X0 = 1090, W = 96, GAP = 40, BASE = 1080 - 120;
  const tops = H.map((h, i) => ({ x: X0 + i * (W + GAP) + W / 2, y: BASE - h - 26 }));
  const arrow = ramp(frame, start + 10, start + 10 + H.length * 7);
  return (
    <>
      {H.map((h, i) => {
        const g = ramp(frame, start + i * 7, start + i * 7 + 14, Easing.out(Easing.cubic));
        return (
          <div key={i} style={{ position: "absolute", left: X0 + i * (W + GAP), top: BASE - h * g, width: W, height: h * g, background: i === H.length - 1 ? C.red : C.orange, filter: DROP, zIndex: 16 }} />
        );
      })}
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 17 }}>
        <path d={pathOf(tops)} stroke={C.ink} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - arrow} />
        <path d={`M ${tops[4].x - 22} ${tops[4].y - 4} L ${tops[4].x + 2} ${tops[4].y - 20} L ${tops[4].x + 6} ${tops[4].y + 8}`} stroke={C.ink} strokeWidth={6} strokeLinecap="round" strokeLinejoin="round" fill="none" opacity={arrow > 0.95 ? 1 : 0} />
      </svg>
      <div style={{ position: "absolute", left: X0, width: 5 * W + 4 * GAP, top: BASE + 22, textAlign: "center", opacity: ramp(frame, start, start + 12), zIndex: 18 }}>
        <Label size={22} color={C.ink} spacing={4}>EVERY LAP, A HIGHER PRICE</Label>
      </div>
    </>
  );
};

export const ForumScene: React.FC = () => {
  const frame = useCurrentFrame();
  const math = ramp(frame, CUE["s4.math"], CUE["s4.math"] + 16, Easing.out(Easing.cubic));
  const a1 = ramp(frame, CUE["s4.n2"] - 10, CUE["s4.n2"] + 4);
  const a2 = ramp(frame, CUE["s4.n3"] - 10, CUE["s4.n3"] + 4);
  const a3 = ramp(frame, CUE["s4.loop"] - 8, CUE["s4.loop"] + 16);
  // triangle of nodes on the right
  const N = [
    { x: 1390, y: 300 },
    { x: 1690, y: 690 },
    { x: 1090, y: 690 },
  ];
  const arc = (a: Pt, b: Pt, bend: number) => {
    const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
    const dx = b.x - a.x, dy = b.y - a.y;
    return `M ${a.x} ${a.y} Q ${mx - dy * bend} ${my + dx * bend} ${b.x} ${b.y}`;
  };
  const lines = [
    { d: arc(N[0], N[1], -0.18), t: a1 },
    { d: arc(N[1], N[2], -0.18), t: a2 },
    { d: arc(N[2], N[0], -0.18), t: a3 },
  ];
  return (
    <Frame>
      <Rise start={CUE["s4.card"]} dur={30} left={120} top={190} width={760} height={640} rotate={-1.2} stroke={{ x: -26, y: 10 }}>
        <div data-fit="forum card" style={{ position: "absolute", inset: 0, background: C.card, padding: "40px 46px", boxSizing: "border-box" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 20 }}>
            <div style={{ width: 70, height: 70, borderRadius: "50%", background: C.orange }} />
            <div>
              <Label size={22} spacing={4}>ONLINE FORUM · 2021</Label>
              <div style={{ fontFamily: ARIAL, fontSize: 50, color: C.ink, letterSpacing: -1, marginTop: 6, opacity: ramp(frame, CUE["s4.name"], CUE["s4.name"] + 10) }}>
                r/wallstreetbets
              </div>
            </div>
          </div>
          <div style={{ height: 4, background: C.ink, margin: "30px 0 34px", opacity: 0.8 }} />
          {/* the math, as a worked sum */}
          {[
            ["Shares sold short", "~140%"],
            ["Shares available to buy back", "100%"],
          ].map(([k, v], i) => (
            <div key={k} style={{ display: "flex", justifyContent: "space-between", fontFamily: PT_SERIF, fontSize: 34, color: C.inkDeep, marginBottom: 22, opacity: ramp(frame, CUE["s4.name"] + 14 + i * 12, CUE["s4.name"] + 26 + i * 12) }}>
              <span>{k}</span>
              <span style={{ fontFamily: ARIAL }}>{v}</span>
            </div>
          ))}
          <div style={{ height: 3, background: C.inkDeep, opacity: 0.6, margin: "6px 0 24px" }} />
          <div style={{ position: "relative", display: "inline-block" }}>
            <span aria-hidden style={{ position: "absolute", left: -8, right: -8, top: "10%", bottom: "4%", background: C.amber, transformOrigin: "left center", transform: `scaleX(${math})` }} />
            <span style={{ position: "relative", fontFamily: TYPEWRITER, fontSize: 44, color: C.inkDeep }}>Someone has to buy.</span>
          </div>
        </div>
      </Rise>

      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 18 }}>
        <g>
          {lines.map((l, i) => (
            <path key={i} d={l.d} stroke={i === 2 ? C.red : C.ink} strokeWidth={8} strokeLinecap="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - l.t} opacity={0.85} />
          ))}
        </g>
      </svg>
      <Node x={N[0].x} y={N[0].y} at={CUE["s4.n1"]} text="TRADERS BUY" />
      <Node x={N[1].x} y={N[1].y} at={CUE["s4.n2"]} text="PRICE RISES" />
      <Node x={N[2].x} y={N[2].y} at={CUE["s4.n3"]} text="SHORTS FORCED TO BUY" red />
      <Stamp startFrame={CUE["s4.loop"] + 6} x={680} y={-370} rotate={-5} title="AT ANY PRICE" width={400} zIndex={30} />
      <PriceLadder start={CUE["s4.lap"]} />
    </Frame>
  );
};

/* ------------------------------------------------------------------ */
/* 5. SQUEEZE — the January chart, drawing itself up to $347.          */
/* ------------------------------------------------------------------ */

// Daily closes, January 2021 (pre-2022 split), NYSE: GME.
const JAN = [17.25, 17.37, 18.36, 18.08, 17.69, 19.94, 19.95, 31.4, 39.91, 35.5, 39.36, 39.12, 43.03, 65.01, 76.79, 147.98, 347.51];
const AFTER = [347.51, 193.6, 325.0, 225.0, 90.0, 92.41, 53.5];

const CH = { left: 300, right: 1560, top: 210, bottom: 860, max: 380 };
const yOf = (v: number) => CH.bottom - (v / CH.max) * (CH.bottom - CH.top);

export const SqueezeScene: React.FC = () => {
  const frame = useCurrentFrame();
  const axis = ramp(frame, CUE["s5.axis"], CUE["s5.axis"] + 20);
  const t = ramp(frame, CUE["s5.drawStart"], CUE["s5.drawEnd"], Easing.in(Easing.quad));
  const pts: Pt[] = JAN.map((v, i) => ({ x: CH.left + (i / (JAN.length - 1)) * (CH.right - CH.left), y: yOf(v) }));
  const tip = along(pts, t);
  const v = JAN[tip.i] + (JAN[tip.i + 1] - JAN[tip.i]) * tip.f;
  const area = `${pathOf(pts)} L ${CH.right} ${CH.bottom} L ${CH.left} ${CH.bottom} Z`;
  const low = ramp(frame, CUE["s5.low"], CUE["s5.low"] + 12);
  return (
    <Frame>
      <Kicker start={4} text="GME · JANUARY 2021" sub="DAILY CLOSING PRICE, PER SHARE" />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 16 }}>
        <defs>
          <clipPath id="reveal">
            <rect x={0} y={0} width={tip.x} height={1080} />
          </clipPath>
        </defs>
        {[100, 200, 300].map((g) => (
          <g key={g} opacity={axis * 0.5}>
            <line x1={CH.left} x2={CH.right} y1={yOf(g)} y2={yOf(g)} stroke={C.ink} strokeWidth={2} strokeDasharray="4 10" />
            <text x={CH.left - 24} y={yOf(g) + 10} textAnchor="end" fontFamily={ARIAL} fontSize={28} fill={C.ink}>${g}</text>
          </g>
        ))}
        <path d={area} fill={C.orange} opacity={0.16} clipPath="url(#reveal)" />
        <path d={pathOf(pts)} stroke={C.orange} strokeWidth={9} strokeLinejoin="round" strokeLinecap="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} style={{ filter: DROP }} />
        {t > 0 ? <circle cx={tip.x} cy={tip.y} r={13} fill={C.red} /> : null}
      </svg>
      {/* starting price */}
      <div style={{ position: "absolute", left: CH.left + 10, top: yOf(17.25) - 110, opacity: low, zIndex: 22 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 56, color: C.ink }}>$17.25</div>
        <Label size={22} spacing={4}>JAN 4</Label>
      </div>
      {/* running price at the tip */}
      {t > 0.04 && t < 1 ? (
        <div style={{ position: "absolute", left: tip.x - 40, top: tip.y - 96, transform: "translateX(-100%)", zIndex: 22, fontFamily: ARIAL, fontSize: 60, color: C.red, fontVariantNumeric: "tabular-nums" }}>
          ${v.toFixed(2)}
        </div>
      ) : null}
      <Stamp startFrame={CUE["s5.peak"]} x={250} y={-270} rotate={-4} title="$347.51" sub="CLOSE · JAN 27" width={540} zIndex={30} />
      <PaperBand startFrame={0} endFrame={24} height={210} bottom={-60} rotate={-0.4}>
        {[
          { i: 0, l: "JAN 4" },
          { i: 7, l: "JAN 13" },
          { i: 13, l: "JAN 22" },
          { i: 16, l: "JAN 27" },
        ].map((d) => (
          <div key={d.l} style={{ position: "absolute", left: 60 + CH.left + (d.i / (JAN.length - 1)) * (CH.right - CH.left), top: 56, transform: "translateX(-50%)" }}>
            <Label size={24} color={C.ink} spacing={3}>{d.l}</Label>
          </div>
        ))}
        <div style={{ position: "absolute", right: 120, top: 112 }}>
          <Label size={16} spacing={3}>PRICES BEFORE THE 2022 4-FOR-1 SPLIT</Label>
        </div>
      </PaperBand>
    </Frame>
  );
};

/* ------------------------------------------------------------------ */
/* 6. MELVIN — a fund's January, on a ledger.                          */
/* ------------------------------------------------------------------ */

export const MelvinScene: React.FC = () => {
  const frame = useCurrentFrame();
  const drop = ramp(frame, CUE["s6.drop"], CUE["s6.stamp"] + 6, Easing.inOut(Easing.cubic));
  const remain = 1 - 0.53 * drop;
  const nameOn = ramp(frame, CUE["s6.name"], CUE["s6.name"] + 12);
  return (
    <Frame>
      <Rise start={CUE["s6.ledger"] + 2} dur={32} left={260} top={170} width={1400} height={640} rotate={-0.7} stroke={{ x: -26, y: 10 }}>
        <div data-fit="ledger" style={{ position: "absolute", inset: 0, background: C.card, padding: "54px 70px", boxSizing: "border-box", backgroundImage: "repeating-linear-gradient(180deg, transparent 0 63px, rgba(26,26,26,0.08) 63px 65px)" }}>
          <Label size={24} spacing={6}>HEDGE FUND · RETURN, JANUARY 2021</Label>
          <div style={{ fontFamily: PLAYFAIR, fontSize: 104, color: C.inkDeep, letterSpacing: -2, marginTop: 10, opacity: nameOn }}>Melvin Capital</div>
          <div style={{ height: 4, background: C.inkDeep, margin: "26px 0 56px", opacity: 0.7 }} />
          <div style={{ position: "relative", height: 120, width: 1100 }}>
            <div style={{ position: "absolute", inset: 0, border: `4px dashed rgba(26,26,26,0.4)` }} />
            <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${remain * 100}%`, background: C.ink }} />
            <div
              style={{
                position: "absolute",
                left: `${remain * 100}%`,
                top: 0,
                bottom: 0,
                width: `${(1 - remain) * 100}%`,
                background: C.red,
                opacity: 0.85,
                backgroundImage: "repeating-linear-gradient(-45deg, rgba(255,255,255,0.22) 0 10px, transparent 10px 22px)",
              }}
            />
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", width: 1100, marginTop: 20 }}>
            <Label size={24} color={C.ink} spacing={4}>JAN 1</Label>
            <Label size={24} color={C.red} spacing={4}>JAN 31</Label>
          </div>
        </div>
      </Rise>
      <Stamp startFrame={CUE["s6.stamp"]} x={520} y={-350} rotate={-6} title="−53%" sub="IN ONE MONTH" width={500} zIndex={30} />
      <Rise start={CUE["s6.rescue"]} dur={26} dist={300} left={1090} top={730} width={700} height={240} rotate={1.4} stroke={{ x: 22, y: 10 }} z={24}>
        <div data-fit="rescue card" style={{ position: "absolute", inset: 0, background: C.card, padding: "28px 36px", boxSizing: "border-box", overflow: "hidden" }}>
          <Label size={22} color={C.red} spacing={4}>JAN 25, 2021 · EMERGENCY FUNDING</Label>
          <div style={{ fontFamily: ARIAL, fontSize: 64, color: C.ink, marginTop: 12, lineHeight: 1, whiteSpace: "nowrap" }}>$2.75 BILLION</div>
          <div style={{ fontFamily: PT_SERIF, fontSize: 28, color: C.inkDeep, marginTop: 14, whiteSpace: "nowrap" }}>from Citadel and Point72</div>
        </div>
      </Rise>
      <div style={{ position: "absolute", left: 270, top: 900, zIndex: 20, opacity: 0.6 }}>
        <Label size={18} spacing={3}>FUND RETURN AS REPORTED · JANUARY 2021</Label>
      </div>
    </Frame>
  );
};

/* ------------------------------------------------------------------ */
/* 7. HALT — the buy button goes dead; the price falls; Congress.      */
/* ------------------------------------------------------------------ */

export const HaltScene: React.FC = () => {
  const frame = useCurrentFrame();
  const dis = frame >= CUE["s7.disable"];
  const grey = ramp(frame, CUE["s7.disable"], CUE["s7.disable"] + 8);
  const CR = { left: 980, right: 1720, top: 300, bottom: 800, max: 380 };
  const y2 = (v: number) => CR.bottom - (v / CR.max) * (CR.bottom - CR.top);
  const pts: Pt[] = AFTER.map((v, i) => ({ x: CR.left + (i / (AFTER.length - 1)) * (CR.right - CR.left), y: y2(v) }));
  const t = ramp(frame, CUE["s7.crash"], CUE["s7.crash"] + 40, Easing.inOut(Easing.cubic));
  const chartOn = ramp(frame, CUE["s7.crash"] - 16, CUE["s7.crash"]);
  const end = along(pts, t);
  return (
    <Frame>
      <Kicker start={CUE["s7.date"]} text="JANUARY 28, 2021" sub="ROBINHOOD AND OTHER BROKERS RESTRICT BUYING" />
      <Rise start={CUE["s7.phone"] + 2} dur={32} left={300} top={250} width={430} height={780} rotate={-2} stroke={{ x: -26, y: 10, radius: 56 }}>
        <div style={{ position: "absolute", inset: 0, background: C.inkDeep, borderRadius: 56, padding: 22, boxSizing: "border-box" }}>
          <div data-fit="phone screen" style={{ width: "100%", height: "100%", background: "#F4F1EA", borderRadius: 38, padding: "48px 38px", boxSizing: "border-box" }}>
            <Label size={24} spacing={4}>GAMESTOP CORP</Label>
            <div style={{ fontFamily: ARIAL, fontSize: 82, color: C.ink, marginTop: 6 }}>GME</div>
            <svg width={360} height={120} style={{ marginTop: 18 }}>
              <path d="M 0 100 L 60 92 L 120 96 L 170 70 L 220 74 L 270 40 L 320 10 L 360 30" stroke={C.orange} strokeWidth={6} fill="none" strokeLinejoin="round" />
            </svg>
            <div
              style={{
                position: "relative",
                marginTop: 56,
                height: 104,
                borderRadius: 52,
                background: interpolate(grey, [0, 1], [0, 1]) > 0.5 ? "#B9B4AA" : C.orange,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontFamily: ARIAL,
                fontSize: 46,
                letterSpacing: 4,
                color: grey > 0.5 ? "#6D675E" : "#FFF",
              }}
            >
              <span style={{ position: "relative" }}>
                BUY
                {dis ? <Strike startFrame={CUE["s7.disable"] + 4} duration={8} thickness={8} /> : null}
              </span>
            </div>
            <div style={{ marginTop: 22, textAlign: "center", opacity: grey }}>
              <Label size={19} color={C.red} spacing={2}>POSITION CLOSING ONLY</Label>
            </div>
            <div style={{ height: 3, background: "rgba(26,26,26,0.15)", margin: "34px 0 22px" }} />
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
              <Label size={18} spacing={3}>INTRADAY HIGH</Label>
              <div style={{ fontFamily: ARIAL, fontSize: 40, color: C.ink }}>$483</div>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginTop: 12 }}>
              <Label size={18} spacing={3}>CLOSE</Label>
              <div style={{ fontFamily: ARIAL, fontSize: 40, color: C.red }}>$193.60</div>
            </div>
          </div>
        </div>
      </Rise>

      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 16, opacity: chartOn }}>
        <line x1={CR.left} x2={CR.right} y1={y2(347.51)} y2={y2(347.51)} stroke={C.ink} strokeWidth={2} strokeDasharray="4 10" opacity={0.5} />
        <text x={CR.left} y={y2(347.51) - 18} fontFamily={ARIAL} fontSize={26} fill={C.ink} opacity={0.7}>$347.51 · JAN 27</text>
        <path d={pathOf(pts)} stroke={C.red} strokeWidth={9} strokeLinejoin="round" strokeLinecap="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />
        {t > 0 ? <circle cx={end.x} cy={end.y} r={12} fill={C.red} /> : null}
        <text x={CR.right} y={y2(53.5) + 60} textAnchor="end" fontFamily={ARIAL} fontSize={44} fill={C.red} opacity={ramp(frame, CUE["s7.crash"] + 34, CUE["s7.crash"] + 44)}>$53.50 · FEB 4</text>
      </svg>
      <Stamp startFrame={CUE["s7.hearing"]} x={640} y={-170} rotate={-4} title="CONGRESS" sub="HEARING · FEB 18" width={560} zIndex={30} />
      <Rise start={CUE["s7.why"]} dur={26} dist={260} left={980} top={850} width={760} height={170} rotate={-0.8} z={20}>
        <div data-fit="why card" style={{ position: "absolute", inset: 0, background: C.card, padding: "24px 32px", boxSizing: "border-box", overflow: "hidden", borderLeft: `10px solid ${C.red}` }}>
          <Label size={22} color={C.red} spacing={4}>WHY THE BRAKES?</Label>
          <div style={{ fontFamily: PT_SERIF, fontSize: 28, lineHeight: 1.3, color: C.inkDeep, marginTop: 10 }}>
            Clearing deposits spiked. Robinhood was told to post about $3 billion overnight.
          </div>
        </div>
      </Rise>
    </Frame>
  );
};

/* ------------------------------------------------------------------ */
/* 8. CLOSER — typewriter, the answer to the hook.                     */
/* ------------------------------------------------------------------ */

export const CloserScene: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const s = spring({ frame: frame - CUE["s8.reveal"], fps, config: { damping: 12, mass: 0.6, stiffness: 200 }, durationInFrames: 26 });
  const revealO = interpolate(frame, [CUE["s8.reveal"], CUE["s8.reveal"] + 6], [0, 1], clamp);
  const rule = ramp(frame, CUE["s8.reveal"] + 12, CUE["s8.reveal"] + 30, Easing.out(Easing.cubic));
  const vig = ramp(frame, CUE["s8.vignette"], CUE["s8.vignette"] + 40, Easing.out(Easing.cubic));
  return (
    <Frame>
      <Rise start={0} dur={36} dist={340} left={210} top={120} width={1500} height={800} rotate={-1.2} z={11} style={{ filter: DROP, opacity: 0.62 }}>
        <div data-box="closer card" style={{ position: "absolute", inset: 0, background: C.card, clipPath: tornClip(41, 20, 2) }} />
      </Rise>
      <div data-inside="closer card" style={{ position: "absolute", left: 960, top: 230, width: 1300, transform: "translateX(-50%)", textAlign: "center", zIndex: 20 }}>
        <Typewriter
          text="Sell more shares than anyone can buy back,"
          startFrame={CUE["s8.line1Start"]}
          endFrame={CUE["s8.line1End"]}
          style={{ fontFamily: TYPEWRITER, fontSize: 46, color: "rgba(26,26,26,0.8)" }}
        />
      </div>
      <div data-inside="closer card" style={{ position: "absolute", left: 960, top: 360, width: 1560, transform: "translateX(-50%)", textAlign: "center", zIndex: 22 }}>
        <div style={{ opacity: revealO, transform: `scale(${interpolate(s, [0, 1], [1.4, 1])})` }}>
          <div style={{ fontFamily: ARIAL, fontSize: 116, letterSpacing: -2, color: C.red, whiteSpace: "nowrap", lineHeight: 1 }}>SOONER OR LATER</div>
        </div>
        <div style={{ height: 9, width: 640, background: C.red, margin: "26px auto 0", transform: `scaleX(${rule})` }} />
      </div>
      <div data-inside="closer card" style={{ position: "absolute", left: 960, top: 600, width: 1300, transform: "translateX(-50%)", textAlign: "center", zIndex: 22 }}>
        <Typewriter
          text="someone asks for them."
          startFrame={CUE["s8.line2Start"]}
          endFrame={CUE["s8.line2End"]}
          style={{ fontFamily: PLAYFAIR, fontStyle: "italic", fontSize: 66, color: C.inkDeep }}
        />
      </div>
      <div data-inside="closer card" style={{ position: "absolute", left: 960, top: 740, transform: "translateX(-50%)", zIndex: 22, opacity: ramp(frame, CUE["s8.vignette"], CUE["s8.vignette"] + 20) }}>
        <Label size={24} spacing={6}>GAMESTOP · JANUARY 2021</Label>
      </div>
      <AbsoluteFill
        aria-hidden
        style={{ background: "radial-gradient(circle at 50% 48%, transparent 38%, rgba(20,16,12,0.62) 100%)", opacity: vig, pointerEvents: "none", zIndex: 30 }}
      />
    </Frame>
  );
};
