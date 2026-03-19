import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from utils import *


def xray(draw, cx, cy):
    rounded_box(draw, cx, cy, 126, 164, (63, 68, 80), radius=16, outline=(92, 96, 110))
    for i in range(4):
        y = cy - 48 + i * 28
        draw.arc([cx - 46, y - 8, cx - 10, y + 8], 0, 180, fill=(110, 116, 128), width=2)
        draw.arc([cx + 10, y - 8, cx + 46, y + 8], 0, 180, fill=(110, 116, 128), width=2)
    draw.ellipse([cx - 28, cy - 26, cx + 28, cy + 44], fill=(150, 158, 172), outline=(186, 192, 204), width=2)


def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    xray(draw, 112, 194)
    arrow(draw, 184, 184, 260, 136, C_LIGHT, width=3)
    arrow(draw, 184, 204, 260, 194, C_LIGHT, width=3)
    arrow(draw, 184, 224, 260, 252, C_LIGHT, width=3)

    rounded_box(draw, 334, 132, 122, 52, C_BLUE, radius=14)
    rounded_box(draw, 334, 194, 122, 52, C_MINT, radius=14)
    rounded_box(draw, 334, 256, 122, 52, C_PEACH, radius=14)
    centered_text(draw, 334, 132, "CTR", F_BIG, C_DARK)
    centered_text(draw, 334, 194, "CPAR", F_LABEL, C_DARK)
    centered_text(draw, 334, 256, "ICU", F_BIG, C_DARK)

    draw.line([(394, 132), (438, 194)], fill=C_LIGHT, width=3)
    draw.line([(394, 194), (438, 194)], fill=C_LIGHT, width=3)
    draw.line([(394, 256), (438, 194)], fill=C_LIGHT, width=3)
    arrow(draw, 438, 194, 526, 194, C_LIGHT, width=4)

    rounded_box(draw, 606, 194, 126, 92, lighten(C_LAVENDER, 0.35), radius=16)
    centered_text(draw, 606, 180, "Dx", F_BIG, C_DARK)
    centered_text(draw, 606, 220, "~", F_SYMBOL, darken(C_MINT, 0.28))
    centered_text(draw, 606, 360, "explainable", F_LABEL, C_MID)

    return save_image(img, "multimodal_cardiomegaly")


if __name__ == "__main__":
    generate()
