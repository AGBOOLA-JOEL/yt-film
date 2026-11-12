"""b4 · Dr Chadwick (P18-P21): the house on the west side, the faint, Mrs. Chadwick of Euclid Avenue, nobody came."""
from chad import *

b = Batch("b4")
S = Seq(b)

# P18
S.at(0.0, scene("S05a_westside", zoom=((887, 443, 887), (820, 470, 760)), label="Cleveland · 1893", label_at=0.2))
b.fx("rain", 0.0, 5.4, db=-20)
S.at(5.4, scene("S05b_parlour", zoom=((887, 443, 887), (760, 470, 780))))
m = Marks()
sg.leader(m, (1320, 250), (880, 110), "Dr. Leroy Chadwick", 11.0, size=34)
S.at(10.6, scene("S05b_parlour", zoom=((760, 470, 780), (1150, 330, 620)), marks=m))
S.at(15.3, scene("S05c_leroy_face", "face", act=dict(widen=[(16.9, 19.0, 0.25)], expr=[(17.0, 19.6, "o", None)])))

# P19
S.at(20.2, scene("S05d_faint", zoom=((887, 443, 887), (1050, 400, 680)), shake=[(20.8, 4)]))
b.fx("thud", 20.85, db=-24)
S.at(24.6, scene("S05e_explains", zoom=((887, 443, 887), (1150, 420, 700))))
S.at(29.0, scene("S05e_explains", zoom=((1150, 420, 700), (860, 430, 680))))

# P20
S.at(31.9, scene("S05f_wedding", zoom=((887, 443, 887), (860, 400, 720)), label="1897", label_at=0.3))
S.at(35.6, drawin("S05g_euclid", zoom=((887, 443, 887), (820, 430, 800)), ink=(0.0, 1.6), flood=(1.3, 2.6),
                  label="Euclid Avenue, Cleveland"))
photo(b, "chadwick_house.jpg", 38.4, 40.8, pos=(0.74, 0.42), height=0.42, credit=CREDIT["chadwick_house.jpg"])
S.at(41.0, scene("S05h_arrives", zoom=((887, 443, 887), (980, 470, 720))))
m = Marks()
m.typed("Betsy Bigley", (240, 210), 40, 44.8, dur=0.2)
m.typed("Madame Lydia DeVere", (240, 280), 40, 44.8, dur=0.2)
m.typed("Marie LaRose", (240, 350), 40, 44.8, dur=0.2)
m.typed("Mrs. Hoover", (240, 420), 40, 44.8, dur=0.2)
for i, w in enumerate((420, 640, 470, 440)):
    sg.cross(m, (230, 190 + 70 * i, 230 + w, 235 + 70 * i), 45.0 + 0.12 * i, dur=0.12)
m.typed("Mrs. Cassie L. Chadwick", (240, 580), 70, 45.8)
sg.underline(m, (240, 620), (1180, 620), 47.0, color="red")
S.at(44.8, page("B02_card", [], marks=m))

# P21
S.at(49.0, scene("S05i_neighbours", zoom=((887, 443, 887), (900, 360, 680))))
S.at(54.4, scene("S06a_tea", zoom=((887, 443, 887), (780, 420, 720))))
S.at(56.0, scene("S06c_cards", zoom=((887, 443, 887), (900, 420, 760))))
S.at(57.4, scene("S06d_window", zoom=((887, 443, 887), (880, 400, 780))))
S.at(60.8, scene("S06b_hurt_face", "face", act=dict(expr=[(61.0, 62.9, "frown", None)])))
S.at(63.2, scene("S06e_dusk", zoom=((887, 443, 887), (900, 420, 760)), fx=[("fade_out", b.end - 0.7, b.end)]))
b.fx("wind", 63.2, b.end, db=-20)
S.end()

if __name__ == "__main__":
    b.render()
