# publications_webp/static_src/static_llm_landscape_med.py
"""
LLM Medical QA: Benchmark 8 LLMs, accuracy correlates with confidence.
Visual: Model bars → correlation indicators (+ confidence, - length).
Minimal text: just bars and correlation symbols.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Model ranking bars ===
    models = [
        (0.82, C_BLUE),
        (0.67, C_MINT),
        (0.65, C_PEACH),
        (0.63, C_LAVENDER),
        (0.60, C_GOLD),
    ]

    bar_w = 180
    bar_h = 32
    bar_x = 50
    bar_y_start = 100

    for i, (score, col) in enumerate(models):
        by = bar_y_start + i * 55

        # Bar track
        rrect(draw, [bar_x, by, bar_x + bar_w, by + bar_h], r=8, fill=C_GRAY)

        # Filled portion
        fill_w = int(bar_w * score)
        if fill_w > 8:
            rrect(draw, [bar_x, by, bar_x + fill_w, by + bar_h], r=8, fill=col)

        # Neural dot indicator
        draw_circle(draw, bar_x + fill_w + 20, by + bar_h//2, 10, col)

    # Arrow to pattern insights
    draw_arrow(draw, bar_x + bar_w + 50, bar_y_start + 120, 380, 200, C_LIGHT, width=4, head=14)

    # === RIGHT: Correlation patterns ===
    pattern_cx = 520
    pattern_y_start = 110

    # Pattern 1: Confidence → positive correlation
    p1_y = pattern_y_start
    draw_box(draw, pattern_cx, p1_y, 180, 60, C_MINT, r=10)

    # Up arrow showing positive correlation
    draw.line([(pattern_cx - 50, p1_y + 15), (pattern_cx - 50, p1_y - 15)], fill=darken(C_POS, 0.2), width=4)
    draw.polygon([(pattern_cx - 58, p1_y - 10), (pattern_cx - 42, p1_y - 10), (pattern_cx - 50, p1_y - 25)],
                 fill=darken(C_POS, 0.2))

    # Plus sign
    tc(draw, pattern_cx + 40, p1_y, "+", F_SYMBOL, darken(C_POS, 0.3))

    # Pattern 2: Question length → negative correlation
    p2_y = pattern_y_start + 90
    draw_box(draw, pattern_cx, p2_y, 180, 60, C_CORAL, r=10)

    # Down arrow showing negative correlation
    draw.line([(pattern_cx - 50, p2_y - 15), (pattern_cx - 50, p2_y + 15)], fill=darken(C_NEG, 0.2), width=4)
    draw.polygon([(pattern_cx - 58, p2_y + 10), (pattern_cx - 42, p2_y + 10), (pattern_cx - 50, p2_y + 25)],
                 fill=darken(C_NEG, 0.2))

    # Minus sign
    tc(draw, pattern_cx + 40, p2_y, "−", F_SYMBOL, darken(C_NEG, 0.3))

    # Pattern 3: Human difficulty → positive correlation
    p3_y = pattern_y_start + 180
    draw_box(draw, pattern_cx, p3_y, 180, 60, C_BLUE, r=10)

    # Up arrow
    draw.line([(pattern_cx - 50, p3_y + 15), (pattern_cx - 50, p3_y - 15)], fill=darken(C_POS, 0.2), width=4)
    draw.polygon([(pattern_cx - 58, p3_y - 10), (pattern_cx - 42, p3_y - 10), (pattern_cx - 50, p3_y - 25)],
                 fill=darken(C_POS, 0.2))

    # Plus sign
    tc(draw, pattern_cx + 40, p3_y, "+", F_SYMBOL, darken(C_POS, 0.3))

    # === Bottom: Similarity indicator ===
    tc(draw, 280, 390, "≈", F_SYMBOL, C_MID)

    # Equal performance pattern across models
    for i, col in enumerate([C_BLUE, C_MINT, C_PEACH]):
        draw_circle(draw, 350 + i * 40, 390, 15, col)

    return save_image(img, "llm_landscape_med")

if __name__ == "__main__":
    generate()
