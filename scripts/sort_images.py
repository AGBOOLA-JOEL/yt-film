"""Put downloaded images into a project under the right names (for anyone who generates images by hand: ChatGPT,
Google Flow / Whisk, Gemini app, Midjourney, Leonardo, Ideogram, Firefly, Krea...). Those tools save files with
random names; generate the images IN THE GUIDE'S ORDER, download each one as you go, then run this once per group.

    python scripts/sort_images.py <downloads folder> <project folder> --group 02_scenes --guide IMAGE_GUIDE.md
    python scripts/sort_images.py ~/Downloads ~/yt-film-projects/my_story --group 02_scenes --from S03a --dry-run
    python scripts/sort_images.py ~/Downloads ~/yt-film-projects/my_story --names S01a_street S01b_door ...

How it matches: the newest N images in the downloads folder (by the time they were saved, oldest first) are given
the next N names of that group from the guide's "Save as" column, in order. --from starts at a name (to continue a
group later); --since 30m only looks at files saved in the last 30 minutes (or 2h, 1d); --dry-run shows the plan.
Images are converted to PNG, kept at full size, and a contact sheet (renders/sorted_<group>.jpg) is written so you
can check every picture landed on the right name. Files already in the project are never overwritten (--replace to
allow). Supported: png, jpg, jpeg, webp, avif/heic if Pillow can read them on your system.
"""
import re
import sys
import time
from pathlib import Path

from PIL import Image, ImageDraw

EXT = (".png", ".jpg", ".jpeg", ".webp", ".avif", ".heic")
PREFIX = {"00_style": ("style",), "02_scenes": ("S",), "03_sheets": ("X",), "04_bases": ("B",)}


def guide_names(guide, group):
    """Filenames from the guide's tables ('Save as' column) and 'Save as `...`' lines, in order, for one group."""
    text = Path(guide).read_text(encoding="utf-8")
    names = []
    for m in re.finditer(r"`(?:\d\d_\w+/)?([A-Za-z0-9_\-]+)\.(?:png|jpg)`", text):
        n = m.group(1)
        if n not in names:
            names.append(n)
    if group == "01_cast":
        return [n for n in names if not re.match(r"^(S\d|X\d|B\d|style|ref_)", n)]
    pre = PREFIX.get(group)
    return [n for n in names if pre and n.startswith(pre) and (group != "02_scenes" or re.match(r"^S\d", n))]


def since(arg):
    m = re.match(r"(\d+)([mhd])", arg)
    return time.time() - int(m.group(1)) * {"m": 60, "h": 3600, "d": 86400}[m.group(2)]


def main():
    a = sys.argv[1:]
    if len(a) < 2 or "--help" in a:
        print(__doc__)
        sys.exit()
    src, proj = Path(a[0]).expanduser(), Path(a[1]).expanduser()
    group = a[a.index("--group") + 1] if "--group" in a else "02_scenes"
    if "--names" in a:
        names = [x for x in a[a.index("--names") + 1:] if not x.startswith("--")]
    else:
        guide = a[a.index("--guide") + 1] if "--guide" in a else proj / "IMAGE_GUIDE.md"
        names = guide_names(guide, group)
    if "--from" in a:
        start = a[a.index("--from") + 1]
        names = names[next(i for i, n in enumerate(names) if n.startswith(start)):]
    dest = proj / "incoming" / group
    dest.mkdir(parents=True, exist_ok=True)
    replace = "--replace" in a
    names = [n for n in names if replace or not any((dest / f"{n}{e}").exists() for e in (".png", ".jpg"))]
    t_min = since(a[a.index("--since") + 1]) if "--since" in a else 0
    files = sorted([f for f in src.iterdir() if f.suffix.lower() in EXT and f.stat().st_mtime >= t_min],
                   key=lambda f: f.stat().st_mtime)
    n = min(len(files), len(names))
    files = files[-n:] if n else []
    if not n:
        raise SystemExit(f"nothing to sort: {len(names)} names still missing in {group}, {len(files)} images found")
    print(f"{n} images -> {group} (still to make after this: {len(names) - n})")
    plan = list(zip(files, names[:n]))
    for f, name in plan:
        print(f"  {f.name:50s} -> {name}.png")
    if "--dry-run" in a:
        return
    tiles = []
    for f, name in plan:
        im = Image.open(f).convert("RGB")
        im.save(dest / f"{name}.png")
        t = im.copy()
        t.thumbnail((480, 270))
        d = ImageDraw.Draw(t)
        d.rectangle([0, 0, 480, 22], fill=(0, 0, 0))
        d.text((6, 4), name, fill=(255, 230, 0))
        tiles.append(t)
    cols = 4
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 480, rows * 270), (30, 30, 30))
    for i, t in enumerate(tiles):
        sheet.paste(t, ((i % cols) * 480, (i // cols) * 270))
    (proj / "renders").mkdir(exist_ok=True)
    out = proj / "renders" / f"sorted_{group}.jpg"
    sheet.save(out, quality=85)
    print("saved; check the names on", out)


if __name__ == "__main__":
    main()
