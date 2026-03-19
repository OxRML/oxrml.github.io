import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    rounded_box(draw, 126, 186, 150, 132, C_LAVENDER, radius=18)
    draw_wave(draw, 72, 188, 192, 16, darken(C_LAVENDER, 0.24), width=3, cycles=2.3)
    draw_chip(draw, 126, 148, 86, 58, C_BLUE)

    for idx, (cx, cy, label) in enumerate([(320, 132, "OOD"), (378, 186, "data"), (320, 240, "deploy")]):
        circle(draw, cx, cy, 24, C_CORAL if idx < 2 else C_PEACH)
        centered_text(draw, cx, cy, label, F_NOTE, C_DARK)
    for start in range(206, 474, 24):
        draw.line([(start, 186), (start + 12, 186)], fill=darken(C_GOLD, 0.25), width=4)

    rounded_box(draw, 586, 186, 154, 132, C_MINT, radius=18)
    circle(draw, 546, 184, 26, C_CORAL)
    draw_wave(draw, 536, 556, 184, 10, darken(C_CORAL, 0.28), width=3, cycles=1.2)
    circle(draw, 620, 184, 26, C_PEACH)
    draw.line([(612, 184), (628, 184)], fill=darken(C_PEACH, 0.28), width=3)
    draw.line([(620, 176), (620, 192)], fill=darken(C_PEACH, 0.28), width=3)
    centered_text(draw, 586, 320, "clinic", F_LABEL, C_MID)

    return save_image(img, "cardiac_auscultation")


if __name__ == "__main__":
    generate()
