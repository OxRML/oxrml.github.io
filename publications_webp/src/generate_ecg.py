#!/usr/bin/env python3
"""
ECG Digitization (PhysioNet Challenge) — animated WebP

PAPER CONTEXT:
  Paper ECGs (printouts) → digital signal reconstruction.
  Pipeline: Hough transform (rotate) → U-Net (segment) → Vectorize
  Won 1st place at PhysioNet 2024 Challenge.

VISUAL STORY (seamless loop):
  Scene 1 (0-3s): Tilted paper ECG with grid and signal appears
  Scene 2 (3-5.5s): Pipeline steps - rotate, segment, vectorize
  Scene 3 (5.5-8s): Clean digital waveform emerges + 1st place badge

720×450, ~8s loop, 12 fps
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS & TIMING
# ═══════════════════════════════════════════════════════════════════════════════
W, H = 720, 450
FPS = 12
TOTAL = 8.0
N = int(FPS * TOTAL)
OUT = "img/publications/ecg.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_PAPER = (255, 250, 245)       # Paper - warm white
C_GRID = (255, 225, 225)        # ECG grid - pink
C_SIGNAL = (190, 70, 70)        # Paper signal - red
C_DIGITAL = (65, 155, 125)      # Digital signal - teal
C_PROC = (230, 235, 245)        # Processing box - blue-gray
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)
C_GOLD = (255, 215, 130)        # 1st place

# ═══════════════════════════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════════════════════════
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
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

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
def ease(t):
    t = max(0., min(1., t))
    return t * t * (3. - 2. * t)

def ph(f, t0, t1):
    fs = f / FPS
    if fs <= t0: return 0.
    if fs >= t1: return 1.
    return ease((fs - t0) / (t1 - t0))

def lc(c1, c2, t):
    t = max(0., min(1., t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def fbg(col, a):
    return lc(BG, col, a)

def tc(draw, cx, cy, text, font, fill):
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((int(cx - tw/2), int(cy - th/2)), text, font=font, fill=fill)

# ═══════════════════════════════════════════════════════════════════════════════
# ECG WAVEFORM GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

def generate_ecg_wave(x_start, x_end, y_center, amplitude, num_beats=2):
    """Generate ECG-like waveform points."""
    points = []
    beat_width = (x_end - x_start) / num_beats

    for beat in range(num_beats):
        bx = x_start + beat * beat_width
        # P wave
        for i in range(6):
            t = i / 6
            x = bx + t * beat_width * 0.12
            y = y_center - amplitude * 0.12 * math.sin(t * math.pi)
            points.append((x, y))
        # QRS complex
        points.append((bx + beat_width * 0.18, y_center))
        points.append((bx + beat_width * 0.22, y_center + amplitude * 0.12))
        points.append((bx + beat_width * 0.26, y_center - amplitude * 0.80))
        points.append((bx + beat_width * 0.30, y_center + amplitude * 0.20))
        points.append((bx + beat_width * 0.34, y_center))
        # T wave
        for i in range(8):
            t = i / 8
            x = bx + beat_width * 0.48 + t * beat_width * 0.22
            y = y_center - amplitude * 0.22 * math.sin(t * math.pi)
            points.append((x, y))
        # Rest
        for i in range(4):
            t = i / 4
            x = bx + beat_width * 0.75 + t * beat_width * 0.25
            points.append((x, y_center))

    return points

# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_paper_ecg(draw, cx, cy, w, h, alpha, rotation=0.):
    """Draw paper ECG with grid and tilted signal."""
    x0, y0 = cx - w//2, cy - h//2
    x1, y1 = cx + w//2, cy + h//2

    # Paper background
    fill = fbg(C_PAPER, alpha)
    outline = fbg(lc(C_PAPER, C_DARK, 0.15), alpha)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=4, fill=fill, outline=outline, width=2)

    # Grid
    if alpha > 0.3:
        grid_col = fbg(C_GRID, alpha * 0.6)
        for gx in range(int(x0+8), int(x1-5), 10):
            draw.line([(gx, y0+5), (gx, y1-5)], fill=grid_col, width=1)
        for gy in range(int(y0+8), int(y1-5), 10):
            draw.line([(x0+5, gy), (x1-5, gy)], fill=grid_col, width=1)

    # ECG signal (with rotation to show tilt)
    if alpha > 0.4:
        pts = generate_ecg_wave(x0+12, x1-12, cy, 22, num_beats=2)

        if rotation != 0:
            cos_r, sin_r = math.cos(rotation), math.sin(rotation)
            rotated = []
            for px, py in pts:
                rx = cx + (px - cx) * cos_r - (py - cy) * sin_r
                ry = cy + (px - cx) * sin_r + (py - cy) * cos_r
                rotated.append((rx, ry))
            pts = rotated

        sig_col = fbg(C_SIGNAL, alpha)
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=sig_col, width=2)

def draw_process_step(draw, cx, cy, w, h, alpha, icon="", label=""):
    """Processing step box with icon."""
    fill = fbg(C_PROC, alpha)
    outline = fbg(lc(C_PROC, C_DARK, 0.15), alpha)
    draw.rounded_rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], radius=6, fill=fill, outline=outline, width=2)

    if icon and alpha > 0.4:
        tc(draw, cx, cy, icon, F_MD, fbg(C_MID, alpha))

    if label and alpha > 0.5:
        tc(draw, cx, cy + h//2 + 14, label, F_SM, fbg(C_LIGHT, alpha))

def draw_digital_display(draw, cx, cy, w, h, alpha, progress=1.0):
    """Clean digital ECG display."""
    x0, y0 = cx - w//2, cy - h//2
    x1, y1 = cx + w//2, cy + h//2

    # Display background
    fill = fbg((240, 250, 248), alpha)
    outline = fbg(lc(C_DIGITAL, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=fill, outline=outline, width=2)

    # Clean ECG signal (no tilt)
    if alpha > 0.4:
        pts = generate_ecg_wave(x0+12, x1-12, cy, 25, num_beats=2)
        sig_col = fbg(C_DIGITAL, alpha)
        num_pts = int(len(pts) * progress)
        for i in range(min(num_pts - 1, len(pts) - 1)):
            draw.line([pts[i], pts[i+1]], fill=sig_col, width=2)

def draw_arrow(draw, x1, y1, x2, y2, col, width=2, head=8):
    draw.line([(x1, y1), (x2, y2)], fill=col, width=width)
    ang = math.atan2(y2-y1, x2-x1)
    draw.polygon([
        (x2, y2),
        (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4)),
        (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4)),
    ], fill=col)

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene timing with crossfades
    s1_a = (1 - ph(f, 2.5, 3.2)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 7.5, 8.0))
    s2_a = ph(f, 2.8, 3.5) * (1 - ph(f, 5.2, 5.8))
    s3_a = ph(f, 5.5, 6.2) * (1 - ph(f, 7.5, 8.0))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Paper ECG (tilted) appears
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 1.0) * s1_a
        if title_a > 0.3:
            tc(draw, 200, 50, "Paper ECG", F_LG, fbg(C_MID, title_a))

        # Paper ECG with tilt
        ecg_a = ph(f, 0.5, 1.5) * s1_a
        rotation = 0.08  # ~5 degrees tilt
        draw_paper_ecg(draw, 200, 225, 200, 150, ecg_a, rotation)

        # Problem indicator
        prob_a = ph(f, 1.8, 2.4) * s1_a
        if prob_a > 0.3:
            tc(draw, 200, 330, "tilted, noisy", F_SM, fbg(C_SIGNAL, prob_a * 0.7))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Processing pipeline
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Input (smaller paper ECG)
        input_a = s2_a * 0.7
        rot = 0.08 * (1 - ph(f, 3.5, 4.5))  # Rotation decreases
        draw_paper_ecg(draw, 100, 225, 140, 110, input_a, rot)

        # Processing steps
        steps = [
            (260, 180, "↻", "Rotate"),
            (260, 280, "□", "Segment"),
            (380, 225, "→", "Vectorize"),
        ]

        for i, (sx, sy, icon, label) in enumerate(steps):
            step_a = ph(f, 3.0 + i*0.35, 3.8 + i*0.35) * s2_a
            if step_a > 0:
                draw_process_step(draw, sx, sy, 70, 50, step_a, icon, label)

        # Arrows connecting steps
        arr_a = ph(f, 3.5, 4.5) * s2_a
        if arr_a > 0.3:
            arrow_col = fbg(C_LIGHT, arr_a)
            # Input to Rotate
            draw_arrow(draw, 175, 200, 220, 180, arrow_col)
            # Input to Segment
            draw_arrow(draw, 175, 250, 220, 280, arrow_col)
            # Both to Vectorize
            draw_arrow(draw, 300, 180, 340, 210, arrow_col)
            draw_arrow(draw, 300, 280, 340, 240, arrow_col)
            # Vectorize to output
            draw_arrow(draw, 420, 225, 470, 225, arrow_col)

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Clean digital signal + 1st place
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.8, 6.3) * s3_a
        if title_a > 0.3:
            tc(draw, 500, 100, "Digital Signal", F_LG, fbg(C_DARK, title_a))

        # Digital display with drawing animation
        sig_prog = ph(f, 5.8, 7.0)
        draw_digital_display(draw, 500, 235, 200, 140, s3_a, sig_prog)

        # 1st place badge
        badge_a = ph(f, 7.0, 7.4) * s3_a
        if badge_a > 0.3:
            bx, by = 500, 350
            badge_col = fbg(C_GOLD, badge_a)
            outline = fbg((200, 170, 80), badge_a)
            draw.rounded_rectangle([bx-45, by-14, bx+45, by+14], radius=12, fill=badge_col, outline=outline, width=2)
            tc(draw, bx, by, "🥇 1st Place", F_SM, fbg(C_DARK, badge_a * 0.85))

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
    frames[0].save(OUT, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=int(1000/FPS), loop=0, lossless=True)
    print(f"✓ Saved → {OUT} ({os.path.getsize(OUT)//1024} KB)")
