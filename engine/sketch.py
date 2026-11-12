"""Sketch test: an illustrator explaining on one continuous sketchbook page.

Everything lives on one big page (world px). The map is drawn live with a hand-wobbled, pressure-tapered pen; the
train drawing builds up in its real stages (rough pencil -> ink lines -> hatching -> watercolour wash) using the order
from stages.py. The camera glides across the page, finished lines boil gently, the tool in use is shown at the pen
point, and the pencil/pen/brush sounds are synthesised from the pen's actual speed.

    .venv/bin/python tools/sketch.py [--preview]     -> renders/sketch_test.mp4   (--preview: half size, 12 fps)
"""
import json
import math
import subprocess
import sys
import wave
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage, signal
from skimage.measure import approximate_polygon

sys.path.insert(0, str(Path(__file__).parent))
import stages  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GEO = Path(__file__).resolve().parent / "geo" / "ne_10m_land.geojson"
PREVIEW = "--preview" in sys.argv
OW, OH = (960, 540) if PREVIEW else (1920, 1080)
FPS = 12 if PREVIEW else 24
WW, WH = 6600, 2700  # the page, in world px (1.5 world px per output px at the default framing)
PS = 1.5  # paper texture is stored at world / PS
RNG = np.random.default_rng(7)

INK, PENCIL, RED = (34, 27, 22), (88, 86, 90), (172, 46, 38)
import ytf  # noqa: E402
HAND = ytf.font("hand")

# ---------------------------------------------------------------- paper


def make_paper():
    w, h = int(WW / PS), int(WH / PS)
    base = np.array([244, 239, 228], np.float32)
    mottle = ndimage.gaussian_filter(RNG.standard_normal((h // 4, w // 4)), 18)
    mottle = cv2.resize((mottle / mottle.std()).astype(np.float32), (w, h))
    fine = ndimage.gaussian_filter(RNG.standard_normal((h, w)), 0.7)
    fine /= fine.std()
    fibre = ndimage.gaussian_filter(RNG.standard_normal((h, w)), (0.6, 5))
    fibre /= fibre.std()
    lum = 2.2 * mottle + 1.6 * fine + 0.8 * fibre
    paper = np.clip(base[None, None] + lum[..., None] * np.array([1, 1, 1.15]), 0, 255).astype(np.uint8)
    grain = np.clip(0.5 + 0.22 * fine + 0.1 * fibre, 0, 1).astype(np.float32)  # tooth: pencil catches the high spots
    return paper, grain


# ---------------------------------------------------------------- hand-drawn strokes


def resample(pts, step):
    pts = np.asarray(pts, np.float64)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    s = np.concatenate([[0], np.cumsum(seg)])
    if s[-1] < step:
        return pts
    u = np.arange(0, s[-1], step)
    return np.stack([np.interp(u, s, pts[:, 0]), np.interp(u, s, pts[:, 1])], 1)


def wobble(pts, amp=2.0, wl=14):
    """Hand tremor: a smooth sideways drift along the line."""
    if len(pts) < 4:
        return pts
    d = np.gradient(pts, axis=0)
    n = np.stack([-d[:, 1], d[:, 0]], 1) / (np.hypot(*d.T)[:, None] + 1e-9)
    off = ndimage.gaussian_filter1d(RNG.standard_normal(len(pts)), wl)
    off = off / (np.abs(off).max() + 1e-9) * amp
    return pts + n * off[:, None]


class Stroke:
    """One pen-down stroke, drawn progressively into a layer with a pressure-tapered width."""

    def __init__(self, pts, layer, width, t0, dur, tool, ease=0.5):
        self.p = np.asarray(pts, np.float64)
        seg = np.hypot(*np.diff(self.p, axis=0).T)
        self.s = np.concatenate([[0], np.cumsum(seg)])
        L = self.s[-1]
        taper = np.minimum(1, (self.s + 1) / 16) ** 0.6 * np.minimum(1, (L - self.s + 1) / 26) ** 0.8
        press = 1 + 0.12 * ndimage.gaussian_filter1d(RNG.standard_normal(len(self.p)), 6) * 3
        self.w = width * np.clip(0.3 + 0.7 * taper, 0.3, 1) * press
        self.layer, self.t0, self.dur, self.tool, self.ease = layer, t0, dur, tool, ease
        self.done = 0  # index of last drawn point

    def frac(self, t):
        u = min(1.0, max(0.0, (t - self.t0) / self.dur))
        return (1 - self.ease) * u + self.ease * u * u * (3 - 2 * u)

    def pos(self, t):
        L = self.frac(t) * self.s[-1]
        return np.array([np.interp(L, self.s, self.p[:, 0]), np.interp(L, self.s, self.p[:, 1])])

    def draw(self, t, draws):
        n = int(np.searchsorted(self.s, self.frac(t) * self.s[-1], side="right"))
        d = draws[self.layer]
        for i in range(max(self.done, 1), min(n, len(self.p))):
            a, b, wa, wb = self.p[i - 1], self.p[i], self.w[i - 1] / 2, self.w[i] / 2
            v = b - a
            nv = np.array([-v[1], v[0]]) / (np.hypot(*v) + 1e-9)
            d.polygon([tuple(a + nv * wa), tuple(b + nv * wb), tuple(b - nv * wb), tuple(a - nv * wa)], fill=255)
            d.ellipse([b[0] - wb, b[1] - wb, b[0] + wb, b[1] + wb], fill=255)
        self.done = max(self.done, n)


class Text:
    """Handwritten label revealed left to right, as if written."""

    def __init__(self, text, xy, size, layer, t0, dur, tool="pen", angle=-3):
        font = ImageFont.truetype(HAND, size)
        box = font.getbbox(text)
        m = Image.new("L", (box[2] + 20, box[3] + 20))
        ImageDraw.Draw(m).text((10, 10), text, font=font, fill=255)
        m = m.rotate(angle, expand=True, resample=Image.BICUBIC)
        self.m, self.x, self.y = m, int(xy[0]), int(xy[1] - m.size[1] / 2)
        self.layer, self.t0, self.dur, self.tool, self.done = layer, t0, dur, tool, 0
        cols = np.asarray(m).max(0)
        self.cols = np.flatnonzero(cols > 0)

    def frac(self, t):
        return min(1.0, max(0.0, (t - self.t0) / self.dur))

    def pos(self, t):
        c = self.cols[min(len(self.cols) - 1, int(self.frac(t) * len(self.cols)))]
        col = np.flatnonzero(np.asarray(self.m)[:, c] > 0)
        y = col.mean() if len(col) else self.m.size[1] / 2
        return np.array([self.x + c, self.y + y + 6 * math.sin(c * 0.11)])

    def draw(self, t, layers):
        x1 = int(self.cols[0] + self.frac(t) * (self.cols[-1] - self.cols[0] + 1))
        if x1 <= self.done:
            return
        part = self.m.crop((self.done, 0, x1, self.m.size[1]))
        box = (self.x + self.done, self.y, self.x + x1, self.y + self.m.size[1])
        L = layers[self.layer]
        L.paste(ImageChops.lighter(L.crop(box), part), box)
        self.done = x1


def chunked(pts, layer, width, t0, t1, tool, lo=260, hi=520, gap=0.05):
    """Split a long line into several pen-down strokes (with tiny overlaps), timed by length."""
    parts, i = [], 0
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
    while i < len(pts) - 1:
        j = int(np.searchsorted(s, s[i] + RNG.uniform(lo, hi)))
        j = min(max(j, i + 2), len(pts))
        parts.append(pts[max(0, i - 2):j] + RNG.normal(0, 0.8, 2))
        i = j - 1
    lens = np.array([max(1.0, np.hypot(*np.diff(p, axis=0).T).sum()) for p in parts])
    span = (t1 - t0) - gap * len(parts)
    out, t = [], t0
    for p, L in zip(parts, lens):
        d = span * L / lens.sum()
        out.append(Stroke(p, layer, width, t, d, tool, ease=0.25))
        t += d + gap
    return out


def loop(c, rx, ry, t0, dur, layer="red", width=6.5, turns=1.18, tilt=-0.18):
    a0 = RNG.uniform(0, 2 * math.pi)
    a = a0 + np.linspace(0, 2 * math.pi * turns, 140)
    k = np.linspace(0, 1, len(a))
    r = 1 + 0.07 * np.sin(a * 2 + 1) + 0.08 * k
    x, y = rx * r * np.cos(a), ry * r * np.sin(a)
    pts = np.stack([x * math.cos(tilt) - y * math.sin(tilt) + c[0], x * math.sin(tilt) + y * math.cos(tilt) + c[1]], 1)
    return [Stroke(wobble(pts, 1.5, 8), layer, width, t0, dur, "red", ease=0.35)]


def bez(a, b, bend):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = (a + b) / 2 + np.array([-(b - a)[1], (b - a)[0]]) * bend
    u = np.linspace(0, 1, 60)[:, None]
    return (1 - u) ** 2 * a + 2 * (1 - u) * u * m + u ** 2 * b


def arrow(a, b, t0, dur, layer="red", width=6.5, bend=0.18, tool="red"):
    shaft = wobble(resample(bez(a, b, bend), 6), 1.2, 6)
    v = shaft[-1] - shaft[-5]
    ang = math.atan2(v[1], v[0])
    heads = []
    for s in (1, -1):
        h = ang + math.pi - s * 0.5
        tip = shaft[-1]
        heads.append(np.stack([tip, tip + 46 * np.array([math.cos(h), math.sin(h)])]))
    d = dur * 0.7
    return [Stroke(shaft, layer, width, t0, d, tool, ease=0.4),
            Stroke(resample(heads[0][::-1], 4), layer, width, t0 + d + 0.04, dur * 0.12, tool, 0.2),
            Stroke(resample(heads[1], 4), layer, width, t0 + d + 0.04 + dur * 0.16, dur * 0.12, tool, 0.2)]


# ---------------------------------------------------------------- the map (Natural Earth, public domain)

LON, LAT = (0.78, 2.3), (50.68, 51.32)
MX, MY, MW = 260, 470, 2700
KX = math.cos(math.radians(51.0))
MSCALE = MW / ((LON[1] - LON[0]) * KX)


def proj(lon, lat):
    return np.array([MX + (lon - LON[0]) * KX * MSCALE, MY + (LAT[1] - lat) * MSCALE])


def coast_runs():
    feats = json.load(open(GEO, encoding="utf-8"))["features"]
    runs, rings = [], []
    for f in feats:
        g = f["geometry"]
        polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
        for poly in polys:
            ring = np.asarray(poly[0])
            if ring[:, 0].max() < LON[0] - 0.5 or ring[:, 0].min() > LON[1] + 0.5 or \
               ring[:, 1].max() < LAT[0] - 0.5 or ring[:, 1].min() > LAT[1] + 0.5:
                continue
            rings.append(ring)
            inside = (ring[:, 0] > LON[0]) & (ring[:, 0] < LON[1]) & (ring[:, 1] > LAT[0]) & (ring[:, 1] < LAT[1])
            lab, n = ndimage.label(inside)
            for k in range(1, n + 1):
                seg = ring[lab == k]
                if len(seg) > 8:  # Great Britain's ring ends east of lon 2; the continent's runs far beyond
                    runs.append((ring[:, 0].max() < 2.0, np.array([proj(*p) for p in seg])))
    return runs, rings


def land_mask(rings):
    m = Image.new("L", (WW, WH))
    d = ImageDraw.Draw(m)
    for r in rings:
        d.polygon([tuple(proj(*p)) for p in r], fill=255)
    return np.asarray(m) > 0


# ---------------------------------------------------------------- tools at the pen point


def tool_sprite(kind, scale):
    """Pencil / fineliner / red pencil / brush drawn at the given scale, tip at the returned offset."""
    L = 560 * scale
    a = math.radians(32)  # body runs down and to the right of the tip, like a right hand
    c, s = math.cos(a), math.sin(a)
    W_, H_ = int(L * c + 80 * scale), int(L * s + 80 * scale)
    im = Image.new("RGBA", (W_, H_))
    d = ImageDraw.Draw(im)
    tip = np.array([16 * scale, 16 * scale])

    def P(pts):
        return [tuple(tip + np.array([x * c - y * s, x * s + y * c]) * scale) for x, y in pts]

    r = 15
    if kind in ("pencil", "red"):
        body = (52, 78, 62) if kind == "pencil" else (176, 44, 36)
        lead = (58, 58, 60) if kind == "pencil" else (160, 40, 34)
        d.polygon(P([(14, -4), (70, -r), (70, r), (14, 4)]), fill=(226, 196, 150))
        d.polygon(P([(0, 0), (16, -4.5), (16, 4.5)]), fill=lead)
        d.polygon(P([(70, -r), (560, -r), (560, r), (70, r)]), fill=body)
        d.polygon(P([(70, -r + 4), (560, -r + 4), (560, -r + 9), (70, -r + 9)]), fill=tuple(min(255, v + 40) for v in body))
        d.polygon(P([(70, -r), (74, -r - 2), (74, r + 2), (70, r)]), fill=(200, 170, 120))
    elif kind == "pen":
        d.polygon(P([(0, -1.5), (22, -2.5), (22, 2.5), (0, 1.5)]), fill=(150, 150, 150))
        d.polygon(P([(22, -8), (70, -13), (70, 13), (22, 8)]), fill=(40, 40, 42))
        d.polygon(P([(70, -14), (520, -14), (520, 14), (70, 14)]), fill=(26, 26, 28))
        d.polygon(P([(300, -14.5), (330, -14.5), (330, 14.5), (300, 14.5)]), fill=(120, 120, 124))
        d.polygon(P([(70, -10), (520, -10), (520, -6), (70, -6)]), fill=(70, 70, 74))
    else:  # brush
        d.polygon(P([(0, 0), (14, -9), (48, -11), (48, 11), (14, 9)]), fill=(110, 140, 170))
        d.polygon(P([(48, -11), (110, -9), (110, 9), (48, 11)]), fill=(180, 182, 186))
        d.polygon(P([(110, -9), (560, -12), (560, 12), (110, 9)]), fill=(150, 92, 48))
        d.polygon(P([(110, -6), (560, -8), (560, -4), (110, -3)]), fill=(186, 128, 80))
    al = im.split()[3]
    sh = Image.new("RGBA", im.size, (20, 14, 8, 0))
    sh.putalpha(al.point(lambda v: v * 0.22).filter(ImageFilter.GaussianBlur(6 * scale)))
    full = Image.new("RGBA", (W_ + int(40 * scale), H_ + int(40 * scale)))
    full.alpha_composite(sh, (int(22 * scale), int(28 * scale)))
    full.alpha_composite(im, (0, 0))
    return full, tip


# ---------------------------------------------------------------- timeline


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


CAM = [  # t, centre x, centre y, view width (world px)
    (0.0, 1640, 1330, 3050), (14.6, 1700, 1330, 2860), (15.5, 3300, 1330, 3800), (16.6, 4960, 1340, 3200),
    (30.4, 4930, 1350, 3100), (33.6, 4900, 1320, 3000)]
TX, TY, TW = 3500, 380, 2900  # where the train drawing sits on the page
STAGES = dict(rough=(16.7, 19.7), lines=(19.8, 23.8), shaded=(23.9, 27.9), wash=(28.0, 30.5))
END = 33.6


def camera(t):
    for (ta, *a), (tb, *b) in zip(CAM, CAM[1:]):
        if t <= tb:
            u = ease((t - ta) / (tb - ta))
            v = [x + (y - x) * u for x, y in zip(a, b)]
            break
    else:
        v = list(CAM[-1][1:])
    v[0] += 5 * math.sin(t * 0.7) + 3 * math.sin(t * 1.9)
    v[1] += 4 * math.sin(t * 0.5 + 1)
    return v


def build_map():
    runs, rings = coast_runs()
    land = land_mask(rings)
    eng = [r for gb, r in runs if gb]
    fra = [r for gb, r in runs if not gb]
    items = []

    def coast(group, t0, t1, w0, w1):
        group = sorted(group, key=lambda r: -len(r))[:4]
        lines = [wobble(resample(approximate_polygon(r, 2.2), 5), 2.0) for r in group]
        tot = sum(np.hypot(*np.diff(l, axis=0).T).sum() for l in lines)
        t = t0
        for l in lines:
            d = (t1 - t0) * np.hypot(*np.diff(l, axis=0).T).sum() / tot
            items.extend(chunked(l, "ink", 5.2, t, t + d - 0.04, "pen"))
            t += d
            # water-lining: broken pencil echoes on the sea side
        echoes = []
        for l in lines:
            g = np.gradient(l, axis=0)
            n = np.stack([-g[:, 1], g[:, 0]], 1) / (np.hypot(*g.T)[:, None] + 1e-9)
            probe = (l + n * 14).astype(int)
            ok = (probe[:, 0] >= 0) & (probe[:, 0] < WW) & (probe[:, 1] >= 0) & (probe[:, 1] < WH)
            sea_side = np.ones(len(l))
            sea_side[ok] = np.where(land[probe[ok, 1], probe[ok, 0]], -1, 1)
            sgn = 1 if np.median(sea_side) > 0 else -1
            for off, keep in ((16, 0.9), (32, 0.45)):
                e = ndimage.gaussian_filter1d(l + n * sgn * off, 3, axis=0)
                i = int(RNG.integers(0, 20))
                while i < len(e) - 6:
                    j = i + int(RNG.integers(8, 30))
                    if RNG.random() < keep:
                        echoes.append(e[i:min(j, len(e))])
                    i = j + int(RNG.integers(2, 9))
        L = np.array([np.hypot(*np.diff(e, axis=0).T).sum() + 30 for e in echoes])
        t = t1
        for e, l in zip(echoes, L):
            d = (w1 - w0) * l / L.sum()
            if len(e) > 2:
                items.append(Stroke(e, "pencil", 2.5, t, d * 0.8, "pencil", 0.2))
            t += d

    coast(eng, 0.3, 3.1, 3.1, 4.0)
    coast(fra, 4.1, 6.9, 6.9, 7.8)
    items.append(Text("ENGLAND", proj(0.86, 51.2), 118, "ink", 7.9, 0.75))
    items.append(Text("FRANCE", proj(1.98, 50.81), 118, "ink", 8.75, 0.7))
    fol, coq = proj(1.13, 51.093), proj(1.80, 50.93)
    items += loop(fol, 92, 70, 9.65, 0.55)
    items.append(Text("Folkestone", fol + [-470, -150], 76, "ink", 10.25, 0.6))
    items += loop(coq, 92, 70, 10.95, 0.55)
    items.append(Text("Calais", coq + [70, 140], 76, "ink", 11.55, 0.45))
    # the tunnel: a dashed line under the sea, drawn dash by dash
    path = resample(bez(fol + [40, 22], coq + [-45, -10], -0.08), 3)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(path, axis=0).T))])
    dashes, a = [], 0.0
    while a < s[-1]:
        i, j = np.searchsorted(s, [a, a + 30])
        if j - i > 1:
            dashes.append(path[i:j])
        a += 48
    for k, dsh in enumerate(dashes):
        items.append(Stroke(dsh, "ink", 7.5, 12.2 + k * (1.2 / len(dashes)), 0.9 / len(dashes), "pen", 0.1))
    mid = path[len(path) // 2]
    items.append(Text("50 km long", mid + [130, -300], 84, "ink", 13.55, 0.6, angle=-4))
    items += arrow(mid + [190, -240], mid + [14, -24], 14.2, 0.45, layer="ink", width=5, bend=0.25, tool="pen")
    return items


def build_annotations():
    def W(x, y):  # train-drawing px -> world
        return np.array([TX + x * TW / 1536, TY + y * TW / 1536])
    items = [Text("the first trains, 1994", W(70, 130), 92, "red", 30.7, 1.0, tool="red", angle=-4)]
    items += arrow(W(330, 190), W(330, 455), 31.75, 0.55, layer="red", bend=-0.2)
    return items


# ---------------------------------------------------------------- render


def main():
    paper, grain = make_paper()
    st = stages.build()
    f32 = {k: st[k].astype(np.float32) for k in ("rough", "lines", "shaded", "wash")}
    layers = {k: Image.new("L", (WW, WH)) for k in ("ink", "pencil", "red")}
    draws = {k: ImageDraw.Draw(v) for k, v in layers.items()}
    items = sorted(build_map() + build_annotations(), key=lambda i: i.t0)
    sc = OW / 1920
    sprites = {k: tool_sprite(k, 0.36 * sc) for k in ("pencil", "pen", "red", "brush")}  # small: the drawing is the point
    # boil: three gentle displacement fields, switched every 3 frames (24 fps) like re-traced animation lines
    gx, gy = np.meshgrid(np.arange(OW, dtype=np.float32), np.arange(OH, dtype=np.float32))
    boil = []
    for _ in range(3):
        dx = ndimage.gaussian_filter(RNG.standard_normal((OH, OW)), 30 * sc)
        dy = ndimage.gaussian_filter(RNG.standard_normal((OH, OW)), 30 * sc)
        k = 0.85 * sc / max(np.abs(dx).max(), np.abs(dy).max())
        boil.append(((gx + dx * k).astype(np.float32), (gy + dy * k).astype(np.float32)))
    dk = {k: 1 - np.array(c, np.float32) / 255 for k, c in (("ink", INK), ("pencil", PENCIL), ("red", RED))}

    out = ROOT / "renders" / ("sketch_test_preview.mp4" if PREVIEW else "sketch_test.mp4")
    out.parent.mkdir(exist_ok=True)
    silent = out.with_suffix(".silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", ytf.x264_preset(),
                           "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    nfr = int(END * FPS)
    pen_prev, pen_s, sound = None, None, []
    for fi in range(nfr):
        t = fi / FPS
        cx, cy, vw = camera(t)
        s = vw / OW  # world px per output px
        x0, y0 = cx - vw / 2, cy - vw * OH / OW / 2
        # live strokes
        active = None
        for it in items:
            if it.t0 <= t:
                it.draw(t, layers if isinstance(it, Text) else draws)
                if t <= it.t0 + it.dur + 0.02:
                    active = it
        # paper
        Mp = np.float32([[s / PS, 0, x0 / PS], [0, s / PS, y0 / PS]])
        pap = cv2.warpAffine(paper, Mp, (OW, OH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
        grn = cv2.warpAffine(grain, Mp, (OW, OH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
        # stroke layers: crop, prefilter, warp
        bx0, by0 = max(0, int(x0) - 4), max(0, int(y0) - 4)
        bx1, by1 = min(WW, int(x0 + vw) + 5), min(WH, int(y0 + vw * OH / OW) + 5)
        Ms = np.float32([[s, 0, x0 - bx0], [0, s, y0 - by0]])
        alph = []
        for k in ("ink", "pencil", "red"):
            a = np.asarray(layers[k].crop((bx0, by0, bx1, by1)), np.float32) / 255
            if s > 1.05:
                a = cv2.GaussianBlur(a, (0, 0), 0.42 * s)
            alph.append(cv2.warpAffine(a, Ms, (OW, OH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP))
        A = np.dstack(alph)
        # the staged train drawing
        ts = TW / 1536
        D = np.zeros((1024, 1536, 3), np.float32)
        if t >= STAGES["rough"][0] - 0.1:
            def rev(name, soft=0.05):
                a, b = STAGES[name]
                return np.clip((t - (a + st[f"T_{name}"] * (b - a))) / soft, 0, 1)

            def regional(name, fade=0.5):
                a, b = STAGES[name]
                return np.clip((t - (a + st[f"T_{name}"] * (b - a))) / fade, 0, 1)
            pl, ps_ = regional("lines"), regional("shaded")
            vr = rev("rough") * (1 - 0.65 * pl) * (1 - 0.7 * ps_)
            vl = rev("lines") * (1 - ps_)
            a, b = STAGES["wash"]
            w = np.clip((t - (a + st["T_wash"] * (b - a))) / 0.3, 0, 1)[..., None]
            sh = rev("shaded")[..., None] * f32["shaded"]
            top = (1 - w) * sh + w * f32["wash"]
            D = 1 - (1 - (vr * f32["rough"])[..., None]) * (1 - (vl * f32["lines"])[..., None]) * (1 - top)
        Mt = np.float32([[s / ts, 0, (x0 - TX) / ts], [0, s / ts, (y0 - TY) / ts]])
        Dt = cv2.warpAffine(D, Mt, (OW, OH), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP)
        mx, my = boil[(fi * 24 // FPS // 3) % 3]
        A = cv2.remap(A, mx, my, cv2.INTER_LINEAR)
        Dt = cv2.remap(Dt, mx, my, cv2.INTER_LINEAR)
        img = pap.astype(np.float32)
        img *= 1 - A[..., 0:1] * 0.95 * dk["ink"] * (0.9 + 0.1 * grn[..., None])
        img *= 1 - A[..., 1:2] * 0.5 * dk["pencil"] * (0.35 + 0.9 * grn[..., None])
        img *= 1 - A[..., 2:3] * 0.9 * dk["red"] * (0.55 + 0.6 * grn[..., None])
        img *= 1 - Dt * (0.92 + 0.08 * grn[..., None])
        frame = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")
        # the tool at the pen point
        tool, wpos = None, None
        if active is not None:
            tool, wpos = active.tool, active.pos(t)
        else:
            for name, (a, b) in STAGES.items():
                if a <= t <= b:
                    trk = st[f"trk_{name}"]
                    k = int(np.clip(np.searchsorted(trk[:, 0], (t - a) / (b - a)), 0, len(trk) - 1))
                    tool = {"rough": "pencil", "lines": "pen", "shaded": "pen", "wash": "brush"}[name]
                    wpos = np.array([TX + trk[k, 1] * ts, TY + trk[k, 2] * ts])
        speed = 0.0
        if tool:
            p = np.array([(wpos[0] - x0) / s, (wpos[1] - y0) / s])
            stage_tool = active is None
            if pen_s is None or pen_prev != tool:
                pen_s = p
            else:
                k = 0.35 if stage_tool else 1.0
                speed = float(np.hypot(*(p - pen_s))) * FPS / sc
                pen_s = pen_s + (p - pen_s) * k
            spr, tip = sprites[tool]
            px, py = int(pen_s[0] - tip[0]), int(pen_s[1] - tip[1])
            if -spr.size[0] < px < OW and -spr.size[1] < py < OH:
                layer = Image.new("RGBA", frame.size)
                layer.paste(spr, (px, py))
                frame = Image.alpha_composite(frame, layer)
        pen_prev = tool
        sound.append((tool, speed))
        ff.stdin.write(frame.convert("RGB").tobytes())
        if fi % (FPS * 2) == 0:
            print(f"{t:5.1f}s", flush=True)
    ff.stdin.close()
    ff.wait()
    wav = out.with_suffix(".wav")
    make_sound(sound, wav)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(out)], check=True)
    silent.unlink()
    print("wrote", out)


def make_sound(frames, path, sr=48000):
    """Pencil scratch, pen glide and brush swish, driven frame by frame by the pen's real speed."""
    n = int(len(frames) / FPS * sr)
    spf = sr / FPS
    rng = np.random.default_rng(11)
    white = rng.standard_normal(n).astype(np.float32)
    grit = np.abs(signal.sosfilt(signal.butter(2, 40, "lp", fs=sr, output="sos"), rng.standard_normal(n))).astype(np.float32)
    grit /= grit.max()
    voices = {"pencil": (signal.butter(2, [1800, 7000], "bp", fs=sr, output="sos"), 0.9, 0.7),
              "red": (signal.butter(2, [1600, 6500], "bp", fs=sr, output="sos"), 0.9, 0.7),
              "pen": (signal.butter(2, [2500, 9500], "bp", fs=sr, output="sos"), 0.45, 0.4),
              "brush": (signal.butter(2, [300, 2400], "bp", fs=sr, output="sos"), 0.55, 0.15)}
    mix = np.zeros(n, np.float32)
    for name, (sos, gain, scratch) in voices.items():
        env = np.array([min(1.0, sp / 900) ** 0.6 if tl == name else 0.0 for tl, sp in frames], np.float32)
        env = ndimage.gaussian_filter1d(env, 0.8)
        e = np.interp(np.arange(n) / spf, np.arange(len(env)), env).astype(np.float32)
        tex = signal.sosfilt(sos, white).astype(np.float32) * (1 - scratch + scratch * 2.2 * grit)
        mix += gain * e * tex
    mix += 0.004 * signal.sosfilt(signal.butter(1, 400, "lp", fs=sr, output="sos"), white).astype(np.float32)  # room
    mix *= 0.18 / (np.percentile(np.abs(mix), 99.9) + 1e-9)
    pcm = (np.clip(mix, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    main()
