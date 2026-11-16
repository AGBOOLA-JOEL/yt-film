# Portrait mode: reels on the film engine

The film engine renders portrait (1080 x 1920, 24 fps) as well as landscape. A reel is an ordinary batch: the same
`Batch`, shots, camera keys, marks drawn on the picture, sketch sheets, pages, weather, light, transitions and sound.
So a reel gets the full explainer, not only stills with captions. `engine/reel.py` adds what a phone film needs:
captions, an episode badge, a headline, and character or prop cards.

## Turning it on

Any one of:

- `python tools/shots_ep1.py --portrait` (add `--preview` for a quick 540 x 960, 12 fps pass);
- `YTF_FORMAT=portrait` in the environment;
- a file named `format` in the project folder containing the word `portrait` (best for a reel-only project).

`film.PORTRAIT` is then true, `film.OW, film.OH` are 1080, 1920, `film.AR` is the frame shape and `film.S` is the
screen unit (1.0 at full size in both formats; use it for any size given in screen pixels). Landscape renders are
unchanged, frame for frame.

One episode is one batch: `voice/<ep>_words.json` and `voice/<ep>_vo.wav`, a shot file, `b.render()`. The batch
render is already mixed (voice, ducked score, effects) and levelled to about -14 LUFS, so a reel does not go through
`final.py`. Check each export with `scripts/check_reels.py`.

## Framing pictures

Coordinates stay in source px on the 1774 x 887 canvas, exactly as in landscape, so marks and camera keys written
for a landscape film still point at the same things.

- **Reframe a wide picture by subject.** A camera key `(t, cx, cy, h)` with `h` up to 887 fills the phone screen
  with a slice of the picture 0.5625 x h wide. Push in on a face, pan across a table, cut between two halves of
  one scene. Check the start, middle and end of each move with `b.still(t)`.
- **Show a wide picture whole, in a window.** Give `h` larger than 887 (up to 3154, the whole width). The picture
  then sits in a framed window with a soft dark copy of itself above and below, as the Caesar reels do for wide
  shots and geography. `cy` slides the window up or down; `film.full(name)` returns a camera that shows the whole
  picture a little above centre, leaving the lower third to the captions. Marks, weather and light still work inside
  the window, and a move can travel between a close reframe and the window in one shot.
- **Tall pictures (9:16 or 2:3 from the image tool).** They are kept whole and centred on the canvas, never cropped.
  `film.img_box(name)` gives where the picture sits: a 9:16 image is x 637 to 1137, a 2:3 image is x 591 to 1183.
  Give marks and camera keys in those coordinates; `film.full(name)` frames it.
- Ask the image tool for a tall picture when a whole face, gesture or object must fill the screen; reuse wide
  pictures everywhere else.

## Explainer in portrait (the point of this mode)

Everything from the three ways to illustrate works: typed labels and drawn marks on the picture (`Marks`), sheets
that ink and paint themselves (`b.sheet`), pages and blank paper drawn on live (`b.page`, `Paper`), counters
(`fx2.Counter`), lifts, tears, comic pages. A `Paper` page is 2160 x 3840 in portrait; its marks are in half-page px
(1080 x 1920). The landscape map builders (`paper_map`, `map_page`) are laid out for a wide page: in portrait, draw a
map on a `Page` base or show a wide map in a window.

Rule of thumb for a reel: something is drawn, typed, counted or revealed at least every five or six seconds; a
picture is never just held under a caption.

## reel.py

```python
import reel

reel.badge(b, "1/4")
reel.headline(b, "THE WRONG PASSENGER", 0.25, 3.2, label="CAESAR AND THE PIRATES")
cap = reel.captions(b, emph=["Caesar", "fifty"], fix={"farmakusa": "Pharmacussa"},
                    mute=[(0, 3.2)], follow=False)
reel.popup(b, "incoming/06_popups/cornelia.png", t, t + 2.4, "CORNELIA", "Caesar's wife")
```

- **Captions** come from the batch's word timings: short phrases broken at punctuation and pauses, white with a
  dark outline, the `emph` words in gold; `follow=True` also lights the word being spoken. `fix` corrects names and
  numbers the transcription got wrong. `mute` turns them off under a headline or on a silent beat. They stay up over
  drawn pages.
- **Badge** is the episode mark, top right. **Headline** is the opening or cliffhanger line with a series label; it
  slides in with a paper swipe.
- **Popup** is the character or prop card (`character_popup.py`) with its sound: `"paper"` for an introduction,
  `"pop"` for a joke.
- `reel.SAFE` is the part of the screen the apps leave clear, as frame fractions `(0.05, 0.115, 0.86, 0.74)`. Keep
  faces, labels and marks inside it; captions sit just under it at `reel.CAPTION_Y`.
- These are plain overlays. Write the film's own beside them (see [creative.md](creative.md)); `reel.put` lays any
  RGBA picture on the frame.

## Sounds for reels

Besides the full list in the engine guide: `dice`, `splash` (an oar or a stone in water), `latch`, `pop` (a card
landing), `swipe` (a paper transition), `tap` (a pin or pencil point), `creak` (a ship's timber, an old door),
`gulls`. Tie each to a visible movement; leave some cuts clean.

## Worked example

`examples/portrait_reel/shots_reel.py` is the opening of the Grant film as a reel: headline, captions, a reframed
table with typed sums, the whole table in a window, whip and flash cuts, faces, and the question drawn on a blank
page. `examples/portrait_reel/grant_reel_proof.mp4` is the render.
