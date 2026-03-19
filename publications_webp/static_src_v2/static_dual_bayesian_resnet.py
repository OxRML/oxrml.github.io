import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def spectrogram(draw, cx, cy):
    rounded_box(draw, cx, cy, 100, 82, C_BLUE, radius=12)
    for row in range(6):
        for col in range(7):
            fill = mix(C_BLUE, C_DARK, 0.12 + 0.08 * ((row + col) % 4))
            draw.rectangle([cx - 38 + col * 11, cy - 28 + row * 10, cx - 30 + col * 11, cy - 20 + row * 10], fill=fill)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    circle(draw, 88, 150, 24, C_CORAL)
    draw_wave(draw, 48, 128, 238, 20, darken(C_CORAL, 0.25), width=3, cycles=2.5)
    arrow(draw, 146, 192, 188, 192, C_LIGHT, width=4)

    spectrogram(draw, 244, 176)
    spectrogram(draw, 272, 208)
    arrow(draw, 326, 184, 388, 154, C_LIGHT, width=3)
    arrow(draw, 336, 218, 388, 238, C_LIGHT, width=3)

    rounded_box(draw, 458, 150, 112, 58, C_LAVENDER, radius=14)
    rounded_box(draw, 458, 238, 112, 58, C_MINT, radius=14)
    centered_text(draw, 458, 150, "P/U", F_LABEL, C_DARK)
    centered_text(draw, 458, 238, "U/A", F_LABEL, C_DARK)

    draw.line([(514, 150), (554, 192)], fill=C_LIGHT, width=3)
    draw.line([(514, 238), (554, 192)], fill=C_LIGHT, width=3)
    arrow(draw, 554, 192, 612, 192, C_LIGHT, width=4)

    rounded_box(draw, 646, 192, 96, 72, lighten(C_CORAL, 0.45), radius=16)
    centered_text(draw, 646, 192, "vote", F_LABEL, darken(C_CORAL, 0.32))
    draw_chip(draw, 596, 338, 96, 58, C_GOLD)
    centered_text(draw, 596, 338, "4th", F_LABEL, darken(C_GOLD, 0.38))

    return save_image(img, "dual_bayesian_resnet")


if __name__ == "__main__":
    generate()
