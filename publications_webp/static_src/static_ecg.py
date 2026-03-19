# publications_webp/static_src/static_ecg.py
"""
ECG Paper→Digital: Hough rotate + U-Net segment → clean waveform.
Visual: Tilted paper ECG → processing boxes → clean digital ECG + 1st place badge.
Minimal text: just symbols and badge.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *
import math

def generate_ecg_points(x_start, x_end, y_center, amplitude, num_beats=2):
    """Generate ECG-like waveform points."""
    points = []
    beat_width = (x_end - x_start) / num_beats

    for beat in range(num_beats):
        bx = x_start + beat * beat_width
        # P wave
        for i in range(5):
            t = i / 5
            x = bx + t * beat_width * 0.1
            y = y_center - amplitude * 0.1 * math.sin(t * math.pi)
            points.append((x, y))
        # QRS complex
        points.append((bx + beat_width * 0.15, y_center))
        points.append((bx + beat_width * 0.2, y_center + amplitude * 0.1))
        points.append((bx + beat_width * 0.25, y_center - amplitude * 0.75))
        points.append((bx + beat_width * 0.3, y_center + amplitude * 0.15))
        points.append((bx + beat_width * 0.35, y_center))
        # T wave
        for i in range(5):
            t = i / 5
            x = bx + beat_width * 0.5 + t * beat_width * 0.2
            y = y_center - amplitude * 0.2 * math.sin(t * math.pi)
            points.append((x, y))
        # Rest
        for i in range(3):
            t = i / 3
            x = bx + beat_width * 0.75 + t * beat_width * 0.25
            points.append((x, y_center))

    return points

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Paper ECG (tilted with grid) ===
    paper_cx, paper_cy = 140, 200
    paper_w, paper_h = 180, 150

    draw_box(draw, paper_cx, paper_cy, paper_w, paper_h, C_CREAM, r=6)

    # Grid lines (pink)
    grid_col = lighten(C_CORAL, 0.4)
    x0, y0 = paper_cx - paper_w // 2, paper_cy - paper_h // 2
    for gx in range(int(x0 + 8), int(x0 + paper_w - 5), 14):
        draw.line([(gx, y0 + 5), (gx, y0 + paper_h - 5)], fill=grid_col, width=1)
    for gy in range(int(y0 + 8), int(y0 + paper_h - 5), 14):
        draw.line([(x0 + 5, gy), (x0 + paper_w - 5, gy)], fill=grid_col, width=1)

    # ECG signal (slightly tilted)
    pts = generate_ecg_points(x0 + 15, x0 + paper_w - 15, paper_cy, 30, num_beats=2)

    # Rotate slightly
    cos_r, sin_r = math.cos(0.1), math.sin(0.1)
    rotated = []
    for px, py in pts:
        rx = paper_cx + (px - paper_cx) * cos_r - (py - paper_cy) * sin_r
        ry = paper_cy + (px - paper_cx) * sin_r + (py - paper_cy) * cos_r
        rotated.append((rx, ry))

    signal_col = darken(C_CORAL, 0.3)
    for i in range(len(rotated) - 1):
        draw.line([rotated[i], rotated[i + 1]], fill=signal_col, width=3)

    # X mark below (tilted/noisy)
    x_cx, x_cy = paper_cx, paper_cy + paper_h//2 + 30
    x_size = 15
    draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=4)
    draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=4)

    # === PROCESSING PIPELINE ===
    pipe_y = 200

    # Arrow
    draw_arrow(draw, paper_cx + paper_w//2 + 10, pipe_y, 290, pipe_y, C_LIGHT, width=3, head=12)

    # Processing boxes (no text, just colored steps)
    proc_colors = [C_BLUE, C_LAVENDER, C_MINT]
    proc_xs = [330, 400, 470]

    for px, col in zip(proc_xs, proc_colors):
        draw_box(draw, px, pipe_y, 55, 55, col, r=8)
        # Gear/process icon inside
        draw_circle(draw, px, pipe_y, 15, darken(col, 0.2))

    # Small arrows between
    for i in range(len(proc_xs) - 1):
        draw.line([(proc_xs[i] + 30, pipe_y), (proc_xs[i+1] - 30, pipe_y)], fill=C_LIGHT, width=2)

    # Arrow to output
    draw_arrow(draw, 500, pipe_y, 540, pipe_y, C_LIGHT, width=3, head=12)

    # === RIGHT: Clean digital ECG ===
    digi_cx, digi_cy = 620, 200
    digi_w, digi_h = 160, 130

    draw_box(draw, digi_cx, digi_cy, digi_w, digi_h, lighten(C_MINT, 0.4), r=10)

    # Clean ECG signal (no tilt)
    digi_x0 = digi_cx - digi_w // 2
    pts = generate_ecg_points(digi_x0 + 15, digi_x0 + digi_w - 15, digi_cy, 35, num_beats=2)

    digi_col = darken(C_TEAL, 0.2)
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=digi_col, width=3)

    # Checkmark below (clean output)
    check_x, check_y = digi_cx, digi_cy + digi_h//2 + 30
    draw.line([(check_x - 15, check_y), (check_x - 4, check_y + 18)], fill=darken(C_POS, 0.2), width=5)
    draw.line([(check_x - 4, check_y + 18), (check_x + 20, check_y - 12)], fill=darken(C_POS, 0.2), width=5)

    # 1st Place badge (gold medal style)
    badge_x, badge_y = 360, 380
    draw_circle(draw, badge_x, badge_y, 40, C_GOLD)
    tc(draw, badge_x, badge_y, "1", F_TITLE, darken(C_GOLD, 0.5))

    return save_image(img, "ecg")

if __name__ == "__main__":
    generate()
