---
name: yt-film
description: >-
  Make a narrated YouTube documentary/explainer film end to end with a Python film engine, from a title to the
  finished MP4: story research and a verified fact list, an image guide for whatever image tool the user has
  (ChatGPT, Codex, Google Flow/Whisk, the Gemini API, Midjourney and others) with style and character consistency,
  a narrator script written from the images, the voice (Gemini TTS, or the user's own recording/TTS imported and
  timed with Whisper), a score (Lyria or the user's music), living stills (camera moves, smoke, breath, flames,
  light, weather, lifted objects, tears, shatters), drawings made live, typewriter labels, acting faces, comic pages,
  a living map, footnote cards, synthesised sound, parallel batch renders sized to the machine, an ending, a −14 LUFS
  final join, dubbed audio tracks and thumbnails. Works on macOS and Windows. Use whenever the user wants a new
  video, story ideas, an image guide, a script, voice, music, shots, renders, the final film, dubs, thumbnails, or
  help installing or setting up yt-film, or mentions the Chadwick example.
---

# yt-film: narrated films from still images

A production line for story films: the user makes ~150 still images from a guide Claude writes, Claude writes the
script from those images, a voice reads it, and the **Python engine** brings every picture to life in time with the
words. The reference film is the **Chadwick example** (`examples/chadwick/`, *Carnegie's Daughter*: the woman who
borrowed millions as Andrew Carnegie's secret daughter): its images, script, voice, score, shot lists and the
70-second effects test video (`examples/chadwick/video/chadwick_effects_test.mp4`) show every technique.

**`REPO`** below is this skill's folder (where this file is). **`PY`** is its Python: `REPO/.venv/bin/python` on
macOS/Linux, `REPO\.venv\Scripts\python.exe` on Windows. Always run engine commands with `PY`, from the project's
`tools/` folder. If `.venv` doesn't exist, set up first (`references/install.md`): run `setup/install_mac.sh` or
`setup/install_windows.ps1`, then `scripts/doctor.py`, and fix every `[!!]` line.

## Ground rules
- **Never render without the user's go-ahead.** Check with `stills.py` (a contact sheet in ~30 s). Batch renders,
  previews, the ending and the final join take minutes to hours: say what you'd render and how long it may take, and
  wait for a yes. Don't re-render anything that's already rendered unless it changed and the user wants it.
- **Ask the user's routes once per project**: which image tool (`references/image-generation.md`), voice (Gemini
  TTS or their own: `references/voice.md`), music (Lyria or their own: `references/music.md`), art style (the
  suggested egg-headed pastel look or their own: `references/art-styles.md`), their niche and channel name.
- The user's niche is theirs: don't steer them to history or to the example's subject. The example is a reference
  for techniques, not a template for topics.
- Windows: paths with forward slashes work; long jobs run in the background; speed settings in
  `references/performance.md`. Never assume macOS-only tools.
- No API keys in files other than `.env`. Download real photos or sound files only after the user's OK (state
  the file, source, size and licence).

## The stack
| Job | Tool | Where |
|---|---|---|
| Research | web search, verified fact list with sources; flag what can't be confirmed | `OUTLINE.md` |
| Images | the user's image tool, from Claude's guide | `IMAGE_GUIDE.md` (+ `IMAGE_PROMPTS.jsonl` for the API), `incoming/` |
| Script | Claude, **written from the image guide**, one `##` passage per beat, `[SHOTS: …]` notes | `SCRIPT.md` |
| Voice | Gemini TTS (voice Orus, read slowly → 1.25x, pauses capped) **or** the user's audio via `import_voice.py` | `tools/voice.py`, `tools/import_voice.py` |
| Word timings | Whisper: mlx-whisper (Apple Silicon) or faster-whisper (Windows/Intel/Linux) | `voice/<batch>_words.json` |
| Music | Lyria (Gemini API), one cue per section, **or** the user's licensed tracks | `tools/music.py` → `audio/music/` |
| Film engine | Python (OpenCV, Pillow, NumPy, SciPy), no After Effects | `tools/film.py`, `fx2.py`, `seq.py`, `signature.py`, `wr.py`, `kit.py` |
| Shot lists | one file per batch on `seq.py`, cued on the batch's word times | `tools/<story>.py` + `tools/shots_bN.py` |
| Renders | parallel, sized to the machine, low priority | `tools/render_all.py` |
| Ending | the user's own animated sign-off (example: `cta.py`) | `renders/cta.mp4` |
| Final join | batches + ending, one continuous score, −14 LUFS / −2 dBTP | `tools/final.py` |
| Dubs | Spanish + French by default: Gemini translation + TTS in ~3-min chunks, fitted to the English slots | `tools/dub.py` |
| Thumbnails | the user's image tool, from a guide | `references/thumbnails.md` |

Projects live in `YTF_WORKSPACE` (default `~/yt-film-projects/<story>/`), created by
`PY REPO/scripts/new_project.py <story>`, which copies the engine into `tools/` and makes every folder. Settings
are in `.env` (project first, then REPO): `GEMINI_API_KEY`, `YTF_CHANNEL`, voice/model names, speed knobs
(`.env.example` lists them all). `engine/ytf.py` finds fonts, the key, Whisper and the shared art on any OS.

## The order of work
0. **Pick the story** if not given: 3–5 candidates with gap checks (`references/story-finding.md`).
1. **Story and facts**: research; `OUTLINE.md` with sources. Mark anything unconfirmed and word around it later
   ("reportedly"), never state it as fact. Decide the hook (`references/hooks.md`: never the same type as the
   user's last three films).
2. **Image guide first** (`references/image-guide.md`, written for the user's route). It defines the story beat by
   beat through its shots. Aim for **~150 images**: style card, cast sheets, ~120 scene shots with coverage (W wide,
   M medium, F face close-up as an EDIT, D detail, P point of view), 4 scenes with `_lines` versions, ~9 sketch
   sheets + `_lines`, ~7 blank story objects ("bases": a notebook, an old map, a card, a ledger, an envelope, a
   telegram, a newspaper). Exact filenames and folders. Consistency rules: `references/consistency.md`.
3. **Check images** as groups arrive (hands, faces, era details, no text, shape: images arrive ~16:9 and are
   centre-cropped to 2:1, so nothing important at the very top/bottom). Manual downloads: `scripts/sort_images.py`.
   Then gridded sheets in **engine px** (`COLS=4 PY tools/egrid.py out.png IMG ...`) and map every picture's
   chimneys, lamps, candles, breath and calm areas before writing shots.
4. **Script from the images.** Every generated image is used; map each passage to its shots and run the unused-image
   check (example: `examples/chadwick/tools/script_check.py`). **No length cap**: tell the story fully and
   unhurried (~150 words a minute; Chadwick: 1,780 words → 12 min). End with the user's like/follow line.
5. **Voice**: Gemini (`voice.py --test` first, then batches; `--pace` and `SPEEDS` so every batch sits at ~140–160
   wpm) or the user's audio (`import_voice.py --full | --passages | --batches`). Set `BATCHES` (natural breaks, 4–7
   passages, ~65–100 s each) and `GAPS`. Print each batch's words before writing its shots (Whisper mishears names
   and writes numbers as digits: cue on what it wrote).
6. **Music**: 5–7 cues (`music.py`, or the user's files in `audio/music/`); map cues to batches in `final.py`'s `MUSIC`.
7. **Shot lists** per batch with `seq.py` (`references/engine.md`, `examples/chadwick/tools/`): a film module
   (`<story>.py`, like `chad.py`) holds the `LIVE` table (each picture's living layers) and the map settings; each
   `shots_bN.py` is ~60 lines of `S.at(time, scene(...)/page(...)/drawin(...)/map_shot(...))`. Check each with
   `PY tools/stills.py bN` and **look at the sheet** before anything renders.
8. **Renders** (with the user's OK): `PY tools/render_all.py` runs all batches in parallel, as many at once as the
   machine takes; after fixes, `render_all.py b3 b7` or `--changed`. Test a new transition or effect on two frames
   first (a late crash wastes the render).
9. **Ending** once per channel (`references/cta.md`), then **final join** `PY tools/final.py`; check length, fps,
   loudness on the MP4 (−14 LUFS, peak ≤ −1.5 dB) and sample stills (`references/final-render.md`).
10. **Dubs** (`references/dubs.md`) and **thumbnails** (`references/thumbnails.md`) if wanted.

## The look (the suggested default; the user may choose another)
- **Egg-headed people** (egg head, two dark oval eyes, one-line mouth, no nose/ears/brows, simple rounded hands)
  dressed and lit as part of an **era-accurate real world**; ink line + matte pastel gouache. Backgrounds carry the story.
- **No 2.5D, no cutouts, no AI video.** Single images with eased camera moves (push-ins, pans, slow drift).
- **Never hold one picture too long**: cut to the next shot of the moment (W→M→F→D→P) or to a drawn page.
- **Sketch explainers are real drawings**, not icons: lifted from the sheets' line art or drawn by the engine where
  code does it well (accurate maps, routes, marks, simple figures).
- **Blank bases get drawn on live in their own medium**: graphite on paper, chalk on a board, brush ink, halftone
  photos printing into a newspaper, ink routes on a map.
- **Lines carry meaning**: tally marks for years, sound rings, falling-paper paths, smoke lines, crossed-out figures.
- **Labels** (dates, places, names) are **level typewriter** text, typed one key at a time with a soft click.
- **Writing on an object** sits **on that object's real lines** at their angle; illegible printing under it is
  wiped first (`fx2.clean_text`).
- **Contrast always**: nothing dark on dark. Labels auto-pick cream/ink with a halo. Never force `color="ink"`
  without checking what's under it.
- **The tool sprite is small** (0.28 scale) so it never pulls focus.

## Signature animation (all in code on the still images)
`engine/signature.py`, `engine/fx2.py`, shot helpers `engine/wr.py`, `engine/seq.py`. One still of each in
`examples/chadwick/look/`; every one in motion in the effects test video.
- **Living stills (the picture never moves; layers live on it)**: particle smoke from every chimney, breath in the
  cold, living flames and the light they throw, the picture's own lamps found and breathing (`fx2.lamps`), snow,
  rain, falling leaves, glints. **No pixel-warping** (`sg.Flow`) on smoke, steam, fire or water: it smears the
  painting (`look/flow_smear_avoid.png`).
- **Faces that act, only where it matters**: no automatic blinking or expressions. A face acts only when a shot
  passes `act=` / `talk=`, and only a face with a **matched pair of eyes** (`sg.face_audit([...], out.jpg)`: act only
  where both eyes are ringed green). Cues: `blinks`, `glances`, `widen`, `mouth_fx`, `expr` (smile, grin, frown, o,
  laugh, closed eyes, squint...), `talk=(ta, tb)`, reaction marks (`sweat`, `shake`, `!`, `?`, `zzz`). A handful of
  real beats per batch, never decoration.
- **Comic pages** on the blank board (`sg.Comic`): borders ink themselves, each panel inks then paints in, the camera
  visits panels and dives into the last one. Two per film (the hook, the first big set piece). Each panel holds ≥ 1.8 s.
- **Drawings made live** (`fx2.Draw`): one sheet drawing inks in its stroke order (pen sprite and sound), then its
  colour washes in; `card=True` lays a soft cream wash first on busy pictures. A sheet is **never** shown as a page
  of four: each drawing appears when the narrator names it, linked by arrows and short typed labels.
- **The explainer card** (one base reused): names typed and crossed out, a mechanism as a chain of drawings with
  arrows, three drawings with three words.
- **Mark vocabulary, chosen by meaning, never the same mark every time**: underline, tick, cross, bracket, motion
  lines, sound rings, route (dotted path + arrow), leader (dot, line, typed label), tally; `sg.Stamp` (rubber stamp
  thud: FORGED, CLOSED, 14 YEARS), `sg.Tag` (torn paper label), `sg.Inset`, `sg.Flip` (split-flap), `sg.Pin`,
  `fx2.Counter` (rolling money counter).
- **Effects with weight** (a few felt moments per batch): `fx2.Lift` (cut an object out of the picture and animate it,
  `fill_from=` clone-fills the hole), `fx2.Tear` (the picture tears in two), the `("shatter", s, (cx, cy))`
  transition, `sg.Papers` (tumbling papers), fire + strike, shake + thud, press flashes + shutter, `sg.Rays`, `sg.Haze`.
- **The living map** (`seq.map_shot`): real coastlines ink themselves, water washes in, borders dash in, lakes and
  towns type, a red traveller hops along the route with a dashed trail (`seq.set_map(...)`, Natural Earth in `geo/`).
- **Real photos** (`wr.photo`): an archive photo (public domain/CC, credited) as a period print sliding in with its
  credit typing itself, when the narrator names the real person, place or document.
- **Footnotes** (`wr.footnote`, 4–6 per film, on surprising or one-source facts): a gloved hand brings a folded note
  up, it opens into a tea-stained card in a clear corner and the source types itself while the story plays on; a
  red number marks the shot. The card stays up across cuts until typed + 3 s readable. Art in `assets/footnote/`
  (hand, note, board), replaceable with the user's own. Full sources go in the video description.
- **Crowd murmur** (`walla.py`): layered quiet TTS voices in the scene's language, low-passed, for scenes with people.
- **Flow and finish**: every frame gets a gentle grade, fine grain and a soft vignette; fast moves get motion blur;
  `trans=("dissolve", s)`, `("whip", s, ±1)` (2–3 per film at most), `("flash", s)`, `("shatter", ...)`.
- **Invent new effects per film** from what's in its images (every chimney, lamp, candle, breath, document, safe,
  crowd) and add them to fx2.

## Pacing and readability (the picture never runs ahead of the voice)
Enforced by `b.check()` (runs in stills.py and before every render, and **stops** a render on word problems):
- Every word on screen stays readable: typed labels, leaders and handwriting finish ≥ 1.5 s before the cut and sit
  ≥ 90% inside the camera's view. Type labels early; put them in the area the camera keeps (`kit.view_box(keys)`).
- No shot under 1.2 s unless it's a deliberate montage. No more than ~6 s on one picture unless something new
  happens on it; the visual mode changes every 20–30 s.
- Comic panels hold ≥ 1.8 s; footnotes stay open ≥ typing time + 3 s.

## Placement lessons (from the Chadwick example)
- Lamp finders can catch faces (egg heads are warm and bright): check `fx2.lamps` and pass a small `n=`.
- Falling particles over faces: `Leaves(avoid=img, y_max=)`; keep falling layers above head height in crowds.
- Footnote cards, stamps, counters, drawings and leader dots never land on a face, a label or the subject: choose
  `side=`/`pos=` per shot from the stills sheet.
- Lifted objects: `fill_from=(dx, dy)` clones the same fabric/pavement (inpainting smears); include the object's
  painted reflection in the lift.
- Wiping writing: `fx2.clean_text` keeps the paper texture.
- Maps: widen the box until every lake/coast the story touches is whole.
- Dramatised details creep into scripts: check every line against OUTLINE.md before recording.
- Comic page's last panel: end with the camera on the whole page; hold each panel ≥ 1.8 s.
- Films without their own board use `assets/footnote/board.png` (copy to `build/edit/B09_board.png`).

## Sound (felt, never competing with the voice)
- Effects are **synthesised in code** (no library = no copyright): fire, insects, rain, thunder, wind, distant guns,
  engine, crowd, shutter, knock, thud, stamp, bolt, static, morse, type, whoosh, hum, door, clink, paper, rip, rotor,
  train. Few, chosen moments, in gaps between phrases.
- **The right sound for the place**: filtered noise only for real noise (rain, surf, wind, fire, static). People →
  walla; vehicles and animals → CC0 recordings (after the user's OK, credited); **≤ 3 whooshes in a whole film**.
- **Pencil/chalk/brush sound is subtle**: −27 dB under the voice, a further −7 dB while the narrator talks.
- **The narrator always leads**: score −25 dB under the voice, −9 dB more while talking (`MUSIC_DB`, `DUCK_DB`).
  Never raise them. AAC overshoots sharp clicks: `final.py` limits spikes before loudnorm; measure the MP4's peak.

## Content rules
- No extremist insignia, no gore, nobody shot on camera (cut on the sound, smoke, silhouettes, aftermath); keep the
  victims' side honest.
- No readable text in generated images (the engine writes all words live). Real photos only public domain / CC,
  credited.

## Worked example
`examples/chadwick/` (copy it into a project with `PY scripts/new_project.py chadwick --example chadwick`):
`tools/chad.py` (LIVE table for 120 pictures, map settings, credits), `shots_b1…b9.py` (two comic pages, the living
map, the con drawn on the envelope, rolling counters, the shatter, the tear, the lifted note, footnotes, photos, a
halftone newspaper), `test_shots.py` (the 70-second effects test, its narration in `TEST_SCRIPT.md`), `voice.py`
(batches, GAPS, SPEEDS), `music.py` (+ `audio/music/*.prompt.txt`), `final.py`, `walla.py`, `script_check.py`,
`SCRIPT.md`, `IMAGE_GUIDE.md`, `OUTLINE.md`, `incoming/` (every image), `voice/` and `audio/` (so it re-renders without
an API key), `research/` and `incoming/05_photos/` (the real archive sources, with `CREDITS.md`), `look/` (one still
of each technique), `video/chadwick_effects_test.mp4`.

## References
- `references/install.md` — macOS/Windows/Linux setup, Claude Code, updating.
- `references/image-guide.md` — the guide template: opener, character blocks, coverage, face prompt, bases, sheets,
  line versions, save folders, the API prompt file, resume-in-a-new-chat.
- `references/image-generation.md` — ChatGPT, Codex, Google Flow/Whisk, Gemini API (`imagegen.py`), Midjourney and
  others; saving and naming (`sort_images.py`); checking.
- `references/consistency.md` — style card, cast sheets, EDITs, places, drift fixes.
- `references/art-styles.md` — the suggested look and how to use another.
- `references/voice.md` — Gemini TTS, importing your own voice, Whisper.
- `references/music.md`, `references/dubs.md`, `references/thumbnails.md`, `references/cta.md`.
- `references/engine.md` — film.py / seq.py / fx2.py / kit.py API with examples, batch anatomy.
- `references/final-render.md` — stills, previews, parallel renders, the final join, checks.
- `references/performance.md` — slow PCs, Windows speedups, disk and memory.
- `references/troubleshooting.md`, `references/checklist.md`, `references/story-finding.md`, `references/hooks.md`.

## Scripts
- `scripts/new_project.py <story> [--example chadwick] [--update-engine]` — make or refresh a project.
- `scripts/doctor.py` — check the install and get speed advice.
- `scripts/sort_images.py <downloads> <project> --group 02_scenes` — name manually downloaded images.
- `scripts/image_contact.py out.png NAME …` — gridded contact sheet (run inside an incoming folder).
- `scripts/video_stills.py video.mp4 out.png t1 t2 …` — stills of a finished video at given times.
