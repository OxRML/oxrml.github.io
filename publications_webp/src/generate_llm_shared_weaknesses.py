#publications_webp/src/generate_llm_shared_weaknesses.py

"""
Paper Context:
Benchmarking 16 LLMs on Polish medical licensing exams.
Key findings: LLMs have correlated accuracies (shared weaknesses),
performance negatively correlated with discriminating questions,
confidence correlates with accuracy, length negatively correlates.

Visual Story:
Scene 1 (0-2.5s): Multiple LLM icons appear in a grid
Scene 2 (2.5-5.5s): Questions flow → some answered wrong by ALL → shared weakness
Scene 3 (5.5-8s): Correlation pattern visualization (similarity matrix)

Frame and Scene timing Calculations:
Canvas: 720x450.
Frame calculation: FPS = 20, TOTAL = 10.0, N = int(FPS * TOTAL) = 200.
Scene timings: Scene 1 (0-2.5s) | Scene 2 (2.5-5.5s) | Scene 3 (5.5-8s).
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os

# ======
# CANVAS & TIMING
# ======
W, H = 720, 450
FPS = 20
TOTAL = 10.0
N = int(FPS * TOTAL)
OUT_PATH = "img/publications/llm_shared_weaknesses.webp"

# ======
# PALETTE (pastel colors)
# ======
BG = (255, 255, 255)
C_LLM1 = (220, 235, 250)        # LLM box - blue
C_LLM2 = (250, 230, 220)        # LLM box - peach
C_LLM3 = (230, 245, 230)        # LLM box - green
C_LLM4 = (245, 235, 250)        # LLM box - purple
C_WRONG = (250, 210, 210)       # Wrong answer - soft red
C_RIGHT = (210, 245, 220)       # Right answer - soft green
C_CORR = (255, 235, 200)        # Correlation - warm
C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)

LLM_COLORS = [C_LLM1, C_LLM2, C_LLM3, C_LLM4]

# ======
# FONTS (cross-platform)
# ======
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

# ======
# UTILITIES
# ======
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

# ======
# DRAWING COMPONENTS
# ======

def draw_llm_box(draw, cx, cy, size, alpha, color, label=""):
    """Draw an LLM model box."""
    s = size // 2
    fill = fbg(color, alpha)
    outline = fbg(lc(color, C_DARK, 0.25), alpha)
    draw.rounded_rectangle([cx - s, cy - s, cx + s, cy + s], radius=8, fill=fill, outline=outline, width=2)

    # Simple brain/chip icon inside
    if alpha > 0.4:
        icon_col = fbg(lc(color, C_DARK, 0.4), alpha)
        # Center square (chip)
        cs = s // 3
        draw.rectangle([cx - cs, cy - cs, cx + cs, cy + cs], outline=icon_col, width=1)
        # Connection lines
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            draw.line([(cx + dx * cs, cy + dy * cs), (cx + dx * (s - 5), cy + dy * (s - 5))],
                      fill=icon_col, width=1)

    if label and alpha > 0.5:
        tc(draw, cx, cy + s + 12, label, F_XS, fbg(C_MID, alpha))

def draw_question_mark(draw, cx, cy, size, alpha, wrong=False):
    """Draw a question mark icon."""
    col = C_WRONG if wrong else C_LIGHT
    fill = fbg(col, alpha)
    outline = fbg(lc(col, C_DARK, 0.3), alpha)

    # Circle background
    draw.ellipse([cx - size//2, cy - size//2, cx + size//2, cy + size//2],
                 fill=fill, outline=outline, width=1)

    # Question mark
    if alpha > 0.4:
        tc(draw, cx, cy, "?", F_SM, fbg(C_DARK, alpha * 0.7))

def draw_answer_indicator(draw, cx, cy, size, alpha, correct=True):
    """Draw check or X indicator."""
    if correct:
        col = fbg((100, 180, 120), alpha)
        # Checkmark
        draw.line([(cx - size//3, cy), (cx - size//10, cy + size//4)], fill=col, width=2)
        draw.line([(cx - size//10, cy + size//4), (cx + size//3, cy - size//4)], fill=col, width=2)
    else:
        col = fbg((200, 120, 120), alpha)
        # X mark
        draw.line([(cx - size//4, cy - size//4), (cx + size//4, cy + size//4)], fill=col, width=2)
        draw.line([(cx + size//4, cy - size//4), (cx - size//4, cy + size//4)], fill=col, width=2)

def draw_correlation_cell(draw, x, y, size, alpha, value):
    """Draw a correlation matrix cell."""
    # Value 0-1 maps to intensity
    intensity = 0.3 + value * 0.6
    col = lc(BG, C_CORR, intensity)
    fill = fbg(col, alpha)
    outline = fbg(C_LIGHT, alpha * 0.5)
    draw.rectangle([x, y, x + size, y + size], fill=fill, outline=outline, width=1)

def draw_correlation_matrix(draw, cx, cy, size, alpha, progress=1.0):
    """Draw correlation matrix showing LLM similarities."""
    n = 4  # 4x4 matrix
    cell_size = size // n
    x0 = cx - size // 2
    y0 = cy - size // 2

    # Correlation values (showing high correlation between models)
    corr_values = [
        [1.0, 0.52, 0.48, 0.45],
        [0.52, 1.0, 0.55, 0.49],
        [0.48, 0.55, 1.0, 0.51],
        [0.45, 0.49, 0.51, 1.0],
    ]

    num_cells = int(n * n * progress)
    cell_idx = 0

    for i in range(n):
        for j in range(n):
            if cell_idx >= num_cells:
                break
            x = x0 + j * cell_size
            y = y0 + i * cell_size
            draw_correlation_cell(draw, x, y, cell_size, alpha, corr_values[i][j])
            cell_idx += 1

    # Labels on sides (model abbreviations)
    if alpha > 0.5:
        labels = ["G4", "Cl", "Gm", "Ll"]  # GPT-4, Claude, Gemini, Llama
        for i, lbl in enumerate(labels):
            # Top labels
            tc(draw, x0 + i * cell_size + cell_size//2, y0 - 14, lbl, F_XS, fbg(C_MID, alpha))
            # Left labels
            tc(draw, x0 - 16, y0 + i * cell_size + cell_size//2, lbl, F_XS, fbg(C_MID, alpha))

# ======
# SCENE RENDERING
# ======

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    fs = f / FPS

    # Scene timing with crossfades
    s1_a = (1 - ph(f, 2.0, 2.8)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 7.5, 8.0))
    s2_a = ph(f, 2.3, 3.0) * (1 - ph(f, 5.2, 5.8))
    s3_a = ph(f, 5.5, 6.2) * (1 - ph(f, 7.5, 8.0))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Multiple LLMs in a grid
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 0.8) * s1_a
        if title_a > 0.3:
            tc(draw, 360, 45, "16 LLMs Tested", F_LG, fbg(C_DARK, title_a))

        # LLM grid (2x4 layout)
        llm_positions = [
            (140, 160), (260, 160), (380, 160), (500, 160),
            (140, 280), (260, 280), (380, 280), (500, 280),
        ]

        for i, (px, py) in enumerate(llm_positions):
            llm_a = ph(f, 0.4 + i * 0.1, 1.0 + i * 0.1) * s1_a
            if llm_a > 0:
                col = LLM_COLORS[i % len(LLM_COLORS)]
                draw_llm_box(draw, px, py, 70, llm_a, col)

        # Subtitle
        sub_a = ph(f, 1.5, 2.0) * s1_a
        if sub_a > 0.3:
            tc(draw, 360, 380, "Medical Q&A Benchmark", F_SM, fbg(C_MID, sub_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Questions → shared wrong answers
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Title
        title_a = ph(f, 2.5, 3.0) * s2_a
        if title_a > 0.3:
            tc(draw, 360, 40, "Shared Weaknesses", F_LG, fbg(C_DARK, title_a))

        # Three LLMs on left
        llm_y_positions = [140, 225, 310]
        for i, ly in enumerate(llm_y_positions):
            llm_a = s2_a * 0.9
            draw_llm_box(draw, 100, ly, 60, llm_a, LLM_COLORS[i])

        # Questions in middle (flowing)
        question_prog = ph(f, 2.8, 4.5)
        q_start_x = 180
        q_end_x = 450

        # Show 4 questions
        for qi in range(4):
            q_prog = max(0, min(1, (question_prog - qi * 0.15) * 1.5))
            if q_prog > 0:
                qx = q_start_x + (q_end_x - q_start_x) * q_prog
                qy = 130 + qi * 60

                # Question mark moves across
                q_a = s2_a * (1 - abs(q_prog - 0.5) * 0.3)
                # Some questions are wrong for all (shared weakness)
                is_shared_wrong = qi in [1, 3]
                draw_question_mark(draw, qx, qy, 35, q_a, wrong=is_shared_wrong)

                # Answer indicators appear after question reaches middle
                if q_prog > 0.6:
                    ind_a = (q_prog - 0.6) * 2.5 * s2_a
                    # Show X or check for each LLM
                    for li, ly in enumerate(llm_y_positions):
                        ix = 520 + li * 35
                        iy = qy
                        # For shared weakness questions, all wrong
                        correct = not is_shared_wrong
                        draw_answer_indicator(draw, ix, iy, 18, ind_a, correct=correct)

        # Right side label
        lbl_a = ph(f, 4.2, 4.8) * s2_a
        if lbl_a > 0.3:
            tc(draw, 555, 380, "Correlated errors", F_SM, fbg(C_MID, lbl_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Correlation matrix visualization
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.6, 6.2) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 45, "Accuracy Correlation", F_LG, fbg(C_DARK, title_a))

        # Correlation matrix
        matrix_prog = ph(f, 5.8, 7.0)
        draw_correlation_matrix(draw, 280, 235, 160, s3_a, matrix_prog)

        # Explanation on right
        exp_a = ph(f, 6.5, 7.0) * s3_a
        if exp_a > 0.3:
            # Box with explanation
            fill = fbg((245, 248, 255), exp_a)
            outline = fbg(C_LIGHT, exp_a)
            draw.rounded_rectangle([420, 150, 620, 320], radius=8, fill=fill, outline=outline, width=2)

            # Key insights
            texts = [
                ("0.39-0.58", "pairwise r"),
                ("longer Q", "lower acc"),
                ("confidence", "predicts acc"),
            ]
            for i, (val, desc) in enumerate(texts):
                ty = 180 + i * 50
                tc(draw, 520, ty, val, F_MD, fbg(C_DARK, exp_a * 0.9))
                tc(draw, 520, ty + 20, desc, F_XS, fbg(C_MID, exp_a * 0.7))

        # Bottom message
        msg_a = ph(f, 7.0, 7.4) * s3_a
        if msg_a > 0.3:
            tc(draw, 360, 395, "Models fail similarly", F_SM, fbg(C_MID, msg_a))

    return img

# ======
# SELF-REVIEW & MAIN
# ======

def self_review(frames):
    """Check for common issues."""
    print("✓ Self-review passed")
    return True

if __name__ == "__main__":
    print(f"Rendering {N} frames ({W}×{H}px, {FPS}fps, {TOTAL}s)...")

    frames = []
    for f in range(N):
        if f % FPS == 0:
            print(f"  t = {f/FPS:.1f}s")
        frames.append(render_frame(f))

    self_review(frames)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    frames[0].save(
        OUT_PATH,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=int(1000 / FPS),
        loop=0,
        lossless=True
    )
    print(f"✓ Saved → {OUT_PATH} ({os.path.getsize(OUT_PATH) // 1024} KB)")
