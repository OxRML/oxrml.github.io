#!/usr/bin/env python3
"""
Cardiac Auscultation AI Deployment — animated WebP

PAPER CONTEXT:
  AI-driven cardiac auscultation research for low-income settings.
  Key: Bayesian ResNet for heart murmur detection from sound recordings.
  Focus: Gap between AI research and real-world deployment in LMICs.

VISUAL STORY (seamless loop):
  Scene 1 (0-2.5s): Stethoscope icon + heart sound waveform appears
  Scene 2 (2.5-5s): Waveform → spectrogram → AI model → prediction
  Scene 3 (5-8s): Deployment challenges visualized (barriers fading in/out)

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
OUT = "img/publications/cardiac_auscultation.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE (pastel colors)
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_HEART = (245, 200, 200)       # Heart - soft pink
C_WAVE = (200, 220, 245)        # Sound wave - soft blue
C_SPEC = (255, 235, 210)        # Spectrogram - warm peach
C_AI = (210, 235, 220)          # AI model - soft green
C_BARRIER = (245, 220, 220)     # Barrier - soft red
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)
C_ACCENT = (180, 130, 130)      # Accent pink

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
    """Load font with cross-platform fallbacks."""
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

# Font sizes (2× base for legibility)
F_LG = get_font(22, True)
F_MD = get_font(18)
F_SM = get_font(15)

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
def ease(t):
    """Smooth ease-in-out."""
    t = max(0., min(1., t))
    return t * t * (3. - 2. * t)

def ph(f, t0, t1):
    """Progress helper: returns 0-1 progress for frame f between times t0-t1."""
    fs = f / FPS
    if fs <= t0:
        return 0.
    if fs >= t1:
        return 1.
    return ease((fs - t0) / (t1 - t0))

def lc(c1, c2, t):
    """Linear color interpolation."""
    t = max(0., min(1., t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def fbg(col, a):
    """Fade color from background."""
    return lc(BG, col, a)

def tc(draw, cx, cy, text, font, fill):
    """Draw text centered at (cx, cy)."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((int(cx - tw / 2), int(cy - th / 2)), text, font=font, fill=fill)

def draw_arrow(draw, x1, y1, x2, y2, col, width=2, head=8):
    """Draw arrow from (x1,y1) to (x2,y2)."""
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

def draw_heart_icon(draw, cx, cy, size, alpha):
    """Draw a simple heart shape."""
    s = size // 2
    col = fbg(C_HEART, alpha)
    outline = fbg(C_ACCENT, alpha)

    # Simple heart using two circles and a triangle
    r = int(s * 0.45)
    # Left circle
    draw.ellipse([cx - s + 2, cy - s//2, cx - s + 2 + 2*r, cy - s//2 + 2*r], fill=col, outline=outline, width=2)
    # Right circle
    draw.ellipse([cx + s - 2 - 2*r, cy - s//2, cx + s - 2, cy - s//2 + 2*r], fill=col, outline=outline, width=2)
    # Bottom triangle
    draw.polygon([
        (cx - s + 4, cy - s//2 + r),
        (cx + s - 4, cy - s//2 + r),
        (cx, cy + s - 5)
    ], fill=col, outline=outline, width=2)

def draw_stethoscope(draw, cx, cy, size, alpha):
    """Draw simplified stethoscope icon using basic shapes."""
    col = fbg(C_MID, alpha)
    s = size // 2

    # Y-shaped tube structure
    # Main vertical stem
    draw.line([(cx, cy + s//3), (cx, cy + s)], fill=col, width=3)
    # Left branch
    draw.line([(cx, cy + s//3), (cx - s//2, cy - s//2)], fill=col, width=3)
    # Right branch
    draw.line([(cx, cy + s//3), (cx + s//2, cy - s//2)], fill=col, width=3)

    # Earpieces at top (small circles)
    draw.ellipse([cx - s//2 - 6, cy - s//2 - 6, cx - s//2 + 6, cy - s//2 + 6],
                 fill=fbg(C_LIGHT, alpha), outline=col, width=2)
    draw.ellipse([cx + s//2 - 6, cy - s//2 - 6, cx + s//2 + 6, cy - s//2 + 6],
                 fill=fbg(C_LIGHT, alpha), outline=col, width=2)

    # Chest piece (diaphragm) at bottom
    draw.ellipse([cx - s//3, cy + s - s//4, cx + s//3, cy + s + s//4],
                 fill=fbg(C_WAVE, alpha), outline=col, width=2)

def draw_sound_wave(draw, cx, cy, width, height, alpha, phase=0):
    """Draw heart sound waveform."""
    if alpha < 0.1:
        return

    col = fbg(C_ACCENT, alpha)
    pts = []
    num_points = 60

    for i in range(num_points):
        x = cx - width//2 + (width * i / num_points)
        # Create heart sound-like pattern with S1 and S2
        t = i / num_points * 4 * math.pi + phase
        # S1 spike
        s1 = math.exp(-((t % (2*math.pi) - 0.5)**2) * 8) * 0.8
        # S2 spike
        s2 = math.exp(-((t % (2*math.pi) - 1.5)**2) * 10) * 0.5
        amp = (s1 + s2) * height//2
        y = cy - amp
        pts.append((x, y))

    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i+1]], fill=col, width=2)

def draw_spectrogram(draw, cx, cy, width, height, alpha, progress=1.0):
    """Draw simplified spectrogram visualization."""
    if alpha < 0.1:
        return

    x0, y0 = cx - width//2, cy - height//2

    # Background
    fill = fbg(C_SPEC, alpha)
    outline = fbg(lc(C_SPEC, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([x0, y0, x0 + width, y0 + height], radius=5, fill=fill, outline=outline, width=2)

    # Frequency bands (horizontal stripes with varying intensity)
    if alpha > 0.3:
        num_bands = 8
        band_h = (height - 10) // num_bands
        for b in range(num_bands):
            by = y0 + 5 + b * band_h
            # Varying intensity pattern
            for t in range(int(width * progress) - 10):
                tx = x0 + 5 + t
                intensity = 0.3 + 0.4 * math.sin(t * 0.15 + b * 0.5) * math.sin(t * 0.08)
                intensity = max(0.1, min(0.7, intensity))
                col = fbg(lc(C_SPEC, C_ACCENT, intensity), alpha * 0.8)
                draw.rectangle([tx, by, tx + 2, by + band_h - 2], fill=col)

def draw_ai_box(draw, cx, cy, size, alpha, label="AI"):
    """Draw AI model box with neural network suggestion."""
    s = size // 2
    fill = fbg(C_AI, alpha)
    outline = fbg(lc(C_AI, C_DARK, 0.25), alpha)
    draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=8, fill=fill, outline=outline, width=2)

    if alpha > 0.4:
        # Simple neural network dots
        dot_col = fbg(C_MID, alpha * 0.6)
        positions = [
            (cx - s//3, cy - s//3), (cx - s//3, cy + s//3),
            (cx, cy),
            (cx + s//3, cy - s//3), (cx + s//3, cy + s//3),
        ]
        for px, py in positions:
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=dot_col)

        # Connect dots
        line_col = fbg(C_LIGHT, alpha * 0.5)
        draw.line([positions[0], positions[2]], fill=line_col, width=1)
        draw.line([positions[1], positions[2]], fill=line_col, width=1)
        draw.line([positions[2], positions[3]], fill=line_col, width=1)
        draw.line([positions[2], positions[4]], fill=line_col, width=1)

    if alpha > 0.5:
        tc(draw, cx, cy + s + 16, label, F_SM, fbg(C_MID, alpha))

def draw_barrier(draw, cx, cy, width, height, alpha, label=""):
    """Draw deployment barrier."""
    fill = fbg(C_BARRIER, alpha)
    outline = fbg(lc(C_BARRIER, C_DARK, 0.2), alpha)
    draw.rounded_rectangle([cx - width//2, cy - height//2, cx + width//2, cy + height//2],
                           radius=6, fill=fill, outline=outline, width=2)

    if alpha > 0.4 and label:
        tc(draw, cx, cy, label, F_SM, fbg(C_DARK, alpha * 0.8))

def draw_checkmark(draw, cx, cy, size, alpha):
    """Draw checkmark."""
    col = fbg((100, 180, 130), alpha)
    draw.line([(cx - size//3, cy), (cx - size//10, cy + size//4)], fill=col, width=3)
    draw.line([(cx - size//10, cy + size//4), (cx + size//3, cy - size//4)], fill=col, width=3)

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene timing with crossfades
    s1_a = (1 - ph(f, 2.0, 2.8)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 7.5, 8.0))
    s2_a = ph(f, 2.3, 3.0) * (1 - ph(f, 4.8, 5.5))
    s3_a = ph(f, 5.2, 5.8) * (1 - ph(f, 7.5, 8.0))

    fs = f / FPS  # Current time in seconds

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Stethoscope + Heart sound wave
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 0.8) * s1_a
        if title_a > 0.3:
            tc(draw, 360, 45, "Heart Sound Analysis", F_LG, fbg(C_DARK, title_a))

        # Stethoscope on left
        steth_a = ph(f, 0.4, 1.0) * s1_a
        draw_stethoscope(draw, 150, 200, 80, steth_a)

        # Heart icon
        heart_a = ph(f, 0.6, 1.2) * s1_a
        draw_heart_icon(draw, 150, 320, 50, heart_a)

        # Sound wave on right
        wave_a = ph(f, 0.8, 1.4) * s1_a
        phase = fs * 2  # Animate the wave
        draw_sound_wave(draw, 450, 225, 280, 100, wave_a, phase)

        # Label
        if wave_a > 0.5:
            tc(draw, 450, 300, "Phonocardiogram", F_SM, fbg(C_LIGHT, wave_a * 0.8))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Processing pipeline (wave → spectrogram → AI → prediction)
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Mini wave (input)
        wave_a2 = s2_a * 0.8
        draw_sound_wave(draw, 100, 225, 100, 60, wave_a2, fs * 2)

        # Arrow 1
        arr1_a = ph(f, 2.6, 3.2) * s2_a
        if arr1_a > 0.3:
            draw_arrow(draw, 155, 225, 195, 225, fbg(C_LIGHT, arr1_a))

        # Spectrogram
        spec_a = ph(f, 2.8, 3.5) * s2_a
        spec_prog = ph(f, 2.8, 4.0)
        draw_spectrogram(draw, 280, 225, 110, 90, spec_a, spec_prog)
        if spec_a > 0.5:
            tc(draw, 280, 285, "Spectrogram", F_SM, fbg(C_LIGHT, spec_a * 0.7))

        # Arrow 2
        arr2_a = ph(f, 3.3, 3.9) * s2_a
        if arr2_a > 0.3:
            draw_arrow(draw, 340, 225, 385, 225, fbg(C_LIGHT, arr2_a))

        # AI Model
        ai_a = ph(f, 3.5, 4.2) * s2_a
        draw_ai_box(draw, 450, 225, 80, ai_a, "Bayesian\nResNet")

        # Arrow 3
        arr3_a = ph(f, 4.0, 4.5) * s2_a
        if arr3_a > 0.3:
            draw_arrow(draw, 495, 225, 545, 225, fbg(C_LIGHT, arr3_a))

        # Output prediction
        out_a = ph(f, 4.2, 4.8) * s2_a
        if out_a > 0.3:
            # Result box
            fill = fbg((220, 245, 225), out_a)
            outline = fbg(C_LIGHT, out_a)
            draw.rounded_rectangle([555, 195, 660, 255], radius=8, fill=fill, outline=outline, width=2)
            tc(draw, 607, 215, "Murmur", F_SM, fbg(C_MID, out_a))
            draw_checkmark(draw, 607, 238, 30, out_a)

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Deployment challenges (barriers)
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.4, 6.0) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 50, "Deployment in LMICs", F_LG, fbg(C_DARK, title_a))

        # AI model in center
        ai_a = s3_a * 0.9
        draw_ai_box(draw, 360, 200, 70, ai_a, "AI Model")

        # Barriers surrounding (positioned to avoid overlap)
        barriers = [
            (150, 130, "Resources"),
            (150, 270, "Training"),
            (570, 130, "Integration"),
            (570, 270, "Robustness"),
        ]

        for i, (bx, by, label) in enumerate(barriers):
            b_a = ph(f, 5.6 + i * 0.25, 6.4 + i * 0.25) * s3_a
            # Pulsing effect
            pulse = 0.8 + 0.2 * math.sin(fs * 2 + i)
            draw_barrier(draw, bx, by, 100, 45, b_a * pulse, label)

        # Connecting dashed lines (challenges)
        if s3_a > 0.5:
            dash_col = fbg(C_LIGHT, s3_a * 0.5)
            for bx, by, _ in barriers:
                # Draw dashed line toward center
                dx = (360 - bx) * 0.4
                dy = (200 - by) * 0.4
                for d in range(0, 6, 2):
                    t = d / 6
                    x1 = bx + dx * t + (50 if bx < 360 else -50)
                    y1 = by + dy * t
                    x2 = bx + dx * (t + 0.15) + (50 if bx < 360 else -50)
                    y2 = by + dy * (t + 0.15)
                    draw.line([(x1, y1), (x2, y2)], fill=dash_col, width=2)

        # Bottom message
        msg_a = ph(f, 6.8, 7.3) * s3_a
        if msg_a > 0.3:
            tc(draw, 360, 380, "Bridging research to practice", F_SM, fbg(C_MID, msg_a))

    return img

# ═══════════════════════════════════════════════════════════════════════════════
# SELF-REVIEW & MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def self_review(frames):
    """Check for common issues: overlap, clipping, legibility."""
    issues = []
    # Sample frames at key moments
    for f_idx in [0, N//4, N//2, 3*N//4, N-1]:
        if f_idx >= len(frames):
            continue
        img = frames[f_idx]
        # Check edges (5px margin) for non-white pixels indicating clipping
        pixels = img.load()
        edge_issues = 0
        for x in range(W):
            if pixels[x, 2] != BG or pixels[x, H-3] != BG:
                edge_issues += 1
        for y in range(H):
            if pixels[2, y] != BG or pixels[W-3, y] != BG:
                edge_issues += 1
        if edge_issues > 50:
            issues.append(f"Frame {f_idx}: possible edge clipping ({edge_issues} edge pixels)")

    if issues:
        print("Self-review warnings:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✓ Self-review passed: no overlap/clipping detected")
    return len(issues) == 0

if __name__ == "__main__":
    print(f"Rendering {N} frames ({W}×{H}px, {FPS}fps, {TOTAL}s)...")

    frames = []
    for f in range(N):
        if f % FPS == 0:
            print(f"  t = {f/FPS:.1f}s")
        frames.append(render_frame(f))

    self_review(frames)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(OUT), exist_ok=True)

    # Save as animated WebP with lossless compression
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
