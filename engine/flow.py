"""Story-flow checks for a batch (Grant film, Nov 2026), run by Batch.check() before every render:

  - a picture alone: more than HOLD_BARE seconds inside one shot with nothing new drawn, typed, lifted or opened
    (camera moves, living layers and face acting don't count). Draw on it, or cut to the next shot or a drawing.
  - a seam to black: a fade out at the end of the batch or a fade in at its start. Batches are cuts for the
    computer, not chapters; the film may dip to black only at its 2-3 act breaks. Set `b.act_break = True` in the
    shots file of a batch whose end (or start) really is one; the first batch may fade in.

A deliberate long hold (a silent beat on a face before a reveal) is allowed by naming the picture:
`b.long_holds = {"S13j_dawn"}`. Use it rarely.

  - slanted writing: free handwriting more than MAX_SLANT degrees off level.

See references/storytelling.md (sections 5 and 6).
"""
HOLD_BARE = 6.0  # seconds a picture may sit with nothing new on it

_SKIP_KW = {"cam", "fx", "trans", "shake", "img", "ease", "swap", "act"}
_T_ATTR = {"t0", "t1", "t", "t_in", "t_out", "t_ink", "t_col", "type_t", "at_t"}


def _num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _times(o, depth=0, seen=None):
    """Every moment something appears, finishes or changes in `o` (marks, drawings, lifts, tags, panels, pages)."""
    seen = set() if seen is None else seen
    if depth > 4 or id(o) in seen or o is None or isinstance(o, (str, bytes)) or _num(o):
        return []
    seen.add(id(o))
    if isinstance(o, dict):
        it = o.items()
    elif isinstance(o, (list, tuple, set)):
        return [t for x in o for t in _times(x, depth + 1, seen)]
    else:
        d = getattr(o, "__dict__", None)
        if not d:
            return []
        it = d.items()
    out = []
    for k, v in it:
        if not isinstance(k, str) or k.startswith("__") or k in _SKIP_KW or k in ("cam", "keys_cam"):
            continue
        if k in _T_ATTR:
            if _num(v):
                out.append(float(v))
            elif isinstance(v, (list, tuple)) and all(_num(x) for x in v):
                out += [float(x) for x in v]
        elif k == "keys" and isinstance(v, (list, tuple)):
            out += [float(x[0]) for x in v if isinstance(x, (list, tuple)) and x and _num(x[0])]
        elif hasattr(v, "__dict__") or isinstance(v, (list, tuple, dict, set)):
            out += _times(v, depth + 1, seen)
    t0, dur = (getattr(o, "t0", None), getattr(o, "dur", None)) if not isinstance(o, dict) else (o.get("t0"), o.get("dur"))
    if _num(t0) and _num(dur):
        out.append(float(t0) + float(dur))
    return out


def bare_holds(b, shots, hold=HOLD_BARE):
    """[(shot, start, gap)] for every stretch longer than `hold` s inside a shot with nothing new on screen."""
    res = []
    for i, s in enumerate(shots):
        end = shots[i + 1].t0 if i + 1 < len(shots) else b.end
        if s.kw.get("img") in getattr(b, "long_holds", ()):  # a hold the film wants (a silent beat on a face)
            continue
        ts = []
        for k, v in s.kw.items():
            if k not in _SKIP_KW:
                ts += _times(v)
        if s.marks is not None:
            ts += _times(s.marks)
        for f, a, z in getattr(b, "overlays", []):
            ts += [a] + [t for t in _times(f)]
        ev = sorted({s.t0, end} | {t for t in ts if s.t0 < t < end})
        gaps = [(z - a, a) for a, z in zip(ev, ev[1:])]
        if gaps:
            g, a = max(gaps)
            if g > hold:
                res.append((s, a, g))
    return res


def seam_fades(b, shots):
    """Problems with fades at the batch's start or end (see the module notes)."""
    if getattr(b, "act_break", False) or not shots:
        return []
    out = []
    first, last = shots[0], shots[-1]
    if b.name != "b1":
        fx = [e for e in first.kw.get("fx", []) if isinstance(e, (list, tuple)) and e and e[0] == "fade_in"]
        if fx or (first.kw.get("trans") and first.t0 <= 0.05):
            out.append(f"{b.name} starts by fading in from black: start on a straight cut (the story continues from the "
                       f"last batch), or set b.act_break = True if this is one of the film's 2-3 act breaks")
    fo = [e for e in last.kw.get("fx", []) if isinstance(e, (list, tuple)) and e and e[0] == "fade_out"
          and len(e) > 2 and _num(e[2]) and e[2] >= b.end - 0.6]
    if fo:
        out.append(f"{b.name} ends by fading to black: end on a moving shot and let the next batch cut in, or set "
                   f"b.act_break = True if this is one of the film's 2-3 act breaks")
    return out


MAX_SLANT = 4.0  # degrees: free handwriting and labels sit level (words on a tilted object use Marks.write)


def slanted(b, shots, limit=MAX_SLANT):
    """Free handwriting at an angle (Marks.text / Page.text with angle=): it reads as sloppy. Words that belong on a
    line of the picture (a notebook rule, a printed row) go through Marks.write(a, b), which follows that line."""
    out = []
    for s in shots:
        items = list(s.marks.items) if s.marks is not None else []
        pg = s.kw.get("page")
        if pg is not None:
            items += list(getattr(pg, "items", []))
        for it in items:
            ang = getattr(it, "angle", 0) or 0
            if abs(ang) > limit:
                out.append(f"{b.name} {s.kw.get('img', s.kind)}: handwriting at {ang:.0f} degrees: keep it level (angle=0), "
                           f"or write it along the object's line with Marks.write(a, b)")
    return out


def check(b, shots, hold=HOLD_BARE):
    out = seam_fades(b, shots) + slanted(b, shots)
    for s, a, g in bare_holds(b, shots, hold):
        out.append(f"{b.name} {s.kw.get('img', s.kind)} at {a:.1f}s: {g:.1f}s with nothing new drawn (> {hold:.0f}s): "
                   f"draw on it while the narrator explains, or cut to the next shot")
    return out
