# Speed: making films on slow PCs and laptops

A 12-minute film is ~17,000 frames at 1080p, each with layered effects. On a fast Mac (10+ cores, 32 GB) all
batches render in parallel in ~25 minutes. A 4-core Windows laptop with 8 GB might need a few hours, rendering one
or two batches at a time. Both work; slow machines just need a smarter routine.

## What render_all does for you
- Picks how many batches run at once from your cores and RAM (≈ one per 2 cores and per 3 GB), leaving room for the
  system. Override with `--jobs 1` or `YTF_JOBS=1` in `.env`.
- Gives each render a fair share of CPU threads (`YTF_THREADS`) so parallel renders don't fight.
- Runs renders at low priority (Windows: below normal; Mac/Linux: nice 10) so you can keep working.
- `--changed` re-renders only batches whose shots changed.

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

## Windows-specific speedups
- Exclude your projects folder from Windows Defender real-time scanning (it scans every frame file written).
- Plug in the laptop and set Power mode to **Best performance**.
- Keep projects out of OneDrive/Dropbox folders while rendering.
- Close Chrome and other heavy apps during full renders; 8 GB machines especially.
- An SSD matters: the image caches (`build/up/`) are large and read constantly.

## Disk space
Per film: images ~0.5 GB, caches in `build/` 1–3 GB (safe to delete after the film is done: they rebuild), batch
renders 1–2 GB, the final film ~1–1.5 GB. Keep ~10 GB free.

## Memory
A full-size batch can use 2–3 GB. If a render dies without an error (or Windows says "MemoryError"), lower
`YTF_JOBS`. Very long batches (> 120 s) use more: split them into two batches in voice.py.

## Apple Silicon vs Intel/AMD
Apple Silicon is fast for rendering and very fast for Whisper (GPU). On Windows, an NVIDIA GPU speeds up Whisper
(faster-whisper uses CUDA automatically if the CUDA runtime is installed); the renders themselves use the CPU.
