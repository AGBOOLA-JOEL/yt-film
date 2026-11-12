"""b9 · The end (P44-P49): her trunks, blindness, her fiftieth birthday, Woodstock, after, the paper; the end line.
The ending (cta, made by tools/cta.py) follows in final.py."""
import numpy as np

from chad import *

b = Batch("b9")
S = Seq(b)

# P44
trunk = Draw("X09_end", 1, (1250, 150), 200, (1.8, 2.8), (2.8, 3.2), card=True)
S.at(0.0, scene("S12a_trunks", zoom=((887, 443, 887), (900, 420, 760)), draws=[trunk], label="Ohio Penitentiary · January 1906", label_at=0.2))
m = Marks()
sg.leader(m, (260, 640), (140, 520), "her trunks", 8.0, size=34)
sg.leader(m, (900, 760), (700, 840), "her rugs", 8.8, size=34)
sg.leader(m, (620, 400), (760, 120), "her furniture", 9.3, size=34)
S.at(6.6, scene("S12b_cell", zoom=((887, 443, 887), (860, 450, 840)), marks=m))
S.at(11.9, scene("S12b_cell", zoom=((860, 450, 840), (760, 360, 600))))

# P45
S.at(14.1, scene("S12c_hospital", zoom=((887, 443, 887), (1000, 380, 680)), act=dict(expr=[(18.0, 19.5, None, "half")])))
her = Draw("X09_end", 3, (330, 300), 380, (20.0, 21.6), (21.6, 22.4), card=True, t_out=24.2)
S.at(19.6, scene("S12d_rings", zoom=((887, 443, 887), (800, 470, 680)), draws=[her]))
wr.footnote(b, 23.0, 31.0, 5, "Her fiftieth birthday", ["Born 10 October 1857 (by most", "accounts); died 10 October 1907",
                                                         "in the Ohio Penitentiary."], pos=(0.56, 0.19))


# P46 · Woodstock, and her whole road on the map
S.at(24.6, scene("S12e_woodstock", zoom=((887, 443, 887), (900, 420, 760)), label="Woodstock, Ontario · 1907", corner="bl", label_at=0.2))


route = ["Woodstock", "Cleveland", "Toledo", "Columbus", "Cleveland", "New York", "Cleveland", "Columbus", "Woodstock"]
wx, wy = P(*TOWNS["Woodstock"])
grave = Draw("X09_end", 2, (wx + 120, wy - 140), 170, (32.6, 33.4), (33.4, 33.8), card=True)
S.at(29.6, map_shot((29.6, 30.2), towns=[(n, 29.7 + 0.12 * i) for i, n in enumerate(["Woodstock", "Cleveland", "Toledo", "Columbus", "New York"])],
                    route=route, t_route=(30.0, 32.6), fast=True, extra=[grave]))


# P47 · after
S.at(34.0, scene("S12f_tourists", zoom=((887, 443, 887), (760, 420, 760))))
S.at(38.6, scene("S12g_oberlin_build", zoom=((887, 443, 887), (900, 400, 760)), label="Oberlin College", label_at=0.2))
wr.footnote(b, 40.4, 48.2, 6, "The Oberlin library", ["Carnegie paid for a library at Oberlin", "College. Whether it had anything to do",
                                                       "with her, nobody knows."], side="right")
S.at(44.4, scene("S12h_carnegie_reads", zoom=((887, 443, 887), (900, 380, 700)), act=dict(expr=[(45.0, 48.6, "smile", None)])))
m = Marks()
sg.underline(m, (960, 760), (1480, 760), 51.2, color="red")
S.at(49.0, scene("B01_note_written", zoom=((887, 443, 860), (1180, 640, 520)), marks=m, live=False, trans=("dissolve", 0.4)))

# P48 · the paper
S.at(55.0, scene("S12j_mansion_today", zoom=((887, 443, 887), (900, 470, 760))))
S.at(59.3, drawin("S01a_fifth_ave", zoom=((887, 443, 887), (905, 560, 700)), ink=(0.0, 2.2), flood=(1.8, 3.6)))
paper_ground = [(505, 690), (1100, 722), (1150, 770), (1140, 808), (530, 800), (500, 760)]
g = np.mean(paper_ground, 0)
land = Lift("S01e_paper_falls", paper_ground, [(65.6, 760, -170, -30, 1.15), (66.15, 900, 380, 16, 1.07), (66.65, g[0], g[1], 0, 1.0)],
            flutter=0.55, shadow=(10, 12, 0.4), fill_from=(655, 4))
S.at(65.5, scene("S01e_paper_falls", zoom=((887, 480, 840), (860, 560, 720)), extra=[land], fx=[("snow", 0.3)]))
b.fx("paper", 66.55, 66.9, db=-15)

# P49 · the end line over the last story shot
S.at(69.0, scene("S12i_pavement", zoom=((887, 443, 887), (1000, 470, 620)), fx=[("fade_out", b.end - 1.6, b.end)]))
S.end()

if __name__ == "__main__":
    b.render()
