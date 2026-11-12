"""b5 · The lie (P22-P25): the chance meeting (comic page), inside the house, the secret, why nobody could check it."""
from chad import *

b = Batch("b5")
S = Seq(b)

# P22 · the chance meeting, as a comic page
P1, P2, P3, P4 = (60, 50, 1010, 430), (1035, 50, 1714, 430), (60, 455, 690, 837), (715, 455, 1714, 837)


def meeting(b, t0, t1):
    comic = sg.Comic("B09_board", [
        dict(box=P1, img="S07a_holland", focus=(887, 420, 700), t=(0.2, 0.6, 1.3)),
        dict(box=P2, img="S07b_lobby", focus=(1000, 380, 640), t=(3.4, 3.9, 4.6)),
        dict(box=P3, img="S07c_favour", focus=(880, 360, 620), t=(11.5, 11.9, 12.4)),
        dict(box=P4, img="S07d_ride", focus=(887, 380, 600), t=(14.3, 14.7, 15.2)),
    ], border_t=(0.0, 0.8))
    cm = Marks()
    cm.typed("New York · around 1902", (90, 80), 34, 1.6)
    sg.leader(cm, (1520, 150), (1300, 400), "Dillon, the lawyer", 9.4, size=30)
    b.custom(t0, comic, [(t0, 887, 443, 887), (1.0, 540, 240, 520), (3.1, 540, 240, 520), (3.6, 1375, 240, 520), (11.2, 1375, 240, 520),
                         (11.7, 375, 646, 520), (14.0, 375, 646, 520), (14.5, 1214, 646, 560), (t1 - 1.3, 1214, 646, 560), (t1, 887, 443, 887)],
             "B09_board", marks=cm)


S.at(0.0, custom(meeting))
S.at(17.0, scene("S07e_mansion", zoom=((887, 443, 887), (900, 360, 700))))

# P23 · inside the house
S.at(19.5, scene("S07f_hall", zoom=((887, 443, 887), (900, 400, 740))))
S.at(23.4, scene("S07g_housekeeper_face", "face", act=dict(glances=[(25.0, 27.0, -8, 0)])))
m = Marks()
m.typed("nearly half an hour...", (330, 240), 44, 28.0)
S.at(27.6, scene("S07f_hall", zoom=((900, 400, 740), (700, 470, 640)), marks=m))
S.at(33.0, scene("S07h_muff", zoom=((887, 443, 887), (760, 600, 600))))
b.fx("paper", 34.3, 34.9, db=-14)
S.at(36.4, scene("S07i_wave", zoom=((887, 443, 887), (800, 430, 760))))
b.fx("door", 39.6, db=-18)

# P24 · the secret
S.at(40.6, scene("S07j_secret", zoom=((887, 443, 887), (860, 380, 720))))
S.at(46.2, scene("S07k_cassie_tears", "face", act=dict(glances=[(46.5, 48.0, -6, 4)])))
photo(b, "carnegie_1905.jpg", 47.6, 50.6, pos=(0.26, 0.45), height=0.62, credit=CREDIT["carnegie_1905.jpg"], tilt=3.0)
carn = Draw("X05_carnegie", 0, (330, 470), 520, (51.0, 52.6), (52.6, 53.2))
notes = Draw("X02_forger", 3, (860, 400), 300, (52.8, 54.0), (54.0, 54.4))
m = Marks()
m.arrow((470, 360), (690, 380), 52.7, 0.3, color="red")
m.typed("$7,000,000 more in notes", (700, 610), 44, 54.6)
m.typed("to inherit: $400,000,000", (700, 700), 44, 58.0, color="red")
S.at(50.9, page("B02_card", [carn, notes], marks=m))
S.at(61.6, scene("S07l_dillon_oath", "face", act=dict(expr=[(61.9, 64.6, "flat", None)])))

# P25 · nobody could check it
S.at(65.0, scene("S07d_ride", zoom=((887, 443, 887), (700, 380, 680))))
conv = Draw("X05_carnegie", 1, (420, 420), 380, (69.6, 71.0), (71.0, 71.5))
lib = Draw("X05_carnegie", 2, (900, 430), 330, (72.8, 74.2), (74.2, 74.6))
man = Draw("X05_carnegie", 3, (1360, 430), 340, (75.6, 77.0), (77.0, 77.4))
m = Marks()
m.typed("steel", (360, 680), 44, 71.3)
m.typed("libraries", (820, 680), 44, 74.0)
m.typed("married at 51", (1240, 680), 44, 76.2)
S.at(69.2, page("B02_card", [conv, lib, man, Sparkle([(470, 470), (430, 520), (500, 560)], t0=70.4, t1=78.8, size=12)], marks=m))
S.at(78.8, scene("S07e_mansion", zoom=((887, 443, 887), (1050, 470, 600))))
photo(b, "carnegie_mansion_1902.jpg", 79.6, 83.4, pos=(0.27, 0.42), height=0.5, credit=CREDIT["carnegie_mansion_1902.jpg"], tilt=-2.5)
b.fx("knock", 82.0, db=-16)
S.end()

if __name__ == "__main__":
    b.render()
