# Sukuk on the Pakistan Stock Exchange: storyboard

1080×1920 · 140.0 s · voice: Kokoro `af_heart` (offline neural TTS) · whiteboard marker style

## The diagram (fixed layout, one canvas)

```
        [M-1]                                  ✈ airport
   ==|=====|=====|=====|=====|=====|==   ← motorway, cut into 6 equal slices
    [▤]  [▤]  [▤]  [▤]  [▤]  [▤]          ← sukuk certificates
     |                          |  lease
     ↓        money →           ↓
   웃웃웃  ─────────────▶   🏛 Government
 Investors ◀─────────────
               rent
          ╰── buy-back ──╯  (clock 1·3·5·10)
          ╰─ money back ─╯
 [Dec 2023]  ┌──── PSX ────┐ ◀─ [broker]
 [Rs 5,000]  │ SUKUK  ~~~  │ ─▶ [CDC]
             └─────────────┘
               [notes] Rs1 trillion+
```

## Timed storyboard

| # | Time (s) | Voice (s) | Narration | On screen |
|---|---|---|---|---|
| 0 **Hook** | 0.0–7.1 | 1.9–6.7 | You know how shares work. But what is a sukuk, on the Pakistan Stock Exchange? | Zoomed on the PSX board. Marker draws the board, then `PSX`, `SHARES` + a price squiggle, then `SUKUK` with a red **?** |
| 1 **Step 1 · The asset** | 7.1–13.5 | 9.7–13.0 | Start with something real. Say, a stretch of motorway. | Board labels wipe away. Pull back to the whole board, then zoom to the top: a motorway is drawn left→right |
| 2  | 13.5–19.8 | 14.7–19.4 | A sukuk is a certificate that gives you a share in owning an asset like this. | Zoom into the first slice: divider, green hatch, arrow down to one certificate, labelled `sukuk` |
| 3  | 19.8–25.7 | 21.0–25.3 | Every certificate has the same value, so each one is an equal slice. | Pull back slightly: four more dividers, five more identical certificates, `equal slices` |
| 4  | 25.7–35.0 | 27.4–34.4 | In Pakistan, government sukuk have used assets like the M-1 motorway and Jinnah International Airport. | Wider: `M-1` road sign, then a plane with `Jinnah Airport`. **Lock:** detail labels wipe off |
| 5 **Step 2 · The loop** | 35.0–46.0 | 37.9–43.5 | Here's how it works. Investors pay money, and the government sells them a share of the asset. | Pull back to the middle: three investors, a government building, then a green `money` arrow investors→government with coins moving along it, and an arrow carrying a certificate down from the asset to the investors |
| 6  | 46.0–51.6 | 47.6–51.1 | But the government still needs the motorway, so it leases it back. | Zoom right: a car is drawn and drives along the motorway, then a blue `lease` arrow from the road down to the government |
| 7  | 51.6–57.1 | 52.9–56.5 | For using it, the government pays rent to the sukuk holders. | Zoom to centre: green rent arrow government→investors, coins flowing right→left, `rent` |
| 8  | 57.1–63.2 | 57.8–62.7 | That's the big idea. Your return is rent from an asset, not interest on a loan. | `rent` circled; `interest` written in red and struck through |
| 9  | 63.2–70.1 | 65.8–69.4 | That's why it's called an Ijarah sukuk. Ijarah means lease. | Zoom by the lease arrow: `Ijarah = lease`. **Lock:** labels wipe, leaving `rent` |
| 10 **Step 3 · Maturity** | 70.1–79.0 | 72.8–78.6 | When the term ends, after one, three, five or ten years, the government buys the asset back, | Zoom below: a clock marked 1 · 3 · 5 · 10, hand sweeps once; a buy-back arrow carries a certificate investors→government |
| 11  | 79.0–81.8 | 79.2–81.1 | and investors get their money back. | Green arrow government→investors with coins: money returned. **Lock:** clock numbers wipe |
| 12 **Step 4 · The exchange** | 81.8–86.7 | 84.2–86.3 | So where does the stock exchange come in? | Pull back to the whole diagram; `PSX`, `SUKUK`, **?** are rewritten on the board |
| 13  | 86.7–95.8 | 88.1–95.1 | Since December 2023, Government of Pakistan Ijarah Sukuk have been auctioned through PSX. | Zoom left: a calendar with `Dec 2023`; pull back slightly as an arrow carries a certificate government→PSX board |
| 14  | 95.8–102.3 | 97.0–101.8 | They come in units of 5,000 rupees, small enough for a retail investor. | Zoom left: a green certificate with `Rs 5,000` |
| 15  | 102.3–110.1 | 103.6–109.5 | Open a brokerage account and a CDC sub-account, and you can buy and sell them like shares. | Zoom right: `broker` box with an arrow into the board, `CDC` box with an arrow out of the board; a certificate moves into CDC |
| 16  | 110.1–118.3 | 111.5–117.8 | By September 2024, these PSX auctions had raised over one trillion rupees. | Zoom below the board: a stack of notes builds up, `Rs1 trillion+` |
| 17  | 118.3–126.1 | 119.5–125.4 | One thing to watch: sell before maturity, and the price may be higher or lower than you paid. | The **?** wipes away; a dashed 'price paid' line, then a red price line wiggling above and below it |
| 18 **Payoff** | 126.1–140.0 | 127.7–132.8 | So a sukuk is simple. You own a slice of a real asset, and it pays you rent. | Final pull back to the complete diagram. Labels wipe; the takeaway is written above it: **Own a slice. / Collect the rent.** |

Rules enforced by `check.js`: never more than 7 words of on-screen text in frame (checked every 0.05 s), every label held ≥0.3 s per word, and no two motions (draw, erase, camera, flow) overlap in time.
