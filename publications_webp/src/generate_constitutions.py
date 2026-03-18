#!/usr/bin/env python3
"""
Constitutions Role Eval — animated WebP

PAPER CONTEXT:
  Tests how different "constitutions" (written guidelines) affect AI feedback quality.
  Applied to medical interviews for patient-centered communication.

KEY FINDING:
  - Detailed constitutions → better EMOTIVE feedback (empathy, rapport)
  - BUT: No constitution beats baseline for PRACTICAL skills (info gathering)

VISUAL STORY (seamless loop):
  Scene 1 (0-4s): Constitution doc → feeds into LLM critic → produces feedback
  Scene 2 (4-8s): Results comparison - Emotive bar rises high for detailed,
                  Practical bars stay equal (detailed ≠ better)
  Fade back to Scene 1

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
OUT = "img/publications/constitutions.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_DOC_A = (235, 218, 200)      # Basic constitution - warm beige
C_DOC_B = (195, 218, 240)      # Detailed constitution - blue
C_LLM = (218, 205, 235)        # LLM critic - purple
C_GOOD = (185, 225, 195)       # Success - green
C_NEUTRAL = (220, 220, 218)    # No difference - gray
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)

# ═══════════════════════════════════════════════════════════════════════════════
# FONTS
# ═══════════════════════════════════════════════════════════════════════════════
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
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

F_LG = get_font(32, True)
F_MD = get_font(26)
F_SM = get_font(20)

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
# DRAWING COMPONENTS
# ═══════════════════════════════════════════════════════════════════════════════

def draw_document(draw, cx, cy, w, h, col, alpha, num_lines=3, label=""):
    """Document with lines inside showing detail level."""
    fill = fbg(col, alpha)
    outline = fbg(lc(col, C_DARK, 0.25), alpha)
    x0, y0 = cx - w//2, cy - h//2
    x1, y1 = cx + w//2, cy + h//2
    draw.rounded_rectangle([x0, y0, x1, y1], radius=6, fill=fill, outline=outline, width=2)

    # Lines inside
    if alpha > 0.3:
        line_col = fbg(lc(col, C_DARK, 0.2), alpha * 0.6)
        spacing = (h - 30) // (num_lines + 1)
        for i in range(num_lines):
            ly = y0 + 15 + (i + 1) * spacing
            lw = w - 24 - (i % 2) * 15
            draw.line([(x0 + 12, ly), (x0 + 12 + lw, ly)], fill=line_col, width=2)

    # Label below
    if label and alpha > 0.5:
        tc(draw, cx, y1 + 18, label, F_SM, fbg(C_MID, alpha))

def draw_llm_box(draw, cx, cy, w, h, alpha, label=""):
    """LLM critic box."""
    fill = fbg(C_LLM, alpha)
    outline = fbg(lc(C_LLM, C_DARK, 0.2), alpha)
    x0, y0 = cx - w//2, cy - h//2
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=10, fill=fill, outline=outline, width=2)

    # Neural dots
    if alpha > 0.4:
        for dx, dy in [(-20, -12), (0, -12), (20, -12), (-10, 10), (10, 10)]:
            draw.ellipse([cx+dx-4, cy+dy-4, cx+dx+4, cy+dy+4],
                        fill=fbg(lc(C_LLM, C_DARK, 0.3), alpha * 0.7))

    if label and alpha > 0.5:
        tc(draw, cx, y0 + h + 18, label, F_SM, fbg(C_MID, alpha))

def draw_feedback_bubble(draw, cx, cy, w, h, alpha):
    """Speech bubble for feedback."""
    fill = fbg((245, 245, 240), alpha)
    outline = fbg(C_LIGHT, alpha)
    x0, y0 = cx - w//2, cy - h//2
    draw.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=8, fill=fill, outline=outline, width=2)
    # Tail pointing left
    draw.polygon([(x0, cy - 6), (x0, cy + 6), (x0 - 12, cy)], fill=fill)
    # Lines inside
    if alpha > 0.4:
        for dy in [-8, 2, 12]:
            lw = w - 24 if dy != 12 else w - 40
            draw.line([(x0 + 12, cy + dy), (x0 + 12 + lw, cy + dy)],
                     fill=fbg(C_LIGHT, alpha * 0.6), width=2)

def draw_bar(draw, cx, bot_y, w, h, frac, col, alpha, label=""):
    """Vertical bar chart."""
    # Track
    track_col = fbg(lc(col, BG, 0.65), alpha)
    draw.rounded_rectangle([cx - w//2, bot_y - h, cx + w//2, bot_y], radius=5, fill=track_col)

    # Fill
    fh = int(h * frac)
    if fh > 4:
        fill_col = fbg(col, alpha)
        draw.rounded_rectangle([cx - w//2, bot_y - fh, cx + w//2, bot_y], radius=5, fill=fill_col)

    # Label
    if label and alpha > 0.4:
        tc(draw, cx, bot_y + 16, label, F_SM, fbg(C_MID, alpha))

def draw_arrow(draw, x1, y1, x2, y2, col, width=2, head=10):
    draw.line([(x1, y1), (x2, y2)], fill=col, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    for da in (0.4, -0.4):
        ax = x2 - head * math.cos(ang + da)
        ay = y2 - head * math.sin(ang + da)
        draw.line([(x2, y2), (int(ax), int(ay))], fill=col, width=width)

def draw_check(draw, cx, cy, size, col, alpha):
    c = fbg(col, alpha)
    draw.line([(cx - size*0.4, cy), (cx - size*0.1, cy + size*0.35)], fill=c, width=3)
    draw.line([(cx - size*0.1, cy + size*0.35), (cx + size*0.45, cy - size*0.35)], fill=c, width=3)

def draw_equals(draw, cx, cy, size, col, alpha):
    c = fbg(col, alpha)
    draw.line([(cx - size*0.3, cy - 5), (cx + size*0.3, cy - 5)], fill=c, width=3)
    draw.line([(cx - size*0.3, cy + 5), (cx + size*0.3, cy + 5)], fill=c, width=3)

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE RENDERING
# ═══════════════════════════════════════════════════════════════════════════════

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene timing
    # Scene 1: 0-5s (constitution → LLM → feedback)
    # Scene 2: 5-10s (results comparison)
    # Crossfade at boundaries for seamless loop

    s1_a = (1 - ph(f, 4.5, 5.2)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 9.5, 10.0))
    s2_a = ph(f, 4.8, 5.5) * (1 - ph(f, 9.2, 10.0))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Constitution → LLM Critic → Feedback
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Constitution document (left side)
        doc_a = ph(f, 0.4, 1.5) * s1_a
        draw_document(draw, 130, 200, 110, 140, C_DOC_B, doc_a, num_lines=6, label="Constitution")

        # Arrow from doc to LLM
        arr1_a = ph(f, 1.2, 2.2) * s1_a
        if arr1_a > 0.2:
            draw_arrow(draw, 190, 200, 260, 200, fbg(C_LIGHT, arr1_a))

        # LLM Critic (center)
        llm_a = ph(f, 1.6, 2.8) * s1_a
        draw_llm_box(draw, 340, 200, 120, 90, llm_a, "LLM Critic")

        # Arrow from LLM to feedback
        arr2_a = ph(f, 2.5, 3.5) * s1_a
        if arr2_a > 0.2:
            draw_arrow(draw, 405, 200, 475, 200, fbg(C_LIGHT, arr2_a))

        # Feedback bubble (right side)
        fb_a = ph(f, 3.2, 4.3) * s1_a
        draw_feedback_bubble(draw, 570, 200, 140, 80, fb_a)
        if fb_a > 0.6:
            tc(draw, 570, 200, "Feedback", F_MD, fbg(C_MID, fb_a))

        # "Medical interviews" context label at top
        ctx_a = ph(f, 0.6, 1.8) * s1_a
        if ctx_a > 0.3:
            tc(draw, 360, 50, "Patient-centered communication", F_MD, fbg(C_LIGHT, ctx_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Results - Emotive vs Practical
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        bar_w = 55
        bar_h = 150
        bot_y = 360

        # Left section: EMOTIVE (detailed wins)
        em_cx = 220
        em_a = ph(f, 5.3, 6.2) * s2_a

        if em_a > 0.3:
            tc(draw, em_cx, 90, "Emotive", F_LG, fbg(C_DARK, em_a))
            tc(draw, em_cx, 115, "(empathy, rapport)", F_SM, fbg(C_MID, em_a * 0.7))

        # Two bars: Basic (left, short) vs Detailed (right, tall)
        bar_prog = ph(f, 6.2, 7.8)

        # Basic bar
        b1_a = ph(f, 6.0, 6.8) * s2_a
        draw_bar(draw, em_cx - 40, bot_y, bar_w, bar_h, 0.42 * bar_prog, C_DOC_A, b1_a, "Basic")

        # Detailed bar (taller)
        b2_a = ph(f, 6.2, 7.0) * s2_a
        draw_bar(draw, em_cx + 40, bot_y, bar_w, bar_h, 0.78 * bar_prog, C_DOC_B, b2_a, "Detailed")

        # Checkmark above detailed bar
        check_a = ph(f, 7.5, 8.5) * s2_a
        if check_a > 0.3:
            draw_check(draw, em_cx + 40, bot_y - bar_h * 0.78 - 25, 20, (75, 155, 95), check_a)

        # Right section: PRACTICAL (no difference)
        pr_cx = 500
        pr_a = ph(f, 5.6, 6.5) * s2_a

        if pr_a > 0.3:
            tc(draw, pr_cx, 90, "Practical", F_LG, fbg(C_DARK, pr_a))
            tc(draw, pr_cx, 115, "(information gathering)", F_SM, fbg(C_MID, pr_a * 0.7))

        # Two bars: both same height
        b3_a = ph(f, 6.5, 7.3) * s2_a
        draw_bar(draw, pr_cx - 40, bot_y, bar_w, bar_h, 0.50 * bar_prog, C_DOC_A, b3_a, "Basic")

        b4_a = ph(f, 6.7, 7.5) * s2_a
        draw_bar(draw, pr_cx + 40, bot_y, bar_w, bar_h, 0.50 * bar_prog, C_DOC_B, b4_a, "Detailed")

        # Equals sign between (no winner)
        eq_a = ph(f, 7.8, 8.8) * s2_a
        if eq_a > 0.3:
            draw_equals(draw, pr_cx, bot_y - bar_h * 0.50 - 25, 25, C_MID, eq_a)

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

    # Self-review
    issues = 0
    for i in range(0, N, 8):
        for y in range(H):
            for x in range(W):
                if x < 6 or x >= W-6 or y < 6 or y >= H-6:
                    px = frames[i].getpixel((x, y))
                    if abs(px[0]-255) + abs(px[1]-255) + abs(px[2]-255) > 20:
                        issues += 1
                        break
            if issues: break

    if issues:
        print(f"⚠ Edge clipping detected")
    else:
        print("✓ Self-review passed")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    frames[0].save(OUT, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=int(1000/FPS), loop=0, lossless=True)
    print(f"✓ Saved → {OUT} ({os.path.getsize(OUT)//1024} KB)")
