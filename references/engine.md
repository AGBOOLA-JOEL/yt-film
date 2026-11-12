# The film engine (`<project>/tools/`)

**Current way (Carnegie's Daughter): `seq.py` + `fx2.py`.** A film module `tools/<story>.py` does `from seq import *`,
fills `LIVE` (per picture: `lambda t0, t1: ([src effects], [screen fx], [post effects])`), `CREDIT`, and
`set_map(...)`; each `shots_bN.py`:
```python
from chad import *                      # the film module
b = Batch("b6"); S = Seq(b)             # S.at(time | "phrase", builder); S.end() places them (each runs to the next)
S.at(0.0, scene("S08a_bank", "in", label="The Wade Park Bank, Cleveland", label_at=0.2))
S.at(4.4, scene("S08b_office", zoom=((887, 443, 887), (1100, 400, 760)), marks=m))            # living layers come from LIVE
S.at(23.4, scene("S07g_housekeeper_face", "face", act=dict(glances=[(25.0, 27.0, -8, 0)])))  # faces only when asked
S.at(45.4, page("B05_envelope", [Draw("X06_envelope", 1, (870, 400), 300, (51.6, 52.8), (52.8, 53.3))], marks=m))
S.at(35.6, drawin("S05g_euclid", zoom=..., ink=(0.0, 1.6), flood=(1.3, 2.6), label="Euclid Avenue, Cleveland"))
S.at(77.0, map_shot((77.0, 77.6), towns=[("Woodstock", 77.1)], route=["Woodstock", "Cleveland"], t_route=(77.5, 78.6), fast=True))
S.at(22.2, custom(lambda b, t0, t1: ...))   # anything hand-made: a comic page, a newspaper Page with halftone
wr.footnote(b, 40.6, 48.6, 1, "Title", ["line", "line", "line"], side="left" | pos=(x, y))
photo(b, "carnegie_1905.jpg", 47.6, 50.6, pos=(0.26, 0.45), credit=CREDIT[...])
S.end()
```
`scene(...)` options: `zoom=((cx, cy, h), (cx, cy, h))` or a move name, `act=`, `label=`/`corner=`/`label_at=`,
`draws=[Draw]` (made live with pen sprite and sound), `extra=[fx2 effects]`, `marks=`, `post=[stamps, counters]`,
`fx=[("snow", a), ("fade_out", t0, t1), ("flash", [(t, (x, y))])]`, `trans=("dissolve"|"whip"|"flash"|"shatter", s, ...)`,
`shake=[(t, amp)]`, `live=False` (no LIVE layers). Check: `python tools/stills.py bN 24 t1 t2 ...`.

**fx2 (effects that add, never bend):** `Smoke(origin, rate, life, rise, wind, size, color, light, alpha)`,
`Breath(origin, [times], direction)`, `Flame(p, h, light=dict(amount=))`, `Light(p, radius, amount, flicker)`,
`lamps(img, n, amount)` (the picture's own lamps), `Lift(img, poly, keys=[(t, x, y, angle, scale)], flutter=,
shadow=, fill_from=(dx, dy))`, `Draw(sheet, panel, at, height, t_ink, t_col, card=, clip=, t_out=)`, `Tear(img, t0, x)`,
`Counter([(t, value)], pos, label, size)` (post), `Leaves(t0, t1, n, avoid=img, y_max=)` (post), `Sparkle(points)`,
`MapLayer` / `Traveller` (inside `map_shot`), `clean_text(img, polys)`, `Live(img, [effects])`, `u8(*effects)` (for
faces), transition `("shatter", secs, (cx, cy))`. Smoke presets in seq: `coal(p)`, `steam(p)`, `wisp(p)`.

The older way below (kit.cut, sheets, Flow) still runs, but new films use the above.

`scripts/new_project.py <story>` copies the engine to `<workspace>/<story>/tools/`; then change: `voice.py` (STYLE,
BATCHES, GAPS), `music.py` (CUES), `final.py` (BATCHES ending in `"cta"`, MUSIC), make the ending with `cta.py`
(see cta.md), and write new `shots_bN.py`. `Page.seal` needs `text=` (a name for the red seal).
Full worked shot lists: `examples/chadwick/tools/shots_b1…b9.py`. Images are 1774 x 887 (2:1);
all coordinates are **source px** of that image.

## Batch anatomy (`shots_bN.py`)
```python
from film import Batch, Marks, Page
from kit import cut, label, sheet, ...
b = Batch("b3")                 # reads voice/b3_vo.wav + voice/b3_words.json
b.music = ("m_rise", 0.0)     # preview-only music; final.py does the real score
T = b.t                         # T("phrase") = start time of the next match (cursor moves forward)
t_oct, t_found = T("In October"), T("the letter came")      # list cues in narration order
END = b.end
cut(b, t_oct, t_found, "S15a_letter", "in", text=("October 1945", t_oct + 0.3, "tl"))
...
b.fx("night", t_said, t_near, db=-6)
if __name__ == "__main__":
    b.render()
```
Write Whisper's spelling of names in cues (it often mishears names): print the batch's words
first (`voice/bN_words.json`).

## Shots
- `kit.cut(b, t0, t1, img, move, text=(words, t, corner), fx=[...], shake=[(t, amp)])` — one image; moves:
  `in out right left up down face still` or `((cx, cy, h), (cx, cy, h))`. `text` = typewriter label kept inside view.
- `b.scene(t0, img, [(t, cx, cy, h), ...], marks=m, fx=[...], ease="lin"|"io", swap=(t, img2))` — custom keys.
- `b.drawin(t0, img, keys, ink="<img>_lines", flood=True, ink_t=(a, b), flood_t=(a, b))` — ink draws, paint floods.
- `kit.sheet(b, "X04_survival", t0, t1, [(panel, t), ...], done=(panels already drawn,))` — a sketch sheet drawing
  itself; the camera visits each drawing.
- `b.page(t0, page, keys, drift=0.4, shake=[...], marks=m)` — a blank base drawn on live (see Pages).

## Marks (on any shot; colours "auto" pick cream/ink with halos by what's underneath)
- `m.typed(text, xy, size, t0)` — level typewriter label (dates, places, names). Typing sound is added automatically.
- `kit.label(text, t, keys=…, corner="tl"|"tr"|"bl"|"br")` — same, placed inside the area that stays in view.
- `m.write(text, a, b, t0, dur, size=None, typed=False)` — words **on a line of the picture**: baseline from a to b
  at its angle (measure the rule/row on a gridded crop of the image). `kit.rows(start, step, n, length, deg)` gives
  parallel baselines on a tilted page. `kit.cleaned(img, [polygon])` wipes illegible printing there first and
  returns the new image name.
- `m.stroke(pts, t0, dur)`, `m.circle(c, rx, ry, t0, dur)`, `m.arrow(a, b, t0, dur)`, `m.scribble(c, r, t0, dur)`.
- Don't pass `color="ink"` over a picture unless you've checked it's light there.

## Pages (blank bases: `Page(base, medium)`)
Media: `graphite` (pencil on paper), `chalk`, `sumi` (brush ink), `carve` (pale cuts in bamboo/wood).
Dark-ink writing over a dark part of the base gets a paper glow automatically.
- `pg.stroke(pts, t0, dur, width, wob, accent=False)`, `pg.strokes(paths, t0, t1, ...)` (time shared by length),
  `pg.text(s, xy, size, t0, dur)` (level), `pg.seal(center, size, t, text=…)` (red hanko).
- `pg.lift(src, panel|box, center, height, t0, t1, rot, thicken, keep, soft, clip, fade, fill, sweep)` — redraw a
  sheet drawing (panel index) or a box of any `_lines` image on the page, in its stroke order. `clip` polygon keeps
  just the subject; `fade` trails the edges off; `thicken`/`keep` for chalk/brush; `sweep` paints in one brush pass;
  `fill` lightens a chalk face.
- Maps: `island_map(pg, lon, lat, rect, t_coast, t_contour, levels, sea=(t0, t1))` → `(P, field, mask)` then
  `river(field, mask, start)`, `hatch_slopes(field, mask)`; `kit.coast_map(pg, lon, lat, rect, t0, t1)` → `P`.
  Routes: `kit.arc`, `kit.dashes`, `kit.arrowhead`, `kit.ring`. Figures: `kit.egg_figure(c, s, lying, rifle)`,
  `kit.cross`, `lean_to`, `palm`, `ridge_sketch`. `kit.ink_tally(pg, x, y, t0, t1, n)` (accelerating years).
  `kit.halftone(pg, photo, box, t0, t1)` prints a photo into a newspaper box.

## Picture effects (`fx=[...]` on a shot, positions in source px)
`("fire", p, radius, amount)`, `("embers", p)`, `("rain", amount)`, `("lightning", [t, …])`,
`("fireflies", (x0, y0, x1, y1))`, `("snow", amount)`, `("glass", t, p)`, `("flash", [(t, p), …])`,
`("steam", t0, t1, p)`, `("crt", (x0, y0, x1, y1))`, `("alarm", t0, t1, p)`, `("fade_in", secs)`,
`("fade_out", t0, t1)`; camera `shake=[(t, amp)]`.

## Sounds (`b.fx(kind, t0, t1=None, db=0)`)
fire, night, rain, thunder, wind, guns, engine (`away=True`), crowd, shutter, knock, thud, stamp, bolt, static, morse,
type, whoosh, hum, door, ring, alarm, smash. Levels are relative to the voice; most beds sit at −6…−14 dB.

## Workflow per batch
1. Print the batch's word timings; make a gridded contact sheet of its images (to place labels, fire points, lines).
2. Write `shots_bN.py`; `python tools/shots_bN.py --preview` (half size, 12 fps).
3. Pull stills at key times into one contact sheet (`scripts/video_stills.py`) and look: placement, contrast, timing, nothing cut off.
4. Fix, then (only when the user asks for renders) full render, all batches in parallel, sized to the machine:
   `python tools/render_all.py` (or `render_all.py b3 b7`, `--changed`, `--jobs 2`), then `python tools/final.py`.
5. `final.py` writes `renders/<story>_final.mp4`; verify `ffprobe` (1920x1080, 24 fps), `ebur128` on the **MP4**
   (≈ −14 LUFS, peak ≤ −1.5 dB), and stills; then `tools/dub.py` for the dubs (dubs.md).


## Signature animation (`signature.py` as `sg`, `wr.py`)
```python
import signature as sg
from wr import sc, footnote
sc(b, t0, t1, "S05c_bar", "in", src=fx2.u8(Smoke(...)), faces=False)          # living still (fx2 layers)
sc(b, t0, t1, "S06c_teller_face", "face", act=dict(widen=[(t, t2, 0.2)], mouth_fx=[(t, t2, "open", 0.3)]))
card = footnote(b, t_in, t_out, 2, "Title", ["One source only: ...", "Sources: pinned comment."], pos=(0.23, 0.7))
sc(b, t0, t1, "S06i_face", "face", post=[card])     # pass the same card to every shot it spans
comic = sg.Comic("B09_board", [dict(box=(60, 50, 1010, 430), img="S05f_counter", focus=(887, 420, 700), t=(a, b, c)), ...],
                 border_t=(t0, t1))
b.custom(t0, comic, cam_keys, "B09_board", marks=m)          # then a scene of the last panel with trans=("dissolve", .3)
```
- `sc(b, t0, t1, img, move, act=, live=, src=, post=, marks=, fx=, trans=, text=, faces=True)`: one scene; every egg
  face acts. `src=` 2x-source effects (Face, Flow, Inset, Rings, Pin), `post=` frame effects (Stamp, Tag, Rays, Haze,
  Flip, Hand, NoteCard, Sprite, dim).
- `sg.find_faces(img)` → eyes, mouth, head boxes (check on a contact sheet once per film if a face matters).
- Transitions: `trans=("dissolve", s)` / `("whip", s, 1)` / `("flash", s)` on the incoming shot. Motion blur and the
  film finish (grade, grain, vignette) are automatic; `raw=True` on a shot skips the finish.
- Check before rendering: `b.still(t)` returns one finished frame; `python tools/stills.py bN` pulls 24 evenly
  spaced stills of a batch into one sheet in ~30 s, far faster than a preview render.
- Render cost: ~15–25 min per 90 s batch at 1080p on a fast Mac; 2–4x that on a slow PC (performance.md).

## Readability check (run before every render)
`b.check()` lists words out of frame or cut before they can be read, shots under 1.2 s, comic panels held < 1.8 s,
footnote cards closing too soon. `b.render()` runs it and stops on word/footnote/comic problems (`--force` to
override). `b.overlay(f, t0, t1)` puts a frame effect over whatever shot is playing (footnote cards use it).
