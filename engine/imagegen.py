"""Generate the film's images with the Gemini API (optional; for people without ChatGPT/Codex, or who want it
automatic). Reads IMAGE_PROMPTS.jsonl in the project (Claude writes it next to IMAGE_GUIDE.md when you choose the
API route), one image per line, and saves each straight into incoming/ under its exact name.

    python tools/imagegen.py                     every missing image, in order
    python tools/imagegen.py --only S01a S01b    just these (by name start)
    python tools/imagegen.py --redo S03c         make one again (the old one is kept as S03c.prev.png)
    python tools/imagegen.py --group 01_cast     only one folder
    python tools/imagegen.py --dry-run           show what would be sent

IMAGE_PROMPTS.jsonl, one JSON object per line:
    {"file": "00_style/style_card.png", "prompt": "...", "refs": []}
    {"file": "01_cast/anna.png", "prompt": "...", "refs": ["00_style/style_card.png"]}
    {"file": "02_scenes/S01a_street.png", "prompt": "...", "refs": ["00_style/style_card.png", "01_cast/anna.png"]}
    {"file": "02_scenes/S01c_anna_face.png", "prompt": "EDIT: ...", "refs": ["02_scenes/S01b_door.png", "01_cast/anna.png"]}
`refs` are attached as reference images (paths inside incoming/), which is what keeps the cast and style consistent:
always the style card, every named character's cast sheet, and for an EDIT the picture being edited.
An optional first line {"style": "..."} is put in front of every prompt (the opener: style, rules, no text).

Settings (.env): GEMINI_API_KEY, YTF_IMAGE_MODEL (default gemini-2.5-flash-image; check Google AI Studio for the newest
image model and its price), YTF_IMAGE_ASPECT (default 16:9). Paid per image on most plans: check before a full run.
"""
import base64
import json
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import ytf  # noqa: E402

INC = ROOT / "incoming"
MODEL = ytf.setting("YTF_IMAGE_MODEL", "gemini-2.5-flash-image")
ASPECT = ytf.setting("YTF_IMAGE_ASPECT", "16:9")
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}


def load_rows():
    f = ROOT / "IMAGE_PROMPTS.jsonl"
    if not f.exists():
        raise SystemExit("No IMAGE_PROMPTS.jsonl in the project. Ask Claude: \"write IMAGE_PROMPTS.jsonl for the API route\".")
    style, rows = "", []
    for line in f.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        r = json.loads(line)
        if "style" in r and "file" not in r:
            style = r["style"]
        else:
            rows.append(r)
    return style, rows


def ref_part(rel):
    p = INC / rel
    if not p.exists():
        for e in MIME:
            if p.with_suffix(e).exists():
                p = p.with_suffix(e)
                break
    if not p.exists():
        raise FileNotFoundError(f"reference {rel} isn't made yet: generate it first (the guide's order matters)")
    return {"inline_data": {"mime_type": MIME.get(p.suffix.lower(), "image/png"), "data": base64.b64encode(p.read_bytes()).decode()}}


def generate(style, row):
    parts = [ref_part(r) for r in row.get("refs", [])]
    text = (style + "\n\n" if style else "") + row["prompt"]
    if row.get("refs"):
        text += ("\n\nThe attached images are references: match the art style of the style card exactly, and draw every "
                 "named character exactly as on their character sheet.")
    parts.append({"text": text})
    body = {"contents": [{"parts": parts}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": row.get("aspect", ASPECT)}}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": ytf.gemini_key()})
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                d = json.loads(r.read())
            for c in d.get("candidates", []):
                for p in c.get("content", {}).get("parts", []):
                    data = p.get("inlineData") or p.get("inline_data")
                    if data:
                        return base64.b64decode(data["data"])
            raise RuntimeError(f"no image returned: {json.dumps(d)[:300]}")
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:300]
            if e.code in (429, 500, 503):
                print(f"    busy ({e.code}), waiting...", flush=True)
                time.sleep(20 * (attempt + 1))
                continue
            raise SystemExit(f"API error {e.code}: {msg}")
    raise SystemExit("gave up after 5 tries")


def main():
    a = sys.argv[1:]
    style, rows = load_rows()
    if "--group" in a:
        g = a[a.index("--group") + 1]
        rows = [r for r in rows if r["file"].startswith(g)]
    picks = [x for x in a[a.index("--only") + 1:] if not x.startswith("--")] if "--only" in a else None
    redo = [x for x in a[a.index("--redo") + 1:] if not x.startswith("--")] if "--redo" in a else []
    if picks or redo:
        rows = [r for r in rows if any(Path(r["file"]).stem.startswith(p) for p in (picks or []) + redo)]
    made = 0
    for r in rows:
        out = INC / r["file"]
        is_redo = any(Path(r["file"]).stem.startswith(p) for p in redo)
        if out.exists() and not is_redo:
            continue
        print(f"  {r['file']}  (refs: {', '.join(r.get('refs', [])) or 'none'})", flush=True)
        if "--dry-run" in a:
            continue
        out.parent.mkdir(parents=True, exist_ok=True)
        img = generate(style, r)
        if out.exists():
            out.replace(out.with_suffix(".prev" + out.suffix))
        out.write_bytes(img)
        made += 1
    print(f"done: {made} new images. Check them (hands, faces, era details) before writing the script.")


if __name__ == "__main__":
    main()
