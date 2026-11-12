# Rendering and the final film

Nothing renders until you decide. Checking is done with stills sheets, which take ~30 s per batch; renders take
minutes to hours. **Claude never starts a render on its own: it asks first.**

## 1. Check every batch without rendering
```bash
python tools/stills.py b3            # 24 stills of the batch + the readability check -> renders/stills_b3.jpg
python tools/stills.py b3 12 4.5 31  # 12 stills, or stills at given seconds
```
Look at the sheet: nothing over a face, no word cut off, nothing dark on dark, no picture held too long. `b.check()`
(run by stills.py and before every render) lists words that won't be readable, shots under 1.2 s, comic panels too
quick, footnotes closing too soon, and a render stops on them (`--force` overrides).

## 2. Optional preview
`python tools/render_all.py b3 --preview`: half size, 12 fps, a few minutes. Good for checking timing and sound.

## 3. Full renders, in parallel
```bash
python tools/render_all.py                 # every batch, as many at once as this computer can take
python tools/render_all.py b2 b7           # only what changed after fixes
python tools/render_all.py --changed       # every batch whose shots file is newer than its render
python tools/render_all.py --cta           # also the ending
```
Each batch: `renders/bN.mp4` (1920x1080, 24 fps, x264), `renders/bN_fx.npy` (its effects stem for the final mix),
log in `renders/bN.log`. Renders run at low priority so the computer stays usable. Never render batches one after
another by hand: the runner keeps the right number going. Speed advice: performance.md.

## 4. The final join
```bash
python tools/final.py      # -> renders/<film>_final.mp4
```
Joins the batches and the ending with one continuous soundtrack: the narration, every batch's effects, the score
(crossfaded between cues, ducked under the voice), two-pass loudness to −14 LUFS with peaks limited to −2 dBTP. The
video is copied, not re-encoded, so it takes a minute or two. Set `YTF_FINAL_DIR` to also copy it to a finished-films
folder.

## 5. Check before uploading
```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate -show_entries format=duration renders/<film>_final.mp4
ffmpeg -hide_banner -i renders/<film>_final.mp4 -af ebur128=peak=true -f null - 2>&1 | tail -12
python scripts/video_stills.py renders/<film>_final.mp4 renders/final_check.jpg 5 60 180 400 600
```
1920x1080, 24 fps, about −14 LUFS integrated, true peak ≤ −1.5 dB. Then watch it once end to end.

## Upload notes
Title and description from the story (Claude can draft them with chapters from the batch times), sources and photo
credits in the description or a pinned comment (the footnotes point there), the thumbnail (thumbnails.md), and the
dub tracks (dubs.md).
