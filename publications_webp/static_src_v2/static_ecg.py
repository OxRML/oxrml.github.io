import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def paper_ecg(draw, cx, cy, angle=0.0):
    draw_paper(draw, cx, cy, 170, 128, fill=(255, 249, 244), lines=0)
    x0 = cx - 74
    y0 = cy - 54
    for gx in range(0, 150, 12):
        draw.line([(x0 + gx, y0), (x0 + gx, y0 + 108)], fill=(250, 223, 223), width=1)
    for gy in range(0, 108, 12):
        draw.line([(x0, y0 + gy), (x0 + 150, y0 + gy)], fill=(250, 223, 223), width=1)
    pts = []
    for i in range(34):
        t = i / 33
        x = x0 + 12 + t * 126
        base = cy + math.sin(t * math.pi * 4) * 6
        spike = -28 if 0.42 < t < 0.5 else 0
        y = base + spike
        dx = x - cx
        dy = y - cy
        rx = cx + dx * math.cos(angle) - dy * math.sin(angle)
        ry = cy + dx * math.sin(angle) + dy * math.cos(angle)
        pts.append((rx, ry))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=(188, 84, 84), width=2)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    paper_ecg(draw, 94, 198, angle=-0.12)
    arrow(draw, 184, 198, 226, 198, C_LIGHT, width=4)

    steps = [
        (274, C_GRAY, "Hough"),
        (390, C_LAVENDER, "U-Net"),
        (506, C_TEAL, "trace"),
    ]
    for cx, fill, label in steps:
        rounded_box(draw, cx, 198, 88, 58, fill, radius=14)
        centered_text(draw, cx, 198, label, F_LABEL, C_DARK)
    arrow(draw, 318, 198, 346, 198, C_LIGHT, width=3)
    arrow(draw, 434, 198, 462, 198, C_LIGHT, width=3)
    arrow(draw, 550, 198, 590, 198, C_LIGHT, width=4)

    rounded_box(draw, 644, 198, 112, 98, lighten(C_MINT, 0.35), radius=16)
    draw_wave(draw, 598, 690, 198, 22, darken(C_MINT, 0.28), width=3, cycles=2.0)
    draw_chip(draw, 644, 340, 96, 58, C_GOLD)
    centered_text(draw, 644, 340, "1st", F_LABEL, darken(C_GOLD, 0.38))

    return save_image(img, "ecg")


if __name__ == "__main__":
    generate()
