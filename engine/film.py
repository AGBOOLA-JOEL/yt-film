"""The yt-film engine: renders one batch from a shot list, cued to the narration's word timings.

A shot file (tools/shots_<batch>.py) builds `b = Batch("b1")`, adds shots at times taken from the voice with
`b.t("phrase")`, then calls `b.render()`. Shot kinds:
  scene   one image with an eased camera move (cx, cy, h in source px), optional acting swap (`swap=(t, image)`),
          live annotations drawn on top, and effects (fire, embers, rain, lightning, fireflies, snow, steam, glass,
          flashes, shake, crt, alarm glow)
  drawin  a scene that draws itself: its ink version inks on stroke by stroke, then the paint floods in
  page    a real object from the story (field notebook, blackboard, washi...) drawn on live in its own medium
          (pencil graphite, chalk, sumi brush ink): code drawings (maps, contours, hatching, landscapes) and drawings
          lifted from a sketch sheet's line version, see `Page`
  paper   a sketchbook page drawn live (maps, labels, arrows), see `paper_*` builders
Sound: narration + Lyria score (ducked under the voice) + synthesised effects and the drawing tool's own sound, which
follows the tool's real speed, is shaped per tool and sits well under the voice (it dips further while the narrator talks).
Annotations default to colour "auto": cream on dark parts of the image, ink on light parts, so a line is never lost
against the picture; red stays red but gets a cream halo where the picture under it is dark.
Images that are not 2:1 are centre-cropped to 2:1. Sketch sheets are scaled and padded onto the canvas.

    python tools/shots_b1.py [--preview]        (or: python tools/render_all.py b1 b2 ...)
"""
import json
import math
import re
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage, signal

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))  # sketch.py and stages.py sit beside this file
import sketch as sk  # noqa: E402  (pen strokes, handwriting, tool sprites)
import stages  # noqa: E402  (drawing order of an ink image)
import ytf  # noqa: E402  (portable paths, fonts, settings)

PREVIEW = "--preview" in sys.argv
OW, OH = (960, 540) if PREVIEW else (1920, 1080)
FPS = 12 if PREVIEW else 24
SW, SH = 1774, 887  # source image size
UP = 2  # working images are upscaled 2x
INC, BUILD = ROOT / "incoming", ROOT / "build"
COL = dict(ink=(34, 27, 22), red=(190, 44, 36), cream=(246, 238, 220), redh=(190, 44, 36), inkh=(34, 27, 22), creamh=(246, 238, 220))
HALO = dict(redh=(246, 238, 220), inkh=(246, 238, 220), creamh=(20, 16, 12))  # layers drawn over a soft contrasting halo
DARK = 133  # mean luminance below which a mark counts as sitting on a dark area
RNG = np.random.default_rng(5)
MUSIC_DB, DUCK_DB = -25, -9  # score vs the voice overall, and a further dip while he talks: the voice always leads


IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")  # any of these; PNG wins when two exist


def _first(folder, name):
    for e in IMG_EXT:
        p = folder / f"{name}{e}"
        if p.exists():
            return p
    return None


def find_img(name):
    for d in (INC / "02_scenes", INC / "04_bases", BUILD / "edit"):
        p = _first(d, name)
        if p:
            return p
    p = _first(INC / "03_sheets", name)
    if p:
        return norm_sheet(p)
    raise FileNotFoundError(f"{name}: no image called {name}.png/.jpg in incoming/02_scenes, 04_bases, 03_sheets or build/edit")


def norm_sheet(p):
    """A sketch sheet of any shape, scaled to the canvas width and padded with its own paper colour to SW x SH."""
    f = BUILD / "norm" / (p.stem + ".png")
    if f.exists() and f.stat().st_mtime >= p.stat().st_mtime:
        return f
    f.parent.mkdir(parents=True, exist_ok=True)
    a = cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB)
    s_ = min(SH * 16 / 9 * 0.94 / a.shape[1], SH / a.shape[0])  # fits a 16:9 frame whole, so a full view crops nothing
    a = cv2.resize(a, (round(a.shape[1] * s_), round(a.shape[0] * s_)), interpolation=cv2.INTER_AREA)
    edge = np.concatenate([a[:4].reshape(-1, 3), a[-4:].reshape(-1, 3), a[:, :4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)])
    out = np.empty((SH, SW, 3), np.uint8)
    out[:] = np.median(edge, 0).astype(np.uint8)
    y0, x0 = (SH - a.shape[0]) // 2, (SW - a.shape[1]) // 2
    out[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    cv2.imwrite(str(f), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    return f


_cache = {}


def up(name):
    """Source image upscaled 2x (Lanczos + light sharpen, then a touch of blur so camera moves don't shimmer)."""
    if name in _cache:
        return _cache[name]
    f = BUILD / "up" / f"{name}.png"
    if not f.exists() or f.stat().st_mtime < find_img(name).stat().st_mtime:  # rebuilt when an image is replaced
        f.parent.mkdir(parents=True, exist_ok=True)
        a = cv2.cvtColor(cv2.imread(str(find_img(name))), cv2.COLOR_BGR2RGB)
        h, w = a.shape[:2]
        if abs(w / h - SW / SH) > 0.01:  # not 2:1: centre-crop rather than stretch
            if w / h < SW / SH:
                c = round(w * SH / SW); a = a[(h - c) // 2:(h - c) // 2 + c]
            else:
                c = round(h * SW / SH); a = a[:, (w - c) // 2:(w - c) // 2 + c]
        b = cv2.resize(a, (SW * UP, SH * UP), interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
        b = np.clip(b + 0.35 * (b - cv2.GaussianBlur(b, (0, 0), 1.4)), 0, 255)
        cv2.imwrite(str(f), cv2.cvtColor(b.astype(np.uint8), cv2.COLOR_RGB2BGR))
    a = cv2.cvtColor(cv2.imread(str(f)), cv2.COLOR_BGR2RGB)
    a = cv2.GaussianBlur(a, (0, 0), 0.45)
    _cache[name] = a
    if len(_cache) > 8:
        _cache.pop(next(iter(_cache)))
    return a


def ease(u, kind="io"):
    u = min(1.0, max(0.0, u))
    if kind == "lin":
        return u
    if kind == "out":
        return 1 - (1 - u) ** 3
    if kind == "in":
        return u ** 3
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- annotations (drawn on top of an image)


TYPE_FONT = ytf.font("type")


class LineText(sk.Text):
    """Words whose baseline runs along a line from a towards b (2x px), as if written or typed on that line of the
    page in the picture. typed=True: typewriter letters that appear one at a time, with no pen."""

    def __init__(self, text, a, b, size, layer, t0, dur, tool="pen", typed=False, lift=3):
        font = ImageFont.truetype(TYPE_FONT if typed else sk.HAND, int(size))
        asc, desc = font.getmetrics()
        w = int(font.getlength(text)) + 20
        m = Image.new("L", (w, asc + desc + 20))
        ImageDraw.Draw(m).text((10, 10), text, font=font, fill=255)
        a, b = np.asarray(a, float), np.asarray(b, float)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        th = -math.degrees(ang)  # PIL turns counter-clockwise on screen
        r = m.rotate(th, expand=True, resample=Image.BICUBIC)
        c, s_ = math.cos(math.radians(th)), math.sin(math.radians(th))
        p = np.array([10.0, 10.0 + asc]) - np.array(m.size) / 2  # the baseline's left end, from the centre
        q = np.array(r.size) / 2 + np.array([c * p[0] + s_ * p[1], -s_ * p[0] + c * p[1]])
        n = np.array([math.sin(ang), -math.cos(ang)])  # "up" from the line
        org = a + n * lift - q
        self.m, self.x, self.y = r, int(round(org[0])), int(round(org[1]))
        self.layer, self.t0, self.dur, self.tool, self.done = layer, t0, dur, "type" if typed else tool, 0
        self.cols = np.flatnonzero(np.asarray(r).max(0) > 0)
        self.typed, self.n = typed, max(1, len(text))

    def frac(self, t):
        u = min(1.0, max(0.0, (t - self.t0) / self.dur))
        return math.floor(u * self.n) / self.n if self.typed and u < 1 else u  # one key at a time


class Marks:
    """Live drawings on a shot, in source px; rendered into 2x layers so they move with the camera."""

    def __init__(self):
        self.items = []

    def text(self, s, xy, size, t0, dur, color="auto", angle=0):
        it = sk.Text(s, np.array(xy) * UP, size * UP, color, t0, dur, tool="red" if color == "red" else "pen", angle=angle)
        self.items.append(it)

    def write(self, s, a, b, t0, dur, size=None, color="auto", typed=False):
        """Words sitting on a line of the picture (a notebook rule, a printed row): baseline from a towards b, at its
        angle; size fits the line's length unless given."""
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        if size is None:
            size = min(56, 0.92 * L / max(1, len(s)) / (0.56 if typed else 0.5))
        self.items.append(LineText(s, np.array(a) * UP, np.array(b) * UP, size * UP, color, t0, dur,
                                   tool="red" if color == "red" else "pen", typed=typed))

    def typed(self, s, xy, size, t0, dur=None, color="auto"):
        """A level typewriter label (dates, places, names): xy = left end of its baseline's middle height."""
        x, y = xy
        dur = dur or min(1.3, 0.1 + 0.05 * len(s))
        self.write(s, (x, y + size * 0.35), (x + 100, y + size * 0.35), t0, dur, size=size * 0.85, color=color, typed=True)

    def stroke(self, pts, t0, dur, color="auto", width=4.0, ease_=0.4):
        p = sk.resample(np.array(pts, float) * UP, 5)
        self.items.append(sk.Stroke(sk.wobble(p, 1.6, 6), color, width * UP, t0, dur, "red" if color == "red" else "pen", ease_))

    def circle(self, c, rx, ry, t0, dur, color="red", width=4.0):
        for s_ in sk.loop(np.array(c) * UP, rx * UP, ry * UP, t0, dur, layer=color, width=width * UP):
            s_.tool = "red" if color == "red" else "pen"
            self.items.append(s_)

    def arrow(self, a, b, t0, dur, color="red", width=4.0, bend=0.18):
        for s_ in sk.arrow(np.array(a) * UP, np.array(b) * UP, t0, dur, layer=color, width=width * UP, bend=bend,
                           tool="red" if color == "red" else "pen"):
            self.items.append(s_)

    def scribble(self, c, r, t0, dur, color="red", width=4.0):
        """Impact marks: a few quick radiating dashes around a point."""
        n = 7
        for k in range(n):
            a = -math.pi * 0.95 + k * math.pi * 0.95 / (n - 1) + RNG.normal(0, 0.06)
            p0 = np.array(c) + r * np.array([math.cos(a), math.sin(a)])
            p1 = np.array(c) + r * 1.55 * np.array([math.cos(a), math.sin(a)])
            self.stroke([p0, p1], t0 + k * dur / n, dur / n * 0.8, color, width, 0.2)


def resolve_colors(items, bg2x):
    """Give every "auto" mark the colour that stands out from the picture under it; halo red on dark areas."""
    lum = cv2.GaussianBlur(cv2.cvtColor(bg2x, cv2.COLOR_RGB2GRAY).astype(np.float32), (0, 0), 10)
    H, W = lum.shape
    for it in items:
        if it.layer not in ("auto", "red"):
            continue
        if isinstance(it, sk.Text):
            ys, xs = np.nonzero(np.asarray(it.m)[::6, ::6])
            pts = np.stack([it.x + xs * 6, it.y + ys * 6], 1) if len(xs) else np.array([[it.x, it.y]])
        else:
            pts = it.p[::3]
        xi = np.clip(pts[:, 0].astype(int), 0, W - 1)
        yi = np.clip(pts[:, 1].astype(int), 0, H - 1)
        samples = lum[yi, xi]
        v = float(np.percentile(samples, 40))
        spread = float(np.percentile(samples, 90) - np.percentile(samples, 10))  # a mark crossing dark and light areas
        if it.layer == "auto":
            it.layer = "cream" if v < DARK else "ink"
            if 95 < v < 175 or spread > 90:  # mid-tones or mixed ground: neither colour stands out alone, so add a halo
                it.layer += "h"
        elif v < 110 or spread > 90:
            it.layer = "redh"


class Layers:
    def __init__(self, items, fade=None):
        self.items = sorted(items, key=lambda i: i.t0)
        self.L = {k: Image.new("L", (SW * UP, SH * UP)) for k in COL}
        self.D = {k: ImageDraw.Draw(v) for k, v in self.L.items()}
        self.fade = fade or {}

    def update(self, t):
        active = None
        for it in self.items:
            if it.t0 <= t:
                it.draw(t, self.L if isinstance(it, sk.Text) else self.D)
                if t <= it.t0 + it.dur + 0.02:
                    active = it
        return active


# ---------------------------------------------------------------- effects (screen space)


class Snow:
    def __init__(self, n=420, seed=1):
        r = np.random.default_rng(seed)
        self.x, self.y = r.uniform(0, 1, n), r.uniform(0, 1, n)
        self.z = r.uniform(0.3, 1.0, n) ** 2  # depth: near flakes are big, fast, soft
        self.ph = r.uniform(0, 6.28, n)

    def draw(self, img, t, amount=1.0):
        sc = OW / 1920
        ov = np.zeros(img.shape[:2], np.float32)
        y = (self.y + t * (0.035 + 0.11 * self.z)) % 1.0
        x = (self.x + 0.012 * np.sin(t * 0.9 + self.ph) + t * 0.004) % 1.0
        n = int(len(self.x) * amount)
        for i in range(n):
            r = (1.0 + 3.2 * self.z[i]) * sc
            cv2.circle(ov, (int(x[i] * OW), int(y[i] * OH)), max(1, int(round(r))), 0.55 + 0.45 * float(self.z[i]), -1, cv2.LINE_AA)
        ov = cv2.GaussianBlur(ov, (0, 0), 0.8 * sc)
        a = np.clip(ov, 0, 1)[..., None] * 0.85
        return img * (1 - a) + np.array([238, 240, 246], np.float32) * a


def glass(img, t, t0, p, seed=3):
    """Shards bursting inward from a screen point p over 0.8 s."""
    u = t - t0
    if not 0 <= u <= 0.9:
        return img
    r = np.random.default_rng(seed)
    n = 70
    ang = r.uniform(-math.pi * 0.2, math.pi * 1.2, n)
    sp = r.uniform(250, 900, n) * OW / 1920
    ov = np.zeros(img.shape[:2], np.float32)
    for i in range(n):
        x = p[0] + math.cos(ang[i]) * sp[i] * u
        y = p[1] + math.sin(ang[i]) * sp[i] * u + 900 * u * u * OW / 1920
        s = r.uniform(3, 11) * OW / 1920
        rot = ang[i] + u * r.uniform(-12, 12)
        pts = np.array([[x + s * math.cos(rot + k * 2.1), y + s * math.sin(rot + k * 2.1) * 0.6] for k in range(3)], np.int32)
        cv2.fillConvexPoly(ov, pts, 1.0, cv2.LINE_AA)
    a = (np.clip(ov, 0, 1) * (1 - u / 0.9) * 0.9)[..., None]
    return img * (1 - a) + np.array([225, 235, 240], np.float32) * a


def glow(img, p, radius, color, amount):
    if amount <= 0:
        return img
    yy, xx = np.ogrid[:OH, :OW]
    g = np.exp(-(((xx - p[0]) ** 2 + (yy - p[1]) ** 2) / (2 * radius ** 2))).astype(np.float32)
    a = (g * amount)[..., None]
    return img + (np.array(color, np.float32) - img * 0.3) * a


def steam(img, t, p, seed=4, scale=1.0):
    r = np.random.default_rng(seed)
    ov = np.zeros(img.shape[:2], np.float32)
    for i in range(14):
        ph = (t * 0.55 + i / 14) % 1.0
        x = p[0] - ph * 120 * scale + 18 * math.sin(i * 1.7 + t * 2)
        y = p[1] - ph * 70 * scale
        cv2.circle(ov, (int(x), int(y)), int((10 + 55 * ph) * scale), float(0.35 * (1 - ph) * (ph * 4 if ph < 0.25 else 1)), -1, cv2.LINE_AA)
    ov = cv2.GaussianBlur(ov, (0, 0), 14 * scale)
    a = np.clip(ov, 0, 0.6)[..., None]
    return img * (1 - a) + np.array([200, 205, 212], np.float32) * a


def crt(img, rect, t):
    x0, y0, x1, y1 = [int(v) for v in rect]
    x0, y0, x1, y1 = max(0, x0), max(0, y0), min(OW, x1), min(OH, y1)
    if x1 <= x0 or y1 <= y0:
        return img
    reg = img[y0:y1, x0:x1]
    h = y1 - y0
    yy = np.arange(h, dtype=np.float32)[:, None]
    lines = 1 - 0.1 * (np.sin(yy * math.pi / max(2, 3 * OW / 1920)) ** 2)
    band = 1 + 0.07 * np.exp(-(((yy / h - (t * 0.35) % 1.3 + 0.15) / 0.06) ** 2))
    noise = 1 + 0.06 * np.random.default_rng(int(t * 24)).standard_normal(reg.shape[:2]).astype(np.float32)[..., None]
    img[y0:y1, x0:x1] = reg * (lines * band)[..., None] * noise
    return img


def flicker(t, seed=0):
    """A fire's brightness, 0.75..1.15: a slow breath, a quicker waver and the odd sharp flare."""
    v = 0.5 * math.sin(t * 2.3 + seed) + 0.3 * math.sin(t * 5.9 + seed * 2) + 0.2 * math.sin(t * 13.7 + seed * 3)
    return 0.95 + 0.14 * v + 0.06 * max(0.0, math.sin(t * 1.1 + seed)) ** 8


def firelight(img, t, p, radius, amount=0.35):
    """Warm light that breathes over everything near the fire (multiplies the picture, so dark stays dark)."""
    yy, xx = np.ogrid[:OH, :OW]
    f = flicker(t)
    jx, jy = 6 * math.sin(t * 7.1) * OW / 1920, 4 * math.sin(t * 5.3) * OW / 1920  # the flames move
    g = np.exp(-(((xx - p[0] - jx) ** 2 + (yy - p[1] - jy) ** 2) / (2 * (radius * f) ** 2))).astype(np.float32)
    gain = 1 + amount * (f - 0.95) * 4 * g[..., None] * np.array([1.0, 0.75, 0.45], np.float32)
    return img * gain + g[..., None] * np.array([40, 18, 0], np.float32) * amount * (f - 0.6)


class Embers:
    """Sparks lifting off a fire, swaying, cooling from yellow to dull red and going out."""

    def __init__(self, n=40, seed=6):
        r = np.random.default_rng(seed)
        self.ph, self.life = r.uniform(0, 1, n), r.uniform(1.4, 3.0, n)
        self.dx, self.sw = r.normal(0, 1, n), r.uniform(0, 6.28, n)
        self.sz = r.uniform(0.8, 2.2, n)

    def draw(self, img, t, p, scale=1.0):
        ov = np.zeros(img.shape, np.float32)
        for i in range(len(self.ph)):
            u = (t / self.life[i] + self.ph[i]) % 1.0
            x = p[0] + (self.dx[i] * 30 * u + 14 * math.sin(t * 2.1 + self.sw[i]) * u) * scale
            y = p[1] - (u * 260 + 40 * u * u) * scale
            heat = 1 - u
            c = np.array([255, 120 + 120 * heat, 40 * heat], np.float32) * (heat ** 0.6)
            cv2.circle(ov, (int(x), int(y)), max(1, int(self.sz[i] * scale * 1.6)), c.tolist(), -1, cv2.LINE_AA)
        return img + cv2.GaussianBlur(ov, (0, 0), 1.2 * scale) * 1.4 + ov * 0.6


class Rain:
    """Falling streaks in three depths (near ones long, fast and soft), slanted by the wind."""

    def __init__(self, n=900, seed=8):
        r = np.random.default_rng(seed)
        self.x, self.y = r.uniform(0, 1.2, n), r.uniform(0, 1, n)
        self.z = r.choice([0.35, 0.6, 1.0], n, p=[0.5, 0.33, 0.17])

    def draw(self, img, t, amount=1.0, slant=0.12):
        sc = OW / 1920
        ov = np.zeros(img.shape[:2], np.float32)
        n = int(len(self.x) * amount)
        y = (self.y[:n] + t * (1.6 + 2.2 * self.z[:n])) % 1.0
        x = (self.x[:n] - y * slant) % 1.2 - 0.1
        L = (18 + 60 * self.z[:n]) * sc
        for i in range(n):
            x0, y0 = x[i] * OW, y[i] * OH
            cv2.line(ov, (int(x0), int(y0)), (int(x0 - L[i] * slant), int(y0 + L[i])), 0.25 + 0.45 * float(self.z[i]),
                     max(1, int(round((0.8 + 1.4 * self.z[i]) * sc))), cv2.LINE_AA)
        a = np.clip(cv2.GaussianBlur(ov, (0, 0), 0.7 * sc), 0, 1)[..., None] * 0.55
        return img * (1 - a) + np.array([205, 212, 220], np.float32) * a


def lightning(img, t, times):
    """A cold double flash: the whole picture jumps bright, flickers once, and falls back."""
    for tl in times:
        u = t - tl
        if 0 <= u < 0.6:
            k = 0.9 * math.exp(-u * 18) + 0.55 * math.exp(-max(0.0, u - 0.14) * 14) * (u > 0.14)
            img = img * (1 + 0.9 * k) + np.array([90, 100, 130], np.float32) * k
    return img


class Fireflies:
    def __init__(self, n=14, seed=12):
        r = np.random.default_rng(seed)
        self.p, self.ph, self.sp = r.uniform(0, 1, (n, 2)), r.uniform(0, 6.28, n), r.uniform(0.3, 0.8, n)

    def draw(self, img, t, box):
        x0, y0, x1, y1 = box
        ov = np.zeros(img.shape, np.float32)
        for i in range(len(self.ph)):
            x = x0 + (x1 - x0) * ((self.p[i, 0] + 0.03 * math.sin(t * self.sp[i] + self.ph[i])) % 1)
            y = y0 + (y1 - y0) * ((self.p[i, 1] + 0.04 * math.sin(t * self.sp[i] * 0.7 + self.ph[i] * 2)) % 1)
            on = max(0.0, math.sin(t * 1.3 * self.sp[i] + self.ph[i])) ** 3
            cv2.circle(ov, (int(x), int(y)), max(1, int(2 * OW / 1920)), (210 * on, 240 * on, 120 * on), -1, cv2.LINE_AA)
        return img + cv2.GaussianBlur(ov, (0, 0), 3 * OW / 1920) * 3 + ov


# ---------------------------------------------------------------- shots


class Shot:
    def __init__(self, t0, kind, **kw):
        self.t0, self.kind, self.kw = t0, kind, kw
        self.marks = kw.get("marks")
        self.layers = None

    def cam(self, t):
        """(cx, cy, h) at batch time t: keys are [(t, cx, cy, h), ...]; eased between keys."""
        keys = self.kw["cam"]
        if t <= keys[0][0]:
            v = list(keys[0][1:])
        else:
            for (ta, *a), (tb, *b) in zip(keys, keys[1:]):
                if t <= tb:
                    u = ease((t - ta) / max(1e-6, tb - ta), self.kw.get("ease", "io"))
                    v = [x + (y - x) * u for x, y in zip(a, b)]
                    break
            else:
                v = list(keys[-1][1:])
        dr = self.kw.get("drift", 1.0)
        v[0] += dr * (4 * math.sin(t * 0.6) + 2 * math.sin(t * 1.7))
        v[1] += dr * 3 * math.sin(t * 0.45 + 1)
        for (ts, amp) in self.kw.get("shake", []):
            u = t - ts
            if 0 <= u < 0.6:
                k = amp * math.exp(-u * 7)
                v[0] += k * math.sin(u * 61)
                v[1] += k * math.cos(u * 47)
        h = min(SH, v[2])
        w = h * 16 / 9
        v[0] = min(max(v[0], w / 2), SW - w / 2)
        v[1] = min(max(v[1], h / 2), SH - h / 2)
        return v[0], v[1], h

    def to_screen(self, p, cam):
        cx, cy, h = cam
        s = h / OH
        return ((p[0] - (cx - h * 8 / 9)) / s, (p[1] - (cy - h / 2)) / s)


def warp(img2x, cam, interp=cv2.INTER_LINEAR):
    cx, cy, h = cam
    s = UP * h / OH
    x0, y0 = UP * (cx - h * 8 / 9), UP * (cy - h / 2)
    M = np.float32([[s, 0, x0], [0, s, y0]])
    return cv2.warpAffine(img2x, M, (OW, OH), flags=interp | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)


def blurred_warp(a, s, t, cam):
    """warp(), with motion blur when the camera moves fast (a dive, a whip, a quick reframe): the frame is averaged
    over a 180-degree shutter. Slow drifts stay pin sharp and cost nothing extra."""
    c0, c1 = s.cam(t - 0.25 / FPS), s.cam(t + 0.25 / FPS)
    sc = OH / cam[2]
    speed = max(abs(c1[0] - c0[0]) * sc, abs(c1[1] - c0[1]) * sc, abs(c1[2] - c0[2]) / cam[2] * OW) * 2
    if speed < 5 * OW / 1920:
        return warp(a, cam).astype(np.float32)
    n = int(min(7, 2 + speed / (10 * OW / 1920)))
    acc = np.zeros((OH, OW, 3), np.float32)
    for k in range(n):
        u = k / (n - 1)
        acc += warp(a, tuple(x + (y - x) * u for x, y in zip(c0, c1)))
    return acc / n


def transition(tr, a, b, u):
    """Blend the outgoing frame a into the incoming b; u runs 0 -> 1. ("dissolve", secs), ("whip", secs, +1/-1)
    (both frames slide sideways under a strong horizontal blur), ("flash", secs) (a soft white bloom between)."""
    u = min(1.0, max(0.0, u))
    kind = tr[0]
    if kind == "whip":
        d = tr[2] if len(tr) > 2 else 1
        e = ease(u)
        k = int(max(1, math.sin(math.pi * u) * 0.22 * OW))
        out = np.empty_like(b)
        off = int(e * OW) * d
        sa = np.roll(a, -off, axis=1)
        sb = np.roll(b, -off + OW * d, axis=1)
        m = (np.arange(OW) < OW - int(e * OW)) if d > 0 else (np.arange(OW) >= int(e * OW))
        out[:] = np.where(m[None, :, None], sa, sb)
        return cv2.blur(out, (k, 1))
    if kind == "shatter":  # glass breaking away to the next shot (fx2.shatter)
        import fx2
        return fx2.shatter(a, b, u, tr)
    if kind == "flash":
        w = math.sin(math.pi * u)
        mix = a * (1 - ease(u)) + b * ease(u)
        return mix * (1 - w * 0.7) + 250 * w * 0.7
    return a * (1 - ease(u)) + b * ease(u)


class Finish:
    """The film's finish on every frame: a gentle grade (soft contrast, warm highlights, slightly cool lifted
    shadows, like printed gouache under a lamp), a fine moving film grain, and a soft vignette."""

    def __init__(self, grain=3.2, vig=0.13, seed=31):
        r = np.random.default_rng(seed)
        self.grain = [cv2.GaussianBlur(r.standard_normal((OH, OW)).astype(np.float32), (0, 0), 0.6 * OW / 1920) * grain * 1.6
                      for _ in range(6)]
        yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
        d = np.hypot((xx - OW / 2) / (OW / 2), (yy - OH / 2) / (OH / 2)) / 1.414
        self.vig = (1 - vig * np.clip((d - 0.35) / 0.65, 0, 1) ** 1.6)[..., None]
        x = np.arange(256, dtype=np.float32) / 255
        curve = x + 0.06 * np.sin(2 * np.pi * (x - 0.5)) * -1 * 0.5  # a soft S
        self.lut = np.stack([np.clip(curve * 255 * 1.012 + 1.5, 0, 255),           # R: a touch warm
                             np.clip(curve * 255 * 1.0 + 1.0, 0, 255),
                             np.clip(curve * 255 * 0.975 + 5.0 * (1 - x) ** 2, 0, 255)], 1).astype(np.float32)

    def __call__(self, img, fi):
        i = np.clip(img, 0, 255).astype(np.uint8)
        g = np.stack([self.lut[i[..., c], c] for c in range(3)], -1)
        lum = g.mean(2, keepdims=True) / 255
        g = g + self.grain[(fi // 2) % len(self.grain)][..., None] * (0.35 + 1.3 * lum * (1 - lum) * 2)
        return g * self.vig


class Batch:
    def __init__(self, name, tail=1.2):
        self.name = name
        d = json.loads((ROOT / "voice" / f"{name}_words.json").read_text(encoding="utf-8"))
        self.dur, self.words = d["duration"], d["words"]
        self.end = self.dur + tail
        self.shots, self.sfx, self.cursor, self.overlays = [], [], 0, []

    @staticmethod
    def _n(w):
        return re.sub(r"[^a-z0-9]", "", w.lower())

    def t(self, phrase, end=False):
        """Start (or end) time of the next occurrence of `phrase` after the previous match."""
        ws = [self._n(w) for w in phrase.split()]
        W = [self._n(w["w"]) for w in self.words]
        for i in range(self.cursor, len(W) - len(ws) + 1):
            if W[i:i + len(ws)] == ws:
                self.cursor = i + 1
                return self.words[i + len(ws) - 1]["e"] if end else self.words[i]["s"]
        raise KeyError(phrase)

    def p(self, pid):
        """Start time of passage pid (first spoken word); does not move the phrase cursor."""
        return next(w["s"] for w in self.words if w["p"] == pid)

    def scene(self, t0, img, cam, **kw):
        self.shots.append(Shot(t0, "scene", img=img, cam=cam, **kw))

    def drawin(self, t0, img, cam, ink, flood, **kw):
        self.shots.append(Shot(t0, "drawin", img=img, cam=cam, ink=ink, flood=flood, **kw))

    def paper(self, t0, build, **kw):
        self.shots.append(Shot(t0, "paper", build=build, **kw))

    def page(self, t0, page, cam, **kw):
        """A real object drawn on live (see `Page`); cam keys as for a scene, in the base image's source px."""
        self.shots.append(Shot(t0, "page", page=page, img=page.base, cam=cam, **kw))

    def sheet(self, t0, img, cam, windows, **kw):
        """A sketchbook sheet: each drawing (panel i) inks itself in (a, b), then its colour brushes in (b, c).
        windows = [(panel, a, b, c), ...]; panels not listed stay blank paper."""
        self.shots.append(Shot(t0, "sheet", img=img, cam=cam, windows=windows, **kw))

    def custom(self, t0, build, cam, img, **kw):
        """A shot drawn by an object with img2x(t) (2x source image) and pen(t) (e.g. signature.Comic)."""
        self.shots.append(Shot(t0, "custom", build=build, img=img, cam=cam, **kw))

    def panel(self, img, i):
        """(x0, y0, x1, y1) of drawing i on a sheet, in source px."""
        return panels(img)[i]

    def panel_cam(self, img, i, h=760):
        x0, y0, x1, y1 = panels(img)[i]
        return ((x0 + x1) / 2, (y0 + y1) / 2, h)

    def fx(self, kind, t0, t1=None, db=0.0, **kw):
        self.sfx.append(dict(kind=kind, t0=t0, t1=t1 if t1 is not None else t0 + 1, db=db, **kw))

    # ------------------------------------------------------------ frames

    def _shot_at(self, t):
        cur = None
        for s in self.shots:
            if s.t0 <= t:
                cur = s
        return cur

    def check(self, read=1.5, panel_hold=1.8, note_read=3.0, quiet=False):
        """Before rendering: list what viewers won't see or won't have time to read.
        - a mark (label, leader, number) partly outside the camera's view when it finishes or when the shot ends;
        - a mark that stays on screen less than `read` s after it's finished (the shot cuts too soon);
        - a footnote card (anything with .total() and .t_out) on screen less than its typing time + `note_read` s, or
          missing from a shot it spans;
        - a comic panel held less than `panel_hold` s after it's painted, before the next panel or the dive.
        Returns the list of problems (and prints them)."""
        shots = sorted(self.shots, key=lambda s: s.t0)
        out, cards = [], {}
        for i, s in enumerate(shots):
            end = shots[i + 1].t0 if i + 1 < len(shots) else self.end
            img = s.kw.get("img", s.kind)
            for it in (s.marks.items if s.marks is not None else []):
                if isinstance(it, sk.Text):
                    x0, y0 = it.x / UP, it.y / UP
                    x1, y1 = x0 + it.m.size[0] / UP, y0 + it.m.size[1] / UP
                else:
                    p = np.asarray(it.p) / UP
                    (x0, y0), (x1, y1) = p.min(0), p.max(0)
                done = it.t0 + it.dur
                is_text = isinstance(it, sk.Text)
                what = f"{'words' if is_text else 'line'} at ({x0:.0f},{y0:.0f})"
                if is_text and done + read > end:
                    out.append(f"{self.name} {img} {what}: on screen {max(0, end - done):.1f}s after it's drawn (< {read}s)")
                for t in sorted({min(max(done, s.t0), end - 0.05), end - 0.05}):
                    if s.kind == "paper":
                        break
                    cx, cy, h = s.cam(t)
                    w = h * 16 / 9
                    vx0, vy0, vx1, vy1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
                    area = max(1.0, (x1 - x0) * (y1 - y0))
                    inside = max(0, min(x1, vx1) - max(x0, vx0)) * max(0, min(y1, vy1) - max(y0, vy0))
                    if inside / area < (0.9 if is_text else 0.5):
                        out.append(f"{self.name} {img} {what}: {100 - 100 * inside / area:.0f}% out of frame at {t:.1f}s")
                        break
            if end - s.t0 < 1.2 and not s.kw.get("montage"):
                out.append(f"{self.name} {img}: on screen only {end - s.t0:.1f}s (faster than the voice; montage=True if meant)")
            for f in s.kw.get("post", []):
                if hasattr(f, "total") and hasattr(f, "t_out"):
                    cards.setdefault(id(f), [f, []])[1].append((s.t0, end))
            b = s.kw.get("build")
            if b is not None and hasattr(b, "panels"):
                ps = sorted(b.panels, key=lambda p: p["t"][0])
                for k, p in enumerate(ps):
                    nxt = ps[k + 1]["t"][0] if k + 1 < len(ps) else end
                    if nxt - p["t"][2] < panel_hold:
                        out.append(f"{self.name} comic panel {p['img']}: held {nxt - p['t'][2]:.1f}s after it's painted (< {panel_hold}s)")
        for f, t0_, t1_ in self.overlays:
            if hasattr(f, "total"):
                cards.setdefault(id(f), [f, [(0.0, self.end)]])
        for f, spans in cards.values():
            need = 0.8 + f.total() * 0.045 + note_read
            if f.t_out - f.t_in < need - 0.05:
                out.append(f"{self.name} footnote {f.n}: open {f.t_out - f.t_in:.1f}s, needs {need:.1f}s to type and read")
            t = f.t_in
            for a_, b_ in sorted(spans):
                if a_ > t + 0.05:
                    break
                t = max(t, b_)
            if t < f.t_out - 0.05:
                out.append(f"{self.name} footnote {f.n}: disappears at {t:.1f}s (a shot it spans doesn't carry it)")
        if not quiet:
            print("\n".join(out) if out else f"{self.name}: check ok")
        return out

    def overlay(self, f, t0, t1):
        """A frame-space effect over whatever shot is playing from t0 to t1 (a footnote card stays up across cuts)."""
        self.overlays.append((f, t0, t1))

    def still(self, t):
        """One finished frame at time t (for checking placement without a render)."""
        self.shots.sort(key=lambda s: s.t0)
        s = self._shot_at(t)
        if s.marks is not None:
            for it in s.marks.items:
                it.done = 0
            if s.kind in ("scene", "drawin", "sheet", "page", "custom"):
                resolve_colors(s.marks.items, up(s.kw["img"]))
            s.layers = Layers(s.marks.items)
        img, _ = self.frame(s, t, Snow())
        s.layers = None
        return Finish()(img, int(t * FPS))

    def render(self):
        self.shots.sort(key=lambda s: s.t0)
        bad = [p for p in self.check() if "words" in p or "footnote" in p or "comic" in p]
        if bad and "--force" not in sys.argv and not PREVIEW:
            raise SystemExit(f"{self.name}: {len(bad)} readability problems above; fix them (or --force to render anyway)")
        for s in self.shots:  # every typed label gets its keys
            for it in (s.marks.items if s.marks is not None else []):
                if getattr(it, "typed", False):
                    self.fx("type", it.t0, it.t0 + it.dur, db=-17)
        out = ROOT / "renders" / f"{self.name}{'_preview' if PREVIEW else ''}.mp4"
        out.parent.mkdir(exist_ok=True)
        silent = out.with_suffix(".silent.mp4")
        ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                               "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", ytf.x264_preset(),
                               "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
        sc = OW / 1920
        sprites = {k: sk.tool_sprite(k, 0.28 * sc) for k in ("pencil", "pen", "red", "brush")}  # small: it mustn't pull focus
        sprites["chalk"] = chalk_sprite(0.9 * sc)
        snow = Snow()
        pen_log = []
        prev = old = None
        fin = Finish()
        for fi in range(int(self.end * FPS)):
            t = fi / FPS
            s = self._shot_at(t)
            if s is not prev:
                if old is not None:
                    old.layers = None
                old = prev  # the outgoing shot stays alive while a transition blends it away
                if s.marks is not None:
                    if s.kind in ("scene", "drawin", "sheet", "page", "custom"):
                        resolve_colors(s.marks.items, up(s.kw["img"]))
                    s.layers = Layers(s.marks.items)
                prev = s
            img, pen = self.frame(s, t, snow)
            tr = s.kw.get("trans")
            if tr and old is not None and t < s.t0 + tr[1]:
                img = transition(tr, self.frame(old, t, snow)[0], img, (t - s.t0) / tr[1])
            elif old is not None:
                old.layers = None
                old = None
            if not s.kw.get("raw"):
                img = fin(img, fi)
            frame = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
            tool, p = None, None
            if pen is not None:
                tool, p, _ = pen
                spr, tip = sprites[tool]
                px, py = int(p[0] - tip[0]), int(p[1] - tip[1])
                lay = Image.new("RGBA", frame.size)
                lay.paste(spr, (px, py))
                frame = Image.alpha_composite(frame, lay)
            pen_log.append((tool, None if p is None else (float(p[0]), float(p[1]))))
            ff.stdin.write(frame.convert("RGB").tobytes())
            if fi % (FPS * 5) == 0:
                print(f"{t:6.1f}s / {self.end:.1f}", flush=True)
        ff.stdin.close()
        ff.wait()
        wav = out.with_suffix(".wav")
        self.mix(pen_log, wav)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                        "-b:a", "192k", "-shortest", str(out)], check=True)
        silent.unlink()
        print("wrote", out)

    def frame(self, s, t, snow):
        kw = s.kw
        if s.kind == "paper":
            return kw["build"].frame(t)
        cam = s.cam(t)
        sheet_pen = None
        if s.kind == "drawin":
            img = self._drawin(s, t, cam)
        elif s.kind == "sheet":
            img, sheet_pen = self._sheet(s, t, cam)
            sheet_pen = None if sheet_pen is None else ("pen", sheet_pen)
        elif s.kind == "page":
            img, sheet_pen = kw["page"].frame(t, cam)
        elif s.kind == "custom":
            a = kw["build"].img2x(t)
            img = blurred_warp(a, s, t, cam)
            sheet_pen = kw["build"].pen(t)
        else:
            src = kw["img"]
            sw = kw.get("swap")
            if sw and t >= sw[0]:
                src = sw[1]
            a = up(src)
            for f in kw.get("src_fx", []):  # living stills, acting faces (signature.py): on the 2x source
                a = f(a, t)
            img = blurred_warp(a, s, t, cam)
        pen = None
        if s.layers is not None:
            active = s.layers.update(t)
            for k, c in COL.items():
                a = warp(np.asarray(s.layers.L[k]), cam).astype(np.float32)[..., None] / 255
                if k in s.layers.fade:
                    a *= s.layers.fade[k](t)
                if k in HALO and a.max() > 0:
                    r = max(2, int(5 * OW / 1920))
                    h = cv2.GaussianBlur(cv2.dilate(a[..., 0], np.ones((2 * r + 1, 2 * r + 1), np.uint8)), (0, 0), r * 0.6)[..., None]
                    img = img * (1 - h * 0.75) + np.array(HALO[k], np.float32) * h * 0.75
                img = img * (1 - a * 0.92) + np.array(c, np.float32) * a * 0.92
            if active is not None and active.tool != "type":  # typed labels have no pen
                p = s.to_screen(np.array(active.pos(t)) / UP, cam)
                pen = (active.tool, p, 600.0)
        if pen is None and sheet_pen is not None:
            p = np.array(s.to_screen(sheet_pen[1], cam))
            prev_p = getattr(s, "_pen", None)
            s._pen = p if prev_p is None or np.hypot(*(p - prev_p)) > 400 * OW / 1920 else prev_p + (p - prev_p) * 0.35
            pen = (sheet_pen[0], tuple(s._pen), 600.0)
        elif sheet_pen is None:
            s._pen = None
        for e in kw.get("fx", []):
            k = e[0]
            if k == "snow":
                img = snow.draw(img, t, e[1])
            elif k == "glass" and t >= e[1]:
                img = glass(img, t, e[1], s.to_screen(e[2], cam))
            elif k == "flash":
                for (tf, p) in e[1]:
                    u = t - tf
                    if 0 <= u < 0.12:
                        img = glow(img, s.to_screen(p, cam), 70 * OW / 1920, (255, 255, 255), 1.6 * (1 - u / 0.12))
            elif k == "steam":
                if e[1] <= t <= e[2]:
                    img = steam(img, t, s.to_screen(e[3], cam), scale=OW / 1920 * 1.2)
            elif k == "crt":
                a, b_ = s.to_screen(e[1][:2], cam), s.to_screen(e[1][2:], cam)
                img = crt(img, (*a, *b_), t)
            elif k == "alarm":
                if e[1] <= t <= e[2]:
                    img = glow(img, s.to_screen(e[3], cam), 160 * OW / 1920, (255, 40, 30), 0.35 * (0.5 + 0.5 * math.sin(t * 14)))
            elif k == "fire":  # ("fire", p, radius, amount): firelight breathing over the picture
                img = firelight(img, t, s.to_screen(e[1], cam), e[2] / (cam[2] / OH), e[3] if len(e) > 3 else 0.35)
            elif k == "embers":  # ("embers", p)
                self._embers = getattr(self, "_embers", None) or Embers()
                img = self._embers.draw(img, t, s.to_screen(e[1], cam), OH / cam[2])
            elif k == "rain":  # ("rain", amount)
                self._rain = getattr(self, "_rain", None) or Rain()
                img = self._rain.draw(img, t, e[1])
            elif k == "lightning":  # ("lightning", [t, ...])
                img = lightning(img, t, e[1])
            elif k == "fireflies":  # ("fireflies", (x0, y0, x1, y1)) in source px
                self._ff = getattr(self, "_ff", None) or Fireflies()
                a, b_ = s.to_screen(e[1][:2], cam), s.to_screen(e[1][2:], cam)
                img = self._ff.draw(img, t, (*a, *b_))
            elif k == "fade_in":
                img = img * ease((t - s.t0) / e[1])
            elif k == "fade_out":  # ("fade_out", t_start, t_end)
                img = img * (1 - ease((t - e[1]) / max(1e-6, e[2] - e[1])))
        for f in kw.get("post", []):  # frame-space touches (signature.py): case-board dimming, the footnote hand
            img = f(img, t, s, cam)
        for f, t0_, t1_ in getattr(self, "overlays", []):  # footnote cards: above every shot they span
            if t0_ <= t <= t1_:
                img = f(img, t, s, cam)
        return img, pen

    # ------------------------------------------------------------ a scene that draws itself

    _din = {}

    def _drawin(self, s, t, cam):
        kw = s.kw
        key = kw["ink"]
        if key not in self._din:
            f = BUILD / f"order_{key}.npz"
            if f.exists():
                T = np.load(f)["T"]
            else:
                a = np.asarray(Image.open(find_img(key)).convert("L"), np.float32) / 255
                T, _ = stages.strokes(np.clip((0.97 - a) / 0.9, 0, 1), 0.22, (40, 10))
                yy, xx = np.mgrid[0:T.shape[0], 0:T.shape[1]]  # soft front with a hatch grain, not blocks
                T = (ndimage.gaussian_filter(T, 6) + 0.006 * np.sin((xx + yy) * 0.45)).astype(np.float32)
                np.savez_compressed(f, T=T)
            ink = 1 - cv2.cvtColor(up(key), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
            ink = np.clip((ink - 0.04) / 0.9, 0, 1)
            T2 = cv2.resize(T, (SW * UP, SH * UP), interpolation=cv2.INTER_LINEAR)
            h, w = T2.shape
            noise = cv2.resize(RNG.random((h // 64, w // 64)).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
            flood = 0.7 * (np.arange(w, dtype=np.float32)[None, :] / w) + 0.3 * noise
            self._din = {key: (ink, T2, flood)}
        ink, T2, flood = self._din[key]
        (a0, a1), (b0, b1) = kw["ink_t"], kw["flood_t"]
        rev = np.clip((t - (a0 + T2 * (a1 - a0))) / 0.06, 0, 1)
        paper = np.array([244, 239, 228], np.float32)
        base = paper[None, None] * (1 - (rev * ink)[..., None] * 0.9)
        wv = np.clip((t - (b0 + flood * (b1 - b0))) / 0.35, 0, 1)[..., None]
        img2x = base * (1 - wv) + up(kw["img"]).astype(np.float32) * wv
        return warp(img2x, cam)

    # ------------------------------------------------------------ a sketchbook sheet drawing itself, panel by panel

    _sh = {}

    def _sheet(self, s, t, cam):
        kw = s.kw
        name = kw["img"]
        key = (name, tuple(kw["windows"]))
        if key not in self._sh:
            order = sheet_order(name)
            H, W = SH, SW
            Ti = np.full((H, W), 1e6, np.float32)
            Tc = np.full((H, W), 1e6, np.float32)
            track = []
            for w_ in kw["windows"]:
                i, a, b_ = w_[:3]
                c0, c1 = (w_[3], w_[4]) if len(w_) == 5 else (b_, w_[3])  # colour may wait for its cue
                x0, y0, x1, y1 = panels(name)[i]
                T = order[f"T{i}"]
                Ti[y0:y1, x0:x1] = a + T * (b_ - a)
                fl = order[f"F{i}"]
                Tc[y0:y1, x0:x1] = c0 + fl * (c1 - c0)
                tr = order[f"K{i}"]
                track += [(a + tt * (b_ - a), x0 + x, y0 + y) for tt, x, y in tr]
            track.sort()
            Ti2 = cv2.resize(Ti, (W * UP, H * UP), interpolation=cv2.INTER_LINEAR)
            Tc2 = cv2.resize(Tc, (W * UP, H * UP), interpolation=cv2.INTER_LINEAR)
            ink = 1 - cv2.cvtColor(up(name + "_lines"), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
            ink = np.clip((ink - 0.04) / 0.9, 0, 1)
            self._sh = {key: (Ti2, Tc2, ink, np.array(track, np.float32), kw["windows"])}
        Ti2, Tc2, ink, track, wins = self._sh[key]
        rev = np.clip((t - Ti2) / 0.06, 0, 1)
        wv = np.clip((t - Tc2) / 0.3, 0, 1)[..., None]
        src = up(name)
        paper = np.median(np.concatenate([src[:8].reshape(-1, 3), src[-8:].reshape(-1, 3)]), 0).astype(np.float32)  # the sheet's own paper
        base = paper[None, None] * (1 - (rev * ink)[..., None] * 0.92)
        img2x = base * (1 - wv) + up(name).astype(np.float32) * wv
        pen = None
        if any(w_[1] <= t <= w_[2] for w_ in wins) and len(track):
            k = int(np.searchsorted(track[:, 0], t)) - 1
            if k >= 0:
                pen = (float(track[k, 1]), float(track[k, 2]))
        return warp(img2x, cam), pen

    # ------------------------------------------------------------ sound

    def mix(self, pen_log, path, sr=48000):
        n = int(self.end * sr)
        vo, vsr = _read(ROOT / "voice" / f"{self.name}_vo.wav")
        vo = _resample(vo, vsr, sr)[:n]
        voice = np.zeros(n, np.float32)
        voice[:len(vo)] = vo
        voice *= 0.5 / (np.percentile(np.abs(voice), 99.9) + 1e-9)
        mus = np.zeros(n, np.float32)
        cue = self.music if hasattr(self, "music") else None
        if cue:
            m = _decode(ROOT / "audio" / "music" / f"{cue[0]}.mp3", sr)
            m = m[int(cue[1] * sr):][:n]
            mus[:len(m)] = m
            fi, fo = int(1.5 * sr), int(2.5 * sr)
            mus[:fi] *= np.linspace(0, 1, fi)
            mus[n - fo:] *= np.linspace(1, 0, fo)
            venv = ndimage.uniform_filter1d(np.abs(voice), int(0.25 * sr))
            duck = 10 ** (DUCK_DB * np.clip(venv / (np.percentile(venv, 95) * 0.25), 0, 1) / 20)
            mus = mus / (np.sqrt(np.mean(mus ** 2)) + 1e-9) * np.sqrt(np.mean(voice ** 2)) * 10 ** (MUSIC_DB / 20) * duck
        fx = np.zeros(n, np.float32)
        for e in self.sfx:
            fx += _sfx(e, n, sr)
        fx += _pen_sound(pen_log, n, sr, voice)
        if not PREVIEW:  # stems for the full-film mix (final.py): effects relative to a voice peak of 0.5
            np.save(ROOT / "renders" / f"{self.name}_fx.npy", fx.astype(np.float32))
        y = voice + mus + fx
        tmp = path.with_suffix(".raw.wav")
        _write(tmp, y / (np.abs(y).max() + 1e-9) * 0.9, sr)
        r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(tmp), "-af", "loudnorm=I=-14.5:TP=-1.5:LRA=11:print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True)
        i = r.stderr.rfind("{")
        m = json.loads(r.stderr[i:r.stderr.find("}", i) + 1])
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp), "-af",
                        f"loudnorm=I=-14.5:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                        f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true",
                        "-ar", str(sr), str(path)], check=True)
        tmp.unlink()


# ---------------------------------------------------------------- audio helpers


def _read(p):
    import soundfile as sf
    x, sr = sf.read(str(p), dtype="float32")
    return (x if x.ndim == 1 else x.mean(1)), sr


def _write(p, x, sr):
    pcm = (np.clip(x, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def _resample(x, a, b):
    return x if a == b else signal.resample_poly(x, b, a).astype(np.float32)


def _decode(p, sr):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(sr), "-"], capture_output=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def _bp(x, lo, hi, sr, order=2):
    return signal.sosfilt(signal.butter(order, [lo, hi], "bp", fs=sr, output="sos"), x).astype(np.float32)


def _lp(x, hi, sr, order=2):
    return signal.sosfilt(signal.butter(order, hi, "lp", fs=sr, output="sos"), x).astype(np.float32)


def _sfx(e, n, sr):
    """Synthesised effects. Levels are relative to a voice peak of 0.5."""
    r = np.random.default_rng(abs(hash((e["kind"], round(e["t0"], 2)))) % 2 ** 32)
    i0, i1 = int(e["t0"] * sr), min(n, int(e["t1"] * sr))
    out = np.zeros(n, np.float32)
    if i0 >= n:
        return out
    L = max(1, i1 - i0)
    tt = np.arange(L) / sr
    k = e["kind"]
    if k == "wind":
        x = _bp(r.standard_normal(L).astype(np.float32), 150, 900, sr)
        gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.13 * tt + r.uniform(0, 6)) * np.sin(2 * np.pi * 0.07 * tt)
        x *= gust * 0.05
        f = min(L // 2, int(0.6 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "engine":
        ph = 2 * np.pi * (34 + 2 * np.sin(2 * np.pi * 0.7 * tt)) * tt
        x = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sign(np.sin(ph)) * 0.3) * 0.05
        x += _lp(r.standard_normal(L).astype(np.float32), 300, sr) * 0.04
        if e.get("away"):
            x *= np.linspace(1.4, 0.0, L) ** 1.5
        f = min(L // 3, int(0.3 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "thud":
        d = int(0.5 * sr)
        tt = np.arange(d) / sr
        x = np.sin(2 * np.pi * (70 - 30 * tt) * tt) * np.exp(-tt * 14) * 0.5
        x += _bp(r.standard_normal(d).astype(np.float32), 300, 2500, sr) * np.exp(-tt * 18) * 0.25  # snow crunch
        L = d
    elif k == "knock":
        d = int(0.25 * sr)
        tt = np.arange(d) / sr
        x = (np.sin(2 * np.pi * 180 * tt) * 0.4 + _bp(r.standard_normal(d).astype(np.float32), 400, 3000, sr) * 0.3) * np.exp(-tt * 30)
        L = d
    elif k == "smash":
        d = int(1.6 * sr)
        tt = np.arange(d) / sr
        x = _bp(r.standard_normal(d).astype(np.float32), 1500, 12000, sr) * np.exp(-tt * 6) * 0.6
        x += np.sin(2 * np.pi * 90 * tt) * np.exp(-tt * 20) * 0.4
        for _ in range(26):  # falling shards
            j = int(r.uniform(0.08, 1.3) * sr)
            m = int(0.06 * sr)
            if j + m < d:
                f = r.uniform(3000, 7000)
                x[j:j + m] += np.sin(2 * np.pi * f * np.arange(m) / sr) * np.exp(-np.arange(m) / sr * 60) * r.uniform(0.05, 0.15)
        L = d
    elif k == "alarm":  # electric bell
        x = np.sign(np.sin(2 * np.pi * 950 * tt)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 24 * tt)))
        x = _bp(x.astype(np.float32), 700, 4000, sr) * 0.06
    elif k == "crowd":
        x = _bp(r.standard_normal(L).astype(np.float32), 250, 3500, sr)
        x *= (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 0.2 * tt))) * 0.07
        f = min(L // 3, int(0.8 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "shutter":
        d = int(0.12 * sr)
        tt = np.arange(d) / sr
        x = _bp(r.standard_normal(d).astype(np.float32), 2000, 9000, sr) * (np.exp(-tt * 90) + 0.6 * np.exp(-np.maximum(0, tt - 0.05) * 90) * (tt > 0.05)) * 0.25
        L = d
    elif k == "ring":  # 1990s Norwegian phone: 425 Hz bursts
        on = (np.mod(tt, 1.2) < 0.9).astype(np.float32)
        x = (np.sin(2 * np.pi * 425 * tt) * 0.6 + np.sign(np.sin(2 * np.pi * 850 * tt)) * 0.15) * on * 0.06
        x = _bp(x.astype(np.float32), 300, 3000, sr)
    elif k == "hum":
        x = (np.sin(2 * np.pi * 50 * tt) * 0.02 + np.sin(2 * np.pi * 15625 * tt) * 0.004).astype(np.float32)
    elif k == "whoosh":
        d = int(0.5 * sr)
        tt = np.arange(d) / sr
        env = np.sin(np.pi * tt / 0.5) ** 2
        x = _bp(r.standard_normal(d).astype(np.float32), 300, 3000, sr) * env * 0.12
        L = d
    elif k == "morse":  # a distant key: random dits and dahs at 750 Hz
        x = np.zeros(L, np.float32)
        j, dit = 0, int(0.06 * sr)
        while j < L:
            d = dit * (3 if r.random() < 0.4 else 1)
            m = min(d, L - j)
            x[j:j + m] = np.sin(2 * np.pi * 750 * np.arange(m) / sr) * 0.05
            j += d + dit * (3 if r.random() < 0.25 else 1)
        x = _bp(x, 500, 1500, sr)
    elif k == "static":  # valve radio hiss with crackle
        x = _bp(r.standard_normal(L).astype(np.float32), 600, 4500, sr) * 0.018
        x += (r.random(L) < 0.0006).astype(np.float32) * r.uniform(-0.2, 0.2, L).astype(np.float32)
        f = min(L // 3, int(0.4 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "type":  # typewriter keys, a carriage return now and then
        x = np.zeros(L, np.float32)
        j = 0
        while j < L - int(0.05 * sr):
            m = int(0.03 * sr)
            tt_ = np.arange(m) / sr
            x[j:j + m] += _bp(r.standard_normal(m).astype(np.float32), 1500, 6000, sr) * np.exp(-tt_ * 160) * r.uniform(0.12, 0.22)
            j += int(r.uniform(0.07, 0.19) * sr) + (int(0.5 * sr) if r.random() < 0.05 else 0)
    elif k == "guns":  # distant artillery: low thumps at random
        x = np.zeros(L, np.float32)
        j = int(r.uniform(0.1, 0.6) * sr)
        while j < L:
            m = min(int(1.4 * sr), L - j)
            tt_ = np.arange(m) / sr
            x[j:j + m] += (np.sin(2 * np.pi * (48 - 12 * tt_) * tt_) * np.exp(-tt_ * 4) * 0.35
                           + _lp(r.standard_normal(m).astype(np.float32), 220, sr) * np.exp(-tt_ * 3) * 0.3)
            j += int(r.uniform(1.2, 3.0) * sr)
    elif k == "door":  # a heavy door shutting: latch click then a deep thud
        d = int(0.7 * sr)
        tt = np.arange(d) / sr
        x = _bp(r.standard_normal(d).astype(np.float32), 2000, 7000, sr) * np.exp(-tt * 120) * 0.2
        x += np.sin(2 * np.pi * (85 - 25 * tt) * tt) * np.exp(-np.maximum(0, tt - 0.04) * 11) * 0.5 * (tt > 0.04)
        L = d
    elif k == "fire":  # a campfire: soft roar and random wood pops
        x = _lp(r.standard_normal(L).astype(np.float32), 400, sr) * 0.035
        j = 0
        while j < L:
            m = min(int(0.02 * sr), L - j)
            tt_ = np.arange(m) / sr
            x[j:j + m] += _bp(r.standard_normal(m).astype(np.float32), 1200, 7000, sr) * np.exp(-tt_ * 250) * r.uniform(0.04, 0.25)
            j += int(r.exponential(0.09) * sr) + 1
        f = min(L // 3, int(0.6 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "night":  # tropical night: two crickets chirping out of step, a frog now and then
        x = np.zeros(L, np.float32)
        for f0, rate, ph in ((4300, 0.62, 0.0), (4850, 0.55, 0.23)):
            pulse = (np.sin(2 * np.pi * 32 * tt) > 0.2).astype(np.float32)
            chirp = (np.mod(tt / rate + ph, 1.0) < 0.17).astype(np.float32)
            x += np.sin(2 * np.pi * f0 * tt).astype(np.float32) * ndimage.gaussian_filter1d(pulse * chirp, 30) * 0.012
        j = int(r.uniform(0.5, 2) * sr)
        while j < L:
            m = min(int(0.18 * sr), L - j)
            tt_ = np.arange(m) / sr
            x[j:j + m] += (np.sign(np.sin(2 * np.pi * (180 + 40 * tt_) * tt_)) * np.sin(np.pi * tt_ / 0.18) * 0.012).astype(np.float32)
            j += int(r.uniform(1.5, 4) * sr)
        x = _lp(x, 6000, sr)
        f = min(L // 3, int(0.8 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "thunder":  # a close crack, then a long rolling rumble
        d = int(4.5 * sr)
        tt = np.arange(d) / sr
        x = _bp(r.standard_normal(d).astype(np.float32), 400, 4000, sr) * np.exp(-tt * 9) * 0.35
        roll = 0.6 + 0.4 * ndimage.gaussian_filter1d(r.standard_normal(d), int(0.15 * sr)) * 8
        x += _lp(r.standard_normal(d).astype(np.float32), 140, sr) * np.exp(-tt * 0.9) * np.clip(roll, 0.2, 1.4) * 0.9
        x[:int(0.01 * sr)] *= np.linspace(0, 1, int(0.01 * sr))
        L = d
    elif k == "bolt":  # a rifle bolt worked: click, slide back and forward, click
        d = int(0.5 * sr)
        x = np.zeros(d, np.float32)
        for at, g in ((0.0, 0.35), (0.07, 0.12), (0.26, 0.12), (0.36, 0.45)):
            j, m = int(at * sr), int(0.03 * sr)
            tt_ = np.arange(m) / sr
            x[j:j + m] += _bp(r.standard_normal(m).astype(np.float32), 1800, 8000, sr) * np.exp(-tt_ * 160) * g
        j = int(0.08 * sr)
        x[j:j + int(0.16 * sr)] += _bp(r.standard_normal(int(0.16 * sr)).astype(np.float32), 1500, 5000, sr) * 0.05
        L = d
    elif k == "stamp":  # a seal pressed onto paper on a wooden table
        d = int(0.35 * sr)
        tt = np.arange(d) / sr
        x = np.sin(2 * np.pi * (110 - 40 * tt) * tt) * np.exp(-tt * 22) * 0.35
        x += _bp(r.standard_normal(d).astype(np.float32), 600, 3000, sr) * np.exp(-tt * 60) * 0.15
        L = d
    elif k == "clink":  # ice and glass: a few bright inharmonic partials ringing out, a small rattle of ice
        d = int(0.9 * sr)
        tt = np.arange(d) / sr
        x = sum(np.sin(2 * np.pi * f * tt + r.uniform(0, 6)) * np.exp(-tt * dk) * g
                for f, dk, g in ((2650, 7, 0.10), (4120, 9, 0.07), (5480, 12, 0.05), (7230, 16, 0.03))).astype(np.float32)
        x += _bp(r.standard_normal(d).astype(np.float32), 2500, 9000, sr) * np.exp(-tt * 80) * 0.15
        for j in (0.05, 0.11):  # the ice settling
            m = int(0.02 * sr); i_ = int(j * sr)
            x[i_:i_ + m] += _bp(r.standard_normal(m).astype(np.float32), 1800, 6000, sr) * np.exp(-np.arange(m) / sr * 200) * 0.08
        L = d
    elif k == "strike":  # a match struck: a dry scratch on the striking strip, then the flare's soft rush
        d = int(1.2 * sr)
        tt = np.arange(d) / sr
        x = np.zeros(d, np.float32)
        sc_ = int(0.09 * sr)
        x[:sc_] = _bp(r.standard_normal(sc_).astype(np.float32), 2500, 9000, sr) * np.linspace(0.2, 1, sc_) * 0.35
        fl = (tt > 0.08).astype(np.float32) * np.exp(-np.clip(tt - 0.08, 0, None) * 5) * (1 - np.exp(-np.clip(tt - 0.08, 0, None) * 60))
        x += _bp(r.standard_normal(d).astype(np.float32), 300, 3500, sr) * fl * 0.35
        x += _lp(r.standard_normal(d).astype(np.float32), 900, sr) * (tt > 0.3) * np.exp(-np.clip(tt - 0.3, 0, None) * 2) * 0.05
    elif k == "wav":  # a recorded or generated sound file (walla, a ship's horn...): e["path"], looped to the length
        import soundfile as _sf
        y, ysr = _sf.read(str(e["path"]), dtype="float32")
        y = y if y.ndim == 1 else y.mean(1)
        if ysr != sr:
            y = np.interp(np.arange(int(len(y) * sr / ysr)) / sr, np.arange(len(y)) / ysr, y).astype(np.float32)
        reps = int(np.ceil(L / max(1, len(y))))
        x = np.tile(y, reps)[:L] * 0.5 / max(1e-4, np.abs(y).max())
        f = min(int(0.4 * sr), L // 3)
        if f:
            x[:f] *= np.linspace(0, 1, f); x[-f:] *= np.linspace(1, 0, f)
    elif k == "paper":  # a folded note handled: soft crackles and a slide
        x = _bp(r.standard_normal(L).astype(np.float32), 1200, 6000, sr) * 0.012
        x *= np.sin(np.pi * tt / max(1e-6, tt[-1])) ** 2
        j = 0
        while j < L:
            m = min(int(0.015 * sr), L - j)
            x[j:j + m] += _bp(r.standard_normal(m).astype(np.float32), 1500, 7000, sr) * np.exp(-np.arange(m) / sr * 300) * r.uniform(0.03, 0.12)
            j += int(r.exponential(0.05) * sr) + 1
    elif k == "rip":  # cloth torn: a dry, crackling tear that speeds up
        d = int(0.6 * sr)
        tt = np.arange(d) / sr
        x = np.zeros(d, np.float32)
        j = 0
        while j < d - 200:
            m = int(0.004 * sr)
            x[j:j + m] += _bp(r.standard_normal(m).astype(np.float32), 900, 6000, sr) * r.uniform(0.1, 0.3)
            j += int(max(0.002, 0.02 * (1 - j / d) ** 2) * sr * r.uniform(0.5, 1.5))
        x += _bp(r.standard_normal(d).astype(np.float32), 1500, 5000, sr) * 0.03 * np.sin(np.pi * tt / 0.6)
        L = d
    elif k == "train":  # a goods train rolling: deep rumble, the clack-clack of wheels over rail joints, a metal creak
        x = _lp(r.standard_normal(L).astype(np.float32), 160, sr) * 0.09
        j = int(r.uniform(0.1, 0.4) * sr)
        while j < L:
            for dj in (0, int(0.13 * sr)):
                m = min(int(0.05 * sr), L - j - dj)
                if m > 0:
                    tt_ = np.arange(m) / sr
                    x[j + dj:j + dj + m] += (_bp(r.standard_normal(m).astype(np.float32), 300, 2400, sr) * np.exp(-tt_ * 70) * 0.22
                                             + np.sin(2 * np.pi * 95 * tt_) * np.exp(-tt_ * 40) * 0.2)
            j += int(r.uniform(0.85, 1.05) * sr)
        x += np.sin(2 * np.pi * (2400 + 300 * np.sin(2 * np.pi * 0.3 * tt)) * tt).astype(np.float32) * 0.003
        f = min(L // 3, int(0.8 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "rotor":  # a helicopter some way off: blade slap at ~6 Hz over a low turbine whine
        slap = (0.5 + 0.5 * np.cos(2 * np.pi * 6.2 * tt)) ** 8
        x = _lp(r.standard_normal(L).astype(np.float32), 500, sr) * (0.02 + 0.1 * slap)
        x += np.sin(2 * np.pi * 820 * tt).astype(np.float32) * 0.004
        f = min(L // 3, int(1.0 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    elif k == "rain":
        x = _bp(r.standard_normal(L).astype(np.float32), 900, 7000, sr) * 0.025
        x += (r.random(L) < 0.002).astype(np.float32) * r.uniform(0, 0.06, L).astype(np.float32)
        f = min(L // 3, int(0.8 * sr))
        x[:f] *= np.linspace(0, 1, f); x[L - f:] *= np.linspace(1, 0, f)
    else:
        x = np.zeros(L, np.float32)
    x = x[:max(0, min(L, n - i0))] * 10 ** (e["db"] / 20)
    out[i0:i0 + len(x)] = x
    return out


PEN_DB = -27  # the drawing tool against the voice's loudness: heard, never competing (a further -7 dB while he talks)
TOOLS = {  # band (Hz) and level of each tool's sound: a soft graphite grain, dry chalk, a near-silent brush
    "pencil": (450, 3400, 1.0), "red": (450, 3400, 1.0), "pen": (800, 4200, 0.8), "chalk": (300, 3000, 1.15),
    "brush": (140, 1100, 0.4)}


def _pen_sound(log, n, sr, voice):
    """The drawing tool's sound, following its real speed on screen: silent-ish when it rests, fuller when it moves.
    Band-limited and low-passed (no hiss), set PEN_DB under the voice, and dipped further while the narrator speaks."""
    spf = sr / FPS
    r = np.random.default_rng(11)
    white = r.standard_normal(n).astype(np.float32)
    grit = np.abs(_lp(r.standard_normal(n).astype(np.float32), 30, sr))
    grit = (grit / (grit.max() + 1e-9)) ** 1.5
    sp = np.zeros(len(log), np.float32)
    for i in range(1, len(log)):
        (ta, pa), (tb, pb) = log[i - 1], log[i]
        if ta and ta == tb and pa and pb:
            sp[i] = min(3000.0, math.hypot(pb[0] - pa[0], pb[1] - pa[1]) * FPS * 1920 / OW)
    out = np.zeros(n, np.float32)
    on_all = np.zeros(n, np.float32)
    for name, (lo, hi, g) in TOOLS.items():
        on = np.array([1.0 if tl == name else 0.0 for tl, _ in log], np.float32)
        if not on.any():
            continue
        mv = on * (0.2 + 0.8 * np.clip(sp / 900, 0, 1))
        env = ndimage.gaussian_filter1d(mv, 1.2)
        e = np.interp(np.arange(n) / spf, np.arange(len(env)), env).astype(np.float32)
        tex = _bp(white, lo, hi, sr) * (0.35 + 1.4 * grit)
        if name == "chalk":  # dusty little catches on the board
            tex += _bp(((r.random(n) < 0.003) * r.uniform(-1, 1, n)).astype(np.float32), 700, 3500, sr) * 3
        out += tex * e * g
        on_all = np.maximum(on_all, np.interp(np.arange(n) / spf, np.arange(len(on)), on).astype(np.float32))
    if not on_all.any():
        return out
    out = _lp(out, 4200, sr)
    speech = voice[np.abs(voice) > 0.02]
    v_rms = math.sqrt(float(np.mean(speech ** 2))) if len(speech) else 0.1
    p_rms = math.sqrt(float(np.mean(out[on_all > 0.5] ** 2))) + 1e-9
    out *= v_rms * 10 ** (PEN_DB / 20) / p_rms
    venv = ndimage.uniform_filter1d(np.abs(voice), int(0.3 * sr))
    talk = np.clip(venv / (np.percentile(venv, 95) * 0.25 + 1e-9), 0, 1)
    return out * 10 ** (-7 * talk / 20)


# ---------------------------------------------------------------- sketch sheets: panels and drawing order


PANEL_FIX = {"X02_fake_trail": [[9, 185, 444, 715], [444, 270, 850, 630], [850, 197, 1310, 710], [1299, 177, 1765, 703]]}  # passport touches the train


def panels(name):
    f = BUILD / "panels.json"
    allp = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    if name not in allp:
        allp[name] = PANEL_FIX.get(name) or find_panels(name)
        f.write_text(json.dumps(allp), encoding="utf-8")
    return [tuple(int(v) for v in b) for b in allp[name]]


def find_panels(name, n=4):
    """Boxes of the separate drawings on a sheet: split at the widest empty column gaps of its line version."""
    g = np.asarray(Image.open(find_img(name + "_lines")).convert("L"), np.float32)
    ink = g < 200
    col = ndimage.uniform_filter1d(ink.sum(0).astype(np.float32), 5) > 1
    lab, k = ndimage.label(col)
    runs = [(np.flatnonzero(lab == i)[0], np.flatnonzero(lab == i)[-1]) for i in range(1, k + 1)]
    while len(runs) > n:  # merge across the narrowest gap
        gaps = [runs[i + 1][0] - runs[i][1] for i in range(len(runs) - 1)]
        i = int(np.argmin(gaps))
        runs[i:i + 2] = [(runs[i][0], runs[i + 1][1])]
    dens = ndimage.uniform_filter1d(ink.sum(0).astype(np.float32), 9)
    while len(runs) < n:  # drawings that touch: split the widest run at its emptiest column
        i = max(range(len(runs)), key=lambda j: runs[j][1] - runs[j][0])
        a, b_ = runs[i]
        lo, hi = a + (b_ - a) // 5, b_ - (b_ - a) // 5
        c = lo + int(np.argmin(dens[lo:hi]))
        runs[i:i + 1] = [(a, c - 1), (c + 1, b_)]
    out = []
    for x0, x1 in runs:
        rows = np.flatnonzero(ink[:, x0:x1 + 1].sum(1) > 1)
        out.append([int(max(0, x0 - 6)), int(max(0, rows[0] - 6)), int(min(SW, x1 + 7)), int(min(SH, rows[-1] + 7))])
    return out


def sheet_order(name):
    """Per panel: T (ink order 0..1, dense), F (colour brush order 0..1), K (pen track) of the line version."""
    f = BUILD / f"sheet_{name}.npz"
    if f.exists() and f.stat().st_mtime > find_img(name + "_lines").stat().st_mtime:
        return dict(np.load(f))
    a = np.asarray(Image.open(find_img(name + "_lines")).convert("L"), np.float32) / 255
    d = np.clip((0.96 - a) / 0.9, 0, 1)
    out = {}
    for i, (x0, y0, x1, y1) in enumerate(panels(name)):
        crop = d[y0:y1, x0:x1]
        T, trk = stages.strokes(crop, 0.2, (40, 10))
        yy, xx = np.mgrid[0:T.shape[0], 0:T.shape[1]]
        out[f"T{i}"] = (ndimage.gaussian_filter(T, 4) + 0.006 * np.sin((xx + yy) * 0.45)).astype(np.float32)
        nz = ndimage.gaussian_filter(RNG.standard_normal(T.shape), 22)
        nz = (nz - nz.min()) / (nz.max() - nz.min() + 1e-9)
        out[f"F{i}"] = (0.65 * xx / max(1, T.shape[1] - 1) + 0.35 * nz).astype(np.float32)
        out[f"K{i}"] = trk[:, [0, 1, 2]].astype(np.float32)
    np.savez_compressed(f, **out)
    return out


# ---------------------------------------------------------------- sketchbook page drawn live


class Paper:
    """A sketchbook page at 2x output size with live strokes; camera = (cx, cy, w) keys in page px."""

    def __init__(self, t0, cam, color="paper"):
        self.W, self.H = 3840, 2160
        r = np.random.default_rng(9)
        w, h = OW, OH
        mottle = cv2.resize(ndimage.gaussian_filter(r.standard_normal((h // 4, w // 4)), 18).astype(np.float32), (w, h))
        fine = ndimage.gaussian_filter(r.standard_normal((h, w)), 0.7).astype(np.float32)
        self.paper = np.clip(np.array([244, 239, 228], np.float32) + (2.2 * mottle / mottle.std() + 1.5 * fine / fine.std())[..., None], 0, 255)
        self.items, self.t0, self.cam = [], t0, cam
        self.L = {k: Image.new("L", (self.W, self.H)) for k in COL}
        self.D = {k: ImageDraw.Draw(v) for k, v in self.L.items()}
        self.fig = Marks()

    def frame(self, t):
        items = sorted(self.fig.items, key=lambda i: i.t0)
        for it in items:
            if it.layer == "auto":
                it.layer = "ink"
        active = None
        for it in items:
            if it.t0 <= t:
                it.draw(t, self.L if isinstance(it, sk.Text) else self.D)
                if t <= it.t0 + it.dur + 0.02:
                    active = it
        keys = self.cam
        for (ta, *a), (tb, *b) in zip(keys, keys[1:]):
            if t <= tb:
                u = ease((t - ta) / max(1e-6, tb - ta))
                cx, cy, w = [x + (y - x) * u for x, y in zip(a, b)]
                break
        else:
            cx, cy, w = keys[-1][1:]
        s = w / OW
        x0, y0 = cx - w / 2, cy - w * OH / OW / 2
        M = np.float32([[s, 0, x0], [0, s, y0]])
        img = self.paper.copy()
        for k, c in COL.items():
            if k.startswith("cream") or k.endswith("h"):
                continue
            a = cv2.GaussianBlur(np.asarray(self.L[k], np.float32) / 255, (0, 0), 0.5)
            a = cv2.warpAffine(a, M, (OW, OH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)[..., None]
            img = img * (1 - a * 0.92) + np.array(c, np.float32) * a * 0.92
        pen = None
        if active is not None:
            p = np.array(active.pos(t))
            pen = (active.tool, ((p[0] - x0) / s, (p[1] - y0) / s), 600.0)
        return img, pen


# ---------------------------------------------------------------- pages: real objects from the story, drawn on live

MEDIA = dict(graphite=dict(col=(58, 56, 62), tool="pencil"),  # pencil on paper: grey, catches the paper's tooth
             chalk=dict(col=(236, 236, 226), tool="chalk"),    # chalk on a board: dry, broken, a little dust
             sumi=dict(col=(22, 18, 18), tool="brush"),          # brush ink on washi: dense, soft bleeding edge
             carve=dict(col=(234, 224, 186), tool="pencil"))     # cut into bamboo or wood: the pale fibre shows
ACCENT = (178, 38, 30)  # red pencil, the seal
SEAL_FONT = ytf.font("seal")


class Page:
    """A real object from the story (field notebook, blackboard, washi paper...) that drawings are made on, live, in
    its own medium. Drawings are code strokes (maps, contours, hatching, landscapes; source px) or drawings lifted
    from a sketch sheet's line version and redrawn in the page's medium, in the sheet's own stroke order."""

    def __init__(self, base, medium):
        self.base, self.medium, self.tool = base, medium, MEDIA[medium]["tool"]
        self.items, self.lifts, self.seals = [], [], []
        self.L = None

    # ------------------------------------------------------------ what gets drawn

    def stroke(self, pts, t0, dur, width=3.0, wob=1.2, ease_=0.4, accent=False):
        p = sk.resample(np.array(pts, float) * UP, 4)
        if wob and len(p) > 4:
            p = sk.wobble(p, wob * UP, 6)
        self.items.append(sk.Stroke(p, "accent" if accent else "main", width * UP, t0, dur,
                                    "red" if accent else self.tool, ease_))

    def strokes(self, paths, t0, t1, width=3.0, wob=1.0, ease_=0.3, gap=0.15, accent=False):
        """Many strokes one after another between t0 and t1, time shared by length (gap: share of pen-up time)."""
        paths = [np.asarray(q, float) for q in paths if len(q) > 1]
        if not paths:
            return
        L = np.array([np.hypot(*np.diff(q, axis=0).T).sum() for q in paths]) + 1e-6
        d = L / L.sum() * (t1 - t0) * (1 - gap)
        t = t0
        for q, di in zip(paths, d):
            self.stroke(q, t, max(0.02, di), width, wob, ease_, accent)
            t += di + (t1 - t0) * gap / len(paths)

    def text(self, s_, xy, size, t0, dur, angle=0, accent=False):
        self.items.append(sk.Text(s_, np.array(xy) * UP, size * UP, "accent" if accent else "main", t0, dur,
                                  tool="red" if accent else self.tool, angle=angle))

    def lift(self, src, panel, center, height, t0, t1, rot=0.0, thicken=0.0, keep=0.0, soft=0.0, clip=None, fade=0.0,
             fill=(), sweep=None):
        """Redraw a drawing on this page, in its stroke order: drawing `panel` (an index) of a sketch sheet's line
        version, or a box (x0, y0, x1, y1) cut from any line image (a scene's `_lines` version). Centred at `center`,
        `height` tall (source px), turned `rot` degrees. thicken: widen lines (px) for chalk or brush; keep: drop marks
        fainter than this (fine hatching chalk can't hold); soft: blur (px) so hatching turns into an ink wash;
        clip: a polygon (px inside the panel or box) around the subject, leaving its background behind; fade: let the
        drawing trail off unevenly towards the edges of its box (share of the box), as a sketch does; fill: ellipses
        (cx, cy, rx, ry) filled lightly, the lines inside left dark (a chalk face, so it isn't a black hole);
        sweep: paint it in one ragged sweep in this direction (degrees on the page) instead of stroke by stroke, the
        way a brush lays in an object."""
        if isinstance(panel, int):
            x0, y0, x1, y1 = panels(src)[panel]
            name = src + "_lines"
        else:
            x0, y0, x1, y1 = panel
            name = src
        g = np.asarray(Image.open(find_img(name)).convert("L"), np.float32)[y0:y1, x0:x1] / 255
        d = np.clip((0.96 - g) / 0.9, 0, 1)
        if isinstance(panel, int):
            o = sheet_order(src)
            T, K = o[f"T{panel}"].astype(np.float32), o[f"K{panel}"]
        else:
            f = BUILD / f"lift_{name}_{x0}_{y0}_{x1}_{y1}.npz"
            if not f.exists():
                T, K = stages.strokes(d, 0.2, (40, 10))
                yy, xx = np.mgrid[0:T.shape[0], 0:T.shape[1]]
                T = (ndimage.gaussian_filter(T, 4) + 0.006 * np.sin((xx + yy) * 0.45)).astype(np.float32)
                np.savez_compressed(f, T=T, K=K.astype(np.float32))
            o = np.load(f)
            T, K = o["T"], o["K"]
        if clip is not None:
            cm = np.zeros(d.shape, np.uint8)
            cv2.fillPoly(cm, [np.array(clip, np.int32)], 1)
            d = d * cv2.GaussianBlur(cv2.dilate(cm, np.ones((9, 9), np.uint8)).astype(np.float32), (0, 0), 3)
            inside = cm[np.clip(K[:, 2].astype(int), 0, d.shape[0] - 1), np.clip(K[:, 1].astype(int), 0, d.shape[1] - 1)] > 0
            K = K[inside]
            if len(K):  # the pen only visits the subject, so its strokes take the whole drawing time
                lo, hi = K[:, 0].min(), K[:, 0].max()
                T = np.clip((T - lo) / max(1e-6, hi - lo), 0, 1)
                K = np.c_[(K[:, 0] - lo) / max(1e-6, hi - lo), K[:, 1:3]]
        if fade:
            h_, w_ = d.shape
            yy, xx = np.mgrid[0:h_, 0:w_]
            e = np.minimum.reduce([xx, w_ - 1 - xx, yy, h_ - 1 - yy]).astype(np.float32) / (fade * min(h_, w_))
            nz = ndimage.gaussian_filter(RNG.standard_normal(d.shape), 14)
            d = d * np.clip(e + 0.4 * nz / nz.std() - 0.1, 0, 1)
        for (fx_, fy_, rx, ry) in fill:
            em = np.zeros(d.shape, np.float32)
            cv2.ellipse(em, (int(fx_), int(fy_)), (int(rx), int(ry)), 0, 0, 360, 1.0, -1)
            em = cv2.GaussianBlur(em, (0, 0), 3)
            d = d * (1 - em) + em * 0.55 * (1 - d) ** 2
        if soft:
            d = np.maximum(d * 0.85, cv2.GaussianBlur(d, (0, 0), soft) * 1.25)
        if keep:
            d = np.clip((d - keep) / (1 - keep), 0, 1)
        s_ = height / d.shape[0] * UP
        c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        h2, w2 = d.shape[0] / 2, d.shape[1] / 2
        M = np.float32([[s_ * c, -s_ * sn, center[0] * UP - s_ * (c * w2 - sn * h2)],
                        [s_ * sn, s_ * c, center[1] * UP - s_ * (sn * w2 + c * h2)]])
        size = (SW * UP, SH * UP)
        dw = cv2.warpAffine(d, M, size, flags=cv2.INTER_LINEAR)
        Tw = cv2.warpAffine(T, M, size, flags=cv2.INTER_LINEAR, borderValue=2.0)
        if thicken:
            k = max(1, int(round(thicken * UP)))
            ker = np.ones((2 * k + 1, 2 * k + 1), np.uint8)
            dw = np.maximum(dw, cv2.GaussianBlur(cv2.dilate(dw, ker), (0, 0), k * 0.5) * 0.9)
            Tw = cv2.erode(Tw, ker)  # widened marks appear with the stroke they grew from
        if soft or thicken:  # a brush or chalk lays in broader sweeps: a soft front, not specks
            Tw = cv2.GaussianBlur(Tw, (0, 0), (soft + thicken) * UP * 4)
        ys, xs = np.nonzero(dw > 0.02)
        by0, by1, bx0, bx1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        trk = np.c_[K[:, 0], K[:, 1:3] @ M[:, :2].T + M[:, 2]] / np.array([1, UP, UP], np.float32)
        if sweep is not None:
            a = math.radians(sweep)
            pr = xs * math.cos(a) + ys * math.sin(a)
            u = (pr - pr.min()) / max(1e-6, pr.max() - pr.min())
            Tw = np.full(Tw.shape, 2.0, np.float32)
            nz = ndimage.gaussian_filter(RNG.standard_normal((by1 - by0, bx1 - bx0)), 6 * UP)
            Tw[ys, xs] = np.clip(0.9 * u + 0.1 * (nz[ys - by0, xs - bx0] / nz.std()) * 0.5 + 0.05, 0, 1)
            k = np.linspace(0, 1, 60)
            trk = np.array([[q, *np.mean(np.stack([xs, ys], 1)[np.abs(u - q) < 0.02], 0) / UP] for q in k
                            if (np.abs(u - q) < 0.02).any()], np.float32)
        self.lifts.append(dict(d=dw[by0:by1, bx0:bx1].copy(), T=Tw[by0:by1, bx0:bx1].copy(), box=(by0, by1, bx0, bx1),
                               t0=t0, t1=t1, trk=trk[np.argsort(trk[:, 0])]))

    def seal(self, center, size, t, text="小野田"):
        """A red name seal (hanko) pressed onto the page at t: carved characters knocked out of a red square."""
        n = int(size * UP)
        im = Image.new("L", (n, n), 0)
        dr = ImageDraw.Draw(im)
        dr.rounded_rectangle([n * 0.04, n * 0.04, n * 0.96, n * 0.96], radius=n * 0.08, fill=255)
        font = ImageFont.truetype(SEAL_FONT, int(n * 0.27))
        for i, ch in enumerate(text):  # one column, top to bottom
            bb = font.getbbox(ch)
            dr.text(((n - (bb[2] - bb[0])) / 2 - bb[0], n * 0.08 + i * n * 0.29 - bb[1] * 0.5), ch, fill=0, font=font)
        a = np.asarray(im, np.float32) / 255
        r = np.random.default_rng(int(center[0]))
        wear = ndimage.gaussian_filter(r.standard_normal(a.shape), 1.5 * UP)
        a = a * np.clip(0.75 + 0.6 * wear / wear.std(), 0, 1)  # uneven ink, a few bare patches
        self.seals.append(dict(a=a.astype(np.float32), xy=(int(center[0] * UP - n / 2), int(center[1] * UP - n / 2)), t=t))

    # ------------------------------------------------------------ rendering

    def _texture(self):
        """How the surface takes the mark (0..1, at 2x): paper tooth for pencil, dry grain for chalk, ink density for sumi."""
        r = np.random.default_rng(21)
        H, W = SH * UP, SW * UP
        fine = ndimage.gaussian_filter(r.standard_normal((H, W)).astype(np.float32), 0.8)
        fine /= fine.std()
        lum = cv2.cvtColor(up(self.base), cv2.COLOR_RGB2GRAY).astype(np.float32)
        hp = lum - cv2.GaussianBlur(lum, (0, 0), 3)
        hp /= hp.std() + 1e-6
        if self.medium == "graphite":
            return np.clip(0.55 + 0.2 * fine + 0.15 * hp, 0, 1)
        if self.medium == "carve":
            return np.clip(0.8 + 0.15 * fine, 0, 1)
        if self.medium == "chalk":
            streak = ndimage.gaussian_filter(r.standard_normal((H, W)).astype(np.float32), (0.6, 3))
            streak /= streak.std()
            return np.clip(0.62 + 0.32 * fine + 0.18 * streak + 0.1 * hp, 0, 1)
        low = cv2.resize(ndimage.gaussian_filter(r.standard_normal((H // 8, W // 8)), 3).astype(np.float32), (W, H))
        return np.clip(0.9 + 0.08 * low / low.std() + 0.04 * fine, 0, 1)

    def frame(self, t, cam):
        """(screen image, pen) at time t; pen = (tool, point in source px) or None."""
        if self.L is None:
            self.L = {k: Image.new("L", (SW * UP, SH * UP)) for k in ("main", "accent")}
            self.D = {k: ImageDraw.Draw(v) for k, v in self.L.items()}
            self.items.sort(key=lambda i: i.t0)
            self.tex = self._texture()
        pen = None
        for it in self.items:
            if it.t0 <= t:
                it.draw(t, self.L if isinstance(it, sk.Text) else self.D)
                if t <= it.t0 + it.dur + 0.02:
                    pen = (it.tool, np.array(it.pos(t)) / UP)
        main = np.array(self.L["main"], np.float32) / 255
        acc = np.array(self.L["accent"], np.float32) / 255
        for lf in self.lifts:
            if t < lf["t0"]:
                continue
            y0, y1, x0, x1 = lf["box"]
            rev = np.clip((t - (lf["t0"] + lf["T"] * (lf["t1"] - lf["t0"]))) / 0.06, 0, 1)
            np.maximum(main[y0:y1, x0:x1], lf["d"] * rev, out=main[y0:y1, x0:x1])
            if t <= lf["t1"] and pen is None and len(lf["trk"]):  # a printed photo has no pen
                u = (t - lf["t0"]) / max(1e-6, lf["t1"] - lf["t0"])
                k = int(np.clip(np.searchsorted(lf["trk"][:, 0], u), 0, len(lf["trk"]) - 1))
                pen = (self.tool, lf["trk"][k, 1:3].copy())
        for sl in self.seals:
            if t >= sl["t"]:
                u = min(1.0, (t - sl["t"]) / 0.09)  # pressed down: a touch large, then flat on the paper
                a = sl["a"]
                if u < 1:
                    s_ = 1.12 - 0.12 * u
                    a = cv2.resize(a, None, fx=s_, fy=s_) * (0.5 + 0.5 * u)
                x, y = sl["xy"][0] - (a.shape[1] - sl["a"].shape[1]) // 2, sl["xy"][1] - (a.shape[0] - sl["a"].shape[0]) // 2
                reg = acc[y:y + a.shape[0], x:x + a.shape[1]]
                np.maximum(reg, a[:reg.shape[0], :reg.shape[1]], out=reg)
        img = warp(up(self.base), cam).astype(np.float32)
        if self.medium in ("graphite", "sumi"):  # dark ink over a dark part of the object: a soft paper glow behind
            if not hasattr(self, "_lit"):
                lum = cv2.GaussianBlur(cv2.cvtColor(up(self.base), cv2.COLOR_RGB2GRAY).astype(np.float32), (0, 0), 8)
                self._lit = []
                for it in self.items:
                    if isinstance(it, sk.Text):
                        y0, x0 = max(0, it.y), max(0, it.x)
                        reg = lum[y0:y0 + it.m.size[1], x0:x0 + it.m.size[0]]
                        if reg.size and float(np.percentile(reg, 50)) < 165:
                            self._lit.append((y0, y0 + it.m.size[1], x0, x0 + it.m.size[0]))
            if self._lit:
                hm = np.zeros_like(main)
                for (y0, y1, x0, x1) in self._lit:
                    hm[y0:y1, x0:x1] = np.maximum(main[y0:y1, x0:x1], acc[y0:y1, x0:x1])
                if hm.any():
                    r = 7 * UP
                    hm = cv2.GaussianBlur(cv2.dilate(hm, np.ones((2 * r + 1, 2 * r + 1), np.uint8)), (0, 0), r * 0.7)
                    h = np.clip(warp(hm, cam), 0, 1)[..., None] * 0.8
                    img = img * (1 - h) + np.array([244, 238, 222], np.float32) * h
        m = warp(main, cam)[..., None]
        tex = warp(self.tex, cam)[..., None]
        col = np.array(MEDIA[self.medium]["col"], np.float32)
        sc = OW / 1920
        if self.medium == "graphite":
            a = m * (0.4 + 0.6 * tex) * 0.88
            img = img * (1 - a) + img * (col / 255) * a  # graphite darkens what is under it
        elif self.medium == "carve":  # pale cut fibre with a thin dark lip under each cut
            a = np.clip(m * tex, 0, 0.95)
            lip = np.roll(a, max(1, int(2 * sc)), axis=0) * 0.45
            img = img * (1 - lip) + np.array([40, 46, 22], np.float32) * lip
            img = img + (col - img) * a
        elif self.medium == "chalk":
            a = np.clip(m * (0.25 + 0.75 * tex) * 1.05, 0, 0.95)
            dust = cv2.GaussianBlur(a[..., 0], (0, 0), 5 * sc)[..., None] * 0.18
            img = img + (col - img) * np.clip(a + dust, 0, 1)
        else:
            bleed = cv2.GaussianBlur(m[..., 0], (0, 0), 1.4 * sc)[..., None]
            a = np.clip(m * 0.85 + bleed * 0.4, 0, 1) * np.clip(tex, 0, 1) * 0.96
            img = img * (1 - a) + col * a
        if acc.any():
            ac = warp(acc, cam)[..., None] * (0.55 + 0.45 * tex) * 0.92
            img = img * (1 - ac) + img * (np.array(ACCENT, np.float32) / 255) * ac * 0.35 + np.array(ACCENT, np.float32) * ac * 0.65
        return img, pen


def _smooth_ring(r, n=None, closed=True):
    from scipy.interpolate import splprep, splev
    r = np.asarray(r, float)
    r = r[np.r_[True, np.hypot(*np.diff(r, axis=0).T) > 0.5]]
    if len(r) < 5:
        return r
    tck, _ = splprep([r[:, 0], r[:, 1]], s=len(r) * 0.8, per=closed)
    x, y = splev(np.linspace(0, 1, n or len(r) * 6), tck)
    return np.stack([x, y], 1)


def island_map(pg, lon, lat, rect, t_coast, t_contour, levels=5, seed=3, sea=None):
    """A hand-drawn terrain map of the land inside lon x lat, fitted into rect (source px) on a page: the real
    coastline smoothed as a hand would draw it, then contour lines built from the land's shape (higher towards the
    interior, with uneven ridges). sea=(t0, t1): broken wave lines echoing the coast offshore, as old maps draw water.
    Returns (P, field, mask): lon/lat -> page px, the height field and the land mask,
    for rivers (`river`), hillside hatching (`hatch_slopes`) and marks."""
    x0, y0, x1, y1 = rect
    K = math.cos(math.radians((lat[0] + lat[1]) / 2))
    S = min((x1 - x0) / ((lon[1] - lon[0]) * K), (y1 - y0) / (lat[1] - lat[0]))
    cx, cy, lc, ac = (x0 + x1) / 2, (y0 + y1) / 2, (lon[0] + lon[1]) / 2, (lat[0] + lat[1]) / 2

    def P(lo, la):
        return np.array([cx + (lo - lc) * K * S, cy - (la - ac) * S])

    rings = []
    for f in _geojson("ne_10m_land.geojson"):
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = np.asarray(poly[0])
            if r[:, 0].min() >= lon[0] and r[:, 0].max() <= lon[1] and r[:, 1].min() >= lat[0] and r[:, 1].max() <= lat[1]:
                rings.append(_smooth_ring(np.array([P(*q) for q in r])))
    rings.sort(key=len, reverse=True)
    mask = np.zeros((SH, SW), np.uint8)
    cv2.fillPoly(mask, [np.round(r).astype(np.int32) for r in rings], 1)
    dist = cv2.distanceTransform(mask, cv2.DIST_L2, 5)
    rng = np.random.default_rng(seed)
    nz = ndimage.gaussian_filter(rng.standard_normal((SH, SW)), 22)
    field = dist * (1 + 0.55 * nz / nz.std()) * mask
    field = ndimage.gaussian_filter(field, 3) * mask
    pg.strokes([r[::2] for r in rings], t_coast[0], t_coast[1], width=2.6, wob=0.8, gap=0.08)
    top = np.percentile(field[mask > 0], 99)
    paths = []
    for lv in np.linspace(0.16, 0.86, levels) * top:
        cs, _ = cv2.findContours((field > lv).astype(np.uint8), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        for c in sorted(cs, key=len, reverse=True):
            if len(c) > 40:
                q = c[:, 0, :].astype(float)[::3]
                q = np.stack([ndimage.gaussian_filter1d(q[:, 0], 2, mode="wrap"), ndimage.gaussian_filter1d(q[:, 1], 2, mode="wrap")], 1)
                paths.append(np.vstack([q, q[:1]]))
    pg.strokes(paths, t_contour[0], t_contour[1], width=1.4, wob=0.5, gap=0.1)
    if sea:
        out_d = cv2.distanceTransform((1 - mask).astype(np.uint8), cv2.DIST_L2, 5)
        waves = []
        for k, off in enumerate((9, 19, 31)):
            cs, _ = cv2.findContours((out_d < off).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            for c in cs:
                q = c[:, 0, :].astype(float)[::2]
                i = int(rng.integers(0, 12))
                while i < len(q) - 6:  # broken: shorter and sparser further out
                    n_ = int(rng.integers(8, 26 - 6 * k))
                    waves.append(q[i:i + n_])
                    i += n_ + int(rng.integers(4, 10 + 8 * k))
        pg.strokes(waves, sea[0], sea[1], width=1.1, wob=0.3, gap=0.05)
    return P, field, mask


def river(field, mask, start, step=3.0, wiggle=0.35, seed=1):
    """A stream's course: downhill from `start` across the height field until it reaches the coast."""
    gy, gx = np.gradient(ndimage.gaussian_filter(field, 4))
    r = np.random.default_rng(seed)
    p, out = np.array(start, float), []
    for _ in range(600):
        out.append(p.copy())
        x, y = int(p[0]), int(p[1])
        if not (0 <= x < SW and 0 <= y < SH) or not mask[y, x]:
            break
        g = np.array([gx[y, x], gy[y, x]])
        d = -g / (np.hypot(*g) + 1e-9)
        a = r.normal(0, wiggle)
        d = np.array([d[0] * math.cos(a) - d[1] * math.sin(a), d[0] * math.sin(a) + d[1] * math.cos(a)])
        p = p + d * step
    o = np.array(out)
    return np.stack([ndimage.gaussian_filter1d(o[:, 0], 2), ndimage.gaussian_filter1d(o[:, 1], 2)], 1)


def hatch_slopes(field, mask, n=140, length=10, light=(-1, -1), band=(0.12, 0.7), seed=2):
    """Short hatching strokes down the slopes that face away from the light: the way an illustrator shades hills."""
    gy, gx = np.gradient(ndimage.gaussian_filter(field, 4))
    top = np.percentile(field[mask > 0], 99)
    ok = (field > band[0] * top) & (field < band[1] * top)
    ys, xs = np.nonzero(ok)
    r = np.random.default_rng(seed)
    out, L = [], np.array(light, float) / np.hypot(*light)
    for i in r.permutation(len(xs)):
        x, y = xs[i], ys[i]
        g = np.array([gx[y, x], gy[y, x]])
        if np.hypot(*g) < 1e-3 or np.dot(-g / np.hypot(*g), L) > -0.15:  # downhill must point away from the light
            continue
        d = -g / np.hypot(*g)
        out.append(np.array([[x, y], [x + d[0] * length, y + d[1] * length]]))
        if len(out) >= n:
            break
    out.sort(key=lambda q: (q[0][0] + q[0][1]))
    return out


def lean_to(c, s=1.0):
    """A small sketched lean-to shelter (roof, poles, ground line) as stroke paths."""
    x, y = c
    return [np.array([[x - 16 * s, y], [x - 2 * s, y - 14 * s], [x + 18 * s, y - 6 * s]]),
            np.array([[x - 2 * s, y - 14 * s], [x - 2 * s, y + 1 * s]]), np.array([[x + 16 * s, y - 6 * s], [x + 16 * s, y + 1 * s]]),
            np.array([[x - 22 * s, y + 2 * s], [x + 24 * s, y + 2 * s]])]


def palm(base, h, lean=0.25, s=1.0, seed=0):
    """A coconut palm as a few strokes: a curved trunk and drooping fronds."""
    r = np.random.default_rng(seed)
    x, y = base
    tx, ty = x + lean * h, y - h
    trunk = np.array([[x + lean * h * u * u, y - h * u] for u in np.linspace(0, 1, 12)])
    out = [trunk]
    for a in np.linspace(-2.6, -0.5, 6) + r.normal(0, 0.12, 6):
        L = h * r.uniform(0.38, 0.52) * s
        pts = [[tx + math.cos(a) * L * u, ty + math.sin(a) * L * u + 0.55 * L * u * u] for u in np.linspace(0, 1, 8)]
        out.append(np.array(pts))
    return out


def ridge_sketch(x0, x1, y, amp, seed=4):
    """A hand-drawn line of jungle hills across a page, with hatching under each hill."""
    r = np.random.default_rng(seed)
    xs = np.linspace(x0, x1, 120)
    u = (xs - x0) / (x1 - x0)
    ys = y - amp * (0.55 * np.sin(u * 3.1 + 0.4) ** 2 + 0.35 * np.sin(u * 7.3 + 1.2) ** 2 + 0.1 * np.sin(u * 17)) \
        + ndimage.gaussian_filter1d(r.standard_normal(120), 3) * 3
    ridge = np.stack([xs, ys], 1)
    hatch = []
    for xi in np.arange(x0 + 8, x1 - 8, 9):
        yt = np.interp(xi, xs, ys)
        L = r.uniform(14, 34)
        hatch.append(np.array([[xi, yt + 6], [xi - 5, yt + 6 + L]]))
    return ridge, hatch


def chalk_sprite(scale):
    """A stub of white chalk held at the same angle as the pencil, tip at the returned offset."""
    L, r = 150 * scale, 13 * scale
    a = math.radians(32)
    c, s_ = math.cos(a), math.sin(a)
    W_, H_ = int(L * c + 60 * scale), int(L * s_ + 60 * scale)
    im = Image.new("RGBA", (W_, H_))
    d = ImageDraw.Draw(im)
    tip = np.array([14 * scale, 14 * scale])

    def P(pts):
        return [tuple(tip + np.array([x * c - y * s_, x * s_ + y * c]) * 1.0) for x, y in pts]

    d.polygon(P([(0, -r * 0.6), (L, -r), (L, r), (0, r * 0.6)]), fill=(238, 236, 228))
    d.polygon(P([(0, r * 0.1), (L, r * 0.3), (L, r), (0, r * 0.6)]), fill=(208, 205, 196))
    d.ellipse([tip[0] - 3 * scale, tip[1] - 3 * scale, tip[0] + 3 * scale, tip[1] + 3 * scale], fill=(240, 238, 230))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.split()[3].point(lambda v: v * 0.3).filter(ImageFilter.GaussianBlur(5 * scale)))
    full = Image.new("RGBA", (W_ + int(30 * scale), H_ + int(30 * scale)))
    full.alpha_composite(sh, (int(14 * scale), int(20 * scale)))
    full.alpha_composite(im, (0, 0))
    return full, tip


GEO = Path(__file__).resolve().parent / "geo"  # Natural Earth land + borders
_geo = {}


def _geojson(fname):
    if fname not in _geo:
        _geo[fname] = json.load(open(GEO / fname, encoding="utf-8"))["features"]
    return _geo[fname]


def map_page(t0, t1, lon, lat, places=(), routes=(), labels=(), borders=(), coast_t=1.5, height=900, cx=800):
    """A sketch map drawn live on a page. Coordinates in half-page px (1920 x 1080 space).
    places: [(name, lon, lat, t, style, (dx, dy))] style 'circle' (red) | 'dot' (ink)
    routes: [(lon_lat_from, lon_lat_to, t, dur, bend, color)] dashed;  labels: [(text, lon, lat, t, size, color)]
    borders: country names whose land borders are drawn (thin ink)."""
    S = height / (lat[1] - lat[0])
    K = math.cos(math.radians((lat[0] + lat[1]) / 2))
    X0 = cx - (lon[1] - lon[0]) * K * S / 2

    def P(lo, la):
        return np.array([X0 + (lo - lon[0]) * K * S, 90 + (lat[1] - la) * S])

    def inside(q):
        return lon[0] < q[0] < lon[1] and lat[0] < q[1] < lat[1]

    runs = []
    for fname in ("ne_10m_land.geojson", "ne_10m_admin_0_boundary_lines_land.geojson"):
        is_border = "admin" in fname
        if is_border and not borders:
            continue
        for f in _geojson(fname):
            g = f["geometry"]
            if is_border and not any(b in json.dumps(f["properties"]) for b in borders):
                continue
            lines = g["coordinates"] if g["type"] in ("MultiPolygon", "MultiLineString") else [g["coordinates"]]
            for ln in lines:
                ring = np.asarray(ln[0] if g["type"].endswith("Polygon") else ln)
                if ring.ndim != 2 or not (ring[:, 0].max() > lon[0] and ring[:, 0].min() < lon[1]
                                          and ring[:, 1].max() > lat[0] and ring[:, 1].min() < lat[1]):
                    continue
                ok = np.array([inside(q) for q in ring])
                lab, n = ndimage.label(ok)
                for k in range(1, n + 1):
                    seg = ring[lab == k]
                    if len(seg) >= 5:
                        runs.append((is_border, np.array([P(*q) for q in seg])))
    w = (lon[1] - lon[0]) * K * S * 2 + 400
    pg = Paper(t0, [(t0, cx * 2, 1080, max(3300, min(3700, w))), (t1, cx * 2, 1090, max(3100, min(3500, w * 0.95)))])
    f = pg.fig
    coast = sorted([r for b_, r in runs if not b_], key=len, reverse=True)[:10]
    tot = sum(len(r) for r in coast) + 1
    t = t0 + 0.05
    for r in coast:
        d = coast_t * len(r) / tot
        step = max(1, len(r) // 400)
        f.stroke(r[::step], t, max(0.1, d), color="ink", width=2.4, ease_=0.2)
        t += d
    for b_, r in runs:
        if b_:
            f.stroke(r[::2], t, 0.3, color="ink", width=1.6, ease_=0.2)
            t += 0.3
    for (name, lo, la, tp, style, off) in places:
        p = P(lo, la)
        if style == "circle":
            f.circle(p, 22, 18, tp, 0.35)
        else:
            f.circle(p, 10, 9, tp, 0.2, color="ink", width=3)
        if name:
            f.text(name, p + np.array(off), 42, tp + 0.25, 0.45, color="ink", angle=-2)
    for (a, b_, tr, dur, bend, color) in routes:
        path = sk.resample(sk.bez(P(*a), P(*b_), bend), 3)
        s_ = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(path, axis=0).T))])
        dashes, q = [], 0.0
        while q < s_[-1]:
            i, j = np.searchsorted(s_, [q, q + 16])
            if j - i > 1:
                dashes.append(path[i:j])
            q += 28
        for k, dsh in enumerate(dashes):
            f.stroke(dsh, tr + k * dur / len(dashes), dur * 0.75 / len(dashes), color=color, width=3.4, ease_=0.1)
        tip, prev = path[-1], path[-6]
        f.arrow(prev - (tip - prev) * 0.01, tip, tr + dur, 0.2, color=color, width=3.4, bend=0)
    for (text, lo, la, tl, size, color) in labels:
        f.text(text, P(lo, la), size, tl, 0.5, color=color, angle=-3)
    pg.P = P
    return pg


def timeline_page(t0, t1, events, line_t=0.8, title=None):
    """A hand-drawn timeline across a page. events: [(t, x_frac, top_text, bottom_text, color)]."""
    pg = Paper(t0, [(t0, 1920, 1080, 3600), (t1, 1920, 1080, 3400)])
    f = pg.fig
    y, xa, xb = 560, 220, 1700
    f.stroke([(xa, y), ((xa + xb) / 2, y - 6), (xb, y)], t0 + 0.05, line_t, color="ink", width=3.2, ease_=0.3)
    f.arrow((xb - 10, y), (xb + 40, y), t0 + 0.05 + line_t, 0.15, color="ink", width=3.2, bend=0)
    if title:
        f.text(title, (xa, 260), 64, t0 + 0.1, 0.8, color="ink", angle=-2)
    for (te, xf, top, bottom, color) in events:
        x = xa + xf * (xb - xa)
        f.stroke([(x, y - 34), (x, y + 34)], te, 0.12, color=color, width=4, ease_=0.2)
        if top:
            f.text(top, (x - 70, y - 105), 68, te + 0.1, 0.45, color=color, angle=-3)
        if bottom:
            f.text(bottom, (x - 70, y + 100), 50, te + 0.4, 0.6, color="ink", angle=-3)
    return pg
