"""b6 · The envelope (P26-P31): Wade Park, the seal, the receipt, the whisper, how it worked (drawn on the envelope),
Oberlin, Beckwith's own money."""
from chad import *

b = Batch("b6")
S = Seq(b)

# P26
S.at(0.0, scene("S08a_bank", "in", label="The Wade Park Bank, Cleveland", label_at=0.2))
m = Marks()
sg.leader(m, (1480, 200), (1180, 90), "Iri Reynolds", 7.3, size=34)
S.at(4.4, scene("S08b_office", zoom=((887, 443, 887), (1100, 400, 760)), marks=m))
S.at(10.0, scene("S08b_office", zoom=((1100, 400, 760), (1250, 470, 560))))
S.at(15.3, scene("S08c_seal", zoom=((887, 443, 887), (700, 560, 640))))
b.fx("stamp", 16.6, db=-12)

# P27
S.at(18.8, scene("S08d_receipt", zoom=((887, 443, 887), (900, 560, 660))))
S.at(21.6, scene("S08e_vault", zoom=((887, 443, 887), (1220, 470, 620))))
b.fx("bolt", 22.2, db=-14)
m = Marks()
m.typed("NOT TO BE OPENED", (250, 300), 56, 26.0, color="ink")
sg.tally(m, 250, 560, 24, 26.9, 29.6, h=60, gap=18, color="red", width=4)
m.typed("two years, unopened", (250, 680), 40, 28.2, color="ink")
S.at(25.4, page("B05_envelope", [], marks=m, zoom=((887, 443, 887), (800, 470, 820))))
S.at(30.8, scene("S08f_reynolds_face", "face", act=dict(expr=[(31.6, 34.0, "smile", None)])))
wr.footnote(b, 26.6, 34.4, 4, "Iri, not Ira", ["Iri Reynolds, secretary-treasurer of", "the Wade Park Bank. The papers",
                                                "often misspelled him as \"Ira\"."])

# P28 · the whisper
m = Marks()
sg.sound(m, (690, 300), 37.2, n=3, r0=26, step=22, arc=70, direction=180, color="auto")
S.at(34.3, scene("S08g_club", zoom=((887, 443, 887), (820, 400, 720)), marks=m))
m = Marks()
sg.sound(m, (470, 330), 40.4, n=3, r0=22, step=20, arc=60, direction=0, color="auto")
sg.sound(m, (1380, 350), 41.4, n=3, r0=22, step=20, arc=60, direction=180, color="auto")
S.at(39.6, scene("S08h_boardroom", zoom=((887, 443, 887), (887, 400, 760)), marks=m))

# P29 · how it worked, drawn on the envelope that hid it
notes = Draw("X02_forger", 3, (330, 250), 220, (46.4, 47.4), (47.4, 47.8))
rec = Draw("X02_forger", 1, (330, 620), 230, (49.6, 50.5), (50.5, 50.9))
vault = Draw("X06_envelope", 1, (870, 400), 300, (51.6, 52.8), (52.8, 53.3))
box = Draw("X06_envelope", 2, (870, 720), 150, (54.3, 55.1), (55.1, 55.4))
cash = Draw("X06_envelope", 3, (1360, 420), 220, (58.0, 58.9), (58.9, 59.3))
env = Draw("X06_envelope", 0, (620, 230), 150, (50.9, 51.5), (51.5, 51.8))


def chain_marks(fast=None):
    q = (lambda t: fast) if fast is not None else (lambda t: t)
    m = Marks()
    sg.cross(m, (200, 140, 470, 360), q(48.9))
    m.typed("the notes: never shown", (170, 400), 36, q(49.0), color="ink")
    m.typed("the receipt", (240, 770), 36, q(50.6), color="ink")
    m.arrow((470, 600), (700, 470), q(51.2), 0.35, color="red")
    m.typed("a respectable bank", (720, 590), 36, q(53.1), color="ink")
    m.typed("\"Carnegie's paper\"", (980, 760), 36, q(55.5), color="ink")
    m.arrow((1030, 400), (1230, 410), q(57.8), 0.3, color="red")
    m.typed("loans, high interest", (1190, 570), 36, q(59.4), color="ink")
    m.typed("+ a bonus", (1190, 620), 36, q(60.3), color="ink")
    return m


S.at(45.4, page("B05_envelope", [notes, rec, env, vault, box, cash], marks=chain_marks()))
S.at(62.6, scene("S08i_desk", zoom=((887, 443, 887), (1100, 420, 700))))
S.at(66.0, scene("S08j_banker_face", "face", act=dict(expr=[(66.3, 68.8, "grin", "happy")])))
done = [Draw(d_[0], d_[1], d_[2], d_[3], (69.0, 69.05), (69.05, 69.1)) for d_ in
        (("X02_forger", 3, (330, 250), 220), ("X02_forger", 1, (330, 620), 230), ("X06_envelope", 0, (620, 230), 150), ("X06_envelope", 1, (870, 400), 300),
         ("X06_envelope", 2, (870, 720), 150), ("X06_envelope", 3, (1360, 420), 220))]
m = chain_marks(fast=69.0)
m.arrow((1360, 560), (420, 720), 70.2, 0.9, color="red", bend=-0.35)
m.typed("the next banker... and the next", (900, 830), 40, 70.6, color="red")
S.at(69.0, page("B05_envelope", done, marks=m, trans=None, zoom=((887, 443, 887), (887, 470, 860))))

# P30 · Oberlin
S.at(73.4, scene("S09a_oberlin", "in", label="Oberlin, Ohio", label_at=0.2))
m = Marks()
sg.leader(m, (390, 210), (180, 90), "Charles Beckwith", 80.6, size=34)
sg.leader(m, (590, 260), (700, 110), "Spear", 81.4, size=34)
S.at(78.2, scene("S09b_beckwith_office", zoom=((887, 443, 887), (700, 400, 760)), marks=m))
S.at(84.2, scene("S09c_beckwith_face", "face", act=dict(expr=[(84.3, 85.6, "grin", "happy")])))
S.at(85.8, scene("S09d_counting", zoom=((887, 443, 887), (1000, 470, 680))))

# P31 · his own money
S.at(88.0, scene("S09e_own_money", zoom=((887, 443, 887), (700, 470, 720))))
own = Counter([(94.6, 0), (96.4, 100_000)], pos=(0.74, 0.18), label="his own savings", size=1.15)
S.at(92.6, scene("S09e_own_money", zoom=((700, 470, 720), (900, 560, 560)), post=[own], fx=[("fade_out", b.end - 0.6, b.end)]))
S.end()

if __name__ == "__main__":
    b.render()
