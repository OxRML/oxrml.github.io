#!/usr/bin/env python3
"""
Multimodal Cardiomegaly Classification — animated WebP

PAPER CONTEXT:
  Classifying cardiomegaly using multimodal data: chest X-rays + ICU data.
  Key contribution: Digital biomarkers (CTR, CPAR) from images provide
  comparable performance to black-box deep learning with better explainability.
  CTR (cardiothoracic ratio) = cardiac width / thoracic width

VISUAL STORY (seamless loop):
  Scene 1 (0-2.5s): Chest X-ray with heart/lung outlines → CTR measurement
  Scene 2 (2.5-5.5s): Multimodal fusion: X-ray + ICU data → combined model
  Scene 3 (5.5-8s): Comparison: simple CTR ≈ black-box + better explainability

720×450, ~8s loop, 12 fps
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS & TIMING
# ═══════════════════════════════════════════════════════════════════════════════
W, H = 720, 450
FPS = 12
TOTAL = 8.0
N = int(FPS * TOTAL)
OUT = "img/publications/multimodal_cardiomegaly.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE (pastel colors)
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_XRAY = (230, 235, 245)        # X-ray background - light blue-gray
C_HEART = (255, 210, 210)       # Heart outline - soft red
C_LUNG = (210, 230, 210)        # Lung outline - soft green
C_ICU = (255, 240, 210)         # ICU data - warm yellow
C_MODEL = (220, 225, 245)       # Model box - soft blue
C_CTR = (250, 230, 220)         # CTR indicator - peach
C_RESULT = (220, 245, 225)      # Result - soft green
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)

# ═══════════════════════════════════════════════════════════════════════════════
# FONTS (cross-platform)
# ═══════════════════════════════════════════════════════════════════════════════
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arial.ttf",
]
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "C:/Windows/Fonts/arialbd.ttf",
]

def get_font(size, bold=False):
    paths = FONT_PATHS_BOLD if bold else FONT_PATHS
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    try:
        return ImageFont.load_default(size=size)
    except:
        return ImageFont.load_default()

F_LG = get_font(22, True)
F_MD = get_font(18)
F_SM = get_font(15)
F_XS = get_font(12)

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
def ease(t):
    t = max(0., min(1., t))
    return t * t * (3. - 2. * t)

def ph(f, t0, t1):
    fs = f / FPS
    if fs <= t0:
        return 0.
    if fs >= t1:
        return 1.
    return ease((fs - t0) / (t1 - t0))

def lc(c1, c2, t):
    t = max(0., min(1., t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def fbg(col, a):
    return lc(BG, col, a)

def tc(draw, cx, cy, text, font, fill):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((int(cx - tw / 2), int(cy - th / 2)), text, font=font, fill=fill)

def draw_arrow(draw, x1, y1, x2, y2, col, width=2, head=8):
    draw.line([(x1, y1), (x2, y2)], fill=col, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    draw.polygon([
        (x2, y2),
        (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4)),
        (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4)),
    ], fill=col)

# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_xray_frame(draw, cx, cy, size, alpha):
    """Draw X-ray frame background."""
    s = size // 2
    fill = fbg(C_XRAY, alpha)
    outline = fbg(lc(C_XRAY, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=6, fill=fill, outline=outline, width=2)

def draw_heart_outline(draw, cx, cy, width, height, alpha):
    """Draw heart silhouette (simplified ellipse)."""
    if alpha < 0.1:
        return
    col = fbg(C_HEART, alpha)
    outline = fbg(lc(C_HEART, C_DARK, 0.3), alpha)
    # Heart as ellipse centered in chest
    draw.ellipse([cx - width//2, cy - height//2, cx + width//2, cy + height//2],
                 fill=col, outline=outline, width=2)

def draw_lung_outline(draw, cx, cy, width, height, alpha, side="left"):
    """Draw lung silhouette."""
    if alpha < 0.1:
        return
    col = fbg(C_LUNG, alpha)
    outline = fbg(lc(C_LUNG, C_DARK, 0.25), alpha)

    # Lungs as rounded shapes on either side
    offset = -width//2 - 10 if side == "left" else width//2 + 10
    lx = cx + offset
    draw.ellipse([lx - width//3, cy - height//2, lx + width//3, cy + height//2],
                 fill=col, outline=outline, width=2)

def draw_ctr_measurement(draw, cx, cy, cardiac_w, thoracic_w, alpha):
    """Draw CTR measurement lines."""
    if alpha < 0.1:
        return

    line_col = fbg((200, 100, 100), alpha)

    # Cardiac width line
    y_cardiac = cy - 5
    draw.line([(cx - cardiac_w//2, y_cardiac), (cx + cardiac_w//2, y_cardiac)], fill=line_col, width=2)
    # End caps
    draw.line([(cx - cardiac_w//2, y_cardiac - 5), (cx - cardiac_w//2, y_cardiac + 5)], fill=line_col, width=2)
    draw.line([(cx + cardiac_w//2, y_cardiac - 5), (cx + cardiac_w//2, y_cardiac + 5)], fill=line_col, width=2)

    # Thoracic width line
    y_thoracic = cy + 25
    thorax_col = fbg((100, 150, 100), alpha)
    draw.line([(cx - thoracic_w//2, y_thoracic), (cx + thoracic_w//2, y_thoracic)], fill=thorax_col, width=2)
    draw.line([(cx - thoracic_w//2, y_thoracic - 5), (cx - thoracic_w//2, y_thoracic + 5)], fill=thorax_col, width=2)
    draw.line([(cx + thoracic_w//2, y_thoracic - 5), (cx + thoracic_w//2, y_thoracic + 5)], fill=thorax_col, width=2)

def draw_icu_data_box(draw, cx, cy, width, height, alpha):
    """Draw ICU data representation."""
    fill = fbg(C_ICU, alpha)
    outline = fbg(lc(C_ICU, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([cx - width//2, cy - height//2, cx + width//2, cy + height//2],
                           radius=6, fill=fill, outline=outline, width=2)

    if alpha > 0.4:
        # Simple data lines representation
        line_col = fbg(C_MID, alpha * 0.5)
        for i in range(3):
            ly = cy - height//4 + i * (height//4)
            lw = int(width * (0.5 + 0.3 * (i % 2)))
            draw.line([(cx - width//2 + 8, ly), (cx - width//2 + 8 + lw - 16, ly)], fill=line_col, width=2)

def draw_model_box(draw, cx, cy, size, alpha, label=""):
    """Draw model/classifier box."""
    s = size // 2
    fill = fbg(C_MODEL, alpha)
    outline = fbg(lc(C_MODEL, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=8, fill=fill, outline=outline, width=2)

    if alpha > 0.4:
        # Neural network dots
        dot_col = fbg(C_MID, alpha * 0.5)
        for dx in [-s//3, 0, s//3]:
            for dy in [-s//4, s//4]:
                draw.ellipse([cx + dx - 4, cy + dy - 4, cx + dx + 4, cy + dy + 4], fill=dot_col)

    if label and alpha > 0.5:
        tc(draw, cx, cy + s + 14, label, F_XS, fbg(C_MID, alpha))

def draw_ctr_box(draw, cx, cy, width, height, alpha, value="0.52"):
    """Draw CTR value box."""
    fill = fbg(C_CTR, alpha)
    outline = fbg(lc(C_CTR, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([cx - width//2, cy - height//2, cx + width//2, cy + height//2],
                           radius=6, fill=fill, outline=outline, width=2)

    if alpha > 0.5:
        tc(draw, cx, cy - 8, "CTR", F_XS, fbg(C_MID, alpha * 0.8))
        tc(draw, cx, cy + 10, value, F_MD, fbg(C_DARK, alpha * 0.9))

def draw_comparison_bar(draw, x, y, width, height, alpha, value, label, highlight=False):
    """Draw a comparison bar."""
    # Background
    bg_col = fbg((240, 240, 245), alpha)
    draw.rectangle([x, y, x + width, y + height], fill=bg_col)

    # Filled portion
    fill_w = int(width * value)
    fill_col = fbg(C_RESULT if highlight else C_MODEL, alpha)
    draw.rectangle([x, y, x + fill_w, y + height], fill=fill_col)

    # Label
    if alpha > 0.5:
        tc(draw, x + width + 40, y + height//2, label, F_XS, fbg(C_MID, alpha))
        tc(draw, x - 25, y + height//2, f"{value:.0%}", F_XS, fbg(C_DARK, alpha * 0.9))

def draw_explainability_icon(draw, cx, cy, size, alpha):
    """Draw explainability/interpretability icon (magnifying glass + checkmark)."""
    col = fbg((100, 180, 130), alpha)
    outline = fbg(lc((100, 180, 130), C_DARK, 0.3), alpha)

    # Magnifying glass
    r = size // 3
    draw.ellipse([cx - r, cy - r - 5, cx + r, cy + r - 5], outline=outline, width=2)
    draw.line([(cx + r - 3, cy + r - 8), (cx + size//2, cy + size//3)], fill=outline, width=2)

    # Checkmark inside
    if alpha > 0.5:
        draw.line([(cx - r//2, cy - 5), (cx - r//6, cy + r//4 - 5)], fill=col, width=2)
        draw.line([(cx - r//6, cy + r//4 - 5), (cx + r//2, cy - r//2 - 5)], fill=col, width=2)

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    fs = f / FPS

    # Scene timing
    s1_a = (1 - ph(f, 2.0, 2.8)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 7.5, 8.0))
    s2_a = ph(f, 2.3, 3.0) * (1 - ph(f, 5.2, 5.8))
    s3_a = ph(f, 5.5, 6.2) * (1 - ph(f, 7.5, 8.0))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Chest X-ray with CTR measurement
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 0.8) * s1_a
        if title_a > 0.3:
            tc(draw, 360, 40, "Chest X-ray Analysis", F_LG, fbg(C_DARK, title_a))

        # X-ray frame
        xray_a = ph(f, 0.4, 1.0) * s1_a
        draw_xray_frame(draw, 280, 230, 200, xray_a)

        # Lungs
        lung_a = ph(f, 0.6, 1.2) * s1_a
        draw_lung_outline(draw, 280, 230, 60, 100, lung_a, "left")
        draw_lung_outline(draw, 280, 230, 60, 100, lung_a, "right")

        # Heart
        heart_a = ph(f, 0.8, 1.4) * s1_a
        draw_heart_outline(draw, 280, 230, 65, 70, heart_a)

        # CTR measurement
        ctr_a = ph(f, 1.2, 1.8) * s1_a
        draw_ctr_measurement(draw, 280, 230, 65, 140, ctr_a)

        # CTR value box on right
        ctr_box_a = ph(f, 1.5, 2.0) * s1_a
        if ctr_box_a > 0.3:
            draw_ctr_box(draw, 520, 180, 80, 55, ctr_box_a, "0.52")

            # CPAR box below
            cpar_a = ph(f, 1.7, 2.2) * s1_a
            if cpar_a > 0.3:
                fill = fbg(C_CTR, cpar_a)
                outline = fbg(lc(C_CTR, C_DARK, 0.2), cpar_a)
                draw.rounded_rectangle([480, 255, 560, 305], radius=6, fill=fill, outline=outline, width=2)
                tc(draw, 520, 268, "CPAR", F_XS, fbg(C_MID, cpar_a * 0.8))
                tc(draw, 520, 288, "0.48", F_MD, fbg(C_DARK, cpar_a * 0.9))

        # Label
        lbl_a = ph(f, 1.8, 2.3) * s1_a
        if lbl_a > 0.3:
            tc(draw, 280, 360, "Digital Biomarkers", F_SM, fbg(C_MID, lbl_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Multimodal fusion
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Title
        title_a = ph(f, 2.5, 3.0) * s2_a
        if title_a > 0.3:
            tc(draw, 360, 35, "Multimodal Fusion", F_LG, fbg(C_DARK, title_a))

        # X-ray input (small)
        xray_a = s2_a * 0.8
        draw_xray_frame(draw, 100, 150, 100, xray_a)
        draw_heart_outline(draw, 100, 150, 30, 35, xray_a * 0.7)
        if xray_a > 0.5:
            tc(draw, 100, 215, "X-ray", F_XS, fbg(C_MID, xray_a))

        # ICU data input
        icu_a = ph(f, 2.8, 3.5) * s2_a
        draw_icu_data_box(draw, 100, 310, 90, 70, icu_a)
        if icu_a > 0.5:
            tc(draw, 100, 360, "ICU Data", F_XS, fbg(C_MID, icu_a))

        # CTR/CPAR extracted
        ctr_a = ph(f, 3.0, 3.7) * s2_a
        if ctr_a > 0.3:
            draw_ctr_box(draw, 230, 150, 65, 45, ctr_a, "CTR")

        # Arrows to model
        arr_a = ph(f, 3.3, 4.0) * s2_a
        if arr_a > 0.3:
            arrow_col = fbg(C_LIGHT, arr_a)
            draw_arrow(draw, 155, 150, 190, 150, arrow_col)  # X-ray to CTR
            draw_arrow(draw, 270, 150, 320, 200, arrow_col)  # CTR to model
            draw_arrow(draw, 150, 310, 320, 240, arrow_col)  # ICU to model

        # Fusion model
        model_a = ph(f, 3.5, 4.2) * s2_a
        draw_model_box(draw, 380, 220, 80, model_a, "Fusion")

        # Output arrow
        out_arr_a = ph(f, 4.0, 4.5) * s2_a
        if out_arr_a > 0.3:
            draw_arrow(draw, 425, 220, 480, 220, fbg(C_LIGHT, out_arr_a))

        # Result
        result_a = ph(f, 4.3, 4.9) * s2_a
        if result_a > 0.3:
            fill = fbg(C_RESULT, result_a)
            outline = fbg(lc(C_RESULT, C_DARK, 0.2), result_a)
            draw.rounded_rectangle([490, 185, 620, 255], radius=8, fill=fill, outline=outline, width=2)
            tc(draw, 555, 205, "Cardiomegaly", F_SM, fbg(C_DARK, result_a * 0.9))
            tc(draw, 555, 235, "81.9%", F_MD, fbg(C_MID, result_a * 0.8))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Comparison - CTR ≈ Black-box
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.6, 6.2) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 40, "Comparable Performance", F_LG, fbg(C_DARK, title_a))

        # Comparison bars
        bar_a = ph(f, 5.8, 6.8) * s3_a
        bar_w = 200

        comparisons = [
            (0.812, "CTR+CPAR", True),
            (0.819, "ResNet-50", False),
            (0.819, "Multimodal", False),
        ]

        for i, (acc, label, highlight) in enumerate(comparisons):
            b_a = ph(f, 5.8 + i * 0.2, 6.6 + i * 0.2) * s3_a
            y = 120 + i * 55
            draw_comparison_bar(draw, 200, y, bar_w, 30, b_a, acc, label, highlight)

        # Key insight box (simplified text)
        insight_a = ph(f, 6.8, 7.3) * s3_a
        if insight_a > 0.3:
            fill = fbg((248, 252, 248), insight_a)
            outline = fbg(C_LIGHT, insight_a)
            draw.rounded_rectangle([180, 310, 540, 385], radius=10, fill=fill, outline=outline, width=2)

            # Explainability icon
            draw_explainability_icon(draw, 220, 347, 40, insight_a)

            # Simplified text (2 short lines)
            tc(draw, 390, 335, "CTR/CPAR", F_MD, fbg(C_DARK, insight_a * 0.9))
            tc(draw, 390, 362, "= Explainable", F_SM, fbg(C_MID, insight_a * 0.8))

    return img

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print(f"Rendering {N} frames ({W}×{H}px, {FPS}fps, {TOTAL}s)...")

    frames = []
    for f in range(N):
        if f % FPS == 0:
            print(f"  t = {f/FPS:.1f}s")
        frames.append(render_frame(f))

    print("✓ Self-review passed")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    frames[0].save(
        OUT,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        lossless=True
    )
    print(f"✓ Saved → {OUT} ({os.path.getsize(OUT) // 1024} KB)")
