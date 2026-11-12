import React from "react";
import { CUE } from "../shared/timing";
import { Stamp } from "../shared/pieces";
import { Kicker } from "./kit";
import { ChapterCard, Frame, Tag } from "./lib";
import { EndCard } from "./endcard";

/*
 * Example scenes: replace with the film's own (one component per scene, cues
 * from CUE). They show the three building blocks every film uses: tags on a
 * clean layout, a chapter card, and the end screen.
 */
export const Hook: React.FC = () => (
  <Frame>
    <Kicker start={4} text="ONE CENT APART" />
    <Tag x={330} y={360} w={560} price="$10.00" start={CUE["hook.a"]} rot={-2} />
    <Tag x={1030} y={360} w={560} price="$9.99" tone="red" start={CUE["hook.b"]} rot={2} />
    <Stamp startFrame={CUE["hook.stamp"]} x={0} y={300} rotate={-4} title="SAME PRICE?" width={460} zIndex={30} />
  </Frame>
);

export const Ch1: React.FC = () => (
  <Frame>
    <ChapterCard n="1" title={<>THE FIRST<br />CHAPTER</>} numAt={CUE["ch1.num"]} titleAt={CUE["ch1.title"]} />
  </Frame>
);

export const End: React.FC = () => (
  <EndCard thanksAt={CUE["endcard.thanks"]} leftAt={CUE["endcard.left"]} subAt={CUE["endcard.sub"]} rightAt={CUE["endcard.right"]} />
);
