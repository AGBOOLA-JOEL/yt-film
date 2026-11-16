"""Effects layer 2 (Chadwick, Nov 2026): effects that ADD to the picture instead of bending its pixels.

An audit of an earlier film showed that warping painted smoke (signature.Flow) melts the
picture. Everything here draws a new layer over the still image, in source px (moves with the camera):

  Smoke(origin, ...)        particle smoke: puffs that rise, curl, grow and fade (chimneys, cigars, steam engines)
  Breath(origin, times)     short puffs of cold breath (horses, people in winter)
  Flame(p, h)               a living candle / lamp / gas flame, with its light breathing on the picture
  Light(p, radius)          warm light that flickers on the scene (a lamp, a fire, a chandelier)
  Lift(img, poly, keys)     an object cut out of the picture and animated (a note slipping from a muff, falling, landing)
  Draw(sheet, panel, at, h) a proper drawing made live: the line art inks itself stroke by stroke, then the colour
                            washes in; optional `card` = a soft cream wash first, so it reads on a busy picture
  Tear(t0)                  the whole picture is a paper that tears in two and falls apart
  Counter(...)              (post) a rolling-digit money counter on a paper tag
  shatter(a, b, u, tr)      (transition) the outgoing picture cracks and falls away in glass shards

Shots: `b.custom(t0, Live(img, [effects...]), cam_keys, img, marks=..., post=[...])` gives the drawing pen its
sprite and sound. Plain `b.scene(..., src_fx=[...])` also works for effects without a pen.
"""
import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import film
import look
import ytf
from film import UP, SW, SH, OW, OH, up, ease

RNG = np.random.default_rng(7)


def _sm(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def _blend(a, x0, y0, rgb, al):
    """Composite rgb (h,w,3 float) with alpha al (h,w) onto a (2x image, float or uint8) at x0, y0, clipped."""
    H, W = a.shape[:2]
    h, w = al.shape
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return a
    sa = al[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None]
    sr = rgb[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0] if rgb.ndim == 3 else rgb
    reg = a[Y0:Y1, X0:X1].astype(np.float32)
    a[Y0:Y1, X0:X1] = reg * (1 - sa) + sr * sa
    return a


def clean_text(name, polys, k=11, keep=0.08):
    """A copy of an image with the thin dark writing inside polys lifted off the paper (a grey closing: the paper's
    own texture stays, unlike inpainting, which smears). Returns the new image's name (build/edit)."""
    out = film.BUILD / "edit" / f"{name}_clean2.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        a = cv2.imread(str(film.find_img(name)))
        H, W = a.shape[:2]
        f = W / SW
        crop = (H - round(W * SH / SW)) // 2 if W / H < SW / SH else 0
        m = np.zeros((H, W), np.uint8)
        cv2.fillPoly(m, [(np.array(q, np.float32) * f + [0, crop]).astype(np.int32) for q in polys], 255)
        ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
        clean = cv2.morphologyEx(a, cv2.MORPH_CLOSE, ker)
        clean = cv2.medianBlur(clean, 3)
        tex = a.astype(np.float32) - cv2.GaussianBlur(a.astype(np.float32), (0, 0), 1.2)
        dark = (cv2.cvtColor(a, cv2.COLOR_BGR2GRAY).astype(np.float32) < cv2.cvtColor(clean, cv2.COLOR_BGR2GRAY).astype(np.float32) - 18)
        tex[dark] = 0
        clean = np.clip(clean.astype(np.float32) + tex * 0.6, 0, 255)
        w = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 5)[..., None] * (1 - keep)
        cv2.imwrite(str(out), np.clip(a * (1 - w) + clean * w, 0, 255).astype(np.uint8))
    return f"{name}_clean2"


def u8(*fs):
    """Wrap effects for a plain scene's src_fx list (faces etc. expect uint8 images)."""
    def wrap(f):
        def g(a, t):
            return np.clip(f(a, t), 0, 255).astype(np.uint8)
        g.pen = getattr(f, "pen", None)
        return g
    return [wrap(f) for f in fs]


class Live:
    """A shot built from one picture plus effects layers (for b.custom: gives the pen its sprite and sound)."""

    def __init__(self, img, items):
        self.img, self.items = img, list(items)

    def img2x(self, t):
        a = up(self.img).astype(np.float32)
        for f in self.items:
            a = f(a, t)
        return a

    def pen(self, t):
        for f in reversed(self.items):
            p = getattr(f, "pen", None)
            if p is not None:
                q = p(t)
                if q is not None:
                    return q
        return None


# ---------------------------------------------------------------- smoke


def _puffs(n=8, size=160, seed=3):
    """Soft, clumpy painted puffs (alpha, shade), like gouache smoke: fractal noise inside a round falloff."""
    r = np.random.default_rng(seed)
    out = []
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / (size - 1) * 2 - 1
    rad = np.hypot(xx, yy)
    for _ in range(n):
        noise = np.zeros((size, size), np.float32)
        for oc, amp in ((4, 1.0), (8, 0.5), (16, 0.25)):
            noise += amp * cv2.resize(r.random((oc, oc)).astype(np.float32), (size, size), interpolation=cv2.INTER_CUBIC)
        noise /= 1.75
        shape = np.clip(1 - rad * (0.9 + 0.5 * (noise - 0.5)), 0, 1)
        al = np.clip((shape - 0.18) / 0.5, 0, 1) ** 1.2
        al = cv2.GaussianBlur(al, (0, 0), size / 60)
        shade = np.clip(0.55 + 0.45 * (-(xx + yy) * 0.5) + 0.25 * (noise - 0.5), 0, 1)  # lit from the top left
        out.append((al.astype(np.float32), shade.astype(np.float32)))
    return out


PUFFS = _puffs()


class Smoke:
    """Particle smoke from `origin` (source px). Puffs are born `rate` per second, live `life` s, rise `rise` px/s
    (slowing as they cool), drift with `wind` (px/s), grow from size[0] to size[1] px across, curl, and fade.
    t0/t1: when it starts/stops (it is already going at the shot's start unless t0 is given). `color` is the
    smoke's mid tone; `light` the lit side. Coal smoke: dark grey; steam/breath: near-white, short life."""

    def __init__(self, origin, t0=None, t1=1e9, rate=5.0, life=5.0, rise=45.0, wind=(18.0, 0.0), size=(18, 110),
                 color=(96, 94, 98), light=(170, 166, 168), alpha=0.8, spread=5.0, curl=14.0, seed=1, windows=None):
        self.o = np.array(origin, np.float32)
        self.t0, self.t1, self.rate, self.life, self.rise = t0, t1, rate, life, rise
        self.wind, self.size, self.alpha, self.spread, self.curl = np.array(wind, np.float32), size, alpha, spread, curl
        self.col, self.lit = np.array(color, np.float32), np.array(light, np.float32)
        self.seed, self.windows = seed, windows
        self._cache = {}

    def _p(self, i):
        r = np.random.default_rng(self.seed * 100003 + i + 50000)
        return dict(j=r.uniform(0, 1), dx=r.normal(0, self.spread), k=r.integers(len(PUFFS)), ph=r.uniform(0, 6.28),
                    s=r.uniform(0.8, 1.2), fl=bool(r.integers(2)), a=r.uniform(0.75, 1.0), v=r.uniform(0.8, 1.2))

    def _sprite(self, k, d, fl):
        key = (k, d, fl)
        if key not in self._cache:
            al, sh = PUFFS[k]
            al = cv2.resize(al, (d, d), interpolation=cv2.INTER_AREA)
            sh = cv2.resize(sh, (d, d), interpolation=cv2.INTER_AREA)
            if fl:
                al, sh = al[:, ::-1], sh[:, ::-1]
            rgb = self.col[None, None] * (1 - sh[..., None]) + self.lit[None, None] * sh[..., None]
            self._cache[key] = (np.ascontiguousarray(al), rgb.astype(np.float32))
            if len(self._cache) > 400:
                self._cache.pop(next(iter(self._cache)))
        return self._cache[key]

    def __call__(self, a, t):
        if t > self.t1 + self.life or (self.t0 is not None and t < self.t0):
            return a
        start = self.t0 if self.t0 is not None else -1e3
        i0 = int(math.floor((max(start, t - self.life)) * self.rate)) - 1
        i1 = int(math.floor(min(t, self.t1) * self.rate))
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        for i in range(i0, i1 + 1):
            p = self._p(i)
            tb = (i + p["j"]) / self.rate
            if tb < start or tb > min(t, self.t1):
                continue
            if self.windows and not any(w0 <= tb <= w1 for w0, w1 in self.windows):
                continue
            u = t - tb
            k = u / (self.life * p["v"])
            if not 0 <= k < 1:
                continue
            rise = self.rise * u * (1 - 0.35 * k)
            curl = self.curl * k * math.sin(u * 1.1 + p["ph"])
            x = self.o[0] + p["dx"] * (1 + 2 * k) + self.wind[0] * u + curl
            y = self.o[1] - rise + self.wind[1] * u
            dia = (self.size[0] + (self.size[1] - self.size[0]) * (1 - (1 - k) ** 2)) * p["s"]
            op = self.alpha * p["a"] * _sm(u / 0.35) * (1 - k) ** 1.6
            d = max(4, int(dia * UP / 4) * 4)
            al, rgb = self._sprite(p["k"], d, p["fl"])
            a = _blend(a, int(x * UP - d / 2), int(y * UP - d / 2), rgb, al * op)
        return a


def Breath(origin, times, direction=(-1, 0.15), dur=0.5, size=(6, 40), color=(225, 228, 232), seed=4, **kw):
    """Cold breath: a short white puff from `origin` at each time in `times`, blown along `direction`."""
    d = np.array(direction, np.float32)
    d = d / (np.linalg.norm(d) + 1e-6)
    return Smoke(origin, t0=min(times) - 0.1, rate=22, life=1.4, rise=6, wind=tuple(d * 40), size=size, color=color,
                 light=(250, 250, 252), alpha=0.42, spread=2.0, curl=4.0, seed=seed,
                 windows=[(s, s + dur) for s in times], **kw)


# ---------------------------------------------------------------- flame and light


class Light:
    """Warm light breathing on the picture around p (source px): an additive glow of `radius` px."""

    def __init__(self, p, radius, amount=0.25, color=(255, 196, 120), flicker=0.35, seed=2, t0=-1e9, t1=1e9):
        self.p, self.r, self.amount, self.col, self.fl, self.seed = p, radius, amount, np.array(color, np.float32), flicker, seed
        self.t0, self.t1 = t0, t1
        R = int(radius * UP * 2.2)
        yy, xx = np.mgrid[-R:R, -R:R].astype(np.float32)
        self.g = np.exp(-(xx ** 2 + yy ** 2) / (2 * (radius * UP) ** 2)).astype(np.float32)
        self.R = R

    def level(self, t):
        f = 0.6 * math.sin(t * 13.1 + self.seed) + 0.3 * math.sin(t * 23.7 + 2 * self.seed) + 0.25 * math.sin(t * 5.3)
        return self.amount * (1 + self.fl * f * 0.5) * _sm((t - self.t0) / 0.3) * (1 - _sm((t - self.t1) / 0.3))

    def __call__(self, a, t):
        k = self.level(t)
        if k <= 0:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        x0, y0 = int(self.p[0] * UP) - self.R, int(self.p[1] * UP) - self.R
        H, W = a.shape[:2]
        X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(W, x0 + 2 * self.R), min(H, y0 + 2 * self.R)
        g = self.g[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0][..., None] * k
        reg = a[Y0:Y1, X0:X1].astype(np.float32)
        a[Y0:Y1, X0:X1] = reg + (self.col - reg * 0.35) * g  # brightens and warms, never pure white
        return a


class Flame:
    """A small living flame at p (its base, source px), h px tall: a teardrop that sways and flickers, a hot core,
    and its own Light on the picture around it."""

    def __init__(self, p, h, light=None, seed=1, color=(255, 168, 64), core=(255, 244, 214), t0=-1e9, t1=1e9):
        self.p, self.h, self.seed, self.col, self.core = np.array(p, np.float32), h, seed, np.array(color, np.float32), np.array(core, np.float32)
        self.t0, self.t1 = t0, t1
        self.light = Light(p, h * 6, **(light or {}), seed=seed, t0=t0, t1=t1) if light is not False else None

    def __call__(self, a, t):
        if t < self.t0 or t > self.t1 + 0.3:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        if self.light is not None:
            a = self.light(a, t)
        s = self.seed
        fl = 1 + 0.10 * math.sin(t * 19 + s) + 0.06 * math.sin(t * 31 + 2 * s) + 0.05 * math.sin(t * 7.3 + s)
        h = self.h * fl * UP * _sm((t - self.t0) / 0.25)
        if h < 2:
            return a
        w = h * 0.36
        sway = h * (0.10 * math.sin(t * 4.1 + s) + 0.05 * math.sin(t * 9.7 + s))
        B = int(h * 1.6)
        pad = np.zeros((2 * B, 2 * B), np.float32)
        c = np.array([B, B * 1.5])
        pts = []
        for k in range(40):
            th = k / 39 * 2 * math.pi
            # teardrop: round bottom, pointed, leaning top
            yy = -math.cos(th)
            xx = math.sin(th) * (1 - yy) ** 0.5 * 0.71
            y = c[1] - (yy + 1) / 2 * h
            x = c[0] + xx * w + sway * ((yy + 1) / 2) ** 2
            pts.append((x, y))
        cv2.fillPoly(pad, [np.int32(pts)], 1.0, cv2.LINE_AA)
        outer = cv2.GaussianBlur(pad, (0, 0), max(1, h / 18))
        inner = cv2.GaussianBlur(cv2.erode(pad, np.ones((max(1, int(w * 0.6)),) * 2, np.uint8)), (0, 0), max(1, h / 14))
        glow = cv2.GaussianBlur(pad, (0, 0), h / 2.2) * 0.45
        x0, y0 = int(self.p[0] * UP - B), int(self.p[1] * UP - B * 1.5)
        rgb = np.ones((2 * B, 2 * B, 3), np.float32)
        a = _blend(a, x0, y0, rgb * np.array((255, 190, 110), np.float32), glow)
        a = _blend(a, x0, y0, rgb * self.col, outer * 0.95)
        a = _blend(a, x0, y0, rgb * self.core, inner)
        return a


# ---------------------------------------------------------------- an object lifted out of the picture


class Lift:
    """Cut `poly` (source px of `src`, default the shot's own image) and move it along `keys` =
    [(t, x, y, angle_deg, scale), ...] (its centre in the shot's source px). Before the first key the picture is
    untouched; after it, the hole is filled (inpainted) if the object came from this picture. `flutter` > 0 makes
    a paper turn over as it falls (its width breathes); `shadow` = (dx, dy, amount) a soft shadow under it."""

    def __init__(self, img, poly, keys, src=None, flutter=0.0, flutter_hz=2.2, shadow=(10, 14, 0.35), inpaint=True,
                 feather=1.5, ease_kind="io", fill_from=None):
        self.img, self.src = img, src or img
        self.keys, self.flutter, self.fhz, self.shadow, self.ek = keys, flutter, flutter_hz, shadow, ease_kind
        poly = np.array(poly, np.float32)
        self.c0 = poly.mean(0)
        x0, y0 = np.floor(poly.min(0) - 4).astype(int)
        x1, y1 = np.ceil(poly.max(0) + 4).astype(int)
        S = up(self.src).astype(np.float32)
        m = np.zeros(((y1 - y0) * UP, (x1 - x0) * UP), np.float32)
        cv2.fillPoly(m, [((poly - [x0, y0]) * UP).astype(np.int32)], 1.0, cv2.LINE_AA)
        m = cv2.GaussianBlur(m, (0, 0), feather)
        self.rgb = S[y0 * UP:y1 * UP, x0 * UP:x1 * UP].copy()
        self.al = m
        self.cxy = ((self.c0[0] - x0) * UP, (self.c0[1] - y0) * UP)
        self.patch = None
        if inpaint and self.src == img:
            pad = 30
            X0, Y0 = max(0, (x0 - pad) * UP), max(0, (y0 - pad) * UP)
            X1, Y1 = min(SW * UP, (x1 + pad) * UP), min(SH * UP, (y1 + pad) * UP)
            reg = up(img)[Y0:Y1, X0:X1].copy()
            hole = np.zeros(reg.shape[:2], np.uint8)
            cv2.fillPoly(hole, [(poly * UP - [X0, Y0]).astype(np.int32)], 255)
            hole = cv2.dilate(hole, np.ones((9, 9), np.uint8))
            if fill_from is not None:  # clone-stamp: fill the hole with the picture a little way off (same fabric, same pavement)
                dx, dy = int(fill_from[0] * UP), int(fill_from[1] * UP)
                big = up(img)
                src_reg = big[np.clip(np.arange(Y0, Y1) + dy, 0, SH * UP - 1)][:, np.clip(np.arange(X0, X1) + dx, 0, SW * UP - 1)]
                hm = cv2.GaussianBlur(cv2.dilate(hole, np.ones((15, 15), np.uint8)).astype(np.float32) / 255, (0, 0), 6)[..., None]
                self.patch = (X0, Y0, src_reg.astype(np.float32) * hm + reg.astype(np.float32) * (1 - hm))
                return
            small = cv2.resize(reg, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            hs = cv2.resize(hole, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_NEAREST)
            fill = cv2.inpaint(cv2.cvtColor(small, cv2.COLOR_RGB2BGR), hs, 9, cv2.INPAINT_TELEA)
            fill = cv2.cvtColor(cv2.resize(fill, (reg.shape[1], reg.shape[0]), interpolation=cv2.INTER_CUBIC), cv2.COLOR_BGR2RGB)
            # keep the picture's grain: add back fine texture from around the hole
            tex = reg.astype(np.float32) - cv2.GaussianBlur(reg.astype(np.float32), (0, 0), 3)
            tex = cv2.inpaint(np.clip(tex + 128, 0, 255).astype(np.uint8), hole, 5, cv2.INPAINT_TELEA).astype(np.float32) - 128
            hm = cv2.GaussianBlur(hole.astype(np.float32) / 255, (0, 0), 4)[..., None]
            self.patch = (X0, Y0, np.clip(fill + tex * 0.8, 0, 255) * hm + reg * (1 - hm))

    def state(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return ks[0][1:]
        for (ta, *a), (tb, *b) in zip(ks, ks[1:]):
            if t <= tb:
                u = ease((t - ta) / max(1e-6, tb - ta), self.ek)
                return [x + (y - x) * u for x, y in zip(a, b)]
        return ks[-1][1:]

    def __call__(self, a, t):
        if t < self.keys[0][0]:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        if self.patch is not None:
            X0, Y0, p = self.patch
            a[Y0:Y0 + p.shape[0], X0:X0 + p.shape[1]] = p
        x, y, ang, sc = self.state(t)
        fx = 1.0
        if self.flutter and t < self.keys[-1][0]:
            fx = 1 - self.flutter * (1 - abs(math.cos((t - self.keys[0][0]) * self.fhz * math.pi)))
        th = math.radians(ang)
        # affine: centre of the cut -> (x, y) in 2x, scaled (fx * sc, sc), rotated
        cs, sn = math.cos(th), math.sin(th)
        A = np.array([[cs * sc * fx, -sn * sc], [sn * sc * fx, cs * sc]], np.float32)
        cx, cy = self.cxy
        tvec = np.array([x * UP, y * UP], np.float32) - A @ np.array([cx, cy], np.float32)
        M = np.hstack([A, tvec[:, None]])
        H, W = a.shape[:2]
        h, w = self.al.shape
        corners = (A @ np.array([[0, 0], [w, 0], [0, h], [w, h]], np.float32).T).T + tvec
        X0, Y0 = np.floor(corners.min(0)).astype(int) - 40
        X1, Y1 = np.ceil(corners.max(0)).astype(int) + 40
        X0, Y0, X1, Y1 = max(0, X0), max(0, Y0), min(W, X1), min(H, Y1)
        if X1 <= X0 or Y1 <= Y0:
            return a
        M2 = M.copy()
        M2[:, 2] -= [X0, Y0]
        size = (X1 - X0, Y1 - Y0)
        al = cv2.warpAffine(self.al, M2, size, flags=cv2.INTER_LINEAR)
        rgb = cv2.warpAffine(self.rgb, M2, size, flags=cv2.INTER_LINEAR)
        if self.shadow and self.shadow[2] > 0:
            dx, dy, k = self.shadow
            sh = cv2.GaussianBlur(al, (0, 0), 8)
            sh = np.roll(np.roll(sh, int(dy * UP), 0), int(dx * UP), 1) * k
            reg = a[Y0:Y1, X0:X1]
            a[Y0:Y1, X0:X1] = reg * (1 - sh[..., None])
        shade = 0.85 + 0.15 * fx  # the turning side darkens a little
        reg = a[Y0:Y1, X0:X1]
        a[Y0:Y1, X0:X1] = reg * (1 - al[..., None]) + rgb * shade * al[..., None]
        return a


# ---------------------------------------------------------------- a proper drawing, made live


class Draw:
    """A drawing from a sketch sheet made live on the shot: panel `i` of `sheet` (its `_lines` version inks itself in
    stroke order, the pen following it; then the colour version washes in with a brush). at = centre (source px of
    the shot), height = its height there. t_ink = (a, b), t_col = (c, d). card=True paints a soft cream wash first
    (t_ink[0]-0.5 .. t_ink[0]) so a drawing reads over a busy picture; on a blank base leave it off.
    clip = (x0, y0, x1, y1) inside the panel, in sheet px, to draw only part of it. t_out fades it away."""

    def __init__(self, sheet, i, at, height, t_ink, t_col=None, card=False, clip=None, t_out=None, ink_color=(40, 32, 26),
                 colour=True, flip=False):
        order = film.sheet_order(sheet)
        x0, y0, x1, y1 = film.panels(sheet)[i]
        T = order[f"T{i}"]
        K = order[f"K{i}"]
        if clip is not None:
            cx0, cy0, cx1, cy1 = clip
            T = T[cy0 - y0:cy1 - y0, cx0 - x0:cx1 - x0]
            K = K[(K[:, 1] >= cx0 - x0) & (K[:, 1] < cx1 - x0) & (K[:, 2] >= cy0 - y0) & (K[:, 2] < cy1 - y0)]
            K = K - [0, cx0 - x0, cy0 - y0]
            if len(K):
                lo, hi = K[:, 0].min(), K[:, 0].max()
                K[:, 0] = (K[:, 0] - lo) / max(1e-6, hi - lo)
                T = np.clip((T - lo) / max(1e-6, hi - lo), 0, 1)
            x0, y0, x1, y1 = clip
        lines = up(sheet + "_lines")[y0 * UP:y1 * UP, x0 * UP:x1 * UP].astype(np.float32)
        col = up(sheet)[y0 * UP:y1 * UP, x0 * UP:x1 * UP].astype(np.float32)
        paper = np.median(np.concatenate([col[:6].reshape(-1, 3), col[-6:].reshape(-1, 3)]), 0)
        s = height * UP / lines.shape[0]
        size = (max(2, int(lines.shape[1] * s)), max(2, int(lines.shape[0] * s)))
        lines = cv2.resize(lines, size, interpolation=cv2.INTER_AREA)
        col = cv2.resize(col, size, interpolation=cv2.INTER_AREA)
        T = cv2.resize(T.astype(np.float32), size, interpolation=cv2.INTER_LINEAR)
        if flip:
            lines, col, T = lines[:, ::-1], col[:, ::-1], T[:, ::-1]
        g = cv2.cvtColor(lines.astype(np.uint8), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
        self.ink = np.clip((0.9 - g) / 0.7, 0, 1)
        diff = np.abs(col - paper).max(2)
        cal = np.clip((diff - 10) / 35, 0, 1)
        cal = cv2.morphologyEx(cal, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        self.cal = cv2.GaussianBlur(np.maximum(cal, self.ink), (0, 0), 1.0)
        self.col = col
        self.T = T
        hgt, wid = self.ink.shape
        r = np.random.default_rng(int(at[0]))
        nz = cv2.resize(r.random((max(2, hgt // 60), max(2, wid // 60))).astype(np.float32), (wid, hgt), interpolation=cv2.INTER_CUBIC)
        xx, yy = np.meshgrid(np.linspace(0, 1, wid, dtype=np.float32), np.linspace(0, 1, hgt, dtype=np.float32))
        self.F = np.clip(0.6 * (0.7 * xx + 0.3 * yy) + 0.4 * nz, 0, 1)  # brush order for the colour
        self.pos = (int(at[0] * UP - wid / 2), int(at[1] * UP - hgt / 2))
        self.K = K.copy()
        sx, sy = size[0] / ((x1 - x0) * 1.0), size[1] / ((y1 - y0) * 1.0)
        self.K[:, 1] = self.K[:, 1] * sx / UP
        self.K[:, 2] = self.K[:, 2] * sy / UP
        if flip:
            self.K[:, 1] = wid / UP - self.K[:, 1]
        self.t_ink, self.t_col, self.t_out = t_ink, t_col, t_out
        self.inkc = np.array(ink_color, np.float32)
        self.colour = colour and t_col is not None
        self.card = None
        if card:
            m = np.zeros((hgt + 120, wid + 120), np.float32)
            cv2.ellipse(m, ((wid + 120) // 2, (hgt + 120) // 2), ((wid + 90) // 2, (hgt + 90) // 2), 0, 0, 360, 1.0, -1)
            nz2 = cv2.resize(r.random((12, 12)).astype(np.float32), (wid + 120, hgt + 120), interpolation=cv2.INTER_CUBIC)
            m = np.clip((cv2.GaussianBlur(m, (0, 0), 30) * (0.7 + 0.6 * nz2) - 0.45) * 2.4, 0, 1)
            self.card = (m * 0.88).astype(np.float32)
            self.card_rgb = np.ones((hgt + 120, wid + 120, 3), np.float32) * np.array((243, 234, 214), np.float32)

    def _out(self, t):
        return 1.0 if self.t_out is None else 1 - _sm((t - self.t_out) / 0.6)

    def __call__(self, a, t):
        a0, b0 = self.t_ink
        start = a0 - (0.5 if self.card is not None else 0)
        if t < start:
            return a
        k_out = self._out(t)
        if k_out <= 0:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        X, Y = self.pos
        if self.card is not None:
            k = _sm((t - start) / 0.5) * k_out
            a = _blend(a, X - 60, Y - 60, self.card_rgb, self.card * k)
        p = (t - a0) / max(1e-6, b0 - a0)
        rev = np.clip((p - self.T) / 0.03, 0, 1) * self.ink
        if self.colour:
            c0, c1 = self.t_col
            q = (t - c0) / max(1e-6, c1 - c0)
            wash = np.clip((q * 1.25 - self.F) / 0.25, 0, 1) * self.cal * k_out
            if wash.max() > 0:
                a = _blend(a, X, Y, self.col, wash)
        a = _blend(a, X, Y, np.broadcast_to(self.inkc, self.col.shape), rev * 0.9 * k_out)
        return a

    def pen(self, t):
        a0, b0 = self.t_ink
        X, Y = self.pos
        if a0 <= t <= b0 and len(self.K):
            p = (t - a0) / (b0 - a0)
            k = int(np.searchsorted(self.K[:, 0], p)) - 1
            if k >= 0:
                return ("pen", (X / UP + float(self.K[k, 1]), Y / UP + float(self.K[k, 2])))
        if self.colour:
            c0, c1 = self.t_col
            if c0 <= t <= c1:
                q = (t - c0) / (c1 - c0)
                h, w = self.ink.shape
                return ("brush", (X / UP + w / UP * (0.15 + 0.7 * q), Y / UP + h / UP * (0.35 + 0.3 * math.sin(q * 9))))
        return None


# ---------------------------------------------------------------- a paper torn in two


class Tear:
    """The shot's whole picture is a sheet of paper on a dark table: from t0 a jagged tear runs down it (0.45 s),
    then the halves pull apart, turn and slide away. x = where the tear runs (source px)."""

    def __init__(self, img, t0, x=None, bg=(34, 26, 20), seed=5):
        self.t0, self.img = t0, img
        H, W = SH * UP, SW * UP
        x = (x or SW / 2) * UP
        r = np.random.default_rng(seed)
        ys = np.linspace(0, H, 60)
        xs = x + np.cumsum(r.normal(0, 9 * UP, 60)) * 0.6 + 30 * UP * np.sin(ys / H * 3)
        self.path = np.stack([xs, ys], 1)
        left = np.zeros((H, W), np.float32)
        poly = np.vstack([[[0, 0]], self.path, [[0, H]]]).astype(np.int32)
        cv2.fillPoly(left, [poly], 1.0, cv2.LINE_AA)
        self.L = left
        edge = np.zeros((H, W), np.float32)
        cv2.polylines(edge, [self.path.astype(np.int32)], False, 1.0, 5 * UP, cv2.LINE_AA)
        self.edge = cv2.GaussianBlur(edge, (0, 0), 2) * (0.6 + 0.4 * cv2.resize(r.random((H // 20, W // 20)).astype(np.float32), (W, H)))
        b = cv2.GaussianBlur(cv2.resize(up(img), (W // 8, H // 8)), (0, 0), 6).astype(np.float32)
        self.bg = np.clip(cv2.resize(b, (W, H)) * 0.22 + np.array(bg, np.float32) * 0.6, 0, 255)

    def __call__(self, a, t):
        u = t - self.t0
        if u < 0:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        H, W = a.shape[:2]
        # the tear running down: a pale fibrous line grows from the top
        run = _sm(u / 0.45)
        if u < 0.45:
            ys = np.arange(H, dtype=np.float32)[:, None] / H
            m = self.edge * (ys < run)
            return a * (1 - m[..., None] * 0.9) + 245 * m[..., None] * 0.9
        v = u - 0.45
        e = 1 - math.exp(-v * 2.2)
        sep = 230 * UP * e + 6 * UP * v
        rot = 7.0 * e
        drop = 40 * UP * e
        out = self.bg.copy()
        for side, mask in ((-1, self.L), (1, 1 - self.L)):
            piv = (0, H) if side < 0 else (W, H)
            M = cv2.getRotationMatrix2D(piv, side * -rot * 0.6, 1.0)
            M[0, 2] += side * sep
            M[1, 2] += drop * (0.6 if side < 0 else 1.0)
            al = cv2.warpAffine(mask * (1 - self.edge * 0.0), M, (W, H))
            im = cv2.warpAffine(a, M, (W, H), borderMode=cv2.BORDER_REPLICATE)
            ed = cv2.warpAffine(self.edge, M, (W, H))
            sh = cv2.GaussianBlur(al, (0, 0), 18) * 0.5
            out = out * (1 - sh[..., None])
            im = im * (1 - ed[..., None] * 0.5) + 240 * ed[..., None] * 0.5  # the torn edge's pale fibres
            out = out * (1 - al[..., None]) + im * al[..., None]
        return out


# ---------------------------------------------------------------- a rolling money counter (post: screen space)

try:
    _DIG = ImageFont.truetype(ytf.font("mono_bold"), 64)
except OSError:
    _DIG = ImageFont.load_default()


class Counter:
    """A cream paper tag with rolling digits (an odometer): keys = [(t, value), ...]; pos = (x, y) as 0-1 of the
    screen (the tag's centre); label = a small typed word under it. Digits roll like a mechanical counter."""

    def __init__(self, keys, pos=(0.78, 0.16), t_in=None, t_out=None, label=None, prefix="$", size=1.0, digits=9):
        self.keys, self.pos, self.label, self.prefix, self.size = keys, pos, label, prefix, size
        self.t_in = keys[0][0] - 0.4 if t_in is None else t_in
        self.t_out = t_out
        self.font = ImageFont.truetype(ytf.font("mono_bold"), int(58 * size * OW / 1920))
        self.lfont = ImageFont.truetype(ytf.font("mono"), int(30 * size * OW / 1920))
        vmax = max(v for _, v in keys)
        self.nd = max(1, len(str(int(vmax))))
        self.cw = int(self.font.getlength("0"))
        self.ch = int(66 * size * OW / 1920)
        self.glyph = {}
        for d in "0123456789$,":
            im = Image.new("L", (self.cw + 4, self.ch), 0)
            ImageDraw.Draw(im).text((2, self.ch * 0.06), d, font=self.font, fill=255)
            self.glyph[d] = np.asarray(im, np.float32) / 255

    def value(self, t):
        ks = self.keys
        if t <= ks[0][0]:
            return ks[0][1]
        for (ta, a), (tb, b) in zip(ks, ks[1:]):
            if t <= tb:
                return a + (b - a) * ease((t - ta) / max(1e-6, tb - ta))
        return ks[-1][1]

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t_in or (self.t_out is not None and t > self.t_out + 0.5):
            return img
        k = _sm((t - self.t_in) / 0.35) * (1 if self.t_out is None else 1 - _sm((t - self.t_out) / 0.4))
        v = self.value(t)
        # layout: $ d,ddd,ddd
        cells = []
        for i in range(self.nd):
            p = self.nd - 1 - i
            cells.append(("d", p))
            if p and p % 3 == 0:
                cells.append(("c", None))
        W_ = (len(cells) + 1) * self.cw - sum(self.cw // 2 for c_ in cells if c_[0] == 'c')
        pw, ph = W_ + int(60 * OW / 1920), self.ch + int(56 * OW / 1920) + (int(34 * OW / 1920) if self.label else 0)
        H, Wd = img.shape[:2]
        cx, cy = int(self.pos[0] * Wd), int(self.pos[1] * H)
        x0, y0 = cx - pw // 2, cy - ph // 2 + int((1 - k) * 30)
        out = img
        # the tag: cream paper with a soft shadow and a slightly ragged edge
        tag = np.zeros((ph + 40, pw + 40), np.float32)
        cv2.rectangle(tag, (20, 20), (pw + 20, ph + 20), 1.0, -1)
        sh = cv2.GaussianBlur(tag, (0, 0), 10) * 0.4 * k
        out = _blend(out, x0 - 14, y0 - 12, np.zeros((ph + 40, pw + 40, 3), np.float32), sh)
        out = _blend(out, x0 - 20, y0 - 20, np.ones((ph + 40, pw + 40, 3), np.float32) * np.array(look.rgb("paper"), np.float32), tag * k * 0.97)
        ink = np.array(look.on_paper(), np.float32)
        x = x0 + int(30 * OW / 1920)
        y = y0 + int(22 * OW / 1920)
        g = self.glyph["$"]
        out = _blend(out, x, y, np.broadcast_to(ink, g.shape + (3,)), g * k)
        x += self.cw
        for kind, p in cells:
            if kind == "c":
                g = self.glyph[","]
                out = _blend(out, x - self.cw // 4, y, np.broadcast_to(ink, g.shape + (3,)), g * k * (1 if v >= 10 ** 3 else 0.25))
                x += self.cw // 2
                continue
            dv = (v / 10 ** p) % 10
            lo = int(dv) % 10
            fr = dv - int(dv)
            if p > 0:  # a digit only turns while the one below it rolls over
                low = (v / 10 ** (p - 1)) % 10
                fr = max(0.0, (low - 9)) if low > 9 else 0.0
            off = int(fr * self.ch)
            lead = v < 10 ** p and p > 0
            for d, dy in ((lo, -off), ((lo + 1) % 10, self.ch - off)):
                g = self.glyph[str(d)]
                y_ = y + dy
                gy0, gy1 = max(0, -dy), min(self.ch, self.ch - dy)
                if gy1 <= gy0:
                    continue
                gg = g[gy0:gy1]
                out = _blend(out, x, y + max(0, dy), np.broadcast_to(ink, gg.shape + (3,)), gg * k * (0.25 if lead else 1))
            x += self.cw
        if self.label:
            im = Image.new("L", (pw, int(40 * OW / 1920)), 0)
            ImageDraw.Draw(im).text((int(30 * OW / 1920), 0), self.label, font=self.lfont, fill=255)
            g = np.asarray(im, np.float32) / 255
            out = _blend(out, x0, y0 + self.ch + int(30 * OW / 1920), np.broadcast_to(ink, g.shape + (3,)), g * k * 0.9)
        return out


# ---------------------------------------------------------------- glass shatter (a transition)

_SH = {}


def _shards(seed=9, n=46, centre=(0.5, 0.45)):
    key = (OW, OH, seed, n, centre)
    if key in _SH:
        return _SH[key]
    r = np.random.default_rng(seed)
    c = np.array([centre[0] * OW, centre[1] * OH])
    pts = [c]
    for _ in range(n):  # denser near the impact
        ang, rad = r.uniform(0, 2 * math.pi), (r.random() ** 1.6) * OW * 0.75
        pts.append(c + rad * np.array([math.cos(ang), math.sin(ang)]))
    pts += [(-OW, -OH), (2 * OW, -OH), (-OW, 2 * OH), (2 * OW, 2 * OH)]
    sub = cv2.Subdiv2D((-2 * OW, -2 * OH, 5 * OW, 5 * OH))
    for p in pts:
        sub.insert((float(p[0]), float(p[1])))
    facets, centres = sub.getVoronoiFacetList([])
    shards = []
    for f, cc in zip(facets, centres):
        poly = np.clip(np.array(f), [-5, -5], [OW + 5, OH + 5]).astype(np.int32)
        m = np.zeros((OH, OW), np.uint8)
        cv2.fillPoly(m, [poly], 255)
        ys, xs = np.nonzero(m)
        if len(xs) < 20:
            continue
        x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
        d = np.array(cc) - c
        dist = np.linalg.norm(d) / OW
        shards.append(dict(box=(x0, y0, x1, y1), m=(m[y0:y1, x0:x1] > 0).astype(np.float32), c=np.array(cc, np.float32),
                           v=d / (np.linalg.norm(d) + 1e-6) * r.uniform(80, 260) * OW / 1920, spin=r.uniform(-90, 90),
                           delay=dist * 0.35 + r.uniform(0, 0.08), poly=poly))
    # crack lines: the facet edges, drawn outward from the impact
    cracks = np.zeros((OH, OW), np.float32)
    dmap = np.full((OH, OW), 9.0, np.float32)
    for s in shards:
        cv2.polylines(cracks, [s["poly"]], True, 1.0, max(1, int(2 * OW / 1920)), cv2.LINE_AA)
    yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
    dmap = np.hypot(xx - c[0], yy - c[1]) / (OW * 0.8)
    _SH[key] = (shards, cracks, dmap, c)
    return _SH[key]


def shatter(a, b, u, tr):
    """("shatter", secs, (cx, cy)): cracks race out from the impact over the first 30%, then the shards fall away
    (turning, catching the light) and the next shot shows through."""
    centre = tr[2] if len(tr) > 2 else (0.5, 0.45)
    shards, cracks, dmap, c = _shards(centre=tuple(centre))
    a = a.astype(np.float32)
    if u < 0.3:
        k = u / 0.3
        m = cracks * (dmap < k * 1.1)
        return a * (1 - m[..., None] * 0.8) + 250 * m[..., None] * 0.8
    out = b.astype(np.float32).copy()
    T = (u - 0.3) / 0.7 * 1.2  # seconds-ish of fall
    for s in sorted(shards, key=lambda s: -s["delay"]):
        tt = T - s["delay"]
        x0, y0, x1, y1 = s["box"]
        if tt <= 0:  # still in place, still cracked
            reg = a[y0:y1, x0:x1]
            m = s["m"][..., None]
            out[y0:y1, x0:x1] = out[y0:y1, x0:x1] * (1 - m) + reg * m
            continue
        dx, dy = s["v"] * tt * 2.2
        dy += 2200 * OW / 1920 * tt * tt
        ang = s["spin"] * tt
        sc = 1 + 0.25 * tt
        cx, cy = s["c"]
        M = cv2.getRotationMatrix2D((float(cx), float(cy)), ang, sc)
        M[0, 2] += dx
        M[1, 2] += dy
        full_m = np.zeros((OH, OW), np.float32)
        full_m[y0:y1, x0:x1] = s["m"]
        m = cv2.warpAffine(full_m, M, (OW, OH))
        if m.max() <= 0:
            continue
        im = cv2.warpAffine(a, M, (OW, OH))
        glint = 0.25 * max(0.0, math.sin(ang * 0.07 + cx * 0.01)) ** 4
        fade = max(0.0, 1 - max(0.0, tt - 0.9) * 3)
        mm = (m * fade)[..., None]
        edge = cv2.morphologyEx(m, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8))[..., None] * fade
        out = out * (1 - mm) + (im * (1 - glint) + 255 * glint) * mm
        out = out * (1 - edge * 0.6) + 235 * edge * 0.6  # the glass edge catching light
    return out


# ---------------------------------------------------------------- found lamps, leaves, glints (Chadwick)

def find_lights(img, n=6, vmin=238, min_area=12, max_area=2600):
    """The picture's own lamps, candles and lit lamp glasses: small, very bright, warm blobs (source px).
    Returns [(x, y, area), ...], brightest first. Cached in build/lights.json."""
    import json
    f = film.BUILD / "lights.json"
    allf = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    if img in allf:
        return [tuple(v) for v in allf[img]]
    a = up(img)[::UP, ::UP].astype(np.int16)
    R, G, B = a[..., 0], a[..., 1], a[..., 2]
    m = ((R >= 251) & (G >= 228) & (R - B >= 30)).astype(np.uint8)
    try:  # never a face: egg heads are warm and bright too
        import signature as sg
        for fc in sg.find_faces(img):
            x0, y0, x1, y1 = [int(v) for v in fc["head"]]
            m[max(0, y0 - 10):y1 + 10, max(0, x0 - 10):x1 + 10] = 0
    except Exception:
        pass
    m = cv2.dilate(m, np.ones((3, 3), np.uint8))
    k, lab, st, cen = cv2.connectedComponentsWithStats(m)
    out = []
    for i in range(1, k):
        ar = st[i, cv2.CC_STAT_AREA]
        w_, h_ = st[i, cv2.CC_STAT_WIDTH], st[i, cv2.CC_STAT_HEIGHT]
        if min_area <= ar <= max_area and max(w_, h_) < 120:
            out.append((float(cen[i][0]), float(cen[i][1]), int(ar)))
    out.sort(key=lambda v: -v[2])
    out = out[:n]
    allf[img] = out
    f.write_text(json.dumps(allf), encoding="utf-8")
    return out


def lamps(img, amount=0.14, flicker=0.3, n=6, scale=1.0):
    """Light() on each of the picture's own lamps (find_lights): they breathe softly, as gas and oil light does."""
    return [Light((x, y), (22 + math.sqrt(ar) * 3.2) * scale, amount=amount, flicker=flicker, seed=i + int(x) % 7)
            for i, (x, y, ar) in enumerate(find_lights(img, n=n))]


class Leaves:
    """Autumn leaves drifting down across the frame (screen space, post=[...]): each turns over as it falls."""

    def __init__(self, t0, t1, n=14, seed=4, colors=((168, 74, 34), (196, 120, 40), (140, 52, 30), (210, 150, 60)), scale=1.0,
                 avoid=None, y_max=None):
        r = np.random.default_rng(seed)
        self.y_max = y_max  # leaves fade out before this height (0-1 of the screen): kept in the treetops
        self.heads = []
        if avoid:  # faces in this picture (source px): a leaf never crosses one
            import signature as sg
            self.heads = [tuple(float(v) for v in f["head"]) for f in sg.find_faces(avoid)]
        self.t0, self.t1 = t0, t1
        self.p = [dict(t=r.uniform(t0 - 4, t1), x=r.uniform(-0.05, 1.05), z=r.uniform(0.45, 1.0), ph=r.uniform(0, 6.3),
                       spin=r.uniform(1.0, 2.6) * r.choice([-1, 1]), c=np.array(colors[r.integers(len(colors))], np.float32),
                       ang=r.uniform(0, 360)) for _ in range(n)]
        self.scale = scale

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t0 - 0.1 or t > self.t1 + 8:
            return img
        H, W = img.shape[:2]
        out = img
        for p in sorted(self.p, key=lambda q: q["z"]):
            u = t - p["t"]
            if u < 0:
                continue
            y = -0.08 + u * (0.07 + 0.08 * p["z"])
            if y > 1.1:
                continue
            fade_k = 1.0
            if self.y_max is not None:
                fade_k = float(np.clip((self.y_max - y) / 0.08, 0, 1))
                if fade_k <= 0:
                    continue
            x = p["x"] + 0.05 * math.sin(u * 1.3 + p["ph"]) + u * 0.012
            size = (0.012 + 0.018 * p["z"]) * W * self.scale
            flip = abs(math.cos(u * p["spin"] + p["ph"])) * 0.85 + 0.15
            box = cv2.ellipse2Poly((int(x * W), int(y * H)), (max(2, int(size * flip)), max(2, int(size * 0.55))),
                                   int(p["ang"] + u * p["spin"] * 50), 0, 360, 20)
            m = np.zeros((H, W), np.float32)
            cv2.fillConvexPoly(m, box, 1.0, lineType=cv2.LINE_AA)
            if self.heads and s is not None:
                lx, ly = x * W, y * H
                hit = False
                for (hx0, hy0, hx1, hy1) in self.heads:
                    (ax, ay), (bx, by) = s.to_screen((hx0, hy0), cam), s.to_screen((hx1, hy1), cam)
                    pad = 0.35 * (bx - ax) + size
                    if ax - pad < lx < bx + pad and ay - pad < ly < by + pad:
                        hit = True
                if hit:
                    continue
            col = p["c"] * (0.8 + 0.2 * flip)
            out = out * (1 - m[..., None] * 0.95 * fade_k) + col * m[..., None] * 0.95 * fade_k
        return out


class Sparkle:
    """Glints on jewels, glass and gilt: little four-point stars that flare and fade at points (source px)."""

    def __init__(self, points, t0=-1e9, t1=1e9, rate=1.4, size=16, seed=3):
        self.pts, self.t0, self.t1, self.rate, self.size = points, t0, t1, rate, size
        r = np.random.default_rng(seed)
        self.ph = r.uniform(0, 10, len(points))

    def __call__(self, a, t):
        if not self.t0 <= t <= self.t1:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        for (x, y), ph in zip(self.pts, self.ph):
            u = ((t + ph) * self.rate) % 3.0
            if u > 0.6:
                continue
            k = math.sin(math.pi * u / 0.6)
            S = int(self.size * UP * (0.6 + 0.6 * k))
            pad = np.zeros((2 * S + 1, 2 * S + 1), np.float32)
            cv2.line(pad, (0, S), (2 * S, S), 1.0, max(1, UP), cv2.LINE_AA)
            cv2.line(pad, (S, 0), (S, 2 * S), 1.0, max(1, UP), cv2.LINE_AA)
            pad = cv2.GaussianBlur(pad, (0, 0), 1.2) * 1.6 + cv2.GaussianBlur(pad, (0, 0), S / 4) * 0.8
            yy, xx = np.mgrid[-S:S + 1, -S:S + 1]
            pad *= np.clip(1 - np.hypot(xx, yy) / S, 0, 1)
            a = _blend(a, int(x * UP) - S, int(y * UP) - S, np.ones((2 * S + 1, 2 * S + 1, 3), np.float32) * 255, np.clip(pad * k, 0, 1))
        return a



# ---------------------------------------------------------------- a living map: shores inked, water washed in, a traveller

class MapLayer:
    """Real shorelines drawn live on a map base: `lakes` = list of polygons (source px rings, outer ring first), drawn
    as one continuous pen line lake by lake over t_shore=(a, b), then the water washes in over t_wash with a darker
    edge, like gouache, and short cartographer's hatch lines settle on it; `border` = polylines dashed in over t_border."""

    def __init__(self, lakes, border=(), t_shore=(0.0, 2.0), t_wash=(1.6, 2.6), t_border=None, ink=(52, 46, 52),
                 water=(150, 182, 204), width=2.4, seed=3, lines=()):
        H, W = SH * UP, SW * UP
        self.T = np.full((H, W), 9.0, np.float32)
        rings = [np.asarray(r[0], np.float32) * UP for r in lakes] + [np.asarray(l_, np.float32) * UP for l_ in lines]
        total = sum(float(np.hypot(*np.diff(r, axis=0).T).sum()) for r in rings) or 1.0
        acc, track = 0.0, []
        for r in rings:
            for a_, b_ in zip(r, r[1:]):
                L = float(np.hypot(*(b_ - a_)))
                cv2.line(self.T, tuple(np.int32(a_)), tuple(np.int32(b_)), float(acc / total), int(width * UP), cv2.LINE_AA)
                track.append((acc / total, a_[0] / UP, a_[1] / UP))
                acc += L
        self.track = np.array(track, np.float32)
        self.shore = (self.T < 8.5).astype(np.float32)
        self.shore = cv2.GaussianBlur(self.shore, (0, 0), 0.8)
        fill = np.zeros((H, W), np.float32)
        for poly in lakes:
            cv2.fillPoly(fill, [np.int32(np.asarray(poly[0]) * UP)], 1.0, cv2.LINE_AA)
            for hole in poly[1:]:
                cv2.fillPoly(fill, [np.int32(np.asarray(hole) * UP)], 0.0, cv2.LINE_AA)
        soft = cv2.GaussianBlur(fill, (0, 0), 2.0)
        edge = np.clip(soft - cv2.GaussianBlur(cv2.erode(fill, np.ones((15, 15), np.uint8)), (0, 0), 6), 0, 1)
        self.wash, self.edge = soft, edge
        r = np.random.default_rng(seed)
        hatch = np.zeros((H, W), np.float32)
        ys, xs = np.nonzero(cv2.erode(fill, np.ones((31, 31), np.uint8)) > 0.5)
        for k in r.choice(len(xs), size=min(len(xs), 140), replace=False) if len(xs) else []:
            x, y = int(xs[k]), int(ys[k])
            cv2.line(hatch, (x - 14 * UP // 2, y), (x + 14 * UP // 2, y), 1.0, max(1, UP), cv2.LINE_AA)
        self.hatch = cv2.GaussianBlur(hatch, (0, 0), 0.6) * fill
        nz = cv2.resize(r.random((max(2, H // 90), max(2, W // 90))).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
        self.F = np.clip(0.6 * np.linspace(0, 1, W, dtype=np.float32)[None, :] + 0.4 * nz, 0, 1)
        self.bord = None
        if border and t_border:
            bm = np.zeros((H, W), np.float32)
            bT = np.full((H, W), 9.0, np.float32)
            for line in border:
                q = np.asarray(line, np.float32) * UP
                d = np.r_[0, np.cumsum(np.hypot(*np.diff(q, axis=0).T))]
                Ltot = d[-1] or 1
                for i, (a_, b_) in enumerate(zip(q, q[1:])):
                    if int(d[i] / (9 * UP)) % 2 == 0:  # dashes
                        cv2.line(bm, tuple(np.int32(a_)), tuple(np.int32(b_)), 1.0, max(1, int(1.6 * UP)), cv2.LINE_AA)
                        cv2.line(bT, tuple(np.int32(a_)), tuple(np.int32(b_)), float(d[i] / Ltot), max(1, int(1.6 * UP)), cv2.LINE_AA)
            self.bord, self.bT = bm, bT
        self.t_shore, self.t_wash, self.t_border = t_shore, t_wash, t_border
        self.ink, self.water = np.array(ink, np.float32), np.array(water, np.float32)

    def __call__(self, a, t):
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        c0, c1 = self.t_wash
        q = (t - c0) / max(1e-6, c1 - c0)
        if q > 0:
            w = np.clip((q * 1.3 - self.F) / 0.3, 0, 1)
            al = (self.wash * 0.5 + self.edge * 0.3) * w
            a = a * (1 - al[..., None]) + self.water * 0.85 * al[..., None]
            h = self.hatch * np.clip((q - 0.6) / 0.4, 0, 1) * 0.55
            a = a * (1 - h[..., None]) + self.ink * h[..., None]
        p = (t - self.t_shore[0]) / max(1e-6, self.t_shore[1] - self.t_shore[0])
        if p > 0:
            rev = self.shore * np.clip((p - self.T) / 0.004, 0, 1)
            a = a * (1 - rev[..., None] * 0.9) + self.ink * rev[..., None] * 0.9
        if self.bord is not None:
            b0, b1 = self.t_border
            pb = (t - b0) / max(1e-6, b1 - b0)
            if pb > 0:
                rv = self.bord * np.clip((pb - self.bT) / 0.01, 0, 1) * 0.7
                a = a * (1 - rv[..., None]) + self.ink * rv[..., None]
        return a

    def pen(self, t):
        a0, b0 = self.t_shore
        if a0 <= t <= b0 and len(self.track):
            p = (t - a0) / (b0 - a0)
            k = int(np.searchsorted(self.track[:, 0], p)) - 1
            if k >= 0:
                return ("pen", (float(self.track[k, 1]), float(self.track[k, 2])))
        return None


class Traveller:
    """A red marker travelling along a road (source px points) over (t0, t1), easing at each stop, with a fading trail
    of dots behind it and a small pulse ring when it arrives at each stop."""

    def __init__(self, pts, t0, t1, color=(186, 44, 36), r=9, stops=True):
        self.p = np.asarray(pts, np.float32)
        d = np.r_[0, np.cumsum(np.hypot(*np.diff(self.p, axis=0).T))]
        self.d, self.L, self.t0, self.t1, self.col, self.r, self.stops = d, d[-1] or 1, t0, t1, np.array(color, np.float32), r, stops
        n = len(self.p) - 1
        self.ts = [t0 + (t1 - t0) * k / n for k in range(n + 1)]  # each leg gets equal time: an easing hop per leg

    def at(self, t):
        if t <= self.t0:
            return self.p[0]
        for k in range(len(self.ts) - 1):
            if t <= self.ts[k + 1]:
                u = ease((t - self.ts[k]) / (self.ts[k + 1] - self.ts[k]))
                return self.p[k] + (self.p[k + 1] - self.p[k]) * u
        return self.p[-1]

    def __call__(self, a, t):
        if t < self.t0:
            return a
        a = a if a.dtype == np.float32 else a.astype(np.float32)
        H, W = a.shape[:2]
        lay = np.zeros((H, W), np.float32)
        for k in range(1, 9):  # the trail
            tt = t - k * 0.06
            if tt < self.t0:
                break
            x, y = self.at(tt) * UP
            cv2.circle(lay, (int(x), int(y)), max(1, int(self.r * UP * (0.55 - 0.05 * k))), 0.5 * (1 - k / 9), -1, cv2.LINE_AA)
        x, y = self.at(t) * UP
        halo = np.zeros((H, W), np.float32)
        cv2.circle(halo, (int(x), int(y)), int(self.r * UP * 1.6), 1.0, -1, cv2.LINE_AA)
        if self.stops:
            for ts, q in zip(self.ts[1:], self.p[1:]):
                u = t - ts
                if 0 <= u < 0.6:
                    cv2.circle(lay, (int(q[0] * UP), int(q[1] * UP)), int(self.r * UP * (1.2 + 3 * u)), 0.8 * (1 - u / 0.6),
                               max(1, UP * 2), cv2.LINE_AA)
        cv2.circle(lay, (int(x), int(y)), int(self.r * UP), 1.0, -1, cv2.LINE_AA)
        halo = cv2.GaussianBlur(halo, (0, 0), 3) * 0.7
        a = a * (1 - halo[..., None]) + np.array(look.rgb("light"), np.float32) * halo[..., None]
        return a * (1 - lay[..., None]) + self.col * lay[..., None]
