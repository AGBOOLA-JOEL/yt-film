# Formats: not only documentaries

The engine doesn't care what the film is about. Anything narrated over still pictures that come alive (drawings
inking in, numbers typing, maps, stamps, acting faces) works. Pick a format with the user before the spine; it
decides the spine's shape, the hook, the mix of images, and which engine features carry the film.

Start a project in a format (writes a spine template into OUTLINE.md):
```bash
python scripts/new_project.py my_film --format explainer --look clean
```
Formats: `story` (default), `explainer`, `countdown`, `rise-fall`, `storytime`, `kids`, `summary`, `case-study`,
`news`. The rules in `references/storytelling.md` still apply to all of them (a spine joined by but/therefore,
continuous batches, few spoken dates, show then draw); what changes is the shape.

## The formats
### `story`: a true story (the example's format)
- **Spine:** what someone wanted → the decision or wrong act → how it grew → how it broke → the cost and the twist.
- **Hook:** the strangest true moment, the price tag, the document (references/hooks.md).
- **Images:** ~100 scenes with coverage of the key moments, cast sheets, sketch sheets for the mechanism.
- **Carries it:** acting faces, lifts, comic pages, the living map, footnotes, real archive photos.

### `explainer`: how something works, or why something is the way it is
- **Spine:** the puzzling fact → the naive answer, BUT it fails → the real mechanism, step by step, each step
  THEREFORE the next → what it means for the viewer.
- **Hook:** a question the viewer has asked themselves ("Why is the sky dark at night if there are infinite
  stars?"), or a startling everyday object in your hand.
- **Images:** fewer scenes (~40), many more **bases and sketch sheets** (~20 sheets, ~15 bases), a few
  diagrams-to-be (blank charts, cut-away objects without labels). Characters optional (references/art-styles.md).
- **Carries it:** drawings made live on pages, counters, arrows and labels, the map, `_lines` scenes drawing in.
- **Mark `[DRIVE]`** on the passage where the real mechanism first appears; it should come by ~25%.

### `countdown`: a ranked list ("7 heists that went wrong")
- **Spine:** the promise of the list → each entry is a mini-story with its own hook, turn and payoff → number 1 is
  the strongest and pays off the title. Order entries by rising strength; link them ("If that sounds bold, number
  four didn't even need a gun.").
- **Hook:** a flash of number 1 (without the answer), or the most surprising single fact from the list.
- **Images:** 8–15 per entry; one "title card" base reused for every number (the number types on it).
- **Carries it:** stamps and counters for the numbers, typed tags, quick comic pages for action entries.
- **Batches:** one entry per batch fits well; the seams between entries are the act breaks, so a short fade or a
  card is fine there (`b.act_break = True`).

### `rise-fall`: the life of a company, a product, a city, an idea
- **Spine:** the problem it solved → the breakthrough → the boom (with numbers) → the mistake or the rival → the
  fall → what's left today.
- **Hook:** what it was at its peak against what it is now (two pictures), or the moment it started to fall.
- **Images:** places and objects over decades; a growth chart base; product close-ups (no logos: draw them live as
  simple marks, or leave them generic).
- **Carries it:** rolling counters, a chart drawn live, the map, era changes shown with a place/date tag.

### `storytime`: a personal or fictional story told by one voice
- **Spine:** the setup in one breath → what went wrong → it got worse → the moment → what changed. First person
  is fine.
- **Hook:** the funniest or most alarming line of the story, said straight.
- **Images:** a recurring cast (2–4 people) with plenty of face close-ups; few explanations.
- **Carries it:** acting faces (talk, glance, widen), comic pages, quick reaction shots, typed thoughts.

### `kids`: fables, bedtime stories, gentle facts for children
- **Spine:** a small hero wants something → tries → it goes wrong → helps or is helped → learns one thing.
- **Look:** `storybook` (or `comic`); slower narration; no frightening detail; one clear moral at the end.
- **Images:** soft scenes, animal or round-head characters, big simple shapes; fewer cuts, more drawn things.
- **Carries it:** drawings appearing, gentle living layers (leaves, snow, stars), acting faces.

### `summary`: a book, a theory or an idea in 10–15 minutes
- **Spine:** the big claim → why it's surprising → the 3–5 ideas that support it, each with one concrete example
  story → the strongest objection → what to take away.
- **Images:** one illustrated example per idea, plus a "notebook" base the ideas are written and drawn into.
- **Carries it:** handwriting and drawings on the notebook, typed key phrases, simple diagrams.

### `case-study`: a business, money or legal case
- **Spine:** the result (a fortune made or lost) → the situation → the clever or reckless move → the numbers as it
  played out → the reckoning → the lesson.
- **Hook:** the number (number punch or price tag).
- **Images:** offices, documents, ledgers, charts as blank bases.
- **Carries it:** counters, stamps, documents typing, the chart drawn live, footnotes for sources.

### `news`: what happened and why it matters
- **Spine:** what happened (one picture, one sentence) → the background you need, only that → the key players and
  what each wants → what happens next.
- Keep facts sourced and dated; this is the one format where a few more dates are fine (always on tags).
- **Images:** quick turnaround: fewer scenes, more maps, documents and drawn diagrams.

## Shapes outside these
Anything else (a travel film, a recipe history, a sports legend, a mystery) fits one of these shapes, or a mix:
write the spine first, mark the `[DRIVE]`, and choose the image mix from what the narration will *explain* (drawn
on bases and sheets) against what it will *show* (scenes).

## What stays the same in every format
- The narration decides the shots: show a picture for 3–5 s, then draw while the narrator explains.
- Batches are continuous; fades only at real breaks.
- Every picture made is used; no readable text in images; words are typed or written live.
- The format is not a template: vary the hook from film to film (references/hooks.md).

The engine renders 1920x1080 (16:9). Vertical Shorts aren't built in; cut a 9:16 crop from a finished batch in an
editor if you need one.
