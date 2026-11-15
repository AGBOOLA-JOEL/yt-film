"""Stills from a finished video at given times, two per row, time stamped (to check a render without watching it).

    python scripts/video_stills.py renders/b3.mp4 renders/b3_check.jpg 4 12.5 30 61
"""
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

def thumbnail(frame, timestamp):
    height, width = frame.shape[:2]
    box_width, box_height = (360, 640) if height > width else (640, 360)
    scale = min(box_width / width, box_height / height)
    size = (max(1, round(width * scale)), max(1, round(height * scale)))
    image = cv2.resize(frame, size, interpolation=cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR)
    tile = np.zeros((box_height, box_width, 3), dtype=np.uint8)
    x, y = (box_width - size[0]) // 2, (box_height - size[1]) // 2
    tile[y:y + size[1], x:x + size[0]] = image
    cv2.putText(tile, f"{timestamp:g}s", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    return tile


def main():
    if len(sys.argv) < 4:
        raise SystemExit("usage: video_stills.py VIDEO OUTPUT TIME [TIME ...]")
    video, output = sys.argv[1:3]
    timestamps = [float(value) for value in sys.argv[3:]]
    images = []
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "frame.png"
        for timestamp in timestamps:
            path.unlink(missing_ok=True)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(timestamp), "-i", video,
                            "-frames:v", "1", str(path)], check=True)
            if not path.is_file():
                raise SystemExit(f"no frame at {timestamp:g}s")
            frame = cv2.imread(str(path))
            if frame is None:
                raise SystemExit(f"could not read the frame at {timestamp:g}s")
            images.append(thumbnail(frame, timestamp))
    if len(images) % 2:
        images.append(np.zeros_like(images[0]))
    sheet = np.vstack([np.hstack(images[i:i + 2]) for i in range(0, len(images), 2)])
    if not cv2.imwrite(output, sheet):
        raise SystemExit(f"could not write {output}")
    print("wrote", output)


if __name__ == "__main__":
    main()
