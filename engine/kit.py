"""Shot helpers for a film's batches: camera moves by name, labels, sketch sheets that follow their drawings, the
blank bases' drawings (globe, military map, blackboard figures, bamboo carvings, newspaper photos).

Camera keys are (t, cx, cy, h) in source px (the image is 1774 x 887; h = visible height)."""
import math
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

import film
from film import Marks, Page, UP, SW, SH

WEB = Path(film.ROOT) / "web"  # this project's public-domain photos (credit them in web/CREDITS.md)

MOVES = {  # name -> (start (cx, cy, h), end (cx, cy, h))
    "in": ((887, 443, 887), (887, 443, 720)),
    "out": ((887, 443, 720), (887, 443, 887)),
    "right": ((760, 443, 780), (1014, 443, 780)),
    "left": ((1014, 443, 780), (760, 443, 780)),
    "up": ((887, 520, 760), (887, 366, 760)),
    "down": ((887, 366, 760), (887, 520, 760)),
    "face": ((887, 430, 860), (887, 410, 740)),  # a close-up: a slow push
    "still": ((887, 443, 860), (887, 443, 830)),
}


def cam(move, t0, t1):
    """Camera keys for a named move, or a custom one: ((cx, cy, h), (cx, cy, h))."""
    a, b = MOVES[move] if isinstance(move, str) else move
    return [(t0, *a), (t1, *b)]


def cut(b, t0, t1, img, move="in", text=None, **kw):
    """One image with a named camera move; text=(words, t[, corner]) writes a label kept inside the view."""
    keys = cam(move, t0, t1)
    if text:
        kw["marks"] = label(text[0], text[1], keys=keys, corner=text[2] if len(text) > 2 else "tl", marks=kw.get("marks"))
    b.scene(t0, img, keys, **kw)


def view_box(keys):
    """The part of the image the camera keeps in view through every key: (x0, y0, x1, y1)."""
    boxes = []
    for k in keys:
        cx, cy, h = k[1:4] if len(k) >= 4 else k
        h = min(SH, h)
        w = h * 16 / 9
        cx, cy = min(max(cx, w / 2), SW - w / 2), min(max(cy, h / 2), SH - h / 2)
        boxes.append((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2))
    return (max(b_[0] for b_ in boxes), max(b_[1] for b_ in boxes), min(b_[2] for b_ in boxes), min(b_[3] for b_ in boxes))


def label(text, t, xy=(90, 70), size=54, marks=None, color="auto", dur=None, keys=None, corner="tl"):
    """A typewriter label (date, place, name) on a shot, level. With `keys` (the shot's camera keys, or a move's (start, end)), the label is placed in
    `corner` ('tl', 'tr', 'bl', 'br') of the area that stays in view all shot, so a push-in never crops it."""
    m = marks or Marks()
    if keys is not None:
        x0, y0, x1, y1 = view_box(keys)
        wt = 0.62 * size * len(text)  # rough width of the typed label
        pad_x, pad_y = 0.04 * (x1 - x0), 0.05 * (y1 - y0)
        x = x0 + pad_x if corner[1] == "l" else x1 - pad_x - wt
        y = y0 + pad_y if corner[0] == "t" else y1 - pad_y - size * 1.3
        xy = (x, y)
    m.typed(text, xy, size, t, dur, color=color)
    return m


def sheet(b, name, t0, t1, cues, marks=None, ink=1.4, colour=0.9, done=(), **kw):
    """A sketch sheet drawing itself, one drawing per cue: cues = [(panel, t), ...]. The camera visits each drawing as
    it is drawn, then pulls back to the whole page. done: panels already drawn (a sheet we return to)."""
    keys, wins = [], [(p, t0 - 3, t0 - 2.5, t0 - 2) for p in done]
    for i, (p, tc) in enumerate(cues):
        x0, y0, x1, y1 = film.panels(name)[p]
        c = ((x0 + x1) / 2, (y0 + y1) / 2)
        keys.append((tc, c[0], c[1], 820))  # wide enough that labels under the drawing stay in frame
        nxt = cues[i + 1][1] if i + 1 < len(cues) else t1
        d = max(0.6, min(ink, (nxt - tc) * 0.65))
        wins.append((p, tc, tc + d, tc + d + min(colour, max(0.3, nxt - tc - d))))
    keys = [(t0, *keys[0][1:])] + keys
    if t1 - cues[-1][1] > 2.2:
        keys.append((cues[-1][1] + 1.6, 887, 450, 860))
    keys.append((t1, *keys[-1][1:]))
    b.sheet(t0, name, keys, windows=wins, marks=marks, **kw)


# ---------------------------------------------------------------- drawings for the bases

def arc(a, c, bend=0.25, n=40):
    a, c = np.asarray(a, float), np.asarray(c, float)
    m = (a + c) / 2
    d = c - a
    nrm = np.array([-d[1], d[0]])
    ctrl = m + nrm * bend
    u = np.linspace(0, 1, n)[:, None]
    return (1 - u) ** 2 * a + 2 * (1 - u) * u * ctrl + u ** 2 * c


def dashes(path, on=3, off=3):
    return [path[i:i + on + 1] for i in range(0, len(path) - on, on + off)]


def arrowhead(path, size=18):
    tip, back = np.asarray(path[-1]), np.asarray(path[-4])
    d = (tip - back) / (np.hypot(*(tip - back)) + 1e-9)
    n = np.array([-d[1], d[0]])
    return [np.array([tip - d * size + n * size * 0.55, tip, tip - d * size - n * size * 0.55])]


def ring(c, r, n=36):
    th = np.linspace(0, 2 * math.pi, n)
    return np.stack([c[0] + r * np.cos(th), c[1] + r * np.sin(th)], 1)


def egg_figure(c, s=1.0, lying=False, rifle=False):
    """A small chalk-board egg-headed soldier (the film's own figure, as a teacher would draw it)."""
    x, y = c
    if lying:
        th = np.linspace(0, 2 * math.pi, 24)
        head = np.stack([x - 52 * s + 14 * s * np.cos(th), y - 6 * s + 12 * s * np.sin(th)], 1)
        return [head, np.array([[x - 38 * s, y - 4 * s], [x + 30 * s, y]]),
                np.array([[x + 30 * s, y], [x + 56 * s, y - 6 * s]]), np.array([[x + 30 * s, y], [x + 54 * s, y + 8 * s]]),
                np.array([[x - 20 * s, y - 2 * s], [x - 6 * s, y + 18 * s]])]
    th = np.linspace(0, 2 * math.pi, 24)
    head = np.stack([x + 15 * s * np.cos(th), y - 60 * s + 18 * s * np.sin(th) + 2 * s * np.sin(th) ** 2], 1)
    cap = np.array([[x - 17 * s, y - 64 * s], [x - 12 * s, y - 80 * s], [x + 12 * s, y - 80 * s], [x + 19 * s, y - 64 * s]])
    out = [head, cap, np.array([[x, y - 42 * s], [x, y]]), np.array([[x, y], [x - 14 * s, y + 40 * s]]),
           np.array([[x, y], [x + 14 * s, y + 40 * s]]), np.array([[x - 18 * s, y - 20 * s], [x, y - 34 * s], [x + 18 * s, y - 20 * s]])]
    if rifle:
        out.append(np.array([[x + 14 * s, y - 52 * s], [x + 30 * s, y + 6 * s]]))
    return out


def cross(c, r):
    x, y = c
    return [np.array([[x - r, y - r], [x + r, y + r]]), np.array([[x + r, y - r], [x - r, y + r]])]


def halftone(page, photo, box, t0, t1, dot=5.0):
    """A photo printing itself into a newspaper box as halftone dots, top to bottom like a press run."""
    x0, y0, x1, y1 = box
    a = np.asarray(Image.open(photo).convert("L"), np.float32) / 255
    h, w = a.shape
    bw, bh = x1 - x0, y1 - y0
    s_ = max(bw / w, bh / h)
    a = cv2.resize(a, (int(w * s_), int(h * s_)), interpolation=cv2.INTER_AREA)
    oy, ox = (a.shape[0] - bh) // 2, (a.shape[1] - bw) // 2
    a = a[oy:oy + bh, ox:ox + bw]
    a = cv2.GaussianBlur(a, (0, 0), 1.0)
    lo, hi = np.percentile(a, 3), np.percentile(a, 97)
    a = np.clip((a - lo) / max(1e-3, hi - lo), 0, 1) ** 0.9  # full tonal range, like a press photo
    W2, H2 = bw * UP, bh * UP
    d = np.zeros((H2, W2), np.float32)
    step = dot * UP
    for yy in np.arange(step / 2, H2, step):
        for xx in np.arange(step / 2 + (step / 2 if int(yy / step) % 2 else 0), W2, step):
            v = 1 - a[min(bh - 1, int(yy / UP)), min(bw - 1, int(xx / UP))]
            r = step * 0.62 * math.sqrt(v)
            if r > 0.4:
                cv2.circle(d, (int(xx), int(yy)), int(round(r)), 1.0, -1, cv2.LINE_AA)
    T = np.repeat(np.linspace(0, 1, H2, dtype=np.float32)[:, None], W2, 1)
    page.lifts.append(dict(d=d, T=T, box=(y0 * UP, y1 * UP, x0 * UP, x1 * UP), t0=t0, t1=t1,
                           trk=np.zeros((0, 3), np.float32)))


def ink_tally(page, x0, y0, t0, t1, n, col_w=56, row_h=150, per_row=4, start=0):
    """Tally marks cut into wood: groups of four strokes and a slash, appearing faster and faster (t0..t1)."""
    paths = []
    for k in range(start, start + n):
        g, i = divmod(k, 5)
        gx, gy = x0 + (g % per_row) * col_w * 2.2, y0 + (g // per_row) * row_h
        if i < 4:
            paths.append(np.array([[gx + i * 14, gy], [gx + i * 14 + 3, gy + 90]]))
        else:
            paths.append(np.array([[gx - 8, gy + 70], [gx + 58, gy + 18]]))
    m = len(paths)
    u = np.linspace(0, 1, m + 1) ** 0.55  # accelerating: the years go faster
    for p, a, c in zip(paths, u[:-1], u[1:]):
        page.stroke(p, t0 + a * (t1 - t0), max(0.04, (c - a) * (t1 - t0) * 0.8), width=4.2, wob=0.4, ease_=0.2)


def coast_map(page, lon, lat, rect, t0, t1, width=2.4, keep=14, min_len=6):
    """Real coastlines inside lon x lat drawn on a page, fitted into rect (source px); the longest coasts first.
    Returns P(lon, lat) -> page px."""
    x0, y0, x1, y1 = rect
    K = math.cos(math.radians((lat[0] + lat[1]) / 2))
    S = min((x1 - x0) / ((lon[1] - lon[0]) * K), (y1 - y0) / (lat[1] - lat[0]))
    cx, cy, lc, ac = (x0 + x1) / 2, (y0 + y1) / 2, (lon[0] + lon[1]) / 2, (lat[0] + lat[1]) / 2

    def P(lo, la):
        return np.array([cx + (lo - lc) * K * S, cy - (la - ac) * S])

    runs = []
    for f in film._geojson("ne_10m_land.geojson"):
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            r = np.asarray(poly[0])
            if r[:, 0].max() < lon[0] or r[:, 0].min() > lon[1] or r[:, 1].max() < lat[0] or r[:, 1].min() > lat[1]:
                continue
            ok = (r[:, 0] > lon[0]) & (r[:, 0] < lon[1]) & (r[:, 1] > lat[0]) & (r[:, 1] < lat[1])
            lab, n = __import__("scipy.ndimage", fromlist=["label"]).label(ok)
            for k in range(1, n + 1):
                seg = r[lab == k]
                if len(seg) >= min_len:
                    q = np.array([P(*v) for v in seg])
                    if np.hypot(*(q.max(0) - q.min(0))) > 12:
                        runs.append(q)
    runs.sort(key=lambda q: -np.hypot(*np.diff(q, axis=0).T).sum())
    runs = [q[::max(1, len(q) // 300)] for q in runs[:keep]]
    page.strokes(runs, t0, t1, width=width, wob=0.6, gap=0.05)
    return P


def cleaned(name, polys, keep=0.12):
    """A copy of an image with the illegible printing inside polys wiped back to plain paper (inpainted, a trace of
    the old ink kept), so words can be written there cleanly. Returns the new image's name."""
    out = film.BUILD / "edit" / f"{name}_clean.png"
    if not out.exists():
        out.parent.mkdir(parents=True, exist_ok=True)
        a = cv2.imread(str(film.find_img(name)))
        m = np.zeros(a.shape[:2], np.uint8)
        cv2.fillPoly(m, [np.array(q, np.int32) for q in polys], 255)
        clean = cv2.inpaint(a, m, 9, cv2.INPAINT_TELEA)
        grain = np.random.default_rng(4).normal(0, 3.0, a.shape).astype(np.float32)
        clean = np.clip(clean.astype(np.float32) + grain, 0, 255)
        w = cv2.GaussianBlur(m.astype(np.float32) / 255, (0, 0), 6)[..., None] * (1 - keep)
        cv2.imwrite(str(out), np.clip(a * (1 - w) + clean * w, 0, 255).astype(np.uint8))
    return f"{name}_clean"


def rows(start, step, n, length, deg):
    """Baselines of n lines of writing on a tilted page: (a, b) pairs, the first starting at `start`, each next one
    `step` (dx, dy) further on, `length` long at `deg` degrees (positive = sloping down to the right)."""
    d = np.array([math.cos(math.radians(deg)), math.sin(math.radians(deg))])
    out = []
    for k in range(n):
        a = np.array(start, float) + np.array(step, float) * k
        out.append((tuple(a), tuple(a + d * length)))
    return out
