<div align="center">

# 📰 Newspaper Highlight Animation

### Turn any word into a 3-second newspaper hook, exported in **4K at 60 fps**.

23 newspaper, magazine and web pages flip past, with **your word highlighted in yellow, dead-centre, on every one.**
Reel and YouTube versions, rendered at once.

[![4K 60 fps](https://img.shields.io/badge/export-4K%20·%2060%20fps-f5d547?style=for-the-badge)](#-what-you-get)

[![macOS](https://img.shields.io/badge/macOS-✓-222?style=flat-square&logo=apple)](#-requirements)
[![Windows](https://img.shields.io/badge/Windows-✓-222?style=flat-square&logo=windows)](#-requirements)
[![Linux](https://img.shields.io/badge/Linux-✓-222?style=flat-square&logo=linux&logoColor=white)](#-requirements)
[![Agent Skill](https://img.shields.io/badge/Agent%20Skills-open%20standard-5a67d8?style=flat-square)](https://agentskills.io)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-d97757?style=flat-square)](#-install)
[![MIT](https://img.shields.io/badge/license-MIT-2ea44f?style=flat-square)](LICENSE)

<img src="media/demo-youtube.gif" alt="Demo: the phrase 'Your Text Here' highlighted on 23 flipping newspaper, magazine and web pages" width="640">
&nbsp;
<img src="media/demo-reel.gif" alt="The same animation in vertical reel format" width="180">

<sub>A downsized, silent preview. **[🔊 Watch it with the projector sound](media/demo-with-sound.mp4)**</sub>

</div>

---

## ✨ What you get

| | |
| --- | --- |
| 🎬 **4K · 60 fps** | Two finished videos per run: reel **2160 × 3840** and YouTube **3840 × 2160** |
| 🖍️ **Your word, dead-centre** | 23 pages from newspapers, magazines, web articles, a memo and a tabloid finale, with your word always on the exact centre of the frame |
| 🔊 **Optional projector sound** | A fast mechanical rattle, synthesised in code, so there's nothing to license |
| 💻 **Runs everywhere** | macOS, Windows and Linux |
| ✅ **Checks its own work** | Frame count, frame rate, duration and sound, plus a contact sheet of every page |

No templates to buy, no After Effects, no keyframes. Every page is drawn from scratch:
newsprint fibres, creases, ink bleed, marker streaks and film grain.

## 📦 Install

<details open>
<summary><b>Claude Code (recommended)</b></summary>

<br>

```text
/plugin marketplace add meetjunaid/newspaper-highlight-animation
/plugin install newspaper-highlight-animation@newspaper-highlight-animation
```

Update later with `claude plugin update newspaper-highlight-animation@newspaper-highlight-animation`.

</details>

<details>
<summary><b>Codex, Cursor and other agents</b></summary>

<br>

```sh
npx skills add meetjunaid/newspaper-highlight-animation
```

or, with the GitHub CLI (v2.90+):

```sh
gh skill install meetjunaid/newspaper-highlight-animation newspaper-highlight-animation
```

</details>

<details>
<summary><b>Manual</b></summary>

<br>

```sh
git clone https://github.com/meetjunaid/newspaper-highlight-animation
cp -R newspaper-highlight-animation/skills/newspaper-highlight-animation ~/.claude/skills/
```

The skill is just the `skills/newspaper-highlight-animation/` folder. Put it wherever your agent looks for skills.

</details>

## ✍️ Use it

Ask your agent for it in plain words:

```text
> make the newspaper highlight video
```

It asks you two quick questions, **what word to highlight** and **whether you want the
projector sound** (yes or no), then renders both videos into
`~/Downloads/newspaper-highlight-animation/`.

<details>
<summary><b>Prefer the terminal?</b></summary>

<br>

```sh
python3 skills/newspaper-highlight-animation/scripts/make.py "Your Phrase" [output_dir] [--sound]
```

On Windows, use `py` instead of `python3`.

</details>

## 🧰 Requirements

| | |
| --- | --- |
| 🐍 **Python 3.12+** | From [python.org](https://www.python.org/downloads/), or `brew install python` on a Mac |
| 💾 **About 250 MB** | Installed automatically, once, on the first run |
| ⏱️ **Render time** | About 2 minutes on Apple Silicon (hardware encoder), about 5–10 minutes on Windows and Linux |
| 🐧 **Minimal Linux only** | Desktop Linux is ready to go. Servers and containers need `sudo apt install libegl1 libgl1`, and the skill tells you if so |

## 💌 FAQ

<details>
<summary><b>Will it look the same on Windows and Linux?</b></summary>

<br>

Same pages, same layout, same highlight. The design uses classic macOS typefaces
(Didot, Bodoni, Baskerville…). Where a system doesn't have them, the skill uses
bundled open-licensed lookalikes, so the type differs only slightly.

</details>

<details>
<summary><b>Can I tweak the sound?</b></summary>

<br>

Yes. Speed, loudness, tone, click length and hiss are all at the top of
[`scripts/sound.py`](skills/newspaper-highlight-animation/scripts/sound.py).

</details>

<details>
<summary><b>Will the same word give me the same video?</b></summary>

<br>

Yes. The pages are seeded from your phrase. Only the film grain is fresh on every frame, like real film.

</details>

<details>
<summary><b>Can I change the look?</b></summary>

<br>

Fork it and edit `scripts/render.py` (the pages) and `scripts/copy_text.py` (all the
fictional news). The full design spec is in
[`references/look.md`](skills/newspaper-highlight-animation/references/look.md).

</details>

## 📜 License

[MIT](LICENSE) © 2026 Junaid Ahmed. Bundled fonts are under the SIL Open Font License; see
[`assets/fonts`](skills/newspaper-highlight-animation/assets/fonts/).

<div align="center"><sub>⭐ Star the repo if it made your next video pop.</sub></div>
