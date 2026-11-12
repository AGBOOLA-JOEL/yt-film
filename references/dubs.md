# Dubbed audio tracks (YouTube multi-language audio)

YouTube lets one video carry several audio tracks (YouTube Studio → the video → **Languages** → Add language →
**Dub** → upload the audio file). The picture stays the same, so the dubs only need the film's audio rebuilt with a
translated voice, exactly the film's length.

```bash
python tools/dub.py                      # Spanish + French (the default) -> dubs/out/<film>_<lang>.m4a
python tools/dub.py es                   # one language; other codes: pt de hi it ja id (add more in LANGS)
```

What it does, per language:
1. Translates every passage with Gemini (kept in `dubs/<lang>/translation.json`: edit it by hand and re-run to fix a
   line). Facts, names, numbers and hedges ("reportedly") are kept.
2. Records the translation in ~3-minute chunks (one TTS request each, which keeps a film well inside the daily
   request cap), finds where each passage starts with Whisper and cuts in the pause before it; a passage that won't
   fit is recorded alone. Each passage is fitted into the English passage's time slot (same start, never running
   into the next one); a line too long for its slot is shortened by the model, then sped up slightly (max ~1.4x).
3. Mixes it with the film's own effects stems and score exactly as `final.py` does, at −14 LUFS.

Needs: the batch renders (`renders/bN.mp4` + `bN_fx.npy`), the English word timings, `audio/music/`, and a Gemini key.
`YTF_DUB_JOBS` limits how many languages run at once (default 2: more trips the TTS rate limit; use 1 on a slow PC).

## Your end line in other languages
`CTA_LINE` in `tools/dub.py` holds the like/follow line per language with `{ch}` for your channel name
(`YTF_CHANNEL`); it replaces the machine translation of the passage containing `YTF_CTA_MARK` (default
"like the video"). Check these lines with a native speaker once; they're on every film.

## Dubbing a voice you recorded yourself
The dub script times each translated passage from the English word timings, so it works with an imported voice too
(import_voice.py writes the same timings). The dubbed voice is Gemini's; if you want your own voice in other
languages, record each translated passage (read `dubs/<lang>/translation.json`), name the files `P01.wav`... and ask
Claude to fit them into the slots instead of synthesising (same `passage_audio` step with your files).

## Checks before uploading
Length equals the film's (the script prints both), loudness ≈ −14 LUFS, the end line is right, and listen to a minute
in the middle and the last minute.
