import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def neuron(draw, cx, cy, fill, r=12):
    circle(draw, cx, cy, r, fill)
    for ang in [0.2, 2.3, 4.3]:
        x = cx + math.cos(ang) * (r + 16)
        y = cy + math.sin(ang) * (r + 16)
        draw.line([(cx, cy), (x, y)], fill=darken(fill, 0.18), width=2)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    for x, y, r in [(128, 145, 14), (175, 188, 16), (138, 238, 13)]:
        neuron(draw, x, y, C_CORAL, r=r)
    centered_text(draw, 150, 300, "few", F_LABEL, C_MID)

    arrow(draw, 232, 190, 315, 190, C_LIGHT, width=4)
    centered_text(draw, 360, 90, "2.5-24%", F_BIG, C_DARK)

    cluster = [
        (392, 128, C_BLUE), (438, 154, C_LAVENDER), (488, 136, C_MINT), (532, 164, C_PEACH),
        (406, 210, C_TEAL), (452, 236, C_CORAL), (500, 216, C_MINT), (548, 240, C_BLUE),
        (388, 290, C_GOLD), (438, 316, C_LAVENDER), (488, 300, C_PEACH), (538, 324, C_MINT),
    ]
    for x, y, fill in cluster:
        circle(draw, x, y, 11, fill)
        arrow(draw, x, y - 26, x, y - 8, darken(fill, 0.25), width=2, head=7)

    rounded_box(draw, 620, 224, 86, 164, lighten(C_MINT, 0.45), radius=14)
    draw_bar(draw, 620, 300, 44, 108, 0.78, C_MINT)
    arrow(draw, 620, 118, 620, 144, darken(C_MINT, 0.25), width=5)
    centered_text(draw, 620, 364, "many", F_LABEL, C_DARK)

    return save_image(img, "dpo_toxicity")


if __name__ == "__main__":
    generate()
