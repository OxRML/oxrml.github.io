# publications_webp/static_src/static_lingolytoo.py
"""
LingOly-TOO: Obfuscation preserves meaning, scrambles surface form.
Visual: Word card transforms → same meaning bubble → score bars drop.
Minimal text: just the example words and score numbers.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Original word card ===
    card_w, card_h = 180, 100
    left_cx = 160

    draw_box(draw, left_cx, 180, card_w, card_h, C_BLUE)
    tc(draw, left_cx, 165, "Ufgent", F_TITLE, darken(C_BLUE, 0.5))

    # Meaning bubble below (small, connected)
    draw_circle(draw, left_cx, 260, 35, C_CREAM)
    tc(draw, left_cx, 260, "flew", F_SMALL, C_MID)

    # === TRANSFORMATION ARROW ===
    arrow_y = 180
    draw_arrow(draw, 270, arrow_y, 410, arrow_y, C_LIGHT, width=4, head=14)

    # Scramble effect dots along arrow
    for i, dx in enumerate([300, 330, 360, 390]):
        size = 4 + (i % 2) * 2
        col = lc(C_BLUE, C_PEACH, i / 3)
        draw_circle(draw, dx, arrow_y - 15 + (i % 2) * 8, size, col)

    # === RIGHT: Obfuscated word card ===
    right_cx = 560

    draw_box(draw, right_cx, 180, card_w, card_h, C_PEACH)
    tc(draw, right_cx, 165, "Eqcawg", F_TITLE, darken(C_PEACH, 0.5))

    # Same meaning bubble (identical to show preservation)
    draw_circle(draw, right_cx, 260, 35, C_CREAM)
    tc(draw, right_cx, 260, "flew", F_SMALL, C_MID)

    # Equals sign between meaning bubbles
    tc(draw, 360, 260, "=", F_SYMBOL, C_MID)

    # === BOTTOM: Score comparison ===
    bar_w, bar_h = 70, 110
    bar_y = 400

    # Original bar (higher)
    left_bar = 280
    draw_bar(draw, left_bar, bar_y, bar_w, bar_h, darken(C_BLUE, 0.1), 0.79)
    tc(draw, left_bar, bar_y - bar_h * 0.79 - 20, ".59", F_LABEL, C_DARK)

    # Obfuscated bar (lower)
    right_bar = 440
    draw_bar(draw, right_bar, bar_y, bar_w, bar_h, darken(C_PEACH, 0.1), 0.61)
    tc(draw, right_bar, bar_y - bar_h * 0.61 - 20, ".48", F_LABEL, C_DARK)

    # Drop arrow between bars
    mid_bar = (left_bar + right_bar) // 2
    draw.line([(mid_bar, bar_y - bar_h * 0.79 + 15), (mid_bar, bar_y - bar_h * 0.61 - 5)],
              fill=C_NEG, width=3)
    draw.polygon([(mid_bar - 6, bar_y - bar_h * 0.61),
                  (mid_bar + 6, bar_y - bar_h * 0.61),
                  (mid_bar, bar_y - bar_h * 0.61 + 10)], fill=C_NEG)

    return save_image(img, "lingolytoo")

if __name__ == "__main__":
    generate()
