import math
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    experts = [(102, 116, C_BLUE), (182, 86, C_PEACH), (270, 84, C_MINT), (350, 112, C_LAVENDER)]
    for idx, (cx, cy, fill) in enumerate(experts, start=1):
        circle(draw, cx, cy, 30, fill)
        centered_text(draw, cx, cy, str(idx), F_BIG, C_DARK)
        mx = (cx + 292) / 2
        my = min(cy, 192) - 34
        pts = []
        for step in range(18):
            t = step / 17
            x = (1 - t) ** 2 * cx + 2 * (1 - t) * t * mx + t ** 2 * 292
            y = (1 - t) ** 2 * cy + 2 * (1 - t) * t * my + t ** 2 * 206
            pts.append((x, y))
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=lighten(fill, 0.05), width=2)

    circle(draw, 292, 220, 58, C_CREAM)
    centered_text(draw, 292, 220, "LLM", F_BIG, C_DARK)
    arrow(draw, 350, 220, 450, 220, C_LIGHT, width=4)

    draw_bar(draw, 528, 392, 54, 138, 0.52, C_GRAY)
    draw_bar(draw, 614, 392, 54, 138, 0.84, C_MINT)
    centered_text(draw, 528, 408, "ICL", F_LABEL, C_MID)
    centered_text(draw, 614, 408, "ens", F_LABEL, C_DARK)
    draw_check(draw, 614, 216, size=12, col=darken(C_MINT, 0.2))

    return save_image(img, "icl_ensemble")


if __name__ == "__main__":
    generate()
