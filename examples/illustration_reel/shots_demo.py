"""Every way the engine illustrates, on the Grant film's own images (no narration): a reference reel.
    python tools/stills.py demo 24      a stills sheet          python tools/shots_demo.py      the full render
Each segment is labelled (top left) with the technique it shows and the engine call that makes it."""
from grant import *

b = Batch("demo")
S = Seq(b)
END = b.end
b.act_break = True  # a reel, not a film: it may fade in and out
b.long_holds = {"S01h_parlour", "S16e_twain_broke"}  # the reel holds while the footnote types


def name(t0, t1, text):
    b.overlay(tag(b, text, t0 + 0.2, t1 - 0.3, corner="tl"), t0, t1)


# 1 · a living picture, the camera with a purpose (scene, LIVE table, cam keys with eases)
name(0.0, 7.0, "1 · living picture + a camera move")
S.at(0.0, scene("S01h_parlour", fx=[("fade_in", 0.8)], light=(851, 330),
                cam=lambda a, z: [(a, 887, 560, 560), (a + 3.0, 887, 443, 887, "out"), (z, 600, 330, 600, "io")]))

# 2 · drawn on the picture itself: typed numbers, a circle, an arrow, a level handwritten note, an underline
name(7.0, 15.0, "2 · sketching on the picture (Marks, sg)")
m = Marks()
m.typed("$80", (230, 680), 110, 7.6)
m.typed("$130", (760, 690), 110, 8.4)
m.circle((380, 590), 250, 150, 9.4, 0.6, color="red")
m.arrow((1330, 300), (1080, 520), 10.4, 0.5, color="red")
m.text("all he had left", (1130, 230), 56, 10.9, 0.9, color="redh", angle=0)
m.typed("= $210", (1260, 660), 120, 12.0)
sg.underline(m, (1260, 760), (1700, 760), 13.0, color="red")
sg.motion(m, (560, 520), -90, 3, 90, 13.6, color="cream")
S.at(7.0, scene("S01g_table", marks=m, cam=lambda a, z: [(a, 887, 443, 887), (z, 900, 470, 800, "lin")]))
b.fx("coins", 8.5, db=-13, n=5)

# 3 · a scene that draws itself: its _lines version inks in, then the paint floods (drawin)
name(15.0, 22.0, "3 · the scene draws itself (drawin)")
S.at(15.0, drawin("S01a_wall_st", ink=(0.0, 2.2), flood=(2.0, 3.6), label="Wall Street, New York · 1884",
                  cam=lambda a, z: [(a, 887, 443, 887), (z, 1000, 400, 700, "io")]))

# 4 · pin mode: one drawing from a sheet pinned on a scrap over the scene (scene(draws=[Scrap, Draw]))
name(22.0, 30.0, "4 · pinned scrap with a live drawing")
S.at(22.0, scene("S15a_pressroom", cam=lambda a, z: [(a, 1100, 443, 700), (z, 887, 443, 887, "out")],
                 draws=[Scrap((1480, 160), (300, 230), 22.6), dr("X08_book", 1, (1480, 160), 200, 22.8),
                        Scrap((300, 200), (280, 250), 25.0), dr("X02_wall_st", 0, (300, 200), 210, 25.2)]))
b.fx("press", 22.0, 30.0, db=-16)

# 5 · the sketchbook sheet itself: each drawing inks in, then its colour; captions and a circle (sketchbook)
name(30.0, 45.0, "5 · the sketchbook sheet (sketchbook)")
cm = Marks()
S.at(30.0, sketchbook("X03_machine", [(0, 0.3), (1, 3.4), (2, 6.4), (3, 9.6)],
                      captions={0: "one bond", 1: "three envelopes", 2: "three banks", 3: "the same money"},
                      circles={0: (0.5, 0.78, 0.22, 0.18)}, marks=cm))

# 6 · a blank page: drawings lifted from the sheets and redrawn stroke by stroke, a timeline drawn in code (blank)
name(45.0, 58.0, "6 · the blank page (blank + page.lift)")


def on_paper(pg, t0, t1):
    pg.lift("X02_wall_st", 3, (330, 420), 560, t0 + 0.3, t0 + 2.6, fade=0.06)
    pg.lift("X02_wall_st", 0, (900, 380), 420, t0 + 2.8, t0 + 5.0, fade=0.06)
    pg.text("Ward, 29", (220, 760), 48, t0 + 2.4, 0.6, accent=True)
    pg.text("the ticker", (790, 650), 48, t0 + 4.8, 0.6, accent=True)
    arc_ = kit.arc((520, 300), (720, 300), 0.35)
    pg.stroke(arc_, t0 + 5.4, 0.5, width=4, accent=True)
    pg.strokes(kit.arrowhead(arc_, 20), t0 + 5.9, t0 + 6.1, width=4, accent=True)
    pg.stroke([(1080, 600), (1560, 600)], t0 + 6.6, 0.7, width=3)
    for k, (x, yr) in enumerate([(1100, "1880"), (1300, "1882"), (1500, "1884")]):
        pg.stroke([(x, 580), (x, 620)], t0 + 7.3 + 0.4 * k, 0.2, width=3)
        pg.text(yr, (x - 45, 650), 40, t0 + 7.4 + 0.4 * k, 0.4)
    pg.stroke(kit.ring((1500, 600), 34), t0 + 8.8, 0.5, width=4, accent=True)
    pg.text("the crash", (1410, 520), 44, t0 + 9.2, 0.6, accent=True)


S.at(45.0, blank(on_paper, medium="graphite",
                 cam=lambda a, z: [(a, 500, 420, 760), (a + 5.0, 700, 420, 900, "io"), (a + 7.0, 1250, 520, 760, "io"),
                                   (z, 887, 443, 887, "out")]))

# 7 · a story object drawn on: the map base, a route, ticks, leader labels, two pinned drawings (page)
name(58.0, 66.0, "7 · drawing on a story object (page)")
mp = Marks()
pts = {"66": (860, 220), "V": (800, 380), "W": (700, 780)}
for k, p in pts.items():
    sg.tick(mp, p, 18, 58.6 if k != "W" else 59.2, color="red")
sg.leader(mp, pts["66"], (980, 160), "3 East 66th Street", 59.0, size=34)
sg.leader(mp, pts["V"], (980, 420), "Vanderbilt, Fifth Avenue", 59.8, size=34)
sg.leader(mp, pts["W"], (860, 830), "2 Wall Street", 59.4, size=30)
sg.route(mp, [pts["66"], (840, 300), pts["V"]], 60.4, 62.0)
S.at(58.0, page("B03_map", [dr("X05_vanderbilt", 3, (330, 640), 190, 61.0), dr("X05_vanderbilt", 1, (330, 300), 230, 62.6)],
                marks=mp, cam=lambda a, z: [(a, 887, 443, 887), (z, 887, 443, 850, "lin")]))
b.fx("hooves", 58.0, 66.0, db=-22)

# 8 · a comic page: panels painted in turn on the board, the camera visiting each (sg.Comic)
name(66.0, 79.0, "8 · the comic page (sg.Comic)")
P1, P2, P3, P4 = (60, 50, 1010, 430), (1035, 50, 1714, 430), (60, 455, 690, 837), (715, 455, 1714, 837)


def comic(b, t0, t1):
    c = sg.Comic("B09_board", [
        dict(box=P1, img="S01b_hats", focus=(900, 470, 620), t=(t0 + 0.2, t0 + 0.6, t0 + 1.2)),
        dict(box=P2, img="S11g_grant_resolve", focus=(887, 380, 640), t=(t0 + 3.2, t0 + 3.6, t0 + 4.2)),
        dict(box=P3, img="S01b_hats", focus=(1560, 380, 520), t=(t0 + 6.2, t0 + 6.6, t0 + 7.2)),
        dict(box=P4, img="S01c_office", focus=(1000, 420, 640), t=(t0 + 9.2, t0 + 9.6, t0 + 10.2)),
    ], border_t=(t0, t0 + 0.8))
    b.custom(t0, c, [(t0, 887, 443, 887), (t0 + 1.0, 535, 240, 520), (t0 + 3.0, 535, 240, 520, "lin"), (t0 + 3.5, 1375, 240, 520),
                     (t0 + 6.0, 1375, 240, 520, "lin"), (t0 + 6.5, 375, 646, 520), (t0 + 9.0, 375, 646, 520, "lin"),
                     (t0 + 9.5, 1214, 646, 560), (t1 - 0.8, 887, 443, 887), (t1, 887, 443, 887)], "B09_board", marks=Marks())


S.at(66.0, custom(comic))

# 9 · felt effects: a rolling counter, a rubber stamp with its thump (Counter, stamp)
name(79.0, 87.0, "9 · counter + stamp")
words_ctr = Counter([(79.6, 0), (81.4, 366_000)], pos=(0.24, 0.84), label="words", prefix="", size=1.1)
S.at(79.0, scene("S13i_pencil", post=[words_ctr, stamp("FINISHED", (1250, 700), 83.0, b=b)],
                 cam=lambda a, z: [(a, 1100, 330, 600), (z, 887, 443, 860, "out")]))

# 10 · an archive photo print and a footnote card over the film (pic, note)
name(87.0, END, "10 · archive photo + footnote")
S.at(87.0, scene("S16e_twain_broke", light=(1700, 150), fx=[("fade_out", END - 0.8, END)],
                 cam=lambda a, z: [(a, 887, 443, 887), (z, 870, 330, 680, "io")]))
pic(b, "twain_1884.jpg", 87.4, END - 0.6, pos=(0.77, 0.44), height=0.58, tilt=3.0)
note(b, 88.2, END - 0.3, 1, "Mark Twain", ["Published the memoirs in 1885.", "Sources: pinned comment."], side="left")
S.end()

if __name__ == "__main__":
    b.render()
