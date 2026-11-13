# Styles: make the films look like your channel, not like the example

A film's look has two layers, and you choose both:

1. **The image style**: what your image tool paints (gouache, watercolour, comic, chalkboard, noir ink, flat
   vector...). It's set by the **opener** at the top of the image guide and by the style card.
2. **The engine look**: what the engine adds on top (the grade, grain and vignette; the colour of drawn lines,
   typed tags and paper scraps; the accent colour for circles and stamps; the fonts; the drawing sound). It's set by
   **`YTF_LOOK`** in the project's `.env`, fine-tuned in **`look.json`**.

Pick a pair below, or mix: the engine look doesn't have to share a name with the image style.

```bash
python scripts/new_project.py my_film --look clean --format explainer   # writes YTF_LOOK and a spine template
python tools/look.py            # list the looks, and see which one this project uses
python tools/look.py noir       # every value of one look
python tools/stills.py b1 8     # see it on real frames (seconds, no render)
```

## The engine looks (`YTF_LOOK`)
| Look | Feels like | Grade and texture | Lines / tags / accent / type |
|---|---|---|---|
| `gouache` (default) | a hand-painted graphic novel | warm print grade, fine grain, soft vignette | brown-black ink, cream paper, red pencil, typewriter |
| `clean` | a modern explainer | neutral, no grain, no vignette | near-black ink, white tags, blue accent, bold sans |
| `noir` | ink wash, crime, cold war | near-monochrome, hard contrast, heavy grain | black ink, grey paper, red accent, monospace |
| `chalk` | a classroom board | soft, faint grain (for dark images) | chalk-white lines, yellow chalk accent, handwriting |
| `comic` | bright comic, ligne claire | rich colour, no grain | black ink, yellow paper, red-orange accent, bold stamp lettering |
| `storybook` | a children's book, soft watercolour | light warm grade, faint grain | blue-grey ink, cream paper, coral accent, handwriting |
| `blueprint` | engineering, how-it-works | cool (for blue technical images) | white lines, blue tags, orange accent, monospace |

Change any single value in `look.json` at the project root; it overrides the preset:
```json
{"accent": [20, 110, 220], "grain": 0, "type_font": "bold", "pen_db": null}
```
Values: `grain`, `vignette`, `warmth` (-1 cool .. 1 warm), `contrast`, `shadow_tint`, `saturation`, `ink`, `light`
(lines on dark areas), `accent`, `paper`, `type_font` / `hand_font` (`type`, `mono`, `bold`, `stamp`, `hand`),
`ruled_tags`, `pen_db` (the drawing sound; `null` = silent). Lines drawn with colour `"auto"` switch between `ink`
and `light` by what's under them, so keep `ink` dark and `light` light in any look.

To use your own font, put the `.ttf` in `fonts/` and add it at the front of that role in `engine/ytf.py` `FONTS`.

## The image style (the opener)
The image guide starts with an **opener** pasted once into the image tool's chat. Three blocks: WORLD (what the
pictures look like), PEOPLE (how characters are drawn), and FOR ANIMATION (what the engine needs; keep it in every
style). Swap WORLD and PEOPLE for your channel; Claude writes them from your description and two or three example
images if you have them.

### WORLD blocks to start from
- **Gouache graphic novel** (the example): *"grounded editorial illustration: confident ink line with matte gouache
  colour, like a hand-painted graphic novel; muted real-world colour; natural, unglamorous light."* Look: `gouache`.
- **Clean flat editorial**: *"clean modern editorial illustration: flat colour shapes with subtle grain textures,
  simple geometric forms, a limited palette of 5–6 colours plus off-white, soft shadows as flat darker shapes, thin
  outlines or none."* Look: `clean`.
- **Noir ink wash**: *"black ink and grey wash on paper, heavy shadows, strong light from one side, rain-wet streets,
  film-noir framing, almost no colour (one muted accent at most)."* Look: `noir`.
- **Chalkboard**: *"white and coloured chalk drawings on a dark green-black school chalkboard, visible chalk texture
  and smudges, simple confident lines, a teacher's diagrams."* Look: `chalk`.
- **Bright comic / ligne claire**: *"clear-line European comic art: uniform black outlines, flat bright colours, no
  hatching, clean readable shapes, cheerful light."* Look: `comic`.
- **Storybook watercolour**: *"soft watercolour and coloured pencil on textured paper, gentle pastel colours, rounded
  friendly shapes, the warm feel of a children's picture book."* Look: `storybook`.
- **Blueprint / technical**: *"technical drawing in white lines on blueprint-blue paper, with exploded views,
  cut-aways and measurement-style lines but no readable text."* Look: `blueprint`.
- Also good: linocut or woodcut print, 1950s travel poster, paper cut-out collage, oil sketch, retro risograph,
  pixel art (big pixels, sharp), anime backgrounds with simple characters.

### PEOPLE: the egg head is optional
The engine's acting faces (blink, glance, smile, talk) need **two clear eyes and a mouth that reads as a line or a
simple shape**, visible and not covered by hair, hats or hands. Any of these work:
- **Egg heads** (the example): an egg-shaped head, two dark oval eyes, one mouth line, no nose or ears.
- **Round-head figures**: a circle head with dot eyes and a line mouth, simple bodies; good with `clean` and `comic`.
- **Simple stylised people**: real proportions, faces as two dots and a line (a very common explainer style).
- **Animal characters**: an animal for each person (a fox banker, an owl judge), with simple eyes and mouth.
- **Silhouettes or faceless figures**: fine; the faces just don't act, the rest of the engine works.
- **No characters at all**: objects, places, maps and diagrams only (science, finance, how-it-works). Leave the
  PEOPLE block out, skip cast sheets, and plan more bases and sketch sheets.

Write the PEOPLE block once, make cast sheets from it, and copy the character blocks word for word into every
prompt. For real people, never ask for a realistic likeness; a stylised look keeps the likeness question away.

### FOR ANIMATION (keep in every style)
*"Everything in sharp focus (no depth-of-field blur, no motion blur); smoke, steam, snow, rain and water painted as
soft separate shapes that don't cross anyone's face; the main subject inside the central 70% of the frame, nobody
cut off by the edges; calm areas left for notes I will draw later; no readable text or letters anywhere. Landscape."*

| The engine does | So the style needs |
|---|---|
| eased camera moves over a still | sharp focus everywhere, no baked-in depth of field or motion blur |
| acting faces | two clear eyes and a simple mouth (or accept that faces don't act) |
| living layers (smoke, flames, light, weather) | painted smoke/steam as soft separate shapes; no strong glow already painted in |
| drawing a scene in (lines, then colour) | a clean line version of a few scenes (`_lines`) |
| drawings made live on pages | sketch sheets with separate drawings + their line versions, in the same style |
| typed labels and writing | **no readable text** in the images; blank signs, papers and screens |
| depth focus and weather | a sense of near and far (very flat styles: skip `focus=`) |
| cropping to 2:1 | key things away from the very top and bottom edges |

**Sketch sheets and line versions follow the style:** in `chalk`, sketches are chalk on the board; in `blueprint`,
white line drawings on blue; in `clean`, simple flat drawings. Change the sketch-sheet prompt's first sentence to
match, and keep "separate drawings with white space between them" and the line-version EDIT.

Photorealistic styles work technically but lose most of the charm (drawings, acting faces) and raise likeness
issues with real people; a stylised look is strongly recommended.

## Make the channel unmistakably yours
Pick the image style, the engine look, a palette and one or two signatures of your own, and keep them for every film:
- **A recurring device:** a host character, a narrator's desk, a pinboard, a notebook every explanation is drawn
  in, a stamp you always close on.
- **Your own footnote art:** replace `assets/footnote/hand.png`, `note.png`, `board.png` with your drawings (same
  names), or don't use footnotes.
- **Your ending** (`references/cta.md`), **your thumbnails** (`references/thumbnails.md`), your music cues.
- **Your format** (`references/formats.md`): a documentary, an explainer, a countdown, a story time.
- Change at least the image style or the look from the example's pair. Two channels with the same opener, the same
  look and the same footnote art look like copies, and YouTube can treat look-alike channels as repetitive.

## Testing a new style before the whole guide
1. Make the style card and two scenes in your image tool with the new opener.
2. Put them in a test project, set `YTF_LOOK`, write a 30-second `TEST_SCRIPT.md` and a one-batch shots file.
3. Run `stills.py` on it and adjust `look.json` until the lines, tags and grade sit right on your pictures.
4. Only then write the full image guide.
