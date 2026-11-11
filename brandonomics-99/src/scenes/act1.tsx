import React from "react";
import { Easing, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { CUE } from "../shared/timing";
import { Stamp } from "../shared/pieces";
import { Kicker } from "./kit";
import { ARIAL, C, Card, ChapterCard, DROP, Frame, Glyph, Headline, Icon, Label, PLAYFAIR, Rise, Tag, Tick, clamp, ramp, useIn } from "./lib";

/* 1 — Ten dollars. Nine ninety-nine. One cent apart. */
export const Hook: React.FC = () => {
  const frame = useCurrentFrame();
  const gap = ramp(frame, CUE["hook.gap"], CUE["hook.gap"] + 18, Easing.out(Easing.cubic));
  const lbl = useIn(CUE["hook.gap"] + 8);
  return (
    <Frame>
      <Tag x={330} y={330} w={560} price="$10.00" start={CUE["hook.a"]} rot={-2} />
      <Tag x={1030} y={330} w={560} price="$9.99" tone="red" start={CUE["hook.b"]} rot={2} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 16 }}>
        <path d="M 640 690 L 640 730 L 1340 730 L 1340 690" stroke={C.ink} strokeWidth={6} fill="none" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - gap} />
      </svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: 770, textAlign: "center", opacity: lbl, zIndex: 18 }}>
        <span style={{ fontFamily: ARIAL, fontSize: 84, color: C.red }}>1¢</span>
        <span style={{ fontFamily: ARIAL, fontSize: 40, letterSpacing: 8, color: C.ink, marginLeft: 22 }}>APART</span>
      </div>
    </Frame>
  );
};

/* 2 — Basically the same price… and yet your brain refuses. */
export const Brain: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const tilt = spring({ frame: frame - CUE["brain.tilt"], fps, config: { damping: 9, mass: 0.9, stiffness: 70 }, durationInFrames: 60 });
  const a = (-9 * tilt * Math.PI) / 180;
  const PX = 960, PY = 300, L = 540, DROPY = 300;
  const ends = [
    { x: PX - L * Math.cos(a), y: PY - L * Math.sin(a) },
    { x: PX + L * Math.cos(a), y: PY + L * Math.sin(a) },
  ];
  const stand = useIn(0, 18);
  const eq = useIn(CUE["brain.same"]);
  const slash = ramp(frame, CUE["brain.tilt"] + 4, CUE["brain.tilt"] + 14, Easing.out(Easing.cubic));
  const lbl = useIn(CUE["brain.label"]);
  const TW = 330;
  const TH = Math.round(TW * 0.46);
  return (
    <Frame>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 10, opacity: stand, filter: DROP }}>
        <path d={`M ${PX - 140} 960 L ${PX + 140} 960 L ${PX + 100} 920 L ${PX - 100} 920 Z`} fill={C.ink} />
        <rect x={PX - 12} y={PY} width={24} height={620} fill={C.ink} />
        <g transform={`rotate(${(a * 180) / Math.PI} ${PX} ${PY})`}>
          <rect x={PX - L - 10} y={PY - 10} width={2 * L + 20} height={20} rx={10} fill={C.inkDeep} />
        </g>
        <circle cx={PX} cy={PY} r={26} fill={C.red} />
        {ends.map((e, i) => (
          <g key={i}>
            <path d={`M ${e.x} ${e.y} L ${e.x - 200} ${e.y + DROPY} M ${e.x} ${e.y} L ${e.x + 200} ${e.y + DROPY}`} stroke="rgba(26,26,26,0.6)" strokeWidth={3} />
            <path d={`M ${e.x - 230} ${e.y + DROPY} Q ${e.x} ${e.y + DROPY + 70} ${e.x + 230} ${e.y + DROPY} Z`} fill={C.ink} />
          </g>
        ))}
      </svg>
      {ends.map((e, i) => (
        <Tag key={i} x={e.x - TW / 2 + 20} y={e.y + DROPY - TH - 4} w={TW} price={i ? "$9.99" : "$10.00"} tone={i ? "red" : "paper"} start={4 + i * 10} string={false} />
      ))}
      {/* "=" that gets struck when the brain refuses */}
      <div style={{ position: "absolute", left: PX - 70, top: 110, width: 140, textAlign: "center", opacity: eq, zIndex: 18 }}>
        <div style={{ position: "relative", fontFamily: ARIAL, fontSize: 130, lineHeight: 1, color: C.ink }}>
          =
          <div aria-hidden data-mark style={{ position: "absolute", left: 20, right: 20, top: "50%", height: 12, background: C.red, borderRadius: 6, transform: `rotate(-60deg) scaleX(${slash})` }} />
        </div>
      </div>
      <div style={{ position: "absolute", left: 1210, top: 120, width: 520, textAlign: "center", opacity: lbl, zIndex: 18 }}>
        <Label size={34} color={C.red} spacing={5}>FEELS CHEAPER</Label>
      </div>
    </Frame>
  );
};

/* 3 — That one cent changes cars, dresses, luxury. */
const StakeCard: React.FC<{ at: number; left: number; kind: "car" | "dress" | "bag"; w: number; lines: [string, string]; rot: number }> = ({ at, left, kind, w, lines, rot }) => (
  <Card start={at} left={left} top={420} width={470} height={500} name={`stake ${kind}`} rotate={rot} pad="44px 40px">
    <div style={{ height: 260, display: "flex", alignItems: "center", justifyContent: "center" }}>
      <Glyph kind={kind} width={w} />
    </div>
    <div style={{ height: 6, width: 70, background: C.red, margin: "34px auto 22px" }} />
    <div style={{ textAlign: "center", fontFamily: ARIAL, fontSize: 32, lineHeight: 1.15, color: C.ink }}>
      {lines[0]}
      <br />
      {lines[1]}
    </div>
  </Card>
);

export const Stakes: React.FC = () => (
  <Frame>
    <Icon kind="coin" start={CUE["stakes.coin"]} left={890} top={70} width={140} />
    <Headline at={CUE["stakes.title"]} text="ONE CENT CHANGES…" top={250} size={58} />
    <StakeCard at={CUE["stakes.car"]} left={175} kind="car" w={340} lines={["WHAT PEOPLE PAY", "FOR USED CARS"]} rot={-1} />
    <StakeCard at={CUE["stakes.dress"]} left={725} kind="dress" w={170} lines={["HOW MANY DRESSES", "A STORE SELLS"]} rot={0.6} />
    <StakeCard at={CUE["stakes.bag"]} left={1275} kind="bag" w={230} lines={["WHY LUXURY", "REFUSES IT"]} rot={-0.6} />
  </Frame>
);

/* 4 — Why does almost everything end in 99? */
const PRICES = ["$4.99", "$19.99", "$0.99", "$9.99", "$29.99", "$2.99", "$99.99", "$7.99"];
export const Why99: React.FC = () => (
  <Frame>
    <Kicker start={6} text="ALMOST EVERYTHING ENDS IN .99" />
    {PRICES.map((p, i) => (
      <Tag
        key={p}
        x={180 + (i % 4) * 400}
        y={300 + Math.floor(i / 4) * 230}
        w={330}
        price={p}
        start={CUE["why99.tags"] + i * 5}
        hl={[p.length - 3, p.length - 2, p.length - 1]}
        rot={[-3, 2, -1, 3, 2, -2, 3, -1][i]}
        tone={i === 3 ? "red" : "paper"}
      />
    ))}
    <Card start={CUE["why99.q"]} left={340} top={790} width={1240} height={150} name="question" pad="0 48px" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ fontFamily: ARIAL, fontSize: 46, color: C.ink, whiteSpace: "nowrap" }}>
        IS IT ACTUALLY <span style={{ color: C.red }}>SAVING YOU MONEY?</span>
      </div>
    </Card>
  </Frame>
);

/* 5 — Chapter 1 */
export const Ch1: React.FC = () => (
  <Frame>
    <ChapterCard n="1" title={<>THE LEFT-DIGIT<br />EFFECT</>} numAt={CUE["ch1.num"]} titleAt={CUE["ch1.title"]} />
  </Frame>
);

/* 6–8 — The big $9.99 that the next three scenes share. */
const BigPrice: React.FC<{ enterAt: number; circleAt?: number; dimAt?: number; liftAt?: number }> = ({ enterAt, circleAt, dimAt, liftAt }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const circle = circleAt === undefined ? 0 : ramp(frame, circleAt, circleAt + 14, Easing.out(Easing.cubic));
  const dim = dimAt === undefined ? 0 : ramp(frame, dimAt, dimAt + 16);
  const lift = liftAt === undefined ? 0 : spring({ frame: frame - liftAt, fps, config: { damping: 12, mass: 0.7, stiffness: 150 }, durationInFrames: 30 });
  const chars = ["$", "9", ".", "9", "9"];
  return (
    <Card start={enterAt} left={460} top={190} width={1000} height={430} name="big price" pad="0 60px" style={{ display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ position: "relative", fontFamily: ARIAL, fontSize: 240, lineHeight: 1, letterSpacing: 0, color: C.ink, whiteSpace: "nowrap" }}>
        {chars.map((ch, i) => (
          <span
            key={i}
            style={{
              display: "inline-block",
              position: "relative",
              color: i === 1 && (circle > 0 || lift > 0) ? C.red : C.ink,
              opacity: i === 1 ? 1 : 1 - dim * 0.75,
              transform: i === 1 ? `translateY(${-lift * 14}px) scale(${1 + lift * 0.1})` : undefined,
              margin: i === 1 ? `0 ${lift * 22}px` : undefined,
            }}
          >
            {ch}
            {i === 1 && circleAt !== undefined ? (
              <svg aria-hidden data-mark width={210} height={270} viewBox="0 0 210 270" style={{ position: "absolute", left: -38, top: -18, overflow: "visible" }}>
                <ellipse cx={105} cy={135} rx={96} ry={128} stroke={C.red} strokeWidth={9} fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - circle} transform="rotate(-8 105 135)" />
              </svg>
            ) : null}
          </span>
        ))}
      </div>
    </Card>
  );
};

export const Read: React.FC = () => {
  const frame = useCurrentFrame();
  const sweep = ramp(frame, CUE["read.sweep"], CUE["read.sweep"] + 26, Easing.inOut(Easing.cubic));
  return (
    <Frame push={0}>
      <Kicker start={CUE["read.kicker"]} text="INSIDE YOUR HEAD" />
      <BigPrice enterAt={CUE["read.price"]} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 18 }}>
        <path d="M 560 700 L 1360 700" stroke={C.red} strokeWidth={10} strokeLinecap="round" fill="none" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - sweep} />
        <path d="M 1330 676 L 1364 700 L 1330 724" stroke={C.red} strokeWidth={10} strokeLinecap="round" strokeLinejoin="round" fill="none" opacity={sweep > 0.95 ? 1 : 0} />
      </svg>
      <div style={{ position: "absolute", left: 0, right: 0, top: 750, textAlign: "center", opacity: ramp(frame, CUE["read.sweep"] + 10, CUE["read.sweep"] + 22), zIndex: 18 }}>
        <Label size={32} color={C.ink} spacing={8}>LEFT TO RIGHT</Label>
      </div>
    </Frame>
  );
};

export const Impatient: React.FC = () => (
  <Frame push={0}>
    <Kicker start={CUE["impatient.kicker"]} text="YOUR BRAIN IS IMPATIENT" />
    <BigPrice enterAt={-100} circleAt={CUE["impatient.circle"]} dimAt={CUE["impatient.fade"]} />
    <div style={{ position: "absolute", left: 0, right: 0, top: 720, textAlign: "center", zIndex: 18 }}>
      <div style={{ opacity: ramp(useCurrentFrame(), CUE["impatient.circle"] + 8, CUE["impatient.circle"] + 20) }}>
        <Label size={32} color={C.red} spacing={8}>JUDGED ON THE FIRST DIGIT</Label>
      </div>
    </div>
  </Frame>
);

export const Grabs: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const line = ramp(frame, CUE["grabs.line"], CUE["grabs.line"] + 20, Easing.out(Easing.cubic));
  const pin = spring({ frame: frame - CUE["grabs.line"] - 12, fps, config: { damping: 13, mass: 0.6, stiffness: 160 }, durationInFrames: 26 });
  const strike = ramp(frame, CUE["grabs.strike"], CUE["grabs.strike"] + 10, Easing.out(Easing.quad));
  const X0 = 460, X1 = 1460, Y = 850;
  const px = X0 + (X1 - X0) * 0.1;
  return (
    <Frame push={0}>
      <BigPrice enterAt={-100} dimAt={-100} liftAt={CUE["grabs.lift"]} />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 16 }}>
        <line x1={X0} x2={X0 + (X1 - X0) * line} y1={Y} y2={Y} stroke={C.ink} strokeWidth={6} strokeLinecap="round" />
        {[X0, X1].map((x) => (
          <line key={x} x1={x} x2={x} y1={Y - 16} y2={Y + 16} stroke={C.ink} strokeWidth={6} opacity={line} />
        ))}
        <g opacity={interpolate(pin, [0, 0.2], [0, 1], clamp)} transform={`translate(${px} ${Y - 70 * pin})`}>
          <circle r={16} fill={C.red} />
          <line y1={16} y2={70} stroke={C.red} strokeWidth={6} />
        </g>
      </svg>
      <div style={{ position: "absolute", left: X0 - 60, width: 120, top: Y + 26, textAlign: "center", opacity: line, zIndex: 18 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 48, color: C.ink }}>9</div>
      </div>
      <div style={{ position: "absolute", left: X1 - 80, width: 160, top: Y + 26, textAlign: "center", opacity: line, zIndex: 18 }}>
        <div style={{ position: "relative", display: "inline-block", fontFamily: ARIAL, fontSize: 48, color: C.ink }}>
          10
          <div aria-hidden data-mark style={{ position: "absolute", left: -12, right: -12, top: "48%", height: 8, background: C.red, borderRadius: 4, transformOrigin: "left center", transform: `scaleX(${strike}) rotate(-8deg)` }} />
        </div>
      </div>
      <div style={{ position: "absolute", left: px - 300, width: 600, top: Y - 150, textAlign: "center", opacity: interpolate(pin, [0.4, 1], [0, 1], clamp), zIndex: 18 }}>
        <Label size={32} color={C.red} spacing={6}>NINE-SOMETHING</Label>
      </div>
    </Frame>
  );
};

/* 9 — The left-digit effect: Thomas & Morwitz, NYU, 2005, five experiments. */
export const Study1: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Frame>
      <Headline at={CUE["study1.title"]} text="THE LEFT-DIGIT EFFECT" top={120} size={100} rule />
      <Card start={CUE["study1.card"]} left={410} top={400} width={1100} height={500} name="study card" rotate={-0.6} pad="50px 64px">
        <Label size={26} spacing={6} color={C.red}>STUDY · 2005 · NEW YORK UNIVERSITY</Label>
        <div style={{ fontFamily: PLAYFAIR, fontSize: 62, color: C.inkDeep, marginTop: 26, lineHeight: 1.1, opacity: ramp(frame, CUE["study1.names"], CUE["study1.names"] + 14), whiteSpace: "nowrap" }}>
          Manoj Thomas &amp; Vicki Morwitz
        </div>
        <div style={{ height: 4, background: C.inkDeep, opacity: 0.4, margin: "36px 0 34px" }} />
        <div style={{ display: "flex", alignItems: "center", gap: 26, opacity: ramp(frame, CUE["study1.five"] - 6, CUE["study1.five"] + 6) }}>
          <Label size={30} color={C.ink} spacing={5}>FIVE EXPERIMENTS</Label>
          <div style={{ display: "flex", gap: 16, marginLeft: 20 }}>
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} style={{ width: 64, height: 64, border: `5px solid ${C.ink}`, boxSizing: "border-box", display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Tick at={CUE["study1.five"] + 6 + i * 7} size={44} />
              </div>
            ))}
          </div>
        </div>
      </Card>
    </Frame>
  );
};

/* 10 — Cheaper mostly when the first digit changes: $2.99 vs $3, $2.89 vs $2.90. */
const Gauge: React.FC<{ at: number; top: number; fill: number; label: string; red?: boolean }> = ({ at, top, fill, label, red }) => {
  const frame = useCurrentFrame();
  const t = ramp(frame, at, at + 22, Easing.out(Easing.cubic));
  return (
    <div style={{ position: "absolute", left: 1180, top, width: 560, opacity: ramp(frame, at - 4, at + 6), zIndex: 16 }}>
      <Label size={28} color={red ? C.red : C.ink} spacing={5}>{label}</Label>
      <div style={{ position: "relative", marginTop: 18, height: 44, border: `5px solid ${C.ink}`, boxSizing: "border-box", background: C.card }}>
        <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${fill * t * 100}%`, background: red ? C.red : C.ink }} />
      </div>
      <div style={{ display: "flex", justifyContent: "space-between", marginTop: 10 }}>
        <Label size={18} spacing={3}>FEELS THE SAME</Label>
        <Label size={18} spacing={3}>FEELS DIFFERENT</Label>
      </div>
    </div>
  );
};

export const FirstDigit: React.FC = () => {
  const frame = useCurrentFrame();
  const vs = (at: number, top: number) => (
    <div style={{ position: "absolute", left: 590, top, width: 90, textAlign: "center", opacity: ramp(frame, at + 8, at + 18), zIndex: 16 }}>
      <Label size={34} color={C.ink} spacing={2}>VS</Label>
    </div>
  );
  return (
    <Frame>
      <Headline at={CUE["firstdigit.h1"]} text="A PRICE ENDING IN 9 FEELS CHEAPER" top={96} size={56} />
      <Headline at={CUE["firstdigit.h2"]} text="MOSTLY WHEN THE FIRST DIGIT CHANGES" top={170} size={56} color={C.red} />
      <Tag x={220} y={340} w={340} price="$2.99" start={CUE["firstdigit.r1"]} hl={[1]} rot={-2} />
      {vs(CUE["firstdigit.r1"], 398)}
      <Tag x={720} y={340} w={340} price="$3.00" start={CUE["firstdigit.r1"] + 12} hl={[1]} rot={2} />
      <Gauge at={CUE["firstdigit.g1"]} top={350} fill={0.86} label="A BIG DIFFERENCE" red />
      <Tag x={220} y={640} w={340} price="$2.89" start={CUE["firstdigit.r2"]} hl={[1]} rot={2} />
      {vs(CUE["firstdigit.r2"], 698)}
      <Tag x={720} y={640} w={340} price="$2.90" start={CUE["firstdigit.r2"] + 12} hl={[1]} rot={-2} />
      <Gauge at={CUE["firstdigit.g2"]} top={650} fill={0.07} label="BARELY ANYTHING" />
    </Frame>
  );
};

/* 11 — Your brain files $9.99 closer to $9 than $10. */
export const NumberLine: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const X0 = 260, X1 = 1660, Y = 640;
  const xOf = (v: number) => X0 + (v - 9) * (X1 - X0);
  const line = ramp(frame, 4, 30, Easing.out(Easing.cubic));
  const real = spring({ frame: frame - CUE["numberline.real"], fps, config: { damping: 13, mass: 0.6, stiffness: 160 }, durationInFrames: 26 });
  const slide = ramp(frame, CUE["numberline.felt"], CUE["numberline.felt"] + 36, Easing.inOut(Easing.cubic));
  const feltX = xOf(9.99) + (xOf(9.12) - xOf(9.99)) * slide;
  const feltOn = ramp(frame, CUE["numberline.felt"] - 4, CUE["numberline.felt"] + 4);
  const cent = ramp(frame, CUE["numberline.cent"], CUE["numberline.cent"] + 14, Easing.out(Easing.cubic));
  return (
    <Frame>
      <Kicker start={4} text="WHERE YOUR BRAIN FILES $9.99" />
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 16 }}>
        <line x1={X0} x2={X0 + (X1 - X0) * line} y1={Y} y2={Y} stroke={C.ink} strokeWidth={7} strokeLinecap="round" />
        {[9, 9.25, 9.5, 9.75, 10].map((v) => (
          <line key={v} x1={xOf(v)} x2={xOf(v)} y1={Y - (v % 1 ? 12 : 22)} y2={Y + (v % 1 ? 12 : 22)} stroke={C.ink} strokeWidth={v % 1 ? 4 : 7} opacity={line} />
        ))}
        <g opacity={interpolate(real, [0, 0.2], [0, 1], clamp)} transform={`translate(${xOf(9.99)} ${Y - 90 * real})`}>
          <circle r={18} fill={C.ink} />
          <line y1={18} y2={90} stroke={C.ink} strokeWidth={7} />
        </g>
        <g opacity={feltOn} transform={`translate(${feltX} ${Y - 210})`}>
          <circle r={18} fill={C.red} />
          <line y1={18} y2={210} stroke={C.red} strokeWidth={7} strokeDasharray="14 10" />
        </g>
        <path d={`M ${xOf(9.99) - 30} ${Y + 70} L ${xOf(9.99) - 30} ${Y + 90} L ${xOf(10) + 10} ${Y + 90} L ${xOf(10) + 10} ${Y + 70}`} stroke={C.red} strokeWidth={6} fill="none" opacity={cent} />
      </svg>
      {[
        { v: 9, t: "$9.00" },
        { v: 10, t: "$10.00" },
      ].map((d) => (
        <div key={d.t} style={{ position: "absolute", left: xOf(d.v) - 120, width: 240, top: Y + 36, textAlign: "center", opacity: line, zIndex: 18 }}>
          <div style={{ fontFamily: ARIAL, fontSize: 44, color: C.ink }}>{d.t}</div>
        </div>
      ))}
      <div style={{ position: "absolute", right: 1920 - xOf(9.99) - 40, top: Y - 215, textAlign: "right", opacity: interpolate(real, [0.4, 1], [0, 1], clamp), zIndex: 18 }}>
        <Label size={22} spacing={4}>WHERE IT REALLY IS</Label>
        <div style={{ fontFamily: ARIAL, fontSize: 48, color: C.ink }}>$9.99</div>
      </div>
      <div style={{ position: "absolute", left: xOf(9.12) - 30, top: Y - 330, opacity: ramp(frame, CUE["numberline.felt"] + 30, CUE["numberline.felt"] + 42), zIndex: 18 }}>
        <Label size={22} spacing={4} color={C.red}>WHERE YOUR BRAIN FILES IT</Label>
        <div style={{ fontFamily: ARIAL, fontSize: 48, color: C.red }}>“NINE-ISH”</div>
      </div>
      <div style={{ position: "absolute", right: 1920 - xOf(10) - 40, top: Y + 110, textAlign: "right", opacity: cent, zIndex: 18 }}>
        <Label size={26} spacing={5} color={C.red}>ONE CENT FROM $10</Label>
      </div>
    </Frame>
  );
};

/* 12 — It isn't just prices. */
const NumCard: React.FC<{ at: number; hlAt: number; left: number; label: string; num: string; first: number; rot: number }> = ({ at, hlAt, left, label, num, first, rot }) => {
  const frame = useCurrentFrame();
  const on = frame >= hlAt;
  return (
    <Card start={at} left={left} top={380} width={500} height={330} name={`number ${label}`} rotate={rot} pad="44px 44px" style={{ textAlign: "center" }}>
      <Label size={26} spacing={7}>{label}</Label>
      <div style={{ height: 5, width: 60, background: C.red, margin: "20px auto 34px" }} />
      <div style={{ fontFamily: ARIAL, fontSize: 92, lineHeight: 1, color: C.ink, whiteSpace: "nowrap" }}>
        {num.split("").map((ch, i) => (
          <span key={i} style={{ color: i === first && on ? C.red : C.ink, opacity: on && i !== first ? 0.45 : 1 }}>
            {ch}
          </span>
        ))}
      </div>
    </Card>
  );
};

export const Strange: React.FC = () => (
  <Frame>
    <Kicker start={CUE["strange.kicker"]} text="IT ISN'T JUST PRICES" />
    <NumCard at={CUE["strange.cards"]} hlAt={CUE["strange.hl"]} left={180} label="MILEAGE" num="79,900" first={0} rot={-1} />
    <NumCard at={CUE["strange.cards"] + 12} hlAt={CUE["strange.hl"] + 8} left={710} label="PRICES" num="$9.99" first={1} rot={0.6} />
    <NumCard at={CUE["strange.cards"] + 24} hlAt={CUE["strange.hl"] + 16} left={1240} label="ANY NUMBER" num="1,999" first={0} rot={-0.6} />
    <Headline at={CUE["strange.hl"] + 20} text="THE SAME SHORTCUT, EVERYWHERE" top={820} size={44} color={C.red} />
  </Frame>
);
