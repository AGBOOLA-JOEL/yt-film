# Keeping ~150 images consistent (style, characters, places)

A film falls apart when the hero's coat changes colour between shots or the painting style drifts halfway. These
rules hold the set together on any image tool.

## 1. Lock the style first: the style card
- One image that shows the whole look: a street, an interior, two or three people, the palette, the line and paint.
- Make it first, choose it carefully (redo it 3–5 times if needed), then **attach it to every single later prompt**.
- Start each new film by attaching the previous film's card, so a channel keeps one look.

## 2. Lock every person: cast sheets
- One sheet per character (and per age or big costume change): front, three-quarter, side, back, and four head
  close-ups. Plain background, even light.
- After the sheets exist, **rewrite the character blocks to match what was actually drawn** (the hat it gave, the
  hair, the coat buttons). A prompt that fights the sheet makes the model drift.
- Copy the block word for word into every prompt that person appears in; attach their sheet; name them in CAPITALS.
- Related people: attach one person's sheet when making another's (sisters, a person at two ages) so they share
  features.

## 3. One chat / one session per film
Consistency comes from context. In ChatGPT keep the whole film in **one chat**; in Flow/Whisk keep the same project
with the same ingredients; on the API, the references are attached on every call (that's what `refs` does).
When a chat must be replaced, the resume guide re-attaches the style card, the needed sheets and two finished scenes.

## 4. EDIT instead of re-prompting
Face close-ups, the same room at another moment, a before/after: make them as **EDITs of the picture just made**
("change only what I ask; keep the same camera, framing, light and every object in place"). Half of a film's images
are EDITs; they are the cheapest consistency there is.

## 5. Places are characters too
For a set used many times (the house, the bank, the courtroom), make one wide first and attach it to every later shot
in that place. Real places: attach a public-domain archive photo as a reference for the building only.

## 6. The opener's hard rules
Every image: same world and light rules, no readable text, no logos, nothing glossy or 3D, subjects in the central 70%
of the frame, some calm areas for drawings, sharp focus (no depth-of-field: the engine moves the camera).
If something keeps appearing that you don't want, add it to the NEVER line of the opener.

## 7. Check by groups, fix early
After each group, look at a contact sheet next to the style card and the cast sheets. Redo drifted images straight
away; a drift copied into ten later EDITs costs ten redos.

## Drift fixes that work
- *"Match the attached style card exactly: the same ink line weight, the same matte gouache, the same muted palette."*
- *"ANNA exactly as on the attached character sheet: the same green coat with six buttons, the same hat."*
- *"Fewer details, larger shapes, calmer background, as in the attached scene."*
- Faces animated by the engine need **two clearly visible eyes and the mouth line**: *"both eyes and the mouth line
  clearly visible, not covered by hair, hats or hands."*
