"""Carnegie's Daughter narration (third-person narrator, Gemini TTS voice Orus read slowly then played at 1.25x): one passage per `## ` section of SCRIPT.md (or TEST_SCRIPT.md with --test).

Per passage: synthesise slowly -> speed up (atempo, pitch kept, default 1.25x) -> cap long pauses -> Whisper word timings.
Per batch: passages joined with fixed gaps, so the narration flows the same inside and across batches.
Outputs voice/<pid>.wav (cache), voice/<batch>_vo.wav and voice/<batch>_words.json ({duration, words[p,w,s,e]}).

    python tools/voice.py [batch ...]      (default: every batch)
    python tools/voice.py --test           (the 30-second drawing test, TEST_SCRIPT.md)
    python tools/voice.py --pace           (words a minute per passage; prints SPEEDS for rushed takes)
    python tools/voice.py --text           (list the passages and their word counts)

Recorded the voice yourself (ElevenLabs, your own mic, another TTS)? Don't use this file: see
`python tools/import_voice.py --help` and references/voice.md. Settings (.env): GEMINI_API_KEY, YTF_VOICE (default
orus), YTF_TTS_MODEL, YTF_WHISPER_MODEL.
"""
import base64
import http.client
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "voice"
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parent))
import ytf  # noqa: E402
API = "https://generativelanguage.googleapis.com/v1beta"
MODEL = ytf.setting("YTF_TTS_MODEL", "gemini-3.8-flash-tts")   # check Google AI Studio for the current TTS model name
VOICE = ytf.setting("YTF_VOICE", "orus")                         # deep, calm male narrator; try charon, kore, aoede, fenrir...


class _Key:  # the key is read only when something is actually synthesised (so --pace and imports need none)
    def __str__(self):
        return ytf.gemini_key()


KEY = _Key()
STYLE = ("a documentary narrator telling a true and strange story: unhurried and deliberate, every word clear, low and "
         "warm, close to the listener; quietly gripping, lets the tension build, takes a real breath before each reveal "
         "and lets the strange details land; a calm, measured pace, never rushed, never theatrical")
STYLES = {}
SPEED, MAXPAUSE, GAP, SR = 1.25, 0.75, 0.9, 24000
SPEEDS = {'P02': 1.056, 'P04': 1.162, 'P06': 1.144, 'P07': 1.054, 'P14': 1.155, 'P15': 1.138, 'P17': 1.106, 'P18': 1.133, 'P19': 1.187, 'P21': 1.082, 'P22': 1.061, 'P23': 1.076, 'P24': 1.159, 'P25': 1.177, 'P26': 1.174, 'P27': 1.135, 'P29': 1.072, 'P31': 1.152, 'P36': 1.068, 'P41': 1.071, 'P45': 1.101, 'P47': 1.121, 'P48': 1.137, 'P49': 1.171}  # rushed takes evened out to ~160 wpm (Nov 2026)

# render batches: cut at natural breaks in the one continuous narration (filled in once SCRIPT.md exists)
BATCHES = {"b1": ['P01', 'P02', 'P03', 'P04'],   # the hook: the note on Fifth Avenue
           "b2": ['P05', 'P06', 'P07', 'P08', 'P09', 'P10'],   # Ontario: Betsy, the letter, the heiress card, the faces, to Cleveland
           "b3": ['P11', 'P12', 'P13', 'P14', 'P15', 'P16', 'P17'],   # Cleveland: the furniture, Madame DeVere, twelve days, the names, Toledo, prison, parole
           "b4": ['P18', 'P19', 'P20', 'P21'],   # Dr Chadwick, the faint, Euclid Avenue, nobody came
           "b5": ['P22', 'P23', 'P24', 'P25'],   # the chance meeting, inside the house, the secret, why it worked
           "b6": ['P26', 'P27', 'P28', 'P29', 'P30', 'P31'],   # the envelope, the receipt, the whisper, how it worked, Oberlin, Beckwith's money
           "b7": ['P32', 'P33', 'P34', 'P35', 'P36', 'P37'],   # the ledger, Queen of Ohio, the parties, Newton, Carnegie's answer, the run
           "b8": ['P38', 'P39', 'P40', 'P41', 'P42', 'P43'],   # the envelope opened, the Breslin, the trial, the gallery, guilty, the bankers
           "b9": ['P44', 'P45', 'P46', 'P47', 'P48', 'P49'],   # her trunks, the end, Woodstock, after, the paper, the end line
           "test": ["T01", "T02", "T03", "T04", "T05"]}
GAPS = {("P04", "P05"): 1.8, ("P21", "P22"): 1.6, ("P25", "P26"): 1.2, ("P34", "P35"): 1.6, ("P43", "P44"): 1.4,
        ("P47", "P48"): 1.2, ("P48", "P49"): 1.4}   # a longer breath before an act change (default GAP between passages)
SCRIPT = ROOT / ("TEST_SCRIPT.md" if "--test" in sys.argv else "SCRIPT.md")


def passages():
    """{P01: text, ...} in script order; cue lines (`[...]`) and markdown are dropped."""
    s = SCRIPT.read_text(encoding="utf-8").split("\n---\n", 1)[1]
    out = {}
    for i, m in enumerate(re.finditer(r"^## [^\n]*\n(.*?)(?=^## |\Z)", s, re.S | re.M), 1):
        lines = [l.strip() for l in m.group(1).splitlines()]
        lines = [l for l in lines if l and l != "---" and not l.startswith(("[", "`"))]
        text = re.sub(r"\*([^*]+)\*", r"\1", " ".join(lines))
        out[f"{'T' if SCRIPT.name.startswith('TEST') else 'P'}{i:02d}"] = re.sub(r"\s+", " ", text).strip()
    return out


def synth(text, style):
    body = {"model": MODEL, "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
            "annotations": [{"type": "speech_metadata", "style": style}]}]}],
            "response_format": {"type": "audio"}, "generation_config": {"speech_config": [{"voice": VOICE}]}}
    req = urllib.request.Request(API + "/interactions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "x-goog-api-key": str(KEY)})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            a = [c for s in d.get("steps", []) if s.get("type") == "model_output" for c in s.get("content", []) if c.get("type") == "audio"]
            return base64.b64decode(a[-1]["data"])
        except (urllib.error.URLError, http.client.HTTPException, TimeoutError, OSError, KeyError, IndexError) as e:
            print(f"    retry {attempt + 1}: {str(e)[:120]}", flush=True)
    raise SystemExit("TTS failed")


def tighten(x, sr):
    win = int(sr * 0.02)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(win) / win, mode="same"))
    quiet = rms < 10 ** (-42 / 20)
    keep = np.ones(len(x), bool)
    i = 0
    while i < len(x):
        if quiet[i]:
            j = i
            while j < len(x) and quiet[j]:
                j += 1
            if j - i > MAXPAUSE * sr and i > 0 and j < len(x):
                keep[i + int(MAXPAUSE * sr / 2): j - int(MAXPAUSE * sr / 2)] = False
            i = j
        else:
            i += 1
    nz = np.where(~quiet)[0]
    lo, hi = (nz[0], nz[-1] + win) if len(nz) else (0, len(x))
    keep[:max(0, lo - int(0.03 * sr))] = False
    keep[min(len(x), hi + int(0.05 * sr)):] = False
    return x[keep]


def passage_wav(pid, text):
    out = OUT / f"{pid}.wav"
    if out.exists():
        return out
    raw = OUT / f"{pid}_raw.wav"
    if not raw.exists():
        print(f"  tts {pid} ({len(text.split())} words)", flush=True)
        raw.write_bytes(synth(text, STYLES.get(pid, STYLE)))
    x, sr = sf.read(raw)
    x = x if x.ndim == 1 else x.mean(1)
    tmp = OUT / f"{pid}_tight.wav"
    sf.write(tmp, tighten(x, sr), sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", f"atempo={SPEEDS.get(pid, SPEED)}", "-ar", str(SR), "-ac", "1", str(out)], check=True)
    tmp.unlink()
    return out


def words(path, pid, offset):
    """Word timings (mlx-whisper on Apple Silicon, faster-whisper elsewhere), shifted to the batch's clock."""
    return [dict(p=pid, w=w["word"].strip(), s=round(w["start"] + offset, 3), e=round(w["end"] + offset, 3))
            for w in ytf.transcribe(path)]


def build(batch, pids, P):
    parts, W, t = [], [], 0.0
    for i, pid in enumerate(pids):
        if i:
            g = GAPS.get((pids[i - 1], pid), GAP)
            parts.append(np.zeros(int(g * SR))); t += g
        x, sr = sf.read(passage_wav(pid, P[pid]))
        W += words(OUT / f"{pid}.wav", pid, t)
        parts.append(x); t += len(x) / sr
    y = np.concatenate(parts)
    sf.write(OUT / f"{batch}_vo.wav", y, SR)
    (OUT / f"{batch}_words.json").write_text(json.dumps(dict(duration=len(y) / SR, words=W), indent=0), encoding="utf-8")
    print(f"{batch}: {len(y) / SR:.1f}s, {len(W)} words", flush=True)


def pace(P, target=160, cap=168):
    """Words a minute of every recorded passage; prints a SPEEDS dict that slows the rushed ones to ~target
    (Gemini sometimes reads a take fast: Chadwick had 20 of 49 passages over 180 wpm). Paste it into SPEEDS, delete
    those voice/<pid>.wav files (the _raw takes are kept) and run again."""
    sp = {}
    for k, v in P.items():
        f = OUT / f"{k}.wav"
        if f.exists():
            r = len(v.split()) / sf.info(f).duration * 60
            print(f"{k} {r:4.0f} wpm")
            if r > cap:
                sp[k] = round(max(1.05, SPEED * target / r), 3)
    print("SPEEDS =", sp)


def main(only):
    P = passages()
    if "--pace" in only:
        return pace(P)
    if "--test" in only:
        only = ["test"]
    if "--text" in only:
        for k, v in P.items():
            print(k, len(v.split()), v[:90])
        return
    for b in only or [k for k in BATCHES if k != "test"]:
        build(b, BATCHES[b], P)


if __name__ == "__main__":
    main(sys.argv[1:])
