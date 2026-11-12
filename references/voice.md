# Narration: Gemini TTS, or bring your own voice

Every shot is cued on the narrator's words, so the voice comes **before** the shot lists. Whatever makes the voice,
the engine needs the same two files per batch:
`voice/<batch>_vo.wav` (the narration) and `voice/<batch>_words.json` (every word with its start and end time).

## The script format (both routes)
`SCRIPT.md`: a title, a line `---`, then one `## ` section per passage (P01, P02 ... in order). Lines starting with
`[` are notes for Claude (`[SHOTS: S03a, S03b]`, `[NOTE 2]`, `[FX: ...]`) and are never read aloud.
Batches (`BATCHES` in `tools/voice.py`) group 4–7 passages at natural breaks, ~65–100 s each; `GAPS` sets longer
breaths before an act change.

## Route 1 · Gemini TTS (the default, what the example uses)
```bash
python tools/voice.py --test          # the 30-second test script first: listen to it
python tools/voice.py                 # every batch (or: voice.py b3 b4)
python tools/voice.py --pace          # words a minute per passage
```
- Voice **Orus** read slowly with a narrator style prompt (`STYLE` in voice.py), then sped up to **1.25x** (pitch
  kept), long pauses capped at 0.75 s, 0.9 s between passages. That combination sounds calm but never sleepy.
- Other voices: `YTF_VOICE=charon` (or kore, aoede, fenrir, puck, leda, zephyr...) in `.env`. Try two or three on the
  test script before a full film. Women narrators: try kore or aoede.
- **Pace check**: Gemini sometimes reads a take fast. `--pace` prints a `SPEEDS` dict for the passages over ~168 wpm;
  paste it into voice.py, delete those passages' `voice/Pxx.wav` (the `_raw` takes are kept, so no new TTS) and run
  again. Aim for ~140–160 wpm in every batch.
- Change one passage: edit SCRIPT.md, delete `voice/Pxx.wav` and `voice/Pxx_raw.wav`, run `voice.py <its batch>`.
- Free-tier limits: a full film is ~50 TTS calls; if you hit a rate limit, run it again later (finished passages are
  cached).

## Route 2 · Your own voice or another TTS (ElevenLabs, OpenAI, Azure, CapCut, your microphone...)
Write the script with Claude first (SCRIPT.md), then record or generate from it. Three ways to bring it in:

**One file for the whole film** (easiest):
```bash
python tools/import_voice.py --full narration.mp3
```
Whisper times every word, matches them to the script's passages and cuts the file into the batches in the silences.
Read the script as written (small slips are fine; whole skipped passages are not).

**One file per passage** (best for fixing later): name them `P01.mp3`, `P02.mp3` ... like the script's passages, put
them in one folder:
```bash
python tools/import_voice.py --passages takes/
```
To redo one passage, replace its file and run it again.

**One file per batch**: `b1.wav`, `b2.wav` ... in a folder: `python tools/import_voice.py --batches my_batches/`.

Options: `--speed 1.1` (you read slowly; pitch kept), `--keep-pauses`, `--check` (length and words a minute per batch),
`--words b3` (print what Whisper heard, with times).

Recording tips: a quiet room, the mic a hand's width away, a steady level; export WAV or a high-bitrate MP3, mono is
fine. ElevenLabs/OpenAI: one passage per generation keeps the delivery consistent and makes redoing one easy.
Don't add music or effects to the voice: the engine mixes the score, the effects and the drawing sounds itself.

## Word timings (Whisper)
- Apple Silicon Macs use `mlx-whisper` (fast, on the GPU). Windows, Intel Macs and Linux use `faster-whisper`
  (CPU int8; an NVIDIA GPU with CUDA is used automatically).
- Slow PC: set `YTF_WHISPER_MODEL=small.en` (or `medium.en`) in `.env`. Timings stay good; names may be misheard more.
- **Whisper mishears names and writes numbers as digits** ("Dylan" for Dillon, "in 1988"). Shots are cued on what
  Whisper wrote: print a batch's words before writing its shots (`import_voice.py --words b1`, or read
  `voice/b1_words.json`). Spell names correctly only on screen.
- Languages other than English work too (Whisper detects the language); write the script in that language.
