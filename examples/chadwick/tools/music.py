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
    "c_hook": COMMON + "Documentary cold open: New York, 1902, a Gilded Age con artist drops a forged two-million-dollar "
              "note signed by Andrew Carnegie outside his Fifth Avenue mansion. Hushed, intriguing and elegant, around 72 BPM: "
              "low pizzicato strings, a ticking clock-like celesta, a muted solo piano motif, soft sustained cello; sly and "
              "suspenseful, never loud.",
    "c_ontario": COMMON + "A poor railway family in a snowy small town in Ontario, Canada, in the 1860s and 1870s; a quiet, "
              "half-deaf girl who learns to forge letters. Sparse, wistful and slightly uneasy, around 68 BPM: solo fiddle and "
              "upright piano, soft harmonium, a little music-box figure; plain, cold and lonely with a hint of mischief.",
    "c_cleveland": COMMON + "Cleveland in the 1880s and 1890s: a fortune teller's candlelit parlour, false names, short "
              "marriages, prison and parole, a wealthy avenue of mansions that snubs her. Sly, playful-dark chamber "
              "underscore, around 80 BPM: a slow waltz on piano and clarinet, pizzicato strings, a soft bassoon; theatrical "
              "and a little sinister.",
    "c_con": COMMON + "The con: a lie whispered in a carriage, a sealed envelope locked in a bank vault, bankers lending "
              "fortunes against a receipt. Clever, building heist underscore, around 92 BPM: a repeating piano ostinato, "
              "pizzicato and staccato strings, light snare brushes, a low clarinet line; confident, intricate, quietly thrilling.",
    "c_queen": COMMON + "The Queen of Ohio, 1903: diamond necklaces, a gold pipe organ, lavish dinners under chandeliers "
              "in a Euclid Avenue mansion. Lush, gilded Gilded Age waltz, around 84 BPM: strings and harp, a gentle "
              "celesta, a warm piano melody; opulent and dreamlike with a faint unease underneath.",
    "c_fall": COMMON + "December 1904: a banker calls in his loan, Carnegie denies her, a run on a small-town bank, the "
              "envelope cut open, an arrest in a hotel, a trial. Tense, unravelling underscore, minor key, around 76 BPM: "
              "low strings, a slow pulsing piano, timpani rolls held very soft, a falling motif; tension and consequence.",
    "c_end": COMMON + "The quiet epilogue of a true story from 1907: an empty room, autumn leaves in a small Ontario town, "
              "a folded paper on a snowy city pavement. Reflective and bittersweet, around 60 BPM: solo piano and cello, soft "
              "strings that open up gently and settle; ending in stillness.",
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
