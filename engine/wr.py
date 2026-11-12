"""Shot helpers for a film's batches , on top of film.py / kit.py / signature.py.

    sc(b, t0, t1, img, move, ...)   a scene: camera move by name (kit.MOVES) or ((cx, cy, h), (cx, cy, h)); every egg
                                    face in it acts (blinks; `act=` cues go to the biggest face); `live=` living areas
                                    (signature.Flow), `post=` frame touches, `marks=`, `fx=`, `trans=`, `text=` label
    note(b, t0, t1, n, title, lines, prev_img, prev_keys)   a footnote: a red superscript on the shot it belongs to is
                                    added by the caller; the narrator's hand slides the note up, then the note writes itself
    comic(b, t0, panels, ...)       a comic page on B09 (signature.Comic) with the camera visiting each panel and diving
                                    into the last
"""
import film
import kit
import signature as sg
from film import Marks

HAND = sg.host_file(film.INC / "01_cast" / "hand.png", "hand.png")
NOTE = sg.pad_to_canvas(sg.host_file(film.INC / "04_bases" / "B10_note.png", "note.png"), "B10_note_pad")
# (the ending: the like/follow line plays over the last story shot, then the cta batch follows; an extra host scene
#  before it adds nothing)


def keys_of(move, t0, t1):
    return kit.cam(move, t0, t1)


# script words that give the main face an expression (mouth, eyes): at most one per shot, held to the shot's end
CUES = {("laugh", "laughed", "laughing"): ("laugh", "happy"),
        ("smile", "smiled", "smiling", "cheering", "cheer", "hero", "friend", "toast", "hope", "hoped", "polite"): ("smile", None),
        ("freezes", "froze", "freeze", "fear", "frightened", "scared"): ("o", None),
        ("nervous", "desperate"): ("wobble", None),
        ("sick",): ("grimace", "squint"),
        ("caught", "stunned", "crashed", "shocked", "inside"): ("o", None),
        ("drunk", "bottle"): (None, "half"),
        ("debts", "bills", "changed", "worried", "stern", "nothing"): ("frown", None),
        ("asleep", "sleeping"): (None, "closed")}
MIN_HEAD = 110  # faces narrower than this (source px) are too small for an expression to read


def auto_expr(b, t0, t1, img):
    """The first cue word spoken during the shot, as an expr cue for its biggest face (or None)."""
    fs = sg.find_faces(img)
    if not fs or fs[0]["head"][2] - fs[0]["head"][0] < MIN_HEAD:
        return None
    for w in b.words:
        if t0 <= w["s"] <= t1 - 0.4:
            n = b._n(w["w"])
            for keys, (ms, es) in CUES.items():
                if n in keys and (ms is None or fs[0]["mouth"] is not None or ms in ("smile", "frown", "wobble", "grimace")):
                    return (w["s"], t1 + 1.0, ms if fs[0]["mouth"] is not None else None, es)
    return None


def sc(b, t0, t1, img, move="in", act=None, live=(), src=(), post=(), marks=None, fx=(), trans=None, text=None,
       faces=None, keys=None, react=(), talk=None, **kw):
    """react=[(kind, t), ...] reaction marks beside the main head; talk=(ta, tb): the main face mouths the narrator's
    words between ta and tb (a quoted line)."""
    k = keys or keys_of(move, t0, t1)
    # Rule: faces act only when this shot asks (act= / talk= / faces=True), never by default, and never
    # with automatic expressions from the narration
    if faces is None:
        faces = bool(act) or bool(talk)
    act = dict(act or {})
    if talk:
        act["talk"] = [(w["s"], w["e"]) for w in b.words if talk[0] <= w["s"] <= talk[1]]
    if react:
        fs = sg.find_faces(img)
        if fs:
            marks = marks or Marks()
            for kind, t_ in react:
                sg.react(marks, fs[0]["head"], kind, t_)
    sf = list(src) + list(live) + (sg.acting(img, seed=int(t0 * 10), **act) if faces else [])
    if text:
        marks = kit.label(text[0], text[1], keys=k, corner=text[2] if len(text) > 2 else "tl", marks=marks)
    if trans:
        kw["trans"] = trans
    b.scene(t0, img, k, src_fx=sf, post=list(post), marks=marks, fx=list(fx), **kw)
    return k


def note(b, t0, t1, n, title, lines):
    """The tea-stained note (B10) writing itself: red number, typed title, typed lines. Starts with the note pushing up
    out of a soft dissolve (the hand has just brought it)."""
    m = Marks()
    m.text(str(n), (415, 150), 80, t0 + 0.15, 0.3, color="red")
    m.typed(title, (490, 205), 54, t0 + 0.35, 0.4)
    span = max(0.3, (t1 - t0 - 1.4) / max(1, len(lines)))
    for i, ln in enumerate(lines):
        m.typed(ln, (430, 345 + i * 65), 40, t0 + 0.85 + i * span, min(0.6, span * 0.9))
    b.scene(t0, NOTE, [(t0, 887, 443, 860), (t1, 870, 420, 760)], marks=m, trans=("dissolve", 0.3))


def hand(t_in, t_out):
    return sg.Hand(HAND, t_in, t_out, x=0.8, height=0.58)


def marker(m, xy, n, t0):
    """The red superscript number that says: there's a footnote on this."""
    m.text(str(n), xy, 64, t0, 0.22, color="red")


READ_NOTE = 3.0  # seconds a footnote stays open after it has finished typing


def photo(b, name, t_in, t_out, pos=(0.7, 0.48), height=0.62, tilt=-3.0, credit=None, dim=0.25, sound=True):
    """A real archive photo as a period print over whatever shot is playing (an overlay), with a soft paper sound."""
    p = sg.Photo(name, t_in, t_out, pos=pos, height=height, tilt=tilt, credit=credit, dim=dim)
    b.overlay(p, t_in, t_out + 0.5)
    if sound:
        b.fx("paper", t_in, t_in + 0.5, db=-14)
    return p


def footnote(b, t_in, t_out, n, title, lines, side="right", pos=None, photo_name=None, credit=None):
    """A footnote card over the film from t_in, with its sounds (paper, typing). It stays up across cuts (an overlay)
    and is kept open until it has typed and been readable for READ_NOTE s, whatever t_out says. Keep it short:
    a title and 2-3 short lines. Returns the card (no need to put it in a shot's post=[...])."""
    card = sg.NoteCard(t_in, t_out, n, title, lines, side=side, pos=pos)
    card.t_out = max(t_out, t_in + 0.8 + card.total() * 0.045 + READ_NOTE)
    b.overlay(card, t_in, card.t_out + 0.6)
    b.fx("paper", t_in, t_in + 0.6, db=-6)
    b.fx("type", t_in + 0.75, t_in + 0.75 + card.total() * 0.045, db=-19)
    if photo_name:  # a small real photo pinned beside the card
        cx, cy = card.pos
        px = cx - 0.27 if cx > 0.5 else cx + 0.27
        p = sg.Photo(photo_name, t_in + 1.0, card.t_out, pos=(px, cy + 0.08), height=0.4, tilt=4 if cx > 0.5 else -4,
                     credit=credit, dim=0.0)
        b.overlay(p, t_in + 1.0, card.t_out + 0.5)
    return card
