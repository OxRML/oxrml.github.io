# publications_webp/static_src/static_dual_bayesian_resnet.py
"""
Heart sound → Spectrogram → Dual Bayesian ResNet → Murmur detection.
Visual: Heart/waveform → spectrogram → dual classifiers → output + badge.
Minimal text: just symbols and visual flow.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *
import math

def draw_spectrogram(draw, cx, cy, w, h, col):
    """Draw simplified spectrogram."""
    x0, y0 = cx - w//2, cy - h//2

    num_bands = 8
    band_h = h // num_bands

    for i in range(num_bands):
        by = y0 + i * band_h
        for j in range(10):
            bx = x0 + j * w // 10
            bw = w // 10
            intensity = 0.3 + 0.5 * math.sin(i * 0.7 + j * 0.5)
            bar_col = lc(col, darken(col, 0.5), intensity)
            draw.rectangle([bx, by, bx + bw - 1, by + band_h - 1], fill=bar_col)

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Heart sound input ===
    audio_cx, audio_cy = 100, 200

    # Heart icon
    draw_circle(draw, audio_cx, audio_cy - 50, 35, C_CORAL)
    tc(draw, audio_cx, audio_cy - 50, "♥", F_TITLE, lighten(C_CORAL, 0.4))

    # Waveform below
    pts = []
    for i in range(15):
        x = audio_cx - 50 + i * 7
        amp = math.sin(i * 0.8) * (0.3 + 0.7 * abs(math.sin(i * 0.3)))
        y = audio_cy + 40 + int(amp * 25)
        pts.append((x, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=darken(C_CORAL, 0.25), width=3)

    # Arrow
    draw_arrow(draw, audio_cx + 55, audio_cy, 190, audio_cy, C_LIGHT, width=3, head=12)

    # === Spectrogram ===
    spec_cx, spec_cy = 250, 200

    draw_box(draw, spec_cx, spec_cy, 90, 80, C_BLUE, r=8)
    draw_spectrogram(draw, spec_cx, spec_cy, 80, 70, C_BLUE)

    # Arrows to dual classifiers
    draw_arrow(draw, spec_cx + 50, spec_cy - 25, 360, 140, C_LIGHT, width=3, head=10)
    draw_arrow(draw, spec_cx + 50, spec_cy + 25, 360, 260, C_LIGHT, width=3, head=10)

    # === Dual Bayesian ResNet ===
    res_cx = 430
    res_y1, res_y2 = 140, 260

    # Classifier 1
    draw_box(draw, res_cx, res_y1, 110, 65, C_LAVENDER, r=10)
    # Neural dots
    for dx, dy in [(-25, -10), (0, -10), (25, -10), (-12, 12), (12, 12)]:
        draw_circle(draw, res_cx + dx, res_y1 + dy, 7, darken(C_LAVENDER, 0.25))

    # Classifier 2
    draw_box(draw, res_cx, res_y2, 110, 65, C_MINT, r=10)
    for dx, dy in [(-25, -10), (0, -10), (25, -10), (-12, 12), (12, 12)]:
        draw_circle(draw, res_cx + dx, res_y2 + dy, 7, darken(C_MINT, 0.25))

    # Merge arrows
    merge_x = res_cx + 70
    draw.line([(res_cx + 55, res_y1 + 20), (merge_x, 200)], fill=C_LIGHT, width=2)
    draw.line([(res_cx + 55, res_y2 - 20), (merge_x, 200)], fill=C_LIGHT, width=2)
    draw_arrow(draw, merge_x, 200, 580, 200, C_LIGHT, width=4, head=14)

    # === Output ===
    out_cx, out_cy = 640, 200

    draw_box(draw, out_cx, out_cy, 110, 80, lighten(C_CORAL, 0.4), r=12)

    # Heart with detection indicator
    draw_circle(draw, out_cx, out_cy - 8, 25, C_CORAL)
    tc(draw, out_cx, out_cy - 8, "♥", F_LABEL, lighten(C_CORAL, 0.4))

    # Waveform symbol below
    draw.line([(out_cx - 25, out_cy + 25), (out_cx - 10, out_cy + 18),
               (out_cx, out_cy + 32), (out_cx + 10, out_cy + 18),
               (out_cx + 25, out_cy + 25)], fill=darken(C_CORAL, 0.3), width=2)

    # === 4th Place badge ===
    badge_x, badge_y = 360, 380
    draw_circle(draw, badge_x, badge_y, 40, C_GOLD)
    tc(draw, badge_x, badge_y, "4", F_TITLE, darken(C_GOLD, 0.5))

    return save_image(img, "dual_bayesian_resnet")

if __name__ == "__main__":
    generate()
