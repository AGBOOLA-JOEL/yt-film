"""Stills from a finished video at given times, two per row, time stamped (to check a render without watching it).

    python scripts/video_stills.py renders/b3.mp4 renders/b3_check.jpg 4 12.5 30 61
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

vid, out = sys.argv[1], sys.argv[2]
ts = [float(x) for x in sys.argv[3:]]
ims = []
with tempfile.TemporaryDirectory() as d:
    f = str(Path(d) / "f.png")
    for t in ts:
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(t), "-i", vid, "-frames:v", "1", f], check=True)
        a = cv2.imread(f)
        cv2.putText(a, str(t), (10, 40), 0, 1.2, (0, 255, 255), 3)
        ims.append(cv2.resize(a, (640, 360)))
while len(ims) % 2:
    ims.append(np.zeros_like(ims[0]))
cv2.imwrite(out, np.vstack([np.hstack(ims[i:i + 2]) for i in range(0, len(ims), 2)]))
print("wrote", out)
