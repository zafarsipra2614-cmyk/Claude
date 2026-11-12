import React from "react";
import { CUE } from "../shared/timing";
import { Stamp } from "../shared/pieces";
import { Kicker } from "./kit";
import { ChapterCard, Frame, Tag } from "./lib";
import { EndCard } from "./endcard";
import { ArchivePhoto, NewsClipping } from "./archive";
import { PullBack, SnapZoom } from "./camera";

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

/* A documentary beat: a pull-back reveals an archive photo, a clipping lands beside it,
 * then a snap zoom punches in on the clipping's headline as its key word is said. */
export const Doc: React.FC = () => (
  <Frame push={0}>
    <SnapZoom at={CUE["doc.zoom"]} x={1380} y={420} to={1.12} settle={1.06}>
      <PullBack dur={50} x={560} y={500} from={2}>
        <ArchivePhoto src="archive/placeholder.jpg" start={CUE["doc.photo"]} left={160} top={180} width={760} height={520} caption="A shop counter, around 1900" credit="PLACEHOLDER · REPLACE WITH A CREDITED COMMONS IMAGE" />
        <NewsClipping start={CUE["doc.clip"]} left={1040} top={240} width={680} height={290} masthead="The Evening Ledger" date="1922" headline="Odd prices catch on" highlight="Odd prices" body="Merchants find that a price just under the round dollar draws the eye. Most now end in 95." />
      </PullBack>
    </SnapZoom>
  </Frame>
);

export const End: React.FC = () => (
  <EndCard thanksAt={CUE["endcard.thanks"]} leftAt={CUE["endcard.left"]} subAt={CUE["endcard.sub"]} rightAt={CUE["endcard.right"]} />
);
