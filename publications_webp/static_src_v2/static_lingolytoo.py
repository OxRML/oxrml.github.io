import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    rounded_box(draw, 160, 170, 180, 96, C_BLUE)
    centered_text(draw, 160, 165, "Ufgent", F_BIG, darken(C_BLUE, 0.42))
    circle(draw, 160, 265, 34, C_CREAM)
    centered_text(draw, 160, 265, "flew", F_LABEL, C_MID)

    arrow(draw, 265, 170, 455, 170, C_LIGHT, width=4, head=14)
    for x, y, fill in [(312, 150, C_BLUE), (348, 180, C_LAVENDER), (386, 156, C_PEACH), (420, 178, C_CORAL)]:
        circle(draw, x, y, 7, fill, outline=fill, width=1)

    rounded_box(draw, 560, 170, 180, 96, C_PEACH)
    centered_text(draw, 560, 165, "Eqcawg", F_BIG, darken(C_PEACH, 0.42))
    circle(draw, 560, 265, 34, C_CREAM)
    centered_text(draw, 560, 265, "flew", F_LABEL, C_MID)
    centered_text(draw, 360, 265, "=", F_SYMBOL, C_MID)

    draw_bar(draw, 290, 392, 74, 122, 0.79, darken(C_BLUE, 0.08))
    draw_bar(draw, 430, 392, 74, 122, 0.58, darken(C_PEACH, 0.08))
    centered_text(draw, 290, 250, ".79", F_LABEL, C_DARK)
    centered_text(draw, 430, 276, ".58", F_LABEL, C_DARK)
    arrow(draw, 360, 280, 360, 320, C_NEG, width=4, head=12)

    return save_image(img, "lingolytoo")


if __name__ == "__main__":
    generate()
