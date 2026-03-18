#publications_webp/src/generate_eval_llm_judge.py

"""
Paper Context:
LLM judges evaluate multimodal content across 12 languages and multiple task types.
The paper shows judge performance is shaped by composite interactions between task, language, and model behavior rather than separable factors.

Visual Story:
Scene 1 (0.5-4.0s): A balance scale compares two multimodal responses with the judge orb at the pivot.
Scene 2 (4.5-8.0s): Twelve language bubbles orbit the judge and vary their connection strengths.
Scene 3 (8.5-10.0s): Task bars rise to different heights to show non-decomposable performance.

Frame and Scene timing Calculations:
Canvas: 720x450.
Frame calculation: FPS = 20, TOTAL = 10.0, N = int(FPS * TOTAL) = 200.
Scene timing note: Scene 3 is configured through 12.0s in code, but the 10.0s loop renders the 8.5-10.0s segment before reset.
"""

import math, os
from PIL import Image, ImageDraw, ImageFont

# ======
# Canvas & timing
# ======
W, H    = 720, 450     # canvas size (px)
FPS     = 20           # frames per second — smoother animation
TOTAL   = 10.0         # total animation duration (seconds)
N       = int(FPS * TOTAL)
OUT_PATH = os.path.join(os.environ.get("WEBP_OUT_DIR", "img/publications"), "eval_llm_judge.webp")

# ======
# Pastel palette
# ======
BG          = (255, 255, 255)
P_BLUE      = (190, 215, 240)
P_GREEN     = (185, 230, 200)
P_YELLOW    = (255, 238, 180)
P_PURPLE    = (215, 195, 235)
P_ORANGE    = (255, 218, 185)
P_PINK      = (240, 200, 215)
P_TEAL      = (185, 228, 220)
P_RED       = (240, 192, 192)
P_LIME      = (210, 235, 180)
TEXT_DARK   = (55,  55,  75)
TEXT_MID    = (115, 115, 140)
TEXT_LIGHT  = (175, 175, 195)

# ======
# Font
# ======
FONT_PATHS_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",        # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",           # macOS
    "/Library/Fonts/Arial.ttf",                               # macOS alt
    "C:/Windows/Fonts/arial.ttf",                             # Windows
]
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   # Linux
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",      # macOS
    "/Library/Fonts/Arial Bold.ttf",                          # macOS alt
    "C:/Windows/Fonts/arialbd.ttf",                           # Windows
]

def get_font(size, bold=False):
    paths = FONT_PATHS_BOLD if bold else FONT_PATHS_REG
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    # Fallback with explicit size for newer Pillow
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

# ======
# Math
# ======
def smooth(t):
    """Smoothstep ease-in/out, clamped [0,1]."""
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def lc(c1, c2, t):
    """Blend two RGB tuples by t ∈ [0,1]."""
    return tuple(max(0, min(255, int(lerp(a, b, t)))) for a, b in zip(c1, c2))

def scene_alpha(fs, s0, s1, fade=0.35):
    """
    Alpha [0,1] for a scene active [s0, s1] with smooth fade-in/out of `fade` s.
    First and last frames → 0 → seamless white loop.
    """
    if fs < s0 - fade or fs > s1 + fade:
        return 0.
    ai = smooth((fs - (s0 - fade)) / (2 * fade))
    ao = smooth(((s1 + fade) - fs) / (2 * fade))
    return max(0., min(1., ai * ao))

def sp(fs, t0, t1):
    """Smoothstep progress [0,1] from t0 → t1 seconds."""
    return smooth(max(0., min(1., (fs - t0) / max(1e-9, t1 - t0))))

# ======
# Drawing primitives
# ======
def tc(draw, x, y, text, font, color):
    """Text centred at (x, y)."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((int(x - tw / 2), int(y - th / 2)), text, font=font, fill=color)

def rr(draw, xy, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

def arrowhead(draw, x1, y1, x2, y2, color, lw=3):
    draw.line([(x1, y1), (x2, y2)], fill=color, width=lw)
    ang = math.atan2(y2 - y1, x2 - x1)
    sz  = 11
    p1  = (x2 - sz * math.cos(ang - 0.4), y2 - sz * math.sin(ang - 0.4))
    p2  = (x2 - sz * math.cos(ang + 0.4), y2 - sz * math.sin(ang + 0.4))
    draw.polygon([(x2, y2), p1, p2], fill=color)

def draw_eye(draw, cx, cy, color):
    """A simple eye icon (oval outline + pupil dot) at (cx, cy)."""
    ew, eh = 18, 11
    # upper arc
    draw.arc([cx - ew, cy - eh, cx + ew, cy + eh],
             start=205, end=335, fill=color, width=2)
    # lower arc
    draw.arc([cx - ew, cy - eh, cx + ew, cy + eh],
             start=25, end=155, fill=color, width=2)
    # pupil
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=color)

# ======
# Scene 1: The Scale
# ======
# Two image cards hang from a balance beam; judge orb sits at the pivot.
# ======
# ======
# The beam slowly tilts left — left card rises (winner), right falls (loser).
# ======
# ======
# A ✓ appears over the winning card.
#
# Key coordinates to edit
# ======
# ======
# pivot_y — height of beam pivot
# ======
# ======
# ======
# ======
# beam_arm — half-length of beam (controls how wide the scale is)
# ======
# ======
# ======
# ======
# string_h — length of string from beam end to card top
# ======
# ======
# ======
# ======
# cw, ch — card width and height
# ======
# ======
# ======
# ======
# tilt deg — maximum tilt angle (line: math.radians(...))
# ======
# ======
def draw_scene1(draw, fs):
    a = scene_alpha(fs, 0.5, 4.0, fade=0.35)
    if a < 0.001:
        return

    cx, pivot_y = W // 2, H // 2 - 30       # beam pivot: (360, 195)
    beam_arm    = 232                         # half-beam length (px)
    string_h    = 62                          # string length (px)
    cw, ch      = 138, 108                    # card dimensions (px)

    # Tilt: starts level, tips left (left card goes UP = lower py) by 14°
    # Change degrees in math.radians() to adjust tilt amount
    tilt_t = sp(fs, 2.0, 3.5)
    tilt   = math.radians(14 * tilt_t)

    # Current beam endpoints (changes as tilt animates)
    lbx = cx - beam_arm * math.cos(tilt)
    lby = pivot_y - beam_arm * math.sin(tilt)   # left end moves UP
    rbx = cx + beam_arm * math.cos(tilt)
    rby = pivot_y + beam_arm * math.sin(tilt)   # right end moves DOWN

    # Card centres (hang below beam ends)
    lcx = int(lbx)
    lcy = int(lby + string_h + ch // 2)
    rcx = int(rbx)
    rcy = int(rby + string_h + ch // 2)

    # ── Fulcrum triangle + base ───────────────────────────────────────────────
    ft = sp(fs, 0.55, 1.1) * a
    if ft > 0:
        # Triangle points: tip at pivot, base 44px wide, 46px tall
        draw.polygon([
            (cx, pivot_y + 5),
            (cx - 30, pivot_y + 50),
            (cx + 30, pivot_y + 50),
        ], fill=lc(BG, (205, 198, 228), ft))
        draw.rectangle([cx - 44, pivot_y + 48, cx + 44, pivot_y + 58],
                       fill=lc(BG, (205, 198, 228), ft))

    # ── Beam ─────────────────────────────────────────────────────────────────
    bt = sp(fs, 0.5, 1.0) * a
    if bt > 0:
        draw.line([(int(lbx), int(lby)), (int(rbx), int(rby))],
                  fill=lc(BG, (195, 188, 222), bt), width=6)

    # ── Judge orb at pivot ────────────────────────────────────────────────────
    jt    = sp(fs, 0.65, 1.15) * a
    orb_r = 32                                  # orb radius (px)
    if jt > 0:
        draw.ellipse([cx - orb_r, pivot_y - orb_r, cx + orb_r, pivot_y + orb_r],
                     fill=lc(BG, P_PURPLE, jt),
                     outline=lc(BG, (178, 150, 215), jt), width=3)
        draw_eye(draw, cx, pivot_y, lc(BG, TEXT_MID, jt))

    # ── Strings ───────────────────────────────────────────────────────────────
    st = sp(fs, 0.85, 1.35) * a
    if st > 0:
        for bx, by in [(lbx, lby), (rbx, rby)]:
            draw.line([(int(bx), int(by)), (int(bx), int(by + string_h))],
                      fill=lc(BG, (198, 193, 222), st), width=2)

    # ── Left card (blue — winning response) ───────────────────────────────────
    # Edit lc(BG, P_BLUE, ...) colour to change card fill
    ct = sp(fs, 0.9, 1.4) * a
    if ct > 0:
        rr(draw, [lcx - cw // 2, lcy - ch // 2, lcx + cw // 2, lcy + ch // 2],
           12, fill=lc(BG, P_BLUE, ct), outline=lc(BG, (150, 185, 220), ct), width=3)
        if ct > 0.38:
            it = smooth((ct - 0.38) / 0.55) * a
            # image panel inside card
            ix1, iy1 = lcx - 36, lcy - 40
            draw.rectangle([ix1, iy1, ix1 + 72, iy1 + 54],
                           fill=lc(BG, (208, 225, 242), it))
            draw.polygon([                             # mountain silhouette
                (ix1 + 4,  iy1 + 52), (ix1 + 22, iy1 + 20),
                (ix1 + 44, iy1 + 34), (ix1 + 68, iy1 + 52),
            ], fill=lc(BG, (172, 202, 228), it))
            draw.ellipse([ix1 + 46, iy1 + 4, ix1 + 66, iy1 + 22],  # sun
                         fill=lc(BG, P_YELLOW, it))
            for yo in [20, 30]:                        # text-stub lines
                draw.line([(lcx - 33, lcy + yo), (lcx + 33, lcy + yo)],
                          fill=lc(BG, (152, 178, 208), it), width=3)

    # ── Right card (orange — losing response) ─────────────────────────────────
    ct2 = sp(fs, 0.95, 1.45) * a
    if ct2 > 0:
        rr(draw, [rcx - cw // 2, rcy - ch // 2, rcx + cw // 2, rcy + ch // 2],
           12, fill=lc(BG, P_ORANGE, ct2), outline=lc(BG, (220, 182, 138), ct2), width=3)
        if ct2 > 0.38:
            it = smooth((ct2 - 0.38) / 0.55) * a
            ix1, iy1 = rcx - 36, rcy - 40
            draw.rectangle([ix1, iy1, ix1 + 72, iy1 + 54],
                           fill=lc(BG, (245, 228, 205), it))
            draw.polygon([
                (ix1 + 4,  iy1 + 52), (ix1 + 16, iy1 + 26),
                (ix1 + 40, iy1 + 36), (ix1 + 68, iy1 + 52),
            ], fill=lc(BG, (228, 200, 168), it))
            draw.ellipse([ix1 + 46, iy1 + 4, ix1 + 66, iy1 + 22],
                         fill=lc(BG, P_YELLOW, it))
            for yo in [20, 30]:
                draw.line([(rcx - 33, rcy + yo), (rcx + 33, rcy + yo)],
                          fill=lc(BG, (205, 175, 142), it), width=3)

    # ── ✓ verdict above the winning (left) card ───────────────────────────────
    # Appears once tilt is underway; edit sp() t0/t1 to change timing
    if fs > 2.8:
        vt = sp(fs, 2.8, 3.5) * a
        gr = 42                                    # glow halo radius (px)
        vy = lcy - ch // 2 - 18                   # vertical position above card
        draw.ellipse([lcx - gr, vy - gr, lcx + gr, vy + gr],
                     fill=lc(BG, (210, 238, 215), vt))
        # Font size 56 — change to resize the ✓ symbol
        tc(draw, lcx, vy, "\u2713", get_font(56, bold=True), lc(BG, (72, 158, 92), vt))

# ======
# Scene 2: Language Ring
# ======
# 12 language bubbles stagger in and orbit the central judge orb.
# Connector lines vary in thickness/opacity to hint at unequal performance.
#
# Key values to edit
# ======
# ======
# R — orbit radius
# ======
# ======
# ======
# ======
# br — bubble radius
# ======
# ======
# ======
# ======
# LANGS — 2-letter language codes
# ======
# ======
# ======
# ======
# STRENGTHS — relative line opacity per language (1.0 = brightest)
# ======
# ======
def draw_scene2(draw, fs):
    a = scene_alpha(fs, 4.5, 8.0, fade=0.35)
    if a < 0.001:
        return

    cx, cy = W // 2, H // 2            # centre: (360, 225)
    R       = 145                       # orbit radius (px)
    orb_r   = 34                        # judge orb radius
    br      = 24                        # language bubble radius

    LANGS = ["EN", "AR", "ZH", "FR", "DE", "IT", "JA", "KO", "PT", "RU", "ES", "CS"]
    COLORS = [
        P_BLUE, P_ORANGE, P_PINK,  P_GREEN,
        P_TEAL, P_YELLOW, P_PURPLE, P_RED,
        P_LIME, (200, 215, 238),   P_ORANGE, P_TEAL,
    ]
    # Line opacity per language — reflects relative performance disparity
    # 1.0 = high-resource, well-performing; 0.6 = lower-resource
    # Edit these numbers (0.55–1.0) to adjust visual contrast
    STRENGTHS = [1.0, 0.78, 0.90, 0.86, 0.84, 0.88,
                 0.70, 0.62, 0.87, 0.82, 0.89, 0.76]

    # ── Judge orb ─────────────────────────────────────────────────────────────
    draw.ellipse([cx - orb_r, cy - orb_r, cx + orb_r, cy + orb_r],
                 fill=lc(BG, P_PURPLE, a),
                 outline=lc(BG, (178, 150, 215), a), width=3)
    draw_eye(draw, cx, cy, lc(BG, TEXT_MID, a))

    # ── Language bubbles ─────────────────────────────────────────────────────
    t0 = 4.5
    n  = len(LANGS)
    for i, (lang, col, strength) in enumerate(zip(LANGS, COLORS, STRENGTHS)):
        # Stagger each bubble's entry over 0.9 s total
        delay = i / n * 0.9
        lt    = smooth(max(0., min(1., (fs - (t0 + delay)) / 0.45)))
        if lt <= 0:
            continue

        ang = 2 * math.pi * i / n - math.pi / 2    # top = first bubble
        # gentle breathing oscillation after fully in
        osc = 1 + 0.018 * math.sin(fs * 1.1 + i * 0.5) * lt
        r   = lerp(R + 18, R * osc, lt)

        bx = cx + r * math.cos(ang)
        by = cy + r * math.sin(ang)

        # Connector line — width and alpha encode relative performance
        if lt > 0.5:
            la  = smooth((lt - 0.5) / 0.4) * a * strength
            dx, dy = cx - bx, cy - by
            dist   = math.hypot(dx, dy)
            sx  = bx + dx * (br + 2) / dist
            sy  = by + dy * (br + 2) / dist
            ex  = bx + dx * (dist - orb_r - 3) / dist
            ey  = by + dy * (dist - orb_r - 3) / dist
            lw  = 2 if strength >= 0.85 else 1    # thicker = stronger
            draw.line([(int(sx), int(sy)), (int(ex), int(ey))],
                      fill=lc(BG, (188, 185, 215), la), width=lw)

        # Bubble + label
        draw.ellipse([bx - br, by - br, bx + br, by + br],
                     fill=lc(BG, col, lt * a),
                     outline=lc(BG, (175, 175, 200), lt * a))
        # Font size 20 — change to resize language codes
        tc(draw, int(bx), int(by), lang,
           get_font(20, bold=True), lc(BG, TEXT_DARK, lt * a))

# ======
# Scene 3: Task Bars
# ======
# Three bars at dramatically different heights show task-dependent performance.
# Scatter dots on each bar show cross-language variance within each task.
# The ≠ symbol appears last as the key takeaway.
#
# Key values to edit
# ======
# ======
# baseline — y-coordinate of bar bottom
# ======
# ======
# ======
# ======
# chart_h — max bar height (tallest bar at acc=1.0)
# ======
# ======
# ======
# ======
# bar_w — bar width (px)
# ======
# ======
# ======
# ======
# gap — space between bars (px)
# ======
# ======
# ======
# ======
# ACCS — overall accuracy per task (controls bar height)
# ======
# ======
# ======
# ======
# BCOLORS — bar fill colours
# ======
# ======
def draw_scene3(draw, fs):
    a = scene_alpha(fs, 8.5, 12.0, fade=0.35)
    if a < 0.001:
        return

    t0       = 8.5
    baseline = H - 78        # bar bottom y-coordinate: 372
    chart_h  = 258            # max bar height — change to rescale bars
    bar_w    = 112            # bar width (px)
    gap      = 62             # gap between bars (px)

    # Three bar x-centres, evenly distributed
    total_w = 3 * bar_w + 2 * gap     # = 460 px
    left_x  = (W - total_w) // 2      # = 130
    bcs = [
        left_x + bar_w // 2,                       # ~186
        left_x + bar_w + gap + bar_w // 2,         # ~360
        left_x + 2 * (bar_w + gap) + bar_w // 2,  # ~534
    ]

    # Task labels, accuracy values, colours
    # Edit ACCS to change bar heights; TASKS for labels; BCOLORS for fill
    TASKS   = ["HAL", "RSN", "SAF"]                   # ← 3-letter abbreviations
    ACCS    = [0.952, 0.512, 0.626]                   # ← overall accuracy per task
    BCOLORS = [P_GREEN,   P_RED,    P_YELLOW]
    OCOLORS = [(148, 205, 165), (210, 160, 160), (225, 200, 130)]  # outlines

    # Per-task language-level values (for scatter dots)
    VARIANCE = [
        [0.983, 0.901, 0.952, 0.971, 0.963, 0.956],  # HAL row
        [0.541, 0.491, 0.512, 0.493, 0.467, 0.521],  # RSN row
        [0.635, 0.606, 0.626, 0.646, 0.630, 0.595],  # SAF row
    ]

    # Baseline tick line
    base_t = sp(fs, t0, t0 + 0.4) * a
    if base_t > 0:
        draw.line([(left_x - 12, baseline), (left_x + total_w + 12, baseline)],
                  fill=lc(BG, TEXT_LIGHT, base_t), width=2)

    for i, (bc, task, acc, col, ocol) in enumerate(
            zip(bcs, TASKS, ACCS, BCOLORS, OCOLORS)):
        bar_h  = int(acc * chart_h)
        delay  = 0.2 + i * 0.38          # stagger bar emergence (seconds)
        bt     = sp(fs, t0 + delay, t0 + delay + 1.1)
        if bt <= 0:
            continue

        bar_top = baseline - int(bar_h * bt)
        bx1     = bc - bar_w // 2
        bx2     = bc + bar_w // 2

        # Bar body
        rr(draw, [bx1, bar_top, bx2, baseline], 8,
           fill=lc(BG, col, bt * a),
           outline=lc(BG, ocol, bt * a), width=2)

        # Accuracy % above bar — font 26; edit to resize
        if bt > 0.68:
            pt = smooth((bt - 0.68) / 0.3) * a
            tc(draw, bc, bar_top - 22,
               f"{acc * 100:.0f}%", get_font(26, bold=True),
               lc(BG, TEXT_DARK, pt))

        # Task label below bar — font 22; edit to resize
        tc(draw, bc, baseline + 24, task,
           get_font(22), lc(BG, TEXT_MID, bt * a))

        # Scatter dots on bar face (cross-language variance per task)
        if bt > 0.82:
            vt = smooth((bt - 0.82) / 0.17) * a
            vals   = VARIANCE[i]
            n_dots = len(vals)
            for j, dv in enumerate(vals):
                dot_y = baseline - int(dv * chart_h)
                dot_x = bx1 + (j + 1) * bar_w // (n_dots + 1)
                draw.ellipse([dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4],
                             fill=lc(BG, ocol, vt))

    # ≠ symbol — the paper's core message; font 38; edit to resize
    # Appears last, centred below bars
    if fs > t0 + 2.25:
        nt = sp(fs, t0 + 2.25, t0 + 2.85) * a
        tc(draw, W // 2, H - 38, "\u2260",        # ≠ Unicode  (y raised to clear margin)
           get_font(38, bold=True), lc(BG, TEXT_MID, nt))

# ======
# Frame builder
# ======
def build_frame(idx):
    fs   = idx / FPS
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    draw_scene1(draw, fs)
    draw_scene2(draw, fs)
    draw_scene3(draw, fs)
    return img

# ======
# Self-review: edge-clip check
# ======
def check_frame(img, idx):
    MARGIN = 6
    W_, H_  = img.size
    for y in range(H_):
        for x in range(W_):
            if x < MARGIN or x >= W_ - MARGIN or y < MARGIN or y >= H_ - MARGIN:
                px   = img.getpixel((x, y))
                diff = abs(px[0] - 255) + abs(px[1] - 255) + abs(px[2] - 255)
                if diff > 18:
                    print(f"  ⚠ Frame {idx}: edge @ ({x},{y}) = {px}")
                    return False
    return True

# ======
# Main
# ======
if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    print(f"Rendering {N} frames  ({W}×{H}px, {FPS}fps, {TOTAL}s)…")
    frames, warns = [], 0

    for i in range(N):
        if i % FPS == 0:
            print(f"  t = {i / FPS:.1f}s  ({i}/{N})")
        frame = build_frame(i)
        if i % 6 == 0:
            if not check_frame(frame, i):
                warns += 1
        frames.append(frame)

    if warns:
        print(f"\n⚠  {warns} clipping warnings — check coordinates above")
    else:
        print("\n✓  Self-review passed — no edge clipping detected")

    dur_ms = int(1000 / FPS)    # ms per frame
    frames[0].save(
        OUT_PATH,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=dur_ms,
        loop=0,
        lossless=True,   # crisp text rendering
    )
    print(f"✓  WebP saved → {OUT_PATH}  ({len(frames)} frames, {dur_ms}ms/frame)")
