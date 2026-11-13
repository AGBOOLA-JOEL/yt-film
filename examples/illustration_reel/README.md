# Illustration reel: every way the engine draws

A 95-second reel with no narration, made from one film's images (Grant and Ward, Nov 2026), each segment labelled
(top left) with the technique and the call that makes it. Watch `illustration_reel.mp4`; read `shots_demo.py` for
the exact code.

| # | Segment | Mode | Call |
|---|---|---|---|
| 1 | a living picture, a camera move with a purpose | on the picture | `scene(..., cam=, light=)` |
| 2 | sketching on the picture: typed numbers, a circle, an arrow, level handwriting, an underline, motion lines | on the picture | `Marks`, `sg.underline`, `sg.motion` |
| 3 | the scene draws itself (lines, then paint) | on the picture | `drawin(...)` |
| 4 | pin mode: drawings pinned on scraps over the scene | on the picture | `scene(draws=[Scrap(...), Draw(...)])` |
| 5 | the sketchbook sheet: drawings ink in, then wash; captions; a circle | sketchbook sheet | `sketchbook(sheet, cues, captions=, circles=)` |
| 6 | the blank page: drawings redrawn stroke by stroke, an arrow, a timeline | blank page | `blank(draw)` + `page.lift / stroke / text` |
| 7 | drawing on a story object: a map, a route, ticks, leader labels, pinned drawings | blank page (a base) | `page("B03_map", [...], marks=)` |
| 8 | the comic page: panels painted in turn | on a board | `sg.Comic(...)` |
| 9 | a rolling counter and a rubber stamp | effects | `Counter(...)`, `stamp(...)` |
| 10 | an archive photo print and a footnote card | effects | `pic(...)`, `note(...)` |

To make one for your own film: copy `shots_demo.py` into your project's `tools/`, change the image names to yours,
write `voice/demo_words.json` as `{"duration": 95, "words": []}` with a silent `voice/demo_vo.wav`, then
`python tools/stills.py demo 24` and `python tools/shots_demo.py`. It needs the film module the shots import
(`from grant import *` here: change it to your film's module, which defines `pic`, `note`, `dr`).
