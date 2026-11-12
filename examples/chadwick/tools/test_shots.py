"""The Chadwick effects and illustration test (60 s of narration + footnote tail): every animation style of the new
films on the real Chadwick images, after the audit (no pixel-warp effects, no four-up sheets, no long holds).

  S01a  particle smoke, horse and coachman breath, gas lamps with living flames and light, snow, a typed place
  S01b  the carriage lamp burning, its light breathing on the leather
  S01a  a proper drawing made on the picture: Carnegie inks himself in (pen) then the colour washes in, on a cream wash
  S01d  coal smoke from the chimneys, breath, the carriage lamp; she stumbles (shake, her eyes widen), the note slips
        from her muff and falls out of frame (cut out of the picture, the hole filled)
  S01e  the note tumbles down from above and lands on the pavement, with its shadow
  S01g  Dillon's eyes widen
  S01f  the note's words are written on its lines as he reads; then FORGED stamps onto it
  B02   how the con worked, drawn on a card: note -> sealed envelope -> vault -> receipt -> the next banker's loan,
        each a real drawing (ink, then colour) appearing as it's named, linked by arrows; no four-up sheet
  S09j  candles, chandelier and fireplace alive; a rolling money counter climbs to $2,000,000
  -> glass shatter -> S10b Newton reads the letter
  S10h  the run on the bank: snow, chimney smoke, lamps, a crowd murmur
  S10l  the forgeries; B01 the note (written) tears in two and falls apart; the footnote card over the torn halves

Narration: TEST_SCRIPT.md (tools/voice.py --test).    python tools/test_shots.py [--preview]
"""
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import film
import kit
import signature as sg
import sketch as sk
from film import Batch, Marks
from fx2 import Live, Smoke, Breath, Flame, Light, Lift, Draw, Tear, Counter, u8, clean_text
from kit import label
from wr import sc, footnote

b = Batch("test", tail=10.5)
T = b.t
END = b.end

t_ny, t_dylan, t_checking, t_woman = T("New York"), T("Dylan"), T("checking"), T("The woman")
t_andrew, t_mansion, t_hour = T("Andrew"), T("mansion"), T("hour", end=True)
t_when, t_stumbles, t_folded, t_slips, t_muff = T("When she"), T("stumbles"), T("folded"), T("slips"), T("muff", end=True)
t_picks, t_promise, t_two, t_dollars, t_andrew2, t_carnegie = T("Dylan picks"), T("I promise"), T("two"), T("dollars"), T("Andrew"), T("Carnegie", end=True)
t_forgery, t_worked = T("forgery"), T("worked")
t_note, t_sealed, t_env2, t_vault, t_receipt, t_next, t_lent, t_onit = (T("note went"), T("sealed"), T("The envelope"), T("bank vault"),
                                                                        T("receipt"), T("next banker"), T("lent"), T("on it", end=True))
t_by, t_borrowed, t_million, t_queen = T("By"), T("borrowed"), T("million"), T("queen", end=True)
t_then, t_asked, t_crowds, t_doors = T("Then"), T("asked"), T("Crowds"), T("doors", end=True)
t_and_when, t_opened, t_tore, t_two_end = T("And when"), T("opened"), T("tore"), T("two", end=True)

COAL, COAL_LIT = (104, 100, 104), (176, 170, 172)


# ---------------------------------------------------------------- Fifth Avenue: a living street
def street(t_a, t_b):
    """S01a's living layers: chimney smoke, breath, gas lamps, the carriage lamp."""
    return [Smoke((695, 58), rate=3, life=5, rise=26, wind=(16, -2), size=(12, 70), color=COAL, light=COAL_LIT, alpha=0.6, seed=2),
            Breath((588, 708), [t_a + 0.6, t_a + 2.4, t_a + 4.2, t_a + 6.0, t_b - 3.0, t_b - 1.2], direction=(-1, 0.12), seed=3),
            Breath((925, 596), [t_a + 1.5, t_a + 4.9, t_b - 2.2], direction=(-0.9, -0.35), size=(4, 26), seed=5),
            Flame((1486, 356), 10, light=dict(amount=0.22), seed=1), Flame((1571, 530), 7, light=dict(amount=0.18), seed=2),
            Flame((983, 672), 8, light=dict(amount=0.2), seed=3)]


k = [(0.0, 887, 443, 887), (t_checking, 905, 560, 640)]
m = label("New York, around 1902", 0.5, corner="tl", keys=k)
b.custom(0.0, Live("S01a_fifth_ave", street(0.0, t_checking)), k, "S01a_fifth_ave", marks=m, fx=[("snow", 0.45), ("fade_in", 0.6)])
b.fx("wind", 0.0, t_checking + 0.4, db=-15)

# the carriage: the lamp is alive
k = [(t_checking - 0.05, 887, 443, 887), (t_andrew, 850, 440, 820)]
b.custom(t_checking - 0.05, Live("S01b_dillon_waits", [Flame((200, 300), 24, light=dict(amount=0.32, flicker=0.5), seed=4)]),
         k, "S01b_dillon_waits")

# Carnegie drawn onto the street beside his mansion: a cream wash, the ink line, then the colour
DRAW_C = Draw("X05_carnegie", 0, (1585, 320), 380, (t_andrew + 0.2, t_andrew + 1.6), (t_andrew + 1.6, t_andrew + 2.3), card=True)
k = [(t_andrew - 0.05, 1170, 400, 770), (t_when - 0.2, 1190, 405, 730)]
m = Marks()
m.typed("Andrew Carnegie", (1468, 590), 34, t_andrew + 1.2)
m.arrow((1470, 420), (1240, 380), t_mansion + 0.1, 0.4, color="red", bend=-0.2)
b.custom(t_andrew - 0.05, Live("S01a_fifth_ave", street(t_andrew, t_when) + [DRAW_C]), k, "S01a_fifth_ave", marks=m,
         fx=[("snow", 0.35)])

# ---------------------------------------------------------------- she comes out; the note slips from her muff
paper_hand = [(975, 625), (1040, 612), (1058, 688), (992, 700)]
c = np.mean(paper_hand, 0)
slip = Lift("S01d_trip", paper_hand, [(t_slips - 0.05, c[0], c[1], 0, 1.0), (t_slips + 0.35, c[0] - 20, c[1] + 70, 25, 1.05),
                                     (t_slips + 1.0, c[0] - 60, 980, 80, 1.15)], flutter=0.5, shadow=(6, 10, 0.25),
            fill_from=(-95, 0))
d_items = [Smoke((1042, 112), rate=3, life=5, rise=30, wind=(10, -3), size=(10, 60), color=COAL, light=COAL_LIT, alpha=0.65, seed=7),
           Smoke((1138, 108), rate=3, life=5, rise=30, wind=(10, -3), size=(10, 60), color=COAL, light=COAL_LIT, alpha=0.65, seed=8),
           Breath((80, 570), [t_when + 0.3, t_when + 2.4, t_when + 4.4], direction=(-1, 0.05), seed=9),
           Flame((441, 390), 10, light=dict(amount=0.25), seed=5), slip]
k = [(t_when - 0.1, 887, 443, 887), (t_stumbles, 900, 470, 720), (t_muff + 0.3, 950, 520, 640)]
T_E = t_slips + 0.8
sc(b, t_when - 0.1, T_E, "S01d_trip", keys=k, src=u8(*d_items), act=dict(widen=[(t_stumbles, t_stumbles + 0.9, 0.25)]),
   fx=[("snow", 0.35)], shake=[(t_stumbles + 0.1, 7)])
b.fx("thud", t_stumbles + 0.1, db=-20)
b.fx("paper", t_slips, t_slips + 0.6, db=-11)

# the note lands on the pavement
paper_ground = [(505, 690), (1100, 722), (1150, 770), (1140, 808), (530, 800), (500, 760)]
g = np.mean(paper_ground, 0)
t_e = T_E
land = Lift("S01e_paper_falls", paper_ground, [(t_e, 760, -170, -30, 1.15), (t_e + 0.55, 900, 380, 16, 1.07),
                                              (t_e + 1.05, g[0], g[1], 0, 1.0)], flutter=0.55, shadow=(10, 12, 0.4),
            fill_from=(655, 4))
T_G = t_e + 1.45
b.scene(t_e, "S01e_paper_falls", [(t_e, 887, 480, 840), (T_G, 860, 560, 720)], src_fx=u8(land), fx=[("snow", 0.3)])
b.fx("paper", t_e + 0.95, t_e + 1.3, db=-15)

# ---------------------------------------------------------------- he reads it
t_g = T_G
T_F = t_g + 1.25
sc(b, t_g, T_F, "S01g_dillon_face", keys=[(t_g, 887, 443, 887), (T_F, 860, 380, 760)],
   src=u8(Flame((207, 245), 22, light=dict(amount=0.3), seed=6)), act=dict(widen=[(t_g + 0.15, T_F, 0.3)]))

NOTE = clean_text("S01f_reads", [[(405, 285), (1330, 285), (1330, 712), (405, 712)]])
m = Marks()
m.write("I promise to pay to the order of", (440, 345), (1300, 345), T_F + 0.05, t_two - T_F - 0.1, color="ink")
m.write("Mrs. Cassie L. Chadwick", (440, 425), (1040, 425), t_two - 0.05, 0.6, color="ink")
m.write("the sum of two million dollars", (440, 505), (1240, 505), t_two + 0.6, t_dollars - t_two - 0.2, color="ink")
m.write("$2,000,000.00", (440, 585), (800, 585), t_dollars + 0.1, 0.5, color="ink")
m.write("Andrew Carnegie", (930, 685), (1310, 685), t_andrew2 - 0.15, 0.85, size=62, color="ink")
k = [(T_F, 870, 470, 800), (t_forgery, 880, 480, 740), (t_worked, 880, 480, 760)]
b.scene(T_F, NOTE, k, marks=m, post=[sg.Stamp("FORGED", (1130, 560), t_forgery + 0.35, size=120, angle=-11)])
b.fx("stamp", t_forgery + 0.35, db=-4)

# ---------------------------------------------------------------- how it worked: drawn on a card, as it's said
t_c = t_worked - 0.1
note_d = Draw("X02_forger", 2, (330, 300), 190, (t_note - 0.1, t_note + 0.7), (t_note + 0.7, t_note + 1.15))
env_d = Draw("X06_envelope", 0, (790, 300), 205, (t_sealed - 0.2, t_sealed + 0.6), (t_sealed + 0.6, t_sealed + 1.05))
vault_d = Draw("X06_envelope", 1, (1300, 320), 290, (t_vault - 0.3, t_vault + 0.8), (t_vault + 0.8, t_vault + 1.3))
rec_d = Draw("X02_forger", 1, (1300, 650), 185, (t_receipt - 0.2, t_receipt + 0.55), (t_receipt + 0.55, t_receipt + 0.9))
cash_d = Draw("X06_envelope", 3, (720, 650), 165, (t_lent - 0.9, t_lent - 0.15), (t_lent - 0.15, t_lent + 0.2))
m = Marks()
m.typed("the note", (250, 440), 40, t_note + 0.5)
m.arrow((450, 300), (650, 300), t_sealed - 0.45, 0.3, color="red")
m.typed("sealed", (735, 440), 40, t_sealed + 0.3)
m.arrow((920, 305), (1120, 315), t_env2 + 0.4, 0.3, color="red")
m.typed("the vault", (1210, 498), 40, t_vault + 0.5)
m.arrow((1300, 480), (1300, 548), t_receipt - 0.5, 0.25, color="red")
m.typed("a receipt", (1405, 650), 40, t_receipt + 0.4)
m.arrow((1175, 650), (850, 650), t_next - 0.25, 0.35, color="red")
m.typed("the next banker", (880, 598), 36, t_next + 0.1)
m.typed("a loan", (668, 770), 40, t_lent - 0.3)
m.arrow((600, 640), (330, 420), t_lent + 0.25, 0.45, color="red", bend=0.35)
k = [(t_c, 887, 443, 887), (t_by, 887, 443, 860)]
b.custom(t_c, Live("B02_card", [note_d, env_d, vault_d, rec_d, cash_d]), k, "B02_card", marks=m, trans=("dissolve", 0.3))

# ---------------------------------------------------------------- like a queen: the dinner, alive, and the counter
dinner = [Light((828, 70), 170, amount=0.16, flicker=0.15, seed=1)]
for i, p in enumerate([(717, 540), (1020, 510), (798, 640), (998, 640), (1055, 545)]):
    dinner.append(Light(p, 55, amount=0.16, flicker=0.4, seed=10 + i))
for i, x in enumerate((62, 84, 104)):
    dinner.append(Flame((x, 535), 30 + 6 * (i % 2), light=dict(amount=0.18), seed=20 + i))
counter = Counter([(t_borrowed - 0.2, 0), (t_million + 0.6, 2_000_000)], pos=(0.79, 0.16), label="borrowed, 1902-1904", size=1.25)
k = [(t_by - 0.1, 887, 443, 887), (t_queen, 880, 410, 600)]
b.custom(t_by - 0.1, Live("S09j_dinner", dinner), k, "S09j_dinner", post=[counter], trans=("dissolve", 0.35))
b.fx("fire", t_by, t_then + 0.3, db=-22)
b.fx("type", t_borrowed - 0.1, t_million + 0.5, db=-24)

# ---------------------------------------------------------------- it all breaks
t_s = t_then - 0.3
sc(b, t_s, t_crowds - 0.15, "S10b_newton", keys=[(t_s, 887, 443, 887), (t_crowds, 980, 380, 650)],
   act=dict(widen=[(t_asked, t_asked + 1.0, 0.2)]), trans=("shatter", 1.25, (0.55, 0.4)))
b.fx("smash", t_s + 0.36, db=-6)

run = [Smoke((1022, 46), rate=3, life=5, rise=30, wind=(8, -3), size=(10, 60), color=COAL, light=COAL_LIT, alpha=0.6, seed=12),
       Light((470, 140), 50, amount=0.2, seed=3), Light((1205, 195), 50, amount=0.2, seed=4), Light((1680, 165), 50, amount=0.2, seed=5)]
k = [(t_crowds - 0.15, 887, 443, 887), (t_and_when, 820, 470, 720)]
b.custom(t_crowds - 0.15, Live("S10h_run", run), k, "S10h_run", fx=[("snow", 0.5)])
b.fx("wav", t_crowds - 0.15, t_and_when + 0.3, db=-15, path=str(film.ROOT / "audio" / "walla" / "crowd_bank.wav"))
b.fx("wind", t_crowds - 0.15, t_and_when + 0.3, db=-20)

b.scene(t_and_when, "S10l_forgeries", [(t_and_when, 887, 443, 887), (t_tore - 0.6, 940, 420, 720)])
b.fx("paper", t_opened, t_opened + 0.6, db=-12)


# ---------------------------------------------------------------- the note, torn in two
def written_note():
    out = film.BUILD / "edit" / "B01_note_written.png"
    if not out.exists():
        a = Image.open(film.find_img("B01_note")).convert("RGB")
        W, H = a.size
        sx, sy = W / 1670 * 1670 / 1774 * (1670 / W), 1.0  # engine px -> file px (same crop rule as film.up)
        crop = (H - round(W * 887 / 1774)) // 2
        f = W / 1774

        def P(x, y):
            return (x * f, y * f + crop)
        dr = ImageDraw.Draw(a)
        for txt, (x, y), size in [("I promise to pay to the order of Mrs. Cassie L. Chadwick", (330, 430), 44),
                                  ("the sum of two million dollars,  $2,000,000.00", (330, 530), 44),
                                  ("Andrew Carnegie", (980, 655), 70)]:
            font = ImageFont.truetype(sk.HAND, int(size * f))
            dr.text(P(x, y), txt, font=font, fill=(52, 40, 32))
        out.parent.mkdir(parents=True, exist_ok=True)
        a.save(out)
    return "B01_note_written"


NOTE2 = written_note()
t_n = t_tore - 0.6
k = [(t_n, 887, 443, 860), (END, 887, 455, 887)]
b.custom(t_n, Live(NOTE2, [Tear(NOTE2, t_tore - 0.05, x=900)]), k, NOTE2, trans=("dissolve", 0.25),
         post=[sg.Stamp("FORGED", (1180, 300), t_n + 0.2, size=90, angle=8)], fx=[("fade_out", END - 1.2, END)])
b.fx("stamp", t_n + 0.2, db=-8)
b.fx("rip", t_tore - 0.05, t_tore + 0.7, db=-8)
footnote(b, t_two_end + 0.5, END - 1.5, 1, "The carriage story",
         ["Dillon's own account, retold", "in the papers after her arrest.", "We only have his word for it."])

if __name__ == "__main__":
    b.render()
