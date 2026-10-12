import json
tl=json.load(open('timeline.json')); s=json.load(open('script.json'))
V=[
("Hook","Zoomed on the PSX board. Marker draws the board, then `PSX`, `SHARES` + a price squiggle, then `SUKUK` with a red **?**"),
("Step 1 · The asset","Board labels wipe away. Pull back to the whole board, then zoom to the top: a motorway is drawn left→right"),
("","Zoom into the first slice: divider, green hatch, arrow down to one certificate, labelled `sukuk`"),
("","Pull back slightly: four more dividers, five more identical certificates, `equal slices`"),
("","Wider: `M-1` road sign, then a plane with `Jinnah Airport`. **Lock:** detail labels wipe off"),
("Step 2 · The loop","Pull back to the middle: three investors, a government building, then a green `money` arrow investors→government with coins moving along it, and an arrow carrying a certificate down from the asset to the investors"),
("","Zoom right: a car is drawn and drives along the motorway, then a blue `lease` arrow from the road down to the government"),
("","Zoom to centre: green rent arrow government→investors, coins flowing right→left, `rent`"),
("","`rent` circled; `interest` written in red and struck through"),
("","Zoom by the lease arrow: `Ijarah = lease`. **Lock:** labels wipe, leaving `rent`"),
("Step 3 · Maturity","Zoom below: a clock marked 1 · 3 · 5 · 10, hand sweeps once; a buy-back arrow carries a certificate investors→government"),
("","Green arrow government→investors with coins: money returned. **Lock:** clock numbers wipe"),
("Step 4 · The exchange","Pull back to the whole diagram; `PSX`, `SUKUK`, **?** are rewritten on the board"),
("","Zoom left: a calendar with `Dec 2023`; pull back slightly as an arrow carries a certificate government→PSX board"),
("","Zoom left: a green certificate with `Rs 5,000`"),
("","Zoom right: `broker` box with an arrow into the board, `CDC` box with an arrow out of the board; a certificate moves into CDC"),
("","Zoom below the board: a stack of notes builds up, `Rs1 trillion+`"),
("","The **?** wipes away; a dashed 'price paid' line, then a red price line wiggling above and below it"),
("Payoff","Final pull back to the complete diagram. Labels wipe; the takeaway is written above it: **Own a slice. / Collect the rent.**"),
]
o=["# Sukuk on the Pakistan Stock Exchange: storyboard\n",
"1080×1920 · %.1f s · voice: Kokoro `af_heart` (offline neural TTS) · whiteboard marker style\n" % tl['total'],
"## The diagram (fixed layout, one canvas)\n",
"```\n        [M-1]                                  ✈ airport\n   ==|=====|=====|=====|=====|=====|==   ← motorway, cut into 6 equal slices\n    [▤]  [▤]  [▤]  [▤]  [▤]  [▤]          ← sukuk certificates\n     |                          |  lease\n     ↓        money →           ↓\n   웃웃웃  ─────────────▶   🏛 Government\n Investors ◀─────────────\n               rent\n          ╰── buy-back ──╯  (clock 1·3·5·10)\n          ╰─ money back ─╯\n [Dec 2023]  ┌──── PSX ────┐ ◀─ [broker]\n [Rs 5,000]  │ SUKUK  ~~~  │ ─▶ [CDC]\n             └─────────────┘\n               [notes] Rs1 trillion+\n```\n",
"## Timed storyboard\n","| # | Time (s) | Voice (s) | Narration | On screen |","|---|---|---|---|---|"]
for l,(sec,v) in zip(tl['lines'],V):
    o.append(f"| {l['i']} {('**'+sec+'**') if sec else ''} | {l['slot']:.1f}–{l['end']:.1f} | {l['v0']:.1f}–{l['v1']:.1f} | {s[l['i']]['sub']} | {v} |")
o.append("\nRules enforced by `check.js`: never more than 7 words of on-screen text in frame (checked every 0.05 s), every label held ≥0.3 s per word, and no two motions (draw, erase, camera, flow) overlap in time.\n")
open('storyboard.md','w').write('\n'.join(o))
