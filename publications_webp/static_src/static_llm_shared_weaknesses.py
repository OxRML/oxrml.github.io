# publications_webp/static_src/static_llm_shared_weaknesses.py
"""
LLMs share weaknesses: when one fails, others often fail too.
Visual: Overlapping circles (Venn-like) with shared red center + correlation bars.
Minimal text: just overlap visualization and correlation indicators.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Overlapping LLM circles showing correlation ===
    overlap_cx = 220
    overlap_cy = 220

    # Draw overlapping circles
    circles = [
        (overlap_cx - 55, overlap_cy - 40, C_BLUE),
        (overlap_cx + 55, overlap_cy - 40, C_PEACH),
        (overlap_cx - 35, overlap_cy + 50, C_MINT),
        (overlap_cx + 35, overlap_cy + 50, C_LAVENDER),
    ]

    for cx, cy, col in circles:
        draw.ellipse([cx - 55, cy - 55, cx + 55, cy + 55],
                     fill=lighten(col, 0.4), outline=darken(col, 0.15), width=3)

    # Central overlap region (shared weakness - coral/red)
    draw.ellipse([overlap_cx - 35, overlap_cy - 20, overlap_cx + 35, overlap_cy + 30],
                 fill=C_CORAL, outline=darken(C_CORAL, 0.2), width=2)

    # X mark in center showing failure
    x_cx, x_cy = overlap_cx, overlap_cy + 5
    x_size = 18
    draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=5)
    draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=5)

    # === RIGHT: Correlation visualization ===
    corr_cx = 530
    bar_y_start = 120

    # Correlation bars (showing high positive correlation)
    correlations = [
        (0.58, C_CORAL),
        (0.52, C_CORAL),
        (0.45, C_PEACH),
        (0.39, C_PEACH),
    ]

    bar_w = 140
    bar_h = 25

    for i, (corr, col) in enumerate(correlations):
        by = bar_y_start + i * 55

        # Track
        rrect(draw, [corr_cx - bar_w//2, by, corr_cx + bar_w//2, by + bar_h], r=6, fill=C_GRAY)

        # Fill
        fill_w = int(bar_w * corr)
        if fill_w > 6:
            rrect(draw, [corr_cx - bar_w//2, by, corr_cx - bar_w//2 + fill_w, by + bar_h], r=6, fill=col)

        # Connection line to center overlap
        draw.line([(corr_cx - bar_w//2 - 20, by + bar_h//2), (overlap_cx + 80, overlap_cy)],
                  fill=lighten(col, 0.5), width=1)

    # Arrows between circles showing correlation
    for i, (cx1, cy1, _) in enumerate(circles):
        for cx2, cy2, _ in circles[i+1:]:
            mid_x = (cx1 + cx2) // 2
            mid_y = (cy1 + cy2) // 2
            # Double-headed arrow
            draw.line([(cx1 + 20, cy1), (cx2 - 20, cy2)], fill=C_LIGHT, width=2)

    # Bottom: equals sign showing similarity
    tc(draw, 360, 400, "≈", F_SYMBOL, C_MID)

    return save_image(img, "llm_shared_weaknesses")

if __name__ == "__main__":
    generate()
