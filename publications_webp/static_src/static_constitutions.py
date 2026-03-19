# publications_webp/static_src/static_constitutions.py
"""
Constitutions: Detailed helps emotive skills, NOT practical.
Visual: Document → LLM → Two bar comparisons (emotive: detailed wins, practical: equal).
Minimal text: emoji-like icons, check/equals symbols.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def draw_document(draw, cx, cy, w, h, col, num_lines=4):
    """Document icon with lines inside."""
    draw_box(draw, cx, cy, w, h, col, r=8)
    x0 = cx - w//2 + 12
    spacing = (h - 20) // (num_lines + 1)
    for i in range(num_lines):
        ly = cy - h//2 + 10 + (i + 1) * spacing
        lw = w - 24 - (i % 2) * 15
        draw.line([(x0, ly), (x0 + lw, ly)], fill=darken(col, 0.15), width=3)

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === TOP: Pipeline ===
    pipe_y = 100

    # Document (constitution)
    draw_document(draw, 120, pipe_y, 90, 80, C_BLUE, num_lines=5)

    # Arrow
    draw_arrow(draw, 175, pipe_y, 260, pipe_y, C_LIGHT, width=3, head=10)

    # LLM box
    draw_box(draw, 330, pipe_y, 100, 70, C_LAVENDER)
    # Neural dots inside
    for dx, dy in [(-18, -10), (0, -10), (18, -10), (-9, 10), (9, 10)]:
        draw_circle(draw, 330 + dx, pipe_y + dy, 7, darken(C_LAVENDER, 0.2))

    # Arrow
    draw_arrow(draw, 390, pipe_y, 475, pipe_y, C_LIGHT, width=3, head=10)

    # Feedback bubble
    draw_box(draw, 560, pipe_y, 110, 70, C_CREAM)
    # Lines inside
    for i, lw in enumerate([55, 40, 50]):
        ly = pipe_y - 18 + i * 14
        draw.line([(560 - 40, ly), (560 - 40 + lw, ly)], fill=C_LIGHT, width=2)

    # === BOTTOM: Results comparison ===

    # EMOTIVE section (left)
    em_cx = 200
    bar_y = 370
    bar_w, bar_h = 55, 120

    # Heart icon for emotive
    draw_circle(draw, em_cx, 220, 30, C_CORAL)
    tc(draw, em_cx, 220, "♥", F_LABEL, lighten(C_CORAL, 0.5))

    # Basic bar (shorter)
    draw_bar(draw, em_cx - 40, bar_y, bar_w, bar_h, C_PEACH, 0.45)

    # Detailed bar (taller) - wins!
    draw_bar(draw, em_cx + 40, bar_y, bar_w, bar_h, C_BLUE, 0.82)

    # Checkmark above detailed
    check_x, check_y = em_cx + 40, bar_y - bar_h * 0.82 - 25
    draw.line([(check_x - 12, check_y), (check_x - 3, check_y + 14)], fill=darken(C_POS, 0.2), width=4)
    draw.line([(check_x - 3, check_y + 14), (check_x + 16, check_y - 10)], fill=darken(C_POS, 0.2), width=4)

    # PRACTICAL section (right)
    pr_cx = 520

    # Clipboard icon for practical
    draw_box(draw, pr_cx, 220, 50, 60, C_MINT, r=6)
    for i in range(3):
        draw.line([(pr_cx - 15, 205 + i * 15), (pr_cx + 15, 205 + i * 15)],
                  fill=darken(C_MINT, 0.2), width=2)

    # Both bars equal height
    draw_bar(draw, pr_cx - 40, bar_y, bar_w, bar_h, C_PEACH, 0.55)
    draw_bar(draw, pr_cx + 40, bar_y, bar_w, bar_h, C_BLUE, 0.55)

    # Equals sign between
    eq_y = bar_y - bar_h * 0.55 - 20
    draw.line([(pr_cx - 15, eq_y - 6), (pr_cx + 15, eq_y - 6)], fill=C_MID, width=4)
    draw.line([(pr_cx - 15, eq_y + 6), (pr_cx + 15, eq_y + 6)], fill=C_MID, width=4)

    return save_image(img, "constitutions")

if __name__ == "__main__":
    generate()
