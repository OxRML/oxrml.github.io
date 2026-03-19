# publications_webp/static_src/static_cardiac_auscultation.py
"""
AI cardiac screening: Research → deployment gap → real-world clinic.
Visual: Research model → gap/challenges → clinic setting.
Minimal text: just symbols and visual flow.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Research setting ===
    lab_cx, lab_cy = 130, 200

    draw_box(draw, lab_cx, lab_cy, 150, 130, C_LAVENDER, r=14)

    # Model box inside
    draw_box(draw, lab_cx, lab_cy - 10, 100, 60, C_BLUE, r=10)
    # Neural dots
    for dx, dy in [(-25, -10), (0, -10), (25, -10), (-12, 12), (12, 12)]:
        draw_circle(draw, lab_cx + dx, lab_cy - 10 + dy, 7, darken(C_BLUE, 0.25))

    # Checkmark (works in lab)
    check_x, check_y = lab_cx, lab_cy + 45
    draw.line([(check_x - 12, check_y), (check_x - 3, check_y + 15)], fill=darken(C_POS, 0.2), width=4)
    draw.line([(check_x - 3, check_y + 15), (check_x + 18, check_y - 10)], fill=darken(C_POS, 0.2), width=4)

    # === MIDDLE: Deployment gap ===
    gap_cx = 360
    gap_y = 200

    # Dashed line showing gap
    for i in range(10):
        x1 = lab_cx + 85 + i * 25
        x2 = x1 + 15
        if x2 < gap_cx + 80:
            draw.line([(x1, gap_y), (x2, gap_y)], fill=C_MID, width=4)

    # Challenge indicators (warning circles)
    challenges = [
        (gap_cx - 60, gap_y - 60),
        (gap_cx + 60, gap_y - 60),
        (gap_cx, gap_y + 70),
    ]

    for cx, cy in challenges:
        draw_circle(draw, cx, cy, 30, C_CORAL)
        tc(draw, cx, cy, "!", F_LABEL, C_DARK)

    # X marks showing problems
    for cx, cy in challenges:
        x_cx, x_cy = cx + 25, cy - 25
        x_size = 10
        draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=3)
        draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=3)

    # === RIGHT: Clinic setting ===
    clinic_cx, clinic_cy = 590, 200

    draw_box(draw, clinic_cx, clinic_cy, 150, 130, C_MINT, r=14)

    # Heart icon
    draw_circle(draw, clinic_cx - 35, clinic_cy, 30, C_CORAL)
    tc(draw, clinic_cx - 35, clinic_cy, "♥", F_LABEL, lighten(C_CORAL, 0.4))

    # Stethoscope-like circle
    draw_circle(draw, clinic_cx + 35, clinic_cy, 30, C_PEACH)
    # Stethoscope head
    draw_circle(draw, clinic_cx + 35, clinic_cy, 15, darken(C_PEACH, 0.2))

    # Question mark (uncertain outcome)
    tc(draw, clinic_cx, clinic_cy + 50, "?", F_TITLE, C_MID)

    # Arrow from gap to clinic (partial)
    draw_arrow(draw, gap_cx + 100, gap_y, clinic_cx - 80, gap_y, C_LIGHT, width=3, head=12)

    # === Bottom: Framework indication ===
    # Multiple connected circles showing framework approach
    framework_y = 380
    colors = [C_BLUE, C_PEACH, C_MINT, C_LAVENDER]

    for i, col in enumerate(colors):
        fx = 230 + i * 90
        draw_circle(draw, fx, framework_y, 25, col)
        if i < len(colors) - 1:
            draw.line([(fx + 25, framework_y), (fx + 65, framework_y)], fill=C_LIGHT, width=3)

    # Arrow showing complete path
    draw_arrow(draw, 230 + 3 * 90 + 30, framework_y, 600, framework_y, darken(C_POS, 0.2), width=3, head=12)

    return save_image(img, "cardiac_auscultation")

if __name__ == "__main__":
    generate()
