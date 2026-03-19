import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    draw.polygon([(170, 90), (558, 90), (558, 360), (170, 360)], fill=lighten(C_MINT, 0.7))
    draw.line([(170, 360), (558, 90)], fill=darken(C_LAVENDER, 0.2), width=3)

    circle(draw, 280, 280, 12, C_CORAL)
    centered_text(draw, 144, 120, "valid", F_LABEL, C_DARK)
    centered_text(draw, 542, 120, "minimal", F_LABEL, C_DARK)

    circle(draw, 420, 164, 12, C_BLUE)
    arrow(draw, 294, 270, 408, 174, darken(C_BLUE, 0.2), width=4)
    draw_check(draw, 448, 144, size=10, col=darken(C_MINT, 0.2))

    circle(draw, 386, 220, 10, C_PEACH)
    draw.line([(288, 276), (378, 226)], fill=darken(C_PEACH, 0.24), width=3)
    draw_cross(draw, 414, 204, size=8, col=C_NEG)
    centered_text(draw, 522, 272, "boundary", F_LABEL, C_MID)

    return save_image(img, "counterfactual")


if __name__ == "__main__":
    generate()
