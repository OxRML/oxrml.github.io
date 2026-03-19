# publications_webp/static_src/static_lingoly_one.py
"""
LingOly: Olympiad puzzles in 90+ low-resource languages. Models struggle.
Visual: Globe with language dots → puzzle box → low performance bars.
Minimal text: just symbols and visual elements.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *
import math

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Globe with language diversity ===
    globe_cx, globe_cy = 160, 200
    globe_r = 90

    # Globe circle
    draw_circle(draw, globe_cx, globe_cy, globe_r, lighten(C_BLUE, 0.5), outline=C_BLUE, width=3)

    # Latitude/longitude lines
    for i in range(-2, 3):
        lat_y = globe_cy + i * 25
        lat_r = int(math.sqrt(globe_r**2 - (i*25)**2)) if abs(i*25) < globe_r else 0
        if lat_r > 10:
            draw.arc([globe_cx - lat_r, lat_y - 5, globe_cx + lat_r, lat_y + 5],
                     0, 180, fill=lighten(C_BLUE, 0.2), width=1)

    # Meridians
    draw.arc([globe_cx - 30, globe_cy - globe_r, globe_cx + 30, globe_cy + globe_r],
             0, 360, fill=lighten(C_BLUE, 0.2), width=1)

    # Language dots scattered on globe
    lang_colors = [C_CORAL, C_PEACH, C_MINT, C_LAVENDER, C_GOLD, C_TEAL]
    lang_positions = [
        (-50, -40), (30, -50), (-20, 10), (45, 20), (-40, 50), (20, 60),
        (-60, -10), (55, -20), (10, -30), (-30, 40)
    ]
    for i, (dx, dy) in enumerate(lang_positions):
        if dx*dx + dy*dy < globe_r*globe_r * 0.85:
            draw_circle(draw, globe_cx + dx, globe_cy + dy, 8, lang_colors[i % len(lang_colors)])

    # Arrow to puzzle
    draw_arrow(draw, globe_cx + globe_r + 20, globe_cy, 320, globe_cy, C_LIGHT, width=4, head=14)

    # === MIDDLE: Puzzle/question box ===
    puzzle_cx = 400
    puzzle_cy = 200

    draw_box(draw, puzzle_cx, puzzle_cy, 120, 100, C_LAVENDER, r=12)

    # Question mark
    tc(draw, puzzle_cx, puzzle_cy, "?", F_SYMBOL, darken(C_LAVENDER, 0.4))

    # Puzzle piece indicators
    for dx, dy in [(-45, -35), (45, -35), (-45, 35), (45, 35)]:
        draw_circle(draw, puzzle_cx + dx, puzzle_cy + dy, 12, C_CREAM)

    # Arrow to results
    draw_arrow(draw, puzzle_cx + 70, puzzle_cy, 520, puzzle_cy, C_LIGHT, width=4, head=14)

    # === RIGHT: Low performance bars ===
    bar_w, bar_h = 50, 140
    bar_y = 350

    bars = [
        (540, 0.48, C_BLUE),
        (600, 0.45, C_PEACH),
        (660, 0.35, C_MINT),
    ]

    for bx, frac, col in bars:
        draw_bar(draw, bx, bar_y, bar_w, bar_h, col, frac)

    # X mark showing difficulty
    x_cx, x_cy = 600, bar_y - bar_h - 30
    x_size = 20
    draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=5)
    draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=5)

    # Down arrow showing poor performance
    draw.line([(600, bar_y + 10), (600, bar_y + 50)], fill=C_NEG, width=4)
    draw.polygon([(592, bar_y + 45), (608, bar_y + 45), (600, bar_y + 60)], fill=C_NEG)

    return save_image(img, "lingoly_one")

if __name__ == "__main__":
    generate()
