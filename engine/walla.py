"""Crowd murmur ("walla") for the scenes with people talking, made from several Gemini TTS voices saying quiet
everyday lines in the scene's language, layered with offsets, low-passed and softened -> audio/walla/<name>.wav.
Used with b.fx("wav", t0, t1, db=..., path=...). No library sounds, so no copyright.

    python tools/walla.py [name ...]
"""
import json
import sys
import base64
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

import voice as V

OUT = V.ROOT / "audio" / "walla"
OUT.mkdir(parents=True, exist_ok=True)
VOICES = ["puck", "kore", "charon", "fenrir", "aoede", "leda", "zephyr", "orus"]
STYLE = "a person in a crowd talking quietly to the person next to them, casual, low, not performing, natural pauses"
SETS = {   # one set per crowd scene: 6-8 quiet everyday lines in the scene's own language and era
    "crowd_street": ["Did you hear what happened this morning?", "I'm not waiting in this line all day.",
                     "They say it's all over the papers.", "My sister told me to come first thing.",
                     "Has anybody seen the manager?", "Look at all these people.",
                     "It'll be fine, it always is.", "Somebody said the doors open at nine."],
    "dinner_party": ["Oh, it's delicious, really.", "Did you see the opera last week?",
                     "A little more wine, sir?", "My husband talks of nothing but the market.",
                     "He's a very private man, you know.", "We leave for the coast in April.",
                     "What a lovely evening.", "Have you met our host before?"],
}


def synth(text, voice):
    body = {"model": V.MODEL, "input": [{"type": "user_input", "content": [{"type": "text", "text": text,
            "annotations": [{"type": "speech_metadata", "style": STYLE}]}]}],
            "response_format": {"type": "audio"}, "generation_config": {"speech_config": [{"voice": voice}]}}
    req = urllib.request.Request(V.API + "/interactions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "x-goog-api-key": str(V.KEY)})
    import time
    for attempt in range(8):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                d = json.loads(r.read())
            break
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(20 * (attempt + 1))
    a = [c for s in d.get("steps", []) if s.get("type") == "model_output" for c in s.get("content", []) if c.get("type") == "audio"]
    return base64.b64decode(a[-1]["data"])


def make(name, lines, secs=24.0, sr=24000):
    tmp = OUT / name
    tmp.mkdir(exist_ok=True)
    rng = np.random.default_rng(len(name))
    mix = np.zeros(int(secs * sr), np.float32)
    for i, line in enumerate(lines):
        f = tmp / f"{i}.wav"
        if not f.exists():
            f.write_bytes(synth(line, VOICES[i % len(VOICES)]))
        x, xsr = sf.read(f, dtype="float32")
        x = x if x.ndim == 1 else x.mean(1)
        x = x / max(1e-4, np.abs(x).max()) * rng.uniform(0.35, 0.8)
        # each voice repeats a few times across the bed, at random places
        for _ in range(3):
            j = int(rng.uniform(0, secs - len(x) / xsr - 0.1) * sr)
            mix[j:j + len(x)] += x[:len(mix) - j]
    sos = butter(2, [180, 3200], btype="band", fs=sr, output="sos")
    mix = sosfilt(sos, mix)
    mix = mix / max(1e-4, np.abs(mix).max()) * 0.6
    sf.write(OUT / f"{name}.wav", mix.astype(np.float32), sr)
    print(name, f"{secs:.0f}s", flush=True)


if __name__ == "__main__":
    for n in sys.argv[1:] or SETS:
        make(n, SETS[n])
