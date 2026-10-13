---
name: newspaper-highlight-animation
description: Make a 3-second "newspaper highlight" hook video, a stop-motion flip through 23 newspaper, magazine and web-article pages where one word or phrase is highlighted in yellow marker and pinned to the centre of the frame. Renders 4K 60 fps in both vertical reel (2160x3840) and YouTube landscape (3840x2160) at once, with an optional projector sound. Use when the user asks for a newspaper highlight video, paper animation hook, highlighted-word intro, news-clipping montage, or "the highlight video for <phrase>".
license: MIT
compatibility: macOS, Windows or Linux with Python 3.11+, including the Claude.ai and ChatGPT code sandboxes. The first run installs about 250 MB of Python packages. Minimal Linux installs also need the system GL libraries (libegl1, libgl1).
metadata:
  version: "1.1.0"
---

# Newspaper highlight animation

A locked, reusable design. Do NOT redesign it, restyle it or add motion. Only the
highlighted phrase changes.

## 1. Ask two questions, one at a time

1. Ask: **"What word or phrase should be highlighted?"** Wait for the answer. Use
   the user's exact spelling and capitalisation. Ask even if you think you know it.
2. Then ask: **"Do you want the projector sound?"** as a multiple-choice question
   with two options, using your structured question tool if you have one (in
   Claude Code, AskUserQuestion):
   - **Yes**: a fast mechanical projector rattle under the whole video
   - **No**: silent, so they can add their own music

   Without such a tool, ask the same question and accept yes or no.

Render only after both answers.

## 2. Render

Run the launcher in this skill's `scripts/` folder. On Windows use `py` or
`python` instead of `python3`.

```sh
python3 "<this skill's directory>/scripts/make.py" "<phrase exactly as given>" [output_dir] [--sound]
```

Add `--sound` only if the user answered Yes.

- It renders both orientations in 4K at 60 fps. This takes about 2 minutes on
  Apple Silicon, which has a hardware encoder. Elsewhere it takes several
  minutes, about 5–10 depending on the machine.
- Give the command a timeout of at least 20 minutes, because the first run also
  installs the dependencies.
- The default output folder is `~/Downloads/newspaper-highlight-animation/`.
- It writes `<slug>_reel_2160x3840_60fps.mp4` and
  `<slug>_youtube_3840x2160_60fps.mp4`.
- The first run creates a Python environment in the user's cache folder. If it
  says Python 3.11+ is missing, or prints commands to install system graphics
  libraries (minimal Linux installs), pass that on to the user.

### In a hosted sandbox (Claude.ai, ChatGPT and similar)

If you are running in a web app's code sandbox rather than on the user's own
computer, render each orientation as its own command, so each one finishes
within the sandbox's time limit, and add `--web`:

```sh
python3 "<this skill's directory>/scripts/make.py" "<phrase>" <outputs folder> --web --only reel [--sound]
python3 "<this skill's directory>/scripts/make.py" "<phrase>" <outputs folder> --web --only youtube [--sound]
```

- `--web` still renders 4K at 60 fps but keeps each file at about 25 MB, under
  the web apps' 30 MB download limit. It looks the same as the full-size file.
- Use the folder your platform offers for downloads (for example
  `/mnt/user-data/outputs` on Claude.ai or `/mnt/data` on ChatGPT), then give the
  user both files to download.
- Each command takes about 2–4 minutes. The first one also installs the
  dependencies.
- If it prints commands to install the system graphics libraries and you can
  run `apt-get` (with `sudo` if needed), install them and run it again.

## 3. Verify before reporting

`make.py` checks its own output. For each video it prints the size, frame rate,
frame count, duration and whether it has sound, and saves a contact sheet with
one thumbnail per card.

- Each file should be 180 frames, 60 fps and 3.00 s long, and "with sound" only
  if `--sound` was used.
- Open both contact sheets and look at them. A thin red cross marks the frame
  centre: the highlighted phrase should sit on it in every card, and a long
  phrase must not be cut off at the frame edge.
- Report only what you checked.

## Other sizes

`scripts/render.py "<phrase>" <width> <height> <fps> <out.mp4>` renders any
single size, using the Python environment that `make.py` created. Layout scales
from the short side, so 1080x1920 at 24 fps gives a 1080p version.
`--cards-dir DIR` also saves every card as a full-resolution PNG still, and
`--sound` adds the projector rattle.

## Reference

- The full design spec (timing, card order, highlight colours, paper, fonts,
  copy rules, sound): [references/look.md](references/look.md)
- Master stills for the phrase "AI": `assets/reference/`
