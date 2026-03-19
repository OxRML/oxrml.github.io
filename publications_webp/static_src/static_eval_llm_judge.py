# publications_webp/static_src/static_eval_llm_judge.py
"""
PolyVis: Evaluating LLM judges across languages and modalities.
Visual: Language flags + image/text icons → Judge → task grid with varied performance.
Minimal text: just symbols and visual grid.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Language diversity (flags/boxes) ===
    lang_cx = 120
    lang_y_start = 100

    lang_colors = [C_BLUE, C_PEACH, C_CORAL, C_MINT, C_LAVENDER, C_GOLD]

    for i, col in enumerate(lang_colors):
        row, col_idx = i // 3, i % 3
        lx = lang_cx - 45 + col_idx * 50
        ly = lang_y_start + row * 60
        draw_box(draw, lx, ly, 40, 35, col, r=6)
        # Text-like lines inside
        draw.line([(lx - 12, ly), (lx + 12, ly)], fill=darken(col, 0.3), width=2)

    # === LEFT BOTTOM: Modality icons ===
    mod_y = 260

    # Image icon
    img_x = lang_cx - 40
    draw_box(draw, img_x, mod_y, 55, 50, C_BLUE, r=6)
    # Mountain in image
    draw.polygon([(img_x - 15, mod_y + 15),
                  (img_x, mod_y - 8),
                  (img_x + 15, mod_y + 15)], fill=darken(C_BLUE, 0.25))

    # Text icon
    txt_x = lang_cx + 40
    draw_box(draw, txt_x, mod_y, 55, 50, C_PEACH, r=6)
    for i in range(3):
        draw.line([(txt_x - 18, mod_y - 12 + i * 12),
                   (txt_x + 12 - i * 6, mod_y - 12 + i * 12)],
                  fill=darken(C_PEACH, 0.25), width=3)

    # Arrows to judge
    draw_arrow(draw, lang_cx + 80, lang_y_start + 50, 270, 200, C_LIGHT, width=3, head=10)
    draw_arrow(draw, lang_cx + 80, mod_y, 270, 220, C_LIGHT, width=3, head=10)

    # === CENTER: Judge LLM ===
    judge_cx, judge_cy = 350, 210

    draw_box(draw, judge_cx, judge_cy, 120, 90, C_LAVENDER, r=14)

    # Gavel/judge symbol
    draw_circle(draw, judge_cx, judge_cy - 10, 25, darken(C_LAVENDER, 0.15))
    tc(draw, judge_cx, judge_cy - 10, "⚖", F_TITLE, darken(C_LAVENDER, 0.5))

    # Arrow to results
    draw_arrow(draw, judge_cx + 70, judge_cy, 470, judge_cy, C_LIGHT, width=4, head=14)

    # === RIGHT: Task performance grid ===
    grid_x = 570
    grid_y_start = 110

    tasks = [
        (C_CORAL, 0.72),
        (C_MINT, 0.68),
        (C_BLUE, 0.65),
    ]

    bar_w = 110
    bar_h = 25

    for i, (col, score) in enumerate(tasks):
        ty = grid_y_start + i * 65

        # Icon circle
        draw_circle(draw, grid_x - 70, ty + bar_h//2, 20, col)

        # Score bar
        rrect(draw, [grid_x - 40, ty, grid_x + bar_w - 40, ty + bar_h], r=6, fill=C_GRAY)
        fill_w = int(bar_w * score)
        if fill_w > 6:
            rrect(draw, [grid_x - 40, ty, grid_x - 40 + fill_w, ty + bar_h], r=6, fill=col)

    # Variance indicator (~)
    tc(draw, grid_x + 30, grid_y_start + 3 * 65, "~", F_SYMBOL, C_MID)

    # Bottom arrows showing language affects performance
    for i in range(3):
        draw.line([(grid_x - 40, grid_y_start + 30 + i * 65),
                   (grid_x - 40, grid_y_start + 50 + i * 65)], fill=C_LIGHT, width=2)

    return save_image(img, "eval_llm_judge")

if __name__ == "__main__":
    generate()
