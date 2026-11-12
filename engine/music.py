"""Score: instrumental cues generated with Google Lyria (Gemini API) -> audio/music/<cue>.mp3.
One cue per story section (5-7 per film). Generated for your film, so no third-party copyright; Lyria output carries
Google's SynthID watermark. No Gemini key? Put any licensed / royalty-free / your own .mp3 files in audio/music/ with
the cue names used in final.py's MUSIC table (see references/music.md).

    python tools/music.py [cue ...]          (default: every cue; existing files are kept)
"""
import base64
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ytf  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audio" / "music"
OUT.mkdir(parents=True, exist_ok=True)
MODEL = ytf.setting("YTF_MUSIC_MODEL", "lyria-3.5")   # check Google AI Studio for the current Lyria model name
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
COMMON = ("Instrumental only, no vocals, no choir. An underscore that sits under a spoken narration: plenty of space, "
          "no sudden loud hits, steady dynamics. About three minutes, ending with a natural fade. ")
# Describe the section's place, era and mood, the tempo and a few instruments. Lyria refuses prompts that mention
# death, prison, graves or violence: describe the mood and the place instead ("the quiet epilogue of a true story").
CUES = {
    "m_hook": COMMON + "Documentary cold open: <the strangest moment of your story, in one line>. Hushed and intriguing, "
              "around 72 BPM: low pizzicato strings, a soft piano motif, a sustained cello; suspenseful, never loud.",
    "m_rise": COMMON + "<the world of the story and how it begins>. Curious and building, around 84 BPM: a repeating "
              "piano ostinato, light strings, soft percussion.",
    "m_fall": COMMON + "<things unravel>. Tense, minor key, around 76 BPM: low strings, a slow pulsing piano, soft timpani.",
    "m_end": COMMON + "The quiet epilogue of a true story. Reflective and bittersweet, around 60 BPM: solo piano and "
             "cello, soft strings that open up gently and settle; ending in stillness.",
}


def gen(name, prompt):
    out = OUT / f"{name}.mp3"
    if out.exists():
        return f"{name}: exists"
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    req = urllib.request.Request(URL + "?fields=candidates(content(parts(text,inlineData)),finishReason)", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "x-goog-api-key": ytf.gemini_key()})
    with urllib.request.urlopen(req, timeout=300) as r:
        d = json.loads(r.read())
    parts = d["candidates"][0]["content"]["parts"]
    audio = [p["inlineData"]["data"] for p in parts if "inlineData" in p]
    out.write_bytes(base64.b64decode(audio[-1]))
    (OUT / f"{name}.prompt.txt").write_text(prompt + "\n\n" + "\n".join(p.get("text", "") for p in parts if "text" in p), encoding="utf-8")
    return f"{name}: {out.stat().st_size // 1024} KB"


if __name__ == "__main__":
    for n in sys.argv[1:] or CUES:
        print(gen(n, CUES[n]), flush=True)
