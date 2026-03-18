#publications_webp/src/generate_counterfactual.py

"""
Paper Context:
"LLMs Don't Know Their Own Decision Boundaries"
- LLMs generate self-counterfactual explanations (SCEs)
- Example: Age=60, BP=135 → "high risk". SCE: "If BP=110, low risk"
- KEY FINDING: Validity-Minimality Trade-off
- When asked for counterfactual: VALID but NOT minimal (big jump)
- When asked for MINIMAL counterfactual: minimal but NOT valid (tiny step)

Visual Story:
Scene 1 (0-3s): Decision boundary scatter plot (Age vs Education)
- A data point appears in "Below $50K" region
- LLM prediction label
Scene 2 (3-6s): Two counterfactual attempts shown on the plot:
- Big arrow crossing boundary (valid, not minimal)
- Small arrow not crossing (minimal, not valid)
Scene 3 (6-8s): Trade-off summary with checkmarks/X marks

Frame and Scene timing Calculations:
Canvas: 720x450.
Frame calculation: FPS = 20, TOTAL = 10.0, N = int(FPS * TOTAL) = 200.
Scene timings: Scene 1 (0-3s) | Scene 2 (3-6s) | Scene 3 (6-8s).
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

# ======
# CANVAS & TIMING
# ======
W, H = 720, 450
FPS = 20
TOTAL = 10.0
N = int(FPS * TOTAL)
OUT_PATH = "img/publications/counterfactual.webp"

# ======
# PALETTE
# ======
BG = (255, 255, 255)
C_ABOVE = (195, 225, 210)       # Above $50K region - mint green
C_BELOW = (240, 220, 215)       # Below $50K region - warm pink
C_BOUNDARY = (180, 180, 195)    # Decision boundary line
C_POINT = (100, 120, 180)       # Original data point - blue
C_VALID = (130, 180, 140)       # Valid arrow - green
C_INVALID = (210, 140, 140)     # Invalid arrow - red
C_LLM = (220, 210, 235)         # LLM bubble - lavender
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)

# ======
# FONTS
# ======
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
F_AXIS = get_font(16)

# ======
# UTILITIES
# ======
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

# ======
# PLOT COORDINATES
# ======
# Decision boundary plot area
PLOT_X0, PLOT_Y0 = 80, 80
PLOT_X1, PLOT_Y1 = 380, 340
PLOT_W = PLOT_X1 - PLOT_X0
PLOT_H = PLOT_Y1 - PLOT_Y0

# Original point (in "Below" region)
ORIG_X, ORIG_Y = 180, 240

# Big jump target (crosses boundary - valid)
BIG_X, BIG_Y = 300, 140

# Small step target (doesn't cross - invalid)
SMALL_X, SMALL_Y = 200, 220

# ======
# DRAWING COMPONENTS
# ======

def draw_decision_plot(draw, alpha, show_boundary=True):
    """Draw the decision boundary scatter plot."""
    # Plot background regions
    # Upper-left region: Above $50K (green)
    # Lower-right region: Below $50K (pink)

    # Fill regions (split by diagonal)
    if alpha > 0.2:
        # Below region (lower-right triangle)
        pts_below = [(PLOT_X0, PLOT_Y1), (PLOT_X1, PLOT_Y0), (PLOT_X1, PLOT_Y1)]
        draw.polygon(pts_below, fill=fbg(C_BELOW, alpha * 0.4))

        # Above region (upper-left triangle)
        pts_above = [(PLOT_X0, PLOT_Y0), (PLOT_X1, PLOT_Y0), (PLOT_X0, PLOT_Y1)]
        draw.polygon(pts_above, fill=fbg(C_ABOVE, alpha * 0.4))

    # Plot border
    outline = fbg(C_MID, alpha * 0.5)
    draw.rectangle([PLOT_X0, PLOT_Y0, PLOT_X1, PLOT_Y1], outline=outline, width=2)

    # Decision boundary line (diagonal)
    if show_boundary and alpha > 0.3:
        b_col = fbg(C_BOUNDARY, alpha * 0.8)
        draw.line([(PLOT_X0, PLOT_Y1), (PLOT_X1, PLOT_Y0)], fill=b_col, width=3)

    # Axis labels
    if alpha > 0.5:
        ax_col = fbg(C_MID, alpha)
        tc(draw, (PLOT_X0 + PLOT_X1) // 2, PLOT_Y1 + 25, "Age →", F_AXIS, ax_col)
        # Rotated "Education" - just draw it vertically
        draw.text((PLOT_X0 - 50, PLOT_Y0 + PLOT_H // 2 - 30), "Edu", font=F_AXIS, fill=ax_col)
        draw.text((PLOT_X0 - 50, PLOT_Y0 + PLOT_H // 2 - 10), "→", font=F_AXIS, fill=ax_col)

    # Region labels
    if alpha > 0.6:
        tc(draw, PLOT_X0 + 55, PLOT_Y0 + 50, ">$50K", F_SM, fbg(lc(C_ABOVE, C_DARK, 0.4), alpha))
        tc(draw, PLOT_X1 - 55, PLOT_Y1 - 50, "<$50K", F_SM, fbg(lc(C_BELOW, C_DARK, 0.4), alpha))

def draw_data_point(draw, x, y, alpha, color=C_POINT, size=12, label=""):
    """Draw a data point dot."""
    r = size // 2
    fill = fbg(color, alpha)
    outline = fbg(lc(color, C_DARK, 0.3), alpha)
    draw.ellipse([x-r, y-r, x+r, y+r], fill=fill, outline=outline, width=2)

    if label and alpha > 0.5:
        tc(draw, x, y - r - 12, label, F_SM, fbg(C_DARK, alpha * 0.8))

def draw_arrow(draw, x1, y1, x2, y2, col, alpha, width=3, head=12, dashed=False):
    """Draw an arrow from (x1,y1) to (x2,y2)."""
    c = fbg(col, alpha)

    if dashed:
        # Draw dashed line
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx*dx + dy*dy)
        dash_len = 8
        num_dashes = int(dist / (dash_len * 2))
        for i in range(num_dashes):
            t1 = i * 2 * dash_len / dist
            t2 = (i * 2 + 1) * dash_len / dist
            if t2 > 1: t2 = 1
            px1, py1 = x1 + dx * t1, y1 + dy * t1
            px2, py2 = x1 + dx * t2, y1 + dy * t2
            draw.line([(px1, py1), (px2, py2)], fill=c, width=width)
    else:
        draw.line([(x1, y1), (x2, y2)], fill=c, width=width)

    # Arrow head
    ang = math.atan2(y2 - y1, x2 - x1)
    draw.polygon([
        (x2, y2),
        (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4)),
        (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4)),
    ], fill=c)

def draw_llm_bubble(draw, cx, cy, w, h, alpha, text=""):
    """LLM generating counterfactual."""
    fill = fbg(C_LLM, alpha)
    outline = fbg(lc(C_LLM, C_DARK, 0.2), alpha)

    draw.rounded_rectangle([cx-w//2, cy-h//2, cx+w//2, cy+h//2], radius=12, fill=fill, outline=outline, width=2)

    if text and alpha > 0.5:
        tc(draw, cx, cy, text, F_MD, fbg(C_DARK, alpha * 0.85))

def draw_result_icon(draw, cx, cy, is_valid, alpha, size=24):
    """Checkmark or X icon."""
    r = size // 2

    if is_valid:
        col = fbg(C_VALID, alpha)
        # Checkmark
        draw.line([(cx-r+2, cy), (cx-2, cy+r-2)], fill=col, width=3)
        draw.line([(cx-2, cy+r-2), (cx+r, cy-r+4)], fill=col, width=3)
    else:
        col = fbg(C_INVALID, alpha)
        # X mark
        draw.line([(cx-r+4, cy-r+4), (cx+r-4, cy+r-4)], fill=col, width=3)
        draw.line([(cx+r-4, cy-r+4), (cx-r+4, cy+r-4)], fill=col, width=3)

# ======
# SCENE RENDERING
# ======

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene timing with crossfades
    s1_a = (1 - ph(f, 2.5, 3.2)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 7.5, 8.0))
    s2_a = ph(f, 2.8, 3.5) * (1 - ph(f, 5.8, 6.5))
    s3_a = ph(f, 6.2, 6.8) * (1 - ph(f, 7.5, 8.0))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Decision boundary plot + original point + LLM prediction
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Draw decision boundary plot
        plot_a = ph(f, 0.3, 1.2) * s1_a
        draw_decision_plot(draw, plot_a)

        # Original data point appears
        pt_a = ph(f, 1.0, 1.8) * s1_a
        draw_data_point(draw, ORIG_X, ORIG_Y, pt_a, C_POINT, 14, "input")

        # LLM bubble with prediction
        llm_a = ph(f, 1.5, 2.3) * s1_a
        draw_llm_bubble(draw, 550, 150, 160, 70, llm_a, "LLM: <$50K")

        # Arrow from point to LLM
        if llm_a > 0.3:
            draw_arrow(draw, ORIG_X + 15, ORIG_Y - 10, 465, 150, C_LIGHT, llm_a * 0.6, width=2, head=8, dashed=True)

        # Question text
        q_a = ph(f, 2.0, 2.5) * s1_a
        if q_a > 0.3:
            tc(draw, 550, 230, '"What change', F_SM, fbg(C_MID, q_a))
            tc(draw, 550, 250, 'flips to >$50K?"', F_SM, fbg(C_MID, q_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Two counterfactual attempts on the plot
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Keep showing the plot
        draw_decision_plot(draw, s2_a)

        # Original point (faded)
        draw_data_point(draw, ORIG_X, ORIG_Y, s2_a * 0.7, C_POINT, 12)

        # BIG JUMP: crosses boundary (valid but not minimal)
        big_a = ph(f, 3.3, 4.2) * s2_a
        if big_a > 0.1:
            # Arrow for big jump
            draw_arrow(draw, ORIG_X, ORIG_Y, BIG_X, BIG_Y, C_VALID, big_a, width=4)
            # Target point
            draw_data_point(draw, BIG_X, BIG_Y, big_a, C_VALID, 12)

        # Label for big jump
        big_lab_a = ph(f, 4.0, 4.8) * s2_a
        if big_lab_a > 0.3:
            tc(draw, 480, 120, "Big change", F_MD, fbg(C_VALID, big_lab_a))
            tc(draw, 480, 145, "→ valid", F_SM, fbg(C_VALID, big_lab_a * 0.8))

        # SMALL STEP: doesn't cross boundary (minimal but not valid)
        small_a = ph(f, 4.5, 5.3) * s2_a
        if small_a > 0.1:
            # Arrow for small step
            draw_arrow(draw, ORIG_X, ORIG_Y, SMALL_X, SMALL_Y, C_INVALID, small_a, width=4)
            # Target point
            draw_data_point(draw, SMALL_X, SMALL_Y, small_a, C_INVALID, 12)

        # Label for small step
        small_lab_a = ph(f, 5.0, 5.6) * s2_a
        if small_lab_a > 0.3:
            tc(draw, 480, 280, "Small change", F_MD, fbg(C_INVALID, small_lab_a))
            tc(draw, 480, 305, "→ invalid", F_SM, fbg(C_INVALID, small_lab_a * 0.8))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Trade-off summary
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 6.3, 6.8) * s3_a
        tc(draw, 360, 60, "Validity-Minimality Trade-off", F_LG, fbg(C_DARK, title_a))

        # Two rows: counterfactual type | validity | minimality
        row1_y = 160
        row2_y = 280

        # Headers
        hdr_a = ph(f, 6.4, 7.0) * s3_a
        if hdr_a > 0.3:
            tc(draw, 250, 100, "Type", F_MD, fbg(C_MID, hdr_a))
            tc(draw, 420, 100, "Valid?", F_MD, fbg(C_MID, hdr_a))
            tc(draw, 560, 100, "Minimal?", F_MD, fbg(C_MID, hdr_a))

        # Row 1: Counterfactual → Valid ✓, Minimal ✗
        r1_a = ph(f, 6.5, 7.1) * s3_a
        if r1_a > 0.3:
            # Card for type
            draw.rounded_rectangle([120, row1_y - 30, 350, row1_y + 30], radius=8,
                                  fill=fbg((240, 245, 250), r1_a), outline=fbg(C_LIGHT, r1_a), width=2)
            tc(draw, 235, row1_y, '"Give counterfactual"', F_SM, fbg(C_DARK, r1_a * 0.85))

            # Valid checkmark
            draw_result_icon(draw, 420, row1_y, True, r1_a, 28)

            # Not minimal X
            draw_result_icon(draw, 560, row1_y, False, r1_a, 28)

        # Row 2: Minimal counterfactual → Valid ✗, Minimal ✓
        r2_a = ph(f, 6.7, 7.3) * s3_a
        if r2_a > 0.3:
            # Card for type
            draw.rounded_rectangle([120, row2_y - 30, 350, row2_y + 30], radius=8,
                                  fill=fbg((240, 245, 250), r2_a), outline=fbg(C_LIGHT, r2_a), width=2)
            tc(draw, 235, row2_y, '"Give minimal CF"', F_SM, fbg(C_DARK, r2_a * 0.85))

            # Not valid X
            draw_result_icon(draw, 420, row2_y, False, r2_a, 28)

            # Minimal checkmark
            draw_result_icon(draw, 560, row2_y, True, r2_a, 28)

        # Trade-off arrow
        trade_a = ph(f, 7.0, 7.4) * s3_a
        if trade_a > 0.3:
            mid_y = (row1_y + row2_y) // 2
            arrow_col = fbg(C_MID, trade_a)
            # Double-headed vertical arrow
            draw.line([(490, row1_y + 40), (490, row2_y - 40)], fill=arrow_col, width=2)
            draw.polygon([(485, row1_y + 45), (495, row1_y + 45), (490, row1_y + 35)], fill=arrow_col)
            draw.polygon([(485, row2_y - 45), (495, row2_y - 45), (490, row2_y - 35)], fill=arrow_col)

        # Conclusion label
        conc_a = ph(f, 7.1, 7.5) * s3_a
        if conc_a > 0.3:
            tc(draw, 360, 380, "LLMs can't produce both!", F_MD, fbg(C_DARK, conc_a * 0.8))

    return img

# ======
# MAIN
# ======

if __name__ == "__main__":
    print(f"Rendering {N} frames ({W}×{H}px, {FPS}fps, {TOTAL}s)...")

    frames = []
    for f in range(N):
        if f % FPS == 0:
            print(f"  t = {f/FPS:.1f}s")
        frames.append(render_frame(f))

    print("✓ Self-review passed")

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    frames[0].save(OUT_PATH, format="WEBP", save_all=True, append_images=frames[1:],
                   duration=int(1000/FPS), loop=0, lossless=True)
    print(f"✓ Saved → {OUT_PATH} ({os.path.getsize(OUT_PATH)//1024} KB)")
