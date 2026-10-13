# Changelog

## 1.1.2 — 2026-10-14

- Both questions now open in one pop-up: type your phrase (or pick a sample), choose the sound, press send. A short summary of the steps appears first.

## 1.1.1 — 2026-10-14

- Fix: Claude.ai rejected the upload because the skill description contained `<phrase>`, which it reads as an XML tag.

## 1.1.0 — 2026-10-14

- Works on **Claude.ai** and **ChatGPT**: the skill runs in the chat's own sandbox and hands you both videos to download.
- New `--web` mode: still 4K 60 fps, but each file stays around 25 MB, under the web apps' 30 MB download limit, with no visible difference.
- New `--only reel|youtube`: render one orientation per command, to stay within a sandbox's time limit.
- Runs on Python 3.11+, and installs into the system Python where a virtual environment isn't available.
- Every release now carries an upload-ready ZIP, linked from a one-click download button in the README.

## 1.0.0 — 2026-10-14

First public release.

- 3-second newspaper highlight animation: 23 printed and web pages, with the phrase pinned to the centre of the frame.
- Exports 4K 60 fps in both orientations at once: reel 2160x3840 and YouTube 3840x2160.
- Runs on macOS, Windows and Linux. On a Mac it uses the original macOS typefaces; elsewhere it uses bundled open-licensed lookalikes.
- Uses Apple's hardware encoder on macOS (about 2 minutes for both videos on Apple Silicon) and x264 everywhere else.
- Optional `--sound`: a synthesised projector rattle, a fast, bright run of mechanical clicks under the whole video. No samples, so no licensing. Its settings sit at the top of `scripts/sound.py`.
- Asks two questions before rendering: the phrase, then a Yes/No choice for the projector sound.
- Checks its own output: size, frame rate, frame count, duration and sound, plus a per-card contact sheet with a centre marker.
- Works as an Agent Skill and as a Claude Code plugin.
