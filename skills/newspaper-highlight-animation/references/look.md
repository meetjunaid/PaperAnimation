# The locked look

This is the spec the renderer implements. Use it to check a render, not to change one.

`assets/reference/` holds master stills for the phrase "AI". They show every card in
both orientations, plus one full-size hero frame per orientation. They were rendered
at 1080p. The 4K output is the same design drawn at twice the resolution.

## Timing

- 23 different pages at 8 cards per second.
- Each card is held 0.125 s and the last card is held 0.25 s, so the total is
  exactly 3.0 s.
- At 60 fps the cards alternate 8 and 7 frames, for 180 frames in total. At
  24 fps every card is 3 frames, with the last held for 6.
- Stepped, with no in-betweens. Fresh film grain on every frame (σ≈0.022) keeps
  it alive.

## Anchor

The centre of the highlighted phrase sits exactly at the centre of the frame on
every card. Rotation (±2°) pivots around it.

## Highlight

- A solid yellow marker box with slightly uneven corners.
- Print pages use (0.98, 0.86, 0.36), with a marker-streak texture.
- Web pages use (1.0, 0.89, 0.30).
- On dark-mode web pages, the phrase text turns black on the marker.

## Card order

1. News body ×2, news headline, web article, news body, magazine pull-quote
2. Dense news, news headline, web headline, typewriter memo, news body, magazine headline
3. Dark-mode web, news headline, dense news, web article, magazine pull-quote
4. News body, web headline, dense news, news headline
5. Tabloid, tabloid (the ending punch)

## Print treatment

- Warm newsprint (~#E7E2D6) with mottling and fibres.
- 3–7 creases with ridge highlights.
- A lighting gradient and a vignette.
- Uneven ink and a 0.6 px ink bleed. All pixel sizes are at 1080p and scale with
  resolution.
- Some cards get shallow depth of field away from the phrase.

## Typography

| Use | Fonts |
| --- | --- |
| Body serifs | Times, Georgia, Baskerville, Charter, Hoefler, PT Serif, Iowan, Palatino, Cochin |
| Headlines | Bodoni, Didot, Big Caslon |
| Web pages | Helvetica Neue, Avenir, Verdana |
| Memo | American Typewriter or Courier |
| Tabloids | Impact, Arial Black, DIN Condensed or Avenir Next Condensed |

These are macOS system fonts. Any that the system lacks, as on Windows and
Linux, is replaced by an open-licensed lookalike bundled in `assets/fonts/`
(see the README there). The layout is identical; only the type design differs
slightly. macOS never uses the bundled fonts.

## Copy

- All copy is fictional: no real outlets, names or brands.
- The phrase is used only as a noun phrase, with no verb agreeing with it, so any
  phrase reads naturally.
- No sentence or headline containing the phrase repeats within a video.

## Determinism

The seed is the CRC32 of the phrase, so the same phrase always lays out the same
pages.

## Long phrases

- If the phrase is wider than 86% of the frame or column, its style is scaled
  down so the highlight stays fully on screen.
- Tabloid endings get smaller for very long phrases.

## Sound (optional, `--sound`)

- A synthesised projector rattle runs under the whole video. It is not synced
  to page changes, just like a real projector.
- About 42 clicks per second, from a repeating 300 ms gear pattern of gaps
  (24, 23, 13, 30, 24, 29, 24, 24, 23, 13, 30, 24, 19 ms) with per-click accents.
- Each click is a ~5 ms band-passed noise burst in one of two bright voices
  (~9 kHz and ~13.5 kHz), over a faint hiss at −47 dBFS.
- It sits quietly at about −36 dBFS RMS, with no low end at all.
- Every knob (speed, level, tone, click length, hiss) is at the top of
  `scripts/sound.py`.
- AAC at 256 kb/s, 48 kHz stereo. Without `--sound` the video is silent.

## Encoding

- H.264 High, yuv420p, BT.709 (limited range), with BT.709 tags.
- Encoder: Apple VideoToolbox at constant quality 80 when available (macOS),
  otherwise x264 `fast` at CRF 14 (Windows, Linux).
- Both videos render in parallel when the machine has at least 8 GB of RAM,
  otherwise one after the other. Each 4K render peaks at about 2 GB.
