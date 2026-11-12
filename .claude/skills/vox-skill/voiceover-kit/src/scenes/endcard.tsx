import React from "react";
import { Easing, interpolate, useCurrentFrame } from "remotion";
import { C, DROP, ARIAL, Frame, Headline, Label, Rise, clamp, ramp, useIn } from "./lib";

/**
 * YouTube end screen: a 16:9 video placeholder either side, the channel circle
 * and a SUBSCRIBE button in the middle. The frames and the circle are where
 * YouTube Studio's end-screen elements go, so once in they hold still.
 * Start it on the sign-off line ("Tell me in the comments…") and give the
 * timeline `tail` enough frames that it lasts 10–20 s (YouTube allows 5–20).
 */
const VIDEO = { w: 640, h: 360, top: 370 };

const VideoSlot: React.FC<{ at: number; left: number; label: string; rot: number }> = ({ at, left, label, rot }) => {
  const frame = useCurrentFrame();
  return (
    <>
      <div style={{ position: "absolute", left, width: VIDEO.w, top: VIDEO.top - 66, textAlign: "center", opacity: ramp(frame, at + 6, at + 18), zIndex: 18 }}>
        <Label size={26} spacing={8} color={C.ink}>{label}</Label>
      </div>
      <Rise start={at} dur={28} dist={240} left={left} top={VIDEO.top} width={VIDEO.w} height={VIDEO.h} rotate={rot} z={14} style={{ filter: "none" }}>
        <div aria-hidden style={{ position: "absolute", inset: 0, background: C.red, transform: "translate(-16px, 10px)" }} />
        <div data-fit={`end screen ${label}`} style={{ position: "absolute", inset: 0, background: C.card, padding: 16, boxSizing: "border-box", filter: DROP }}>
          <div style={{ width: "100%", height: "100%", background: C.inkDeep, display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width={110} height={110} viewBox="0 0 110 110">
              <circle cx={55} cy={55} r={52} fill="none" stroke="rgba(239,235,224,0.35)" strokeWidth={5} />
              <path d="M 44 34 L 78 55 L 44 76 Z" fill="rgba(239,235,224,0.55)" />
            </svg>
          </div>
        </div>
      </Rise>
    </>
  );
};

export const EndCard: React.FC<{
  thanksAt: number;
  leftAt: number;
  subAt: number;
  rightAt: number;
  prompt?: string;
  leftLabel?: string;
  rightLabel?: string;
}> = ({ thanksAt, leftAt, subAt, rightAt, prompt = "TELL ME IN THE COMMENTS", leftLabel = "WATCH NEXT", rightLabel = "YOU MAY ALSO LIKE" }) => {
  const frame = useCurrentFrame();
  const pop = interpolate(frame, [subAt, subAt + 8, subAt + 14], [0.6, 1.08, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const subOn = ramp(frame, subAt, subAt + 8);
  const btnAt = subAt + 10;
  const btn = ramp(frame, btnAt, btnAt + 12, Easing.out(Easing.back(1.6)));
  const pulse = frame > btnAt + 40 ? 1 + 0.025 * Math.sin(((frame - btnAt - 40) / 30) * Math.PI * 1.4) : 1;
  return (
    <Frame push={0}>
      <Headline at={thanksAt} text="THANKS FOR WATCHING" top={110} size={68} />
      <div style={{ position: "absolute", left: 0, right: 0, top: 200, textAlign: "center", opacity: useIn(thanksAt + 12), zIndex: 18 }}>
        <Label size={26} spacing={8} color={C.red}>{prompt}</Label>
      </div>
      <VideoSlot at={leftAt} left={120} label={leftLabel} rot={-0.6} />
      <VideoSlot at={rightAt} left={1160} label={rightLabel} rot={0.6} />
      <div data-fit="subscribe circle" style={{ position: "absolute", left: 850, top: 390, width: 220, height: 220, borderRadius: "50%", background: C.card, border: `10px solid ${C.red}`, boxSizing: "border-box", opacity: subOn, transform: `scale(${pop})`, filter: DROP, zIndex: 16, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <svg width={96} height={96} viewBox="0 0 96 96">
          <circle cx={48} cy={34} r={18} fill={C.ink} />
          <path d="M 14 88 Q 14 58 48 58 Q 82 58 82 88 Z" fill={C.ink} />
        </svg>
      </div>
      <div
        data-fit="subscribe button"
        style={{ position: "absolute", left: 810, top: 650, width: 300, height: 76, borderRadius: 14, background: C.red, boxShadow: `6px 7px 0 ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "center", gap: 14, opacity: btn > 0 ? 1 : 0, transform: `translateY(${(1 - btn) * 40}px) scale(${pulse})`, zIndex: 17 }}
      >
        <svg width={30} height={30} viewBox="0 0 30 30">
          <path d="M 15 3 Q 6 3 6 13 L 6 20 L 3 24 L 27 24 L 24 20 L 24 13 Q 24 3 15 3 Z" fill="#FFF6EE" />
          <circle cx={15} cy={27} r={3} fill="#FFF6EE" />
        </svg>
        <div style={{ fontFamily: ARIAL, fontSize: 32, letterSpacing: 3, color: "#FFF6EE" }}>SUBSCRIBE</div>
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 860, textAlign: "center", opacity: useIn(rightAt + 20), zIndex: 16 }}>
        <Label size={26} spacing={8} color={C.ink}>SEE YOU IN THE NEXT ONE</Label>
      </div>
    </Frame>
  );
};
