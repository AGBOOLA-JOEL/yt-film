"""The film's look in code: everything the engine adds on top of your images (the grade, grain and vignette, the
colour of drawn lines, tags and paper scraps, the accent colour, the fonts, the drawing sound).

Pick a preset in the project's .env:

    YTF_LOOK=clean

and change any single value in `look.json` at the project root (it overrides the preset):

    {"accent": [20, 110, 220], "grain": 0, "type_font": "bold"}

See every preset and what each value does: `python tools/look.py` (and `python tools/look.py clean` for one).
The images themselves come from your image tool; their style is set by the image guide's opener
(references/art-styles.md has a matching opener for each preset).

Values:
  grain        film grain strength (0 = none; gouache 3.2)
  vignette     darkening at the corners (0 = none; gouache 0.13)
  warmth       -1 cool .. 0 neutral .. 1 warm highlights (gouache 1)
  contrast     strength of the soft S-curve (0 = flat; gouache 0.03, punchy 0.08)
  shadow_tint  how much the shadows lean blue (0 = none; gouache 5)
  saturation   1 = as painted, <1 duller, >1 richer
  ink          drawn lines and words on light areas (RGB)
  light        drawn lines and words on dark areas (RGB)
  accent       the "red pencil": circles, underlines, seals, stamps (RGB)
  paper        typed tags, pinned scraps, counters (RGB)
  type_font    font role for typed words: type | mono | bold | stamp | hand   (fonts in ytf.FONTS)
  hand_font    font role for handwriting: hand | type | bold
  ruled_tags   true: a ruled line along the top and bottom of each tag
  pen_db       the drawing sound against the voice (dB; gouache -27; null = silent)
"""
import json
import sys
from pathlib import Path

PRESETS = {
    "gouache": dict(
        about="The default: ink line and matte gouache, warm print grade, fine grain, cream paper, brown-black ink, red pencil, typewriter.",
        grain=3.2, vignette=0.13, warmth=1.0, contrast=0.03, shadow_tint=5.0, saturation=1.0,
        ink=(34, 27, 22), light=(246, 238, 220), accent=(190, 44, 36), paper=(242, 233, 210),
        type_font="type", hand_font="hand", ruled_tags=True, pen_db=-27),
    "clean": dict(
        about="Modern explainer: neutral colour, no grain or vignette, white tags, near-black ink, blue accent, clean sans-serif.",
        grain=0.0, vignette=0.0, warmth=0.0, contrast=0.02, shadow_tint=0.0, saturation=1.05,
        ink=(24, 26, 32), light=(250, 250, 252), accent=(24, 112, 230), paper=(252, 252, 250),
        type_font="bold", hand_font="hand", ruled_tags=False, pen_db=-30),
    "noir": dict(
        about="Ink wash / crime: near-monochrome, hard contrast, heavier grain and corners, grey-white paper, red accent.",
        grain=5.0, vignette=0.24, warmth=-0.2, contrast=0.11, shadow_tint=2.0, saturation=0.25,
        ink=(16, 16, 18), light=(236, 234, 228), accent=(200, 30, 30), paper=(226, 224, 218),
        type_font="mono", hand_font="hand", ruled_tags=True, pen_db=-27),
    "chalk": dict(
        about="Classroom chalkboard: for dark images; chalk-white lines, yellow chalk accent, handwritten labels.",
        grain=2.0, vignette=0.10, warmth=0.2, contrast=0.03, shadow_tint=0.0, saturation=0.95,
        ink=(36, 40, 38), light=(242, 240, 232), accent=(246, 206, 70), paper=(48, 58, 54),
        type_font="hand", hand_font="hand", ruled_tags=False, pen_db=-26),
    "comic": dict(
        about="Bright comic / ligne claire: rich colour, no grain, black ink, yellow-red accent, bold stamp lettering.",
        grain=0.0, vignette=0.05, warmth=0.3, contrast=0.05, shadow_tint=0.0, saturation=1.18,
        ink=(14, 14, 16), light=(255, 255, 250), accent=(232, 60, 30), paper=(255, 244, 196),
        type_font="stamp", hand_font="hand", ruled_tags=False, pen_db=-30),
    "storybook": dict(
        about="Children's book / soft watercolour: light warm grade, faint grain, blue-grey ink, coral accent, handwriting.",
        grain=1.4, vignette=0.08, warmth=0.6, contrast=0.015, shadow_tint=3.0, saturation=1.0,
        ink=(48, 58, 82), light=(252, 248, 238), accent=(226, 96, 80), paper=(250, 244, 230),
        type_font="hand", hand_font="hand", ruled_tags=False, pen_db=-29),
    "blueprint": dict(
        about="Engineering / how-it-works: for blue technical images; white lines, orange accent, monospace labels.",
        grain=1.0, vignette=0.10, warmth=-0.5, contrast=0.03, shadow_tint=6.0, saturation=1.0,
        ink=(18, 40, 72), light=(240, 246, 252), accent=(255, 150, 40), paper=(28, 64, 112),
        type_font="mono", hand_font="mono", ruled_tags=False, pen_db=-30),
}
KEYS = set(PRESETS["gouache"]) - {"about"}


def _load():
    import ytf  # noqa: E402  (the engine's settings: .env of the project, then the repo)
    name = (ytf.setting("YTF_LOOK") or "gouache").strip().lower()
    if name not in PRESETS:
        print(f"look: unknown YTF_LOOK={name!r}, using gouache (choose from {', '.join(PRESETS)})", file=sys.stderr)
        name = "gouache"
    v = dict(PRESETS[name], name=name)
    f = Path(__file__).resolve().parent.parent / "look.json"  # the project root (the engine lives in <project>/tools)
    if f.exists():
        extra = json.loads(f.read_text(encoding="utf-8"))
        bad = set(extra) - KEYS
        if bad:
            print(f"look.json: unknown keys {sorted(bad)} (known: {sorted(KEYS)})", file=sys.stderr)
        v.update({k: (tuple(x) if isinstance(x, list) else x) for k, x in extra.items() if k in KEYS})
        v["name"] = name + " + look.json"
    return v


class _Look(dict):
    __getattr__ = dict.__getitem__


L = _Look(_load())


def rgb(key):
    return tuple(int(c) for c in L[key])


def lum(c):
    return 0.3 * c[0] + 0.59 * c[1] + 0.11 * c[2]


def on_paper():
    """The colour for words typed on the look's paper: ink on light paper, the light colour on dark paper."""
    return rgb("ink") if lum(L["paper"]) > 128 else rgb("light")


def dark():
    """A dark colour for halos behind light lines: the ink if it is dark, else near-black."""
    return rgb("ink") if lum(L["ink"]) < 90 else (20, 16, 12)


if __name__ == "__main__":
    pick = [a for a in sys.argv[1:] if not a.startswith("-")]
    for n, p in PRESETS.items():
        if pick and n not in pick:
            continue
        print(f"{n:10s} {p['about']}")
        if pick:
            for k in sorted(KEYS):
                print(f"    {k:12s} {p[k]}")
    print(f"\nthis project uses: {L['name']}")
