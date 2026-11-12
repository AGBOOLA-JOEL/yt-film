"""b4 again, the v2 way (Nov 2026): the same pictures and voice as shots_b4.py, with camera moves that have a purpose,
pulled focus, weather in depth, lit faces, paper tags, an inset on a pinned scrap and a card that fills the frame.
This is the reference for new films. It needs depth maps (python tools/depth.py) and, for the pauses, in voice.py:

    BEATS = {"P19": [("She fainted", 0.5), ("He believed", 0.6)], "P20": [("In 1897", 0.3), ("was now", 0.35)],
             "P21": [("But Euclid", 0.4), ("She didn't", 0.8), ("She was planning", 0.6)]}

Every time below is taken from the narration by phrase, so the shot list follows the voice wherever the beats land.
"""
from chad import *
import seq
seq.LIVE.update(LIVE)                 # chad.py keeps its own older builders; the v2 ones come from the engine's seq
from seq import Seq, scene, drawin, page, Focus, Haze, Snow, Rain, FaceLight, Scrap, Tag, tag

b = Batch("b4")
b.music = ("c_cleveland", 90.8)       # preview only (final.py does the real score): the cue carries on from batch 3
S = Seq(b)
T = b.t
t_house, t_evening, t_name, t_kind = T("a house where"), T("One evening"), T("His name"), T("He was kind")
t_real = T("realized")
t_faint, t_beaut, t_round = T("She fainted"), T("beautifully"), T("When she came")
t_teach, t_believed = T("She was only"), T("He believed")
t_1897, t_married, t_euclid, t_row, t_rock = T("In 1897"), T("they married"), T("Euclid Avenue"), T("Millionaire's"), T("Rockefeller")
t_betsy, t_rail, t_now, t_cassie = T("Betsy Bigley"), T("the railwayman's"), T("was now"), T("Cassie Chadwick")
t_but, t_stranger, t_neigh, t_invited, t_didnt = T("But Euclid"), T("a stranger"), T("The neighbors"), T("When she invited"), T("they didn't")
t_behind, t_watched, t_she, t_plan = T("Behind their"), T("watched her"), T("She didn't"), T("She was planning")
END = b.end

# ---- P18 · the house on the west side: pull back from the lit door to the whole street; the rain falls in depth
S.at(0.0, scene("S05a_westside", cam=lambda a, z: [(a, 800, 470, 470), (z - 0.3, 887, 443, 860, "out")],
                haze=(0.20, (128, 134, 158)), label="Cleveland · 1893"))
b.fx("rain", 0.0, t_house + 0.4, db=-20)

# the parlour: ONE move (sofa -> Cassie -> the doctor at the door) with the focus pulled along it; no cut inside a picture
S.at(t_house, scene("S05b_parlour", light=(640, 520),
                    cam=lambda a, z: [(a, 430, 400, 520), (t_evening - 0.3, 1050, 380, 600, "io"), (t_evening, 1050, 380, 600),
                                      (t_name - 0.3, 1300, 320, 520, "out"), (z, 1310, 315, 490, "lin")],
                    focus=[(t_house, (400, 400), 0.8), (t_house + 1.6, (400, 400), 0.8), (t_evening - 0.4, (1138, 440), 0.8),
                           (t_evening + 0.2, (1138, 440), 0.8), (t_name - 0.4, (1493, 320), 0.9)]))
# his name stays up across the cut to his face: a tag is screen-space, so it can be an overlay like a footnote card
b.overlay(tag(b, "Dr. Leroy Chadwick", t_name - 0.1, t_kind + 2.4), t_name - 0.1, t_kind + 2.8)

# his face: looser, lit from the lamp, a slow drift and one push on "realized"
S.at(t_kind - 0.1, scene("S05c_leroy_face", light=(300, 240), focus=(950, 330),
                         cam=lambda a, z: [(a, 887, 443, 887), (t_real - 0.1, 930, 410, 780, "io"),
                                           (t_real + 0.55, 950, 365, 610, "out"), (z, 950, 360, 585, "lin")],
                         act=dict(widen=[(t_real, t_real + 2.2, 0.25)], expr=[(t_real + 0.1, t_real + 2.8, "o", None)])))

# ---- P19 · the faint: tight on the two of them, then out to the whole room on "beautifully"
S.at(t_faint - 0.15, scene("S05d_faint", light=(640, 520), shake=[(t_faint + 0.35, 5)],
                           cam=lambda a, z: [(a, 1120, 330, 540), (t_beaut - 0.05, 1125, 325, 500, "lin"), (z, 887, 443, 880, "out")],
                           focus=[(t_faint, (1200, 330), 0.7), (t_beaut, (1200, 330), 0.7), (t_beaut + 0.5, (1200, 330), 0.15)]))
b.fx("thud", t_faint + 0.38, db=-24)

# she explains; the focus goes over to him as he listens and stays on him for "He believed her."
S.at(t_round - 0.06, scene("S05e_explains", light=(798, 325),
                           cam=lambda a, z: [(a, 1280, 400, 620), (t_teach - 0.5, 1300, 380, 560, "io"), (t_teach + 0.2, 1300, 380, 560),
                                             (t_teach + 2.0, 560, 400, 600, "io"), (z, 530, 385, 530, "lin")],
                           focus=[(t_round, (1345, 420), 0.8), (t_teach + 0.3, (1345, 420), 0.8), (t_teach + 1.7, (473, 420), 0.85)]))

# ---- P20 · the wedding: the ring on a pinned scrap (never a glowing oval)
S.at(t_1897 - 0.15, scene("S05f_wedding", light=(900, 100), focus=[(t_1897, (700, 420), 0.5)], label="1897", label_at=0.25,
                          cam=lambda a, z: [(a, 887, 443, 887), (t_married + 0.1, 900, 425, 770, "out"), (z, 905, 420, 745, "lin")],
                          draws=[Scrap((1268, 660), (205, 170), t_married),
                                 Draw("X03_names", 2, (1268, 670), 92, (t_married + 0.25, t_married + 1.05), (t_married + 1.05, t_married + 1.6))]))
b.fx("paper", t_married, t_married + 0.4, db=-14)

# Euclid Avenue draws itself, then the camera travels down the row
S.at(t_euclid - 0.2, drawin("S05g_euclid", ink=(0.0, 1.4), flood=(1.1, 2.3), label="Euclid Avenue, Cleveland",
                            cam=lambda a, z: [(a, 887, 443, 887), (a + 2.5, 887, 443, 860, "lin"), (t_rock - 0.1, 1100, 520, 610, "io"),
                                              (z, 1130, 525, 580, "lin")]))
photo(b, "chadwick_house.jpg", t_row - 0.1, t_rock + 0.7, pos=(0.27, 0.42), height=0.42, credit=CREDIT["chadwick_house.jpg"])

# the card fills the frame: the old name large, struck out; then the new one written across it
m = Marks()
m.typed("Betsy Bigley", (430, 215), 80, t_betsy)
m.typed("the railwayman's daughter", (434, 318), 42, t_rail)
m.stroke([(420, 222), (960, 212)], t_now - 0.45, 0.22, color="red", width=5)
m.stroke([(424, 322), (1010, 314)], t_now - 0.2, 0.22, color="red", width=4)
m.write("Mrs. Cassie L. Chadwick", (410, 540), (1420, 540), t_now + 0.55, t_cassie + 0.7 - (t_now + 0.55), size=92)
sg.underline(m, (410, 600), (1400, 600), t_cassie + 0.85, color="red")
S.at(t_betsy - 0.2, page("B02_card", marks=m, cam=lambda a, z: [(a, 850, 300, 500), (t_now - 0.3, 860, 310, 520, "lin"),
                                                                (t_now + 0.7, 905, 395, 650, "out"), (z, 905, 400, 625, "lin")]))

# ---- P21 · the stranger: from her to the servants watching from the steps
S.at(t_but - 0.2, scene("S05h_arrives", cam=lambda a, z: [(a, 800, 500, 640), (z, 1150, 500, 520, "io")],
                        focus=[(t_but, (917, 560), 0.7), (t_stranger - 0.2, (917, 560), 0.7), (t_stranger + 0.8, (1400, 520), 0.6)]))
S.at(t_neigh - 0.1, scene("S05i_neighbours", cam=lambda a, z: [(a, 900, 420, 760), (z, 1060, 345, 520, "out")], focus=(1080, 340)))
S.at(t_invited - 0.1, scene("S06a_tea", cam=lambda a, z: [(a, 902, 420, 440), (z, 887, 443, 880, "out")]))   # out: every chair is empty
S.at(t_didnt - 0.1, scene("S06c_cards", cam=lambda a, z: [(a, 760, 440, 640), (z, 960, 450, 640, "lin")]))

# behind the curtains: one lady, the other, then through the glass to the snow outside (the only place it falls)
S.at(t_behind - 0.06, scene("S06d_window", light=(887, 300), snow_z=(0.0, 0.12),
                            cam=lambda a, z: [(a, 560, 330, 560), (t_watched - 0.3, 1180, 340, 560, "io"), (t_watched, 1180, 340, 560),
                                              (t_watched + 1.5, 900, 330, 440, "io"), (z, 895, 325, 410, "lin")],
                            focus=[(t_behind, (443, 300), 0.8), (t_watched - 1.3, (443, 300), 0.8), (t_watched - 0.4, (1271, 300), 0.8),
                                   (t_watched + 0.1, (1271, 300), 0.8), (t_watched + 1.2, 0.02, 0.9)]))

# her face in the pause, then the mouth sets on "She didn't."
S.at(t_she - 0.3, scene("S06b_hurt_face", light=(150, 300), focus=(931, 355),
                        cam=lambda a, z: [(a, 900, 430, 800), (z, 925, 400, 690, "out")],
                        act=dict(expr=[(t_she + 0.45, t_plan + 0.85, "flat", None)])))
S.at(t_plan - 0.15, scene("S06e_dusk", haze=(0.18, (150, 150, 182)), cam=lambda a, z: [(a, 887, 443, 887), (z, 960, 440, 660, "lin")],
                          fx=[("fade_out", END - 0.7, END)]))
b.fx("wind", t_plan - 0.15, END, db=-20)
S.end()

if __name__ == "__main__":
    b.render()
