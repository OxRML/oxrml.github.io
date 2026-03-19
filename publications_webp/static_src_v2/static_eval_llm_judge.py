import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    rounded_box(draw, 210, 170, 118, 82, C_BLUE, radius=16)
    rounded_box(draw, 510, 170, 118, 82, C_PEACH, radius=16)
    draw.rectangle([178, 146, 206, 168], fill=lighten(C_BLUE, 0.1), outline=darken(C_BLUE, 0.2), width=2)
    draw.line([(180, 178), (238, 178)], fill=darken(C_BLUE, 0.24), width=3)
    draw.rectangle([478, 146, 506, 168], fill=lighten(C_PEACH, 0.1), outline=darken(C_PEACH, 0.2), width=2)
    draw.line([(480, 178), (538, 178)], fill=darken(C_PEACH, 0.24), width=3)

    circle(draw, 360, 170, 42, C_LAVENDER)
    centered_text(draw, 360, 170, "J", F_LABEL, C_DARK)
    draw.line([(246, 170), (318, 170)], fill=C_LIGHT, width=4)
    draw.line([(402, 170), (474, 170)], fill=C_LIGHT, width=4)

    labels = ["EN", "AR", "ZH", "ES", "HI", "FR", "TR", "DE", "PT", "BN", "UR", "JA"]
    for idx, label in enumerate(labels):
        ang = idx * math.pi * 2 / len(labels) - math.pi / 2
        cx = 360 + math.cos(ang) * 138
        cy = 170 + math.sin(ang) * 138
        fill = [C_BLUE, C_PEACH, C_MINT, C_LAVENDER][idx % 4]
        circle(draw, int(cx), int(cy), 22, fill)
        centered_text(draw, int(cx), int(cy), label[:2], F_NOTE, C_DARK)
        draw.line([(360, 170), (cx, cy)], fill=lighten(fill, 0.1), width=2 + (idx % 3 == 0))

    for x, frac, fill in [(260, 0.42, C_BLUE), (330, 0.78, C_MINT), (400, 0.55, C_LAVENDER), (470, 0.66, C_PEACH)]:
        draw_bar(draw, x, 400, 44, 120, frac, fill)
    centered_text(draw, 580, 360, "12", F_LABEL, C_MID)

    return save_image(img, "eval_llm_judge")


if __name__ == "__main__":
    generate()
