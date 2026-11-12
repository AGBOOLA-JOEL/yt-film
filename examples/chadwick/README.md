# Example: Carnegie's Daughter (Cassie Chadwick)

A complete yt-film project: the woman who, as "Cassie L. Chadwick", borrowed millions from Ohio bankers on the
strength of a forged note signed "Andrew Carnegie" and a sealed envelope nobody opened (1857–1907). 12 minutes,
9 batches, 164 images. Use it to learn how every technique is written and how a film is put together.

## Watch first
`video/chadwick_effects_test.mp4`: the 70-second effects test (narration in `TEST_SCRIPT.md`, shots in
`tools/test_shots.py`). In order: a street drawing itself and coming alive (coal smoke, breath, gas lamps, snow, a
typed place label); Carnegie drawn beside his house (ink, then colour); she stumbles, the note slips from her muff
and lands on the pavement; the lawyer's eyes widen; the note's words written on its lines, then FORGED stamped; the
con drawn as a chain on a card (note → envelope → vault → receipt → the next banker); a dinner with candles, chandelier
and fire while a counter rolls to $2,000,000; a glass shatter into the next scene; the run on the bank with a crowd
murmur; the note tearing in two; a footnote card.

`look/` has one still of each technique (comic page, living map, drawing on a scene, explainer card, footnote card,
real photo print, halftone newspaper, lifted note, shatter, names crossed out, leader label, typed place label...).
`look/flow_smear_avoid.png` shows what NOT to do (pixel-warped smoke smearing the painting).

## What's here
| Path | What |
|---|---|
| `OUTLINE.md` | the verified facts with sources, weak ones flagged, the hook choice, the footnotes |
| `IMAGE_GUIDE.md` | the 164-image guide (written for ChatGPT): spine, opener, character blocks, every shot |
| `SCRIPT.md` | the narration, 49 passages with `[SHOTS: …]`, `[NOTE n]`, `[PHOTO: …]`, `[FX: …]` notes |
| `TEST_SCRIPT.md` | the effects test's narration |
| `incoming/` | every image: style card, cast sheets, 129 scenes (JPEG here to keep the repo small; the guide says .png, the engine reads both), sketch sheets + line versions, bases, real archive photos with `CREDITS.md` |
| `research/` | *The Great Chadwick Bubble* (1904 pamphlet, public domain), a primary source |
| `voice/` | the narration per batch + Whisper word timings (so the example renders without an API key) |
| `audio/music/` | the 7 Lyria cues and their prompts; `audio/walla/` the bank-run crowd murmur |
| `build/edit/` | one hand-prepared image (the note with its writing) |
| `tools/chad.py` | the film module: the LIVE table (living layers of 120 pictures), map settings, photo credits |
| `tools/shots_b1…b9.py` | the nine batches' shot lists |
| `tools/test_shots.py` | the effects test |
| `tools/voice.py`, `music.py`, `final.py`, `walla.py` | the film's batches, gaps, speeds, cues, cue map, crowd lines |
| `tools/script_check.py` | the check that every image is placed in the script |

## Load it
```bash
python scripts/new_project.py chadwick --example chadwick      # copies the engine + this folder into a project
cd ~/yt-film-projects/chadwick/tools
python stills.py b1        # contact sheet of batch 1 + readability check, ~30 s, no render
python stills.py b6 12     # any batch
```
(Use the repo's `.venv` Python.) Rendering the full film takes ~25 min on a fast Mac and a few hours on a slow PC;
only do it if you want to (`python render_all.py`, then `python final.py`; make an ending first or it ends on b9).

## How to learn from it
Open a shots file and its stills sheet side by side. Every `S.at(...)` line is a shot at a time in the narration;
`LIVE` in `chad.py` says what lives on each picture. Ask Claude: *"explain shots_b5.py line by line"*, *"how was the
con drawn on the envelope?"*, *"make a shot like the falling note for my film"*.
