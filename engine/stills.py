"""Stills of a batch, without rendering: python tools/stills.py b3 [n=24] -> renders/stills_b3.jpg (time on each tile).
Also runs the readability check."""
import importlib.util
import sys
from pathlib import Path

import cv2
import numpy as np

sys.argv += ["--preview"] if "--full" not in sys.argv else []
HERE = Path(__file__).resolve().parent
name = sys.argv[1]
n = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 24
spec = importlib.util.spec_from_file_location("shots", HERE / f"shots_{name}.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
b = mod.b
b.check()
ts = [float(x) for x in sys.argv[3:] if x.replace(".", "").isdigit()] or list(np.linspace(0.6, b.end - 0.3, n))
tiles = []
for t in ts:
    a = cv2.cvtColor(np.clip(b.still(t), 0, 255).astype(np.uint8), cv2.COLOR_RGB2BGR)
    a = cv2.resize(a, (480, 270))
    cv2.putText(a, f"{t:.1f}", (6, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    tiles.append(a)
while len(tiles) % 4:
    tiles.append(np.zeros_like(tiles[0]))
out = HERE.parent / "renders" / f"stills_{name}.jpg"
out.parent.mkdir(exist_ok=True)
cv2.imwrite(str(out), np.vstack([np.hstack(tiles[i:i + 4]) for i in range(0, len(tiles), 4)]), [cv2.IMWRITE_JPEG_QUALITY, 85])
print("wrote", out)
