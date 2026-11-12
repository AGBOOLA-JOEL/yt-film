"""The whole film: every story batch and the closing ending (cta) joined, with one continuous soundtrack.

Narration (each batch voice placed at its batch's start), the batch effect stems (renders/<b>_fx.npy), and a score
that flows across the joins: one music cue per section, crossfaded where the cue changes and looped (with a
crossfade) where a section outlasts its cue, ducked under the voice. Two-pass loudnorm, then -14 LUFS / -2 dBTP
(YouTube's level). The ending is renders/cta.mp4 made by tools/cta.py; without one the film ends on the last batch.

    python tools/final.py      -> renders/<film>_final.mp4   (and a copy in YTF_FINAL_DIR/<film>/ if that is set)
"""
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np
from scipy import ndimage

import film
import ytf

ROOT = Path(__file__).resolve().parent.parent
FILM = ROOT.name
R = ROOT / "renders"
SR = 48000
MUSIC_DB, DUCK_DB = -25, -9  # score vs the voice overall, and a further dip while the narrator talks: the voice always leads
BATCHES = ["b1", "b2", "b3", "cta"]          # every batch in order, then the ending
# (cue, offset into the cue at the section start) per batch; None = the previous batch's cue carries on
MUSIC = {"b1": ("m_hook", 0.0), "b2": ("m_rise", 0.0), "b3": ("m_end", 0.0), "cta": ("m_end", None)}
XF = 3.0  # crossfade seconds, between cues and at loop points


def src(b, kind):
    """Where batch b's video / effects stem / voice live (the ending, cta, is rendered into renders/ like a batch)."""
    return {"mp4": R / f"{b}.mp4", "fx": R / f"{b}_fx.npy", "vo": ROOT / "voice" / f"{b}_vo.wav"}[kind]


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def looped(x, start, n):
    """n samples of cue x from `start`, looping back to 20 s with a crossfade when it runs out."""
    k = int(XF * SR)
    total, body = x[int(start * SR):], x[int(20 * SR):]
    while len(total) < n:
        mid = total[-k:] * np.linspace(1, 0, k) + body[:k] * np.linspace(0, 1, k)
        total = np.concatenate([total[:-k], mid, body[k:]])
    return total[:n].astype(np.float32).copy()


def main():
    global BATCHES
    missing = [b for b in BATCHES if not src(b, "mp4").exists()]
    if missing == ["cta"]:
        print("note: no renders/cta.mp4 (make one with tools/cta.py, see references/cta.md); joining without an ending")
        BATCHES = [b for b in BATCHES if b != "cta"]
    elif missing:
        raise SystemExit(f"render these batches first: {missing}  (python tools/render_all.py)")
    lens = [dur(src(b, "mp4")) for b in BATCHES]
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
    n = int(sum(lens) * SR)
    voice, fx, mus = (np.zeros(n, np.float32) for _ in range(3))
    for b, t0, L in zip(BATCHES, starts, lens):
        i0, m = int(t0 * SR), int(L * SR)
        vo, vsr = film._read(src(b, "vo"))
        vo = film._resample(vo, vsr, SR)
        vo = vo * 0.5 / (np.percentile(np.abs(vo), 99.9) + 1e-9) if np.abs(vo).max() > 0 else vo  # the CTA has no voice  # same voice level the batch effects were made against
        voice[i0:i0 + min(len(vo), m)] = vo[:m]
        f = np.load(src(b, "fx"))
        fx[i0:i0 + min(len(f), m)] += f[:m]
    # score: one bed per cue run, crossfaded at the cue changes
    runs, cur = [], None
    for b, t0, L in zip(BATCHES, starts, lens):
        cue, off = MUSIC[b]
        if off is None and cur is not None:
            cur[2] += L
        else:
            cur = [cue, t0, L, off or 0.0]
            runs.append(cur)
    xf = int(XF * SR)
    for cue, t0, L, off in runs:
        x = film._decode(ROOT / "audio" / "music" / f"{cue}.mp3", SR)
        i0 = max(0, int(t0 * SR) - (xf // 2 if t0 > 0 else 0))
        m = min(n - i0, int(L * SR) + (xf if t0 > 0 else 0))
        seg = looped(x, off, m)
        seg = seg / (np.sqrt(np.mean(seg ** 2)) + 1e-9)
        k = min(xf, m // 4)
        seg[:k] *= np.linspace(0, 1, k)
        seg[-k:] *= np.linspace(1, 0, k)
        mus[i0:i0 + m] += seg
    venv = ndimage.uniform_filter1d(np.abs(voice), int(0.25 * SR))
    duck = 10 ** (DUCK_DB * np.clip(venv / (np.percentile(venv, 95) * 0.25), 0, 1) / 20)
    mus *= np.sqrt(np.mean(voice ** 2)) * 10 ** (MUSIC_DB / 20) * duck
    end = int(2.5 * SR)
    mus[-end:] *= np.linspace(1, 0, end)
    y = voice + mus + fx
    tmp = R / f"{FILM}_final.raw.wav"
    film._write(tmp, y / (np.abs(y).max() + 1e-9) * 0.9, SR)
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14.5:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    i = r.stderr.rfind("{")
    mj = json.loads(r.stderr[i:r.stderr.find("}", i) + 1])
    wav = R / f"{FILM}_final.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af",
                    f"loudnorm=I=-14.5:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
                    f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true",
                    "-ar", str(SR), str(wav)], check=True)
    tmp.unlink()
    lst = R / "concat.txt"
    lst.write_text("".join(f"file '{src(b, 'mp4').resolve().as_posix()}'\n" for b in BATCHES), encoding="utf-8")  # forward slashes: Windows-safe
    out = R / f"{FILM}_final.mp4"
    # the synthesised clicks (typewriter, shutters) are spiky and AAC overshoots them by several dB: limit the spikes,
    # then normalise to YouTube's -14 LUFS with true peaks at -2 dBFS
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-i", str(wav),
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-af", "alimiter=limit=0.45:attack=0.5:release=40:level=false,loudnorm=I=-14:TP=-2:LRA=11,aresample=48000",
                    "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", str(out)], check=True)
    print("wrote", out, f"{sum(lens):.1f}s")
    dest = ytf.setting("YTF_FINAL_DIR")
    if dest:  # optional: copy the finished film to your finished-films folder
        d = Path(dest).expanduser() / FILM
        d.mkdir(parents=True, exist_ok=True)
        shutil.copy2(out, d / out.name)
        print("copied to", d / out.name)


if __name__ == "__main__":
    main()
