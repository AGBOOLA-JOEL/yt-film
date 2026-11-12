"""b2 · Ontario (P05-P10): Betsy, the quiet one, the first letter, the heiress card, the faces, to Cleveland."""
from chad import *

b = Batch("b2")
S = Seq(b)

# P05
S.at(0.0, map_shot((0.2, 3.4), towns=[("Woodstock", 2.6)], zoom=((887, 443, 887), (820, 450, 840)), trans=None))
S.at(5.9, scene("S02a_town", "in", label="Ontario, Canada", label_at=0.1))
hand = Draw("X01_ontario", 1, (1060, 150), 170, (8.8, 10.0), (10.0, 10.6), card=True)
S.at(8.6, scene("S02b_father", zoom=((887, 443, 887), (900, 360, 760)), draws=[hand]))

# P06
S.at(12.8, scene("S02c_kitchen", zoom=((887, 443, 887), (600, 470, 700))))
S.at(16.9, scene("S02d_betsy_face", "face", act=dict(glances=[(18.6, 20.6, 9, 0)])))
girl = Draw("X01_ontario", 3, (560, 450), 560, (22.0, 24.0), (24.0, 24.8))
farm = Draw("X01_ontario", 0, (1200, 470), 440, (24.6, 26.3), (26.3, 27.1))
m = Marks()
m.typed("watched", (1040, 720), 40, 23.4)
m.typed("listened", (1040, 772), 40, 24.6)
m.typed("said little", (1040, 824), 40, 25.9)
S.at(21.9, page("B02_card", [girl, farm], marks=m))

# P07
S.at(28.3, scene("S02e_letter", zoom=((887, 443, 887), (700, 470, 680))))
m = Marks()
m.typed("\"...your uncle has died...\"", (1080, 90), 38, 32.6)
S.at(32.0, scene("S02f_letter_d", zoom=((887, 443, 887), (950, 400, 800)), marks=m))
ink = Draw("X02_forger", 0, (480, 430), 400, (36.2, 37.8), (37.8, 38.4))
lets = Draw("X02_forger", 1, (1220, 430), 420, (39.8, 41.4), (41.4, 42.0))
m = Marks()
m.arrow((720, 430), (960, 430), 39.0, 0.4, color="red")
m.typed("paper + the right words", (930, 720), 40, 41.2)
m.typed("= belief", (930, 775), 40, 43.6, color="red")
lamp = Draw("X01_ontario", 2, (250, 700), 200, (37.9, 38.7), (38.7, 39.0))
S.at(36.0, page("B02_card", [ink, lets, lamp], marks=m))

# P08
S.at(46.4, scene("S02g_woodstock", "in", label="Woodstock, Ontario · 1879"))
S.at(52.9, scene("S02h_card", zoom=((887, 443, 887), (1150, 360, 640))))
m = Marks()
m.typed("Miss Bigley,", (260, 330), 64, 57.2)
m.typed("Heiress to $15,000.", (260, 450), 72, 58.6)
card = Draw("X02_forger", 2, (520, 680), 200, (56.4, 57.2), (57.2, 57.6))
S.at(56.3, page("B02_card", [card], marks=m, zoom=((887, 443, 887), (860, 450, 830))))
wr.footnote(b, 59.6, 67.4, 2, "Heiress to $15,000", ["Her calling card, Woodstock, 1879,", "as quoted in later accounts.",
                                                      "Sources: pinned comment."])

# P09
S.at(62.4, scene("S02i_courtroom", zoom=((887, 443, 887), (760, 440, 720))))
S.at(66.6, scene("S02j_face_pull", "face", act=dict(expr=[(66.9, 68.7, "wobble", "squint")])))
S.at(69.1, scene("S02i_courtroom", zoom=((760, 440, 720), (887, 443, 860)), post=[stamp("NOT GUILTY", (420, 170), 70.6, size=100, b=b)]))

# P10
S.at(73.6, scene("S02k_train", "in"))
S.at(77.0, map_shot((77.0, 77.6), towns=[("Woodstock", 77.1), ("Cleveland", 77.6)], route=["Woodstock", "Cleveland"],
                    t_route=(77.5, 78.6), zoom=((887, 443, 887), (800, 480, 820)), fast=True))
S.at(80.4, scene("S03a_cleveland", "in", label="Cleveland, Ohio"))
S.end()

if __name__ == "__main__":
    b.render()
