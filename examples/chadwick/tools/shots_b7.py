"""b7 · Queen of Ohio, and the fall begins (P32-P37): the ledger, the spending, the parties; Newton, Carnegie's answer,
the run on the Oberlin bank. The dinner shatters into Brookline."""
from chad import *

b = Batch("b7")
S = Seq(b)

# P32 · the ledger: lenders on the right page, what it bought drawn on the left
m = Marks()
for i, (txt, t) in enumerate((("Citizens National Bank, Oberlin", 0.3), ("Wade Park Bank, Cleveland", 0.8),
                              ("Herbert Newton, Brookline", 1.3), ("... and bank after bank", 1.8))):
    m.typed(txt, (1010, 200 + 62 * i), 30, t, color="ink")
m.typed("about $2,000,000", (1010, 520), 50, 5.0, color="red")
m.typed("(about $70 million today)", (1010, 600), 34, 8.0, color="ink")
neck = Draw("X07_queen", 0, (330, 300), 300, (6.0, 6.8), (6.8, 7.1))
organ = Draw("X07_queen", 1, (640, 320), 360, (6.9, 7.8), (7.8, 8.1))
gown = Draw("X07_queen", 2, (330, 640), 300, (8.0, 8.8), (8.8, 9.1))
coach = Draw("X07_queen", 3, (660, 690), 220, (9.0, 9.9), (9.9, 10.2))
ctr = Counter([(2.4, 0), (5.2, 2_000_000)], pos=(0.77, 0.86), label="borrowed, in all", size=1.15)
S.at(0.0, page("B04_ledger", [neck, organ, gown, coach], marks=m, post=[ctr], trans=("dissolve", 0.4)))

# P33 · and she spent it
S.at(11.0, scene("S09f_jeweller", zoom=((887, 443, 887), (960, 400, 700))))
S.at(13.8, scene("S09g_dressmaker", zoom=((887, 443, 887), (800, 430, 760))))
S.at(15.4, scene("S09h_closets", zoom=((887, 443, 887), (1000, 420, 720))))
S.at(17.0, scene("S09i_organ", zoom=((887, 443, 887), (1050, 420, 700))))

# P34 · the parties
S.at(21.4, drawin("S09j_dinner", zoom=((887, 443, 887), (880, 420, 720)), ink=(0.0, 1.4), flood=(1.1, 2.4)))
b.fx("fire", 21.4, 25.4, db=-24)
S.at(25.4, scene("S09k_gift", zoom=((887, 443, 887), (820, 470, 640))))
m = Marks()
m.typed("\"the Queen of Ohio\"", (1120, 120), 44, 27.45)
S.at(27.4, scene("S09m_queen_face", "face", act=dict(expr=[(27.6, 29.4, "smile", None)]), marks=m))
S.at(30.0, scene("S09l_christmas", zoom=((887, 443, 887), (820, 430, 760))))
S.at(31.8, scene("S09n_night", zoom=((887, 443, 887), (800, 420, 720))))

# P35 · Newton (the queen's world shatters)
S.at(37.9, scene("S10a_brookline", "in", label="Brookline, Massachusetts · 1904", label_at=0.9, trans=("shatter", 1.25, (0.45, 0.42))))
b.fx("smash", 38.3, db=-6)
m = Marks()
sg.leader(m, (1050, 230), (1250, 110), "Herbert Newton", 43.3, size=34)
m.typed("$190,000", (1180, 520), 54, 45.0, color="red")
S.at(43.0, scene("S10b_newton", zoom=((887, 443, 887), (960, 360, 700)), marks=m))
S.at(47.6, scene("S10b_newton", zoom=((960, 360, 700), (1020, 300, 520)), act=dict(widen=[(49.2, 50.4, 0.2)])))
S.at(51.0, scene("S10c_court_clerk", zoom=((887, 443, 887), (700, 470, 720)), label="November 1904", label_at=0.3))

# P36 · Carnegie's answer
S.at(55.4, scene("S10e_reporters", zoom=((887, 443, 887), (900, 420, 760)), fx=[("flash", [(56.9, (0.5, 0.42))])]))
b.fx("shutter", 56.9, db=-10)
S.at(58.0, scene("S10d_telegram", zoom=((887, 443, 887), (860, 470, 700))))
S.at(59.4, scene("S10f_carnegie_office", zoom=((887, 443, 887), (700, 440, 720))))
m = Marks()
m.typed("Mr. Carnegie does not know", (180, 470), 44, 61.6, color="ink")
m.typed("Mrs. Chadwick of Cleveland.", (180, 540), 44, 62.3, color="ink")
m.typed("He has not signed a note", (180, 650), 44, 63.4, color="ink")
m.typed("in more than thirty years.", (180, 720), 44, 63.8, color="ink")
tele = Draw("X08_fall", 0, (1380, 230), 160, (61.6, 62.4), (62.4, 62.7))
S.at(61.5, page("B06_telegram", [tele], marks=m))
S.at(66.9, scene("S10g_carnegie_face", "face", act=dict(expr=[(66.8, 69.0, "smile", None)])))

# P37 · the run
S.at(69.1, scene("S10h_run", zoom=((887, 443, 887), (820, 470, 720))))
b.fx("wav", 69.1, 74.8, db=-15, path=str(film.ROOT / "audio" / "walla" / "crowd_bank.wav"))
b.fx("knock", 71.6, db=-18)
S.at(74.6, scene("S10i_empty", zoom=((887, 443, 887), (1000, 470, 720)), post=[stamp("CLOSED", (1180, 220), 80.3, b=b)]))
S.at(80.6, scene("S10j_beckwith_face", "face", act=dict(expr=[(80.8, 84.0, "frown", "half")]), fx=[("fade_out", b.end - 0.6, b.end)]))
S.end()

if __name__ == "__main__":
    b.render()
