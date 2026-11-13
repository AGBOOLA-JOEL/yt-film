# The image guide (the film's storyboard)

The user generates every image (ChatGPT, Codex, Flow, the Gemini API or another tool: see image-generation.md and ask
which route they use); Claude writes the guide and picks the files up. The guide is the storyboard: write it before
the script, and write the script from it. The art style below (egg-headed people, ink and matte pastel gouache) is the
suggested default; for another style, adapt the opener and keep the engine's needs (art-styles.md).

**Reference guide: `examples/chadwick/IMAGE_GUIDE.md`** (164 images). Lessons from it:
- ChatGPT ignores "leave calm areas": its scenes come back dense. Ask for them anyway, and plan to draw on the
  explainer card (B02) or a base when a picture has no room; drawings on a busy scene need `card=True`.
- Ask for at least one big blank **explainer card** (B02) and an envelope/document base that the story's mechanism can
  be drawn on; they carried most of Chadwick's illustration.
- Sheets: four drawings each, but each drawing is used alone; write the guide knowing which narration line names
  each drawing (the script check fails if one is unused).
- Images arrive ~16:9 (1670x942) and are cropped to 2:1 by the engine: keep heads and key objects off the very top and
  bottom edges.

## Structure of the guide
1. Title, the look in one paragraph, **the spine** (the question and the but/therefore beats, from
   `references/storytelling.md`). The rest of the guide follows the spine in order: one heading per beat.
2. **Count table** and status (style cards, cast, scenes, line versions, bases, sheets, sheet lines).
3. **Where to save**: `<project>/incoming/` with `00_style/ 01_cast/ 02_scenes/ 03_sheets/ 04_bases/`, exact
   filenames, "original PNG, not a screenshot", the full path for Codex if it saves the files.
4. **How to work** (written for their route): landscape always; in ChatGPT the user works in **one chat** (paste the opener once, then the prompts in order); attach the style
   card + cast sheets of everyone in the image; EDIT rules; drift fix; hands check; refusal → `(skipped X)` in name.
5. Chat opener, face prompt, character blocks.
6. Steps: style cards → cast sheets → scenes (by chat) → scene line versions → sketch sheets (+ line versions) → bases.
7. What Claude draws live (maps, counters, timelines, all words) so no images are wasted on them.
8. Facts still to check before the script.

## Chat opener (adapt WORLD to the story's places and years)
```
Every image from here on follows these rules.
WORLD: grounded editorial illustration of the real world: confident ink line with matte gouache colour, like a hand-painted graphic novel. Everything is era-accurate to [PLACES, YEARS]: real architecture, period vehicles, [STORY-SPECIFIC PROPS]. Believable materials and everyday wear: [WEAR]. Natural, unglamorous light. Muted real-world colour: [PALETTE]. The setting tells the story: it is always clear where and when we are.
PEOPLE: every person is the same stylised figure, matching the attached character sheets: an egg-shaped head, wider at the bottom, no chin, plain cream-white skin with soft grey shading on one side; two small solid dark oval eyes set wide apart; one thin line for the mouth (expressions come from the mouth line, head tilt and body pose); the two eyes and the mouth line are always clearly visible, never covered by hair, hats or hands (they are animated); no nose, no ears, no eyebrows. Hair, hats, moustaches and glasses sit on the egg head as simple shapes. Slim body, simple rounded hands. Every person has exactly two arms and two hands. People differ by hair, hats, clothes, build and accessories, never by face. They are painted with the same gouache and the same light as the world, standing in it with proper shadows and contact, never pasted on.
NEVER: [STORY-SPECIFIC BANS e.g. extremist insignia], blood, wounds, gore, anyone being shot on camera, shiny or glossy rendering, glow, bloom, lens flare, HDR, neon, orange-and-teal movie grading, god rays, airbrushing, 3D-render or plastic look, realistic human faces, flat vector style, anime, readable text or letters anywhere (signs, papers, leaflets and screens stay blank or illegible), logos, watermarks, borders.
FOR ANIMATION: everything in sharp focus (no depth-of-field blur, no motion blur); smoke, steam, snow, rain and water are painted as soft separate shapes that don't cross anyone's face; the main subject inside the central 70% of the frame, nobody cut off by the edges, and some calm areas (sky, wall, floor, ground) left for notes I will draw on later. Landscape format.
When I say EDIT: change only what I ask; keep the same camera, framing, light and every object in place.
```
Style card: the first film describes the style in words (and any example images the user likes); later films attach
the previous film's `style_card.png` so the look carries over. Offer an EDIT variant if the first one is off; the user
picks → `00_style/style_card.png`.

## Cast sheets
```
A character sheet on a plain light-grey background, same style as the attached card: [CHARACTER BLOCK]. Show: full body front, three-quarter and side views, a back view, and a row of four head close-ups (neutral, determined, worried, shocked). Exactly two arms and two hands in every view. Even studio light, no scenery, no text.
```
Character blocks are copied word for word into every prompt. One sheet per age/look of a person (young, worn, old).
After the sheets exist, **rewrite the blocks to match what ChatGPT actually drew** (hats, hair, straps), so later
prompts don't fight the sheets. Real photos (public domain) can be attached for clothes and build only.

## The guide follows the narration (show, then draw)
The way the film is narrated decides the shots (`references/storytelling.md`, section 6): each beat **shows** a
moment for 3–5 s in a painted picture, then **draws** while the narrator explains. So the guide plans both, beat by
beat, and every image row says which line of narration it serves and what will be drawn on or after it:

```
### Beat 5 · One bond, three loans  (BUT there were no real profits, SO he pledged one bond three times)
| # | file | shot | shows (the narration line) | then drawn |
| 61 | S05d_vault.png | M | "Ward had one bond." | the bond lifts off the shelf |
| 62 | B02_bond.png (base) | – | "...borrowed against it, three times" | three banks, arrows, $ typed |
| 63 | S05e_ward_face.png | F | "Nobody compared notes." | – |
```

Budget the images by the spine, not by the person's life:
- **The rise, the turn and the fall get the coverage** (3–7 shots per big moment). Backstory gets 1–2 shots per
  person, and only for the trait that drives the story. No sequences for childhood, schooling or other careers.
- **Every explanation beat gets drawing material**, not more scenes: a sketch-sheet panel, a blank base, or a
  scene with a `_lines` version. Plan **12 sketch sheets** (+ line versions), **~10 bases** and **6 scenes that
  draw themselves**; about **100 scene shots** (≈150 images in all, as before, but more of them drawn).
- **A time or place change gets one establishing W shot** carrying the place/date tag, instead of the narrator
  saying the date.
- **Seams:** for each planned act break (2–3 per film) plan a strong closing image and a strong opening image; other
  batch boundaries need nothing special (the story continues across them).

## Shot coverage
A new picture **or a new drawing** every ~4–6 s. Give each big moment 3–7 shots, smaller ones 1–2:
- **W** wide: where we are · **M** medium: people doing something · **F** face: EDIT pushed in, one expression ·
  **D** detail: hands or an object · **P** point of view: what someone sees.
- Filenames: beat number + shot letter (`S03c_rifle.png`), so a moment's shots stay together.
- About half are EDITs (faces, repeat visits to a set): quick in ChatGPT, made right after the image they edit.

Face prompt:
```
EDIT: the same moment, with the camera pushed in close on [NAME]: head and shoulders fill the middle of the frame, the same light, the same background now further behind. Expression: [EXPRESSION]. Keep the hat, hair and clothes exactly as on the attached character sheet. If a hand is visible, it is one of exactly two.
```
Write expressions as mouth line + head tilt + shoulders ("mouth a flat hard line, head lowered, shoulders squared").

## Scenes that draw themselves (6 per film)
```
EDIT: the exact same picture as an illustrator's pen-and-ink drawing: remove all colour and painted shading, keep only black ink outlines and ink hatching on pure white paper. Same composition, nothing moved.
```
Save as `<scene>_lines.png`. Pick big moments (arrival, the climax, the ending).

## Sketch sheets (12 per film, 4 drawings each, one per explanation beat or two)
```
A page from an illustrator's sketchbook: four separate drawings in confident pen-and-ink with fine hatching and a watercolour wash, on pure white paper, arranged left to right with clear white space between them (I will link them later). Neat, accurate drawings of real places and objects, not icons and not cartoons; the people are the egg-headed figures from the attached sheets, drawn in ink. No text, letters, numbers, arrows, frames, boxes, flags or insignia. Landscape.
```
then "1) … 2) … 3) … 4) …". After the first sheet, attach it to every later one. Line version right after each:
```
EDIT: the exact same page and drawings, with all colour and all painted shading removed: only the black ink lines and ink hatching remain, on pure white paper. Same drawings, same positions and sizes, nothing redrawn or moved.
```
Sheet drawings double as **lift sources**: the engine redraws any single drawing on a blank base.

## Bases (blank story objects, ~10)
Real objects the story would have, **kept empty** (no map shapes, marks or writing): a field notebook of squared
paper, an old military map sheet, a blackboard, a sheet of washi with ink stone and brush, a bamboo trunk, a
newspaper page with an empty headline/photo box, an old globe turned to the region. Claude draws on them live.

**Comic-page groups** (two per film): mark the group "plays as a comic page" and keep each subject in the centre
third so it survives a panel crop. **The footnote art is already made**: the gloved hand, the tea-stained note (B10)
and the cream board (B09) are in `assets/footnote/`; don't ask for them again unless the user wants their own
(then save as `01_cast/hand.png`, `04_bases/B10_note.png`, `build/edit/B09_board.png`).
Plan the footnotes (4–6) when writing the guide: the one-source facts the script will word as "reportedly".

## API route (IMAGE_PROMPTS.jsonl)
When the user picks the Gemini API (`tools/imagegen.py`), also write `IMAGE_PROMPTS.jsonl`: a first line
`{"style": "<the opener>"}`, then one line per image in guide order: `{"file": "02_scenes/S01a_x.png", "prompt":
"<character blocks written out + the prompt>", "refs": ["00_style/style_card.png", "01_cast/anna.png"]}`. EDITs put
the edited picture first in `refs`. Character blocks are written out in full (no "[block]").

## Resume in a new chat (when ChatGPT gets stuck)
Paste the opener + "I'm continuing a series… match the attached frames exactly", attach the style card, the cast
sheets still needed and **two finished scenes** from the film; list only what's left, with filenames. Line versions
whose original chat is gone: attach the original image and ask for a trace of it.
