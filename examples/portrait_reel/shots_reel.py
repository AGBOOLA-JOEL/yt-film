"""Portrait proof: the opening of the Grant film as a reel (python tools/shots_reel.py --portrait [--stills out.png])."""
import sys
import numpy as np
import cv2
import film, reel
from film import Batch, Marks, Paper

b = Batch("b1")
b.end = 39.2
b.music = ("g_hook", 0.0)
T = b.t
t210, t80, t130, t_all, t_won, t_pres, t_morn = T("$210"), T("$80"), T("$130"), T("That was all"), T("He had won"), T("President"), T("And that morning")
t_name, t_man, t_32, t_small, t_how, t_preach, t_empty, t_general, t_war = (
    T("His name"), T("the man who"), T("32"), T("small"), T("So how"), T("preacher's"), T("empty"), T("general"), T("war"))

reel.badge(b, "1/3")
reel.headline(b, "THE GENERAL'S LAST $210", 0.25, t80 - 0.15, label="GRANT AND THE YOUNG NAPOLEON")
reel.captions(b, emph=["$210", "$80", "$130", "millionaire", "Grant", "32", "nobody"], mute=[(0, t80 - 0.1)])

# the price tag: each pile close as it is named, then the whole table in a window with the sum
m = Marks()
m.typed("$80", (585, 250), 64, t80 - 0.05)
m.circle((545, 560), 105, 80, t80 + 0.5, 0.6)
m.typed("$130", (1090, 250), 64, t130 - 0.05)
m.typed("= $210", (840, 770), 96, t_all + 0.5)
m.stroke([(840, 842), (1215, 834)], t_all + 1.6, 0.4, color="red", width=6)
b.scene(0.0, "S01g_table", [(0, 700, 443, 887), (t80 - 0.2, 630, 470, 800, "io"), (t130 - 0.3, 630, 470, 780, "lin"),
                            (t130 + 0.3, 1130, 460, 800, "out"), (t_all - 0.5, 1150, 460, 780, "lin"),
                            (t_all + 0.4, 887, 560, 1650, "back"), (t_won - 0.3, 887, 560, 1600, "lin")], marks=m, fx=[("fade_in", 0.6)])
b.fx("coins", t80 + 0.1, db=-13, n=4)
b.fx("coins", t130 + 0.1, db=-13, n=6)
b.fx("pop", t_all + 0.15, db=-16)
b.fx("tick", 0.0, t_won - 0.3, db=-24)

b.scene(t_won - 0.25, "S01h_parlour", [(t_won - 0.25, 760, 480, 760), (t_pres, 620, 400, 640, "out"), (t_morn - 0.3, 590, 380, 600, "lin")],
        trans=("whip", 0.3, 1), fx=[("fire", (851, 330), 320, 0.3)])
b.fx("swipe", t_won - 0.3, db=-18)
b.fx("fire", t_won - 0.25, t_name - 0.3, db=-22)
b.scene(t_morn - 0.25, "S01i_julia_face", [(t_morn - 0.25, 940, 443, 887), (t_name - 0.3, 950, 420, 720, "io")])
b.scene(t_name - 0.3, "S01e_grant_face", [(t_name - 0.3, 930, 470, 800), (t_man - 0.1, 955, 480, 660, "out")], trans=("flash", 0.25))
m = Marks()
m.typed("FERDINAND WARD, 32", (700, 120), 40, t_32 - 0.1)
b.scene(t_man - 0.1, "S05i_ward_face", [(t_man - 0.1, 800, 380, 700), (t_small, 900, 400, 800, "io"), (t_how - 0.3, 910, 400, 780, "lin")], marks=m)

# the question, drawn on a blank page: famous, not rich; the money going one way
pg = Paper(t_how - 0.3, [(t_how - 0.3, 1080, 1700, 2160), (b.end, 1080, 1640, 2050)])
f = pg.fig
f.text("a preacher's son", (130, 520), 84, t_preach, 0.8)
f.text("a general", (560, 900), 84, t_general - 0.2, 0.6)
f.arrow((640, 860), (420, 620), t_empty, 0.6, color="red", width=7)
f.text("$", (560, 640), 150, t_empty + 0.5, 0.3, color="red")
f.text("trusted nobody", (250, 1130), 84, t_war - 1.4, 0.8)
f.stroke([(240, 1250), (860, 1236)], t_war - 0.3, 0.4, color="red", width=7)
f.text("?", (900, 1040), 220, t_war + 0.1, 0.35, color="red")
b.paper(t_how - 0.3, pg, trans=("dissolve", 0.3))
b.fx("swipe", t_how - 0.35, db=-18)

if "--stills" in sys.argv:
    ts = [1.2, 3.3, 5.6, 9.0, 11.0, 15.4, 20.5, 24.5, 28.4, 34.3, 36.6, 38.8]
    fr = [cv2.resize(np.clip(b.still(t), 0, 255).astype(np.uint8), (360, 640)) for t in ts]
    sheet = np.vstack([np.hstack(fr[i:i + 6]) for i in range(0, len(fr), 6)])
    cv2.imwrite(sys.argv[sys.argv.index("--stills") + 1], cv2.cvtColor(sheet, cv2.COLOR_RGB2BGR))
else:
    b.render()
