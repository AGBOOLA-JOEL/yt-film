"""Render the Caesar character and prop overlays on a portrait test canvas."""

import argparse
from pathlib import Path
import subprocess
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "engine"))
from character_popup import CharacterPopup

WIDTH, HEIGHT, FPS = 540, 960, 24


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="path for the preview MP4")
    args = parser.parse_args()
    if args.output.exists():
        parser.error(f"output already exists: {args.output}")

    art = HERE / "art"
    popups = [
        CharacterPopup(art / "cornelia.png", 0.2, 2.5, title="CORNELIA", subtitle="Caesar's wife",
                       pos=(0.5, 0.48), width=0.67, bounce=0.047),
        CharacterPopup(art / "coin_purse.png", 2.6, 4.5, title="RANSOM FUND", pos=(0.5, 0.48), width=0.67),
        CharacterPopup(art / "poetry_scroll.png", 4.6, 6.5, title="POETRY NIGHT", pos=(0.5, 0.48), width=0.67),
    ]
    background = np.empty((HEIGHT, WIDTH, 3), np.uint8)
    background[:] = (36, 49, 50)
    command = ["ffmpeg", "-n", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}",
               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(args.output)]
    with subprocess.Popen(command, stdin=subprocess.PIPE) as ffmpeg:
        for index in range(round(6.7 * FPS)):
            frame = background.copy()
            for popup in popups:
                popup(frame, index / FPS)
            ffmpeg.stdin.write(frame.tobytes())
        ffmpeg.stdin.close()
        if ffmpeg.wait():
            raise SystemExit("FFmpeg could not write the pop-up preview")
    print("wrote", args.output)


if __name__ == "__main__":
    main()
