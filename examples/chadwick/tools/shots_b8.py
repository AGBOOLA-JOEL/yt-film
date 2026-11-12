"""b8 · The fall (P38-P43): the envelope opened, the Breslin, the newspapers, the trial, Carnegie in the gallery,
guilty, the bankers."""
from chad import *

b = Batch("b8")
S = Seq(b)

# P38 · the envelope opened
S.at(0.0, scene("S10k_opened", zoom=((887, 443, 887), (860, 520, 680))))
b.fx("rip", 2.9, 3.6, db=-14)
m = Marks()
sg.tally(m, 250, 560, 24, 4.8, 4.9, h=60, gap=18, color="red", width=4)
m.stroke([(150, 120), (600, 140), (1100, 125), (1650, 140)], 5.0, 0.5, color="red", width=5)
m.typed("opened, at last", (250, 300), 52, 4.9, color="ink")
S.at(4.8, page("B05_envelope", [], marks=m))
m = Marks()
m.typed("not even good ones", (980, 760), 44, 9.2, color="cream")
S.at(7.4, scene("S10l_forgeries", zoom=((887, 443, 887), (940, 430, 760)), marks=m, post=[stamp("FORGED", (800, 420), 8.3, size=130, b=b)]))

# P39 · the Breslin; the papers
S.at(12.0, scene("S10m_breslin", "in", label="New York · 7 December 1904", label_at=0.2))
S.at(15.0, scene("S10n_arrest", zoom=((887, 443, 887), (700, 470, 760))))
m = Marks()
sg.leader(m, (660, 760), (300, 820), "about $100,000", 20.4, size=40)
S.at(20.1, scene("S10n_arrest", zoom=((700, 470, 760), (700, 640, 520)), marks=m))
S.at(23.0, scene("S10o_defiant_face", "face", act=dict(expr=[(23.1, 24.4, "flat", None)])))


def papers(b, t0, t1):
    pg = Page("B07_newspaper", "graphite")
    kit.halftone(pg, str(film.INC / "05_photos" / "chadwick_1904.jpg"), (340, 85, 700, 500), t0 + 0.2, t0 + 1.6)
    pg.lift("X08_fall", 3, (1230, 700), 220, t0 + 0.6, t0 + 1.6)
    pg.lift("X08_fall", 1, (560, 700), 220, t0 + 1.2, t0 + 2.2)
    pg.lift("X08_fall", 2, (900, 700), 150, t0 + 1.8, t0 + 2.6)
    m = Marks()
    m.typed("MRS. CHADWICK ARRESTED", (740, 150), 46, t0 + 0.3, color="ink")
    m.typed("Queen of Swindlers", (760, 260), 36, t0 + 1.6, color="ink")
    m.typed("Duchess of Diamonds", (760, 330), 36, t0 + 2.4, color="ink")
    m.typed("High Priestess of Fraudulent Finance", (760, 400), 30, t0 + 2.5, color="ink")
    b.page(t0, pg, [(t0, 887, 443, 887), (t1, 887, 380, 760)], marks=m, trans=("dissolve", 0.3))
    b.fx("shutter", t0 + 0.2, db=-14)


S.at(24.4, custom(papers))

# P40 · the trial
S.at(30.0, scene("S11a_courthouse", "in", label="Cleveland · March 1905", label_at=0.05))
b.fx("rain", 30.0, 32.8, db=-20)
S.at(32.8, drawin("S11b_courtroom", zoom=((887, 443, 887), (900, 400, 760)), ink=(0.0, 1.3), flood=(1.0, 2.3)))
S.at(35.7, scene("S11c_defence", zoom=((887, 443, 887), (760, 380, 700))))
S.at(38.2, scene("S11d_prosecutor", zoom=((887, 443, 887), (900, 360, 720))))

# P41 · in the gallery
m = Marks()
sg.leader(m, (860, 500), (380, 140), "reportedly: Andrew Carnegie", 43.4, size=34)
S.at(41.3, scene("S11e_carnegie", zoom=((887, 443, 887), (900, 420, 740)), marks=m))
S.at(47.0, scene("S11f_note_pov", zoom=((887, 443, 887), (1050, 330, 640))))
S.at(51.0, scene("S11e_carnegie", zoom=((900, 420, 740), (900, 380, 520)), act=dict(expr=[(52.4, 54.8, "smile", None)])))

# P42 · guilty
gavel = Draw("X09_end", 0, (1480, 160), 160, (56.2, 56.9), (56.9, 57.2), card=True)
S.at(55.4, scene("S11g_verdict", zoom=((887, 443, 887), (1000, 420, 760)), draws=[gavel]))
b.fx("knock", 57.0, db=-10)
m = Marks()
m.typed("+ a $70,000 fine", (1240, 360), 40, 62.1, color="cream")
S.at(59.8, scene("S11h_verdict_face", "face", act=dict(expr=[(60.0, 64.4, "wobble", None)]), marks=m,
                 post=[stamp("14 YEARS", (1360, 230), 60.8, size=110, b=b)]))

# P43 · the bankers
S.at(64.6, scene("S11i_beckwith_home", zoom=((887, 443, 887), (760, 420, 720))))
S.at(70.2, scene("S11j_spear", zoom=((887, 443, 887), (880, 420, 720)), fx=[("fade_out", b.end - 0.6, b.end)]))
S.end()

if __name__ == "__main__":
    b.render()
