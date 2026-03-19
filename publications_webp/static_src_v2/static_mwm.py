import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def icon(draw, cx, cy, fill, kind):
    circle(draw, cx, cy, 18, fill)
    ink = darken(fill, 0.3)
    if kind == "lens":
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], outline=ink, width=2)
        draw.line([(cx + 6, cy + 6), (cx + 14, cy + 14)], fill=ink, width=2)
    elif kind == "target":
        draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], outline=ink, width=2)
        circle(draw, cx, cy, 3, ink, outline=ink, width=1)
    elif kind == "grid":
        draw.rectangle([cx - 8, cy - 8, cx + 8, cy + 8], outline=ink, width=2)
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=ink, width=2)
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=ink, width=2)
    else:
        draw.line([(cx - 8, cy), (cx + 8, cy)], fill=ink, width=3)
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=ink, width=3)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    for px, py in [(70, 122), (112, 100), (142, 130), (88, 176), (136, 198)]:
        draw_paper(draw, px, py, 36, 44, fill=lighten(C_GRAY, 0.05), lines=2)
    arrow(draw, 172, 154, 226, 154, C_LIGHT, width=4)

    rounded_box(draw, 280, 122, 74, 46, C_BLUE, radius=12)
    rounded_box(draw, 280, 186, 74, 46, C_MINT, radius=12)
    rounded_box(draw, 280, 250, 74, 46, C_PEACH, radius=12)
    centered_text(draw, 280, 122, "phen", F_LABEL, C_DARK)
    centered_text(draw, 280, 186, "task", F_LABEL, C_DARK)
    centered_text(draw, 280, 250, "metric", F_LABEL, C_DARK)
    centered_text(draw, 350, 186, "?", F_SYMBOL, C_NEG)

    rounded_box(draw, 612, 224, 156, 94, C_PEACH, radius=20)
    centered_text(draw, 612, 224, "score", F_LABEL, C_DARK)

    xs = [390, 426, 462, 498, 534, 570, 606, 642]
    kinds = ["lens", "target", "grid", "plus", "lens", "target", "grid", "plus"]
    fills = [C_BLUE, C_MINT, C_GOLD, C_LAVENDER, C_PEACH, C_TEAL, C_CORAL, C_MINT]
    for cx, kind, fill in zip(xs, kinds, fills):
        icon(draw, cx, 122, fill, kind)
    arrow(draw, 318, 186, 374, 186, C_LIGHT, width=3)
    draw.line([(390, 140), (612, 176)], fill=C_LIGHT, width=2)
    arrow(draw, 318, 316, 560, 316, darken(C_MINT, 0.22), width=5)
    draw_check(draw, 590, 316, size=12, col=darken(C_MINT, 0.22))

    return save_image(img, "mwm")


if __name__ == "__main__":
    generate()
