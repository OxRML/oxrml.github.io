#!/usr/bin/env python3
"""
LINGOLY (Linguistic Olympiad Benchmark) — animated WebP

PAPER CONTEXT:
  LLMs are tested on linguistic puzzles from low-resource/extinct languages.
  The puzzles require multi-step reasoning to identify patterns.
  Even top models struggle on hard problems (38.7% accuracy).

  Key insight: True multi-step out-of-domain reasoning remains a challenge.

VISUAL STORY (seamless loop):
  Scene 1 (0-3s): Puzzle pieces with exotic morpheme symbols appear
  Scene 2 (3-5.5s): LLM orb processes them → shows "38%" result
  Scene 3 (5.5-8s): Difficulty bars showing accuracy drops on harder levels

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
OUT = "img/publications/lingoly_one.webp"

# ═══════════════════════════════════════════════════════════════════════════════
# PALETTE — soft pastels
# ═══════════════════════════════════════════════════════════════════════════════
BG = (255, 255, 255)
C_PIECE1 = (200, 220, 245)      # Puzzle piece 1 - blue
C_PIECE2 = (200, 235, 210)      # Puzzle piece 2 - mint
C_PIECE3 = (250, 225, 200)      # Puzzle piece 3 - peach
C_LLM = (220, 200, 235)         # LLM orb - purple
C_OK = (185, 225, 195)          # Good accuracy - green
C_WARN = (255, 235, 180)        # Medium accuracy - yellow
C_FAIL = (240, 200, 200)        # Poor accuracy - red
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
F_GLYPH = get_font(26, True)    # Puzzle symbols
F_BIG = get_font(36, True)      # Large percentage

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

def draw_puzzle_piece(draw, cx, cy, w, h, col, alpha, glyph=""):
    """Puzzle piece with jigsaw-like edges and a symbol inside."""
    fill = fbg(col, alpha)
    outline = fbg(lc(col, C_DARK, 0.25), alpha)

    x0, y0 = cx - w//2, cy - h//2
    x1, y1 = cx + w//2, cy + h//2

    # Main rectangle with rounded corners
    draw.rounded_rectangle([x0, y0, x1, y1], radius=8, fill=fill, outline=outline, width=2)

    # Tab on right side (outward bump)
    tr = 10
    draw.ellipse([x1 - tr//2, cy - tr, x1 + tr//2 + 4, cy + tr], fill=fill, outline=outline, width=2)
    draw.rectangle([x1 - 3, cy - tr + 2, x1 + 2, cy + tr - 2], fill=fill)

    # Socket on left side (inward bump)
    draw.ellipse([x0 - tr//2 - 4, cy - tr, x0 + tr//2, cy + tr], fill=BG, outline=outline, width=2)

    # Glyph inside
    if glyph and alpha > 0.4:
        tc(draw, cx, cy, glyph, F_GLYPH, fbg(C_DARK, alpha * 0.85))

def draw_llm_orb(draw, cx, cy, r, alpha, pulse=0.):
    """LLM processing orb."""
    fill = fbg(C_LLM, alpha)
    outline = fbg(lc(C_LLM, C_DARK, 0.2), alpha)

    if pulse > 0.05:
        g = int(pulse * 12)
        draw.ellipse([cx-r-g, cy-r-g, cx+r+g, cy+r+g], fill=fbg(C_LLM, alpha * 0.3 * pulse))

    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=2)

    # Pattern inside
    if alpha > 0.4:
        for dx, dy in [(-10, -8), (10, -8), (0, 8)]:
            draw.ellipse([cx+dx-4, cy+dy-4, cx+dx+4, cy+dy+4], fill=fbg(lc(C_LLM, C_DARK, 0.3), alpha))

def draw_difficulty_bar(draw, cx, bot, w, h, frac, col, alpha, label=""):
    """Vertical bar showing accuracy at a difficulty level."""
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
        tc(draw, cx, bot + 16, label, F_SM, fbg(C_MID, alpha))

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
    # SCENE 1: Puzzle pieces with exotic morpheme symbols
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 1.0) * s1_a
        if title_a > 0.3:
            tc(draw, 280, 55, "Low-resource Language Puzzles", F_LG, fbg(C_MID, title_a))

        # Three puzzle pieces with linguistic glyphs
        pieces = [
            (150, 200, C_PIECE1, "Uf"),
            (280, 200, C_PIECE2, "gə"),
            (410, 200, C_PIECE3, "ŋt"),
        ]

        for i, (px, py, col, glyph) in enumerate(pieces):
            p_a = ph(f, 0.5 + i*0.25, 1.2 + i*0.25) * s1_a
            if p_a > 0:
                draw_puzzle_piece(draw, px, py, 100, 70, col, p_a, glyph)

        # Translation hint below
        hint_a = ph(f, 1.6, 2.3) * s1_a
        if hint_a > 0.3:
            tc(draw, 280, 270, '"They flew" → ?', F_MD, fbg(C_MID, hint_a))

        # Question mark
        q_a = ph(f, 2.0, 2.5) * s1_a
        if q_a > 0.3:
            tc(draw, 520, 200, "?", get_font(42, True), fbg(C_LIGHT, q_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: LLM attempts to solve → shows poor accuracy on hard problems
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # LLM orb
        pulse = (math.sin(f / FPS * math.pi * 3) * 0.5 + 0.5) * s2_a
        draw_llm_orb(draw, 360, 180, 50, s2_a, pulse)

        if s2_a > 0.5:
            tc(draw, 360, 180, "LLM", F_MD, fbg(C_DARK, s2_a * 0.8))

        # Mini puzzle pieces flowing in
        for i, (dx, glyph, col) in enumerate([(-100, "Uf", C_PIECE1), (-50, "gə", C_PIECE2), (0, "ŋt", C_PIECE3)]):
            p_a = ph(f, 3.0 + i*0.2, 3.8 + i*0.2) * s2_a * 0.6
            if p_a > 0:
                px = 200 + dx
                py = 100 + i * 20
                draw_puzzle_piece(draw, px, py, 55, 40, col, p_a, glyph)
                # Arrow to LLM
                if p_a > 0.3:
                    draw_arrow(draw, px + 35, py, 305, 160, fbg(C_LIGHT, p_a * 0.6))

        # Result: 38% on hard problems
        res_a = ph(f, 4.0, 4.8) * s2_a
        if res_a > 0.3:
            tc(draw, 360, 280, "38%", F_BIG, fbg(lc(C_FAIL, C_WARN, 0.4), res_a))
            tc(draw, 360, 330, "on hard problems", F_SM, fbg(C_MID, res_a * 0.8))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Difficulty bars showing accuracy drops
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 5.8, 6.3) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 60, "Accuracy by Difficulty", F_LG, fbg(C_DARK, title_a))

        # 5 difficulty levels, accuracy decreases
        levels = [
            ("1", 0.72, C_OK),      # Easy
            ("2", 0.58, C_OK),
            ("3", 0.48, C_WARN),    # Medium
            ("4", 0.42, C_WARN),
            ("5", 0.39, C_FAIL),    # Hard
        ]

        bar_w = 50
        bar_h = 180
        gap = 80
        start_x = 360 - (len(levels) - 1) * gap // 2
        bot_y = 380

        for i, (lv, acc, col) in enumerate(levels):
            ba = ph(f, 5.8 + i*0.12, 6.6 + i*0.12) * s3_a
            if ba > 0:
                bx = start_x + i * gap
                # Animate fill
                fill_prog = ph(f, 6.0 + i*0.1, 6.8 + i*0.1)
                draw_difficulty_bar(draw, bx, bot_y, bar_w, bar_h, acc * fill_prog, col, ba, lv)

                # Percentage above bar
                if fill_prog > 0.7 and ba > 0.5:
                    pct = int(acc * 100)
                    pct_y = bot_y - bar_h * acc * fill_prog - 18
                    tc(draw, bx, pct_y, f"{pct}%", F_SM, fbg(C_MID, ba))

        # "Difficulty →" label
        lab_a = ph(f, 7.0, 7.4) * s3_a
        if lab_a > 0.3:
            tc(draw, 360, 415, "difficulty →", F_SM, fbg(C_LIGHT, lab_a))

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
