# publications_webp/static_src/static_helpmed.py
"""
LLM alone 94.9%, with real users only 34.5% - interaction is the challenge.
Visual: LLM alone (high bar) → user interaction → dramatic drop (low bar).
Minimal text: just visual comparison with arrows.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: LLM alone (high performance) ===
    alone_cx = 140
    bar_y = 350
    bar_w, bar_h = 80, 180

    # LLM box
    draw_box(draw, alone_cx, 120, 100, 70, C_LAVENDER, r=12)
    for dx, dy in [(-20, -10), (0, -10), (20, -10), (-10, 10), (10, 10)]:
        draw_circle(draw, alone_cx + dx, 120 + dy, 7, darken(C_LAVENDER, 0.25))

    # High performance bar
    draw_bar(draw, alone_cx, bar_y, bar_w, bar_h, C_MINT, 0.95)

    # Checkmark above
    check_x, check_y = alone_cx, bar_y - bar_h * 0.95 - 25
    draw.line([(check_x - 15, check_y), (check_x - 4, check_y + 18)], fill=darken(C_POS, 0.2), width=5)
    draw.line([(check_x - 4, check_y + 18), (check_x + 20, check_y - 12)], fill=darken(C_POS, 0.2), width=5)

    # === MIDDLE: User interaction ===
    mid_cx = 360
    mid_y = 180

    # Arrow from LLM
    draw_arrow(draw, alone_cx + 60, 120, mid_cx - 90, mid_y, C_LIGHT, width=3, head=12)

    # User icon (head + shoulders)
    user_x = mid_cx - 50
    draw_circle(draw, user_x, mid_y - 30, 22, C_PEACH)
    draw.arc([user_x - 30, mid_y - 5, user_x + 30, mid_y + 45], 0, 180,
             fill=darken(C_PEACH, 0.15), width=4)

    # LLM icon
    llm_x = mid_cx + 50
    draw_box(draw, llm_x, mid_y - 10, 55, 50, C_BLUE, r=8)
    for dx, dy in [(-12, -8), (12, -8), (0, 10)]:
        draw_circle(draw, llm_x + dx, mid_y - 10 + dy, 6, darken(C_BLUE, 0.25))

    # Chat bubbles between them
    draw_box(draw, mid_cx - 15, mid_y - 60, 35, 22, C_CREAM, r=6)
    draw_box(draw, mid_cx + 20, mid_y - 35, 35, 22, C_CREAM, r=6)
    draw_box(draw, mid_cx - 10, mid_y + 25, 35, 22, C_CREAM, r=6)

    # Bidirectional arrows
    draw.line([(user_x + 30, mid_y - 20), (llm_x - 35, mid_y - 20)], fill=C_LIGHT, width=2)
    draw.line([(llm_x - 35, mid_y), (user_x + 30, mid_y + 10)], fill=C_LIGHT, width=2)

    # Arrow to result
    draw_arrow(draw, mid_cx + 90, mid_y, 520, mid_y, C_LIGHT, width=3, head=12)

    # === RIGHT: With users (low performance) ===
    result_cx = 580

    # Low performance bar
    draw_bar(draw, result_cx, bar_y, bar_w, bar_h, C_CORAL, 0.35)

    # X mark above
    x_cx, x_cy = result_cx, bar_y - bar_h * 0.35 - 30
    x_size = 18
    draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=5)
    draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=5)

    # === Drop indicator ===
    drop_y = 395

    # Horizontal line showing comparison
    draw.line([(alone_cx, bar_y - bar_h * 0.95 + 20), (alone_cx, drop_y)], fill=C_LIGHT, width=2)
    draw.line([(result_cx, bar_y - bar_h * 0.35 + 20), (result_cx, drop_y)], fill=C_LIGHT, width=2)

    # Drop arrow
    draw.line([(alone_cx + 30, drop_y), (result_cx - 30, drop_y)], fill=C_NEG, width=3)
    draw.polygon([(result_cx - 40, drop_y - 8), (result_cx - 40, drop_y + 8), (result_cx - 25, drop_y)],
                 fill=C_NEG)

    # Not equal symbol
    tc(draw, 360, drop_y + 30, "≠", F_SYMBOL, C_MID)

    return save_image(img, "helpmed")

if __name__ == "__main__":
    generate()
