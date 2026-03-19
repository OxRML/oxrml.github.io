# publications_webp/static_src/static_mwm.py
"""
Measuring What Matters: Review of 445 LLM benchmarks → validity issues.
Visual: Paper funnel → validity chain → checklist recommendations.
Minimal text: just symbols and visual elements.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Paper funnel ===
    funnel_cx = 130
    funnel_y = 190

    # Funnel shape
    draw.polygon([
        (funnel_cx - 70, funnel_y - 80),
        (funnel_cx + 70, funnel_y - 80),
        (funnel_cx + 35, funnel_y + 20),
        (funnel_cx - 35, funnel_y + 20),
    ], fill=C_BLUE, outline=darken(C_BLUE, 0.2), width=2)

    # Narrow part
    rrect(draw, [funnel_cx - 25, funnel_y + 20, funnel_cx + 25, funnel_y + 70],
          r=5, fill=C_BLUE, outline=darken(C_BLUE, 0.2))

    # Papers falling into funnel
    for dx, dy in [(-35, -60), (0, -70), (35, -55), (-20, -45), (25, -40)]:
        draw_box(draw, funnel_cx + dx, funnel_y + dy, 22, 18, C_CREAM, r=3)

    # Output papers (fewer)
    for i in range(3):
        draw_box(draw, funnel_cx, funnel_y + 85 + i * 20, 18, 14, C_CREAM, r=2)

    # Arrow to validity chain
    draw_arrow(draw, funnel_cx + 80, funnel_y, 240, funnel_y, C_LIGHT, width=4, head=14)

    # === MIDDLE: Validity chain (phenomenon → task → metric → claims) ===
    chain_cx = 350
    chain_y_start = 100

    chain_colors = [C_LAVENDER, C_MINT, C_PEACH, C_BLUE]
    box_h = 50
    box_w = 90

    for i, col in enumerate(chain_colors):
        by = chain_y_start + i * 65
        draw_box(draw, chain_cx, by, box_w, box_h, col, r=10)

        # Question mark (validity concern)
        tc(draw, chain_cx + 60, by, "?", F_LABEL, C_MID)

        # Arrow down
        if i < len(chain_colors) - 1:
            draw.line([(chain_cx, by + box_h//2 + 5), (chain_cx, by + box_h//2 + 15)],
                      fill=C_LIGHT, width=3)
            draw.polygon([(chain_cx - 6, by + box_h//2 + 12),
                          (chain_cx + 6, by + box_h//2 + 12),
                          (chain_cx, by + box_h//2 + 22)], fill=C_LIGHT)

    # Warning indicator
    draw_circle(draw, chain_cx - 70, chain_y_start + 130, 25, C_CORAL)
    tc(draw, chain_cx - 70, chain_y_start + 130, "!", F_LABEL, C_DARK)

    # Arrow to recommendations
    draw_arrow(draw, chain_cx + 70, chain_y_start + 130, 500, chain_y_start + 130, C_LIGHT, width=4, head=14)

    # === RIGHT: Recommendations checklist ===
    rec_cx = 600
    rec_y_start = 90

    for i in range(6):
        ry = rec_y_start + i * 45

        # Checkbox
        cb_x = rec_cx - 40
        draw_box(draw, cb_x, ry, 24, 24, C_MINT, r=5)

        # Checkmark inside
        draw.line([(cb_x - 6, ry), (cb_x - 1, ry + 8)], fill=darken(C_POS, 0.2), width=3)
        draw.line([(cb_x - 1, ry + 8), (cb_x + 8, ry - 5)], fill=darken(C_POS, 0.2), width=3)

        # Line representing recommendation text
        draw.line([(cb_x + 20, ry), (cb_x + 70, ry)], fill=C_LIGHT, width=3)

    # "8" badge showing total recommendations
    draw_circle(draw, rec_cx + 40, rec_y_start + 120, 25, C_GOLD)
    tc(draw, rec_cx + 40, rec_y_start + 120, "8", F_LABEL, darken(C_GOLD, 0.5))

    return save_image(img, "mwm")

if __name__ == "__main__":
    generate()
