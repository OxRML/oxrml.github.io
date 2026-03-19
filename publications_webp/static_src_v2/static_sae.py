import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    rounded_box(draw, 180, 200, 190, 138, C_BLUE)
    centered_text(draw, 180, 138, "SAE", F_BIG, C_DARK)
    for x, y, r in [(148, 198, 14), (184, 182, 18), (220, 205, 16), (167, 228, 12), (211, 232, 14)]:
        circle(draw, x, y, r, lighten(C_BLUE, 0.2))

    arrow(draw, 70, 108, 150, 156, darken(C_LAVENDER, 0.18), width=5, head=14)
    draw.line([(70, 108), (102, 140)], fill=darken(C_LAVENDER, 0.18), width=5)

    axis_y = 246
    draw.line([(330, axis_y), (505, axis_y)], fill=C_LIGHT, width=2)
    for x, frac, fill in [(352, 0.64, C_MINT), (390, 0.42, C_MINT), (428, 0.24, C_MINT)]:
        draw_bar(draw, x, axis_y, 26, 86, frac, fill)
    draw.rounded_rectangle([466 - 13, axis_y, 466 + 13, axis_y + 40], radius=8, fill=C_CORAL, outline=darken(C_CORAL, 0.12), width=2)
    centered_text(draw, 466, axis_y + 60, "-", F_BIG, C_NEG)

    draw.line([(560, 225), (626, 170)], fill=darken(C_LAVENDER, 0.18), width=6)
    draw.line([(560, 225), (622, 250)], fill=darken(C_CORAL, 0.18), width=6)
    draw.line([(560, 225), (606, 198)], fill=darken(C_BLUE, 0.22), width=5)
    draw.line([(618, 210), (662, 228)], fill=darken(C_GRAY, 0.28), width=6)
    centered_text(draw, 640, 278, "!=", F_SYMBOL, C_NEG)

    return save_image(img, "sae")


if __name__ == "__main__":
    generate()
