# publications_webp/static_src/static_sae.py
"""
SAEs can't interpret steering vectors: out-of-distribution + negative projections.
Visual: SAE box with distribution cloud, vector outside, bars with negatives, reconstruction mismatch.
Minimal text: "SAE" label, "≠" symbol.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *
import math

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: SAE with distribution cloud ===
    sae_cx, sae_cy = 180, 200
    sae_w, sae_h = 180, 130

    draw_box(draw, sae_cx, sae_cy, sae_w, sae_h, C_BLUE)
    tc(draw, sae_cx, sae_cy - 35, "SAE", F_TITLE, C_DARK)

    # Training distribution cloud inside
    cloud_cx, cloud_cy = sae_cx, sae_cy + 15
    draw.ellipse([cloud_cx - 55, cloud_cy - 25, cloud_cx + 55, cloud_cy + 30],
                 fill=C_CREAM, outline=darken(C_CREAM, 0.1), width=2)

    # Data dots inside cloud
    for dx, dy in [(-25, -5), (0, 10), (20, -8), (-10, 15), (30, 5)]:
        draw_circle(draw, cloud_cx + dx, cloud_cy + dy, 6, darken(C_CREAM, 0.15))

    # Steering vector OUTSIDE (purple arrow)
    vec_col = C_LAVENDER
    draw_arrow(draw, 50, 100, 95, 135, darken(vec_col, 0.2), width=5, head=14)

    # Warning indicator (vector is outside)
    draw_circle(draw, 75, 165, 16, C_CORAL)
    tc(draw, 75, 165, "!", F_LABEL, C_DARK)

    # === CENTER: Feature decomposition ===
    feat_cx = 380
    feat_cy = 200
    bar_w = 28
    spacing = 38

    # Arrow into features
    draw_arrow(draw, sae_cx + sae_w//2 + 15, sae_cy, feat_cx - 80, feat_cy, C_LIGHT, width=3, head=10)

    # Mix of positive (up) and negative (down) bars
    features = [(45, False), (35, True), (55, False), (30, True), (40, True)]

    for i, (h, is_neg) in enumerate(features):
        bx = feat_cx - (len(features) - 1) * spacing // 2 + i * spacing

        if is_neg:
            # Negative bar pointing DOWN (red)
            rrect(draw, [bx - bar_w//2, feat_cy, bx + bar_w//2, feat_cy + h],
                  r=5, fill=C_NEG, outline=darken(C_NEG, 0.1))
        else:
            # Positive bar pointing UP (green)
            rrect(draw, [bx - bar_w//2, feat_cy - h, bx + bar_w//2, feat_cy],
                  r=5, fill=C_POS, outline=darken(C_POS, 0.1))

    # === RIGHT: Reconstruction comparison ===
    comp_cx = 600
    comp_y = 200

    # Original vector
    draw_arrow(draw, comp_cx - 50, comp_y + 40, comp_cx + 30, comp_y - 20,
               darken(C_LAVENDER, 0.2), width=5, head=14)

    # Reconstructed vector (different direction!)
    draw_arrow(draw, comp_cx - 50, comp_y - 50, comp_cx + 30, comp_y - 10,
               darken(C_CORAL, 0.1), width=5, head=14)

    # Not equal symbol
    tc(draw, comp_cx - 10, comp_y + 70, "≠", F_SYMBOL, C_NEG)

    # X mark
    x_cx, x_cy = comp_cx + 50, comp_y + 70
    x_size = 18
    draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=5)
    draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=5)

    return save_image(img, "sae")

if __name__ == "__main__":
    generate()
