"""Portrait reels (Shorts, Reels, TikTok): the overlays a phone film needs, on top of the same film engine.

Run a shot file with --portrait (or YTF_FORMAT=portrait, or a file `format` holding "portrait" in the project) and
film.py renders 1080 x 1920. Everything else is the engine you know: scenes, marks drawn on the picture, sketch sheets,
pages, weather, light, transitions, sound. This module adds what is special to a reel:

    import reel
    reel.captions(b, emph=["Caesar", "fifty"], fix={"farmakusa": "Pharmacussa"})   word-timed captions
    reel.badge(b, "1/4")                                                            episode badge, top right
    reel.headline(b, "THE WRONG PASSENGER", 0.2, 3.4, label="CAESAR AND THE PIRATES")
    reel.popup(b, "incoming/06_popups/cornelia.png", t, t + 2.4, "CORNELIA", "Caesar's wife")

Positions are fractions of the frame. SAFE is the part of a phone screen the apps leave clear: keep faces, labels and
captions inside it. All of these are plain overlays (f(img, t, shot, cam) -> img), so a film can write its own beside
them: that is the intended way to go past the base set (see references/creative.md).
"""
import re

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import film
import ytf
from film import OH, OW, S, ease

# the area apps leave clear, as frame fractions (x0, y0, x1, y1): top bar above, caption/likes column right and below
SAFE = (0.05, 0.115, 0.86, 0.74)
CAPTION_Y = 0.737  # top of the caption block (the Caesar reels: 1415 / 1920)
WHITE, GOLD, INK, RUST, CREAM = (255, 255, 255), (251, 198, 100), (26, 24, 22), (164, 63, 54), (250, 238, 212)


def _norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def put(img, rgba, x, y, k=1.0):
    """Lay an RGBA picture (uint8 array) on the frame at (x, y), clipped to the frame; k scales its opacity."""
    h, w = rgba.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(img.shape[1], x + w), min(img.shape[0], y + h)
    if x0 >= x1 or y0 >= y1 or k <= 0:
        return img
    p = rgba[y0 - y:y1 - y, x0 - x:x1 - x].astype(np.float32)
    a = p[..., 3:4] * (k / 255)
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a) + p[..., :3] * a
    return img


# ---------------------------------------------------------------- captions


class Captions:
    """Word-timed captions from the batch's own word timings: short phrases, white with a dark outline, the words
    in `emph` in gold. follow=True also lights the word being spoken. fix corrects what Whisper misheard
    ({"farmakusa": "Pharmacussa"}); mute=[(t0, t1), ...] leaves the captions off (under a headline, on a quiet beat).
    Phrases break at punctuation, at a pause, and before they get too long to read at a glance."""

    def __init__(self, words, emph=(), fix=None, follow=False, mute=(), y=CAPTION_Y, size=62, max_chars=26,
                 max_width=0.79, pause=0.45, hold=0.35, color=WHITE, hi=GOLD):
        fix = {_norm(k): v for k, v in (fix or {}).items()}
        self.emph = {_norm(w) for w in emph}
        self.follow, self.mute, self.y, self.color, self.hi = follow, list(mute), y, color, hi
        self.maxw = int(OW * max_width)
        self.font = ImageFont.truetype(ytf.font("bold"), max(8, int(size * S)))
        self.small = ImageFont.truetype(ytf.font("bold"), max(8, int(size * 0.855 * S)))
        ws = [dict(w=fix.get(_norm(w["w"]), w["w"]), s=w["s"], e=w["e"]) for w in words]
        self.phrases, cur = [], []
        for i, w in enumerate(ws):
            if cur and len(" ".join(x["w"] for x in cur)) + 1 + len(w["w"]) > max_chars:
                self.phrases.append(cur)
                cur = []
            cur.append(w)
            nxt = ws[i + 1]["s"] if i + 1 < len(ws) else None
            if w["w"][-1:] in ".,?!;:" or nxt is None or nxt - w["e"] > pause:
                self.phrases.append(cur)
                cur = []
        self.span = []
        for i, ph in enumerate(self.phrases):
            end = ph[-1]["e"] + hold
            if i + 1 < len(self.phrases):
                end = min(end, self.phrases[i + 1][0]["s"] - 0.02)
            self.span.append((ph[0]["s"] - 0.04, max(end, ph[-1]["e"])))
        self._cache = {}

    def _lines(self, ph, font):
        lines, cur = [], []
        for i, w in enumerate(ph):
            if cur and font.getlength(" ".join(ph[j]["w"] for j in cur + [i])) > self.maxw:
                lines.append(cur)
                cur = []
            cur.append(i)
        return lines + [cur]

    def _render(self, pi, active):
        key = (pi, active)
        if key in self._cache:
            return self._cache[key]
        ph = self.phrases[pi]
        font = self.font
        lines = self._lines(ph, font)
        if len(lines) > 2:  # a long phrase: the smaller size, as the Caesar captions fall back
            font = self.small
            lines = self._lines(ph, font)
        asc, desc = font.getmetrics()
        lh = int((asc + desc) * 1.08)
        pad = int(14 * S)
        im = Image.new("RGBA", (self.maxw + 2 * pad, lh * len(lines) + 2 * pad))
        d = ImageDraw.Draw(im)
        sw, so = max(1, int(4 * S)), max(1, int(4 * S))
        space = font.getlength(" ")
        for li, line in enumerate(lines):
            width = sum(font.getlength(ph[i]["w"]) for i in line) + space * (len(line) - 1)
            x, yy = (im.width - width) / 2, pad + li * lh
            for i in line:
                txt = ph[i]["w"]
                col = self.hi if (_norm(txt) in self.emph or (self.follow and i == active)) else self.color
                d.text((x, yy + so), txt, font=font, fill=(18, 17, 16, 150), stroke_width=sw * 2, stroke_fill=(18, 17, 16, 150))
                d.text((x, yy), txt, font=font, fill=col + (255,), stroke_width=sw, stroke_fill=INK + (255,))
                x += font.getlength(txt) + space
        a = np.asarray(im)
        if len(self._cache) > 40:
            self._cache.clear()
        self._cache[key] = a
        return a

    def __call__(self, img, t, s=None, cam=None):
        if any(a <= t <= b for a, b in self.mute):
            return img
        for pi, (a, b) in enumerate(self.span):
            if a <= t <= b:
                ph = self.phrases[pi]
                active = next((i for i, w in enumerate(ph) if w["s"] - 0.03 <= t <= w["e"] + 0.05), -1) if self.follow else -1
                im = self._render(pi, active)
                u = ease(min(1.0, (t - a) / 0.09), "out")  # a small rise as it lands
                return put(img, im, (OW - im.shape[1]) // 2, int(OH * self.y + (1 - u) * 10 * S), k=u)
        return img


def captions(b, t0=0.0, t1=None, **kw):
    """Captions for the whole batch (or from t0 to t1), from its word timings. Returns the Captions object."""
    c = Captions(b.words, **kw)
    b.overlay(c, t0, b.end if t1 is None else t1)
    return c


# ---------------------------------------------------------------- episode badge, headline


class Badge:
    """A small dark pill, top right: the episode number ("1/4") or a series mark."""

    def __init__(self, text, pos=(0.866, 0.076), size=30):
        font = ImageFont.truetype(ytf.font("mono_bold"), max(8, int(size * S)))
        w, h = int(font.getlength(text) + 44 * S), int(63 * S)
        im = Image.new("RGBA", (w, h))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), radius=int(14 * S), fill=(27, 42, 44, 215), outline=CREAM + (200,), width=max(1, int(2 * S)))
        d.text((w / 2, h / 2), text, font=font, fill=CREAM + (255,), anchor="mm")
        self.im, self.pos = np.asarray(im), pos

    def __call__(self, img, t, s=None, cam=None):
        return put(img, self.im, int(OW * self.pos[0] - self.im.shape[1] / 2), int(OH * self.pos[1] - self.im.shape[0] / 2))


def badge(b, text, **kw):
    f = Badge(text, **kw)
    b.overlay(f, 0.0, b.end)
    return f


class Headline:
    """The opening (or cliffhanger) headline: big condensed capitals that slide in and settle, a small series label
    above in typewriter rust. Lines wrap to the safe width. Cue it on the hook line and take it off before the first
    drawn mark so the two never fight."""

    def __init__(self, text, t0, t1, label=None, pos=(0.08, 0.15), size=112, max_width=0.8, color=CREAM):
        font = ImageFont.truetype(ytf.font("stamp"), max(8, int(size * S)))
        maxw = OW * max_width
        lines, cur = [], ""
        for w in text.split():
            if cur and font.getlength(cur + " " + w) > maxw:
                lines.append(cur)
                cur = w
            else:
                cur = (cur + " " + w).strip()
        lines.append(cur)
        asc, desc = font.getmetrics()
        lh = int((asc + desc) * 0.98)
        lab = ImageFont.truetype(ytf.font("mono_bold"), max(8, int(33 * S)))
        top = int(60 * S) if label else 0
        pad = int(16 * S)
        im = Image.new("RGBA", (int(maxw) + 2 * pad, top + lh * len(lines) + 2 * pad))
        d = ImageDraw.Draw(im)
        if label:
            d.text((pad, pad), label, font=lab, fill=RUST + (255,), stroke_width=max(1, int(3 * S)), stroke_fill=CREAM + (235,))
        for i, ln in enumerate(lines):
            d.text((pad, pad + top + i * lh + int(5 * S)), ln, font=font, fill=(18, 17, 16, 160), stroke_width=max(1, int(9 * S)), stroke_fill=(18, 17, 16, 160))
            d.text((pad, pad + top + i * lh), ln, font=font, fill=color + (255,), stroke_width=max(1, int(5 * S)), stroke_fill=INK + (255,))
        self.im, self.t0, self.t1, self.pos = np.asarray(im), t0, t1, pos

    def __call__(self, img, t, s=None, cam=None):
        if not self.t0 <= t <= self.t1:
            return img
        a = ease(min(1.0, (t - self.t0) / 0.35), "back")
        k = min(1.0, (t - self.t0) / 0.15, (self.t1 - t) / 0.25)
        return put(img, self.im, int(OW * self.pos[0] - (1 - a) * OW * 0.25), int(OH * self.pos[1]), k=max(0.0, k))


def headline(b, text, t0, t1, sound=True, **kw):
    f = Headline(text, t0, t1, **kw)
    b.overlay(f, t0, t1)
    if sound:
        b.fx("swipe", t0, db=-20)
    return f


# ---------------------------------------------------------------- character and prop cards


def popup(b, path, t0, t1, title, subtitle=None, sound="paper", db=-23, **kw):
    """A character or prop card (character_popup.CharacterPopup) on the word that introduces it, with its small
    sound: "paper" for an introduction, "pop" for a joke, None for silence. pos/width/bounce as CharacterPopup."""
    from character_popup import CharacterPopup
    kw.setdefault("pos", (0.5, 0.44) if film.PORTRAIT else (0.74, 0.44))
    kw.setdefault("width", 0.6 if film.PORTRAIT else 0.3)
    f = CharacterPopup(path, t0, t1, title=title, subtitle=subtitle, **kw)
    b.overlay(f, t0, t1)
    if sound:
        b.fx(sound, t0 + 0.05, t0 + 0.4, db=db)
    return f
