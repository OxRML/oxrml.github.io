import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    rounded_box(draw, 114, 152, 112, 84, C_LAVENDER, radius=16)
    draw_chip(draw, 114, 152, 88, 64, C_LAVENDER)
    centered_text(draw, 114, 248, "95%", F_LABEL, darken(C_MINT, 0.32))

    draw_person(draw, 320, 176, C_PEACH)
    draw_chip(draw, 402, 192, 74, 58, C_BLUE)
    for cx in [298, 340, 382, 424]:
        circle(draw, cx, 106, 7, C_CREAM)
    draw.line([(340, 182), (368, 182)], fill=C_LIGHT, width=3)
    draw.line([(368, 196), (340, 196)], fill=C_LIGHT, width=3)

    arrow(draw, 170, 176, 248, 176, C_LIGHT, width=4)
    arrow(draw, 450, 176, 530, 176, C_LIGHT, width=4)

    rounded_box(draw, 602, 176, 112, 84, lighten(C_CORAL, 0.45), radius=16)
    centered_text(draw, 602, 176, "35%", F_LABEL, darken(C_CORAL, 0.35))
    draw.line([(142, 312), (142, 340)], fill=C_LIGHT, width=2)
    draw.line([(602, 226), (602, 340)], fill=C_LIGHT, width=2)
    draw.line([(142, 340), (602, 340)], fill=C_NEG, width=3)
    centered_text(draw, 372, 360, "-60", F_LABEL, C_NEG)

    return save_image(img, "helpmed")


if __name__ == "__main__":
    generate()
