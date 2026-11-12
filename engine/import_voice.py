"""Bring your own narration: use a voice you recorded or made elsewhere (your mic, ElevenLabs, OpenAI TTS, Azure,
CapCut, any TTS) instead of tools/voice.py. Produces exactly what voice.py produces, so the rest of the engine
can't tell the difference:  voice/<batch>_vo.wav  +  voice/<batch>_words.json

Three ways in (any audio format ffmpeg reads: wav, mp3, m4a, ogg, flac):

  1. ONE FILE for the whole film (easiest when you record or generate in one go):
        python tools/import_voice.py --full narration.mp3
     Whisper times every word, the words are matched to SCRIPT.md's passages, and the file is cut into the batches
     of voice.py's BATCHES in the silences between them.

  2. ONE FILE PER PASSAGE (P01.mp3, P02.mp3 ... named like the `## ` passages in SCRIPT.md, in one folder):
        python tools/import_voice.py --passages my_takes/
     Each take is cleaned (long pauses capped) and the batches are joined with the same gaps voice.py uses.
     This is the best way to fix one passage later: replace one file and run it again.

  3. ONE FILE PER BATCH (b1.wav, b2.wav ... in one folder):
        python tools/import_voice.py --batches my_batches/

Options:
  --speed 1.1     play the takes faster (pitch kept), e.g. if you read slowly. Default 1.0 (as recorded).
  --keep-pauses   don't shorten long pauses (default caps pauses at 0.75 s, like voice.py)
  --check         after importing, print each batch's length and words a minute (aim for ~140-160 wpm)

Batches come from BATCHES in tools/voice.py: set them first (natural breaks, 4-7 passages, 65-100 s each).
Names Whisper mishears are fine: cue your shots on what Whisper wrote (print a batch's words with --words b1).
"""
import difflib
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
_argv = sys.argv
sys.argv = [sys.argv[0]]
import voice as V  # noqa: E402  (passages, BATCHES, GAPS, tighten, words)
import ytf  # noqa: E402
sys.argv = _argv

ROOT, OUT, SR = V.ROOT, V.OUT, V.SR
AUDIO = (".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac", ".opus", ".webm", ".mp4")


def load(path, speed=1.0):
    """Any audio file -> mono float32 at SR, optionally sped up (atempo keeps the pitch)."""
    af = ["-af", f"atempo={speed}"] if abs(speed - 1) > 1e-3 else []
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), *af, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def write_batch(name, y, W):
    sf.write(OUT / f"{name}_vo.wav", y.astype(np.float32), SR)
    (OUT / f"{name}_words.json").write_text(json.dumps(dict(duration=len(y) / SR, words=W), indent=0), encoding="utf-8")
    print(f"{name}: {len(y) / SR:.1f}s, {len(W)} words", flush=True)


def label(words, P, pids):
    """Give each Whisper word the passage id it belongs to, by matching the transcript to the script text."""
    script = [(pid, norm(w)) for pid in pids for w in P[pid].split() if norm(w)]
    heard = [norm(w["word"]) for w in words]
    sm = difflib.SequenceMatcher(None, heard, [t for _, t in script], autojunk=False)
    owner = [None] * len(heard)
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            owner[a + k] = script[b + k][0]
    last = pids[0]
    for i in range(len(owner)):  # unmatched words (numbers, misheard names) belong to the passage around them
        if owner[i] is None:
            owner[i] = last
        last = owner[i]
    return owner


def by_passages(folder, speed, keep):
    P = V.passages()
    files = {f.stem.upper(): f for f in Path(folder).iterdir() if f.suffix.lower() in AUDIO}
    missing = [p for p in P if p not in files and not p.startswith("T")]
    if missing:
        print("warning: no take for", missing)
    for pid, f in files.items():
        x = load(f, speed)
        x = x if keep else V.tighten(x, SR)
        sf.write(OUT / f"{pid}.wav", x, SR)  # voice.py treats these as finished takes and never calls TTS for them
    for b, pids in V.BATCHES.items():
        if b == "test" or not all(p in files for p in pids):
            continue
        V.build(b, pids, P)


def by_batches(folder, speed, keep):
    P = V.passages()
    for f in sorted(Path(folder).iterdir()):
        if f.suffix.lower() not in AUDIO or f.stem not in V.BATCHES:
            continue
        y = load(f, speed)
        y = y if keep else V.tighten(y, SR)
        tmp = OUT / f"_{f.stem}_import.wav"
        sf.write(tmp, y, SR)
        ws = ytf.transcribe(tmp)
        tmp.unlink()
        owner = label(ws, P, V.BATCHES[f.stem])
        W = [dict(p=o, w=w["word"].strip(), s=round(w["start"], 3), e=round(w["end"], 3)) for w, o in zip(ws, owner)]
        write_batch(f.stem, y, W)


def by_full(path, speed):
    P = V.passages()
    order = [b for b in V.BATCHES if b != "test"]
    pids = [p for b in order for p in V.BATCHES[b]]
    y = load(path, speed)
    tmp = OUT / "_full_import.wav"
    sf.write(tmp, y, SR)
    print("timing every word (Whisper; a few minutes on a slow PC)...", flush=True)
    ws = ytf.transcribe(tmp)
    tmp.unlink()
    owner = label(ws, P, pids)
    # cut between batches in the middle of the silence after a batch's last word
    first = {}
    for i, o in enumerate(owner):
        first.setdefault(o, i)
    cuts = [0.0]
    for b in order[1:]:
        i = first.get(V.BATCHES[b][0])
        if i is None:
            raise SystemExit(f"couldn't find passage {V.BATCHES[b][0]} in the recording: does it follow SCRIPT.md?")
        prev_end = ws[i - 1]["end"] if i else 0.0
        cuts.append((prev_end + ws[i]["start"]) / 2)
    cuts.append(len(y) / SR)
    for k, b in enumerate(order):
        t0, t1 = cuts[k], cuts[k + 1]
        lead = 0.15  # keep a breath before the first word
        s0 = max(0.0, min(t0, next((w["start"] for w, o in zip(ws, owner) if o in V.BATCHES[b]), t0) - lead))
        seg = y[int(s0 * SR):int(t1 * SR)]
        W = [dict(p=o, w=w["word"].strip(), s=round(w["start"] - s0, 3), e=round(w["end"] - s0, 3))
             for w, o in zip(ws, owner) if o in V.BATCHES[b] and t0 <= w["start"] < t1]
        write_batch(b, seg, W)


def check():
    P = V.passages()
    for b, pids in V.BATCHES.items():
        f = OUT / f"{b}_words.json"
        if b == "test" or not f.exists():
            continue
        d = json.loads(f.read_text(encoding="utf-8"))
        n = sum(len(P[p].split()) for p in pids if p in P)
        print(f"{b}: {d['duration']:.1f}s  {n / d['duration'] * 60:.0f} wpm  ({len(d['words'])} words heard, {n} in script)")


def show_words(b):
    d = json.loads((OUT / f"{b}_words.json").read_text(encoding="utf-8"))
    print(" ".join(f"{w['w']}@{w['s']:.1f}" for w in d["words"]))


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or "--help" in a or "-h" in a:
        print(__doc__)
        sys.exit()
    speed = float(a[a.index("--speed") + 1]) if "--speed" in a else 1.0
    keep = "--keep-pauses" in a
    if "--full" in a:
        by_full(a[a.index("--full") + 1], speed)
    elif "--passages" in a:
        by_passages(a[a.index("--passages") + 1], speed, keep)
    elif "--batches" in a:
        by_batches(a[a.index("--batches") + 1], speed, keep)
    elif "--words" in a:
        show_words(a[a.index("--words") + 1])
    if "--check" in a or "--full" in a or "--batches" in a or "--passages" in a:
        check()
