# Troubleshooting

Run `python scripts/doctor.py` first: it checks Python, libraries, FFmpeg, fonts, Whisper, the key and UTF-8.

| Problem | Fix |
|---|---|
| `'ffmpeg' is not recognized` (Windows) | `winget install Gyan.FFmpeg`, then open a **new** terminal |
| `python` opens the Microsoft Store (Windows) | use `py -3.11` or the venv: `.venv\Scripts\python` |
| `UnicodeDecodeError` / `charmap codec` (Windows) | `setx PYTHONUTF8 1`, open a new terminal (setup does this) |
| `No module named cv2` / `PIL` | you're on the system Python: use `.venv/bin/python` (Mac) or `.venv\Scripts\python` (Windows) |
| `No GEMINI_API_KEY` | add it to `.env` (project or repo), or import your own voice (voice.md) |
| `FileNotFoundError: S03c_...` | the image isn't in `incoming/02_scenes` (or 04_bases, 03_sheets) with that exact name |
| `KeyError: 'the phrase'` in a shots file | the cue isn't in Whisper's words: print them (`import_voice.py --words b3`) and cue on what it heard |
| render stops: "readability problems" | read the list above it; fix placement/timing (or `--force` if you're sure) |
| a render dies late / no error | memory: lower `YTF_JOBS`; test new effects on two frames (`stills.py bN 2 t1 t2`) first |
| typewriter labels look plain (Windows) | fonts weren't downloaded: re-run the setup script or see `fonts/README.md` |
| footnote hand/note missing | the project can't find the repo: check `YTF_SKILL=` in the project's `.env` |
| `429` / quota errors | Gemini rate limits: wait and run again (finished parts are cached) |
| TTS model not found | Google renamed it: set `YTF_TTS_MODEL` (and `YTF_MUSIC_MODEL`, `YTF_IMAGE_MODEL`) to the current names from AI Studio |
| final film too quiet/loud | measure the **MP4** with ebur128 (final-render.md); don't change MUSIC_DB/DUCK_DB to fix the voice |
| the picture runs ahead of the voice | shots are cued on old word timings: re-run stills after any voice change and re-cue |
| images look soft | they were smaller than ~1600 px wide; re-download originals, not screenshots |
| Claude can't see the skill | it must be at `~/.claude/skills/yt-film/SKILL.md` (or `<project>/.claude/skills/...`); restart Claude Code |
