"""Shot-list toolkit for a whole film (from Carnegie's Daughter, Nov 2026, the reference film). Copy to
projects/<story>/tools/ with the engine; the film's own `<story>.py` does `from seq import *`, fills LIVE (the living
layers of each picture) and calls set_map(...) for its map. Every shot list is then ~60 lines:

    from mystory import *          # which did: from seq import *; LIVE.update({...}); set_map(...)
    b = Batch("b3"); S = Seq(b)
    S.at(0.0, scene("S03b_furniture", zoom=((887, 443, 887), (800, 470, 760))))
    S.at(4.5, scene("S03c_alice_face", "face", act=dict(widen=[(4.7, 7.2, 0.25)])))
    S.at(12.8, page("B02_card", [Draw("X03_names", 0, (1260, 470), 380, (12.9, 14.0), (14.0, 14.5))], marks=m))
    S.at(77.0, map_shot((77.0, 77.6), towns=[("Woodstock", 77.1), ("Cleveland", 77.6)], route=["Woodstock", "Cleveland"],
                        t_route=(77.5, 78.6), fast=True))
    S.end(); b.render()

Effects ADD a layer (fx2); never sg.Flow. Worked example: examples/chadwick/tools/chad.py + shots_b1..b9.py.
"""
import math

import numpy as np

import film
import kit
import signature as sg
import wr
from film import Batch, Marks
from fx2 import Live, Smoke, Breath, Flame, Light, Lift, Draw, Tear, Counter, Leaves, Sparkle, lamps, u8, clean_text
import fx3
from fx3 import Focus, Haze, Snow, Rain, FaceLight, Scrap, Tag, tag

COAL, COAL_LIT = (104, 100, 104), (176, 170, 172)
STEAM, STEAM_LIT = (196, 196, 200), (236, 236, 238)


def coal(p, seed=1, k=1.0, wind=(14, -2)):
    return Smoke(p, rate=3, life=5, rise=28 * k, wind=wind, size=(10 * k, 62 * k), color=COAL, light=COAL_LIT, alpha=0.6, seed=seed)


def steam(p, seed=1, k=1.0, wind=(-20, -4)):
    return Smoke(p, rate=5, life=3.2, rise=40 * k, wind=wind, size=(14 * k, 90 * k), color=STEAM, light=STEAM_LIT, alpha=0.55, seed=seed)


def wisp(p, seed=1):
    """A thin curl of smoke or steam (a candle, a teacup, a cigar)."""
    return Smoke(p, rate=4, life=3.0, rise=22, wind=(3, 0), size=(3, 18), color=(200, 198, 196), light=(240, 238, 236),
                 alpha=0.35, spread=1.0, curl=6, seed=seed)


# ---------------------------------------------------------------- living layers per picture (source px)
# Each entry: function(t0, t1) -> (src effects, screen fx tuples, post effects). Built from the gridded sheets.
def _L(img, n=4, amount=0.13):
    return lamps(img, amount=amount, n=n)


LIVE = {}  # "S01a_street": lambda t0, t1: ([src effects], [("snow", 0.4)], [post effects]) -- see examples/chadwick/tools/chad.py


def living(img, t0, t1):
    f = LIVE.get(img)
    return f(t0, t1) if f else ([], [], [])


# ---------------------------------------------------------------- the sequencer


class Seq:
    """Shots placed on narration cues: S.at("phrase", builder) or S.at(time, builder); each builder runs with
    (t0, t1) = its cue to the next one's. S.end() places them all (the last runs to the batch end)."""

    def __init__(self, b):
        self.b, self.items = b, []

    def at(self, cue, fn, d=0.0):
        t = (self.b.t(cue) if isinstance(cue, str) else cue) + d
        self.items.append((t, fn))
        return t

    def end(self, t_end=None):
        T = t_end if t_end is not None else self.b.end
        its = sorted(self.items, key=lambda v: v[0])
        for (t0, fn), nxt in zip(its, its[1:] + [(T, None)]):
            fn(self.b, t0, nxt[0])


def keys(move, t0, t1, zoom=None):
    return kit.cam(move, t0, t1) if zoom is None else [(t0, *zoom[0]), (t1, *zoom[1])]


def _cam(cam, move, t0, t1, zoom):
    """Camera keys: cam = a list of (t, cx, cy, h[, ease]) or a function (t0, t1) -> that list; else move / zoom."""
    if cam is not None:
        return cam(t0, t1) if callable(cam) else list(cam)
    return keys(move, t0, t1, zoom)


def _label(b, text, t0, t1, corner, at):
    """A place/date/name as a typed paper tag in a fixed corner of the screen (never cropped by the camera)."""
    return tag(b, text, t0 + at, t1 - 0.3, corner=corner)


def scene(img, move="in", zoom=None, act=None, label=None, corner="bl", draws=(), marks=None, post=(), fx=(), extra=(),
          trans=None, live=True, label_at=0.4, shake=None, swap=None, cam=None, focus=None, light=None, haze=None,
          snow_z=None, typed_label=False):
    """One picture with its living layers. draws = [Scrap(...), Draw(...)] (made live: pen sprite and sound; they stay
    sharp), extra = more fx2 / fx3 effects, act = face cues (only on audited faces), label = a typed paper tag in
    `corner` ("bl" "tl" "br" "tr"); typed_label=True writes it on the picture the old way instead.
    cam = [(t, cx, cy, h[, ease]), ...] or a function (t0, t1) -> keys: several keys, an ease per segment.
    With a depth map (tools/depth.py): focus = a point (x, y) or a depth, or keys [(t, point | depth, amount)] to pull
    the focus; snow and rain from LIVE fall in depth (snow_z=(0, 0.12) keeps snow outside a window);
    haze = (amount, (r, g, b)) mist in the distance. light = (x, y) of the lamp or window: form shading on the faces."""
    def run(b, t0, t1):
        k = _cam(cam, move, t0, t1, zoom)
        src, sfx, spost = living(img, t0, t1) if live else ([], [], [])
        src, sfx, pst, m = list(src), list(sfx), list(spost) + list(post), marks
        deep = fx3.has_depth(img)
        if light:
            src.append(FaceLight(img, light))
        if deep:
            if haze:
                src.append(Haze(img, *haze))
            for e in [e for e in sfx if e[0] in ("snow", "rain")]:  # weather falls in depth, behind what is nearer
                sfx.remove(e)
                src.append(Snow(img, e[1], z=snow_z or (0.05, 1.0), seed=int(t0 * 7) % 97) if e[0] == "snow" else Rain(img, e[1]))
        src += list(extra)
        if focus is not None and deep:
            fk = focus if isinstance(focus, list) else [(t0, focus, 0.45)]
            src.append(Focus(img, fk))
        src += list(draws)
        if label:
            if typed_label:
                m = kit.label(label, t0 + label_at, corner=corner, keys=k, marks=m)
            else:
                pst.append(_label(b, label, t0, t1, corner, label_at))
        kw = dict(marks=m, post=pst, fx=sfx + list(fx))
        if trans:
            kw["trans"] = trans
        if shake:
            kw["shake"] = shake
        if act:
            wr.sc(b, t0, t1, img, keys=k, src=u8(*src), act=act, **kw)
        elif src:
            b.custom(t0, Live(img, src), k, img, **kw)
        else:
            b.scene(t0, img, k, **kw)
    return run


def drawin(img, move="in", zoom=None, ink=(0.0, 2.0), flood=(1.6, 3.0), marks=None, label=None, trans=("dissolve", 0.3), post=(), fx=(),
           cam=None, corner="bl", typed_label=False):
    """A scene that draws itself (its _lines version inks in, then the paint floods), times relative to the cue."""
    def run(b, t0, t1):
        k = _cam(cam, move, t0, t1, zoom)
        m, pst = marks, list(post)
        if label:
            if typed_label:
                m = kit.label(label, t0 + 0.4, keys=k, marks=m)
            else:
                pst.append(_label(b, label, t0, t1, corner, 0.4))
        src, sfx, spost = living(img, t0, t1)
        b.drawin(t0, img, k, ink=img + "_lines", flood=True, ink_t=(t0 + ink[0], t0 + ink[1]), flood_t=(t0 + flood[0], t0 + flood[1]),
                 marks=m, trans=trans, post=list(spost) + pst, fx=list(sfx) + list(fx))
    return run


def page(base, items=(), marks=None, zoom=None, post=(), fx=(), trans=("dissolve", 0.3), cam=None):
    """A blank base drawn on live: items are fx2 effects (Draw, Tear...), marks are words/arrows (Marks). Fill the
    frame: start the camera close on what is being written (cam=), then pull back; never leave the card mostly empty."""
    def run(b, t0, t1):
        k = _cam(cam, None, t0, t1, None) if cam is not None else (
            [(t0, *zoom[0]), (t1, *zoom[1])] if zoom else [(t0, 887, 443, 887), (t1, 887, 443, 850)])
        b.custom(t0, Live(base, list(items)), k, base, marks=marks, post=list(post), fx=list(fx), trans=trans)
    return run


# ---------------------------------------------------------------- the three ways to illustrate
# 1. ON THE PICTURE: marks drawn straight on a scene (arrows, circles, handwritten notes, motion lines), a scene that
#    draws itself (drawin), a drawing pinned on a scrap (scene(draws=[Scrap(...), Draw(...)])) for one small object.
# 2. THE SKETCHBOOK SHEET (sketchbook): the sketch sheet itself on screen, each drawing inking in from its line
#    version and then washed with its own colour, a level handwritten caption under it, a red circle on what matters;
#    the camera visits each drawing and pulls back to the page. For explainers and runs of moments.
# 3. THE BLANK PAGE (blank): a blank page, the sketchbook paper or a story object (notebook, board, map), drawn on
#    live in its medium: sheet drawings redrawn in stroke order (lift), maps, routes, timelines, words.
# Mix all three in every film; never let one carry a whole batch.

def sketchbook(sheet, cues, captions=None, circles=None, marks=None, ink=1.4, colour=0.9, done=(), cap_size=46,
               cap_color="red", **kw):
    """The sketch sheet itself, drawn live (references/engine.md, "three ways to illustrate").
    cues = [(panel, dt), ...] in drawing order, dt = seconds after the shot starts.
    captions = {panel: "words"}: a level handwritten caption under that drawing, written as it finishes inking.
    circles = {panel: (fx, fy, frx, fry)}: a circle around part of the drawing, as fractions of its box, drawn
    after its colour. marks = extra Marks (arrows between drawings, crosses). done = panels already drawn."""
    def run(b, t0, t1):
        m = marks if marks is not None else Marks()
        P = film.panels(sheet)
        abs_cues = [(p, t0 + dt) for p, dt in cues]
        for i, (p, tc) in enumerate(abs_cues):
            x0, y0, x1, y1 = P[p]
            nxt = abs_cues[i + 1][1] if i + 1 < len(abs_cues) else t1
            d = max(0.6, min(ink, (nxt - tc) * 0.65))
            if captions and p in captions:
                txt = captions[p]
                w = cap_size * 0.5 * len(txt)
                m.text(txt, (max(10, (x0 + x1) / 2 - w / 2), min(film.SH - cap_size, y1 + cap_size * 0.9)), cap_size,
                       tc + d * 0.7, min(0.9, 0.12 + 0.05 * len(txt)), color=cap_color, angle=0)
            if circles and p in circles:
                fx_, fy_, rx_, ry_ = circles[p]
                m.circle((x0 + fx_ * (x1 - x0), y0 + fy_ * (y1 - y0)), rx_ * (x1 - x0), ry_ * (y1 - y0),
                         tc + d + min(colour, 0.8), 0.5, color="red")
        kit.sheet(b, sheet, t0, t1, abs_cues, marks=m, ink=ink, colour=colour, done=done, **kw)
    return run


PAPER = "PAPER_sketchbook"


def paper_base(name=PAPER, tint=(250, 247, 240), seed=3):
    """A blank sketchbook page made in code (build/edit/<name>.png, source size), for drawings on blank paper when
    the film has no base of its own. Soft paper tooth, faint fibres, a slightly lighter centre."""
    out = film.BUILD / "edit" / f"{name}.png"
    if not out.exists():
        import cv2
        from PIL import Image
        out.parent.mkdir(parents=True, exist_ok=True)
        r = np.random.default_rng(seed)
        a = np.empty((film.SH, film.SW, 3), np.float32)
        a[:] = tint
        tooth = cv2.GaussianBlur(r.standard_normal((film.SH, film.SW)).astype(np.float32), (0, 0), 0.8) * 3.0
        fib = cv2.GaussianBlur(r.standard_normal((film.SH, film.SW)).astype(np.float32), (0, 0), 18) * 6.0
        yy, xx = np.mgrid[0:film.SH, 0:film.SW].astype(np.float32)
        vig = np.hypot((xx - film.SW / 2) / film.SW, (yy - film.SH / 2) / film.SH) * 14
        a += (tooth + fib - vig)[..., None]
        Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).save(out)
    return name


def blank(draw, base=None, medium="graphite", cam=None, marks=None, post=(), fx=(), trans=("dissolve", 0.3), drift=0.4):
    """A blank page drawn on live. draw(page, t0, t1) adds the drawings to a film.Page: page.lift(sheet, panel,
    center, height, a, b) redraws a sketch-sheet drawing (or a box of a scene's _lines) in stroke order;
    page.stroke / strokes / text for routes, timelines, words. base = a blank story object from the guide
    (notebook, blackboard, map), or None for the code-made sketchbook paper. medium = graphite | chalk | sumi |
    carve (film.MEDIA). cam = keys or a function (t0, t1) -> keys, in the base's source px."""
    def run(b, t0, t1):
        pg = film.Page(base or paper_base(), medium)
        draw(pg, t0, t1)
        k = _cam(cam, None, t0, t1, None) if cam is not None else [(t0, 887, 443, 887), (t1, 887, 443, 860)]
        b.page(t0, pg, k, marks=marks, post=list(post), fx=list(fx), trans=trans, drift=drift)
    return run


def custom(fn):
    """Any hand-written shot: fn(b, t0, t1)."""
    return fn


def photo(b, name, t_in, t_out, pos=(0.72, 0.46), height=0.6, credit=None, tilt=-3.0):
    return wr.photo(b, name, t_in, t_out, pos=pos, height=height, credit=credit, tilt=tilt)


def stamp(text, xy, t, size=110, angle=-9, b=None):
    if b is not None:
        b.fx("stamp", t, db=-5)
    return sg.Stamp(text, xy, t, size=size, angle=angle)


CREDIT = {}  # photo name -> on-screen credit line (fill per film; see examples/chadwick/tools/chad.py)


# ---------------------------------------------------------------- the Great Lakes map (B03): a living map
from film import Page  # noqa: E402
from fx2 import MapLayer, Traveller  # noqa: E402

LON, LAT, RECT = (-88.4, -70.2), (39.3, 46.4), (150, 110, 1640, 850)
TOWNS = {"Woodstock": (-80.75, 43.13), "Cleveland": (-81.69, 41.50), "Toledo": (-83.55, 41.65), "Columbus": (-83.00, 39.96),
         "New York": (-74.00, 40.71), "Oberlin": (-82.22, 41.29), "Brookline": (-71.12, 42.33), "Pittsburgh": (-79.99, 40.44),
         "Youngstown": (-80.65, 41.10)}
REGIONS = [("ONTARIO", (-79.6, 45.2)), ("MICHIGAN", (-84.9, 43.2)), ("OHIO", (-83.3, 40.5)), ("PENNSYLVANIA", (-78.6, 40.9)),
           ("NEW YORK", (-75.8, 42.7)), ("MASS.", (-72.4, 42.9))]
WATERS = [("Lake Erie", (-81.9, 42.25)), ("Lake Ontario", (-78.4, 43.75)), ("Lake Huron", (-82.6, 44.75)), ("L. Michigan", (-87.6, 44.4))]


def _proj():
    x0, y0, x1, y1 = RECT
    K = math.cos(math.radians(sum(LAT) / 2))
    S_ = min((x1 - x0) / ((LON[1] - LON[0]) * K), (y1 - y0) / (LAT[1] - LAT[0]))
    cx, cy, lc, ac = (x0 + x1) / 2, (y0 + y1) / 2, sum(LON) / 2, sum(LAT) / 2
    return lambda lo, la: np.array([cx + (lo - lc) * K * S_, cy - (la - ac) * S_])


P = _proj()


def set_map(lon, lat, towns, regions=(), waters=(), rect=RECT):
    """Point the living map at a story's region: lon/lat ranges, towns {name: (lon, lat)}, region and water names."""
    global LON, LAT, TOWNS, REGIONS, WATERS, RECT, P, _LAKES
    LON, LAT, TOWNS, REGIONS, WATERS, RECT = tuple(lon), tuple(lat), dict(towns), list(regions), list(waters), rect
    P = _proj()
    _LAKES = None
    _ML.clear()


def _projr(ring):
    r = np.asarray(ring, np.float64)
    return np.stack([P(lo, la) for lo, la in r[:, :2]])


_LAKES = None


def lakes():
    """The lakes inside the map (projected polygons: [outer, holes...]), biggest first."""
    global _LAKES
    if _LAKES is None:
        out = []
        for f in film._geojson("ne_10m_lakes.geojson"):
            g = f["geometry"]
            for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
                r = np.asarray(poly[0])
                if r[:, 0].max() < LON[0] or r[:, 0].min() > LON[1] or r[:, 1].max() < LAT[0] or r[:, 1].min() > LAT[1]:
                    continue
                q = _projr(poly[0])
                if np.hypot(*(q.max(0) - q.min(0))) < 35:
                    continue
                out.append([q[::max(1, len(q) // 900)]] + [_projr(h) for h in poly[1:]])
        out.sort(key=lambda pl: -np.hypot(*(pl[0].max(0) - pl[0].min(0))))
        _LAKES = out[:12]
    return _LAKES


def _clip_runs(ring, min_len=6):
    r = np.asarray(ring)
    ok = (r[:, 0] > LON[0]) & (r[:, 0] < LON[1]) & (r[:, 1] > LAT[0]) & (r[:, 1] < LAT[1])
    from scipy import ndimage as _nd
    lab, n = _nd.label(ok)
    out = []
    for k in range(1, n + 1):
        seg = r[lab == k]
        if len(seg) >= min_len:
            q = _projr(seg)
            if np.hypot(*(q.max(0) - q.min(0))) > 25:
                out.append(q[::max(1, len(q) // 400)])
    return out


def coast_runs():
    """The Atlantic coast (land outer rings that reach the sea inside the map)."""
    runs = []
    for f in film._geojson("ne_10m_land.geojson"):
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            runs += _clip_runs(poly[0])
    runs.sort(key=lambda q: -np.hypot(*np.diff(q, axis=0).T).sum())
    return runs[:6]


def border_runs():
    out = []
    for f in film._geojson("ne_10m_admin_0_boundary_lines_land.geojson"):
        g = f["geometry"]
        for line in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            out += _clip_runs(line, 3)
    return out


_ML = {}


def map_layer(t_shore, t_wash, t_border):
    key = (t_shore, t_wash, t_border)
    if key not in _ML:
        _ML[key] = MapLayer(lakes(), border_runs(), t_shore=t_shore, t_wash=t_wash, t_border=t_border, lines=coast_runs())
    return _ML[key]


def map_shot(t_map, towns=(), route=(), t_route=None, zoom=None, fast=False, trans=("dissolve", 0.3), extra=()):
    """The living map on B03: shores inked (pen) and the water washed in over t_map=(a, b) (fast: done by a + 0.5),
    the border dashed in, lake and region names typed; towns = [(name, t)] ink dots + names; route = town names the
    traveller hops along over t_route, leaving a dashed red road."""
    def run(b, t0, t1):
        a, z = t_map
        if fast:
            sh, wa, bo = (a - 0.01, a), (a, a + 0.4), (a, a + 0.3)
        else:
            sh, wa, bo = (a, a + (z - a) * 0.6), (a + (z - a) * 0.5, z), (a + (z - a) * 0.55, z)
        items = [map_layer(sh, wa, bo)]
        m = Marks()
        for i, (name, ll) in enumerate(WATERS):
            m.typed(name, tuple(P(*ll) - [60, 0]), 28, (a if fast else wa[0] + 0.15 * i), color="ink")
        for i, (name, ll) in enumerate(REGIONS):
            m.typed(name, tuple(P(*ll) - [70, 0]), 26, (a if fast else z - 0.3 + 0.1 * i), color="ink")
        for name, t in towns:
            x, y = P(*TOWNS[name])
            m.circle((x, y), 7, 7, t, 0.25, color="red", width=5)
            m.typed(name, (x + 14, y - 26), 32, t + 0.2, color="ink")
        if route and t_route:
            pts = [tuple(P(*TOWNS[n])) for n in route]
            sg.route(m, pts, t_route[0], t_route[1], color="red", width=4, head=False)
            items.append(Traveller(pts, t_route[0], t_route[1]))
        k = [(t0, *zoom[0]), (t1, *zoom[1])] if zoom else [(t0, 887, 443, 887), (t1, 887, 443, 860)]
        b.custom(t0, Live("B03_map", items + list(extra)), k, "B03_map", marks=m, trans=trans)
    return run
