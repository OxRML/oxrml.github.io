import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def modality(draw, cx, cy, fill, kind):
    rounded_box(draw, cx, cy, 74, 74, fill, radius=16)
    ink = darken(fill, 0.28)
    if kind == "img":
        draw.polygon([(cx - 20, cy + 16), (cx - 2, cy - 6), (cx + 20, cy + 16)], fill=ink)
        circle(draw, cx + 20, cy - 18, 7, ink, outline=ink, width=1)
    elif kind == "txt":
        for y in [cy - 12, cy, cy + 12]:
            draw.line([(cx - 20, y), (cx + 18 - (y == cy + 12) * 10, y)], fill=ink, width=3)
    elif kind == "wave":
        draw_wave(draw, cx - 24, cx + 24, cy, 12, ink, width=3, cycles=1.5)
    else:
        draw.line([(cx, cy - 22), (cx, cy + 22)], fill=ink, width=2)
        draw.line([(cx - 22, cy), (cx + 22, cy)], fill=ink, width=2)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    paper_pts = [(88, 104), (144, 78), (146, 136), (86, 188), (150, 236), (102, 292)]
    for px, py in paper_pts:
        draw_paper(draw, px, py, 34, 42, fill=lighten(C_GRAY, 0.05), lines=2)
        draw.line([(px + 18, py), (234, 212)], fill=lighten(C_LIGHT, 0.05), width=1)

    circle(draw, 270, 224, 42, C_GOLD)
    centered_text(draw, 270, 224, "+", F_SYMBOL, C_DARK)
    arrow(draw, 314, 224, 372, 224, C_LIGHT, width=4)

    items = [(430, 130, "img", C_BLUE), (540, 130, "txt", C_PEACH), (430, 238, "wave", C_MINT), (540, 238, "tbl", C_LAVENDER)]
    for cx, cy, kind, fill in items:
        modality(draw, cx, cy, fill, kind)

    arrow(draw, 576, 184, 642, 184, C_LIGHT, width=4)
    for x, frac, fill in [(642, 0.82, C_MINT), (682, 0.56, C_PEACH)]:
        draw_bar(draw, x, 260, 30, 92, frac, fill)
    for x, frac, fill in [(642, 0.72, C_BLUE), (682, 0.48, C_LAVENDER)]:
        draw_bar(draw, x, 390, 30, 92, frac, fill)
    centered_text(draw, 662, 326, "~", F_SYMBOL, C_MID)

    return save_image(img, "multimodal")


if __name__ == "__main__":
    generate()
