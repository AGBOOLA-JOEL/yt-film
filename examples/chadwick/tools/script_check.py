"""Every image in incoming/ placed in SCRIPT.md? Scenes and bases by name; sheet drawings as Xnn.i (all four of each)."""
import re
from pathlib import Path
R = Path(__file__).resolve().parent.parent
s = (R / "SCRIPT.md").read_text(encoding="utf-8")
miss = []
for f in sorted((R / "incoming/02_scenes").glob("*.png")) + sorted((R / "incoming/04_bases").glob("*.png")):
    if f.stem not in s:
        miss.append(f.stem)
for f in sorted((R / "incoming/03_sheets").glob("X0?_*.png")):
    if f.stem.endswith("_lines"):
        continue
    x = f.stem[:3]
    for i in range(4):
        if f"{x}.{i}" not in s:
            miss.append(f"{x}.{i} ({f.stem})")
words = sum(len(re.sub(r"`[^`]*`", "", m).split()) for m in re.findall(r"^## [^\n]*\n(.*?)(?=^## |\Z)", s.split("\n---\n", 1)[1], re.S | re.M))
print(f"{words} words ≈ {words / 128:.1f} min at Orus 1.25x")
print("not placed:", miss or "none")
