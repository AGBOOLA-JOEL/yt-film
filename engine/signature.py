"""Signature animation, all done in code on the painted images:

  Face      faces that act: the egg eyes blink, glance and widen, the mouth line wobbles or opens, on cue
  Flow      living stills: one masked painted area moves (smoke and steam rising, water running)
  Comic     a comic page on a blank board (B09): ink panel borders draw themselves, the shots fill the panels
            (ink first, then the paint), the camera then dives into a panel
  dim       on a case board (sketch sheet), the drawings already talked about fade back so the eye lands on one
  Hand      the narrator's gloved hand sliding a folded note up into the frame (a footnote)

Face and Flow work on a 2x source image (`src_fx=[...]` on a scene); Comic is a shot of its own (`b.custom`);
dim and Hand work on the finished frame (`post=[...]`). Coordinates are source px (1774 x 887) as everywhere.
"""
import math
from pathlib import Path

import cv2
import numpy as np

import film
import ytf
from film import SH, SW, UP, ease, up

RNG = np.random.default_rng(21)
SKILL_HOST = ytf.ASSETS / "footnote"  # the footnote hand, note and board (replace them with your own art if you like)


def host_file(project_path, skill_name):
    """A host asset: this film's own version if it made one (incoming/...), else the skill's fixed one."""
    return project_path if Path(project_path).exists() else SKILL_HOST / skill_name


def _pulse(t, t0, dur):
    """0 -> 1 -> 0 over dur seconds from t0 (a blink, a flinch)."""
    u = (t - t0) / dur
    return math.sin(math.pi * u) if 0 <= u <= 1 else 0.0


def _hold(t, t0, t1, ramp=0.18):
    """0 -> 1, held, -> 0: a glance or a look that lasts from t0 to t1."""
    if t < t0 or t > t1:
        return 0.0
    return ease(min((t - t0) / ramp, (t1 - t) / ramp, 1.0))


# ---------------------------------------------------------------- faces that act


MOUTH_IN = np.array([150, 72, 58], np.float32)
MOUTHS = ("flat", "smile", "grin", "frown", "o", "laugh", "wobble", "grimace")
EYES = ("closed", "happy", "half", "squint")


def _draw_part(shape, info, hw, is_eye, seed, off=(0, 0)):
    """An eye or mouth drawn as ink, in a part's own patch (2x px): returns its alpha. Same weight as the painted
    line, a slight hand wobble, soft edge."""
    h, w = hw
    S = 4  # supersample for a clean, slightly soft line
    m = np.zeros((h * S, w * S), np.uint8)
    fillm = np.zeros_like(m)  # the inside of an open mouth
    cx, cy = (info["c"][0] + off[0]) * S, (info["c"][1] + off[1]) * S
    hx, hy = info["size"][0] * S, info["size"][1] * S
    T = max(2, int(info["thick"] * S))
    r = np.random.default_rng(seed)

    def line(pts, thick=T, closed=False, fill=False):
        p = np.array(pts, np.float32)
        p += r.normal(0, 0.25 * S, p.shape)
        p = p.astype(np.int32)
        if fill:
            cv2.fillPoly(fillm, [p], 255, cv2.LINE_AA)
        cv2.polylines(m, [p], closed, 255, thick, cv2.LINE_AA)

    def oval(c, ax):
        cv2.ellipse(fillm, (int(c[0]), int(c[1])), (int(ax[0]), int(ax[1])), 0, 0, 360, 255, -1, cv2.LINE_AA)
        cv2.ellipse(m, (int(c[0]), int(c[1])), (int(ax[0]), int(ax[1])), 0, 0, 360, 255, max(2, int(T * 0.8)), cv2.LINE_AA)

    if is_eye:
        rx, ry = hx / 1.35 * 0.9, hy / 1.25 * 0.9
        xs = np.linspace(-rx * 1.1, rx * 1.1, 16)
        Te = max(2, int(rx * 0.42))
        if shape == "closed":    # calm, shut: a soft downward curve
            line([(cx + x, cy + ry * 0.15 + ry * 0.18 * (1 - (x / rx) ** 2)) for x in xs], Te)
        elif shape == "happy":   # ^ ^
            line([(cx + x, cy + ry * 0.25 - ry * 0.5 * (1 - (x / (rx * 1.1)) ** 2)) for x in xs], Te)
        elif shape == "half":    # heavy lids: the lower half of the oval under a flat lid
            ell = np.zeros_like(m)
            cv2.ellipse(ell, (int(cx), int(cy + ry * 0.15)), (int(rx), int(ry * 0.75)), 0, 0, 360, 255, -1, cv2.LINE_AA)
            ell[:int(cy), :] = 0
            m = np.maximum(m, ell)
            line([(cx - rx * 1.25, cy), (cx + rx * 1.25, cy)], Te)
        elif shape == "squint":
            cv2.ellipse(m, (int(cx), int(cy)), (int(rx), int(max(T, ry * 0.32))), 0, 0, 360, 255, -1, cv2.LINE_AA)
    else:
        W = max(hx / 1.0 - 6 * S, 20 * S) * 1.0
        W = min(W, (info["size"][0] * S))
        xs = np.linspace(-W, W, 24)
        kind = shape[0] if isinstance(shape, tuple) else shape
        if kind == "flat":
            line([(cx + x, cy) for x in xs])
        elif kind == "smile":
            line([(cx + x, cy + W * 0.22 * (1 - (x / W) ** 2) - W * 0.08) for x in xs])
        elif kind == "frown":
            line([(cx + x, cy - W * 0.18 * (1 - (x / W) ** 2) + W * 0.08) for x in xs])
        elif kind == "wobble":
            line([(cx + x, cy + W * 0.06 * math.sin(i_ * 1.4)) for i_, x in enumerate(xs)])
        elif kind == "grimace":
            line([(cx + x * 1.1, cy + W * 0.07 * (1 if i_ % 4 < 2 else -1)) for i_, x in enumerate(xs)])
        elif kind in ("grin", "laugh"):
            dep = W * (0.42 if kind == "grin" else 0.62)
            top = [(cx + x, cy - W * 0.05 + W * 0.06 * (x / W) ** 2) for x in xs]
            bot = [(cx + x, cy - W * 0.05 + dep * (1 - (x / W) ** 2) ** 0.8) for x in xs[::-1]]
            line(top + bot, closed=True, fill=True)
        elif kind == "o":
            oval((cx, cy + W * 0.05), (W * 0.42, W * 0.5))
        elif kind == "talk":
            k = shape[1]
            if k < 0.12:
                line([(cx + x * 0.6, cy) for x in xs])
            else:
                oval((cx, cy), (W * 0.5, T / 2 + k * W * 0.34))
    a = cv2.resize(m, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    f = cv2.resize(fillm, (w, h), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    return cv2.GaussianBlur(a, (0, 0), 0.5), cv2.GaussianBlur(f, (0, 0), 0.5)


class Face:
    """The egg face of one character in one image. eyes = [(x, y, rx, ry), ...], mouth = (x, y, w, h): the solid
    dark eye ovals and the mouth line in source px (measure them on a gridded crop). The parts are lifted off a skin
    that is painted in underneath (inpaint), then redrawn every frame squashed (blink), moved (glance), scaled
    (widen) or waved (mouth). Blinks come every 2.5-4.5 s on their own; add cues for the acting:
      blinks=[t, ...], glances=[(t0, t1, dx, dy), ...] (source px), widen=[(t0, t1, amount), ...],
      mouth_fx=[(t0, t1, "wobble" | "open" | "smile", amount), ...]  (bends the painted mouth)
      expr=[(t0, t1, mouth, eyes), ...]  a new expression drawn in the face's own ink: mouths flat smile grin frown o
          laugh wobble grimace; eyes closed happy half squint (None keeps the painted part); eased in and out
      talk=[(s, e), ...]  word times of a quoted line: a simple cartoon open-close, not lip-sync
    """

    def __init__(self, img, eyes=(), mouth=None, blinks=(), glances=(), widen=(), mouth_fx=(), expr=(), talk=(), auto=True,
                 seed=0):
        self.img, self.eyes, self.mouth = img, list(eyes), mouth
        self.glances, self.widen, self.mouth_fx = list(glances), list(widen), list(mouth_fx)
        self.expr = list(expr)   # [(t0, t1, mouth shape | None, eye shape | None)]: drawn in ink (see MOUTHS / EYES)
        self.talk = list(talk)   # [(s, e), ...] spoken words: the mouth opens and closes with them (a quoted line)
        self.seed = seed
        r = np.random.default_rng(seed)
        self.blinks = sorted(list(blinks) + (list(np.cumsum(r.uniform(2.5, 4.5, 30)) - 1.5) if auto else []))
        self._prep = None

    def _parts(self, a):
        """Per part: (box, patch, alpha) at 2x, cut from the original; plus the image with the parts painted out."""
        clean = a.copy()
        parts = []
        boxes = [(x, y, rx * 1.35 + 3, ry * 1.25 + 3, 8, 8) for x, y, rx, ry in self.eyes]
        if self.mouth:
            x, y, w, h = self.mouth
            boxes.append((x, y, w / 2 + 6, h / 2 + 6, w * 0.35 + 8, w * 0.45 + 8))  # room for a laugh
        g = cv2.cvtColor(a, cv2.COLOR_RGB2GRAY).astype(np.float32)
        hole = np.zeros(a.shape[:2], np.uint8)
        for (x, y, hx, hy, px, py) in boxes:
            x0, y0 = int((x - hx - px) * UP), int((y - hy - py) * UP)
            x1, y1 = int((x + hx + px) * UP), int((y + hy + py) * UP)
            sub = g[y0:y1, x0:x1]
            ell = np.zeros(sub.shape, np.uint8)
            cv2.ellipse(ell, (int(x * UP - x0), int(y * UP - y0)), (int(hx * UP), int(hy * UP)), 0, 0, 360, 1, -1)
            skin = np.median(sub[ell == 0])
            al = np.clip((skin - sub - 12) / 40, 0, 1) * ell  # what is darker than the skin around it
            al = cv2.dilate(al, np.ones((3, 3), np.uint8))
            al = np.maximum(al, cv2.morphologyEx((al > 0.3).astype(np.uint8), cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8)).astype(np.float32))
            al = cv2.GaussianBlur(al, (0, 0), 1.0)
            patch = a[y0:y1, x0:x1].astype(np.float32)
            dark = patch[al > 0.7]
            if len(dark) > 4:
                lum = dark.mean(1)
                ink = dark[lum <= np.percentile(lum, 25)].mean(0)
            else:
                ink = np.array([30, 24, 20], np.float32)
            info = dict(c=(x * UP - x0, y * UP - y0), size=(hx * UP, hy * UP), ink=np.minimum(ink, 60).astype(np.float32),
                        thick=float(np.clip(al.sum() / max(1.0, 2 * hx * UP), 3, 12)))
            parts.append(((x0, y0, x1, y1), patch, al, info))
            hole[y0:y1, x0:x1] |= (cv2.dilate(al, np.ones((7, 7), np.uint8)) > 0.05).astype(np.uint8)
        pad = 40 * UP
        ys, xs = np.where(hole)
        Y0, Y1, X0, X1 = max(0, ys.min() - pad), ys.max() + pad, max(0, xs.min() - pad), xs.max() + pad
        clean[Y0:Y1, X0:X1] = cv2.inpaint(a[Y0:Y1, X0:X1], hole[Y0:Y1, X0:X1], 9, cv2.INPAINT_TELEA)
        return clean, parts

    def apply(self, a, t, copy=True):
        if self._prep is None:
            self._prep = self._parts(up(self.img))
        clean, parts = self._prep
        out = a.copy() if copy else a
        blink = max([_pulse(t, b, 0.17) for b in self.blinks] + [0.0])
        gx = sum(dx * _hold(t, t0, t1) for t0, t1, dx, dy in self.glances)
        gy = sum(dy * _hold(t, t0, t1) for t0, t1, dx, dy in self.glances)
        wide = sum(w * _hold(t, t0, t1, 0.1) for t0, t1, w in self.widen)
        for i, ((x0, y0, x1, y1), patch, al, info) in enumerate(parts):
            out[y0:y1, x0:x1] = clean[y0:y1, x0:x1]
            h, w = al.shape
            cx, cy = info["c"]
            is_eye = i < len(self.eyes)
            shape, e = None, 0.0
            for t0, t1, ms, es in self.expr:
                k = _hold(t, t0, t1, 0.18)
                sh = es if is_eye else ms
                if sh and k > e:
                    shape, e = sh, k
            if not is_eye and self.talk:
                kt = max(_hold(t, a_, b_, 0.05) * math.sin(math.pi * min(1.0, max(0.0, (t - a_) / max(0.08, b_ - a_))))
                         for a_, b_ in self.talk)
                if any(a_ - 0.15 <= t <= b_ + 0.15 for a_, b_ in self.talk):
                    shape, e = ("talk", kt), 1.0
            if shape is not None and e > 0:
                d_al, d_fill = _draw_part(shape, info, (h, w), is_eye, self.seed + i, (gx * UP, gy * UP) if is_eye else (0, 0))
                if is_eye and blink > 0 and shape in ("half", "squint"):
                    d_al = d_al * (1 - blink * 0.9)
                reg = out[y0:y1, x0:x1].astype(np.float32)
                orig_a = (al * (1 - e))[..., None]
                reg = reg * (1 - orig_a) + patch * orig_a
                fa = (d_fill * e)[..., None]
                reg = reg * (1 - fa) + MOUTH_IN * fa  # the warm inside of an open mouth, like the painted ones
                da = (d_al * e)[..., None]
                out[y0:y1, x0:x1] = (reg * (1 - da) + info["ink"] * da).astype(np.uint8)
                continue
            if is_eye:
                sy = max(0.08, (1 - blink * 0.94) * (1 + wide))
                sx = 1 + wide * 0.6
                M = np.float32([[sx, 0, cx - sx * cx + gx * UP], [0, sy, cy - sy * cy + gy * UP]])
                p2 = cv2.warpAffine(patch, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
                a2 = cv2.warpAffine(al, M, (w, h))
            else:
                p2, a2 = patch, al
                for t0, t1, kind, amt in self.mouth_fx:
                    k = _hold(t, t0, t1, 0.15)
                    if k <= 0:
                        continue
                    if kind == "wobble":  # the line trembles
                        xs = np.arange(w, dtype=np.float32)
                        dy = (amt * UP * k * np.sin(xs / w * 2 * math.pi * 1.5 + t * 22)).astype(np.float32)
                        mx = np.tile(xs, (h, 1))
                        my = np.arange(h, dtype=np.float32)[:, None] - dy[None, :]
                        p2 = cv2.remap(p2, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                        a2 = cv2.remap(a2, mx, my, cv2.INTER_LINEAR)
                    else:  # "open": the mouth opens / quivers; "smile": the corners lift
                        s_ = 1 + amt * k * (1 + 0.15 * math.sin(t * 30)) if kind == "open" else 1.0
                        M = np.float32([[1, 0, 0], [0, s_, cy - s_ * cy]])
                        if kind == "smile":
                            xs = (np.arange(w, dtype=np.float32) - cx) / cx
                            dy = (-amt * UP * k * xs ** 2).astype(np.float32)
                            mx = np.tile(np.arange(w, dtype=np.float32), (h, 1))
                            my = np.arange(h, dtype=np.float32)[:, None] - dy[None, :]
                            p2 = cv2.remap(p2, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
                            a2 = cv2.remap(a2, mx, my, cv2.INTER_LINEAR)
                        else:
                            p2 = cv2.warpAffine(p2, M, (w, h), borderMode=cv2.BORDER_REPLICATE)
                            a2 = cv2.warpAffine(a2, M, (w, h))
            reg = out[y0:y1, x0:x1].astype(np.float32)
            out[y0:y1, x0:x1] = (reg * (1 - a2[..., None]) + p2 * a2[..., None]).astype(np.uint8)
        return out

    def __call__(self, a, t):
        return self.apply(a, t)


# ---------------------------------------------------------------- living stills


class Flow:
    """One painted area that moves: kind "rise" (smoke, steam: drifts up and sways), "run" (water: slides sideways).
    poly = the area in source px; its edge is feathered so the motion melts into the still picture. Two copies of the
    area slide in turn and cross-fade, so the motion loops with no seam."""

    def __init__(self, img, poly, kind="rise", speed=18.0, sway=6.0, period=3.0, feather=18):
        self.img, self.kind, self.speed, self.sway, self.period = img, kind, speed, sway, period
        poly = np.array(poly, np.float32)
        x0, y0 = np.maximum(0, poly.min(0) - feather - 10).astype(int)
        x1, y1 = np.minimum([SW, SH], poly.max(0) + feather + 10).astype(int)
        self.box = (x0 * UP, y0 * UP, x1 * UP, y1 * UP)
        m = np.zeros(((y1 - y0) * UP, (x1 - x0) * UP), np.float32)
        cv2.fillPoly(m, [((poly - [x0, y0]) * UP).astype(np.int32)], 1.0)
        self.mask = cv2.GaussianBlur(m, (0, 0), feather * UP / 2)[..., None]

    def apply(self, a, t):
        X0, Y0, X1, Y1 = self.box
        src = up(self.img)[Y0:Y1, X0:X1].astype(np.float32)
        h, w = src.shape[:2]
        xs, ys = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
        acc = np.zeros_like(src)
        for ph in (0.0, 0.5):
            u = ((t / self.period) + ph) % 1.0
            wgt = 1 - abs(2 * u - 1)  # triangle: each copy fades in and out as it slides
            d = (u - 0.5) * self.speed * self.period * UP
            sw = self.sway * UP * np.sin(ys / (60 * UP) * 2 * math.pi + t * 1.3 + ph * 7)
            if self.kind == "rise":
                mx, my = xs + sw, ys + d
            else:
                mx, my = xs - d, ys + sw * 0.25
            acc += cv2.remap(src, mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT) * wgt
        out = a.copy()
        reg = out[Y0:Y1, X0:X1].astype(np.float32)
        out[Y0:Y1, X0:X1] = (reg * (1 - self.mask) + acc * self.mask).astype(np.uint8)
        return out

    def __call__(self, a, t):
        return self.apply(a, t)


# ---------------------------------------------------------------- the comic page


def _ink_of(rgb):
    """An ink drawing pulled out of a painted image: its dark lines and edges, for the 'ink first' stage."""
    g = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY).astype(np.float32)
    loc = cv2.GaussianBlur(g, (0, 0), 6)
    ink = np.clip((loc - g - 6) / 38, 0, 1) + np.clip((70 - g) / 70, 0, 1) * 0.6
    return np.clip(ink, 0, 1)


class Comic:
    """A comic page on a blank board. panels = [dict(box=(x0, y0, x1, y1) on the board, img=..., focus=(cx, cy, h),
    t=(t_ink, t_paint, t_done), face=Face | None, src_fx=[...]), ...]. The borders draw themselves in border_t,
    each panel's shot inks in then paints in over its times. Coordinates on the board are source px."""

    def __init__(self, board, panels, border_t, width=7.0):
        self.board, self.panels, self.border_t, self.width = board, panels, border_t, width
        self._cache = {}
        r = np.random.default_rng(3)
        self.path = []  # the borders, panel by panel, as one pen path with a little wobble
        for p in panels:
            x0, y0, x1, y1 = p["box"]
            pts = np.array([(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], np.float32)
            dense = np.concatenate([np.linspace(a, b, 40, endpoint=False) for a, b in zip(pts, pts[1:])] + [pts[-1:]])
            dense += r.normal(0, 0.6, dense.shape)
            self.path.append(dense)
        self.lens = np.array([np.sum(np.hypot(*np.diff(d, axis=0).T)) for d in self.path])

    def _panel(self, i):
        if i not in self._cache:
            p = self.panels[i]
            x0, y0, x1, y1 = p["box"]
            W, H = (x1 - x0) * UP, (y1 - y0) * UP
            r = np.random.default_rng(i)
            noise = cv2.resize(r.random((max(2, H // 50), max(2, W // 50))).astype(np.float32), (W, H), interpolation=cv2.INTER_CUBIC)
            grad = (np.arange(W, dtype=np.float32)[None, :] / W * 0.6 + np.arange(H, dtype=np.float32)[:, None] / H * 0.4)
            T = np.clip(0.75 * grad + 0.35 * noise, 0, 1)
            self._cache[i] = T
        return self._cache[i]

    def _crop(self, p, a):
        x0, y0, x1, y1 = p["box"]
        W, H = (x1 - x0) * UP, (y1 - y0) * UP
        cx, cy, h = p["focus"]
        w = h * (x1 - x0) / (y1 - y0)
        if w > SW:
            w, h = SW, SW * (y1 - y0) / (x1 - x0)
        cx = min(max(cx, w / 2), SW - w / 2)
        cy = min(max(cy, h / 2), SH - h / 2)
        s = UP * h / H
        M = np.float32([[s, 0, UP * (cx - w / 2)], [0, s, UP * (cy - h / 2)]])
        return cv2.warpAffine(a, M, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)

    def img2x(self, t):
        out = up(self.board).astype(np.float32).copy()
        paper = np.array([244, 236, 216], np.float32)
        for i, p in enumerate(self.panels):
            ta, tb, tc = p["t"]
            if t < ta:
                continue
            T = self._panel(i)
            a = up(p["img"])
            for f in p.get("src_fx", []):
                a = f(a, t)
            pic = self._crop(p, a).astype(np.float32)
            ink = _ink_of(pic.astype(np.uint8))
            rev = np.clip((t - (ta + T * (tb - ta))) / 0.08, 0, 1)
            wash = np.clip((t - (tb + T * (tc - tb))) / 0.25, 0, 1)[..., None]
            x0, y0, x1, y1 = [v * UP for v in p["box"]]
            reg = out[y0:y1, x0:x1]
            drawn = paper * (1 - (rev * ink)[..., None] * 0.85) + np.array([34, 27, 22], np.float32) * (rev * ink)[..., None] * 0.0
            inside = np.clip((t - ta) / 0.15, 0, 1)
            reg = reg * (1 - inside) + drawn * inside
            out[y0:y1, x0:x1] = reg * (1 - wash) + pic * wash
        # the borders, drawn on top
        a0, a1 = self.border_t
        u = np.clip((t - a0) / max(1e-6, a1 - a0), 0, 1) * self.lens.sum()
        lay = np.zeros(out.shape[:2], np.uint8)
        for d, L in zip(self.path, self.lens):
            if u <= 0:
                break
            seg = np.cumsum(np.r_[0, np.hypot(*np.diff(d, axis=0).T)])
            k = int(np.searchsorted(seg, min(u, L)))
            if k >= 1:
                cv2.polylines(lay, [(d[:k + 1] * UP * 4).astype(np.int32)], False, 255, int(self.width * UP), cv2.LINE_AA, shift=2)
            u -= L
        al = cv2.GaussianBlur(lay.astype(np.float32) / 255, (0, 0), 0.8)[..., None]
        return out * (1 - al * 0.95) + np.array([28, 22, 18], np.float32) * al * 0.95

    def pen(self, t):
        a0, a1 = self.border_t
        if not a0 <= t <= a1:
            return None
        u = (t - a0) / (a1 - a0) * self.lens.sum()
        for d, L in zip(self.path, self.lens):
            if u <= L:
                seg = np.cumsum(np.r_[0, np.hypot(*np.diff(d, axis=0).T)])
                k = min(len(d) - 1, int(np.searchsorted(seg, u)))
                return "pen", (float(d[k][0]), float(d[k][1]))
            u -= L
        return None


# ---------------------------------------------------------------- frame-space touches (post=[...])


def dim(boxes):
    """Case board: [(box, t0, t1), ...] in source px; from t0 the drawing fades back (lighter, greyer) until t1."""

    def f(img, t, s, cam):
        for box, t0, t1 in boxes:
            k = _hold(t, t0, t1, 0.4) * 0.6
            if k <= 0:
                continue
            (x0, y0), (x1, y1) = s.to_screen(box[:2], cam), s.to_screen(box[2:], cam)
            x0, y0 = max(0, int(x0)), max(0, int(y0))
            x1, y1 = min(img.shape[1], int(x1)), min(img.shape[0], int(y1))
            if x1 <= x0 or y1 <= y0:
                continue
            reg = img[y0:y1, x0:x1]
            g = reg.mean(2, keepdims=True)
            img[y0:y1, x0:x1] = reg * (1 - k) + (g * 0.55 + 248 * 0.45) * k
        return img

    return f


def cutout(path):
    """A flat cartoon on a plain background (the narrator's hand) -> RGBA, the background flood-filled away from the
    edges (so the white glove, which is close to the cream background, stays)."""
    a = cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)
    h, w = a.shape[:2]
    m = np.zeros((h + 2, w + 2), np.uint8)
    flags = 4 | cv2.FLOODFILL_MASK_ONLY | cv2.FLOODFILL_FIXED_RANGE | (255 << 8)
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0)):
        cv2.floodFill(a.copy(), m, p, 0, (10, 10, 10), (10, 10, 10), flags)
    al = 1 - m[1:-1, 1:-1].astype(np.float32) / 255
    al = cv2.GaussianBlur(cv2.erode(al, np.ones((3, 3), np.uint8)), (0, 0), 0.8)
    ys, xs = np.where(al > 0.5)
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    return a[y0:y1, x0:x1].astype(np.float32), al[y0:y1, x0:x1]


class Hand:
    """the narrator's gloved hand slides a folded note up from the bottom edge (t_in), holds, and leaves (t_out).
    x = where it stands across the frame (0-1), height = its size as a share of the frame height."""

    def __init__(self, path, t_in, t_out, x=0.78, height=0.62, tilt=-6):
        self.rgb, self.al = cutout(path)
        self.t_in, self.t_out, self.x, self.height, self.tilt = t_in, t_out, x, height, tilt

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t_in or t > self.t_out + 0.5:
            return img
        H, W = img.shape[:2]
        k_in = ease((t - self.t_in) / 0.55, "out")
        k_out = ease((t - self.t_out) / 0.45, "in")
        hh = self.height * H
        sc = hh / self.rgb.shape[0]
        ww = self.rgb.shape[1] * sc
        y_rest = H - hh * 0.92 + 4 * math.sin(t * 2.2)
        y = H + (y_rest - H) * k_in + (H - y_rest) * k_out
        cx = self.x * W
        ang = self.tilt * (1 - k_in) * 2 + self.tilt
        M = cv2.getRotationMatrix2D((self.rgb.shape[1] / 2, self.rgb.shape[0] / 2), ang, sc)
        M[0, 2] += cx - self.rgb.shape[1] / 2
        M[1, 2] += y + hh / 2 - self.rgb.shape[0] / 2
        rgb = cv2.warpAffine(self.rgb, M, (W, H))
        al = cv2.warpAffine(self.al, M, (W, H))[..., None]
        sh = cv2.GaussianBlur(cv2.warpAffine(self.al, M + np.float32([[0, 0, 10 * W / 1920], [0, 0, 14 * W / 1920]]), (W, H)),
                              (0, 0), 12 * W / 1920)[..., None]
        img = img * (1 - sh * 0.35)
        return img * (1 - al) + rgb * al


def pad_to_canvas(src, name, bg=None):
    """A base or cartoon of any shape fitted whole onto the 2:1 canvas (padded with its own background) and saved
    under build/edit/<name>.png, where the engine finds it like any image."""
    a = cv2.cvtColor(cv2.imread(str(src)), cv2.COLOR_BGR2RGB)
    s_ = min(SW / a.shape[1], SH / a.shape[0])
    a = cv2.resize(a, (round(a.shape[1] * s_), round(a.shape[0] * s_)), interpolation=cv2.INTER_AREA)
    out = np.empty((SH, SW, 3), np.uint8)
    out[:] = bg if bg is not None else np.median(a[:6].reshape(-1, 3), 0)
    y0, x0 = (SH - a.shape[0]) // 2, (SW - a.shape[1]) // 2
    out[y0:y0 + a.shape[0], x0:x0 + a.shape[1]] = a
    f = film.BUILD / "edit" / f"{name}.png"
    f.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(f), cv2.cvtColor(out, cv2.COLOR_RGB2BGR))
    return name


# ---------------------------------------------------------------- slap-ons: stamps and paper tags (post=[...])

TYPE = ytf.font("type")
STAMP = ytf.font("stamp")


def _text_img(text, font, size, fill, pad=10):
    from PIL import Image, ImageDraw, ImageFont
    f = ImageFont.truetype(font, int(size))
    b = f.getbbox(text)
    im = Image.new("L", (b[2] - b[0] + 2 * pad, b[3] - b[1] + 2 * pad))
    ImageDraw.Draw(im).text((pad - b[0], pad - b[1]), text, font=f, fill=fill)
    return np.asarray(im, np.float32) / 255


def _paste(img, rgb, al, center, scale, angle):
    H, W = img.shape[:2]
    h, w = al.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, scale)
    M[0, 2] += center[0] - w / 2
    M[1, 2] += center[1] - h / 2
    a = cv2.warpAffine(al, M, (W, H))[..., None]
    c = cv2.warpAffine(rgb, M, (W, H)) if np.ndim(rgb) == 3 else np.array(rgb, np.float32)
    return img * (1 - a) + c * a


class Stamp:
    """A rubber-stamped word (red, distressed, boxed) that thuds onto the picture at t0: 175% -> 92% -> 100%.
    xy in source px; it moves with the camera. Pair with b.fx("stamp", t0)."""

    def __init__(self, text, xy, t0, size=70, angle=-8, color=(178, 34, 30), t1=None):
        r = np.random.default_rng(len(text))
        m = _text_img(text, STAMP, size, 255, pad=int(size * 0.35))
        h, w = m.shape
        box = np.zeros_like(m)
        b = max(3, int(size * 0.08))
        cv2.rectangle(box, (b, b), (w - b, h - b), 1.0, b)
        al = np.clip(m + box, 0, 1)
        grit = cv2.GaussianBlur(r.random((h, w)).astype(np.float32), (0, 0), 1.2)
        self.al = al * np.clip((grit - 0.28) * 3, 0.25, 1) * 0.9  # ink that didn't take everywhere
        self.color, self.xy, self.t0, self.t1, self.angle = color, xy, t0, t1, angle

    def __call__(self, img, t, s, cam):
        if t < self.t0 or (self.t1 and t > self.t1):
            return img
        u = t - self.t0
        k = 1.75 - 0.83 * ease(u / 0.09) if u < 0.09 else (0.92 + 0.08 * ease((u - 0.09) / 0.08))
        a = min(1.0, u / 0.05)
        return _paste(img, self.color, self.al * a, s.to_screen(self.xy, cam), k * img.shape[0] / cam[2], self.angle)


class Tag:
    """A torn cream paper strip with a typed word slapped onto the picture (labels for people and places that
    need weight): it lands with a small overshoot and a tilt. xy in source px."""

    def __init__(self, text, xy, t0, size=40, angle=-3, t1=None):
        r = np.random.default_rng(len(text) + 7)
        m = _text_img(text, TYPE, size, 255, pad=int(size * 0.55))
        h, w = m.shape
        edge = np.ones((h, w), np.float32)
        for side in (0, 1):  # torn ends
            j = np.cumsum(r.normal(0, 1.2, h)).astype(int) % 6 + 4
            for y in range(h):
                if side:
                    edge[y, w - j[y]:] = 0
                else:
                    edge[y, :j[y]] = 0
        self.al = cv2.GaussianBlur(edge, (0, 0), 0.7)
        paper = np.empty((h, w, 3), np.float32)
        paper[:] = (240, 230, 206)
        paper += cv2.GaussianBlur(r.standard_normal((h, w)).astype(np.float32), (0, 0), 2)[..., None] * 6
        self.rgb = paper * (1 - m[..., None] * 0.9) + np.array([34, 28, 24], np.float32) * m[..., None] * 0.9
        self.xy, self.t0, self.t1, self.angle = xy, t0, t1, angle

    def __call__(self, img, t, s, cam):
        if t < self.t0 or (self.t1 and t > self.t1):
            return img
        u = t - self.t0
        k = 1.22 - 0.27 * ease(u / 0.08) if u < 0.08 else 0.95 + 0.05 * ease((u - 0.08) / 0.1)
        ang = self.angle + (4 * (1 - ease(u / 0.18)) if u < 0.18 else 0)
        sc = k * (OH / cam[2])
        c = s.to_screen(self.xy, cam)
        sh = cv2.GaussianBlur(self.al, (0, 0), 4)
        img = _paste(img, (0, 0, 0), sh * 0.35 * min(1, u / 0.05), (c[0] + 5, c[1] + 7), sc, ang)
        return _paste(img, self.rgb, self.al * min(1, u / 0.04), c, sc, ang)


from film import OH, OW  # noqa: E402  (screen size, for the slap-ons)


# ---------------------------------------------------------------- light and air (post=[...])


class Rays:
    """Soft shafts of light from a window or a torch: beams from `origin` (source px) towards `angle` (degrees,
    0 = right, 90 = down), `spread` degrees wide, with dust drifting in them. t0/t1 fade in/out; `flicker` for torches."""

    def __init__(self, origin, angle, spread=24, length=900, t0=-1, t1=1e9, amount=0.22, color=(255, 236, 196),
                 flicker=0.0, n=5, seed=2):
        r = np.random.default_rng(seed)
        self.o, self.ang, self.spread, self.len = origin, angle, spread, length
        self.t0, self.t1, self.amount, self.color, self.flicker = t0, t1, amount, color, flicker
        self.beams = [(r.uniform(-0.5, 0.5) * spread, r.uniform(2, 6), r.uniform(0.5, 1.0), r.uniform(0, 6)) for _ in range(n)]
        self.dust = r.uniform(0, 1, (60, 3))

    def __call__(self, img, t, s, cam):
        k = _hold(t, self.t0, self.t1, 0.6) * self.amount
        if k <= 0:
            return img
        H, W = img.shape[:2]
        sc = OH / cam[2]
        o = np.array(s.to_screen(self.o, cam))
        L = self.len * sc
        m = np.zeros((H // 4, W // 4), np.float32)
        for off, wdeg, g, ph in self.beams:
            a = math.radians(self.ang + off + 1.5 * math.sin(t * 0.3 + ph))
            hw = math.radians(wdeg)
            pts = [o, o + L * np.array([math.cos(a - hw), math.sin(a - hw)]), o + L * np.array([math.cos(a + hw), math.sin(a + hw)])]
            cv2.fillPoly(m, [(np.array(pts) / 4).astype(np.int32)], g * (1 + self.flicker * math.sin(t * 17 + ph) * 0.5))
        yy, xx = np.mgrid[0:H // 4, 0:W // 4].astype(np.float32)
        fall = np.clip(1 - np.hypot(xx - o[0] / 4, yy - o[1] / 4) / (L / 4), 0, 1)
        m = cv2.GaussianBlur(m * fall, (0, 0), 9)
        m = cv2.resize(m, (W, H))[..., None]
        img = img + (np.array(self.color, np.float32) - img * 0.4) * m * k
        for x, y, z in self.dust:  # motes turning in the light
            p = o + L * 0.7 * np.array([math.cos(math.radians(self.ang + (x - 0.5) * self.spread)),
                                        math.sin(math.radians(self.ang + (x - 0.5) * self.spread))]) * ((y + t * 0.02 * (0.5 + z)) % 1)
            if 0 <= p[0] < W and 0 <= p[1] < H:
                b = m[int(p[1]), int(p[0]), 0]
                cv2.circle(img, (int(p[0]), int(p[1])), max(1, int(1.5 * z * W / 1920)), tuple(float(v) for v in self.color), -1, cv2.LINE_AA) if b * k > 0.02 else None
        return img


class Haze:
    """Drifting air (mist over the river, smoke hanging in a room, cold breath of a winter street): a slow,
    soft, low-contrast veil in the lower or upper part of the frame. region = (y0, y1) as 0-1 of the screen."""

    def __init__(self, region=(0.45, 1.0), amount=0.18, color=(226, 224, 220), speed=0.03, t0=-1, t1=1e9, seed=5):
        r = np.random.default_rng(seed)
        self.n = [cv2.resize(cv2.GaussianBlur(r.random((54, 192)).astype(np.float32), (0, 0), 5), (OW * 2, OH)) for _ in range(2)]
        self.region, self.amount, self.color, self.speed, self.t0, self.t1 = region, amount, np.array(color, np.float32), speed, t0, t1
        yy = np.linspace(0, 1, OH, dtype=np.float32)[:, None]
        y0, y1 = region
        self.band = np.clip(np.minimum((yy - y0) / 0.15, (y1 - yy) / 0.15 + 1), 0, 1)

    def __call__(self, img, t, s, cam):
        k = _hold(t, self.t0, self.t1, 0.8) * self.amount
        if k <= 0:
            return img
        o1 = int((t * self.speed * OW) % OW)
        o2 = int((t * self.speed * 0.6 * OW + OW / 3) % OW)
        n = 0.6 * self.n[0][:, o1:o1 + OW] + 0.4 * self.n[1][:, o2:o2 + OW]
        n = (n - n.min()) / (n.max() - n.min() + 1e-6)
        m = (n * self.band)[..., None] * k
        return img * (1 - m) + self.color * m


# ---------------------------------------------------------------- ink drawn into a scene (src_fx=[...])


class Inset:
    """A drawing from a sheet's line version (or any _lines image), drawn into a scene in ink at t0..t1: a bouquet
    beside a teller, a rope down a wall, a little helicopter over the river. src = the _lines image, box = its region
    (source px of that image), at = centre in the scene, height = its height in the scene (source px). The drawing
    appears stroke-like from dark to light lines along a sweep, on a soft paper glow so it reads on dark ground;
    `color` "ink" or "cream" (chalk-like on dark scenes)."""

    def __init__(self, src, box, at, height, t0, t1, color="ink", sweep=(1, 0.4), glow=0.55, t_out=None):
        a = cv2.cvtColor(up(src), cv2.COLOR_RGB2GRAY).astype(np.float32) / 255
        x0, y0, x1, y1 = [v * UP for v in box]
        a = a[y0:y1, x0:x1]
        s_ = height * UP / a.shape[0]
        a = cv2.resize(a, (int(a.shape[1] * s_), int(a.shape[0] * s_)), interpolation=cv2.INTER_AREA)
        ink = np.clip((0.92 - a) / 0.75, 0, 1)
        h, w = ink.shape
        r = np.random.default_rng(int(at[0]))
        noise = cv2.resize(r.random((max(2, h // 40), max(2, w // 40))).astype(np.float32), (w, h), interpolation=cv2.INTER_CUBIC)
        xs, ys = np.meshgrid(np.linspace(0, 1, w, dtype=np.float32), np.linspace(0, 1, h, dtype=np.float32))
        self.T = np.clip(0.55 * (sweep[0] * ys + sweep[1] * xs) / (abs(sweep[0]) + abs(sweep[1])) + 0.25 * noise + 0.2 * a, 0, 1)
        self.ink = ink
        self.halo = np.clip(cv2.GaussianBlur(cv2.dilate(ink, np.ones((9, 9), np.uint8)), (0, 0), 6) * 1.6, 0, 1)
        cx, cy = at
        self.pos = (int(cx * UP - w / 2), int(cy * UP - h / 2))
        self.t0, self.t1, self.t_out, self.glow = t0, t1, t_out, glow
        self.col = np.array((34, 27, 22) if color == "ink" else (244, 238, 222), np.float32)
        self.paper = np.array((246, 238, 220) if color == "ink" else (20, 16, 12), np.float32)

    def __call__(self, a, t):
        if t < self.t0:
            return a
        rev = np.clip((t - (self.t0 + self.T * (self.t1 - self.t0))) / 0.08, 0, 1)
        if self.t_out is not None:
            rev = rev * (1 - ease((t - self.t_out) / 0.5))
        X, Y = self.pos
        h, w = self.ink.shape
        H, W = a.shape[:2]
        x0, y0, x1, y1 = max(0, X), max(0, Y), min(W, X + w), min(H, Y + h)
        out = a.copy()
        reg = out[y0:y1, x0:x1].astype(np.float32)
        sl = (slice(y0 - Y, y1 - Y), slice(x0 - X, x1 - X))
        hal = (cv2.GaussianBlur(rev, (0, 0), 6)[sl] * self.halo[sl] * self.glow)[..., None]
        ink = (rev * self.ink)[sl][..., None] * 0.92
        reg = reg * (1 - hal) + self.paper * hal
        out[y0:y1, x0:x1] = (reg * (1 - ink) + self.col * ink).astype(np.uint8)
        return out


# ---------------------------------------------------------------- objects that count (post=[...] on a base)


class Flip:
    """Split-flap numbers in a window of the scoreboard (B08): `values` = [(t, "07"), ...]; each change flips the
    tiles over in 0.22 s. box = the window in source px; cream digits on dark tiles."""

    def __init__(self, box, values, size=None):
        self.box, self.values = box, values
        self.size = size

    def _digit(self, txt, w, h):
        m = _text_img(txt, STAMP, h * 0.78, 255, pad=0)
        out = np.zeros((h, w), np.float32)
        mh, mw = m.shape
        s_ = min(w * 0.86 / mw, h * 0.8 / mh)
        m = cv2.resize(m, (max(1, int(mw * s_)), max(1, int(mh * s_))))
        y, x = (h - m.shape[0]) // 2, (w - m.shape[1]) // 2
        out[y:y + m.shape[0], x:x + m.shape[1]] = m
        return out

    def __call__(self, img, t, s, cam):
        cur = [v for v in self.values if v[0] <= t]
        if not cur:
            return img
        t_c, txt = cur[-1]
        prev = cur[-2][1] if len(cur) > 1 else None
        (x0, y0), (x1, y1) = s.to_screen(self.box[:2], cam), s.to_screen(self.box[2:], cam)
        x0, y0, x1, y1 = int(x0), int(y0), int(x1), int(y1)
        n = len(txt)
        tw = (x1 - x0) // n
        H, W = img.shape[:2]
        for i, ch in enumerate(txt):
            X0, X1 = x0 + i * tw + 4, x0 + (i + 1) * tw - 4
            if X1 <= 0 or X0 >= W or y1 <= 0 or y0 >= H:
                continue
            w, h = X1 - X0, y1 - y0
            tile = np.empty((h, w, 3), np.float32)
            tile[:] = (34, 32, 30)
            tile[h // 2 - 1:h // 2 + 1] = (16, 14, 12)
            new = self._digit(ch, w, h)
            u = (t - t_c) / 0.22
            if prev is not None and u < 1 and (len(prev) == n and prev[i] != ch):
                old = self._digit(prev[i], w, h)
                d = np.where(np.arange(h)[:, None] < h // 2, new, old) if u < 0.5 else np.where(np.arange(h)[:, None] < h // 2, new, new)
                k = abs(math.cos(math.pi * u))
                hh = max(1, int(h / 2 * k))
                flap = cv2.resize((old if u < 0.5 else new)[: h // 2] if u < 0.5 else new[h // 2:], (w, hh))
                d = d.copy()
                if u < 0.5:
                    d[h // 2 - hh:h // 2] = flap
                else:
                    d[h // 2:h // 2 + hh] = flap
                new = d
            tile = tile * (1 - new[..., None]) + np.array([244, 232, 200], np.float32) * new[..., None]
            ya, yb, xa, xb = max(0, y0), min(H, y1), max(0, X0), min(W, X1)
            img[ya:yb, xa:xb] = tile[ya - y0:yb - y0, xa - X0:xb - X0]
        return img


class Rings:
    """Wet glass rings stamped onto the napkin (B05), one per cue, overlapping and darkening; source px.
    rings = [(t, (cx, cy), r), ...]; `bottle` = (t, (cx, cy), r) a wider, darker ring at the end."""

    def __init__(self, rings, color=(150, 96, 40)):
        self.rings, self.color = rings, np.array(color, np.float32)
        self._m = {}

    def _ring(self, i, r):
        if i not in self._m:
            g = np.random.default_rng(i)
            R = int(r * UP)
            S = 2 * R + 40
            m = np.zeros((S, S), np.float32)
            th = np.linspace(0, 2 * math.pi, 400)
            rr = R * (1 + 0.02 * np.sin(th * 3 + g.uniform(0, 6)))
            pts = np.stack([S / 2 + rr * np.cos(th), S / 2 + rr * np.sin(th)], 1).astype(np.int32)
            cv2.polylines(m, [pts], True, 1.0, int(R * 0.09), cv2.LINE_AA)
            m = cv2.GaussianBlur(m, (0, 0), 2.5) * 0.7 + cv2.GaussianBlur(m, (0, 0), 0.8) * 0.5
            gap = g.uniform(0, 2 * math.pi)  # a ring is never complete
            yy, xx = np.mgrid[0:S, 0:S]
            ang = np.arctan2(yy - S / 2, xx - S / 2)
            m *= np.clip(np.abs(np.angle(np.exp(1j * (ang - gap)))) / 0.7, 0.15, 1)
            m += cv2.GaussianBlur((g.random((S, S)) < 0.0008).astype(np.float32), (0, 0), 3) * 8 * (np.hypot(yy - S / 2, xx - S / 2) < R)
            self._m[i] = np.clip(m, 0, 1)
        return self._m[i]

    def __call__(self, a, t):
        out = None
        for i, (t0, c, r) in enumerate(self.rings):
            if t < t0:
                continue
            if out is None:
                out = a.astype(np.float32)
            m = self._ring(i, r) * min(1, (t - t0) / 0.12) * 0.55
            S = m.shape[0]
            X, Y = int(c[0] * UP - S / 2), int(c[1] * UP - S / 2)
            reg = out[Y:Y + S, X:X + S]
            mm = m[:reg.shape[0], :reg.shape[1], None]
            out[Y:Y + S, X:X + S] = reg * (1 - mm) + reg * (self.color / 255) * mm
        return a if out is None else out.astype(np.uint8)


class Pin:
    """A photo or a cut-out panel pinned onto the corkboard (B01): it drops in with a little bounce, casts a
    shadow and gets a pin. src = image name, crop = (x0, y0, x1, y1) of it in source px, at = centre on the board,
    height in board px, angle in degrees. Used as src_fx on the board shot."""

    def __init__(self, src, crop, at, height, t0, angle=-3, border=10):
        a = up(src)
        x0, y0, x1, y1 = [v * UP for v in crop]
        a = a[y0:y1, x0:x1]
        s_ = height * UP / a.shape[0]
        a = cv2.resize(a, (int(a.shape[1] * s_), int(a.shape[0] * s_)), interpolation=cv2.INTER_AREA).astype(np.float32)
        b = border * UP
        card = np.full((a.shape[0] + 2 * b, a.shape[1] + 2 * b, 3), (238, 232, 218), np.float32)
        card[b:b + a.shape[0], b:b + a.shape[1]] = a
        self.card, self.at, self.t0, self.angle = card, at, t0, angle

    def __call__(self, a, t):
        if t < self.t0:
            return a
        u = t - self.t0
        k = 1.12 - 0.12 * ease(u / 0.14) if u < 0.14 else 1.0
        h, w = self.card.shape[:2]
        H, W = a.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), self.angle + (3 * (1 - ease(u / 0.2)) if u < 0.2 else 0), k)
        M[0, 2] += self.at[0] * UP - w / 2
        M[1, 2] += self.at[1] * UP - h / 2
        al = cv2.warpAffine(np.ones((h, w), np.float32), M, (W, H))
        sh = cv2.GaussianBlur(cv2.warpAffine(np.ones((h, w), np.float32), M + np.float32([[0, 0, 14], [0, 0, 18]]), (W, H)), (0, 0), 10)
        c = cv2.warpAffine(self.card, M, (W, H))
        out = a.astype(np.float32) * (1 - sh[..., None] * 0.45)
        out = out * (1 - al[..., None]) + c * al[..., None]
        px, py = int(self.at[0] * UP), int((self.at[1] * UP - h * k / 2) + 14 * UP)
        cv2.circle(out, (px + 3, py + 4), 9 * UP, (40, 30, 25), -1, cv2.LINE_AA)
        cv2.circle(out, (px, py), 9 * UP, (190, 40, 34), -1, cv2.LINE_AA)
        cv2.circle(out, (px - 3, py - 3), 3 * UP, (240, 160, 150), -1, cv2.LINE_AA)
        return np.clip(out, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- the mark vocabulary (beyond the circle)
# Each adds strokes to a Marks (m) in source px. Choose by meaning: underline = this word/thing matters; tick =
# done/true; cross = wrong/gone; bracket = these belong together; motion = it's moving fast; rings = a sound or an
# alarm; route = the path he took; leader = name a detail without covering it; tally = counting.


def underline(m, a, b, t0, dur=0.35, color="red", width=5):
    y = (a[1] + b[1]) / 2
    xs = np.linspace(a[0], b[0], 12)
    m.stroke([(x, y + 3 * math.sin(i * 0.9)) for i, x in enumerate(xs)], t0, dur, color, width, 0.2)


def tick(m, c, size, t0, dur=0.3, color="red", width=6):
    x, y = c
    m.stroke([(x - size * 0.5, y), (x - size * 0.15, y + size * 0.4), (x + size * 0.6, y - size * 0.6)], t0, dur, color, width, 0.1)


def cross(m, box, t0, dur=0.4, color="red", width=6):
    x0, y0, x1, y1 = box
    m.stroke([(x0, y0), (x1, y1)], t0, dur / 2, color, width, 0.1)
    m.stroke([(x1, y0), (x0, y1)], t0 + dur / 2, dur / 2, color, width, 0.1)


def bracket(m, x, y0, y1, t0, dur=0.4, color="red", width=4, side=1):
    d = 22 * side
    m.stroke([(x - d, y0), (x, y0 + 10), (x, (y0 + y1) / 2 - 12), (x + d * 0.8, (y0 + y1) / 2), (x, (y0 + y1) / 2 + 12),
              (x, y1 - 10), (x - d, y1)], t0, dur, color, width, 0.2)


def motion(m, c, direction, n, length, t0, dur=0.35, color="auto", width=4, spread=40):
    """Speed lines trailing behind something moving (direction = where it's going, degrees)."""
    a = math.radians(direction + 180)
    v = np.array([math.cos(a), math.sin(a)])
    nv = np.array([-v[1], v[0]])
    for k in range(n):
        off = (k - (n - 1) / 2) * spread / max(1, n - 1) * 2
        p0 = np.array(c) + nv * off + v * (20 + 10 * (k % 2))
        m.stroke([p0, p0 + v * length * (0.7 + 0.3 * ((k * 7) % 3) / 2)], t0 + k * dur / n * 0.5, dur * 0.6, color, width, 0.1)


def sound(m, c, t0, n=3, r0=30, step=26, arc=70, direction=-90, dur=0.5, color="auto", width=4):
    """Sound or alarm rings: short arcs spreading from a point."""
    for k in range(n):
        r = r0 + k * step
        th = np.radians(np.linspace(direction - arc / 2, direction + arc / 2, 14))
        m.stroke(np.stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)], 1), t0 + k * dur / n, dur / n, color, width, 0.2)


def route(m, pts, t0, t1, color="red", width=5, dash=True, head=True):
    """A dotted path (the way he went), drawn dash by dash, with an arrowhead."""
    p = np.array(pts, float)
    seg = np.hypot(*np.diff(p, axis=0).T)
    s = np.r_[0, np.cumsum(seg)]
    L = s[-1]
    step = 26 if dash else L
    marks = np.arange(0, L - 1, step)
    for i, a in enumerate(marks):
        b_ = min(L, a + step * 0.55) if dash else L
        q = [(np.interp(x, s, p[:, 0]), np.interp(x, s, p[:, 1])) for x in np.linspace(a, b_, 4)]
        m.stroke(q, t0 + (t1 - t0) * a / L, max(0.04, (t1 - t0) * (b_ - a) / L), color, width, 0.0)
    if head:
        d = p[-1] - p[-2]
        d = d / (np.hypot(*d) + 1e-9)
        nv = np.array([-d[1], d[0]])
        m.stroke([p[-1] - d * 26 + nv * 14, p[-1], p[-1] - d * 26 - nv * 14], t1, 0.2, color, width, 0.1)


def leader(m, dot, text_xy, text, t0, size=40, color="auto"):
    """Name a detail without covering it: a dot on the thing, a thin line out to a typed label."""
    m.stroke([(dot[0] - 4, dot[1]), (dot[0] + 4, dot[1] + 1)], t0, 0.08, color, 9)
    tx, ty = text_xy
    end = (tx - 10, ty) if tx > dot[0] else (tx + size * 0.55 * len(text) + 10, ty)
    m.stroke([dot, end], t0 + 0.08, 0.25, color, 3, 0.2)
    m.typed(text, (tx, ty - size * 0.1), size, t0 + 0.3, color=color)


def tally(m, x, y, n, t0, t1, h=70, gap=22, color="red", width=5):
    """Counting strokes in fives (four up, one across), spread over t0..t1."""
    dt = (t1 - t0) / max(1, n)
    for i in range(n):
        g, k = divmod(i, 5)
        X = x + g * (gap * 5 + 30)
        if k < 4:
            m.stroke([(X + k * gap, y), (X + k * gap + 3, y + h)], t0 + i * dt, dt * 0.8, color, width, 0.1)
        else:
            m.stroke([(X - 12, y + h * 0.75), (X + 3 * gap + 12, y + h * 0.2)], t0 + i * dt, dt * 0.8, color, width, 0.1)


# ---------------------------------------------------------------- finding the egg faces in a painting


def find_faces(img, min_area=900):
    """The egg heads in an image (source px): warm cream skin blobs whose holes are two dark eye ovals and, below
    them, the mouth line. Returns [dict(eyes=[(x, y, rx, ry), (..)], mouth=(x, y, w, h) or None, head=(x0, y0, x1, y1))]
    biggest head first. Faces behind tinted glasses or seen from behind are simply not found (they don't act)."""
    a = cv2.resize(up(img), (SW, SH), interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(a, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin = ((h >= 6) & (h <= 21) & (s >= 55) & (s <= 160) & (v >= 140)).astype(np.uint8)
    skin = cv2.morphologyEx(skin, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(skin)
    out = []
    for i in range(1, n):
        x, y, w, hh, A = st[i]
        if A < min_area or not 0.45 < w / max(1, hh) < 2.0:
            continue
        blob = (lab == i).astype(np.uint8)
        cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        filled = np.zeros_like(blob)
        cv2.drawContours(filled, cnts, -1, 1, -1)
        hull = cv2.convexHull(max(cnts, key=cv2.contourArea))
        if filled.sum() / max(1.0, cv2.contourArea(hull)) < 0.72:  # an egg is convex; lamps and dishes aren't
            continue
        holes = ((filled == 1) & (blob == 0) & (v < 110)).astype(np.uint8)
        k, hl, hs, hc = cv2.connectedComponentsWithStats(holes)
        cand = [(hs[j], hc[j]) for j in range(1, k) if hs[j][4] >= max(8, A * 0.0015) and hs[j][4] <= A * 0.06
                and v[hl == j].mean() < 75]
        eyes = None
        best = 1e9
        for p in range(len(cand)):
            for q in range(p + 1, len(cand)):
                (sa, ca), (sb, cb) = cand[p], cand[q]
                if abs(ca[1] - cb[1]) > max(sa[3], sb[3]) * 1.25:  # heads tilt
                    continue
                if not 0.6 < sa[4] / sb[4] < 1.6:
                    continue
                gap = abs(ca[0] - cb[0])
                if not 1.5 * max(sa[2], sb[2]) < gap < w * 0.7:
                    continue
                if sa[2] > sa[3] * 1.1 or sb[2] > sb[3] * 1.1:  # eyes are upright ovals, not lines
                    continue
                if min(sa[4] / (sa[2] * sa[3]), sb[4] / (sb[2] * sb[3])) < 0.55:  # solid ovals
                    continue
                if max(ca[1], cb[1]) > y + hh * 0.7:  # eyes sit in the upper part of the head
                    continue
                # a real pair (one-eyed heads were a real problem): same size and shape, side by side, spaced like
                # eyes for this head, both well inside it
                if not 0.75 < sa[4] / sb[4] < 1.33 or not 0.7 < (sa[3] / max(1, sa[2])) / (sb[3] / max(1, sb[2])) < 1.43:
                    continue
                if not 0.16 * w < gap < 0.55 * w:
                    continue
                if min(ca[0], cb[0]) < x + w * 0.1 or max(ca[0], cb[0]) > x + w * 0.9:
                    continue
                if abs(ca[1] - cb[1]) > 0.5 * max(sa[3], sb[3]):
                    continue
                score = abs(ca[1] - cb[1]) + abs(sa[4] - sb[4]) * 0.1 - (sa[4] + sb[4]) * 0.01
                if score < best:
                    best, eyes = score, ((sa, ca), (sb, cb))
        if eyes is None:
            continue
        ey = (eyes[0][1][1] + eyes[1][1][1]) / 2
        ex = (eyes[0][1][0] + eyes[1][1][0]) / 2
        eh = max(eyes[0][0][3], eyes[1][0][3])
        mouth = None
        for sm, cm in cand:
            if any(sm is e[0] for e in eyes):
                continue
            if cm[1] > ey + eh * 0.8 and abs(cm[0] - ex) < abs(eyes[0][1][0] - eyes[1][1][0]) * 0.8 \
                    and sm[2] < abs(eyes[0][1][0] - eyes[1][1][0]) * 1.1:
                if sm[3] > abs(eyes[0][1][0] - eyes[1][1][0]) * 0.75:  # too tall to be a mouth (hair, beard)
                    continue
                if mouth is None or cm[1] > mouth[1][1]:  # the lowest one: a moustache sits above the mouth
                    mouth = (sm, cm)
        E = [(float(c[0]), float(c[1]), s_[2] / 2 + 1, s_[3] / 2 + 1) for s_, c in eyes]
        M = None
        if mouth is not None:
            sm, cm = mouth
            M = (float(sm[0] + sm[2] / 2), float(sm[1] + sm[3] / 2), float(sm[2] + 2), float(sm[3] + 2))
        out.append(dict(eyes=sorted(E), mouth=M, head=(x, y, x + w, y + hh), area=A))
    return sorted(out, key=lambda f: -f["area"])


def acting(img, seed=0, auto=False, only_main=True, **cues):
    """The main egg face of an image acting on the given cues only (the rule: no automatic blinking, no extra
    faces; act only where it matters and only on a face checked on the audit sheet, see face_audit()). Returns a list
    for src_fx (empty if no proper two-eyed face is found)."""
    fs = find_faces(img)
    faces = []
    for k, f in enumerate(fs[:1] if only_main else fs[:5]):
        kw = cues if k == 0 else {}
        wants_mouth = k == 0 and (cues.get("mouth_fx") or cues.get("talk") or any(c[2] for c in cues.get("expr", [])))
        faces.append(Face(img, eyes=f["eyes"], mouth=f["mouth"] if wants_mouth else None, seed=seed + k * 7, auto=auto, **kw))
    if not faces:
        return []

    def all_faces(a, t):  # one copy of the picture, every face redrawn into it
        out = a.copy()
        for f in faces:
            out = f.apply(out, t, copy=False)
        return out
    return [all_faces]


class NoteCard:
    """A footnote that doesn't stop the film: the narrator's gloved hand slides the folded note up (t_in), it opens
    into the tea-stained card (B10) at the side of the frame, the red number and the source type themselves, and
    the card slides away at t_out. Screen space (post=[...]); pair with wr.footnote for the sound."""

    def __init__(self, t_in, t_out, n, title, lines, side="right", width=0.36, pos=None):
        from PIL import Image
        a = cv2.cvtColor(cv2.imread(str(host_file(film.INC / "04_bases" / "B10_note.png", "note.png"))), cv2.COLOR_BGR2RGB)
        H0, W0 = a.shape[:2]
        crop = a[int(H0 * 0.066):int(H0 * 0.94), int(W0 * 0.081):int(W0 * 0.92)]
        al = np.ones(crop.shape[:2], np.float32)
        g = cv2.cvtColor(crop, cv2.COLOR_RGB2GRAY).astype(np.float32)
        bg = np.median(np.concatenate([g[:3].ravel(), g[-3:].ravel(), g[:, :3].ravel(), g[:, -3:].ravel()]))
        al = np.clip(np.abs(g - bg) / 18 + (cv2.GaussianBlur((np.abs(g - bg) > 6).astype(np.float32), (0, 0), 3) > 0.5), 0, 1)
        al = cv2.morphologyEx(al, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
        cnts, _ = cv2.findContours((al > 0.5).astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        m = np.zeros_like(al)
        cv2.drawContours(m, [max(cnts, key=cv2.contourArea)], -1, 1, -1)
        self.card, self.al = crop.astype(np.float32), cv2.GaussianBlur(m, (0, 0), 1.2)
        self.hand = Hand(host_file(film.INC / "01_cast" / "hand.png", "hand.png"), t_in, t_in + 0.9, x=0.78 if side == "right" else 0.22,
                         height=0.55)
        self.t_in, self.t_out, self.n, self.title, self.lines, self.side, self.width = t_in, t_out, n, title, lines, side, width
        self.pos = pos or ((0.78 if side == "right" else 0.22), 0.36)  # card centre as fractions of the frame
        self._cache = {}

    def _text_layer(self, w, h, k_chars):
        from PIL import Image, ImageDraw, ImageFont
        key = (w, k_chars)
        if key in self._cache:
            return self._cache[key]
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        fn = ImageFont.truetype(ytf.font("hand"), int(h * 0.16))
        ft = ImageFont.truetype(TYPE, int(h * 0.085))
        fb = ImageFont.truetype(TYPE, int(h * 0.062))
        d.text((w * 0.08, h * 0.06), str(self.n), font=fn, fill=(178, 38, 30, 255))
        left = k_chars
        y = h * 0.11
        t = self.title[:max(0, left)]
        d.text((w * 0.2, y), t, font=ft, fill=(40, 30, 24, 255))
        left -= len(self.title)
        y = h * 0.33
        for ln in self.lines:
            if left <= 0:
                break
            d.text((w * 0.09, y), ln[:left], font=fb, fill=(48, 38, 30, 255))
            left -= len(ln)
            y += h * 0.105
        arr = np.asarray(im, np.float32)
        self._cache = {key: arr}
        return arr

    def total(self):
        return len(self.title) + sum(len(l) for l in self.lines)

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t_in or t > self.t_out + 0.6:
            return img
        img = self.hand(img, t, s, cam) if t < self.t_in + 1.5 else img
        H, W = img.shape[:2]
        u_open = (t - self.t_in - 0.45) / 0.35
        if u_open <= 0:
            return img
        k = ease(min(1.0, u_open), "out") * (1 - ease((t - self.t_out) / 0.45, "in"))
        w = int(W * self.width)
        h = int(w * self.card.shape[0] / self.card.shape[1])
        card = cv2.resize(self.card, (w, h), interpolation=cv2.INTER_AREA)
        al = cv2.resize(self.al, (w, h))
        chars = int(max(0, (t - self.t_in - 0.75) / 0.045))
        tx = self._text_layer(w, h, min(self.total(), chars))
        ta = tx[..., 3:4] / 255
        card = card * (1 - ta) + tx[..., :3] * ta
        cx = W * self.pos[0]
        cy = H * self.pos[1] + (1 - k) * H * 0.8
        sc = 0.35 + 0.65 * k
        ang = -3 + 6 * (1 - k)
        return _paste(_paste(img, (0, 0, 0), cv2.GaussianBlur(al, (0, 0), 10) * 0.4 * k, (cx + 12, cy + 16), sc, ang),
                      card, al * min(1.0, k * 1.5), (cx, cy), sc, ang)


class Sprite:
    """A flat cartoon cut out of its plain background (the narrator's poses) standing in the frame: it pops up from
    below at t0 with a small overshoot, breathes, and drops away at t1. pos = centre (fractions of the frame),
    height = share of the frame height. Screen space (post=[...])."""

    def __init__(self, path, t0, t1, pos=(0.3, 0.55), height=0.78):
        self.rgb, self.al = cutout(path)
        self.t0, self.t1, self.pos, self.height = t0, t1, pos, height

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t0 or t > self.t1 + 0.35:
            return img
        H, W = img.shape[:2]
        u = t - self.t0
        k = (1.06 - 0.06 * ease((u - 0.25) / 0.15)) if u > 0.25 else ease(u / 0.25, "out") * 1.06
        k *= 1 - ease((t - self.t1) / 0.3, "in") if t > self.t1 else 1
        sc = self.height * H / self.rgb.shape[0] * (1 + 0.008 * math.sin(t * 2.4))
        c = (self.pos[0] * W, self.pos[1] * H + (1 - min(1.0, k)) * H * 0.6)
        sh = cv2.GaussianBlur(self.al, (0, 0), 8)
        img = _paste(img, (0, 0, 0), sh * 0.25 * min(1.0, k), (c[0] + 14, c[1] + 18), sc, 0)
        return _paste(img, self.rgb, self.al * min(1.0, k), c, sc, 0)


# ---------------------------------------------------------------- reaction marks (beside a head, in ink)


def react(m, head, kind, t0, color="auto"):
    """A small cartoon reaction drawn live beside an egg head (head = (x0, y0, x1, y1) source px, from find_faces):
    "sweat" a drop, "shake" lines either side, "!" or "?", "worry" three wavy lines above, "glee" little bursts,
    "zzz" sleep. Use few: one at a real story beat, not on every face."""
    x0, y0, x1, y1 = head
    w, h = x1 - x0, y1 - y0
    cx = (x0 + x1) / 2
    if kind == "sweat":
        c = np.array([x1 + w * 0.02, y0 + h * 0.3])
        s_ = w * 0.09
        th = np.linspace(0, 2 * math.pi, 30)
        drop = np.stack([c[0] + s_ * np.sin(th) * (1 - np.cos(th)) * 0.5, c[1] - s_ * 1.4 * np.cos(th) * 0.5 + s_ * 0.6], 1)
        m.stroke(drop, t0, 0.35, color=color, width=3)
    elif kind == "shake":
        for side in (-1, 1):
            bx = x0 - w * 0.08 if side < 0 else x1 + w * 0.08
            for k in range(2):
                th = np.radians(np.linspace(-35, 35, 10))
                r = h * (0.18 + 0.08 * k)
                pts = np.stack([bx + side * (r * np.cos(th) - r * 0.85), y0 + h * 0.45 + r * np.sin(th)], 1)
                m.stroke(pts, t0 + k * 0.08, 0.18, color=color, width=3)
    elif kind in ("!", "?"):
        m.text(kind, (x1 + w * 0.05, y0 + h * 0.02), max(40, h * 0.32), t0, 0.15, color="red")
    elif kind == "worry":
        for k in (-1, 0, 1):
            xs = np.linspace(-w * 0.05, w * 0.05, 8)
            m.stroke([(cx + k * w * 0.16 + x, y0 - h * 0.08 + 4 * math.sin(i * 1.6)) for i, x in enumerate(xs)],
                     t0 + (k + 1) * 0.08, 0.15, color=color, width=3)
    elif kind == "glee":
        c = (x1 + w * 0.02, y0 + h * 0.1)
        for k in range(3):
            a = math.radians(-70 + k * 35)
            p0 = (c[0] + math.cos(a) * w * 0.06, c[1] + math.sin(a) * w * 0.06)
            p1 = (c[0] + math.cos(a) * w * 0.16, c[1] + math.sin(a) * w * 0.16)
            m.stroke([p0, p1], t0 + k * 0.06, 0.12, color=color, width=3)
    elif kind == "zzz":
        for k, sz in enumerate((0.16, 0.2, 0.25)):
            m.text("z", (x1 + w * (0.02 + 0.12 * k), y0 + h * (0.25 - 0.12 * k)), max(30, h * sz), t0 + k * 0.4, 0.2, color=color)


def face_audit(names, out):
    """A sheet of the given images with the face finder's result drawn on: green eye ovals and mouth box on every face
    it accepts. Look at it before giving any shot act= cues: act only where both real eyes are ringed."""
    tiles = []
    for n in names:
        a = up(n).copy()
        a = cv2.resize(a, (SW, SH), interpolation=cv2.INTER_AREA) if a.shape[1] != SW else a
        for f in find_faces(n):
            for (ex, ey, rx, ry) in f["eyes"]:
                cv2.ellipse(a, (int(ex), int(ey)), (int(rx + 3), int(ry + 3)), 0, 0, 360, (0, 255, 0), 2)
            x0, y0, x1, y1 = f["head"]
            cv2.rectangle(a, (x0, y0), (x1, y1), (255, 200, 0), 2)
            if f["mouth"]:
                mx, my, mw, mh = f["mouth"]
                cv2.rectangle(a, (int(mx - mw / 2), int(my - mh / 2)), (int(mx + mw / 2), int(my + mh / 2)), (255, 0, 255), 2)
        a = cv2.resize(a, (600, int(600 * a.shape[0] / a.shape[1])))
        cv2.putText(a, n, (8, 26), 0, 0.7, (255, 255, 0), 2)
        tiles.append(a)
    while len(tiles) % 3:
        tiles.append(np.zeros_like(tiles[0]))
    sheet = np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)])
    cv2.imwrite(str(out), cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))


PHOTOS = film.INC / "05_photos"


class Photo:
    """A real archive photo shown as a period print: cream paper border, a soft shadow, a
    small tilt; it slides in at t_in from the side it sits on (settling with a little overshoot), drifts slowly
    closer while it's up, and slides away at t_out. `credit` types itself small under the print (CC BY / BY-SA
    photos must carry it). `dim` darkens the shot behind it so the print reads. Screen space (post=[...] or
    b.overlay). pos = print centre as fractions of the frame, height = print height as a share of the frame."""

    def __init__(self, name, t_in, t_out, pos=(0.7, 0.48), height=0.62, tilt=-3.0, credit=None, dim=0.25, sepia=None):
        p = PHOTOS / name
        a = cv2.cvtColor(cv2.imread(str(p)), cv2.COLOR_BGR2RGB).astype(np.float32)
        gray = float(np.abs(a[..., 0] - a[..., 2]).mean()) < 6
        if sepia if sepia is not None else gray:  # black-and-white prints get the warm tone of old photo paper
            g = a.mean(2, keepdims=True) / 255
            g = np.clip((g - np.percentile(g, 1)) / max(1e-3, np.percentile(g, 99) - np.percentile(g, 1)), 0, 1)
            a = (g * np.array([236, 222, 196]) + (1 - g) * np.array([38, 30, 24])).astype(np.float32)
        h, w = a.shape[:2]
        s = 900 / max(h, w)
        a = cv2.resize(a, (int(w * s), int(h * s)), interpolation=cv2.INTER_AREA)
        h, w = a.shape[:2]
        bw, bb = int(max(h, w) * 0.045), int(max(h, w) * (0.11 if credit else 0.045))
        paper = np.zeros((h + bw + bb, w + 2 * bw, 3), np.float32) + np.array([238, 230, 212], np.float32)
        paper += np.random.default_rng(3).normal(0, 3, paper.shape[:2])[..., None]
        paper[bw:bw + h, bw:bw + w] = a
        self.print = np.clip(paper, 0, 255)
        self.al = np.ones(paper.shape[:2], np.float32)
        self.box_bottom = (bw + h, bb)
        self.t_in, self.t_out, self.pos, self.height, self.tilt, self.credit, self.dim = t_in, t_out, pos, height, tilt, credit, dim
        self._credit_cache = None

    def _credit_layer(self):
        from PIL import Image, ImageDraw, ImageFont
        if self._credit_cache is None:
            ph, pw = self.print.shape[:2]
            im = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
            d = ImageDraw.Draw(im)
            f = ImageFont.truetype(TYPE, max(14, int(self.box_bottom[1] * 0.32)))
            d.text((int(pw * 0.05), self.box_bottom[0] + int(self.box_bottom[1] * 0.3)), self.credit, font=f,
                   fill=(70, 58, 46, 255))
            self._credit_cache = np.asarray(im, np.float32)
        return self._credit_cache

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t_in or t > self.t_out + 0.5:
            return img
        H, W = img.shape[:2]
        u = (t - self.t_in) / 0.55
        k_in = 1.04 - 0.04 * ease((u - 1) / 0.5) if u > 1 else ease(u, "out") * 1.04
        k_out = ease((t - self.t_out) / 0.45, "in") if t > self.t_out else 0.0
        k = min(1.0, k_in) * (1 - k_out)
        if self.dim:
            img = img * (1 - self.dim * k)
        pr = self.print
        if self.credit:
            chars = int(max(0, (t - self.t_in - 0.7) / 0.04))
            cl = self._credit_layer().copy()
            # reveal the credit left to right, a character's width at a time
            cut = int(cl.shape[1] * min(1.0, chars / max(1, len(self.credit))))
            cl[:, cut:] = 0
            ca = cl[..., 3:4] / 255
            pr = pr * (1 - ca) + cl[..., :3] * ca
        sc = self.height * H / pr.shape[0] * (1 + 0.025 * max(0.0, t - self.t_in) / max(1.0, self.t_out - self.t_in))
        side = 1 if self.pos[0] >= 0.5 else -1
        cx = W * self.pos[0] + side * (1 - min(1.0, k_in)) * W * 0.55 + side * k_out * W * 0.6
        cy = H * self.pos[1]
        ang = self.tilt + side * 6 * (1 - min(1.0, k_in))
        sh = cv2.GaussianBlur(self.al, (0, 0), 14)
        img = _paste(img, (0, 0, 0), sh * 0.45 * min(1.0, k * 1.4), (cx + 16, cy + 20), sc, ang)
        return _paste(img, pr, self.al * min(1.0, k * 1.6), (cx, cy), sc, ang)


class Papers:
    """Loose sheets of paper tumbling down through the frame (the crash, a trading floor, ticker tape): each sheet
    flutters (its width breathes as it turns), sways on the air and drifts down; near ones bigger, softer and faster.
    t0/t1 = when sheets are released; area = (x0, x1) fractions of the frame width they fall across. Screen space."""

    def __init__(self, t0, t1, n=26, area=(0.0, 1.0), seed=5, color=(236, 228, 210), tape=False, scale=1.0):
        r = np.random.default_rng(seed)
        self.t0, self.t1 = t0, t1
        self.sh = [dict(t=r.uniform(t0 - 2.5, t1), x=r.uniform(*area), z=r.uniform(0.4, 1.0), ph=r.uniform(0, 6.3),
                        spin=r.uniform(1.2, 3.0) * r.choice([-1, 1]), sway=r.uniform(0.02, 0.06), ang=r.uniform(0, 360))
                   for _ in range(n)]
        self.color, self.tape, self.scale = np.array(color, np.float32), tape, scale

    def __call__(self, img, t, s=None, cam=None):
        if t < self.t0 - 0.1 or t > self.t1 + 6:
            return img
        H, W = img.shape[:2]
        out = img
        for p in sorted(self.sh, key=lambda q: q["z"]):
            u = t - p["t"]
            if u < 0:
                continue
            y = -0.1 + u * (0.10 + 0.12 * p["z"])
            if y > 1.1:
                continue
            x = p["x"] + p["sway"] * math.sin(u * 1.7 + p["ph"])
            size = (0.035 + 0.05 * p["z"]) * W * self.scale
            w = size * (1.0 if not self.tape else 0.22)
            h = size * (1.3 if not self.tape else 2.4)
            flip = abs(math.cos(u * p["spin"] + p["ph"])) * 0.8 + 0.2
            box = cv2.boxPoints(((x * W, y * H), (w * flip, h), p["ang"] + u * p["spin"] * 40)).astype(np.int32)
            m = np.zeros((H, W), np.float32)
            cv2.fillConvexPoly(m, box, 1.0, lineType=cv2.LINE_AA)
            if p["z"] > 0.8:
                m = cv2.GaussianBlur(m, (0, 0), 1.2)
            shade = 0.82 + 0.18 * flip
            col = self.color * shade
            out = out * (1 - m[..., None]) + col * m[..., None]
            cv2.polylines(out, [box], True, (90, 80, 70), 1, cv2.LINE_AA)
            if not self.tape:  # a few lines of print on each sheet
                c = box.mean(0)
                for k in range(3):
                    a_ = box[0] + (box[1] - box[0]) * 0.2 + (box[3] - box[0]) * (0.25 + 0.2 * k)
                    b_ = box[0] + (box[1] - box[0]) * 0.8 + (box[3] - box[0]) * (0.25 + 0.2 * k)
                    cv2.line(out, tuple(np.int32(a_)), tuple(np.int32(b_)), (150, 140, 128), 1, cv2.LINE_AA)
        return out
