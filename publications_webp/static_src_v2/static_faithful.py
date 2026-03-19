import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    rounded_box(draw, 120, 142, 118, 78, C_CREAM, radius=16)
    rounded_box(draw, 120, 264, 118, 78, C_CREAM, radius=16)
    centered_text(draw, 120, 130, "60", F_LABEL, C_DARK)
    centered_text(draw, 120, 252, "30", F_LABEL, C_DARK)
    for y in [152, 274]:
        circle(draw, 92, y, 5, C_BLUE, outline=C_BLUE, width=1)
        circle(draw, 120, y, 5, C_GOLD, outline=C_GOLD, width=1)
        circle(draw, 148, y, 5, C_MINT, outline=C_MINT, width=1)

    draw_chip(draw, 294, 202, 110, 88, C_LAVENDER)
    draw_speech(draw, 294, 304, 96, 56, C_PEACH)
    centered_text(draw, 294, 304, "age", F_LABEL, darken(C_PEACH, 0.34))
    arrow(draw, 182, 166, 238, 184, C_LIGHT, width=3)
    arrow(draw, 182, 238, 238, 220, C_LIGHT, width=3)

    rounded_box(draw, 444, 202, 106, 76, C_BLUE, radius=14)
    draw.ellipse([420, 184, 468, 212], fill=C_CREAM, outline=darken(C_BLUE, 0.24), width=2)
    circle(draw, 444, 198, 8, darken(C_BLUE, 0.35), outline=darken(C_BLUE, 0.35), width=1)
    arrow(draw, 342, 304, 396, 222, darken(C_PEACH, 0.18), width=5)

    draw_bar(draw, 568, 390, 58, 130, 0.56, C_GRAY)
    draw_bar(draw, 652, 390, 58, 130, 0.82, C_MINT)
    centered_text(draw, 610, 214, "NSG", F_LABEL, C_DARK)
    arrow(draw, 610, 304, 610, 250, darken(C_MINT, 0.24), width=5)

    return save_image(img, "faithful")


if __name__ == "__main__":
    generate()
