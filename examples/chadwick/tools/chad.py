"""Shared shot helpers for Carnegie's Daughter (the nine batches): a sequencer that cuts on narration cues, per-image
living layers (fx2: smoke, breath, flames, the picture's own lamps, snow, leaves), and short builders for scenes,
drawings made live, pages, photos and stamps. Every effect ADDS a layer (the audit rule): no sg.Flow anywhere.

    from chad import *
    b = Batch("b3"); S = Seq(b)
    S.at("She borrowed", scene("S03b_furniture", "in"))
    ...
    S.end(); b.render()
"""
import math

import numpy as np

import film
import kit
import signature as sg
import wr
from film import Batch, Marks
from fx2 import Live, Smoke, Breath, Flame, Light, Lift, Draw, Tear, Counter, Leaves, Sparkle, lamps, u8, clean_text

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


LIVE = {
    "S01a_fifth_ave": lambda a, z: ([coal((695, 58), 2), Breath((588, 708), [a + 0.6, a + 2.4, a + 4.2, z - 1.5], direction=(-1, 0.12), seed=3),
                                     Breath((925, 596), [a + 1.5, z - 2.0], direction=(-0.9, -0.35), size=(4, 26), seed=5),
                                     Flame((1486, 356), 10, light=dict(amount=0.22), seed=1), Flame((1571, 530), 7, light=dict(amount=0.18), seed=2),
                                     Flame((983, 672), 8, light=dict(amount=0.2), seed=3)], [("snow", 0.4)], []),
    "S01b_dillon_waits": lambda a, z: ([Flame((204, 196), 22, light=dict(amount=0.32, flicker=0.5), seed=4)], [], []),
    "S01c_doorway": lambda a, z: ([coal((414, 150), 4)] + _L("S01c_doorway", 3), [("snow", 0.35)], []),
    "S01g_dillon_face": lambda a, z: ([Flame((221, 248), 24, light=dict(amount=0.3), seed=6)], [], []),
    "S01h_cassie_face": lambda a, z: ([Flame((222, 246), 22, light=dict(amount=0.3), seed=7)], [("snow", 0.2)], []),
    "S01i_drive_off": lambda a, z: ([coal((1050, 125), 5), Breath((1040, 470), [a + 0.5, a + 2.2], direction=(1, -0.1), seed=8)], [("snow", 0.45)], []),
    "S12j_mansion_today": lambda a, z: ([coal((695, 58), 9)] + _L("S12j_mansion_today", 4), [("snow", 0.4)], []),
    "S12i_pavement": lambda a, z: ([], [], [Leaves(a, z, n=7, seed=12)]),
    "S02a_town": lambda a, z: ([coal((961, 50), 10, 0.9)], [("snow", 0.3)], []),
    "S02b_father": lambda a, z: ([steam((1350, 120), 11, 0.6, wind=(-24, -2)), Breath((560, 330), [a + 0.8, a + 2.6, a + 4.4], direction=(-1, -0.1), seed=12)], [("snow", 0.3)], []),
    "S02c_kitchen": lambda a, z: ([Light((888, 470), 70, amount=0.2, flicker=0.4, seed=3), wisp((1755, 270), 13)], [], []),
    "S02d_betsy_face": lambda a, z: (_L("S02d_betsy_face", 2), [], []),
    "S02e_letter": lambda a, z: ([Light((533, 469), 140, amount=0.24, flicker=0.45, seed=4)], [], []),
    "S02g_woodstock": lambda a, z: ([Breath((540, 690), [a + 0.6, a + 2.8], direction=(-1, -0.1), seed=14)], [("snow", 0.45)], []),
    "S02i_courtroom": lambda a, z: (_L("S02i_courtroom", 2), [], []),
    "S02k_train": lambda a, z: ([steam((858, 110), 15, 1.0, wind=(-30, -6))] + _L("S02k_train", 2), [("snow", 0.4)], []),
    "S03a_cleveland": lambda a, z: ([coal((1183, 160), 16), coal((1260, 175), 17, 0.8)], [], []),
    "S03b_furniture": lambda a, z: (_L("S03b_furniture", 2), [], []),
    "S03d_garden_st": lambda a, z: (_L("S03d_garden_st", 3, 0.18), [("snow", 0.25)], []),
    "S03e_seance": lambda a, z: ([Flame((1078, 492), 30, light=dict(amount=0.25), seed=1), Flame((715, 527), 30, light=dict(amount=0.25), seed=2),
                                  wisp((1078, 440), 3), wisp((715, 470), 4)], [], []),
    "S03f_crystal": lambda a, z: ([Flame((1539, 262), 64, light=dict(amount=0.3), seed=5), Flame((539, 352), 58, light=dict(amount=0.3), seed=6),
                                   Sparkle([(890, 300), (1030, 420), (1180, 700)], seed=2)], [], []),
    "S04b_hoover": lambda a, z: (_L("S04b_hoover", 2), [("snow", 0.15)], []),
    "S04d_toledo_court": lambda a, z: (_L("S04d_toledo_court", 2), [], []),
    "S04e_pen": lambda a, z: ([coal((739, 110), 18, 0.8), coal((1094, 96), 19, 0.8), coal((1480, 120), 20, 0.8)], [], []),
    "S04f_sewing": lambda a, z: (_L("S04f_sewing", 2), [], []),
    "S04i_gate": lambda a, z: ([coal((488, 420), 21, 0.7)], [], [Leaves(a, z, n=16, seed=4, avoid="S04i_gate")]),
    "S05a_westside": lambda a, z: ([coal((325, 440), 22, 0.8), coal((490, 470), 23, 0.6)] + _L("S05a_westside", 5, 0.16), [("rain", 0.35)], []),
    "S05b_parlour": lambda a, z: (_L("S05b_parlour", 3, 0.16), [], []),
    "S05c_leroy_face": lambda a, z: (_L("S05c_leroy_face", 2, 0.16), [], []),
    "S05d_faint": lambda a, z: (_L("S05d_faint", 3, 0.16), [], []),
    "S05e_explains": lambda a, z: (_L("S05e_explains", 3, 0.16), [], []),
    "S05h_arrives": lambda a, z: ([Breath((180, 470), [a + 0.4, a + 2.4], direction=(-1, 0), seed=24)], [("snow", 0.3)], []),
    "S05i_neighbours": lambda a, z: ([coal((420, 230), 25, 0.6)] + _L("S05i_neighbours", 2), [("snow", 0.3)], []),
    "S06e_dusk": lambda a, z: ([coal((444, 210), 26, 0.7)] + _L("S06e_dusk", 6, 0.15), [("snow", 0.45)], []),
    "S06d_window": lambda a, z: (_L("S06d_window", 2), [("snow", 0.2)], []),
    "S07a_holland": lambda a, z: ([Breath((95, 520), [a + 0.4, a + 2.4], direction=(-1, 0), seed=27)] + _L("S07a_holland", 4), [("snow", 0.4)], []),
    "S07b_lobby": lambda a, z: (_L("S07b_lobby", 3), [], []),
    "S07e_mansion": lambda a, z: (_L("S07e_mansion", 3), [("snow", 0.35)], []),
    "S07f_hall": lambda a, z: (_L("S07f_hall", 2), [], []),
    "S07g_housekeeper_face": lambda a, z: (_L("S07g_housekeeper_face", 2), [], []),
    "S07i_wave": lambda a, z: (_L("S07i_wave", 2) + [Breath((1530, 300), [a + 0.6, a + 2.6], direction=(1, 0), seed=28)], [("snow", 0.3)], []),
    "S07j_secret": lambda a, z: ([], [("snow", 0.2)], []),
    "S08a_bank": lambda a, z: ([coal((872, 70), 29, 0.7), coal((1520, 90), 30, 0.6)] + _L("S08a_bank", 3), [("snow", 0.4)], []),
    "S08b_office": lambda a, z: (_L("S08b_office", 2), [], []),
    "S08c_seal": lambda a, z: ([Light((1630, 250), 110, amount=0.28, flicker=0.5, seed=5), wisp((1630, 200), 31)], [], []),
    "S08e_vault": lambda a, z: (_L("S08e_vault", 2), [], []),
    "S08g_club": lambda a, z: ([wisp((560, 820), 32), wisp((1200, 820), 33)] + _L("S08g_club", 3), [], []),
    "S08h_boardroom": lambda a, z: (_L("S08h_boardroom", 3), [], []),
    "S09b_beckwith_office": lambda a, z: (_L("S09b_beckwith_office", 2), [], []),
    "S09e_own_money": lambda a, z: ([Light((1395, 277), 160, amount=0.2, flicker=0.15, seed=6)], [], []),
    "S09f_jeweller": lambda a, z: (_L("S09f_jeweller", 2) + [Sparkle([(990, 355), (1050, 390), (930, 380), (760, 840), (1330, 830), (1120, 720)], size=18, seed=4)], [], []),
    "S09i_organ": lambda a, z: (_L("S09i_organ", 4), [], []),
    "S09j_dinner": lambda a, z: ([Light((828, 70), 170, amount=0.16, flicker=0.15, seed=1)]
                                 + [Light(p, 55, amount=0.16, flicker=0.4, seed=10 + i) for i, p in enumerate([(717, 540), (1020, 510), (798, 640), (998, 640), (1055, 545)])]
                                 + [Flame((x, 535), 30 + 6 * (i % 2), light=dict(amount=0.18), seed=20 + i) for i, x in enumerate((62, 84, 104))], [], []),
    "S09k_gift": lambda a, z: ([Sparkle([(770, 470), (1140, 120), (1700, 360)], size=20, seed=5)], [], []),
    "S09l_christmas": lambda a, z: ([Sparkle([(1060, 220), (1140, 330), (990, 380), (1120, 470), (1030, 560)], size=14, rate=1.0, seed=6)] + _L("S09l_christmas", 2), [], []),
    "S09m_queen_face": lambda a, z: ([Flame((60, 760), 34, light=dict(amount=0.2), seed=7), Flame((95, 765), 28, light=False, seed=8),
                                      Sparkle([(700, 640), (760, 760), (840, 700)], size=14, seed=7)], [], []),
    "S09n_night": lambda a, z: (_L("S09n_night", 6, 0.16) + [Breath((790, 520), [a + 0.5, a + 2.5], direction=(-1, 0), seed=34)], [("snow", 0.5)], []),
    "S10a_brookline": lambda a, z: ([], [], [Leaves(a, z, n=16, seed=8, avoid="S10a_brookline")]),
    "S10b_newton": lambda a, z: ([], [], []),
    "S10e_reporters": lambda a, z: ([coal((900, 110), 35, 0.6)], [("snow", 0.35)], []),
    "S10f_carnegie_office": lambda a, z: (_L("S10f_carnegie_office", 2), [("snow", 0.15)], []),
    "S10h_run": lambda a, z: ([coal((1022, 46), 12), Light((470, 140), 50, amount=0.2, seed=3), Light((1205, 195), 50, amount=0.2, seed=4),
                               Light((1680, 165), 50, amount=0.2, seed=5)], [("snow", 0.5)], []),
    "S10i_empty": lambda a, z: (_L("S10i_empty", 2), [], []),
    "S10k_opened": lambda a, z: (_L("S10k_opened", 2), [], []),
    "S10m_breslin": lambda a, z: ([coal((210, 160), 36, 0.6), coal((1395, 120), 37, 0.6)] + _L("S10m_breslin", 6, 0.16), [("snow", 0.55)], []),
    "S10n_arrest": lambda a, z: ([Light((180, 450), 120, amount=0.18, flicker=0.3, seed=7)], [], []),
    "S10o_defiant_face": lambda a, z: ([Light((145, 520), 130, amount=0.2, flicker=0.3, seed=8)], [("snow", 0.15)], []),
    "S11a_courthouse": lambda a, z: ([coal((399, 150), 38, 0.8)], [("rain", 0.4)], []),
    "S11b_courtroom": lambda a, z: (_L("S11b_courtroom", 3), [], []),
    "S11d_prosecutor": lambda a, z: (_L("S11d_prosecutor", 3), [], []),
    "S11g_verdict": lambda a, z: (_L("S11g_verdict", 3), [], []),
    "S11j_spear": lambda a, z: ([Breath((700, 300), [a + 0.4, a + 2.0], direction=(-1, 0), seed=39)] + _L("S11j_spear", 2), [("snow", 0.35)], []),
    "S12a_trunks": lambda a, z: ([coal((1080, 70), 40, 0.7), Breath((80, 470), [a + 0.5, a + 2.5], direction=(-1, 0), seed=41)], [("snow", 0.4)], []),
    "S12b_cell": lambda a, z: ([Light((452, 120), 150, amount=0.2, flicker=0.25, seed=9)], [], []),
    "S12c_hospital": lambda a, z: ([], [("snow", 0.15)], []),
    "S12e_woodstock": lambda a, z: ([], [], [Leaves(a, z, n=20, seed=10, avoid="S12e_woodstock", y_max=0.3)]),
    "S12f_tourists": lambda a, z: ([], [], []),
}


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


def scene(img, move="in", zoom=None, act=None, label=None, corner="tl", draws=(), marks=None, post=(), fx=(), extra=(),
          trans=None, live=True, label_at=0.4, shake=None, swap=None):
    """One picture with its living layers. draws = [Draw(...)] (made live: pen sprite and sound), extra = more fx2
    effects, act = face cues (only on audited faces), label = typed place/date, kept inside the camera's view."""
    def run(b, t0, t1):
        k = keys(move, t0, t1, zoom)
        src, sfx, spost = living(img, t0, t1) if live else ([], [], [])
        m = marks
        if label:
            m = kit.label(label, t0 + label_at, corner=corner, keys=k, marks=m)
        kw = dict(marks=m, post=list(spost) + list(post), fx=list(sfx) + list(fx))
        if trans:
            kw["trans"] = trans
        if shake:
            kw["shake"] = shake
        if act:
            wr.sc(b, t0, t1, img, keys=k, src=u8(*(list(src) + list(extra) + list(draws))), act=act, **kw)
        elif draws or src or extra:
            b.custom(t0, Live(img, list(src) + list(extra) + list(draws)), k, img, **kw)
        else:
            b.scene(t0, img, k, **kw)
    return run


def drawin(img, move="in", zoom=None, ink=(0.0, 2.0), flood=(1.6, 3.0), marks=None, label=None, trans=("dissolve", 0.3), post=(), fx=()):
    """A scene that draws itself (its _lines version inks in, then the paint floods), times relative to the cue."""
    def run(b, t0, t1):
        k = keys(move, t0, t1, zoom)
        m = marks
        if label:
            m = kit.label(label, t0 + 0.4, keys=k, marks=m)
        src, sfx, spost = living(img, t0, t1)
        b.drawin(t0, img, k, ink=img + "_lines", flood=True, ink_t=(t0 + ink[0], t0 + ink[1]), flood_t=(t0 + flood[0], t0 + flood[1]),
                 marks=m, trans=trans, post=list(spost) + list(post), fx=list(sfx) + list(fx))
    return run


def page(base, items=(), marks=None, zoom=None, post=(), fx=(), trans=("dissolve", 0.3)):
    """A blank base drawn on live: items are fx2 effects (Draw, Tear...), marks are words/arrows (Marks)."""
    def run(b, t0, t1):
        k = [(t0, *zoom[0]), (t1, *zoom[1])] if zoom else [(t0, 887, 443, 887), (t1, 887, 443, 850)]
        b.custom(t0, Live(base, list(items)), k, base, marks=marks, post=list(post), fx=list(fx), trans=trans)
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


CREDIT = {"chadwick_1904.jpg": "Cassie L. Chadwick, 1904 · Wikimedia Commons",
          "chadwick_house.jpg": "Her house on Euclid Avenue, before 1906 · Wikimedia Commons",
          "carnegie_1905.jpg": "Andrew Carnegie, 1905 · F. B. Johnston / Library of Congress",
          "carnegie_1905_lc.jpg": "Andrew Carnegie, 1905 · F. B. Johnston / Library of Congress",
          "carnegie_mansion_1902.jpg": "Carnegie's Fifth Avenue mansion, c.1902 · Cooper Hewitt",
          "ohio_pen.jpg": "The Ohio Penitentiary, 1874 · Wikimedia Commons"}


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
