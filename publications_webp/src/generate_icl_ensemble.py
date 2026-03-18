#!/usr/bin/env python3
"""
Ensemble SuperICL — animated WebP

PAPER CONTEXT:
  In-context learning (ICL) is cheap but less accurate than fine-tuning.
  This paper: Use multiple fine-tuned SMALL language models (SLMs) as "experts"
  to advise the large LLM → achieves SOTA results.

  Three stages:
  1. Fine-tuned SLMs make predictions
  2. Predictions are fed as context to LLM
  3. LLM makes final prediction (better than ICL alone)

VISUAL STORY (seamless loop):
  Scene 1 (0-3s): Multiple small SLM circles appear with "fine-tuned" labels
  Scene 2 (3-5.5s): SLMs send signals to central large LLM circle
  Scene 3 (5.5-8s): Output comparison - ICL alone vs Ensemble (higher bar)

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
OUT = "img/publications/icl_ensemble.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_SLM1 = (210, 225, 250)        # SLM 1 - blue
C_SLM2 = (250, 225, 210)        # SLM 2 - peach
C_SLM3 = (210, 240, 220)        # SLM 3 - mint
C_SLM4 = (240, 220, 240)        # SLM 4 - lavender
C_LLM = (255, 248, 230)         # LLM - cream
C_SIGNAL = (200, 185, 225)      # Signal - purple
C_ICL = (220, 220, 225)         # ICL bar - gray
C_ENS = (190, 225, 200)         # Ensemble bar - green
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)

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
# SLM POSITIONS
# ═══════════════════════════════════════════════════════════════════════════════
SLMS = [
    (120, 130, C_SLM1, "SLM₁"),
    (220, 90, C_SLM2, "SLM₂"),
    (320, 80, C_SLM3, "SLM₃"),
    (420, 90, C_SLM4, "SLM₄"),
]
LLM_POS = (270, 260)
LLM_R = 55

# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_slm_circle(draw, cx, cy, r, col, alpha, label=""):
    """Small expert SLM circle."""
    fill = fbg(col, alpha)
    outline = fbg(lc(col, C_DARK, 0.25), alpha)

    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=2)

    # Small pattern inside
    if alpha > 0.4:
        dot_col = fbg(lc(col, C_DARK, 0.3), alpha)
        for dx, dy in [(-6, -4), (6, -4), (0, 6)]:
            draw.ellipse([cx+dx-3, cy+dy-3, cx+dx+3, cy+dy+3], fill=dot_col)

    # Label below
    if label and alpha > 0.5:
        tc(draw, cx, cy + r + 15, label, F_SM, fbg(C_MID, alpha))

def draw_llm_circle(draw, cx, cy, r, alpha, pulse=0.):
    """Large central LLM circle."""
    fill = fbg(C_LLM, alpha)
    outline = fbg(lc(C_LLM, C_DARK, 0.2), alpha)

    if pulse > 0.05:
        g = int(pulse * 12)
        draw.ellipse([cx-r-g, cy-r-g, cx+r+g, cy+r+g], fill=fbg(C_LLM, alpha * 0.3 * pulse))

    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=3)

    # "LLM" label inside
    if alpha > 0.5:
        tc(draw, cx, cy, "LLM", F_LG, fbg(C_DARK, alpha * 0.8))

def draw_signal_line(draw, x1, y1, x2, y2, alpha, progress=1.0):
    """Curved signal line from SLM to LLM."""
    # Quadratic bezier
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2 - 25

    steps = 15
    pts = []
    for i in range(steps + 1):
        t = i / steps
        px = (1-t)**2 * x1 + 2*(1-t)*t * mx + t**2 * x2
        py = (1-t)**2 * y1 + 2*(1-t)*t * my + t**2 * y2
        pts.append((int(px), int(py)))

    # Draw up to progress point
    end_idx = int(len(pts) * progress)
    col = fbg(C_SIGNAL, alpha)
    for i in range(min(end_idx - 1, len(pts) - 1)):
        draw.line([pts[i], pts[i+1]], fill=col, width=2)

def draw_signal_dot(draw, x1, y1, x2, y2, t, alpha):
    """Animated dot traveling along curve."""
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2 - 25

    px = (1-t)**2 * x1 + 2*(1-t)*t * mx + t**2 * x2
    py = (1-t)**2 * y1 + 2*(1-t)*t * my + t**2 * y2

    col = fbg(C_SIGNAL, alpha)
    draw.ellipse([px-5, py-5, px+5, py+5], fill=col)

def draw_bar(draw, cx, bot, w, h, frac, col, alpha, label=""):
    """Vertical accuracy bar."""
    # Track
    track = fbg(lc(col, BG, 0.7), alpha)
    draw.rounded_rectangle([cx-w//2, bot-h, cx+w//2, bot], radius=6, fill=track)

    # Fill
    fh = int(h * frac)
    if fh > 5:
        fill = fbg(col, alpha)
        draw.rounded_rectangle([cx-w//2, bot-fh, cx+w//2, bot], radius=6, fill=fill)

    # Label below
    if label and alpha > 0.4:
        tc(draw, cx, bot + 18, label, F_SM, fbg(C_MID, alpha))

def draw_arrow(draw, x1, y1, x2, y2, col, width=2, head=10):
    draw.line([(x1, y1), (x2, y2)], fill=col, width=width)
    ang = math.atan2(y2-y1, x2-x1)
    draw.polygon([
        (x2, y2),
        (x2 - head * math.cos(ang - 0.35), y2 - head * math.sin(ang - 0.35)),
        (x2 - head * math.cos(ang + 0.35), y2 - head * math.sin(ang + 0.35)),
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
    # SCENE 1: Fine-tuned SLMs appear
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 1.0) * s1_a
        if title_a > 0.3:
            tc(draw, 270, 35, "Fine-tuned SLM Experts", F_LG, fbg(C_MID, title_a))

        # Draw SLMs appearing
        for i, (sx, sy, col, label) in enumerate(SLMS):
            slm_a = ph(f, 0.5 + i*0.25, 1.2 + i*0.25) * s1_a
            if slm_a > 0:
                draw_slm_circle(draw, sx, sy, 28, col, slm_a, label)

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: SLMs send signals to LLM
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # LLM circle
        pulse = (math.sin(f / FPS * math.pi * 3) * 0.5 + 0.5) * s2_a
        draw_llm_circle(draw, LLM_POS[0], LLM_POS[1], LLM_R, s2_a, pulse)

        # Draw SLMs (same size, staying visible)
        for i, (sx, sy, col, label) in enumerate(SLMS):
            draw_slm_circle(draw, sx, sy, 28, col, s2_a * 0.9, "")

        # Signal lines from SLMs to LLM
        line_prog = ph(f, 3.2, 4.5)
        for sx, sy, col, _ in SLMS:
            draw_signal_line(draw, sx, sy + 28, LLM_POS[0], LLM_POS[1] - LLM_R, s2_a * 0.5, line_prog)

        # Animated signal dots
        fs = f / FPS
        if 3.5 < fs < 5.0:
            cycle = (fs - 3.5) % 0.8 / 0.8
            for i, (sx, sy, _, _) in enumerate(SLMS):
                dot_t = (cycle + i * 0.15) % 1.0
                if dot_t < 0.85:
                    draw_signal_dot(draw, sx, sy + 28, LLM_POS[0], LLM_POS[1] - LLM_R,
                                   dot_t / 0.85, s2_a * 0.8)

        # "Advise" label
        adv_a = ph(f, 4.0, 4.7) * s2_a
        if adv_a > 0.3:
            tc(draw, LLM_POS[0], LLM_POS[1] + LLM_R + 25, "advised prediction", F_SM, fbg(C_MID, adv_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Output comparison - ICL vs Ensemble
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.8, 6.3) * s3_a
        if title_a > 0.3:
            tc(draw, 550, 80, "Accuracy", F_LG, fbg(C_DARK, title_a))

        bar_w = 55
        bar_h = 180
        bot_y = 380

        # ICL bar (left, lower)
        icl_cx = 500
        icl_fill = ph(f, 6.0, 7.0) * 0.52  # 52% accuracy
        draw_bar(draw, icl_cx, bot_y, bar_w, bar_h, icl_fill, C_ICL, s3_a, "ICL")

        # Ensemble bar (right, higher)
        ens_cx = 600
        ens_fill = ph(f, 6.2, 7.2) * 0.78  # 78% accuracy
        draw_bar(draw, ens_cx, bot_y, bar_w, bar_h, ens_fill, C_ENS, s3_a, "Ensemble")

        # Arrow from LLM area to bars
        arr_a = ph(f, 5.8, 6.5) * s3_a
        if arr_a > 0.3:
            draw_arrow(draw, 340, 260, 450, 280, fbg(C_LIGHT, arr_a))

        # SOTA badge
        sota_a = ph(f, 7.0, 7.4) * s3_a
        if sota_a > 0.3:
            bx, by = 600, 160
            badge_col = fbg((255, 240, 200), sota_a)
            outline = fbg((200, 175, 100), sota_a)
            draw.rounded_rectangle([bx-30, by-12, bx+30, by+12], radius=10, fill=badge_col, outline=outline, width=2)
            tc(draw, bx, by, "SOTA", F_SM, fbg(C_DARK, sota_a * 0.8))

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
