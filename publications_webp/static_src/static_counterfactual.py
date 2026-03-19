# publications_webp/static_src/static_counterfactual.py
"""
Counterfactual trade-off: Valid but excessive OR minimal but invalid.
Visual: Decision boundary with two scenarios showing the dilemma.
Minimal text: just symbols (✓, ✗) and visual arrows.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # Background split (green region / white region)
    # Decision boundary diagonal
    draw.polygon([(100, 380), (620, 80), (620, 380)], fill=lighten(C_MINT, 0.7))

    # Decision boundary line
    draw.line([(100, 380), (620, 80)], fill=darken(C_LAVENDER, 0.2), width=4)

    # === Original point (bottom left region) ===
    orig_x, orig_y = 200, 300
    draw_circle(draw, orig_x, orig_y, 18, C_CORAL)

    # === SCENARIO 1: Valid but NOT minimal (large jump) ===
    # Target far inside green region
    valid_x, valid_y = 480, 150
    draw_circle(draw, valid_x, valid_y, 18, C_BLUE)

    # Long curved arrow showing big jump
    mid_x = (orig_x + valid_x) // 2 - 30
    mid_y = (orig_y + valid_y) // 2 - 50

    # Draw bezier-like path
    steps = 15
    pts = []
    for t in range(steps + 1):
        tt = t / steps
        px = (1 - tt) ** 2 * (orig_x + 20) + 2 * (1 - tt) * tt * mid_x + tt ** 2 * (valid_x - 20)
        py = (1 - tt) ** 2 * (orig_y - 10) + 2 * (1 - tt) * tt * mid_y + tt ** 2 * (valid_y + 10)
        pts.append((int(px), int(py)))

    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=darken(C_BLUE, 0.2), width=4)

    # Arrowhead
    draw.polygon([(valid_x - 25, valid_y + 5), (valid_x - 15, valid_y + 20), (valid_x - 5, valid_y + 10)],
                 fill=darken(C_BLUE, 0.2))

    # Checkmark (valid) next to target
    check_x, check_y = valid_x + 35, valid_y - 15
    draw.line([(check_x - 10, check_y), (check_x - 3, check_y + 12)], fill=darken(C_POS, 0.2), width=4)
    draw.line([(check_x - 3, check_y + 12), (check_x + 14, check_y - 8)], fill=darken(C_POS, 0.2), width=4)

    # X mark (not minimal) - too much change
    x_cx, x_cy = (orig_x + valid_x) // 2 - 20, (orig_y + valid_y) // 2 - 70
    x_size = 14
    draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=4)
    draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=4)

    # === SCENARIO 2: Minimal but NOT valid (small jump, doesn't cross) ===
    # Target just slightly moved, still in same region
    min_orig_x, min_orig_y = 350, 260
    draw_circle(draw, min_orig_x, min_orig_y, 14, lighten(C_CORAL, 0.3), outline=C_CORAL, width=2)

    min_target_x, min_target_y = 380, 245
    draw_circle(draw, min_target_x, min_target_y, 14, C_PEACH)

    # Short arrow
    draw.line([(min_orig_x + 12, min_orig_y - 8), (min_target_x - 12, min_target_y + 8)],
              fill=darken(C_PEACH, 0.25), width=3)

    # X mark (not valid - didn't cross boundary)
    x_cx2, x_cy2 = min_target_x + 30, min_target_y - 20
    draw.line([(x_cx2 - x_size, x_cy2 - x_size), (x_cx2 + x_size, x_cy2 + x_size)], fill=C_NEG, width=4)
    draw.line([(x_cx2 + x_size, x_cy2 - x_size), (x_cx2 - x_size, x_cy2 + x_size)], fill=C_NEG, width=4)

    # Checkmark (minimal) - small change
    check_x2, check_y2 = (min_orig_x + min_target_x) // 2, (min_orig_y + min_target_y) // 2 + 30
    draw.line([(check_x2 - 8, check_y2), (check_x2 - 2, check_y2 + 10)], fill=darken(C_POS, 0.2), width=3)
    draw.line([(check_x2 - 2, check_y2 + 10), (check_x2 + 12, check_y2 - 6)], fill=darken(C_POS, 0.2), width=3)

    # === Bottom: Trade-off symbol ===
    tc(draw, 360, 400, "⇄", F_SYMBOL, C_MID)

    return save_image(img, "counterfactual")

if __name__ == "__main__":
    generate()
