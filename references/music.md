# Music: Lyria cues, or your own

One instrumental cue per section of the story (5–7 per film), each ~3 minutes, crossfaded at section changes and
looped where a section runs longer. `final.py` sits the score **−25 dB under the voice and a further −9 dB while the
narrator talks**: the voice always leads. Don't raise these.

## Route 1 · Lyria (Gemini API)
Write `CUES` in `tools/music.py` (Claude does it from the story): the place, era and mood of the section, a tempo,
three or four instruments, and the shared start ("Instrumental only, no vocals... under a spoken narration").
```bash
python tools/music.py              # every cue (existing files are kept)
python tools/music.py m_fall       # one again (delete audio/music/m_fall.mp3 first)
```
Lyria refuses prompts that mention death, prison, graves or violence: describe the mood and place instead
("the quiet epilogue of a true story", "a cold stone building at dawn"). Output carries Google's SynthID watermark.
The example's cue prompts are in `examples/chadwick/audio/music/*.prompt.txt`.

## Route 2 · Your own music
Any `.mp3`, `.wav` or `.m4a` you have the rights to use on YouTube (your own, a royalty-free library whose licence
covers YouTube monetisation, Suno/Udio with a plan that grants commercial use, YouTube Audio Library). Save each as
`audio/music/<cue>.mp3` and use those cue names in `final.py`.
- Instrumental only, steady dynamics, no big drops (they fight the voice).
- At least ~2 minutes each; shorter tracks loop from 20 s in with a crossfade.

## Mapping cues to batches (`final.py`)
```python
MUSIC = {"b1": ("m_hook", 0.0), "b2": ("m_rise", 0.0), "b3": ("m_rise", None),   # None: b2's cue carries on
         "b4": ("m_fall", 0.0), "b5": ("m_end", 0.0), "cta": ("m_end", None)}
```
The second number is the offset into the cue where that section starts (seconds).
For a preview with music in a single batch, put `b.music = ("m_rise", 0.0)` in its shots file.

## Sound effects and crowd murmur
Effects are synthesised by the engine (no library, no copyright): fire, rain, wind, thunder, knocks, thuds, stamps,
shutters, typing, paper, trains... (`b.fx(kind, t0, t1, db)`). People talking in a scene: `tools/walla.py` layers
quiet Gemini TTS voices into a murmur (`audio/walla/<name>.wav`), played with `b.fx("wav", t0, t1, db=-16, path=...)`.
Any CC0 recording works the same way (credit it). Keep effects few and under the voice; the pencil sound is quiet
(−27 dB) on purpose.
