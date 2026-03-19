import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def puzzle(draw, cx, cy, fill, text):
    rounded_box(draw, cx, cy, 84, 66, fill, radius=18)
    centered_text(draw, cx, cy, text, F_LABEL, darken(fill, 0.42))


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    puzzle(draw, 120, 118, C_BLUE, "nu")
    puzzle(draw, 214, 86, C_PEACH, "ka")
    puzzle(draw, 118, 210, C_MINT, "ti")
    puzzle(draw, 230, 210, C_LAVENDER, "?")

    arrow(draw, 282, 150, 350, 150, C_LIGHT, width=4)
    circle(draw, 414, 150, 54, C_CREAM)
    centered_text(draw, 414, 150, "LLM", F_BIG, C_DARK)

    draw_bar(draw, 546, 392, 54, 140, 0.76, C_BLUE)
    draw_bar(draw, 632, 392, 54, 140, 0.39, C_CORAL)
    centered_text(draw, 546, 408, "easy", F_LABEL, C_MID)
    centered_text(draw, 632, 408, "hard", F_LABEL, C_DARK)
    centered_text(draw, 632, 198, "38%", F_BIG, C_NEG)

    return save_image(img, "lingoly_one")


if __name__ == "__main__":
    generate()
