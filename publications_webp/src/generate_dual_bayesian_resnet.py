#!/usr/bin/env python3
"""
Dual Bayesian ResNet for Heart Murmur Detection — animated WebP

PAPER CONTEXT:
  PhysioNet Challenge 2022 - 4th place solution.
  Uses log mel spectrograms with overlapping segments.
  Dual binary classification: present vs (unknown/absent) + unknown vs (present/absent)
  Classifications aggregated for final patient label.

VISUAL STORY (seamless loop):
  Scene 1 (0-2.5s): Heart sound waveform with overlapping segments
  Scene 2 (2.5-5.5s): Segments → spectrograms → dual binary paths
  Scene 3 (5.5-8s): Aggregation → final classification + 4th place badge

720×450, ~8s loop, 12 fps
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS & TIMING
# ═══════════════════════════════════════════════════════════════════════════════
W, H = 720, 450
FPS = 20
TOTAL = 10.0
N = int(FPS * TOTAL)
OUT = "img/publications/dual_bayesian_resnet.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE (pastel colors)
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_WAVE = (200, 180, 220)        # Audio wave - soft purple
C_SPEC = (255, 230, 200)        # Spectrogram - warm peach
C_PATH1 = (210, 235, 245)       # Path 1 - soft blue
C_PATH2 = (245, 225, 225)       # Path 2 - soft pink
C_RESULT = (220, 245, 225)      # Result - soft green
C_GOLD = (255, 230, 180)        # 4th place - gold
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

F_LG = get_font(30, True)
F_MD = get_font(24)
F_SM = get_font(20)
F_XS = get_font(16)

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

def draw_waveform(draw, cx, cy, width, height, alpha, phase=0, segments=None):
    """Draw audio waveform with optional segment markers."""
    if alpha < 0.1:
        return

    col = fbg(lc(C_WAVE, C_DARK, 0.3), alpha)
    pts = []
    num_points = 80

    for i in range(num_points):
        x = cx - width//2 + (width * i / num_points)
        t = i / num_points * 6 * math.pi + phase
        # Heart sound-like waveform
        s1 = math.exp(-((t % (2*math.pi) - 0.5)**2) * 6) * 0.7
        s2 = math.exp(-((t % (2*math.pi) - 1.4)**2) * 8) * 0.4
        amp = (s1 + s2) * height//2
        y = cy - amp
        pts.append((x, y))

    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=col, width=2)

    # Draw segment markers if provided
    if segments and alpha > 0.4:
        seg_col = fbg(C_LIGHT, alpha * 0.6)
        for sx in segments:
            draw.line([(sx, cy - height//2 - 5), (sx, cy + height//2 + 5)], fill=seg_col, width=1)

def draw_segment_box(draw, cx, cy, width, height, alpha, highlight=False):
    """Draw a segment selection box."""
    col = C_PATH1 if highlight else C_WAVE
    fill = fbg(col, alpha * 0.5)
    outline = fbg(lc(col, C_DARK, 0.3), alpha)
    draw.rectangle([cx - width//2, cy - height//2, cx + width//2, cy + height//2],
                   fill=fill, outline=outline, width=2)

def draw_spectrogram_mini(draw, cx, cy, width, height, alpha):
    """Draw a mini spectrogram."""
    if alpha < 0.1:
        return

    x0, y0 = cx - width//2, cy - height//2
    fill = fbg(C_SPEC, alpha)
    outline = fbg(lc(C_SPEC, C_DARK, 0.25), alpha)
    draw.rounded_rectangle([x0, y0, x0 + width, y0 + height], radius=4, fill=fill, outline=outline, width=1)

    # Frequency band patterns
    if alpha > 0.3:
        num_bands = 5
        band_h = (height - 6) // num_bands
        for b in range(num_bands):
            by = y0 + 3 + b * band_h
            for t in range(width - 6):
                tx = x0 + 3 + t
                intensity = 0.2 + 0.4 * math.sin(t * 0.2 + b * 0.7) * math.sin(t * 0.1)
                intensity = max(0.1, min(0.6, intensity))
                col = fbg(lc(C_SPEC, (180, 120, 80), intensity), alpha * 0.7)
                draw.rectangle([tx, by, tx + 1, by + band_h - 2], fill=col)

def draw_binary_classifier(draw, cx, cy, size, alpha, label="", col=C_PATH1):
    """Draw a binary classifier box."""
    s = size // 2
    fill = fbg(col, alpha)
    outline = fbg(lc(col, C_DARK, 0.25), alpha)
    draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=6, fill=fill, outline=outline, width=2)

    # Binary split icon
    if alpha > 0.4:
        icon_col = fbg(lc(col, C_DARK, 0.4), alpha)
        # Tree-like split
        draw.line([(cx, cy - s//3), (cx, cy)], fill=icon_col, width=2)
        draw.line([(cx, cy), (cx - s//3, cy + s//3)], fill=icon_col, width=2)
        draw.line([(cx, cy), (cx + s//3, cy + s//3)], fill=icon_col, width=2)

    if label and alpha > 0.5:
        tc(draw, cx, cy + s + 14, label, F_XS, fbg(C_MID, alpha))

def draw_aggregation_circle(draw, cx, cy, size, alpha, pulse=0):
    """Draw aggregation/fusion circle."""
    fill = fbg(C_RESULT, alpha)
    outline = fbg(lc(C_RESULT, C_DARK, 0.25), alpha)

    r = size // 2
    if pulse > 0:
        glow_r = r + int(pulse * 8)
        draw.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r],
                     fill=fbg(C_RESULT, alpha * 0.3 * pulse))

    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=2)

    if alpha > 0.5:
        tc(draw, cx, cy, "AGG", F_XS, fbg(C_DARK, alpha * 0.7))

def draw_result_box(draw, cx, cy, width, height, alpha, label=""):
    """Draw final result box."""
    fill = fbg(C_RESULT, alpha)
    outline = fbg(lc(C_RESULT, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([cx - width//2, cy - height//2, cx + width//2, cy + height//2],
                           radius=8, fill=fill, outline=outline, width=2)

    if label and alpha > 0.5:
        tc(draw, cx, cy, label, F_SM, fbg(C_DARK, alpha * 0.9))

def draw_badge(draw, cx, cy, alpha, text="4th"):
    """Draw placement badge."""
    fill = fbg(C_GOLD, alpha)
    outline = fbg(lc(C_GOLD, C_DARK, 0.3), alpha)
    draw.rounded_rectangle([cx - 40, cy - 14, cx + 40, cy + 14], radius=10, fill=fill, outline=outline, width=2)

    if alpha > 0.5:
        tc(draw, cx, cy, text, F_SM, fbg(C_DARK, alpha * 0.9))

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
    # SCENE 1: Waveform with overlapping segments
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 0.8) * s1_a
        if title_a > 0.3:
            tc(draw, 360, 40, "Heart Sound Recording", F_LG, fbg(C_DARK, title_a))

        # Waveform
        wave_a = ph(f, 0.4, 1.2) * s1_a
        # Segment markers for overlapping windows
        seg_positions = [180, 280, 380, 480]
        draw_waveform(draw, 360, 180, 400, 80, wave_a, fs * 1.5, seg_positions)

        # Overlapping segment boxes
        seg_a = ph(f, 1.0, 1.8) * s1_a
        if seg_a > 0.3:
            # Show 3 overlapping segments
            for i, (sx, highlight) in enumerate([(230, False), (330, True), (430, False)]):
                box_a = ph(f, 1.0 + i * 0.2, 1.6 + i * 0.2) * s1_a
                draw_segment_box(draw, sx, 180, 90, 100, box_a * 0.6, highlight=(i == 1))

            # Label
            tc(draw, 360, 260, "4s windows, 1s stride", F_SM, fbg(C_MID, seg_a * 0.8))

        # Arrow down to spectrograms
        arr_a = ph(f, 1.5, 2.0) * s1_a
        if arr_a > 0.3:
            draw_arrow(draw, 360, 280, 360, 320, fbg(C_LIGHT, arr_a))

        # Mini spectrograms
        spec_a = ph(f, 1.6, 2.2) * s1_a
        for i, sx in enumerate([260, 360, 460]):
            sp_a = ph(f, 1.6 + i * 0.15, 2.2 + i * 0.15) * s1_a
            draw_spectrogram_mini(draw, sx, 370, 70, 50, sp_a)

        if spec_a > 0.5:
            tc(draw, 360, 415, "Log Mel Spectrograms", F_SM, fbg(C_MID, spec_a * 0.7))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Dual binary classification paths
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Title
        title_a = ph(f, 2.5, 3.0) * s2_a
        if title_a > 0.3:
            tc(draw, 360, 35, "Dual Binary Classification", F_LG, fbg(C_DARK, title_a))

        # Input spectrogram
        spec_a = s2_a * 0.8
        draw_spectrogram_mini(draw, 100, 225, 80, 60, spec_a)
        if spec_a > 0.5:
            tc(draw, 100, 270, "Input", F_XS, fbg(C_MID, spec_a))

        # Arrow splitting into two paths
        arr_a = ph(f, 2.8, 3.4) * s2_a
        if arr_a > 0.3:
            arrow_col = fbg(C_LIGHT, arr_a)
            # Split arrows
            draw_arrow(draw, 145, 200, 220, 150, arrow_col)
            draw_arrow(draw, 145, 250, 220, 300, arrow_col)

        # Path 1: Present vs (Unknown/Absent)
        path1_a = ph(f, 3.0, 3.8) * s2_a
        draw_binary_classifier(draw, 280, 140, 70, path1_a, "P vs U/A", C_PATH1)

        # Path 2: Unknown vs (Present/Absent)
        path2_a = ph(f, 3.2, 4.0) * s2_a
        draw_binary_classifier(draw, 280, 310, 70, path2_a, "U vs P/A", C_PATH2)

        # Results from each path
        res_a = ph(f, 3.8, 4.5) * s2_a
        if res_a > 0.3:
            # Path 1 result
            fill1 = fbg(C_PATH1, res_a)
            draw.rounded_rectangle([360, 120, 440, 160], radius=5, fill=fill1)
            tc(draw, 400, 140, "0.7", F_SM, fbg(C_DARK, res_a * 0.8))

            # Path 2 result
            fill2 = fbg(C_PATH2, res_a)
            draw.rounded_rectangle([360, 290, 440, 330], radius=5, fill=fill2)
            tc(draw, 400, 310, "0.3", F_SM, fbg(C_DARK, res_a * 0.8))

        # Arrows to aggregation
        arr2_a = ph(f, 4.2, 4.8) * s2_a
        if arr2_a > 0.3:
            arrow_col = fbg(C_LIGHT, arr2_a)
            draw_arrow(draw, 445, 140, 510, 200, arrow_col)
            draw_arrow(draw, 445, 310, 510, 250, arrow_col)

        # Aggregation
        agg_a = ph(f, 4.5, 5.0) * s2_a
        pulse = math.sin(fs * 3) * 0.5 + 0.5 if agg_a > 0.5 else 0
        draw_aggregation_circle(draw, 560, 225, 60, agg_a, pulse * agg_a)

        # Output arrow
        out_a = ph(f, 4.8, 5.2) * s2_a
        if out_a > 0.3:
            draw_arrow(draw, 595, 225, 650, 225, fbg(C_LIGHT, out_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Final result + badge
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.6, 6.2) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 45, "Final Classification", F_LG, fbg(C_DARK, title_a))

        # Three class outputs
        classes = [
            (200, 180, "Present", 0.65),
            (360, 180, "Unknown", 0.20),
            (520, 180, "Absent", 0.15),
        ]

        for i, (cx, cy, label, prob) in enumerate(classes):
            cls_a = ph(f, 5.8 + i * 0.2, 6.5 + i * 0.2) * s3_a
            if cls_a > 0.3:
                # Box
                fill = fbg(C_RESULT if i == 0 else (240, 240, 245), cls_a)
                outline = fbg(C_LIGHT, cls_a)
                draw.rounded_rectangle([cx - 55, cy - 35, cx + 55, cy + 35], radius=8, fill=fill, outline=outline, width=2)

                tc(draw, cx, cy - 10, label, F_SM, fbg(C_DARK, cls_a * 0.9))
                tc(draw, cx, cy + 15, f"{prob:.0%}", F_MD, fbg(C_MID, cls_a * 0.8))

        # Aggregation explanation
        exp_a = ph(f, 6.5, 7.0) * s3_a
        if exp_a > 0.3:
            tc(draw, 360, 270, "Per-patient aggregation", F_SM, fbg(C_MID, exp_a))

        # 4th place badge
        badge_a = ph(f, 6.8, 7.3) * s3_a
        if badge_a > 0.3:
            draw_badge(draw, 360, 340, badge_a, "4th Place")
            tc(draw, 360, 380, "PhysioNet 2022", F_XS, fbg(C_MID, badge_a * 0.7))

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
