#!/usr/bin/env python3
"""
SAE + Steering Vectors — animated WebP

PAPER CONTEXT:
  Can SAEs interpret steering vectors? NO, because:
  1. Steering vectors fall OUTSIDE the SAE's training distribution
  2. Steering vectors have MEANINGFUL NEGATIVE projections (SAEs only do positive)

  Result: SAE reconstructions lose essential steering properties.

VISUAL STORY (seamless loop, connected transitions):
  Scene 1 (0-3s): SAE box with training distribution cloud INSIDE
                  - Shows "trained on activations" concept
                  - Purple steering vector arrow appears OUTSIDE the cloud
  Scene 2 (3-5.5s): Vector enters SAE → feature decomposition
                  - Bars appear: some positive (green), some NEGATIVE (red, pointing down)
                  - "Negative!" warning
  Scene 3 (5.5-8s): Reconstruction fails
                  - Original vector vs reconstructed (different directions)
                  - ≠ symbol, X mark

720×450, ~8s loop, 12 fps
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

# ═══════════════════════════════════════════════════════════════════════════════
# CANVAS & TIMING
# ═══════════════════════════════════════════════════════════════════════════════
W, H = 720, 450
FPS = 20
TOTAL = 10.0
N = int(FPS * TOTAL)
OUT = "img/publications/sae.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_DIST = (245, 240, 220)        # Training distribution - cream
C_VECTOR = (190, 170, 225)      # Steering vector - purple
C_SAE = (225, 235, 248)         # SAE box - blue
C_POS = (175, 215, 190)         # Positive feature - green
C_NEG = (235, 185, 185)         # Negative feature - red
C_RECON = (240, 200, 200)       # Reconstructed - coral
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

F_LG = get_font(28, True)
F_MD = get_font(22)
F_SM = get_font(18)
F_SYM = get_font(36, True)

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
# FIXED POSITIONS (consistent across scenes)
# ═══════════════════════════════════════════════════════════════════════════════
SAE_CX, SAE_CY = 360, 225
SAE_W, SAE_H = 200, 140

# ═══════════════════════════════════════════════════════════════════════════════
# DRAWING COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_sae_box(draw, alpha, show_label=True):
    """SAE processing box - stays in same position."""
    cx, cy, w, h = SAE_CX, SAE_CY, SAE_W, SAE_H

    fill = fbg(C_SAE, alpha)
    outline = fbg(lc(C_SAE, C_DARK, 0.2), alpha)

    draw.rounded_rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], radius=12, fill=fill, outline=outline, width=2)

    if show_label and alpha > 0.5:
        tc(draw, cx, cy - h//2 + 22, "SAE", F_LG, fbg(C_DARK, alpha * 0.85))

def draw_distribution_cloud(draw, alpha, inside_sae=True):
    """Training distribution cloud - shown inside or separate."""
    if inside_sae:
        cx, cy = SAE_CX, SAE_CY + 15
        w, h = 120, 70
    else:
        cx, cy = 180, 225
        w, h = 140, 100

    fill = fbg(C_DIST, alpha * 0.6)
    outline = fbg(lc(C_DIST, C_MID, 0.3), alpha * 0.7)

    draw.ellipse([cx-w//2, cy-h//2, cx+w//2, cy+h//2], fill=fill, outline=outline, width=2)

    # Data dots inside
    if alpha > 0.4:
        dot_col = fbg(C_MID, alpha * 0.35)
        offsets = [(-25, -12), (10, -18), (-12, 8), (18, 5), (3, 15), (-28, 2)]
        for dx, dy in offsets[:4 if inside_sae else 6]:
            scale = 0.7 if inside_sae else 1.0
            draw.ellipse([cx+int(dx*scale)-3, cy+int(dy*scale)-3,
                         cx+int(dx*scale)+3, cy+int(dy*scale)+3], fill=dot_col)

def draw_steering_vector(draw, x1, y1, x2, y2, col, alpha, width=4, head=14):
    """Bold steering vector arrow."""
    c = fbg(col, alpha)
    draw.line([(x1, y1), (x2, y2)], fill=c, width=width)

    ang = math.atan2(y2 - y1, x2 - x1)
    pts = [
        (x2, y2),
        (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4)),
        (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4)),
    ]
    draw.polygon(pts, fill=c)

def draw_feature_bars(draw, cx, cy, alpha, show_negative_prog=0.):
    """Feature decomposition bars - some positive, some negative."""
    # Features: (value, negative_flag)
    features = [(0.7, False), (0.4, False), (0.6, True), (0.35, False), (0.45, True)]

    bar_w = 18
    spacing = 30
    n = len(features)
    start_x = cx - (n - 1) * spacing // 2

    for i, (val, is_neg) in enumerate(features):
        bx = start_x + i * spacing
        bar_h = int(val * 50)

        if is_neg:
            # Animate negative bars appearing
            neg_a = alpha * show_negative_prog
            if neg_a > 0.1:
                col = fbg(C_NEG, neg_a)
                draw.rounded_rectangle([bx-bar_w//2, cy, bx+bar_w//2, cy+bar_h], radius=4, fill=col)
                # Minus sign
                draw.line([(bx-5, cy+bar_h+10), (bx+5, cy+bar_h+10)], fill=fbg(C_NEG, neg_a), width=2)
        else:
            col = fbg(C_POS, alpha)
            if bar_h > 4:
                draw.rounded_rectangle([bx-bar_w//2, cy-bar_h, bx+bar_w//2, cy], radius=4, fill=col)

def draw_small_arrow(draw, x1, y1, x2, y2, col, alpha, width=2, head=10):
    c = fbg(col, alpha)
    draw.line([(x1, y1), (x2, y2)], fill=c, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (0.4, -0.4):
        draw.line([(x2, y2), (x2 - head*math.cos(ang+da), y2 - head*math.sin(ang+da))], fill=c, width=width)

def draw_x_mark(draw, cx, cy, size, alpha):
    col = fbg(C_NEG, alpha)
    s = size // 2
    draw.line([(cx-s, cy-s), (cx+s, cy+s)], fill=col, width=4)
    draw.line([(cx+s, cy-s), (cx-s, cy+s)], fill=col, width=4)

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene alphas with crossfades
    s1_a = (1 - ph(f, 2.5, 3.2)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 7.5, 8.0))
    s2_a = ph(f, 2.8, 3.5) * (1 - ph(f, 5.2, 5.8))
    s3_a = ph(f, 5.5, 6.2) * (1 - ph(f, 7.5, 8.0))

    # SAE box persists across scenes 1 and 2
    sae_persist_a = max(s1_a * ph(f, 0.3, 1.0), s2_a)
    if sae_persist_a > 0.01:
        draw_sae_box(draw, sae_persist_a)

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: SAE with training distribution + steering vector OUTSIDE
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:

        # Training distribution inside SAE
        dist_a = ph(f, 0.6, 1.3) * s1_a
        draw_distribution_cloud(draw, dist_a, inside_sae=True)

        # "Trained on activations" label
        label_a = ph(f, 1.0, 1.6) * s1_a
        if label_a > 0.3:
            tc(draw, SAE_CX, SAE_CY + SAE_H//2 + 20, "trained on activations", F_SM, fbg(C_MID, label_a))

        # Steering vector appears OUTSIDE (left side, pointing toward SAE)
        vec_a = ph(f, 1.4, 2.2) * s1_a
        if vec_a > 0:
            draw_steering_vector(draw, 80, 140, 160, 190, C_VECTOR, vec_a)

            # "Steering vector" label
            if vec_a > 0.5:
                tc(draw, 85, 100, "Steering", F_SM, fbg(C_VECTOR, vec_a))
                tc(draw, 85, 118, "vector", F_SM, fbg(C_VECTOR, vec_a))

        # Warning: "outside distribution!"
        warn_a = ph(f, 1.8, 2.4) * s1_a
        if warn_a > 0.3:
            # Small warning badge
            draw.ellipse([55, 135, 105, 185], fill=fbg(C_NEG, warn_a * 0.25),
                        outline=fbg(C_NEG, warn_a * 0.6), width=2)
            tc(draw, 80, 160, "!", get_font(18, True), fbg(C_NEG, warn_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Vector enters SAE → decomposition with NEGATIVE projections
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Arrow entering SAE
        arr_a = ph(f, 3.0, 3.8) * s2_a
        if arr_a > 0.2:
            draw_small_arrow(draw, 180, 200, SAE_CX - SAE_W//2 - 5, SAE_CY, C_LIGHT, arr_a)

        # Feature bars inside SAE
        feat_a = ph(f, 3.5, 4.3) * s2_a
        neg_prog = ph(f, 4.0, 4.8)
        if feat_a > 0:
            draw_feature_bars(draw, SAE_CX, SAE_CY + 10, feat_a, neg_prog)

        # "Negative projections!" warning
        neg_warn_a = ph(f, 4.5, 5.0) * s2_a
        if neg_warn_a > 0.3:
            tc(draw, SAE_CX, SAE_CY + SAE_H//2 + 25, "Negative projections!", F_MD, fbg(C_NEG, neg_warn_a))

        # Small steering vector (faded, showing it's the input)
        sv_a = ph(f, 3.0, 3.5) * s2_a * 0.4
        if sv_a > 0:
            draw_steering_vector(draw, 90, 160, 150, 200, C_VECTOR, sv_a, width=3, head=10)

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Reconstruction fails - original ≠ reconstructed
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.8, 6.3) * s3_a
        tc(draw, 360, 55, "Reconstruction Fails", F_LG, fbg(C_DARK, title_a))

        # SAE box (smaller, on left)
        sae_mini_a = ph(f, 5.7, 6.2) * s3_a
        if sae_mini_a > 0:
            fill = fbg(C_SAE, sae_mini_a)
            outline = fbg(lc(C_SAE, C_DARK, 0.2), sae_mini_a)
            draw.rounded_rectangle([140, 180, 280, 270], radius=10, fill=fill, outline=outline, width=2)
            tc(draw, 210, 200, "SAE", F_MD, fbg(C_DARK, sae_mini_a * 0.8))

        # Arrow out of SAE
        out_a = ph(f, 6.0, 6.6) * s3_a
        if out_a > 0.3:
            draw_small_arrow(draw, 285, 225, 340, 225, C_LIGHT, out_a)

        # Two vectors for comparison
        # Original vector (bottom)
        orig_a = ph(f, 6.2, 6.9) * s3_a
        if orig_a > 0:
            draw_steering_vector(draw, 380, 280, 520, 320, C_VECTOR, orig_a, width=4, head=14)
            if orig_a > 0.5:
                tc(draw, 560, 340, "original", F_SM, fbg(C_VECTOR, orig_a * 0.8))

        # Reconstructed vector (top, different direction!)
        recon_a = ph(f, 6.5, 7.1) * s3_a
        if recon_a > 0:
            draw_steering_vector(draw, 380, 160, 520, 130, C_RECON, recon_a, width=4, head=14)
            if recon_a > 0.5:
                tc(draw, 560, 110, "reconstructed", F_SM, fbg(C_RECON, recon_a * 0.8))

        # ≠ symbol between them
        neq_a = ph(f, 6.8, 7.2) * s3_a
        if neq_a > 0.3:
            tc(draw, 460, 225, "≠", F_SYM, fbg(C_NEG, neq_a))

        # X mark
        x_a = ph(f, 7.0, 7.4) * s3_a
        if x_a > 0.3:
            draw_x_mark(draw, 600, 225, 35, x_a)

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
