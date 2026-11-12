"""Depth maps for the film's pictures: one 16-bit PNG per image in build/depth/, in engine source px (1774 x 887, the
same crop film.up() makes), near = bright. fx3 (Focus, Snow, Rain, Haze) reads them. Run once per film, after the
images are checked:

    python tools/depth.py            every picture in incoming/02_scenes (skips the ones already done)
    python tools/depth.py S05a S05b  just these

Needs torch + transformers (the voice environment has them; elsewhere: pip install torch transformers) and the
Depth Anything V2 Small model (about 100 MB, Apache-2.0). It is used from the local Hugging Face cache when it is
there; otherwise the first run downloads it from huggingface.co, so ask the user before that first run.
"""
import os
import sys
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "build" / "depth"
MODEL = "depth-anything/Depth-Anything-V2-Small-hf"


def crop21(name):
    """The picture as the engine sees it: centre-cropped to 2:1 and scaled to 1774 x 887 (as film.up() does)."""
    for folder in ("02_scenes", "04_bases"):
        for e in (".png", ".jpg", ".jpeg", ".webp"):
            p = ROOT / "incoming" / folder / f"{name}{e}"
            if p.exists():
                im = Image.open(p).convert("RGB")
                w, h = im.size
                if abs(w / h - 2) > 0.01:
                    if w / h < 2:
                        c = round(w / 2); im = im.crop((0, (h - c) // 2, w, (h - c) // 2 + c))
                    else:
                        c = round(h * 2); im = im.crop(((w - c) // 2, 0, (w - c) // 2 + c, h))
                return im.resize((1774, 887), Image.LANCZOS)
    return None


def main(names):
    OUT.mkdir(parents=True, exist_ok=True)
    if not names:
        names = sorted(p.stem for p in (ROOT / "incoming" / "02_scenes").iterdir()
                       if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp") and not p.stem.endswith("_lines"))
    names = [n for n in names if not (OUT / f"{n}.png").exists() or "--redo" in sys.argv]
    if not names:
        print("depth: nothing to do"); return
    try:  # the cached model if there is one; a download only when there isn't
        proc = AutoImageProcessor.from_pretrained(MODEL, local_files_only=True)
        model = AutoModelForDepthEstimation.from_pretrained(MODEL, local_files_only=True).eval()
    except Exception:
        proc = AutoImageProcessor.from_pretrained(MODEL)
        model = AutoModelForDepthEstimation.from_pretrained(MODEL).eval()
    for n in names:
        im = crop21(n)
        if im is None:
            print("missing", n); continue
        with torch.no_grad():
            d = model(**proc(images=im, return_tensors="pt")).predicted_depth
        d = torch.nn.functional.interpolate(d[None], size=(887, 1774), mode="bicubic", align_corners=False)[0, 0].numpy()
        d = (d - d.min()) / (d.max() - d.min() + 1e-9)
        Image.fromarray((d * 65535).astype(np.uint16)).save(OUT / f"{n}.png")
        print("depth", n, flush=True)


if __name__ == "__main__":
    main([a for a in sys.argv[1:] if not a.startswith("--")])
