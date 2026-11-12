# Getting ~150 images for a film, with any image tool

Claude writes the **image guide** (image-guide.md): every picture, its exact filename, its folder and its prompt, in
story order. You make the pictures with whatever tool you have; the engine only needs them saved in
`<project>/incoming/<folder>/<exact name>.png` (or `.jpg` / `.webp`). Ask Claude which route fits you, and it
writes the guide in that route's format.

| Route | Effort | Consistency | Cost | Best for |
|---|---|---|---|---|
| **A. ChatGPT, one chat** | manual, ~3–5 h per film | very good (attachments + one long chat) | Plus/Pro plan | most people |
| **B. Codex / an agent that saves files** | semi-automatic | very good | plan | people who already use it |
| **C. Google Flow / Whisk / Gemini app** | manual | good (use "ingredients"/references) | Google AI plan | Google users |
| **D. Gemini API (`tools/imagegen.py`)** | automatic | good | pay per image | hands-off, big batches |
| **E. Midjourney, Leonardo, Ideogram, Firefly, Krea, local SDXL/Flux** | manual | depends on character-reference features | varies | an existing favourite |

Whatever the route, the order is always the same: **style card → cast sheets → scenes (in order, EDITs right after
their original) → line versions → sketch sheets (+ lines) → bases**. Later images need the earlier ones as references.

## Route A · ChatGPT (manual)
1. Open **one** new chat. Paste the guide's **opener** once.
2. For each row: attach what the row says (always the style card, plus the cast sheet of everyone named in CAPITALS,
   plus the image being edited for an EDIT), paste the prompt, generate.
3. **Download the original** (the download button, not a screenshot) and save it with the exact name from the row
   into the folder the guide says. Or download everything to one folder and let `sort_images.py` name them (below).
4. If the chat slows down or starts drifting after ~60–80 images, ask Claude for a **resume guide** (an opener for a
   new chat + the attach list + what's left) and continue in a fresh chat with the same attachments.
- Ask for landscape every time; ChatGPT gives ~16:9 (e.g. 1672x941), which the engine crops to 2:1, so keep heads
  and key objects off the very top and bottom edges.
- Refused prompt? Rephrase the moment (show the aftermath, a silhouette, the object) or save a placeholder named
  `<name> (skipped).png` and tell Claude: it will cover that beat with a drawn page.

## Route B · Codex or another agent
Give it the guide and the **full path** of `incoming/`. It must save each image with the exact filename. Check a
contact sheet after each group: `python scripts/image_contact.py out.png S01a S01b ...` (run inside the folder).

## Route C · Google Flow, Whisk, Gemini app (Nano Banana)
- Upload the **style card and cast sheets as "ingredients" / reference images** and keep them attached for every
  scene; say "in the exact style of the reference" and name the character as on their sheet.
- Use **16:9**. For a face close-up (F) or any EDIT, use the tool's edit/"modify" on the previous picture rather than
  a fresh prompt, so the set, light and clothes stay the same.
- Flow and Whisk download with generated names: download in the guide's order and use `sort_images.py`.
- If faces drift, make the face rows last and attach both the cast sheet and the wide shot of that moment.

## Route D · Gemini API, fully automatic
Ask Claude: **"write IMAGE_PROMPTS.jsonl for the API route"**. It writes one line per image with the prompt and the
reference images to attach (style card, cast sheets, the original for an EDIT). Then:
```bash
python tools/imagegen.py --group 00_style        # make the style card, look at it, redo until you like it
python tools/imagegen.py --group 01_cast         # cast sheets, check each against the style card
python tools/imagegen.py                         # everything else that's missing, in order
python tools/imagegen.py --redo S04c             # one again (the old one is kept as .prev)
```
Model and price: `YTF_IMAGE_MODEL` in `.env` (default `gemini-2.5-flash-image`; check AI Studio for the current
model and its price per image before a 150-image run). Free tiers are rate-limited; the script waits and retries.

## Route E · Midjourney, Leonardo, Ideogram, Firefly, Krea, Stable Diffusion / Flux
- Use the tool's **style reference** with the style card and its **character reference** (Midjourney `--cref`/`--oref`,
  Leonardo Character Reference, Ideogram/Krea references, IP-Adapter or a small LoRA locally) with each cast sheet.
- Aspect `16:9` (Midjourney `--ar 16:9`). Turn "stylize"/"magic prompt" low so the prompt is followed literally.
- Most can't EDIT reliably: for face close-ups, generate a portrait of the character in the same setting and light
  and say so to Claude (it will treat it as a separate shot rather than a push-in of the wide).
- Remove any text the tool adds to signs and papers (or regenerate): the engine writes all words live.

## Saving many images quickly: `sort_images.py`
Generate in the guide's order and let every download land in one folder. Then, for each group:
```bash
python scripts/sort_images.py ~/Downloads <project> --group 02_scenes --since 2h --dry-run   # see the plan
python scripts/sort_images.py ~/Downloads <project> --group 02_scenes --since 2h            # do it
```
It takes the newest images (oldest first) and gives them the group's next missing names from the guide, converts
to PNG, never overwrites, and writes `renders/sorted_02_scenes.jpg`, a labelled contact sheet: look at it and fix any
image that landed on the wrong name. `--from S07a` starts at a name; `--names a b c` for a custom list.
Windows: `python scripts\sort_images.py "$env:USERPROFILE\Downloads" C:/films/my_story --group 01_cast`.

## Checking what arrived (do this per group, before the script)
Hands (extra hands and fingers are common), faces (both eyes and the mouth line visible where the face must act),
era details, readable text (should be none), the shape (nothing important at the very top/bottom), and the cast
matching their sheets. Claude makes contact sheets and lists redos; it also reports what's still missing.
