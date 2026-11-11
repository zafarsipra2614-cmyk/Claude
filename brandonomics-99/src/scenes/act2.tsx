import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { CUE } from "../shared/timing";
import { Stamp, Typewriter } from "../shared/pieces";
import { Kicker } from "./kit";
import { ARIAL, C, Card, ChapterCard, DROP, Frame, Glyph, Headline, Icon, Label, Odometer, PLAYFAIR, Rise, TYPEWRITER, Tag, clamp, ramp, useIn } from "./lib";

/* 13 — Chapter 2: the proof. Two famous studies. */
const Folder: React.FC<{ at: number; left: number; n: string; title: string; rot: number }> = ({ at, left, n, title, rot }) => (
  <Card start={at} left={left} top={700} width={640} height={220} name={`folder ${n}`} rotate={rot} pad="0 44px" style={{ display: "flex", alignItems: "center", gap: 30 }}>
    <Glyph kind="folder" width={120} />
    <div>
      <Label size={24} spacing={6} color={C.red}>STUDY {n}</Label>
      <div style={{ fontFamily: ARIAL, fontSize: 33, lineHeight: 1.08, color: C.ink, marginTop: 10, whiteSpace: "nowrap" }}>{title}</div>
    </div>
  </Card>
);

export const Ch2: React.FC = () => {
  const frame = useCurrentFrame();
  const qOut = ramp(frame, CUE["ch2.folders"] - 12, CUE["ch2.folders"]);
  return (
    <Frame>
      <ChapterCard n="2" title="THE PROOF" numAt={CUE["ch2.num"]} titleAt={CUE["ch2.title"]} top={150} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 760, textAlign: "center", zIndex: 18, opacity: 1 - qOut }}>
        <Typewriter
          text="Does it actually change what people buy?"
          startFrame={CUE["ch2.q"]}
          endFrame={CUE["ch2.q"] + 50}
          style={{ fontFamily: TYPEWRITER, fontSize: 52, color: C.inkDeep }}
        />
      </div>
      <Folder at={CUE["ch2.folders"]} left={260} n="1" title="CLOTHING CATALOG" rot={-1} />
      <Folder at={CUE["ch2.folders"] + 14} left={1020} n="2" title="USED CARS" rot={0.8} />
    </Frame>
  );
};

/* 14 — A national women's clothing catalog; one dress. */
export const Catalog: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Frame>
      <Card start={CUE["catalog.page"]} left={200} top={130} width={640} height={820} name="catalog page" rotate={-1.2} pad="48px 56px" style={{ textAlign: "center" }}>
        <div style={{ fontFamily: PLAYFAIR, fontSize: 64, color: C.inkDeep, letterSpacing: -1 }}>The Catalog</div>
        <Label size={20} spacing={6} style={{ marginTop: 8 }}>WOMEN'S CLOTHING · NATIONAL</Label>
        <div style={{ height: 4, background: C.inkDeep, opacity: 0.6, margin: "26px 0 40px" }} />
        <Glyph kind="dress" width={230} />
        <div style={{ marginTop: 36, opacity: ramp(frame, CUE["catalog.dress"], CUE["catalog.dress"] + 12) }}>
          <Label size={26} spacing={6} color={C.red}>PRICE UNDER TEST</Label>
        </div>
      </Card>
      <Card start={CUE["catalog.names"]} left={980} top={260} width={760} height={330} name="researchers" rotate={0.8} pad="50px 56px">
        <Label size={24} spacing={6} color={C.red}>PROFESSORS</Label>
        <div style={{ fontFamily: PLAYFAIR, fontSize: 58, lineHeight: 1.15, color: C.inkDeep, marginTop: 18, whiteSpace: "nowrap" }}>
          Eric Anderson
          <br />
          &amp; Duncan Simester
        </div>
      </Card>
      <Headline at={CUE["catalog.dress"] + 6} text="ONE DRESS. THREE PRICES." left={980} width={800} align="left" top={700} size={54} rule />
    </Frame>
  );
};

/* 15 — $34 normal, $39 jumped by a third, $44 about the same as $34. */
export const DressTest: React.FC = () => {
  const frame = useCurrentFrame();
  const BASE = 860, BW = 170;
  const bars = [
    { x: 1040, h: 300, at: CUE["dresstest.bar34"], label: "$34", red: false },
    { x: 1300, h: 400, at: CUE["dresstest.jump"], label: "$39", red: true },
    { x: 1560, h: 300, at: CUE["dresstest.bar44"], label: "$44", red: false },
  ];
  const ghost = ramp(frame, CUE["dresstest.ghost"], CUE["dresstest.ghost"] + 14) * (1 - ramp(frame, CUE["dresstest.jump"], CUE["dresstest.jump"] + 10));
  const axis = useIn(4, 20);
  return (
    <Frame>
      <Kicker start={4} text="THE DRESS TEST" sub="SAME DRESS · DIFFERENT PRICES" />
      <Icon kind="dress" start={0} left={200} top={300} width={300} />
      <Tag x={560} y={330} w={330} price="$34" start={CUE["dresstest.tag"]} exit={CUE["dresstest.p39"] - 12} rot={3} />
      <Tag x={560} y={330} w={330} price="$39" tone="red" start={CUE["dresstest.p39"]} exit={CUE["dresstest.p44"] - 12} hl={[2]} rot={3} />
      <Tag x={560} y={330} w={330} price="$44" start={CUE["dresstest.p44"]} rot={3} />
      <div style={{ position: "absolute", left: 1000, top: 250, opacity: axis, zIndex: 16 }}>
        <Label size={26} spacing={6} color={C.ink}>DRESSES SOLD</Label>
      </div>
      <div style={{ position: "absolute", left: 1000, width: 760, top: BASE, height: 5, background: C.ink, opacity: axis, zIndex: 15 }} />
      {/* expected: a higher price should mean fewer sales */}
      <div style={{ position: "absolute", left: 1300, top: BASE - 220, width: BW, height: 220, border: `5px dashed ${C.ink}`, boxSizing: "border-box", opacity: ghost * 0.7, zIndex: 13 }} />
      <div style={{ position: "absolute", left: 1300 - 40, width: BW + 80, top: BASE - 270, textAlign: "center", opacity: ghost, zIndex: 16 }}>
        <Label size={22} spacing={4}>EXPECTED</Label>
      </div>
      {bars.map((b) => {
        const g = ramp(frame, b.at, b.at + 22, Easing.out(Easing.back(1.4)));
        return (
          <React.Fragment key={b.label}>
            <div style={{ position: "absolute", left: b.x, top: BASE - b.h * g, width: BW, height: b.h * g, background: b.red ? C.red : C.ink, filter: DROP, zIndex: 14 }} />
            <div style={{ position: "absolute", left: b.x - 20, width: BW + 40, top: BASE + 18, textAlign: "center", opacity: ramp(frame, b.at, b.at + 10), zIndex: 16 }}>
              <div style={{ fontFamily: ARIAL, fontSize: 44, color: b.red ? C.red : C.ink }}>{b.label}</div>
            </div>
          </React.Fragment>
        );
      })}
      <div style={{ position: "absolute", left: 1300 - 60, width: BW + 120, top: BASE - 400 - 96, textAlign: "center", opacity: ramp(frame, CUE["dresstest.third"], CUE["dresstest.third"] + 12), zIndex: 16 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 64, color: C.red }}>+⅓</div>
      </div>
    </Frame>
  );
};

/* 16 — The extra $5 scared no one; strongest on new items. */
export const NewItems: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Frame>
      <div style={{ position: "absolute", left: 230, top: 200, opacity: useIn(CUE["newitems.five"]), zIndex: 18 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 96, color: C.red, lineHeight: 1 }}>+$5</div>
        <Label size={24} spacing={5} style={{ marginTop: 10 }}>AND NOBODY WALKED AWAY</Label>
      </div>
      <Tag x={220} y={430} w={600} price="$39" start={4} hl={[2]} hlAt={CUE["newitems.circle"]} rot={-2} />
      <div style={{ position: "absolute", left: 230, top: 780, opacity: useIn(CUE["newitems.circle"] + 6), zIndex: 18 }}>
        <Label size={30} spacing={5} color={C.ink}>THE 9 SOLD MORE DRESSES</Label>
      </div>
      <Card start={CUE["newitems.new"]} left={1060} top={220} width={680} height={640} name="new items" rotate={0.8} pad="54px 60px">
        <Label size={24} spacing={6} color={C.red}>STRONGEST ON</Label>
        <div style={{ fontFamily: ARIAL, fontSize: 84, color: C.ink, lineHeight: 1, marginTop: 14, whiteSpace: "nowrap" }}>NEW ITEMS</div>
        <div style={{ height: 6, width: 90, background: C.red, margin: "34px 0 44px" }} />
        <div style={{ display: "flex", alignItems: "baseline", gap: 30 }}>
          <Label size={26} spacing={5}>NOW</Label>
          <div style={{ fontFamily: ARIAL, fontSize: 72, color: C.ink }}>$39</div>
        </div>
        <div style={{ display: "flex", alignItems: "baseline", gap: 30, marginTop: 16 }}>
          <Label size={26} spacing={5}>WAS</Label>
          <div style={{ fontFamily: ARIAL, fontSize: 72, color: C.red, opacity: ramp(frame, CUE["newitems.compare"], CUE["newitems.compare"] + 10) }}>?</div>
        </div>
        <div style={{ marginTop: 22, opacity: ramp(frame, CUE["newitems.compare"] + 10, CUE["newitems.compare"] + 22) }}>
          <Label size={22} spacing={4}>NOTHING TO COMPARE AGAINST</Label>
        </div>
      </Card>
    </Frame>
  );
};

/* 17 — Used cars: Lacetera, Pope & Sydnor; 22 million sales. */
export const Cars: React.FC = () => {
  const frame = useCurrentFrame();
  const n = Math.round(22_000_000 * ramp(frame, CUE["cars.count"], CUE["cars.countEnd"], Easing.out(Easing.cubic)));
  return (
    <Frame>
      <Icon kind="car" start={CUE["cars.car"]} left={150} top={400} width={760} />
      <Card start={CUE["cars.names"]} left={1000} top={170} width={760} height={330} name="economists" rotate={-0.8} pad="48px 56px">
        <Label size={24} spacing={6} color={C.red}>ECONOMISTS</Label>
        <div style={{ fontFamily: PLAYFAIR, fontSize: 50, lineHeight: 1.18, color: C.inkDeep, marginTop: 16, whiteSpace: "nowrap" }}>
          Nicola Lacetera,
          <br />
          Devin Pope &amp; Justin Sydnor
        </div>
      </Card>
      <Card start={CUE["cars.count"] - 8} left={1000} top={580} width={760} height={300} name="sales counter" rotate={0.6} pad="48px 56px">
        <div style={{ fontFamily: ARIAL, fontSize: 84, color: C.ink, lineHeight: 1, fontVariantNumeric: "tabular-nums", whiteSpace: "nowrap" }}>
          {n.toLocaleString("en-US")}
          <span style={{ color: C.red }}>+</span>
        </div>
        <Label size={26} spacing={6} style={{ marginTop: 26 }}>USED-CAR SALES STUDIED</Label>
      </Card>
    </Frame>
  );
};

/* 18 — 79,900 miles sold for ~$210 more than 80,000. */
const OdoColumn: React.FC<{ at: number; left: number; from: number; to: number; rollAt: number }> = ({ at, left, from, to, rollAt }) => (
  <Rise start={at} dur={28} left={left} top={190} width={660} height={460} z={12} style={{ filter: "none" }}>
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
      <Glyph kind="car" width={380} />
      <div style={{ marginTop: 44 }}>
        <Odometer from={from} to={to} at={rollAt} width={540} digits={5} />
      </div>
      <Label size={24} spacing={6} style={{ marginTop: 18 }}>MILES</Label>
    </div>
  </Rise>
);

export const OdometerScene: React.FC = () => {
  const frame = useCurrentFrame();
  return (
    <Frame>
      <OdoColumn at={CUE["odometer.left"]} left={180} from={79900} to={79900} rollAt={0} />
      <OdoColumn at={CUE["odometer.right"]} left={1080} from={79999} to={80000} rollAt={CUE["odometer.cross"]} />
      <div style={{ position: "absolute", left: 180, width: 660, top: 720, textAlign: "center", opacity: useIn(CUE["odometer.more"]), zIndex: 18 }}>
        <Label size={26} spacing={6}>SOLD FOR ABOUT</Label>
        <div style={{ fontFamily: ARIAL, fontSize: 96, color: C.red, lineHeight: 1.1 }}>+$210</div>
      </div>
      <div style={{ position: "absolute", left: 1080, width: 660, top: 720, textAlign: "center", opacity: ramp(frame, CUE["odometer.cross"] + 20, CUE["odometer.cross"] + 32), zIndex: 18 }}>
        <Label size={26} spacing={6}>JUST CROSSED</Label>
        <div style={{ fontFamily: ARIAL, fontSize: 96, color: C.ink, lineHeight: 1.1 }}>80,000</div>
      </div>
    </Frame>
  );
};

/* 19 — 100 fewer miles: ~$10. Crossing 80,000: ~$210. A 7 versus an 8. */
const MILES = [79700, 79800, 79900, 80000, 80100, 80200];
const PRICE = [5030, 5020, 5010, 4800, 4790, 4780];
export const Cliff: React.FC = () => {
  const frame = useCurrentFrame();
  const L = 320, R = 1600, TOP = 170, BOT = 560;
  const x = (i: number) => L + (i / (MILES.length - 1)) * (R - L);
  const y = (p: number) => BOT - ((p - 4740) / (5060 - 4740)) * (BOT - TOP);
  const draw = ramp(frame, 6, 46, Easing.inOut(Easing.cubic));
  const d = MILES.map((_, i) => `${i ? "L" : "M"} ${x(i)} ${y(PRICE[i])}`).join(" ");
  const ten = useIn(CUE["cliff.ten"]);
  const cliff = useIn(CUE["cliff.cliff"]);
  return (
    <Frame>
      <div style={{ position: "absolute", right: 1920 - R, top: TOP - 70, opacity: useIn(4), zIndex: 16 }}>
        <Label size={24} spacing={6}>SALE PRICE BY MILEAGE</Label>
      </div>
      <svg width={1920} height={1080} style={{ position: "absolute", inset: 0, zIndex: 14 }}>
        <line x1={L} x2={R} y1={BOT + 40} y2={BOT + 40} stroke={C.ink} strokeWidth={4} opacity={draw} />
        <path d={d} stroke={C.ink} strokeWidth={8} fill="none" strokeLinejoin="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - draw} />
        <path d={`M ${x(1)} ${y(PRICE[1])} L ${x(2)} ${y(PRICE[2])}`} stroke={C.orange} strokeWidth={14} strokeLinecap="round" opacity={ten} />
        <path d={`M ${x(2)} ${y(PRICE[2])} L ${x(3)} ${y(PRICE[3])}`} stroke={C.red} strokeWidth={14} strokeLinecap="round" opacity={cliff} />
        {MILES.map((_, i) => (
          <circle key={i} cx={x(i)} cy={y(PRICE[i])} r={10} fill={C.ink} opacity={draw} />
        ))}
      </svg>
      {MILES.map((m, i) => (
        <div key={m} style={{ position: "absolute", left: x(i) - 90, width: 180, top: BOT + 54, textAlign: "center", opacity: draw, zIndex: 16 }}>
          <Label size={24} color={C.ink} spacing={2}>{m.toLocaleString("en-US")}</Label>
        </div>
      ))}
      <div style={{ position: "absolute", left: (x(1) + x(2)) / 2 - 110, width: 220, top: y(PRICE[1]) - 96, textAlign: "center", opacity: ten, zIndex: 16 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 52, color: C.orange }}>−$10</div>
      </div>
      <div style={{ position: "absolute", left: x(3) + 30, top: (y(PRICE[2]) + y(PRICE[3])) / 2 - 40, opacity: cliff, zIndex: 16 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 64, color: C.red, lineHeight: 1 }}>−$210</div>
        <Label size={22} spacing={4} style={{ marginTop: 8 }}>SAME CAR, 100 MILES</Label>
      </div>
      {[
        { at: CUE["cliff.seven"], left: 400, num: "79,900", t: "STARTS WITH A 7" },
        { at: CUE["cliff.eight"], left: 1020, num: "80,000", t: "STARTS WITH AN 8" },
      ].map((c, i) => (
        <Card key={c.num} start={c.at} left={c.left} top={740} width={500} height={220} name={`miles ${c.num}`} rotate={i ? 0.8 : -0.8} pad="34px 40px" style={{ textAlign: "center" }}>
          <div style={{ fontFamily: ARIAL, fontSize: 84, lineHeight: 1, whiteSpace: "nowrap" }}>
            <span style={{ color: C.red }}>{c.num[0]}</span>
            <span style={{ color: C.ink, opacity: 0.45 }}>{c.num.slice(1)}</span>
          </div>
          <Label size={22} spacing={5} style={{ marginTop: 20 }}>{c.t}</Label>
        </Card>
      ))}
    </Frame>
  );
};

/* 20 — A rush to auction just before each 10,000-mile mark. */
const KM = Array.from({ length: 29 }, (_, i) => 52000 + i * 2000);
const vol = (m: number) => {
  const toMark = (10000 - (m % 10000)) % 10000;
  if (toMark === 2000) return 380; // just before a mark
  if (m % 10000 === 0) return 110; // just after
  return 150 + ((m / 2000) % 3) * 22;
};
export const Auction: React.FC = () => {
  const frame = useCurrentFrame();
  const L = 200, R = 1720, BASE = 820;
  const pitch = (R - L) / KM.length;
  const marks = useIn(CUE["auction.marks"]);
  return (
    <Frame>
      <Kicker start={6} text="CARS SENT TO AUCTION" sub="BY ODOMETER READING" />
      {/* the line that the stamp later replaces, in the same clear band above the chart */}
      <div style={{ position: "absolute", left: 0, right: 0, top: 262, textAlign: "center", opacity: useIn(CUE["auction.wins"]) * (1 - ramp(frame, CUE["auction.stamp"] - 10, CUE["auction.stamp"] - 2)), zIndex: 20 }}>
        <div style={{ fontFamily: ARIAL, fontSize: 52, color: C.red, whiteSpace: "nowrap" }}>THE LEFT DIGIT STILL WINS</div>
      </div>
      {KM.map((m, i) => {
        const at = CUE["auction.bars"] + i * 2;
        const g = ramp(frame, at, at + 18, Easing.out(Easing.cubic));
        const spike = vol(m) > 300;
        const red = spike && frame >= CUE["auction.spikes"] + Math.floor(m / 10000) * 3;
        return <div key={m} style={{ position: "absolute", left: L + i * pitch + 6, width: pitch - 12, top: BASE - vol(m) * g, height: vol(m) * g, background: red ? C.red : C.ink, zIndex: 14 }} />;
      })}
      <div style={{ position: "absolute", left: L, width: R - L, top: BASE, height: 5, background: C.ink, zIndex: 15, opacity: useIn(CUE["auction.bars"]) }} />
      {[60000, 70000, 80000, 90000, 100000].map((m) => {
        const xm = L + ((m - 52000) / 2000) * pitch;
        return (
          <React.Fragment key={m}>
            <div style={{ position: "absolute", left: xm - 2, top: BASE - 430, height: 430, borderLeft: `4px dashed ${C.ink}`, opacity: marks * 0.5, zIndex: 13 }} />
            <div style={{ position: "absolute", left: xm - 80, width: 160, top: BASE + 20, textAlign: "center", opacity: marks, zIndex: 16 }}>
              <Label size={28} color={C.ink} spacing={2}>{`${m / 1000}K`}</Label>
            </div>
          </React.Fragment>
        );
      })}
      <Stamp startFrame={CUE["auction.stamp"]} x={0} y={-250} rotate={-3} title="BUYERS, NOT DEALERS" width={880} zIndex={30} />
      <div style={{ position: "absolute", right: 110, bottom: 50, opacity: 0.6 * useIn(CUE["auction.bars"]), zIndex: 16 }}>
        <Label size={18} spacing={3}>ILLUSTRATIVE PATTERN · LACETERA, POPE &amp; SYDNOR (2012)</Label>
      </div>
    </Frame>
  );
};

/* 21 — Chapter 3 */
export const Ch3: React.FC = () => (
  <Frame>
    <ChapterCard n="3" title={<>WHERE DID THE<br />NINE COME FROM?</>} numAt={CUE["ch3.num"]} titleAt={CUE["ch3.title"]} />
  </Frame>
);

export { interpolate, clamp };
