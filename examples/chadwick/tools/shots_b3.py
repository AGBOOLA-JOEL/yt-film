"""b3 · Cleveland (P11-P17): the furniture, Madame DeVere, twelve days (comic page), the names, Toledo, prison, parole."""
from chad import *

b = Batch("b3")
S = Seq(b)

# P11
S.at(0.0, scene("S03b_furniture", zoom=((887, 443, 887), (800, 470, 760))))
S.at(4.5, scene("S03c_alice_face", "face", act=dict(widen=[(4.7, 7.2, 0.25)])))

# P12
S.at(8.1, scene("S03d_garden_st", "in", label="Garden Street, Cleveland", label_at=0.2))
m = Marks()
m.typed("Madame Lydia DeVere", (240, 330), 60, 12.85)
m.typed("clairvoyant", (240, 430), 44, 13.4)
ball = Draw("X03_names", 0, (1260, 470), 380, (12.9, 14.0), (14.0, 14.5))
S.at(12.8, page("B02_card", [ball], marks=m))
S.at(15.6, scene("S03e_seance", zoom=((887, 443, 887), (880, 470, 720))))
S.at(19.0, scene("S03f_crystal", zoom=((887, 443, 887), (1000, 560, 640))))
b.fx("clink", 20.2, db=-20)

# P13 · twelve days, as a comic page
P1, P2, P3, P4 = (60, 50, 1010, 430), (1035, 50, 1714, 430), (60, 455, 690, 837), (715, 455, 1714, 837)


def twelve_days(b, t0, t1):
    comic = sg.Comic("B09_board", [
        dict(box=P1, img="S03g_wedding", focus=(887, 400, 640), t=(t0 + 0.3, t0 + 0.9, t0 + 1.6)),
        dict(box=P2, img="S03h_paper", focus=(880, 420, 700), t=(27.8, 28.2, 28.8)),
        dict(box=P3, img="S03i_thrown_out", focus=(900, 360, 640), t=(30.8, 31.2, 31.8)),
        dict(box=P4, img="S03j_lydia_face", focus=(890, 330, 560), t=(33.8, 34.3, 35.0)),
    ], border_t=(t0, t0 + 0.8))
    cm = Marks()
    cm.typed("21 November 1882", (90, 80), 34, t0 + 1.7)
    cm.typed("12 days later", (745, 485), 34, 34.6)
    b.custom(t0, comic, [(t0, 887, 443, 887), (t0 + 1.0, 540, 240, 520), (27.6, 540, 240, 520), (28.2, 1375, 240, 520), (30.6, 1375, 240, 520),
                         (31.0, 375, 646, 520), (33.5, 375, 646, 520), (34.1, 1210, 646, 560), (t1 - 1.6, 1214, 646, 560), (t1, 887, 443, 887)],
             "B09_board", marks=cm, trans=("dissolve", 0.3))
    b.fx("paper", 28.0, 28.6, db=-14)
    b.fx("door", 31.4, db=-14)


S.at(22.2, custom(twelve_days))

# P14 · the names
S.at(37.0, scene("S03k_hats", zoom=((887, 443, 887), (1100, 420, 720))))
m = Marks()
m.typed("Madame Lydia DeVere", (240, 300), 54, 40.4, dur=0.3)
sg.cross(m, (230, 270, 900, 330), 41.0)
m.typed("Marie LaRose", (240, 430), 54, 41.9)
trunk = Draw("X03_names", 3, (1290, 470), 420, (40.6, 41.8), (41.8, 42.3))
S.at(40.4, page("B02_card", [trunk], marks=m))
S.at(44.4, scene("S04a_farm", zoom=((887, 443, 887), (1000, 470, 760))))
m = Marks()
m.typed("Madame Lydia DeVere", (240, 230), 44, 46.0, dur=0.2)
m.typed("Marie LaRose", (240, 330), 54, 46.0, dur=0.2)
sg.cross(m, (230, 210, 760, 255), 46.05, dur=0.15)
sg.cross(m, (230, 300, 600, 360), 46.2)
m.typed("Mrs. Hoover", (240, 470), 64, 46.3)
ring = Draw("X03_names", 2, (1080, 330), 170, (46.1, 46.8), (46.8, 47.1))
veil = Draw("X03_names", 1, (1380, 560), 360, (46.6, 47.6), (47.6, 48.0))
S.at(46.0, page("B02_card", [ring, veil], marks=m, trans=None))
S.at(48.6, scene("S04b_hoover", zoom=((887, 443, 887), (900, 470, 720))))

# P15 · Toledo
S.at(52.5, scene("S04c_toledo_shop", zoom=((887, 443, 887), (700, 470, 720)), label="Toledo, Ohio · 1889", label_at=0.2))
S.at(58.0, scene("S04d_toledo_court", zoom=((887, 443, 887), (860, 440, 760))))
S.at(62.1, scene("S04d_toledo_court", zoom=((860, 440, 760), (1200, 300, 600)), post=[stamp("9½ YEARS", (1260, 520), 66.2, b=b)]))

# P16 · the penitentiary
S.at(68.6, scene("S04e_pen", "in", label="The Ohio Penitentiary, Columbus", label_at=0.2))
photo(b, "ohio_pen.jpg", 69.4, 71.6, pos=(0.74, 0.42), height=0.5, credit=CREDIT["ohio_pen.jpg"])
S.at(71.8, scene("S04f_sewing", zoom=((887, 443, 887), (760, 470, 700))))
S.at(74.0, scene("S04g_sew_face", "face", act=dict(glances=[(74.3, 75.3, 0, -6)])))
m = Marks()
m.typed("worked", (330, 690), 44, 75.6)
m.typed("waited", (800, 690), 44, 76.4)
m.typed("behaved", (1230, 690), 44, 77.2)
sew = Draw("X04_prison", 1, (430, 420), 360, (75.5, 76.2), (76.2, 76.5))
keys_ = Draw("X04_prison", 2, (880, 420), 320, (76.3, 77.0), (77.0, 77.3))
wall = Draw("X04_prison", 0, (1330, 420), 360, (77.1, 77.9), (77.9, 78.3))
S.at(75.4, page("B02_card", [sew, keys_, wall], marks=m))

# P17 · parole
S.at(79.4, scene("S04h_parole", zoom=((887, 443, 887), (760, 520, 700))))
wr.footnote(b, 81.0, 88.6, 3, "Paroled by the governor", ["The governor of Ohio in 1893 was", "William McKinley, later President",
                                                           "of the United States."], side="left")
bag = Draw("X04_prison", 3, (1400, 175), 220, (85.4, 86.3), (86.3, 86.7), card=True)
S.at(83.9, scene("S04i_gate", zoom=((887, 443, 887), (900, 420, 740)), draws=[bag], fx=[("fade_out", b.end - 0.6, b.end)]))
b.fx("wind", 83.9, b.end, db=-18)
S.end()

if __name__ == "__main__":
    b.render()
