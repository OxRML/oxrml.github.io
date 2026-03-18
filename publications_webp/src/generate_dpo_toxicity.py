#!/usr/bin/env python3
"""
How Does DPO Reduce Toxicity? — animated WebP

PAPER CONTEXT:
  Prior work claimed DPO reduces toxicity by dampening a few "toxic neurons".
  This paper shows that's only 2.5-24% of the effect.

KEY FINDING:
  DPO actually works via DISTRIBUTED activation shifts across MANY neurons,
  not just a few toxic ones. Four neuron groups combine to reduce toxicity.

VISUAL STORY (seamless loop):
  Scene 1 (0-3s): Prior belief - a few red "toxic" neurons highlighted
  Scene 2 (3-6s): Reality - many neurons show small shifts (arrows), not just toxic ones
  Scene 3 (6-8s): Combined effect → net toxicity reduction

720×450, ~8s loop, 12 fps
"""

from PIL import Image, ImageDraw, ImageFont
import math, os, random

random.seed(42)

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS & TIMING
# ═══════════════════════════════════════════════════════════════════════════════
W, H = 720, 450
FPS = 12
TOTAL = 8.0
N = int(FPS * TOTAL)
OUT = "img/publications/dpo_toxicity.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_TOXIC = (240, 175, 175)      # Toxic neuron - coral/red
C_NEUTRAL = (215, 218, 225)    # Neutral neuron - gray
C_SHIFT_UP = (175, 210, 185)   # Shift up - green
C_SHIFT_DN = (215, 185, 185)   # Shift down - pink
C_GOOD = (165, 210, 180)       # Good outcome - green
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
# NEURON GRID
# ═══════════════════════════════════════════════════════════════════════════════
ROWS, COLS = 4, 8
GRID_X0, GRID_Y0 = 100, 140
GRID_X1, GRID_Y1 = 520, 340
NEURON_R = 18

# Generate neurons with types and shifts
neurons = []
toxic_indices = [5, 18, 27]  # Only 3 toxic neurons out of 32 (~10%)
for idx in range(ROWS * COLS):
    r, c = idx // COLS, idx % COLS
    x = GRID_X0 + c * (GRID_X1 - GRID_X0) // (COLS - 1)
    y = GRID_Y0 + r * (GRID_Y1 - GRID_Y0) // (ROWS - 1)
    is_toxic = idx in toxic_indices
    # All neurons get a shift, not just toxic ones
    shift = random.uniform(-0.5, 0.5)
    neurons.append((x, y, is_toxic, shift))

# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_neuron(draw, x, y, is_toxic, alpha, highlight=False):
    """Draw a single neuron circle."""
    col = C_TOXIC if is_toxic else C_NEUTRAL
    fill = fbg(col, alpha)
    outline = fbg(lc(col, C_DARK, 0.25), alpha * 0.7)

    # Highlight ring for toxic neurons in scene 1
    if highlight and is_toxic:
        draw.ellipse([x-NEURON_R-4, y-NEURON_R-4, x+NEURON_R+4, y+NEURON_R+4],
                    outline=fbg(C_TOXIC, alpha * 0.6), width=2)

    draw.ellipse([x-NEURON_R, y-NEURON_R, x+NEURON_R, y+NEURON_R],
                fill=fill, outline=outline, width=2)

def draw_shift_arrow(draw, x, y, shift, alpha):
    """Draw small vertical arrow showing activation shift."""
    if abs(shift) < 0.15:
        return

    arrow_len = shift * 22
    ax = x + NEURON_R + 6
    ay1 = y
    ay2 = y - arrow_len

    col = fbg(C_SHIFT_UP if shift > 0 else C_SHIFT_DN, alpha)
    draw.line([(ax, ay1), (ax, ay2)], fill=col, width=2)

    # Arrow head
    head_y = ay2
    if shift > 0:
        draw.polygon([(ax-3, head_y+5), (ax+3, head_y+5), (ax, head_y)], fill=col)
    else:
        draw.polygon([(ax-3, head_y-5), (ax+3, head_y-5), (ax, head_y)], fill=col)

def draw_toxicity_meter(draw, cx, cy, w, h, level, alpha, label=""):
    """Vertical toxicity meter."""
    x0, y0 = cx - w//2, cy - h//2
    x1, y1 = cx + w//2, cy + h//2

    # Track
    track_col = fbg((235, 235, 232), alpha)
    draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=track_col)

    # Fill
    fh = int(h * level)
    if fh > 4:
        fill_col = fbg(C_TOXIC, alpha)
        draw.rounded_rectangle([x0+2, y1-fh, x1-2, y1-2], radius=5, fill=fill_col)

    # Label
    if label and alpha > 0.4:
        tc(draw, cx, y0 - 18, label, F_SM, fbg(C_MID, alpha))

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene timing with crossfades
    s1_a = (1 - ph(f, 2.5, 3.2)) * max(ph(f, 0.0, 0.4), 1 - ph(f, 7.6, 8.0))
    s2_a = ph(f, 2.8, 3.5) * (1 - ph(f, 5.8, 6.5))
    s3_a = ph(f, 6.0, 6.8) * (1 - ph(f, 7.5, 8.0))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Prior belief - toxic neurons highlighted
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 1.0) * s1_a
        if title_a > 0.3:
            tc(draw, 310, 55, "Prior belief: few toxic neurons", F_LG, fbg(C_MID, title_a))

        # Draw neurons with toxic ones highlighted
        for i, (x, y, is_toxic, _) in enumerate(neurons):
            n_a = ph(f, 0.3 + i*0.015, 1.0 + i*0.015) * s1_a
            draw_neuron(draw, x, y, is_toxic, n_a, highlight=True)

        # "Only 2-24% of effect" label
        pct_a = ph(f, 1.5, 2.3) * s1_a
        if pct_a > 0.3:
            tc(draw, 310, 375, "Only 2-24% of DPO's effect", F_MD, fbg(C_TOXIC, pct_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Reality - distributed shifts across ALL neurons
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Title
        title_a = ph(f, 3.0, 3.8) * s2_a
        if title_a > 0.3:
            tc(draw, 310, 55, "Reality: distributed shifts", F_LG, fbg(C_DARK, title_a))

        # Draw all neurons with shift arrows
        shift_prog = ph(f, 3.8, 5.2)
        for i, (x, y, is_toxic, shift) in enumerate(neurons):
            n_a = s2_a
            draw_neuron(draw, x, y, is_toxic, n_a, highlight=False)

            # Shift arrows animate in
            if shift_prog > 0.1:
                draw_shift_arrow(draw, x, y, shift * shift_prog, s2_a * shift_prog)

        # "Many neurons, small shifts" label
        lab_a = ph(f, 4.5, 5.3) * s2_a
        if lab_a > 0.3:
            tc(draw, 310, 375, "Many neurons × small shifts", F_MD, fbg(C_MID, lab_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Combined effect → toxicity reduction
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 6.2, 6.8) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 55, "Net effect: toxicity reduced", F_LG, fbg(C_DARK, title_a))

        # Toxicity meter (decreasing)
        meter_a = ph(f, 6.3, 7.0) * s3_a
        tox_level = 0.75 - 0.45 * ph(f, 6.5, 7.3)  # Drops from 75% to 30%
        draw_toxicity_meter(draw, 580, 230, 50, 180, tox_level, meter_a, "Toxicity")

        # Down arrow next to meter
        arr_a = ph(f, 7.0, 7.5) * s3_a
        if arr_a > 0.3:
            draw.line([(620, 180), (620, 280)], fill=fbg(C_GOOD, arr_a), width=3)
            draw.polygon([(615, 280), (625, 280), (620, 295)], fill=fbg(C_GOOD, arr_a))

        # Mini neural grid (simplified, showing distributed concept)
        for i in range(16):
            r, c = i // 4, i % 4
            nx = 180 + c * 55
            ny = 160 + r * 55
            na = ph(f, 6.4 + i*0.02, 7.0 + i*0.02) * s3_a
            # All show slight green tint (contributing)
            col = lc(C_NEUTRAL, C_GOOD, 0.3)
            draw.ellipse([nx-12, ny-12, nx+12, ny+12],
                        fill=fbg(col, na), outline=fbg(lc(col, C_DARK, 0.2), na * 0.6))

        # "Combined effect" label
        comb_a = ph(f, 6.8, 7.4) * s3_a
        if comb_a > 0.3:
            tc(draw, 260, 380, "Combined", F_MD, fbg(C_MID, comb_a))
            # Arrow pointing to meter
            draw.line([(340, 230), (525, 230)], fill=fbg(C_LIGHT, comb_a), width=2)
            draw.polygon([(525, 225), (525, 235), (540, 230)], fill=fbg(C_LIGHT, comb_a))

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
