# Speed: rendering without freezing the computer (slow PCs, laptops, Windows)

A 12-minute film is ~17,000 frames at 1080p, each with layered effects. Batches render in parallel, but **memory,
not CPU, sets how many can run at once.** Each batch render needs about **1.1–1.4 GB** (measured at 1080p with the
v2 effects); preview renders about half that.

## What happens when too many run at once (a real case)
A 14-batch film on a 10-core, 16 GB Mac with a browser, a design tool and an IDE open, 7 renders started at once,
each with a full thread pool:
- memory ran out (73 MB free, 12 GB of swap used); the CPU sat **58% idle**, waiting on memory instead of working;
- progress fell to about 0.4 s of film per minute per batch; after 2 hours only 3 batches were done; the computer
  lagged so badly it was hard to use.

Stopping everything, keeping the 4 finished batches and relaunching the other 10 **4 at a time, 2 threads each, low
priority**, with the heavy apps closed: about 6–8 s of film per minute per batch, all done in ~50 minutes. More at
once is slower once memory runs out. A Windows laptop hits the same wall sooner: less memory, a slower page file.

## What render_all does for you
- Counts **free** memory when it starts (with your apps open) and runs about one batch per 2 GB free, leaving 2 GB
  for the system, and no more than one per 2 CPU cores. Override with `--jobs 1` or `YTF_JOBS=1` in `.env`.
- Before starting each further batch it checks free memory again and **waits** if there isn't room ("waiting for
  free memory before starting b7"), so opening an app mid-render doesn't sink everything.
- Gives each render a fair share of CPU threads (`YTF_THREADS`) so parallel renders don't fight.
- Runs renders at low priority (Windows: below normal; Mac/Linux: nice 10) so you can keep working.
- `--changed` renders only batches whose shots changed or that have no finished mp4: it is also how to resume.

| Machine | Batches at once (`YTF_JOBS`) |
|---|---|
| 8 GB laptop | 1 (2 only with nothing else open) |
| 16 GB | 2–4 (4 only with the browser closed) |
| 32 GB | 4–6 |
| 64 GB+ | 8 |

## Launch it so it keeps going
A render started from Claude's session can stop when the session or terminal closes. Start full renders in their
own window:

```bat
:: Windows (cmd), from the project folder: a separate window at low priority
start "yt renders" /low cmd /k ".venv\Scripts\python tools\render_all.py --changed"
```
```bash
# Mac: in a separate Terminal window, kept awake
caffeinate -i .venv/bin/python tools/render_all.py --changed
```
(Use the `PY` path from SKILL.md if your venv lives in the repo.)

## Is it struggling? Warning signs
Each batch's log (`renders/bN.log`) prints a line every 5 s of film: `  50.0s / 86.7`. With 2–4 at once on a
normal machine expect a new line every ~40–90 s.
- **Windows:** Task Manager → Performance → Memory above ~90% or "Committed" near its limit; Disk at 100% for
  minutes (the page file); render windows "Not responding"; the mouse stutters; a render dies with no error or with
  `MemoryError`.
- **Mac:** Activity Monitor → Memory: pressure yellow or red, swap used growing past a few GB; CPU mostly idle while
  renders are slow (`sysctl vm.swapusage`, `top -l 1 | grep PhysMem`).
- **Any:** log lines several minutes apart.

Logs keep their old text until a batch starts, so a queued batch can still show an old error: check the log's time.

## Recovering without losing finished batches
Never delete a finished `renders/bN.mp4`.
1. **Let the nearly done ones finish.** Pause the renders that are least far along, let the others write their mp4,
   then resume:
   - Windows: Resource Monitor (`resmon`) → CPU tab → right-click the `python.exe` → **Suspend Process**, later
     **Resume Process**.
   - Mac/Linux: `kill -STOP <pid>`, later `kill -CONT <pid>`.
2. **Or stop and relaunch fewer:** Ctrl+C in the render window (or end the `python.exe` renders), delete partial
   `renders/bN.silent.mp4` files, close heavy apps, then `render_all.py --changed --jobs 2`. Finished batches are
   skipped.
3. Still slow with 1 at a time: render overnight; check every batch with `stills.py` first so each renders once.

## The slow-machine routine
1. **Check with stills, not renders.** `stills.py bN` (~30–60 s) catches almost everything a render would.
2. **Preview only what you're unsure of** (`--preview`: a quarter of the pixels, half the frames).
3. **Render full batches once**, overnight or while away: `python tools/render_all.py --changed`.
4. Fix with surgical re-renders: only the batches that changed.

## Settings for slow PCs (`.env`)
```
YTF_JOBS=1                  # or 2: batches at once
YTF_X264_PRESET=faster      # encoding: much quicker, slightly bigger files (veryfast on very slow PCs)
YTF_WHISPER_MODEL=small.en  # word timings in a fraction of the time (check names by eye)
YTF_DUB_JOBS=1              # one dub language at a time (default 2)
```

## Windows: before a full render
- Close Chrome/Edge, Teams, design tools and IDEs; they hold gigabytes.
- Plug in the laptop; Settings → System → Power: Power mode **Best performance**, and sleep **Never** while plugged
  in for the length of the render (set it back afterwards).
- Exclude your projects folder from Windows Security real-time scanning (Virus & threat protection → Exclusions):
  it otherwise scans every frame file written.
- Keep projects out of OneDrive/Dropbox/Google Drive folders while rendering.
- Leave the page file "System managed", on the SSD. An SSD matters: the image caches (`build/up/`) are large and
  read constantly.
- Split batches longer than ~120 s into two in voice.py: they need more memory.

## Disk space
Per film: images ~0.5 GB, caches in `build/` 1–3 GB (safe to delete after the film is done: they rebuild), batch
renders 1–2 GB, the final film ~1–2.5 GB. Keep ~10 GB free.

## Apple Silicon vs Intel/AMD
Apple Silicon is fast for rendering and very fast for Whisper (GPU). On Windows, an NVIDIA GPU speeds up Whisper
(faster-whisper uses CUDA automatically if the CUDA runtime is installed); the renders themselves use the CPU.
