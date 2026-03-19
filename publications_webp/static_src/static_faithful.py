# publications_webp/static_src/static_faithful.py
"""
Self-explanations help predict model behavior: +11-37% accuracy.
Visual: LLM with explanation bubble → predictor → bars showing improvement.
Minimal text: just visual flow and symbols.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: LLM producing answer + explanation ===
    llm_cx, llm_cy = 140, 180

    draw_box(draw, llm_cx, llm_cy, 110, 80, C_LAVENDER, r=12)
    # Neural dots inside
    for dx, dy in [(-25, -15), (0, -15), (25, -15), (-12, 10), (12, 10)]:
        draw_circle(draw, llm_cx + dx, llm_cy + dy, 8, darken(C_LAVENDER, 0.25))

    # Answer output (simple box)
    ans_x, ans_y = 260, 130
    draw_box(draw, ans_x, ans_y, 70, 45, C_MINT, r=8)
    draw.line([(ans_x - 20, ans_y - 8), (ans_x + 20, ans_y - 8)], fill=darken(C_MINT, 0.2), width=3)
    draw.line([(ans_x - 15, ans_y + 5), (ans_x + 15, ans_y + 5)], fill=darken(C_MINT, 0.2), width=3)

    # Explanation output (speech bubble style)
    exp_x, exp_y = 260, 230
    draw_box(draw, exp_x, exp_y, 90, 55, C_PEACH, r=8)
    # Multiple lines inside
    for i, w in enumerate([50, 35, 45]):
        ly = exp_y - 12 + i * 12
        draw.line([(exp_x - 30, ly), (exp_x - 30 + w, ly)], fill=darken(C_PEACH, 0.2), width=2)

    # Arrows from LLM to outputs
    draw_arrow(draw, llm_cx + 60, llm_cy - 25, ans_x - 40, ans_y, C_LIGHT, width=3, head=10)
    draw_arrow(draw, llm_cx + 60, llm_cy + 25, exp_x - 50, exp_y, C_LIGHT, width=3, head=10)

    # === MIDDLE: Predictor ===
    pred_cx, pred_cy = 420, 180

    draw_box(draw, pred_cx, pred_cy, 100, 70, C_BLUE, r=12)
    # Eye symbol (predictor observing)
    draw.ellipse([pred_cx - 18, pred_cy - 12, pred_cx + 18, pred_cy + 12],
                 fill=C_CREAM, outline=darken(C_BLUE, 0.3), width=2)
    draw_circle(draw, pred_cx, pred_cy, 8, darken(C_BLUE, 0.4))

    # Arrow from answer (thin - partial info)
    draw.line([(ans_x + 40, ans_y), (pred_cx - 55, pred_cy - 20)], fill=C_LIGHT, width=2)

    # Arrow from explanation (thick - key info)
    draw_arrow(draw, exp_x + 50, exp_y, pred_cx - 55, pred_cy + 15, darken(C_PEACH, 0.2), width=4, head=12)

    # === RIGHT: Results comparison ===
    bar_w, bar_h = 65, 130
    bar_y = 380

    # Without explanation (lower)
    wo_x = 520
    draw_bar(draw, wo_x, bar_y, bar_w, bar_h, C_GRAY, 0.58)

    # With explanation (higher)
    w_x = 620
    draw_bar(draw, w_x, bar_y, bar_w, bar_h, C_MINT, 0.82)

    # Upward arrow showing improvement
    up_x = (wo_x + w_x) // 2
    draw.line([(up_x, bar_y - bar_h * 0.58 + 15), (up_x, bar_y - bar_h * 0.82 - 10)],
              fill=darken(C_POS, 0.2), width=4)
    draw.polygon([(up_x - 8, bar_y - bar_h * 0.82 - 5),
                  (up_x + 8, bar_y - bar_h * 0.82 - 5),
                  (up_x, bar_y - bar_h * 0.82 - 20)], fill=darken(C_POS, 0.2))

    # Checkmark above better bar
    check_x, check_y = w_x, bar_y - bar_h * 0.82 - 40
    draw.line([(check_x - 12, check_y), (check_x - 3, check_y + 15)], fill=darken(C_POS, 0.2), width=5)
    draw.line([(check_x - 3, check_y + 15), (check_x + 18, check_y - 10)], fill=darken(C_POS, 0.2), width=5)

    return save_image(img, "faithful")

if __name__ == "__main__":
    generate()
