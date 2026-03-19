# publications_webp/static_src/static_multimodal_cardiomegaly.py
"""
Multimodal cardiomegaly: X-ray + biomarkers + ICU data → diagnosis.
Visual: X-ray with heart → measurement ratios → diagnosis output.
Minimal text: just symbols and visual flow.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def draw_heart_xray(draw, cx, cy, size):
    """Draw simplified chest X-ray with heart outline."""
    # X-ray background (dark)
    draw_box(draw, cx, cy, size, int(size * 0.9), (50, 55, 65), r=8)

    # Ribcage outline
    rib_col = (90, 95, 105)
    for i in range(4):
        ry = cy - size * 0.28 + i * size * 0.18
        draw.arc([int(cx - size * 0.4), int(ry - 8), int(cx - size * 0.1), int(ry + 8)],
                 0, 180, fill=rib_col, width=2)
        draw.arc([int(cx + size * 0.1), int(ry - 8), int(cx + size * 0.4), int(ry + 8)],
                 0, 180, fill=rib_col, width=2)

    # Heart shape (enlarged = cardiomegaly)
    heart_col = (150, 160, 175)
    heart_w = size * 0.38
    heart_h = size * 0.42
    draw.ellipse([int(cx - heart_w), int(cy - heart_h * 0.3), int(cx + heart_w), int(cy + heart_h * 0.7)],
                 fill=heart_col, outline=(180, 185, 195), width=3)

    # Measurement lines (showing CTR concept)
    line_col = (220, 180, 180)
    # Heart width line
    draw.line([(int(cx - heart_w + 5), int(cy + heart_h * 0.2)),
               (int(cx + heart_w - 5), int(cy + heart_h * 0.2))], fill=line_col, width=2)
    # Thorax width line (wider)
    draw.line([(int(cx - size * 0.38), int(cy + heart_h * 0.2 + 15)),
               (int(cx + size * 0.38), int(cy + heart_h * 0.2 + 15))], fill=line_col, width=2)

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: X-ray image ===
    xray_cx, xray_cy = 140, 200
    draw_heart_xray(draw, xray_cx, xray_cy, 170)

    # === MIDDLE: Biomarker extraction ===
    bio_cx = 350
    bio_y1 = 130
    bio_y2 = 220
    bio_y3 = 310

    # Arrow from X-ray
    draw_arrow(draw, xray_cx + 90, xray_cy - 40, bio_cx - 70, bio_y1, C_LIGHT, width=3, head=10)
    draw_arrow(draw, xray_cx + 90, xray_cy, bio_cx - 70, bio_y2, C_LIGHT, width=3, head=10)
    draw_arrow(draw, xray_cx + 90, xray_cy + 40, bio_cx - 70, bio_y3, C_LIGHT, width=3, head=10)

    # Biomarker boxes (no text labels - just colored boxes with icons)
    # CTR - ratio visualization
    draw_box(draw, bio_cx, bio_y1, 110, 55, C_BLUE, r=10)
    # Ratio bars inside
    draw.line([(bio_cx - 35, bio_y1 - 8), (bio_cx + 25, bio_y1 - 8)], fill=darken(C_BLUE, 0.3), width=4)
    draw.line([(bio_cx - 35, bio_y1 + 8), (bio_cx + 35, bio_y1 + 8)], fill=darken(C_BLUE, 0.2), width=4)

    # CPAR - area visualization
    draw_box(draw, bio_cx, bio_y2, 110, 55, C_MINT, r=10)
    # Area circles
    draw_circle(draw, bio_cx - 15, bio_y2, 18, darken(C_MINT, 0.2))
    draw_circle(draw, bio_cx + 15, bio_y2, 22, darken(C_MINT, 0.15))

    # ICU data - waveform visualization
    draw_box(draw, bio_cx, bio_y3, 110, 55, C_PEACH, r=10)
    # Waveform inside
    import math
    pts = []
    for i in range(8):
        x = bio_cx - 40 + i * 12
        y = bio_y3 + int(math.sin(i * 1.3) * 12)
        pts.append((x, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=darken(C_PEACH, 0.3), width=3)

    # === Fusion ===
    fusion_x = bio_cx + 80
    draw.line([(bio_cx + 55, bio_y1), (fusion_x, 220)], fill=C_LIGHT, width=2)
    draw.line([(bio_cx + 55, bio_y2), (fusion_x, 220)], fill=C_LIGHT, width=2)
    draw.line([(bio_cx + 55, bio_y3), (fusion_x, 220)], fill=C_LIGHT, width=2)

    draw_arrow(draw, fusion_x, 220, 530, 220, C_LIGHT, width=4, head=14)

    # === RIGHT: Diagnosis output ===
    out_cx = 600
    out_y = 220

    draw_box(draw, out_cx, out_y, 130, 100, lighten(C_LAVENDER, 0.4), r=14)

    # Heart icon with warning
    draw_circle(draw, out_cx, out_y - 10, 30, C_CORAL)
    tc(draw, out_cx, out_y - 10, "♥", F_TITLE, lighten(C_CORAL, 0.4))

    # Enlarged indicator
    draw.line([(out_cx - 25, out_y + 30), (out_cx + 25, out_y + 30)], fill=darken(C_CORAL, 0.2), width=3)
    draw.polygon([(out_cx - 30, out_y + 30), (out_cx - 38, out_y + 25), (out_cx - 38, out_y + 35)],
                 fill=darken(C_CORAL, 0.2))
    draw.polygon([(out_cx + 30, out_y + 30), (out_cx + 38, out_y + 25), (out_cx + 38, out_y + 35)],
                 fill=darken(C_CORAL, 0.2))

    # === Bottom: Explainability indicator ===
    # Equals sign showing equivalence with better explainability
    tc(draw, 360, 400, "=", F_SYMBOL, C_MID)

    # Checkmark
    check_x, check_y = 420, 400
    draw.line([(check_x - 12, check_y), (check_x - 3, check_y + 15)], fill=darken(C_POS, 0.2), width=5)
    draw.line([(check_x - 3, check_y + 15), (check_x + 18, check_y - 10)], fill=darken(C_POS, 0.2), width=5)

    return save_image(img, "multimodal_cardiomegaly")

if __name__ == "__main__":
    generate()
