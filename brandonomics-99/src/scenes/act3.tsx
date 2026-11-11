import React from "react";
import { AbsoluteFill, Easing, interpolate, useCurrentFrame } from "remotion";
import { CUE } from "../shared/timing";
import { Stamp, Typewriter } from "../shared/pieces";
import { Kicker } from "./kit";
import { ARIAL, C, Card, ChapterCard, DROP, Frame, Glyph, Headline, Icon, Label, PLAYFAIR, Rise, TYPEWRITER, Tag, Tick, clamp, ramp, useIn } from "./lib";

/* 22 — The popular origin story: 1800s shop owners vs thieving cashiers. */
const StoryCard: React.FC<{ start: number; typeAt: number; typeEnd: number }> = ({ start, typeAt, typeEnd }) => (
  <Card start={start} left={160} top={170} width={820} height={740} name="story card" rotate={-1} pad="56px 64px">
    <Label size={24} spacing={6} color={C.red}>THE POPULAR STORY</Label>
    <div style={{ fontFamily: PLAYFAIR, fontSize: 60, color: C.inkDeep, marginTop: 14, lineHeight: 1.1 }}>A neat origin story</div>
    <div style={{ height: 4, background: C.inkDeep, opacity: 0.5, margin: "30px 0 34px" }} />
    <Typewriter
      text="Shop owners in the 1800s used odd prices to stop cashiers from stealing."
      startFrame={typeAt}
      endFrame={typeEnd}
      style={{ fontFamily: TYPEWRITER, fontSize: 44, lineHeight: 1.32, color: C.inkDeep }}
    />
  </Card>
);

export const Origin: React.FC = () => (
  <Frame>
    <StoryCard start={CUE["origin.card"]} typeAt={CUE["origin.type"]} typeEnd={CUE["origin.typeEnd"]} />
    <Icon kind="register" start={CUE["origin.reg"]} left={1160} top={400} width={520} />
    <Stamp startFrame={CUE["origin.year"]} x={460} y={-290} rotate={-4} title="1800s" width={340} zIndex={30} />
  </Frame>
);

/* 23 — $1: the bill slips into a pocket. $0.99: open the register, give change, record the sale. */
export const Register: React.FC = () => {
  const frame = useCurrentFrame();
  const slip = ramp(frame, CUE["register.slip"], CUE["register.pocket"] + 4, Easing.inOut(Easing.cubic));
  const billIn = useIn(CUE["register.slip"] - 14);
  const drawer = ramp(frame, CUE["register.open"], CUE["register.open"] + 14, Easing.out(Easing.back(1.6)));
  return (
    <Frame>
      <div style={{ position: "absolute", left: 958, top: 150, height: 800, borderLeft: `5px dashed rgba(26,26,26,0.35)`, zIndex: 10 }} />
      {/* left: exactly $1 */}
      <Tag x={290} y={190} w={400} price="$1.00" start={CUE["register.t1"]} rot={-2} />
      <Icon kind="pocket" start={CUE["register.slip"] - 20} left={560} top={520} width={280} />
      <div data-moving={frame < CUE["register.pocket"] + 8 ? "" : undefined} style={{ position: "absolute", left: 150, top: 560, width: 300, opacity: billIn * (1 - ramp(frame, CUE["register.pocket"] - 2, CUE["register.pocket"] + 6)), transform: `translateX(${slip * 400}px) scale(${1 - slip * 0.4}) rotate(${-8 + slip * 20}deg)`, zIndex: 11 }}>
        <Glyph kind="bill" width={300} />
      </div>
      <div style={{ position: "absolute", left: 100, width: 800, top: 820, textAlign: "center", opacity: useIn(CUE["register.pocket"]), zIndex: 18 }}>
        <Label size={28} color={C.ink} spacing={5}>NO CHANGE · NO RECORD</Label>
      </div>
      {/* right: 99 cents */}
      <Tag x={1230} y={190} w={400} price="$0.99" tone="red" start={CUE["register.t2"]} rot={2} hl={[3, 4]} />
      <Icon kind="register" start={CUE["register.t2"] + 10} left={1040} top={440} width={420} />
      <div style={{ position: "absolute", left: 1055, top: 772 + drawer * 48, width: 390, opacity: ramp(frame, CUE["register.open"], CUE["register.open"] + 6), zIndex: 11 }}>
        <Glyph kind="drawer" width={390} />
      </div>
      <Icon kind="coin" start={CUE["register.coin"]} left={1505} top={470} width={110} />
      <div style={{ position: "absolute", left: 1470, width: 180, top: 594, textAlign: "center", opacity: useIn(CUE["register.coin"] + 8), zIndex: 18 }}>
        <Label size={22} color={C.ink} spacing={3}>CHANGE</Label>
      </div>
      <Card start={CUE["register.receipt"]} left={1665} top={440} width={170} height={420} name="receipt" rotate={1.5} stroke={0} pad="26px 16px" style={{ textAlign: "center" }}>
        <Label size={16} spacing={3}>RECEIPT</Label>
        <div style={{ height: 3, background: C.ink, opacity: 0.4, margin: "14px 0" }} />
        <div style={{ fontFamily: ARIAL, fontSize: 30, color: C.ink }}>$0.99</div>
        <div style={{ height: 3, background: C.ink, opacity: 0.4, margin: "14px 0 22px" }} />
        <div style={{ display: "flex", justifyContent: "center" }}>
          <Tick at={CUE["register.receipt"] + 14} size={50} />
        </div>
        <Label size={16} spacing={2} color={C.red} style={{ marginTop: 14 }}>SALE</Label>
        <Label size={16} spacing={2} color={C.red}>RECORDED</Label>
      </Card>
    </Frame>
  );
};

/* 24 — A great story. Nobody has ever proven it. */
export const Unproven: React.FC = () => (
  <Frame>
    <StoryCard start={-100} typeAt={-100} typeEnd={-99} />
    <Stamp startFrame={CUE["unproven.stamp"]} x={-390} y={220} rotate={-6} title="UNPROVEN" width={430} zIndex={30} />
    <Headline at={4} text="A GREAT STORY." left={1080} width={760} align="left" top={400} size={64} />
    <Headline at={CUE["unproven.stamp"] - 8} text="NEVER PROVEN." left={1080} width={760} align="left" top={500} size={64} color={C.red} />
  </Frame>
);

/* 25 — Common around the 1920s, often .95 not .99. It stuck. */
export const Twenties: React.FC = () => {
  const frame = useCurrentFrame();
  const L = 200, R = 1720, Y = 360;
  const line = ramp(frame, CUE["twenties.line"], CUE["twenties.line"] + 30, Easing.out(Easing.cubic));
  const marks = [
    { x: 380, year: "1800s", sub: "THE STORY", at: CUE["twenties.line"] + 10, red: false },
    { x: 1000, year: "1920s", sub: "BECOMES COMMON", at: CUE["twenties.y1920"], red: true },
    { x: 1580, year: "TODAY", sub: "STILL HERE", at: CUE["twenties.stuck"] - 6, red: false },
  ];
  return (
    <Frame>
      <div style={{ position: "absolute", left: L, width: (R - L) * line, top: Y - 3, height: 6, background: C.ink, zIndex: 14 }} />
      {marks.map((m) => {
        const o = ramp(frame, m.at, m.at + 12);
        return (
          <React.Fragment key={m.year}>
            <div style={{ position: "absolute", left: m.x - 16, top: Y - 16, width: 32, height: 32, borderRadius: "50%", background: m.red ? C.red : C.ink, opacity: o, zIndex: 15 }} />
            <div style={{ position: "absolute", left: m.x - 200, width: 400, top: Y - 110, textAlign: "center", opacity: o, zIndex: 16 }}>
              <div style={{ fontFamily: ARIAL, fontSize: 56, color: m.red ? C.red : C.ink }}>{m.year}</div>
            </div>
            <div style={{ position: "absolute", left: m.x - 200, width: 400, top: Y + 34, textAlign: "center", opacity: o, zIndex: 16 }}>
              <Label size={24} spacing={5}>{m.sub}</Label>
            </div>
          </React.Fragment>
        );
      })}
      <Tag x={690} y={570} w={300} price="$4.95" tone="red" start={CUE["twenties.t95"]} hl={[3, 4]} rot={-2} />
      <Tag x={1030} y={570} w={300} price="$4.99" start={CUE["twenties.t99"]} strikeAt={CUE["twenties.t99"] + 14} rot={2} />
      <div style={{ position: "absolute", left: 640, width: 740, top: 790, textAlign: "center", opacity: useIn(CUE["twenties.t99"] + 18), zIndex: 16 }}>
        <Label size={26} color={C.ink} spacing={5}>BACK THEN, .95 WAS THE FAVOURITE</Label>
      </div>
      <Stamp startFrame={CUE["twenties.stuck"]} x={620} y={150} rotate={-5} title="IT STUCK" width={340}  zIndex={30} />
    </Frame>
  );
};

/* 26 — 60–95% of prices in some markets; nobody wants to be the one at a full $10. */
export const Everywhere: React.FC = () => {
  const frame = useCurrentFrame();
  const bar = ramp(frame, CUE["everywhere.bar"], CUE["everywhere.bar"] + 24, Easing.out(Easing.cubic));
  const BL = 460, BW = 1000;
  return (
    <Frame>
      <Headline at={CUE["everywhere.stat"]} text="60–95%" top={110} size={170} color={C.red} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 310, textAlign: "center", opacity: useIn(CUE["everywhere.bar"]), zIndex: 16 }}>
        <Label size={28} color={C.ink} spacing={6}>OF PRICES END IN 9 · IN SOME MARKETS</Label>
      </div>
      <div style={{ position: "absolute", left: BL, top: 380, width: BW, height: 34, border: `5px solid ${C.ink}`, boxSizing: "border-box", background: C.card, opacity: useIn(CUE["everywhere.bar"]), zIndex: 15 }}>
        <div style={{ position: "absolute", left: `${60}%`, top: 0, bottom: 0, width: `${35 * bar}%`, background: C.red }} />
      </div>
      {[0, 1, 2, 3, 4].map((i) => {
        const x = 200 + i * 330;
        const odd = i === 4;
        const at = odd ? CUE["everywhere.odd"] : CUE["everywhere.stores"] + i * 8;
        return (
          <React.Fragment key={i}>
            <Icon kind="store" start={at} left={x} top={510} width={220} dx={odd ? -12 : 0} />
            <Tag x={x - 5} y={790} w={230} price={odd ? "$10.00" : "$9.99"} tone={odd ? "red" : "paper"} start={at + 10} rot={[-3, 2, -2, 3, 0][i]} />
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: 1370, width: 500, top: 940, textAlign: "center", opacity: useIn(CUE["everywhere.full"]), zIndex: 16 }}>
        <Label size={24} color={C.red} spacing={5}>THE ONLY FULL $10</Label>
      </div>
    </Frame>
  );
};

/* 27 — Chapter 4: the brands that refuse. No nines. */
export const Ch4: React.FC = () => {
  const frame = useCurrentFrame();
  const sign = useIn(CUE["ch4.no"]);
  const slash = ramp(frame, CUE["ch4.no"] + 6, CUE["ch4.no"] + 16, Easing.out(Easing.cubic));
  return (
    <Frame>
      <ChapterCard n="4" title={<>THE BRANDS<br />THAT REFUSE</>} numAt={CUE["ch4.num"]} titleAt={CUE["ch4.title"]} top={150} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 690, display: "flex", justifyContent: "center", alignItems: "center", gap: 40, opacity: sign, zIndex: 18 }}>
        <div style={{ position: "relative", width: 230, height: 230, borderRadius: "50%", border: `16px solid ${C.red}`, boxSizing: "border-box", display: "flex", alignItems: "center", justifyContent: "center", background: C.card }}>
          <span style={{ position: "relative", fontFamily: ARIAL, fontSize: 80, color: C.ink }}>
            .99
            <span aria-hidden data-mark style={{ position: "absolute", left: -40, right: -40, top: "46%", height: 16, background: C.red, transform: `rotate(-40deg) scaleX(${slash})` }} />
          </span>
        </div>
        <div style={{ fontFamily: ARIAL, fontSize: 72, color: C.ink }}>NO NINES</div>
      </div>
    </Frame>
  );
};

/* 28 — A designer handbag: $2,000, not $1,999. On purpose. */
export const Luxury: React.FC = () => (
  <Frame>
    <Icon kind="bag" start={CUE["luxury.bag"]} left={240} top={300} width={580} />
    <Tag x={1060} y={250} w={540} price="$2,000" tone="ink" start={CUE["luxury.t1"]} rot={-2} />
    <Tag x={1060} y={560} w={540} price="$1,999" start={CUE["luxury.t2"]} strikeAt={CUE["luxury.strike"]} rot={2} />
    <Headline at={CUE["luxury.purpose"]} text="ON PURPOSE." left={1080} width={700} align="left" top={880} size={56} color={C.red} />
  </Frame>
);

/* 29 — Wadhwa & Zhang (2015): round feels right when emotional — champagne $40 beat $39.72; for a calculator, the messy price won. */
const Winner: React.FC<{ at: number; left: number; text: string }> = ({ at, left, text }) => (
  <div style={{ position: "absolute", left, width: 300, top: 830, display: "flex", alignItems: "center", justifyContent: "center", gap: 12, opacity: useIn(at), zIndex: 18 }}>
    <Tick at={at} size={46} />
    <Label size={24} color={C.red} spacing={4}>{text}</Label>
  </div>
);

export const Champagne: React.FC = () => {
  const out = CUE["champagne.out"];
  return (
    <Frame>
      <Card start={CUE["champagne.card"]} left={360} top={190} width={1200} height={280} name="study 2015" rotate={-0.6} pad="50px 60px" exit={out}>
        <Label size={24} spacing={6} color={C.red}>STUDY · 2015</Label>
        <div style={{ fontFamily: PLAYFAIR, fontSize: 58, color: C.inkDeep, marginTop: 18, whiteSpace: "nowrap" }}>Monica Wadhwa &amp; Kuangjie Zhang</div>
      </Card>
      <Headline at={CUE["champagne.head"]} text="ROUND PRICES FEEL RIGHT" top={570} size={84} exit={out} />
      <Headline at={CUE["champagne.head"] + 14} text="WHEN THE PURCHASE IS EMOTIONAL" top={690} size={44} color={C.red} exit={out + 3} />
      {/* champagne */}
      <Icon kind="bottle" start={CUE["champagne.bottle"]} left={430} top={130} width={150} />
      <Tag x={200} y={640} w={300} price="$40" start={CUE["champagne.t40"]} rot={-2} />
      <Tag x={540} y={640} w={300} price="$39.72" start={CUE["champagne.t3972"]} rot={2} />
      <Winner at={CUE["champagne.win1"]} left={200} text="FEELS RIGHT" />
      {/* calculator */}
      <Icon kind="calculator" start={CUE["champagne.calc"]} left={1305} top={150} width={230} />
      <Tag x={1080} y={640} w={300} price="$40" start={CUE["champagne.calc"] + 6} rot={-2} />
      <Tag x={1420} y={640} w={300} price="$39.72" start={CUE["champagne.calc"] + 14} rot={2} />
      <Winner at={CUE["champagne.win2"]} left={1420} text="WINS" />
    </Frame>
  );
};

/* 30 — Round suits the heart; odd suits the head. */
const MindCard: React.FC<{ at: number; iconAt: number; left: number; kind: "heart" | "gear"; who: string; price: string; lines: string; rot: number }> = ({ at, iconAt, left, kind, who, price, lines, rot }) => {
  const frame = useCurrentFrame();
  const o = ramp(frame, iconAt, iconAt + 12);
  return (
    <Card start={at} left={left} top={190} width={700} height={700} name={`mind ${who}`} rotate={rot} pad="56px 56px" style={{ textAlign: "center" }}>
      <div style={{ height: 210, display: "flex", alignItems: "center", justifyContent: "center", opacity: o, transform: `scale(${0.8 + 0.2 * o})` }}>
        <Glyph kind={kind} width={210} style={kind === "gear" ? { transform: `rotate(${Math.max(0, frame - iconAt) * 1.2}deg)` } : undefined} />
      </div>
      <Label size={26} spacing={8} style={{ marginTop: 30 }}>{who}</Label>
      <div style={{ fontFamily: ARIAL, fontSize: 120, lineHeight: 1.05, color: kind === "heart" ? C.red : C.ink, marginTop: 16, whiteSpace: "nowrap" }}>{price}</div>
      <div style={{ height: 6, width: 80, background: C.red, margin: "26px auto 22px" }} />
      <Label size={26} spacing={4} color={C.ink}>{lines}</Label>
    </Card>
  );
};

export const HeartHead: React.FC = () => (
  <Frame>
    <MindCard at={2} iconAt={CUE["hearthead.heart"]} left={200} kind="heart" who="YOUR HEART" price="$40" lines="ROUND · EASY TO PROCESS" rot={-1} />
    <MindCard at={CUE["hearthead.right"]} iconAt={CUE["hearthead.head"]} left={1020} kind="gear" who="YOUR HEAD" price="$39.72" lines="ODD · MAKES YOU THINK" rot={0.8} />
  </Frame>
);

/* 31 — The real trick: whole dollars for regular prices, .99 for discounts. */
export const Trick: React.FC = () => (
  <Frame>
    <Kicker start={CUE["trick.kicker"]} text="THE REAL TRICK" />
    <Card start={CUE["trick.card"]} left={150} top={300} width={620} height={420} name="research 2003" rotate={-1} pad="48px 52px">
      <Label size={22} spacing={5} color={C.red}>ANDERSON &amp; SIMESTER · 2003</Label>
      <div style={{ fontFamily: PLAYFAIR, fontSize: 42, lineHeight: 1.25, color: C.inkDeep, marginTop: 22 }}>
        Some retailers kept regular prices in whole dollars, and saved the .99 endings for discounts.
      </div>
    </Card>
    <Tag x={860} y={380} w={440} price="$40" label="REGULAR" start={CUE["trick.reg"]} rot={-2} />
    <div style={{ position: "absolute", left: 860, width: 440, top: 640, textAlign: "center", opacity: useIn(CUE["trick.reg"] + 14), zIndex: 16 }}>
      <Label size={24} spacing={5} color={C.ink}>WHOLE DOLLARS</Label>
    </div>
    <Tag x={1340} y={380} w={440} price="$29.99" label="SALE" tone="red" start={CUE["trick.sale"]} hl={[3, 4, 5]} rot={2} />
    <Stamp startFrame={CUE["trick.badge"]} x={600} y={210} rotate={-5} title="DISCOUNT" width={380} zIndex={30} />
  </Frame>
);

/* 32 — The nine is a message: "this is a bargain". Whether or not it is. */
export const Message: React.FC = () => (
  <Frame>
    <Tag x={180} y={390} w={660} price="$9.99" tone="red" start={4} hl={[3, 4]} rot={-2} />
    <Headline at={CUE["message.label"]} text="IT'S A MESSAGE" left={1000} width={800} align="left" top={240} size={56} rule />
    <Card start={CUE["message.bubble"] - 6} left={1000} top={420} width={780} height={220} name="bargain" rotate={0.8} pad="0 50px" style={{ display: "flex", alignItems: "center" }}>
      <Typewriter text="“This is a bargain.”" startFrame={CUE["message.bubble"]} endFrame={CUE["message.bubbleEnd"]} style={{ fontFamily: TYPEWRITER, fontSize: 60, color: C.inkDeep, whiteSpace: "nowrap" }} />
    </Card>
    <Headline at={CUE["message.q"]} text="WHETHER OR NOT IT IS." left={1000} width={800} align="left" top={720} size={48} color={C.red} />
  </Frame>
);

/* 33 — The twist (2019): prices ending in 9 were usually higher on average. */
export const Twist: React.FC = () => {
  const frame = useCurrentFrame();
  const BASE = 860;
  const bars = [
    { x: 1000, h: 430, label: "ENDING IN 9", red: true, at: CUE["twist.bars"] },
    { x: 1400, h: 330, label: "OTHER ENDINGS", red: false, at: CUE["twist.bars"] + 10 },
  ];
  return (
    <Frame>
      <Kicker start={CUE["twist.kicker"]} text="THE TWIST" />
      <Card start={CUE["twist.card"]} left={150} top={300} width={640} height={240} name="study 2019" rotate={-0.8} pad="46px 52px">
        <Label size={22} spacing={5} color={C.red}>STUDY · 2019</Label>
        <div style={{ fontFamily: PLAYFAIR, fontSize: 46, lineHeight: 1.2, color: C.inkDeep, marginTop: 18 }}>Average prices, compared by ending</div>
      </Card>
      <Headline at={CUE["twist.not"]} text="HIGHER, NOT LOWER." left={150} width={760} align="left" top={640} size={60} color={C.red} rule />
      <div style={{ position: "absolute", left: 960, width: 740, top: BASE, height: 5, background: C.ink, opacity: useIn(CUE["twist.bars"]), zIndex: 15 }} />
      {bars.map((b) => {
        const g = ramp(frame, b.at, b.at + 22, Easing.out(Easing.cubic));
        return (
          <React.Fragment key={b.label}>
            <div style={{ position: "absolute", left: b.x, width: 260, top: BASE - b.h * g, height: b.h * g, background: b.red ? C.red : C.ink, filter: DROP, zIndex: 14 }} />
            <div style={{ position: "absolute", left: b.x - 40, width: 340, top: BASE + 20, textAlign: "center", opacity: ramp(frame, b.at, b.at + 10), zIndex: 16 }}>
              <Label size={24} color={b.red ? C.red : C.ink} spacing={4}>{b.label}</Label>
            </div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: 900, width: 460, top: BASE - 430 - 70, textAlign: "center", opacity: useIn(CUE["twist.higher"]), zIndex: 16 }}>
        <Label size={26} color={C.red} spacing={5}>HIGHER ON AVERAGE</Label>
      </div>
      <div style={{ position: "absolute", right: 110, bottom: 50, opacity: 0.6 * useIn(CUE["twist.bars"]), zIndex: 16 }}>
        <Label size={18} spacing={3}>BAR HEIGHTS ILLUSTRATIVE</Label>
      </div>
    </Frame>
  );
};

/* 34 — The nine isn't a discount. It's a costume. */
export const Costume: React.FC = () => {
  const frame = useCurrentFrame();
  const strike = ramp(frame, CUE["costume.strike"], CUE["costume.strike"] + 10, Easing.out(Easing.quad));
  return (
    <Frame>
      <Tag x={180} y={390} w={660} price="$9.99" tone="red" start={-100} hl={[3, 4]} rot={-2} />
      <div style={{ position: "absolute", left: 1040, top: 230, opacity: useIn(CUE["costume.disc"]), zIndex: 18 }}>
        <div style={{ position: "relative", display: "inline-block", fontFamily: ARIAL, fontSize: 104, color: C.ink, lineHeight: 1 }}>
          DISCOUNT
          <span aria-hidden data-mark style={{ position: "absolute", left: -14, right: -14, top: "46%", height: 14, background: C.red, borderRadius: 7, transformOrigin: "left center", transform: `scaleX(${strike}) rotate(-3deg)` }} />
        </div>
      </div>
      <div style={{ position: "absolute", left: 1040, top: 440, opacity: useIn(CUE["costume.cost"]), zIndex: 18 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 104, color: C.red, lineHeight: 1 }}>COSTUME</div>
      </div>
      <Icon kind="mask" start={CUE["costume.cost"] + 4} left={1090} top={620} width={420} />
    </Frame>
  );
};

/* 35 — Your challenge: count the nines, and the actual deals. */
const SHELF = ["$4.99", "$12.00", "$9.99", "$2.49", "$19.99", "$6.99"];
const Tally: React.FC<{ at: number; n: number }> = ({ at, n }) => {
  const frame = useCurrentFrame();
  return (
    <svg width={200} height={80} viewBox="0 0 200 80">
      {Array.from({ length: n }).map((_, i) => {
        const t = ramp(frame, at + i * 9, at + i * 9 + 8, Easing.out(Easing.cubic));
        const d = i < 4 ? `M ${20 + i * 30} 8 L ${20 + i * 30} 72` : "M 6 60 L 124 16";
        return <path key={i} d={d} stroke={i < 4 ? C.ink : C.red} strokeWidth={8} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - t} />;
      })}
    </svg>
  );
};

export const Challenge: React.FC = () => {
  const frame = useCurrentFrame();
  const rail = ramp(frame, CUE["challenge.shelf"] - 10, CUE["challenge.shelf"] + 10, Easing.out(Easing.cubic));
  let k = 0;
  return (
    <Frame>
      <Kicker start={CUE["challenge.kicker"]} text="YOUR CHALLENGE" />
      <div style={{ position: "absolute", left: 160, width: 1600 * rail, top: 238, height: 14, borderRadius: 7, background: C.ink, zIndex: 13 }} />
      {SHELF.map((p, i) => {
        const nine = p.endsWith("9");
        const tickAt = nine ? CUE["challenge.count"] + k++ * 9 : 0;
        return (
          <React.Fragment key={p}>
            <Tag x={190 + i * 262} y={330} w={230} price={p} start={CUE["challenge.shelf"] + i * 5} rot={[-3, 2, -2, 3, -1, 2][i]} hl={nine ? [p.length - 1] : []} hlAt={nine ? tickAt : undefined} />
            {nine ? (
              <div style={{ position: "absolute", left: 190 + i * 262 + 90, top: 470, zIndex: 16 }}>
                <Tick at={tickAt} size={50} />
              </div>
            ) : null}
          </React.Fragment>
        );
      })}
      <Card start={CUE["challenge.count"] - 10} left={460} top={620} width={1000} height={300} name="tally" rotate={-0.6} pad="40px 60px">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: 100 }}>
          <Label size={30} color={C.ink} spacing={5}>PRICES ENDING IN 9</Label>
          <Tally at={CUE["challenge.count"]} n={5} />
        </div>
        <div style={{ height: 4, background: C.ink, opacity: 0.25, margin: "10px 0" }} />
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: 100 }}>
          <Label size={30} color={C.ink} spacing={5}>ACTUALLY A DEAL</Label>
          <div style={{ fontFamily: ARIAL, fontSize: 80, color: C.red, opacity: ramp(frame, CUE["challenge.deal"], CUE["challenge.deal"] + 10), width: 200, textAlign: "center" }}>?</div>
        </div>
      </Card>
    </Frame>
  );
};

/* 36 — The question for the comments; sign-off. */
export const Comments: React.FC = () => {
  const frame = useCurrentFrame();
  const vig = ramp(frame, CUE["comments.end"] + 30, CUE["comments.end"] + 90, Easing.out(Easing.cubic));
  return (
    <Frame push={0.015}>
      <Card start={0} left={360} top={190} width={1200} height={440} name="comment" rotate={-0.6} pad="50px 64px">
        <div style={{ display: "flex", alignItems: "center", gap: 22 }}>
          <div style={{ width: 70, height: 70, borderRadius: "50%", background: C.red }} />
          <Label size={24} spacing={5}>YOUR COMMENT</Label>
        </div>
        <div style={{ height: 4, background: C.ink, opacity: 0.25, margin: "28px 0 30px" }} />
        <Typewriter
          text="What's the sneakiest pricing trick you've ever fallen for?"
          startFrame={CUE["comments.type"]}
          endFrame={CUE["comments.typeEnd"]}
          style={{ fontFamily: TYPEWRITER, fontSize: 58, lineHeight: 1.3, color: C.inkDeep }}
        />
      </Card>
      <Headline at={CUE["comments.cta"]} text="TELL ME IN THE COMMENTS" top={720} size={60} color={C.red} rule />
      <div style={{ position: "absolute", left: 0, right: 0, top: 880, textAlign: "center", opacity: useIn(CUE["comments.end"]), zIndex: 16 }}>
        <Label size={28} spacing={8} color={C.ink}>SEE YOU IN THE NEXT ONE</Label>
      </div>
      <AbsoluteFill aria-hidden style={{ background: "radial-gradient(circle at 50% 50%, transparent 40%, rgba(20,16,12,0.55) 100%)", opacity: vig, pointerEvents: "none", zIndex: 30 }} />
    </Frame>
  );
};

export { interpolate, clamp, Rise };
