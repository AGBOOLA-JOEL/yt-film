"""Extra film helpers on top of wr / kit / signature."""
import kit
import signature as sg
from film import Marks, Page

BOARD = "B09_board"


def under(b, m, sheet, items, size=36, gap=36):
    """Typed labels centred under drawings of a sheet: items = [(panel, text, t), ...]."""
    P = [b.panel(sheet, i) for i in range(4)]
    y = max(p[3] for p in P) + gap
    for i, s_, t in items:
        x0, _, x1, _ = P[i]
        m.typed(s_, ((x0 + x1) / 2 - len(s_) * size * 0.31, y), size, t)
    return m


def cen(b, sheet, i):
    x0, y0, x1, y1 = b.panel(sheet, i)
    return ((x0 + x1) / 2, (y0 + y1) / 2)


def stamp(b, post, text, xy, t, size=70, angle=-8, db=-5):
    post.append(sg.Stamp(text, xy, t, size, angle=angle))
    b.fx("stamp", t, db=db)
    return post
