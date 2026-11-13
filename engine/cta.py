"""The closing call to action, the film's last batch: on a sketchbook page, your channel name (YTF_CHANNEL) is written by hand, a
thumbs-up, a subscribe button and a bell are drawn in ink; a cursor clicks like (it fills), subscribe (it turns to
"Subscribed") and the bell (it rings). Our own drawing, in the film's style: no stock footage.
Writes renders/cta.mp4 plus its effects stem (renders/cta_fx.npy) and a silent voice (voice/cta_vo.wav) for final.py.

    python tools/cta.py [--preview]

This is an EXAMPLE ending. Change the drawing, the words and the timing to make it yours; see references/cta.md.
"""
import math
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import film
import look
import ytf
from film import FPS, OH, OW, PREVIEW, Paper, ROOT

END = 7.0
SR = 48000
S = OW / 1920  # screen scale
INK, RED, GREY = look.rgb("ink"), look.rgb("accent"), (96, 92, 88)  # the look's ink and accent (YTF_LOOK)
BOLD = ytf.font("bold")
NAME = ytf.channel() if ytf.channel() != "the channel" else "Your Channel"  # YTF_CHANNEL in .env

# layout in screen px at 1920 x 1080 (the Paper page's own Marks use this space too)
LIKE = (520, 560, 170)    # top-left x, y, size
BTN = (770, 590, 420, 120)  # x, y, w, h
BELL = (1300, 560, 150)
CLICKS = [(3.4, "like"), (4.3, "sub"), (5.1, "bell")]


def P(pts, box):
    x, y, s = box
    return [x + px * s for px, py in pts], [y + py * s for px, py in pts]


def path(pts, box):
    xs, ys = P(pts, box)
    return np.stack([xs, ys], 1)


THUMB = [(0.0, 0.45), (0.22, 0.45), (0.22, 1.0), (0.0, 1.0), (0.0, 0.45)]
HAND = [(0.22, 0.5), (0.4, 0.44), (0.5, 0.12), (0.58, 0.0), (0.68, 0.06), (0.67, 0.38), (0.94, 0.4), (1.0, 0.5),
        (0.97, 0.6), (0.99, 0.7), (0.95, 0.8), (0.95, 0.9), (0.87, 1.0), (0.22, 1.0)]
BELL_PTS = [(0.5, 0.06), (0.3, 0.18), (0.24, 0.58), (0.1, 0.8), (0.9, 0.8), (0.76, 0.58), (0.7, 0.18), (0.5, 0.06)]


def build():
    pg = Paper(0.0, [(0.0, 1920, 1080, 3840), (END, 1920, 1080, 3700)])
    f = pg.fig
    f.text(NAME, (640, 250), 120, 0.45, 1.3, color="ink", angle=-2)
    f.stroke([(640, 345), (960, 338), (1290, 345)], 1.75, 0.35, color="red", width=5)
    like = (LIKE[0], LIKE[1], LIKE[2])
    f.stroke(path(THUMB, like), 2.0, 0.35, color="ink", width=5)
    f.stroke(path(HAND, like), 2.3, 0.6, color="ink", width=5)
    bx, by, bw, bh = BTN
    box = [(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh), (bx, by)]
    f.stroke(box, 2.6, 0.45, color="red", width=6, ease_=0.2)
    bell = (BELL[0], BELL[1], BELL[2])
    f.stroke(path(BELL_PTS, bell), 2.95, 0.4, color="ink", width=5)
    th = np.linspace(0, 2 * math.pi, 20)
    cx, cy = bell[0] + 0.5 * bell[2], bell[1] + 0.9 * bell[2]
    f.stroke(np.stack([cx + 10 * np.cos(th), cy + 10 * np.sin(th)], 1), 3.3, 0.15, color="ink", width=5)
    return pg


def poly_mask(pts, box, size):
    m = Image.new("L", size, 0)
    xs, ys = P(pts, box)
    ImageDraw.Draw(m).polygon([(x * S, y * S) for x, y in zip(xs, ys)], fill=255)
    return np.asarray(m, np.float32) / 255


def cursor_sprite():
    s = 1.3 * S
    pts = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]
    im = Image.new("RGBA", (int(40 * s), int(46 * s)))
    d = ImageDraw.Draw(im)
    d.polygon([(x * s + 2, y * s + 2) for x, y in pts], fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=max(1, int(2 * s)))
    return im


def target(name):
    if name == "like":
        return (LIKE[0] + LIKE[2] * 0.55, LIKE[1] + LIKE[2] * 0.7)
    if name == "sub":
        return (BTN[0] + BTN[2] * 0.5, BTN[1] + BTN[3] * 0.55)
    return (BELL[0] + BELL[2] * 0.5, BELL[1] + BELL[2] * 0.45)


def cursor_pos(t):
    pts = [(2.9, (1700, 1000))] + [(tc - 0.05, target(n)) for tc, n in CLICKS] + [(END, target("bell"))]
    for (ta, a), (tb, b) in zip(pts, pts[1:]):
        if t <= tb:
            u = film.ease((t - ta) / max(1e-6, tb - ta - 0.25))
            return (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    return pts[-1][1]


def frame(pg, t, font, cur):
    img, pen = pg.frame(t)
    sz = (OW, OH)
    clicked = {n: t >= tc for tc, n in CLICKS}
    if clicked["like"]:  # the thumb fills with ink and pops
        u = min(1.0, (t - CLICKS[0][0]) / 0.25)
        a = np.maximum(poly_mask(HAND, LIKE, sz), poly_mask(THUMB, LIKE, sz))[..., None] * u * 0.9
        img = img * (1 - a) + np.array(INK, np.float32) * a
    bx, by, bw, bh = [v * S for v in BTN]
    fill_u = np.clip((t - 3.05) / 0.35, 0, 1)
    if fill_u > 0:  # the button fills red, left to right, then turns grey once clicked
        m = Image.new("L", sz, 0)
        ImageDraw.Draw(m).rounded_rectangle([bx, by, bx + bw * fill_u, by + bh], radius=int(10 * S), fill=255)
        a = np.asarray(m, np.float32)[..., None] / 255 * 0.95
        col = np.array(GREY if clicked["sub"] else RED, np.float32)
        img = img * (1 - a) + col * a
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    if fill_u >= 1:
        txt = "SUBSCRIBED" if clicked["sub"] else "SUBSCRIBE"
        tb = d.textbbox((0, 0), txt, font=font)
        d.text((bx + (bw - (tb[2] - tb[0])) / 2, by + (bh - (tb[3] - tb[1])) / 2 - tb[1]), txt, fill=(255, 255, 255), font=font)
    if clicked["bell"]:  # the bell rings: a wobble and three little ink sound marks
        u = t - CLICKS[2][0]
        if u < 1.2:
            cx, cy = (BELL[0] + BELL[2] * 0.5) * S, (BELL[1] + BELL[2] * 0.3) * S
            for k in (-1, 1):
                for r in (0.62, 0.78):
                    rr = BELL[2] * r * S
                    d.arc([cx - rr, cy - rr, cx + rr, cy + rr], -60 if k > 0 else 200, -20 if k > 0 else 240, fill=INK, width=int(4 * S))
    if t >= 2.9:
        p = cursor_pos(t)
        press = any(0 <= t - tc < 0.12 for tc, _ in CLICKS)
        spr = cur.resize((int(cur.width * 0.9), int(cur.height * 0.9))) if press else cur
        out.paste(spr, (int(p[0] * S), int(p[1] * S)), spr)
    if pen is not None and t < 3.0:
        spr, tip = SPR
        out.paste(spr, (int(pen[1][0] - tip[0]), int(pen[1][1] - tip[1])), spr)
    a = np.asarray(out, np.float32)
    k = min(1.0, t / 0.6) * min(1.0, (END - t) / 0.8)
    return (a * k).astype(np.uint8), (pen[0] if pen is not None and t < 3.0 else None, None if pen is None else pen[1])


def sound(log):
    n = int(END * SR)
    fx = np.zeros(n, np.float32)
    r = np.random.default_rng(3)
    for tc, name in CLICKS:  # mouse clicks
        i, m = int(tc * SR), int(0.03 * SR)
        tt = np.arange(m) / SR
        fx[i:i + m] += film._bp(r.standard_normal(m).astype(np.float32), 2000, 9000, SR) * np.exp(-tt * 200) * 0.25
    i, m = int(CLICKS[2][0] * SR), int(1.6 * SR)  # the bell: a soft ding
    tt = np.arange(m) / SR
    fx[i:i + m] += (np.sin(2 * np.pi * 1320 * tt) + 0.4 * np.sin(2 * np.pi * 2640 * tt) + 0.2 * np.sin(2 * np.pi * 3960 * tt)) * np.exp(-tt * 3) * 0.12
    i, m = int(CLICKS[0][0] * SR), int(0.25 * SR)  # the like: a soft pop
    tt = np.arange(m) / SR
    fx[i:i + m] += np.sin(2 * np.pi * (520 + 300 * tt) * tt) * np.exp(-tt * 25) * 0.1
    fx += _pen_ref(log, n)
    return fx


def _pen_ref(log, n):
    """The pen on its own (no narration here) at the film's in-the-gaps level: a short speech-level reference sets the
    level, and nothing is ducked."""
    ref = np.full(n, 1e-4, np.float32)
    ref[: int(0.5 * SR)] = 0.12  # gives the pen sound a speech-level reference without ducking it
    return film._pen_sound(log, n, SR, ref)


SPR = None


def main():
    global SPR
    SPR = film.sk.tool_sprite("pen", 0.28 * S)
    pg = build()
    font = ImageFont.truetype(BOLD, int(46 * S))
    cur = cursor_sprite()
    out = ROOT / "renders" / f"cta{'_preview' if PREVIEW else ''}.mp4"
    silent = out.with_suffix(".silent.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", ytf.x264_preset(),
                           "-pix_fmt", "yuv420p", str(silent)], stdin=subprocess.PIPE)
    log = []
    for fi in range(int(END * FPS)):
        a, (tool, p) = frame(pg, fi / FPS, font, cur)
        log.append((tool, None if p is None or tool is None else (float(p[0]), float(p[1]))))
        ff.stdin.write(a.tobytes())
    ff.stdin.close()
    ff.wait()
    fx = sound(log)
    if not PREVIEW:
        np.save(ROOT / "renders" / "cta_fx.npy", fx)
        film._write(ROOT / "voice" / "cta_vo.wav", np.zeros(int(END * 24000), np.float32), 24000)
    wav = out.with_suffix(".wav")
    film._write(wav, fx / (np.abs(fx).max() + 1e-9) * 0.5, SR)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(wav), "-c:v", "copy", "-c:a", "aac",
                    "-b:a", "192k", "-shortest", str(out)], check=True)
    silent.unlink()
    print("wrote", out)


if __name__ == "__main__":
    main()
