import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def model_box(draw, cx, cy, fill):
    rounded_box(draw, cx, cy, 58, 46, fill, radius=12)
    draw.rectangle([cx - 10, cy - 8, cx + 10, cy + 8], outline=darken(fill, 0.32), width=2)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    positions = [(108, 110, C_BLUE), (180, 110, C_PEACH), (108, 178, C_MINT), (180, 178, C_LAVENDER)]
    for cx, cy, fill in positions:
        model_box(draw, cx, cy, fill)

    questions = [(326, 98, False), (326, 172, True), (326, 246, False)]
    for cx, cy, wrong in questions:
        circle(draw, cx, cy, 24, C_CORAL if wrong else C_CREAM)
        centered_text(draw, cx, cy, "?", F_BIG, C_DARK)
        for mx, my, _ in positions:
            draw.line([(mx + 30, my), (cx - 24, cy)], fill=C_LIGHT, width=2)
        if wrong:
            for ox in [382, 416, 450]:
                draw_cross(draw, ox, cy, size=8, col=C_NEG)

    draw_matrix(draw, 502, 104, 34, [
        [1.0, 0.56, 0.52, 0.49],
        [0.56, 1.0, 0.58, 0.51],
        [0.52, 0.58, 1.0, 0.55],
        [0.49, 0.51, 0.55, 1.0],
    ])
    centered_text(draw, 570, 286, "~", F_SYMBOL, C_MID)

    return save_image(img, "llm_shared_weaknesses")


if __name__ == "__main__":
    generate()
