# publications_webp/static_src/static_multimodal.py
"""
Multimodal ML in Healthcare: 4 modalities, effectiveness varies by task.
Visual: 4 modality icons → fusion → variable output bars with ~symbol.
Minimal text: just icons and symbols.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *
import math

def draw_modality_icon(draw, cx, cy, size, mod_type):
    """Draw modality icon."""
    s = size // 2

    if mod_type == "image":
        col = C_BLUE
        draw_box(draw, cx, cy, size, size, col, r=8)
        m_col = darken(col, 0.25)
        draw.polygon([(cx - s + 10, cy + s - 10),
                      (cx, cy - 5),
                      (cx + s - 10, cy + s - 10)], fill=m_col)
        draw.ellipse([cx + s - 22, cy - s + 10, cx + s - 8, cy - s + 24], fill=darken(col, 0.15))

    elif mod_type == "text":
        col = C_PEACH
        draw_box(draw, cx, cy, size, size, col, r=8)
        for i, w in enumerate([0.75, 0.55, 0.7, 0.5]):
            ly = cy - s + 14 + i * 14
            draw.line([(cx - s + 10, ly), (cx - s + 10 + int((size - 20) * w), ly)],
                      fill=darken(col, 0.25), width=3)

    elif mod_type == "wave":
        col = C_MINT
        draw_box(draw, cx, cy, size, size, col, r=8)
        wave_col = darken(col, 0.35)
        pts = []
        for i in range(10):
            x = cx - s + 10 + i * (size - 20) // 9
            y = cy + int(math.sin(i * 1.2) * 15)
            pts.append((x, y))
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=wave_col, width=3)

    elif mod_type == "table":
        col = C_LAVENDER
        draw_box(draw, cx, cy, size, size, col, r=8)
        grid_col = darken(col, 0.25)
        draw.line([(cx, cy - s + 10), (cx, cy + s - 10)], fill=grid_col, width=2)
        draw.line([(cx - s + 10, cy), (cx + s - 10, cy)], fill=grid_col, width=2)
        for dx, dy in [(-s//2, -s//2), (s//2, -s//2), (-s//2, s//2), (s//2, s//2)]:
            draw.ellipse([cx + dx - 6, cy + dy - 6, cx + dx + 6, cy + dy + 6], fill=grid_col)

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # 4 modality icons
    icon_size = 75
    icon_y = 130
    modalities = [
        (120, "image"),
        (260, "text"),
        (400, "wave"),
        (540, "table"),
    ]

    for mx, mod_type in modalities:
        draw_modality_icon(draw, mx, icon_y, icon_size, mod_type)

    # Fusion arrows pointing down
    for mx, _ in modalities:
        draw.line([(mx, icon_y + icon_size//2 + 10), (mx, icon_y + icon_size//2 + 40)], fill=C_LIGHT, width=3)
        draw.line([(mx, icon_y + icon_size//2 + 40), (330, 270)], fill=C_LIGHT, width=2)

    # Fusion circle
    draw_circle(draw, 330, 290, 35, C_GOLD)
    tc(draw, 330, 290, "+", F_SYMBOL, C_DARK)

    # Arrow down to results
    draw_arrow(draw, 330, 330, 330, 370, C_LIGHT, width=3, head=12)

    # Result bars showing variance
    bar_w, bar_h = 50, 100
    bar_y = 410

    bars = [
        (200, 0.82, C_MINT),
        (280, 0.55, C_PEACH),
        (360, 0.73, C_BLUE),
        (440, 0.48, C_LAVENDER),
        (520, 0.68, C_CORAL),
    ]

    for bx, frac, col in bars:
        draw_bar(draw, bx, bar_y, bar_w, bar_h, col, frac)

    # Tilde symbol showing variance
    tc(draw, 600, 360, "~", F_SYMBOL, C_MID)

    return save_image(img, "multimodal")

if __name__ == "__main__":
    generate()
