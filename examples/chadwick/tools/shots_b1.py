"""b1 · The hook: the note on Fifth Avenue (P01-P04). Hook type: the document."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import film
import sketch as sk
from chad import *

b = Batch("b1")
S = Seq(b)

# P01: the street draws itself, then lives; the carriage; Carnegie drawn beside his house
S.at(0.0, drawin("S01a_fifth_ave", zoom=((887, 443, 887), (900, 470, 800)), ink=(0.0, 1.8), flood=(1.4, 3.2), trans=("dissolve", 0.6),
                 label="New York · around 1902"))
S.at(3.9, scene("S01a_fifth_ave", zoom=((900, 470, 800), (905, 560, 640))))
S.at(7.0, scene("S01b_dillon_waits", zoom=((887, 443, 887), (850, 440, 800))))
carn = Draw("X05_carnegie", 0, (1585, 320), 380, (11.0, 12.4), (12.4, 13.1), card=True)
m = Marks()
m.typed("Andrew Carnegie", (1468, 590), 34, 12.0)
m.arrow((1470, 420), (1240, 380), 12.3, 0.4, color="red", bend=-0.2)
S.at(10.6, scene("S01a_fifth_ave", zoom=((1170, 400, 770), (1190, 405, 730)), draws=[carn], marks=m))

# P02: she comes out, waves, stumbles; the note slips from her muff and lands
S.at(14.4, scene("S01c_doorway", zoom=((887, 443, 887), (1000, 380, 700)), act=dict(widen=[(17.9, 18.8, 0.15)])))
paper_hand = [(975, 625), (1040, 612), (1058, 688), (992, 700)]
c = np.mean(paper_hand, 0)
slip = Lift("S01d_trip", paper_hand, [(24.05, c[0], c[1], 0, 1.0), (24.45, c[0] - 20, c[1] + 70, 25, 1.05), (25.0, c[0] - 60, 980, 80, 1.15)],
            flutter=0.5, shadow=(6, 10, 0.25), fill_from=(-95, 0))
d_items = [Smoke((1042, 112), rate=3, life=5, rise=30, wind=(10, -3), size=(10, 60), color=COAL, light=COAL_LIT, alpha=0.65, seed=7),
           Smoke((1138, 108), rate=3, life=5, rise=30, wind=(10, -3), size=(10, 60), color=COAL, light=COAL_LIT, alpha=0.65, seed=8),
           Breath((80, 570), [20.2, 22.4, 24.3], direction=(-1, 0.05), seed=9), Flame((441, 390), 10, light=dict(amount=0.25), seed=5), slip]
S.at(19.8, scene("S01d_trip", zoom=((900, 470, 760), (950, 520, 640)), extra=d_items, act=dict(widen=[(21.8, 22.8, 0.25)]),
                 fx=[("snow", 0.35)], shake=[(21.9, 7)]))
b.fx("thud", 21.9, db=-20)
b.fx("paper", 24.1, 24.7, db=-11)
paper_ground = [(505, 690), (1100, 722), (1150, 770), (1140, 808), (530, 800), (500, 760)]
g = np.mean(paper_ground, 0)
land = Lift("S01e_paper_falls", paper_ground, [(24.9, 760, -170, -30, 1.15), (25.45, 900, 380, 16, 1.07), (25.95, g[0], g[1], 0, 1.0)],
            flutter=0.55, shadow=(10, 12, 0.4), fill_from=(655, 4))
S.at(24.9, scene("S01e_paper_falls", zoom=((887, 480, 840), (860, 560, 720)), extra=[land], fx=[("snow", 0.3)]))
b.fx("paper", 25.85, 26.2, db=-15)

# P03: he reads it; the words write themselves on the note
S.at(26.7, scene("S01g_dillon_face", zoom=((887, 443, 887), (860, 380, 760)), act=dict(widen=[(26.9, 29.4, 0.3)])))
NOTE = clean_text("S01f_reads", [[(405, 285), (1330, 285), (1330, 712), (405, 712)]])
m = Marks()
m.write("I promise to pay to the order of", (440, 345), (1300, 345), 30.8, 2.0, color="ink")
m.write("Mrs. Cassie L. Chadwick", (440, 425), (1040, 425), 33.0, 1.3, color="ink")
m.write("the sum of two million dollars", (440, 505), (1240, 505), 34.9, 1.1, color="ink")
m.write("$2,000,000.00", (440, 585), (800, 585), 36.1, 0.6, color="ink")
m.write("Andrew Carnegie", (930, 685), (1310, 685), 37.6, 0.9, size=62, color="ink")
S.at(29.6, scene(NOTE, zoom=((870, 470, 800), (880, 480, 740)), marks=m, live=False))
S.at(40.2, scene("S01h_cassie_face", zoom=((887, 443, 887), (860, 400, 720)), act=dict(expr=[(42.1, 43.8, None, "half")])))
wr.footnote(b, 40.6, 48.6, 1, "The carriage story", ["Dillon's own account, retold", "in the papers after her arrest.",
                                                      "We only have his word for it."])


# P04: forged; the promise of the film
def written_note():
    out = film.BUILD / "edit" / "B01_note_written.png"
    if not out.exists():
        a = Image.open(film.find_img("B01_note")).convert("RGB")
        W, H = a.size
        crop = (H - round(W * 887 / 1774)) // 2
        f = W / 1774
        dr = ImageDraw.Draw(a)
        for txt, (x, y), size in [("I promise to pay to the order of Mrs. Cassie L. Chadwick", (330, 430), 44),
                                  ("the sum of two million dollars,  $2,000,000.00", (330, 530), 44), ("Andrew Carnegie", (980, 655), 70)]:
            dr.text((x * f, y * f + crop), txt, font=ImageFont.truetype(sk.HAND, int(size * f)), fill=(52, 40, 32))
        out.parent.mkdir(parents=True, exist_ok=True)
        a.save(out)
    return "B01_note_written"


NOTE2 = written_note()
S.at(43.8, scene(NOTE2, zoom=((887, 443, 860), (980, 470, 700)), live=False, post=[stamp("FORGED", (560, 300), 44.95, b=b)],
                 trans=("dissolve", 0.3)))
S.at(48.8, scene("S01i_drive_off", "in"))
S.at(51.8, scene("S08h_boardroom", zoom=((887, 443, 887), (900, 420, 720))))
S.at(55.6, scene("S09n_night", zoom=((887, 443, 887), (820, 420, 700))))
S.at(58.8, scene("S08e_vault", zoom=((887, 443, 887), (1220, 470, 620))))
S.at(62.8, scene("S07h_muff", zoom=((887, 443, 887), (760, 600, 560)), fx=[("fade_out", b.end - 0.8, b.end)]))
b.fx("wind", 0.0, 14.4, db=-16)
S.end()

if __name__ == "__main__":
    b.render()
