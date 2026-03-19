import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def draw_feedback(draw, cx, cy, fill):
    draw_speech(draw, cx, cy, 94, 62, fill)
    for y in [cy - 10, cy + 2, cy + 14]:
        draw.line([(cx - 26, y), (cx + 22 - (y == cy + 14) * 10, y)], fill=darken(fill, 0.22), width=2)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    draw_doc(draw, 120, 188, 116, 152, C_BLUE, lines=6)
    draw_chip(draw, 318, 188, 118, 92, C_LAVENDER)
    draw_feedback(draw, 505, 158, C_CREAM)
    arrow(draw, 184, 188, 255, 188, C_LIGHT, width=4)
    arrow(draw, 382, 188, 448, 170, C_LIGHT, width=4)

    centered_text(draw, 555, 300, "rapport", F_LABEL, C_DARK)
    centered_text(draw, 640, 300, "skills", F_LABEL, C_DARK)

    draw_bar(draw, 530, 392, 42, 116, 0.84, C_MINT)
    draw_bar(draw, 580, 392, 42, 116, 0.48, C_GRAY)
    draw_bar(draw, 615, 392, 42, 116, 0.49, C_BLUE)
    draw_bar(draw, 665, 392, 42, 116, 0.49, C_GRAY)

    draw_check(draw, 530, 246, size=12, col=darken(C_MINT, 0.2))
    centered_text(draw, 640, 248, "=", F_SYMBOL, C_MID)

    return save_image(img, "constitutions")


if __name__ == "__main__":
    generate()
