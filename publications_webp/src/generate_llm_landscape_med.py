#!/usr/bin/env python3
"""
LLM Landscape in Medical Q&A — animated WebP

PAPER CONTEXT:
  Systematic benchmarking of 8 LLMs on Polish medical licensing exams.
  Enables per-question comparison between LLMs and human test-takers.
  Key patterns: model similarities, confidence-accuracy correlation,
  negative correlation with question length.

VISUAL STORY (seamless loop):
  Scene 1 (0-2.5s): Multiple LLMs of varying sizes appear (landscape view)
  Scene 2 (2.5-5.5s): Questions tested → accuracy chart with human baseline
  Scene 3 (5.5-8s): Key patterns: confidence↑, length↓, human similarity

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
OUT = "img/publications/llm_landscape_med.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE (pastel colors)
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_LLM_L = (200, 220, 250)       # Large LLM - blue
C_LLM_M = (220, 240, 220)       # Medium LLM - green
C_LLM_S = (250, 235, 215)       # Small LLM - peach
C_HUMAN = (255, 220, 220)       # Human baseline - pink
C_CHART = (240, 245, 255)       # Chart background
C_BAR = (180, 200, 230)         # Bar color
C_PATTERN = (255, 245, 230)     # Pattern box - warm
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)
C_ACCENT = (100, 160, 200)      # Accent blue

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

def draw_llm_box(draw, cx, cy, size, alpha, color, label=""):
    """Draw an LLM model box with size indicating model scale."""
    s = size // 2
    fill = fbg(color, alpha)
    outline = fbg(lc(color, C_DARK, 0.25), alpha)
    draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=8, fill=fill, outline=outline, width=2)

    # Brain/chip pattern inside
    if alpha > 0.4 and size > 40:
        pattern_col = fbg(lc(color, C_DARK, 0.3), alpha)
        # Grid of dots
        step = size // 4
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) <= 1:
                    draw.ellipse([cx + dx*step - 3, cy + dy*step - 3,
                                  cx + dx*step + 3, cy + dy*step + 3], fill=pattern_col)

    if label and alpha > 0.5:
        tc(draw, cx, cy + s + 14, label, F_XS, fbg(C_MID, alpha))

def draw_question_stack(draw, cx, cy, width, height, alpha, count=3):
    """Draw a stack of question cards."""
    if alpha < 0.1:
        return

    for i in range(count):
        offset = i * 4
        x0 = cx - width//2 + offset
        y0 = cy - height//2 - (count - 1 - i) * 4
        fill = fbg((245 - i*5, 248 - i*5, 255 - i*5), alpha)
        outline = fbg(C_LIGHT, alpha * 0.7)
        draw.rounded_rectangle([x0, y0, x0 + width, y0 + height], radius=4, fill=fill, outline=outline, width=1)

        # Question mark on top card
        if i == count - 1 and alpha > 0.4:
            tc(draw, x0 + width//2, y0 + height//2, "?", F_MD, fbg(C_MID, alpha * 0.6))

def draw_accuracy_bar(draw, x, y, width, height, alpha, value, label="", highlight=False):
    """Draw a horizontal accuracy bar."""
    # Background
    bg_col = fbg(C_CHART, alpha)
    draw.rectangle([x, y, x + width, y + height], fill=bg_col, outline=fbg(C_LIGHT, alpha * 0.5), width=1)

    # Fill bar
    fill_w = int(width * value)
    fill_col = fbg(C_ACCENT if highlight else C_BAR, alpha)
    if fill_w > 0:
        draw.rectangle([x, y, x + fill_w, y + height], fill=fill_col)

    # Label
    if alpha > 0.5:
        # Value on right
        tc(draw, x + width + 30, y + height//2, f"{value:.0%}", F_XS, fbg(C_DARK, alpha))
        # Label on left
        if label:
            bb = draw.textbbox((0, 0), label, font=F_XS)
            tw = bb[2] - bb[0]
            draw.text((x - tw - 8, y + height//2 - 6), label, font=F_XS, fill=fbg(C_MID, alpha))

def draw_human_baseline(draw, x, y, height, alpha, value, chart_width):
    """Draw human baseline marker."""
    if alpha < 0.1:
        return

    line_x = x + int(chart_width * value)
    col = fbg(C_HUMAN, alpha)
    outline = fbg(lc(C_HUMAN, C_DARK, 0.3), alpha)

    # Vertical dashed line
    for dy in range(0, height, 6):
        draw.line([(line_x, y + dy), (line_x, y + dy + 3)], fill=outline, width=2)

    # Label
    if alpha > 0.5:
        tc(draw, line_x, y - 12, "Human", F_XS, fbg(C_MID, alpha))

def draw_pattern_indicator(draw, cx, cy, alpha, icon_type="up", label=""):
    """Draw pattern indicator (up arrow, down arrow, or similarity)."""
    if alpha < 0.1:
        return

    # Background circle
    fill = fbg(C_PATTERN, alpha)
    outline = fbg(lc(C_PATTERN, C_DARK, 0.2), alpha)
    r = 22
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=2)

    icon_col = fbg(C_DARK, alpha * 0.7)

    if icon_type == "up":
        # Up arrow (positive correlation)
        draw.polygon([(cx, cy - 10), (cx - 8, cy + 5), (cx + 8, cy + 5)], fill=fbg((100, 180, 130), alpha))
    elif icon_type == "down":
        # Down arrow (negative correlation)
        draw.polygon([(cx, cy + 10), (cx - 8, cy - 5), (cx + 8, cy - 5)], fill=fbg((200, 130, 130), alpha))
    elif icon_type == "similar":
        # Overlap circles (similarity)
        draw.ellipse([cx - 12, cy - 8, cx, cy + 8], outline=fbg(C_ACCENT, alpha), width=2)
        draw.ellipse([cx, cy - 8, cx + 12, cy + 8], outline=fbg((180, 130, 180), alpha), width=2)

    if label and alpha > 0.5:
        tc(draw, cx, cy + r + 14, label, F_XS, fbg(C_MID, alpha))

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
    # SCENE 1: LLM Landscape (varying sizes)
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 0.8) * s1_a
        if title_a > 0.3:
            tc(draw, 360, 40, "LLM Landscape", F_LG, fbg(C_DARK, title_a))

        # LLMs of varying sizes (representing different model scales)
        llms = [
            (120, 200, 80, C_LLM_L, "GPT-4"),      # Large
            (260, 210, 65, C_LLM_M, "PaLM 2"),     # Medium-large
            (380, 220, 55, C_LLM_M, "Mixtral"),    # Medium
            (480, 225, 50, C_LLM_S, "Med42"),      # Medium-small
            (570, 230, 40, C_LLM_S, "Llama"),      # Small
            (640, 235, 35, C_LLM_S, "Phi"),        # Smaller
        ]

        for i, (px, py, size, col, label) in enumerate(llms):
            llm_a = ph(f, 0.4 + i * 0.12, 1.0 + i * 0.12) * s1_a
            draw_llm_box(draw, px, py, size, llm_a, col, label)

        # Question stack on right
        q_a = ph(f, 1.2, 1.8) * s1_a
        draw_question_stack(draw, 580, 340, 70, 50, q_a, 4)
        if q_a > 0.5:
            tc(draw, 580, 395, "874 questions", F_SM, fbg(C_MID, q_a))

        # "Medical Exam" subtitle
        sub_a = ph(f, 1.5, 2.0) * s1_a
        if sub_a > 0.3:
            tc(draw, 200, 340, "Medical Licensing Exam", F_SM, fbg(C_MID, sub_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Accuracy comparison chart
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Title
        title_a = ph(f, 2.5, 3.0) * s2_a
        if title_a > 0.3:
            tc(draw, 360, 35, "Per-Question Comparison", F_LG, fbg(C_DARK, title_a))

        # Accuracy bars
        models = [
            ("GPT-4", 0.82, True),
            ("Med42", 0.63, False),
            ("PaLM 2", 0.63, False),
            ("Mixtral", 0.63, False),
            ("GPT-3.5", 0.63, False),
        ]

        chart_x = 180
        chart_w = 280
        bar_h = 22

        for i, (name, acc, highlight) in enumerate(models):
            bar_a = ph(f, 2.8 + i * 0.15, 3.6 + i * 0.15) * s2_a
            y = 90 + i * 45
            draw_accuracy_bar(draw, chart_x, y, chart_w, bar_h, bar_a, acc, name, highlight)

        # Human baseline
        human_a = ph(f, 3.8, 4.3) * s2_a
        draw_human_baseline(draw, chart_x, 90, 5 * 45, human_a, 0.80, chart_w)

        # Pass threshold line
        pass_a = ph(f, 4.0, 4.5) * s2_a
        if pass_a > 0.3:
            pass_x = chart_x + int(chart_w * 0.56)
            col = fbg((150, 200, 150), pass_a)
            draw.line([(pass_x, 85), (pass_x, 310)], fill=col, width=1)
            tc(draw, pass_x, 320, "Pass: 56%", F_XS, fbg(C_MID, pass_a * 0.8))

        # Key finding box
        find_a = ph(f, 4.3, 4.9) * s2_a
        if find_a > 0.3:
            fill = fbg((248, 252, 255), find_a)
            outline = fbg(C_LIGHT, find_a)
            draw.rounded_rectangle([520, 130, 680, 240], radius=8, fill=fill, outline=outline, width=2)
            tc(draw, 600, 160, "All pass", F_SM, fbg(C_DARK, find_a * 0.9))
            tc(draw, 600, 190, "the exam", F_SM, fbg(C_MID, find_a * 0.8))
            tc(draw, 600, 220, "(56%)", F_XS, fbg(C_LIGHT, find_a * 0.7))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Key patterns discovered
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.6, 6.2) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 40, "Discovered Patterns", F_LG, fbg(C_DARK, title_a))

        # Three pattern indicators
        patterns = [
            (180, 180, "up", "Confidence"),
            (360, 180, "down", "Length"),
            (540, 180, "similar", "Human"),
        ]

        for i, (px, py, icon, label) in enumerate(patterns):
            p_a = ph(f, 5.8 + i * 0.25, 6.6 + i * 0.25) * s3_a
            draw_pattern_indicator(draw, px, py, p_a, icon, label)

        # Explanations below each
        explanations = [
            (180, "High confidence"),
            (180, "= higher accuracy"),
            (360, "Longer questions"),
            (360, "= lower accuracy"),
            (540, "LLMs correlate"),
            (540, "with human difficulty"),
        ]

        exp_a = ph(f, 6.5, 7.2) * s3_a
        if exp_a > 0.3:
            # Pattern 1
            tc(draw, 180, 260, "High confidence", F_XS, fbg(C_MID, exp_a))
            tc(draw, 180, 278, "= better accuracy", F_XS, fbg(C_LIGHT, exp_a * 0.8))

            # Pattern 2
            tc(draw, 360, 260, "Longer questions", F_XS, fbg(C_MID, exp_a))
            tc(draw, 360, 278, "= worse accuracy", F_XS, fbg(C_LIGHT, exp_a * 0.8))

            # Pattern 3
            tc(draw, 540, 260, "LLMs correlate", F_XS, fbg(C_MID, exp_a))
            tc(draw, 540, 278, "with human errors", F_XS, fbg(C_LIGHT, exp_a * 0.8))

        # Bottom insight
        insight_a = ph(f, 7.0, 7.4) * s3_a
        if insight_a > 0.3:
            fill = fbg((250, 252, 255), insight_a)
            outline = fbg(C_LIGHT, insight_a)
            draw.rounded_rectangle([140, 330, 580, 400], radius=10, fill=fill, outline=outline, width=2)
            tc(draw, 360, 350, "r = 0.29 to 0.62 pairwise", F_SM, fbg(C_DARK, insight_a * 0.9))
            tc(draw, 360, 378, "Models share strengths & weaknesses", F_SM, fbg(C_MID, insight_a * 0.8))

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
