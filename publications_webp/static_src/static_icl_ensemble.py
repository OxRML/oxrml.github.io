# publications_webp/static_src/static_icl_ensemble.py
"""
SLM Ensemble: Multiple small models advise large LLM → better results.
Visual: Small SLM circles feeding into large LLM → performance bars.
Minimal text: just SLM dots, LLM box, and checkmark.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *
import math

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # SLM positions (arc formation)
    slm_colors = [C_BLUE, C_PEACH, C_MINT, C_LAVENDER, C_CORAL]
    slm_positions = [
        (100, 130),
        (200, 90),
        (300, 75),
        (400, 90),
        (500, 130),
    ]

    # Draw SLMs as small circles with dots inside
    for (sx, sy), col in zip(slm_positions, slm_colors):
        draw_circle(draw, sx, sy, 35, col)
        # Neural dots inside
        for dx, dy in [(-10, -8), (10, -8), (0, 10)]:
            draw_circle(draw, sx + dx, sy + dy, 6, darken(col, 0.25))

    # Central LLM (larger)
    llm_cx, llm_cy = 300, 250
    llm_r = 65
    draw_circle(draw, llm_cx, llm_cy, llm_r, C_CREAM, outline=darken(C_CREAM, 0.2), width=4)

    # Neural network dots inside LLM
    for dx, dy in [(-20, -20), (0, -20), (20, -20), (-10, 5), (10, 5), (0, 25)]:
        draw_circle(draw, llm_cx + dx, llm_cy + dy, 8, darken(C_CREAM, 0.2))

    # Curved lines from SLMs to LLM with signal dots
    for i, ((sx, sy), col) in enumerate(zip(slm_positions, slm_colors)):
        mid_x = (sx + llm_cx) // 2
        mid_y = (sy + llm_cy) // 2 - 20

        # Draw bezier-like curve
        steps = 10
        pts = []
        for t_idx in range(steps + 1):
            tt = t_idx / steps
            px = (1 - tt) ** 2 * sx + 2 * (1 - tt) * tt * mid_x + tt ** 2 * llm_cx
            py = (1 - tt) ** 2 * (sy + 35) + 2 * (1 - tt) * tt * mid_y + tt ** 2 * (llm_cy - llm_r)
            pts.append((int(px), int(py)))

        for j in range(len(pts) - 1):
            draw.line([pts[j], pts[j + 1]], fill=lighten(col, 0.3), width=3)

        # Signal dot on path
        t = 0.5 + i * 0.08
        px = (1 - t) ** 2 * sx + 2 * (1 - t) * t * mid_x + t ** 2 * llm_cx
        py = (1 - t) ** 2 * (sy + 35) + 2 * (1 - t) * t * mid_y + t ** 2 * (llm_cy - llm_r)
        draw_circle(draw, int(px), int(py), 8, col)

    # Arrow to output
    draw_arrow(draw, llm_cx + llm_r + 20, llm_cy, 500, llm_cy, C_LIGHT, width=4, head=14)

    # Comparison bars
    bar_w, bar_h = 55, 130
    bar_y = 400

    # Without ensemble (lower)
    draw_bar(draw, 540, bar_y, bar_w, bar_h, C_GRAY, 0.52)

    # With ensemble (higher)
    draw_bar(draw, 620, bar_y, bar_w, bar_h, C_MINT, 0.78)

    # Checkmark above higher bar
    check_x, check_y = 620, bar_y - bar_h * 0.78 - 30
    draw.line([(check_x - 15, check_y), (check_x - 4, check_y + 18)], fill=darken(C_POS, 0.2), width=5)
    draw.line([(check_x - 4, check_y + 18), (check_x + 20, check_y - 12)], fill=darken(C_POS, 0.2), width=5)

    # Star badge
    draw_circle(draw, 620, bar_y - bar_h - 55, 20, C_GOLD)
    tc(draw, 620, bar_y - bar_h - 55, "★", F_LABEL, darken(C_GOLD, 0.4))

    return save_image(img, "icl_ensemble")

if __name__ == "__main__":
    generate()
