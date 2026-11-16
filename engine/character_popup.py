"""A screen-space character or prop card for landscape and portrait edits."""

import math

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

import ytf

PAPER = (247, 225, 180, 249)
INK = (39, 33, 28)
RUST = (164, 63, 54)


def ease(value):
    value = min(1.0, max(0.0, value))
    return value * value * (3 - 2 * value)


def label(draw, text, center, role, size):
    font = ImageFont.truetype(ytf.font(role), size)
    width = draw.textlength(text, font=font)
    if width > 374:
        font = ImageFont.truetype(ytf.font(role), max(1, round(size * 374 / width)))
    draw.text(center, text, font=font, fill=INK, anchor="mm")


def make_card(path, title, subtitle):
    with Image.open(path) as source:
        sprite = source.convert("RGBA")
    alpha = sprite.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None or alpha.getextrema()[0] == 255:
        raise ValueError(f"Popup artwork must contain a visible subject and transparency: {path}")
    sprite = sprite.crop(bounds)
    sprite.thumbnail((352, 342), Image.Resampling.LANCZOS)

    card = Image.new("RGBA", (476, 546))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((22, 62, 454, 521), radius=48, fill=(28, 25, 24, 94))
    draw.rounded_rectangle((13, 44, 445, 510), radius=40, fill=PAPER, outline=INK, width=5)
    card.alpha_composite(sprite, (229 - sprite.width // 2, 79 + (342 - sprite.height) // 2))
    rule = 416 if subtitle else 432
    draw.line((91, rule, 361, rule), fill=RUST, width=4)
    label(draw, title, (227, rule + 35), "mono_bold", 40)
    if subtitle:
        label(draw, subtitle, (227, rule + 74), "bold", 30)
    return np.asarray(card)


class CharacterPopup:
    """Overlay a transparent character or prop on a timed paper card.

    pos and width are fractions of the rendered frame. Time is in seconds in
    the caller's timeline. The call draws into the frame and returns it. The
    optional shot and camera arguments support film.Batch.overlay callbacks.
    """

    def __init__(self, path, start, end, *, title, subtitle=None, pos=(0.74, 0.44),
                 width=0.42, bounce=0.11, color_order="RGB"):
        if not (math.isfinite(start) and math.isfinite(end) and end > start):
            raise ValueError("Popup end time must follow the start time")
        if not 0 < width <= 1 or len(pos) != 2 or not all(0 <= value <= 1 for value in pos):
            raise ValueError("Popup width and position must be frame fractions")
        if not 0 <= bounce <= 0.35 or color_order not in ("RGB", "BGR"):
            raise ValueError("Expected bounce in [0, 0.35] and RGB or BGR color order")
        self.card = make_card(path, title, subtitle)
        self.start, self.end = start, end
        self.pos, self.width, self.bounce = pos, width, bounce
        self.color_order = color_order

    def __call__(self, frame, time, shot=None, camera=None):
        if not self.start < time < self.end:
            return frame
        age, duration = time - self.start, self.end - self.start
        arrive = ease(age / min(0.30, duration / 3))
        leave = ease((self.end - time) / min(0.28, duration / 3))
        spring = self.bounce * math.sin(math.pi * arrive)
        scale = (0.79 + 0.21 * arrive + spring) * (0.89 + 0.11 * leave)
        ih, iw = frame.shape[:2]
        width = max(1, round(iw * self.width * scale))
        height = max(1, round(width * 546 / 476))
        x = round(iw * self.pos[0] - width / 2 + iw * 0.037 * (1 - arrive))
        y = round(ih * self.pos[1] - height / 2 + ih * (0.022 * (1 - arrive) + 0.016 * (1 - leave)))

        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(iw, x + width), min(ih, y + height)
        if x0 >= x1 or y0 >= y1:
            return frame
        card = cv2.resize(self.card, (width, height), interpolation=cv2.INTER_AREA)
        patch = card[y0 - y:y1 - y, x0 - x:x1 - x]
        color = patch[:, :, :3]
        if self.color_order == "BGR":
            color = color[:, :, ::-1]
        alpha = patch[:, :, 3:4].astype(np.float32) * (min(1.0, arrive * 1.7, leave) / 255)
        area = frame[y0:y1, x0:x1]
        area[:] = area * (1 - alpha) + color * alpha
        return frame
