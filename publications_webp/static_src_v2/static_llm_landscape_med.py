import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    models = [("G4", 0.82, C_BLUE), ("M42", 0.69, C_MINT), ("P2", 0.66, C_PEACH), ("Mx", 0.63, C_LAVENDER), ("G35", 0.60, C_GOLD)]
    start_y = 106
    for idx, (label, frac, fill) in enumerate(models):
        y = start_y + idx * 52
        right_text(draw, 122, y, label, F_LABEL, C_MID)
        draw.rounded_rectangle([140, y - 14, 318, y + 14], radius=8, fill=lighten(C_GRAY, 0.1), outline=lighten(C_GRAY, 0.1), width=1)
        fill_w = int(178 * frac)
        draw.rounded_rectangle([140, y - 14, 140 + fill_w, y + 14], radius=8, fill=fill, outline=darken(fill, 0.12), width=2)

    rounded_box(draw, 514, 132, 150, 72, C_MINT, radius=18)
    centered_text(draw, 482, 124, "conf", F_LABEL, C_DARK)
    centered_text(draw, 556, 126, "+", F_BIG, darken(C_MINT, 0.3))

    rounded_box(draw, 514, 240, 150, 72, C_PEACH, radius=18)
    centered_text(draw, 482, 232, "len", F_LABEL, C_DARK)
    centered_text(draw, 556, 234, "-", F_BIG, darken(C_PEACH, 0.35))

    rounded_box(draw, 514, 348, 150, 72, C_BLUE, radius=18)
    centered_text(draw, 482, 340, "human", F_LABEL, C_DARK)
    centered_text(draw, 556, 342, "+", F_BIG, darken(C_BLUE, 0.35))

    arrow(draw, 330, 210, 420, 210, C_LIGHT, width=4)

    return save_image(img, "llm_landscape_med")


if __name__ == "__main__":
    generate()
