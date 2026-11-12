"""fx3: depth, focus and light on the still pictures, and the screen-space paper label (Nov 2026, from the v2 test on
Carnegie's Daughter batch 4). Like fx2, everything here ADDS a layer or re-lights; no painted pixel is moved and
there is no 2.5D.

  depth maps   tools/depth.py makes build/depth/<image>.png (near = bright) for every scene picture, once per film
  Focus        depth of field with a keyed focal plane: the focus pulls from one person to another
  Snow / Rain  weather that lives in the scene: each flake has a depth and is hidden by anything nearer than it
               (snow behind a figure; z=(0, 0.12) keeps it outside a window)
  Haze         far parts of the picture lifted towards a mist colour
  FaceLight    soft form shading on the flat egg faces from the scene's light (a lamp, a window)
  Scrap        a pinned paper scrap as the ground for an inset drawing (fx2.Draw goes on top of it)
  Tag          a typed paper label in screen space: never cropped by the camera; it can stay up across cuts
               (b.overlay) and can point at someone with a leader (anchor=)

In a shot list these come through seq.scene(...): focus=, light=, haze=, snow_z=, label= (now a Tag), cam= (keys with
an ease per segment). Worked example: examples/chadwick/tools/shots_b4_v2.py.
"""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import film
from film import UP, SW, SH, ease, up
from fx2 import _blend, _sm

ROOT = film.ROOT
K = film.OH / 1080  # screen-space sizes are written for 1080p


def has_depth(img):
    return (ROOT / "build" / "depth" / f"{img}.png").exists()


# ---------------------------------------------------------------- depth
_D = {}


def depth(img):
    """The picture's depth map at source size (near = 1, far = 0); made by tools/depth.py."""
    if img not in _D:
        f = ROOT / "build" / "depth" / f"{img}.png"
        d = cv2.imread(str(f), cv2.IMREAD_UNCHANGED)
        if d is None:
            raise FileNotFoundError(f"{f}: no depth map; run tools/depth.py {img} (see references/engine.md)")
        _D[img] = cv2.GaussianBlur(d.astype(np.float32) / 65535, (0, 0), 1.2)
    return _D[img]


def depth_at(img, p, r=6):
    d = depth(img)
    x, y = int(p[0]), int(p[1])
    return float(np.median(d[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1]))


def _key(keys, t):
    """Linear-eased value of [(t, v...), ...] at t."""
    if t <= keys[0][0]:
        return keys[0][1:]
    for a, b in zip(keys, keys[1:]):
        if t <= b[0]:
            u = ease((t - a[0]) / max(1e-6, b[0] - a[0]))
            return tuple(x + (y - x) * u for x, y in zip(a[1:], b[1:]))
    return keys[-1][1:]


class Focus:
    """Depth of field. keys = [(t, focus, amount)]: focus is a depth (0-1) or a point (x, y) in source px whose
    depth is used; amount 0-1 is how soft the out-of-focus parts get. blur = the largest blur, in source px."""

    def __init__(self, img, keys, blur=4.5, span=0.30):
        self.d = depth(img)
        self.keys = [(t, depth_at(img, f) if isinstance(f, (tuple, list)) else float(f), float(a)) for t, f, a in keys]
        self.blur, self.span = blur, span
        self.dh = cv2.resize(self.d, (SW, SH))  # the blurred copies are made at source size (half the 2x working size)

    def __call__(self, a, t):
        f, amt = _key(self.keys, t)
        if amt <= 0.01:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        coc = np.clip((np.abs(self.dh - f) - self.span * 0.35) / self.span, 0, 1) * amt
        small = cv2.resize(a, (SW, SH), interpolation=cv2.INTER_AREA)
        b1 = cv2.GaussianBlur(small, (0, 0), self.blur * 0.45)
        b2 = cv2.GaussianBlur(small, (0, 0), self.blur)
        w2 = np.clip(coc * 2 - 1, 0, 1)[..., None]
        mix = cv2.resize(b1 * (1 - w2) + b2 * w2, (SW * UP, SH * UP), interpolation=cv2.INTER_LINEAR)
        w1 = cv2.resize(np.clip(coc * 2, 0, 1), (SW * UP, SH * UP), interpolation=cv2.INTER_LINEAR)[..., None]
        return a * (1 - w1) + mix * w1


class Haze:
    """Mist in the distance: far parts of the picture are lifted towards `color`, breathing slowly."""

    def __init__(self, img, amount=0.3, color=(176, 180, 196), power=1.6, seed=3):
        far = np.clip(1 - depth(img) * 1.6, 0, 1) ** power
        r = np.random.default_rng(seed)
        nz = cv2.resize(r.random((6, 12)).astype(np.float32), (SW, SH), interpolation=cv2.INTER_CUBIC)
        self.m = cv2.resize(far * (0.75 + 0.5 * nz), (SW * UP, SH * UP))[..., None] * amount
        self.col = np.array(color, np.float32)

    def __call__(self, a, t):
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        k = 1 + 0.12 * math.sin(t * 0.5)
        return a + (self.col - a) * (self.m * k)


class Snow:
    """Snow that lives in the scene. Each flake has a depth z (1 = right at the lens) and is hidden wherever the
    picture is nearer than it. z = (lo, hi) limits where flakes can be: z=(0, 0.3) keeps them outside a window."""

    def __init__(self, img, amount=0.4, z=(0.05, 1.0), n=520, seed=1, wind=14.0):
        r = np.random.default_rng(seed)
        self.d = depth(img)
        n = int(n * amount / 0.4)
        self.x, self.y = r.uniform(0, SW, n), r.uniform(0, SH, n)
        self.z = z[0] + (z[1] - z[0]) * r.uniform(0, 1, n) ** 1.5
        self.ph, self.wind = r.uniform(0, 6.3, n), wind

    def __call__(self, a, t):
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        H, W = a.shape[:2]
        lay = np.zeros((H, W), np.float32)
        sp = 26 + 95 * self.z
        x = (self.x + self.wind * t * (0.4 + self.z) + 9 * np.sin(t * 1.1 + self.ph)) % SW
        y = (self.y + sp * t) % SH
        vis = self.d[np.clip(y.astype(int), 0, SH - 1), np.clip(x.astype(int), 0, SW - 1)] < self.z + 0.02
        for xi, yi, zi in zip(x[vis], y[vis], self.z[vis]):
            cv2.circle(lay, (int(xi * UP), int(yi * UP)), int(max(1, (0.8 + 2.6 * zi) * UP / 2 + 0.5)), float(0.45 + 0.45 * zi), -1, cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 1.1)[..., None]
        return a + (np.float32(248) - a) * lay


class Rain:
    """Rain with depth: slanted streaks, hidden by anything nearer than they are."""

    def __init__(self, img, amount=0.35, z=(0.05, 1.0), n=700, seed=2, slant=0.14):
        r = np.random.default_rng(seed)
        self.d = depth(img)
        n = int(n * amount / 0.35)
        self.x, self.y = r.uniform(0, SW, n), r.uniform(0, SH, n)
        self.z = z[0] + (z[1] - z[0]) * r.uniform(0, 1, n) ** 1.3
        self.slant = slant

    def __call__(self, a, t):
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        H, W = a.shape[:2]
        lay = np.zeros((H, W), np.float32)
        sp = 420 + 900 * self.z
        y = (self.y + sp * t) % SH
        x = (self.x - self.slant * sp * t) % SW
        vis = self.d[np.clip(y.astype(int), 0, SH - 1), np.clip(x.astype(int), 0, SW - 1)] < self.z + 0.02
        for xi, yi, zi in zip(x[vis], y[vis], self.z[vis]):
            L = (10 + 34 * zi) * UP
            cv2.line(lay, (int(xi * UP), int(yi * UP)), (int(xi * UP + self.slant * L), int(yi * UP - L)),
                     float(0.24 + 0.34 * zi), 1 + int(zi > 0.6), cv2.LINE_AA)
        lay = cv2.GaussianBlur(lay, (0, 0), 0.8)[..., None]
        return a + (np.float32(214) - a) * lay


# ---------------------------------------------------------------- faces: form shading on the flat eggs
class FaceLight:
    """Soft form shading on every egg face (and hand) in the picture, from a light at `light` (source px): the side
    away from the light turns a little darker and cooler, the near side a little warmer, the middle is untouched."""

    def __init__(self, img, light, shadow=0.20, warm=0.07, min_area=500):
        a = cv2.resize(up(img), (SW, SH), interpolation=cv2.INTER_AREA)
        hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
        h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
        skin = ((h >= 6) & (h <= 21) & (s >= 55) & (s <= 160) & (v >= 140)).astype(np.uint8)
        skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        n, lab, st, cen = cv2.connectedComponentsWithStats(skin)
        mul = np.zeros((SH, SW), np.float32)
        add = np.zeros((SH, SW), np.float32)
        for i in range(1, n):
            x, y, w, hh, A = st[i]
            if A < min_area:
                continue
            blob = (lab == i).astype(np.uint8)
            cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            c = max(cnts, key=cv2.contourArea)
            if cv2.contourArea(c) / max(1.0, cv2.contourArea(cv2.convexHull(c))) < 0.72:
                continue
            pad = 6
            x0, y0, x1, y1 = max(0, x - pad), max(0, y - pad), min(SW, x + w + pad), min(SH, y + hh + pad)
            m = np.zeros((y1 - y0, x1 - x0), np.uint8)
            cv2.drawContours(m, [c - [x0, y0]], -1, 1, -1)
            dt = cv2.distanceTransform(m, cv2.DIST_L2, 5)
            R = max(4.0, float(dt.max()))
            nrm = np.clip(dt / R, 0, 1)
            z = np.sqrt(np.clip(1 - (1 - nrm) ** 2, 0, 1)) * R          # a dome over the face
            z = cv2.GaussianBlur(z, (0, 0), max(1.0, R / 7))
            gx, gy = cv2.Sobel(z, cv2.CV_32F, 1, 0, ksize=3) / 8, cv2.Sobel(z, cv2.CV_32F, 0, 1, ksize=3) / 8
            lx, ly = light[0] - cen[i][0], light[1] - cen[i][1]
            ln = math.hypot(lx, ly) + 1e-6
            lam = (-gx * lx / ln - gy * ly / ln)                           # > 0 on the side facing the light
            lam = cv2.GaussianBlur(lam, (0, 0), max(1.0, R / 9))
            lam /= max(1e-6, np.abs(lam).max())
            soft = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 1.2)
            mul[y0:y1, x0:x1] = np.maximum(mul[y0:y1, x0:x1], np.clip(-lam, 0, 1) ** 1.3 * soft)
            add[y0:y1, x0:x1] = np.maximum(add[y0:y1, x0:x1], np.clip(lam, 0, 1) ** 1.5 * soft)
        big = (SW * UP, SH * UP)
        self.mul = cv2.resize(mul, big)[..., None] * shadow
        self.add = cv2.resize(add, big)[..., None] * warm
        self.cool = np.array([0.80, 0.86, 1.0], np.float32)  # shadows lean a little cool
        self.warm = np.array([255, 226, 190], np.float32)

    def __call__(self, a, t):
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        a = a * (1 - self.mul * (1 + (1 - self.cool)))  # darker, and red falls a little more than blue
        return a + (self.warm - a) * self.add


# ---------------------------------------------------------------- a pinned paper scrap (for an inset drawing)
class Scrap:
    """A scrap of cream paper pinned onto the picture at `at` (centre, source px), size (w, h): the ground for a
    drawing made live on top of it (fx2.Draw placed after it in the same shot). It drops on at t0 with its shadow."""

    def __init__(self, at, size, t0, t_out=None, tilt=-2.5, seed=5):
        r = np.random.default_rng(seed)
        w, h = int(size[0] * UP), int(size[1] * UP)
        P = 40
        al = np.zeros((h + 2 * P, w + 2 * P), np.float32)
        pts = []
        for k in range(40):  # an uneven, hand-torn rectangle
            u = k / 40 * 4
            side, f = int(u), u - int(u)
            j = r.normal(0, 2.2)
            pts.append([(P + f * w, P + j), (P + w + j, P + f * h), (P + w - f * w, P + h + j), (P + j, P + h - f * h)][side])
        cv2.fillPoly(al, [np.array(pts, np.int32)], 1.0, cv2.LINE_AA)
        M = cv2.getRotationMatrix2D(((w + 2 * P) / 2, (h + 2 * P) / 2), tilt, 1.0)
        al = cv2.warpAffine(al, M, (w + 2 * P, h + 2 * P))
        self.al = cv2.GaussianBlur(al, (0, 0), 0.8)
        rgb = np.empty((h + 2 * P, w + 2 * P, 3), np.float32)
        rgb[:] = (243, 234, 213)
        tex = cv2.GaussianBlur(r.standard_normal((h + 2 * P, w + 2 * P)).astype(np.float32), (0, 0), 2.5) * 5
        fib = cv2.GaussianBlur(r.standard_normal((h + 2 * P, w + 2 * P)).astype(np.float32), (0, 0), 14) * 9
        rgb += (tex + fib)[..., None]
        edge = np.clip(self.al - cv2.GaussianBlur(self.al, (0, 0), 6), 0, 1)[..., None]
        rgb -= edge * 30                                              # the torn edge is a touch darker
        px, py = (w + 2 * P) // 2, P + 14                             # a brass pin, top centre
        cv2.circle(rgb, (px + 3, py + 4), 9, (120, 104, 84), -1, cv2.LINE_AA)
        cv2.circle(rgb, (px, py), 8, (176, 54, 44), -1, cv2.LINE_AA)
        cv2.circle(rgb, (px - 2, py - 3), 3, (236, 150, 130), -1, cv2.LINE_AA)
        self.rgb = rgb
        self.sh = cv2.GaussianBlur(self.al, (0, 0), 9) * 0.42
        self.pos = (int(at[0] * UP - w / 2 - P), int(at[1] * UP - h / 2 - P))
        self.t0, self.t_out = t0, t_out

    def __call__(self, a, t):
        if t < self.t0:
            return a
        k = _sm((t - self.t0) / 0.22) * (1.0 if self.t_out is None else 1 - _sm((t - self.t_out) / 0.4))
        if k <= 0:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        drop = int((1 - _sm((t - self.t0) / 0.22)) * 26)             # falls the last few px onto the picture
        X, Y = self.pos
        a = _blend(a, X + 10, Y + 14, np.zeros_like(self.rgb), self.sh * k)
        return _blend(a, X, Y - drop, self.rgb, self.al * k)


# ---------------------------------------------------------------- a screen-space label
def _font(size):
    for idx in (1, 0):
        try:
            return ImageFont.truetype(film.TYPE_FONT, int(size), index=idx)
        except Exception:
            continue
    return ImageFont.load_default()


class Tag:
    """A typed paper label in screen space (post=[...]): it slides in, types itself key by key, and leaves. It never
    moves with the camera, so a push-in cannot crop it. pos = its left end (right end with align="r") and vertical
    middle as fractions of the frame. anchor = a point in the picture (source px): a thin ink leader runs from the tag to it."""

    def __init__(self, text, t0, t1, pos=(0.045, 0.85), size=62, anchor=None, cps=22.0, align="l"):
        size = size * K
        f = _font(size)
        tw = int(f.getlength(text))
        pad = int(size * 0.55)
        w, h = tw + 2 * pad, int(size * 1.9)
        im = Image.new("L", (w, h), 0)
        ImageDraw.Draw(im).text((pad, h / 2), text, font=f, fill=255, anchor="lm")
        self.txt = np.asarray(im, np.float32) / 255
        self.cut = [pad + int(f.getlength(text[:i])) + 2 for i in range(len(text) + 1)]
        r = np.random.default_rng(len(text) + 11)
        al = np.ones((h, w), np.float32)
        for side in (0, 1):  # torn ends
            j = np.cumsum(r.normal(0, 1.0, h)).astype(int) % max(2, int(5 * K)) + int(3 * K)
            for y in range(h):
                if side:
                    al[y, w - j[y]:] = 0
                else:
                    al[y, :j[y]] = 0
        self.al = cv2.GaussianBlur(al, (0, 0), 0.7)
        paper = np.empty((h, w, 3), np.float32)
        paper[:] = (242, 233, 210)
        paper += cv2.GaussianBlur(r.standard_normal((h, w)).astype(np.float32), (0, 0), 2)[..., None] * 5
        paper[int(3 * K):int(3 * K) + max(1, int(2 * K)), :] *= 0.93  # a ruled edge, top and bottom
        paper[h - int(3 * K) - max(1, int(2 * K)):h - int(3 * K), :] *= 0.93
        self.paper = paper
        self.sh = cv2.GaussianBlur(np.pad(self.al, 16), (0, 0), 6) * 0.38
        self.ink = np.array([34, 28, 24], np.float32)
        self.t0, self.t1, self.pos, self.anchor, self.cps, self.n = t0, t1, pos, anchor, cps, len(text)
        self.type_t = (t0 + 0.3, t0 + 0.3 + len(text) / cps)
        self.w, self.h, self.align = w, h, align

    @staticmethod
    def _put(img, rgb, al, x, y):
        H, W = img.shape[:2]
        h, w = al.shape
        X0, Y0, X1, Y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
        if X1 <= X0 or Y1 <= Y0:
            return img
        m = al[Y0 - y:Y1 - y, X0 - x:X1 - x][..., None]
        c = rgb if rgb.ndim == 1 else rgb[Y0 - y:Y1 - y, X0 - x:X1 - x]
        img[Y0:Y1, X0:X1] = img[Y0:Y1, X0:X1] * (1 - m) + c * m
        return img

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t0 or t > self.t1 + 0.3:
            return img
        img = img if img.dtype == np.float32 else img.astype(np.float32)
        H, W = img.shape[:2]
        k_out = 1 - _sm((t - self.t1) / 0.3)
        slide = 1 - ease((t - self.t0) / 0.3, "out")
        if self.align == "r":  # pos[0] is its right end; it slides in from the right
            x = int(self.pos[0] * W - self.w + slide * ((1 - self.pos[0]) * W + self.w))
        else:
            x = int(self.pos[0] * W - slide * (self.pos[0] * W + self.w))
        y = int(self.pos[1] * H - self.h / 2)
        n = int(np.clip((t - self.type_t[0]) * self.cps, 0, self.n))
        m = self.txt.copy()
        m[:, self.cut[n]:] = 0
        rgb = self.paper * (1 - m[..., None] * 0.92) + self.ink * m[..., None] * 0.92
        if self.anchor is not None and s is not None and t > self.type_t[1]:
            g = ease((t - self.type_t[1]) / 0.3) * k_out
            ax, ay = s.to_screen(self.anchor, cam)
            sx = x + self.w if ax > x + self.w / 2 else x
            sy = y + self.h / 2
            ex, ey = sx + (ax - sx) * g, sy + (ay - sy) * g
            lay = np.zeros((H, W), np.float32)
            cv2.line(lay, (int(sx), int(sy)), (int(ex), int(ey)), 1.0, max(1, int(3 * K)), cv2.LINE_AA)
            if g > 0.98:
                cv2.circle(lay, (int(ax), int(ay)), int(6 * K), 1.0, -1, cv2.LINE_AA)
            halo = cv2.GaussianBlur(cv2.dilate(lay, np.ones((5, 5), np.uint8)), (0, 0), 2 * K)[..., None] * 0.7 * k_out
            img = img * (1 - halo) + np.array([246, 238, 220], np.float32) * halo
            img = img * (1 - lay[..., None] * k_out) + self.ink * lay[..., None] * k_out
        img = self._put(img, np.zeros(3, np.float32), self.sh * k_out, x - 16 + int(5 * K), y - 16 + int(7 * K))
        return self._put(img, rgb, self.al * k_out, x, y)


def tag(b, text, t0, t1, corner=None, **kw):
    """A Tag with its typing sound. corner = "bl" (default place), "tl", "br", "tr", or give pos=(x, y)."""
    if corner:
        kw["pos"], kw["align"] = CORNERS[corner]
    g = Tag(text, t0, t1, **kw)
    b.fx("type", g.type_t[0], g.type_t[1], db=-17)
    return g


CORNERS = {"bl": ((0.045, 0.85), "l"), "tl": ((0.045, 0.13), "l"), "br": ((0.955, 0.85), "r"), "tr": ((0.955, 0.13), "r")}
