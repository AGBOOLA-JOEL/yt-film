# The ending (call to action)

The film's narration ends on a short like/follow line over the last story shot (a slow push, a fade). Then a short
**ending batch** (`cta`) plays: your channel's own animated sign-off. Make it once, in your style, and reuse it on
every film. This repo does **not** ship a finished ending: make your own so your channel looks like you.

## The example: `tools/cta.py` (Python, no stock footage)
A 7-second sketchbook page drawn live in ink: your channel name (`YTF_CHANNEL`) is handwritten across the top and
underlined in red, a thumbs-up, a subscribe button and a bell are drawn, then a cursor clicks like (it fills),
subscribe (it turns to "Subscribed") and the bell (it rings), with pen, click and bell sounds.
```bash
python tools/cta.py --preview     # quick look: renders/cta_preview.mp4
python tools/cta.py               # the real one: renders/cta.mp4 + renders/cta_fx.npy + voice/cta_vo.wav
```
`final.py` adds it as the last batch (`"cta"` at the end of `BATCHES`); without `renders/cta.mp4` the film simply ends
on its last batch. Copy the three files into each new project's `renders/`/`voice/` to reuse the same ending, or
re-run cta.py there.

## Make it yours (ask Claude, it edits cta.py)
Everything is code, so any of these is a short change:
- the words and font (`f.text(NAME, ...)`), the page (any base image instead of the sketchbook), the colours;
- what's drawn (your mascot's line art lifted from a sheet with `pg.lift`, a logo traced in ink, an end-screen
  layout with two empty boxes where YouTube's end-screen videos will sit: keep 20 s for that if you use end screens);
- the order and timing of the clicks (`CLICKS`), the length (`END`), the sounds (`b.fx` kinds);
- a spoken line: record or TTS it, save as `voice/cta_vo.wav` (same length as the ending).

Example prompt: *"Change the ending: my channel name in the typewriter font on a blank map base, a red pin drops on
it, then the subscribe button draws itself and gets clicked. 8 seconds, keep the pen sound quiet."*

## The spoken line
The last passage of SCRIPT.md, for example: *"If this story stayed with you, like the video, and follow the channel
for more."* Keep it short and calm, and say your channel name if you like. For dubs, add its translations to
`CTA_LINE` in dub.py (dubs.md).
