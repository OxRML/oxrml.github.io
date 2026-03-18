#publications_webp/src/generate_faithful.py

"""
Paper Context:
LLM self-explanations are evaluated for whether they help an observer predict model behavior.
The paper introduces Normalized Simulatability Gain (NSG) as a faithfulness metric and shows explanations can improve prediction while still sometimes misleading observers.

Visual Story:
Scene 1 (0.0-3.35s): A patient prompts an LLM, which answers and reveals an explanation key.
Scene 2 (3.35-6.70s): A counterfactual patient ages from 60 to 30 and the model answer flips.
Scene 3 (6.70-10.05s): Observers with and without explanations are compared with NSG uplift bars.

Frame and Scene timing Calculations:
Canvas: 720x450.
Frame calculation: FPS = 20, N_PER = 67, N_SCENES = 3, N_FRAMES = N_PER * N_SCENES = 201.
Total duration: N_FRAMES / FPS = 10.05s with XFADE = 8 frame cross-fades between scenes.
"""

from PIL import Image, ImageDraw, ImageFont
import math, os

# ======
# Canvas & timing
# ======
W, H       = 720, 450
FPS        = 20
N_PER      = 67           # frames per scene
N_SCENES   = 3
N_FRAMES   = N_PER * N_SCENES   # ~200 frames ≈ 10 s
DELAY_MS   = 1000 // FPS        # 67 ms/frame
XFADE      = 8

OUT_PATH = "img/publications/faithfulNSG.webp"

# ======
# Palette
# ======
BG       = (255, 255, 255)
C_BLUE   = (173, 210, 235)
C_PURPLE = (205, 192, 232)
C_GREEN  = (165, 225, 182)
C_RED    = (235, 178, 178)
C_YELLOW = (252, 232, 168)
C_GRAY   = (188, 190, 208)
C_DARK   = ( 44,  44,  54)
C_MED    = (100, 100, 116)
C_LIGHT  = (152, 152, 168)

# ======
# Font sizes (increased for readability)
# ======
SZ_XS = 24
SZ_SM = 28
SZ_MD = 32
SZ_LG = 40
SZ_XL = 50

FONT_PATHS_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",        # Linux
    "/System/Library/Fonts/Supplemental/Arial.ttf",           # macOS
    "/Library/Fonts/Arial.ttf",                               # macOS alt
    "C:/Windows/Fonts/arial.ttf",                             # Windows
]
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   # Linux
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",      # macOS
    "/Library/Fonts/Arial Bold.ttf",                          # macOS alt
    "C:/Windows/Fonts/arialbd.ttf",                           # Windows
]

# ======
# FONT LOADING
# ======

def _font(bold, size):
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

def make_fonts():
    return {
        "xs"  : _font(False, SZ_XS),
        "sm"  : _font(False, SZ_SM),
        "md"  : _font(False, SZ_MD),
        "b_xs": _font(True,  SZ_XS),
        "b_sm": _font(True,  SZ_SM),
        "b_md": _font(True,  SZ_MD),
        "b_lg": _font(True,  SZ_LG),
        "b_xl": _font(True,  SZ_XL),
    }

# ======
# UTILITIES
# ======

def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3.0 - 2.0 * t)

def lerp(a, b, t):
    return a + (b - a) * t

def fade(color, alpha):
    a = max(0.0, min(1.0, alpha))
    return tuple(int(BG[i] + (color[i] - BG[i]) * a) for i in range(3))

def rr(draw, x0, y0, x1, y1, fill, outline=None, radius=8, width=2):
    draw.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                            fill=fill, outline=outline, width=width)

def ct(draw, text, cx, cy, font, color):
    bb = draw.textbbox((0, 0), text, font=font)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((int(cx - w / 2), int(cy - h / 2)), text, fill=color, font=font)

def arw(draw, x0, y0, x1, y1, color, width=3, head=12):
    draw.line([(x0, y0), (x1, y1)], fill=color, width=width)
    ang = math.atan2(y1 - y0, x1 - x0)
    for da in (0.40, -0.40):
        ax = x1 - head * math.cos(ang + da)
        ay = y1 - head * math.sin(ang + da)
        draw.line([(x1, y1), (int(ax), int(ay))], fill=color, width=width)

# ======
# SHARED DRAWING COMPONENTS
# ======

def draw_person(draw, cx, cy, alpha, color=None, size=1.0):
    """
    Simple person icon: circle head above a rounded-rect body.
    Total height ≈ (30 + 6 + 56) * size = 92 * size px.
    """
    if color is None:
        color = C_BLUE
    hr = int(30 * size)   # head radius
    bw = int(54 * size)   # body width
    bh = int(56 * size)   # body height
    bx0, by0 = cx - bw // 2, cy + hr + 6
    rr(draw, bx0, by0, bx0 + bw, by0 + bh,
       fade(color, alpha), fade(C_GRAY, alpha * 0.65), radius=10)
    draw.ellipse([cx - hr, cy - hr, cx + hr, cy + hr],
                 fill=fade(color, alpha), outline=fade(C_GRAY, alpha * 0.65), width=2)

def draw_llm(draw, cx, cy, w, h, alpha, pulse=0.0):
    """
    LLM box: rounded rect with internal neural-dot grid + optional glow.
    """
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2
    # Glow
    if pulse > 0.05:
        g = int(pulse * 10)
        rr(draw, x0 - g, y0 - g, x1 + g, y1 + g,
           fade(C_PURPLE, alpha * 0.28 * pulse), None, radius=18)
    rr(draw, x0, y0, x1, y1, fade(C_PURPLE, alpha), fade(C_GRAY, alpha), radius=14, width=2)
    # Neural dots (3 input, 2 hidden)
    dr = 6
    dots = [
        (cx - 52, cy - 30), (cx,      cy - 30), (cx + 52, cy - 30),
        (cx - 28, cy + 18), (cx + 28, cy + 18),
    ]
    for dx, dy in dots:
        draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr],
                     fill=fade(C_GRAY, alpha * 0.85))
    # Connection lines
    for i in range(3):
        for j in (3, 4):
            xi, yi = dots[i]; xj, yj = dots[j]
            draw.line([(xi, yi), (xj, yj)], fill=fade(C_GRAY, alpha * 0.4), width=1)

def draw_bubble(draw, cx, cy, w, h, color, alpha, tail="up"):
    """Speech bubble with tail pointing up or down."""
    x0, y0 = cx - w // 2, cy - h // 2
    x1, y1 = cx + w // 2, cy + h // 2
    rr(draw, x0, y0, x1, y1, fade(color, alpha), fade(C_GRAY, alpha * 0.6), radius=12)
    tx = cx
    if tail == "up":
        draw.polygon([(tx - 10, y0), (tx + 10, y0), (tx, y0 - 18)],
                     fill=fade(color, alpha))
    elif tail == "down":
        draw.polygon([(tx - 10, y1), (tx + 10, y1), (tx, y1 + 18)],
                     fill=fade(color, alpha))

def draw_key(draw, cx, cy, size, color, alpha):
    """Geometric key icon: ring head + shaft + two teeth."""
    c    = fade(color, alpha)
    cout = fade(C_GRAY, alpha * 0.7)
    r  = int(size * 0.38)
    hr = max(2, int(r * 0.42))
    sw = int(size * 0.18)
    sh = int(size * 0.58)
    sx0 = cx + r
    # Head
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c, outline=cout, width=2)
    draw.ellipse([cx - hr, cy - hr, cx + hr, cy + hr], fill=fade(BG, alpha))
    # Shaft
    draw.rectangle([sx0, cy - sw // 2, sx0 + sh, cy + sw // 2], fill=c)
    # Teeth
    tw, th = int(size * 0.14), int(size * 0.22)
    for tx in (sx0 + sh - tw * 3, sx0 + sh - tw):
        draw.rectangle([tx, cy + sw // 2, tx + tw - 1, cy + sw // 2 + th], fill=c)

def draw_check(draw, cx, cy, size, color, alpha):
    """Geometric checkmark (two line segments)."""
    c = fade(color, alpha)
    lw = max(3, int(size * 0.22))
    xm = cx - int(size * 0.08); ym = cy + int(size * 0.36)
    draw.line([(cx - int(size*0.44), cy - int(size*0.05)), (xm, ym)], fill=c, width=lw)
    draw.line([(xm, ym), (cx + int(size*0.50), cy - int(size*0.44))],  fill=c, width=lw)

def draw_xmark(draw, cx, cy, size, color, alpha):
    """Geometric ✗ (two diagonal lines)."""
    c = fade(color, alpha)
    lw = max(3, int(size * 0.22))
    s  = int(size * 0.42)
    draw.line([(cx - s, cy - s), (cx + s, cy + s)], fill=c, width=lw)
    draw.line([(cx + s, cy - s), (cx - s, cy + s)], fill=c, width=lw)

# ======
# ======
# SCENE 1 — Patient → LLM → Answer + Explanation key appears
# ======
# ======

def scene1(t, fonts):
    """
    Left:    person icon (age 60)
    Centre:  LLM box (pulsing)
    Right:   answer bubble "No disease ✓"
    Bottom:  explanation bubble with key + minimal text
    """
    img = Image.new("RGB", (W, H), BG)
    d   = ImageDraw.Draw(img)

    a_person = ease(min(1.0, t * 2.2))
    a_llm    = ease(max(0.0, min(1.0, t * 2.5 - 0.45)))
    a_ans    = ease(max(0.0, min(1.0, t * 2.5 - 0.9)))
    a_exp    = ease(max(0.0, t * 2.2 - 1.15))
    pulse    = (math.sin(t * math.pi * 5) * 0.5 + 0.5) * a_llm

    # ── Person (left) ─────────────────────────────────────────────────────────
    PX, PY = 118, 162
    draw_person(d, PX, PY, a_person, C_BLUE)
    ct(d, "Age  60", PX, PY + 106, fonts["b_sm"], fade(C_DARK, a_person))

    # Arrow: person → LLM
    arw(d, PX + 57, PY + 22, 268, PY + 22, fade(C_GRAY, a_llm * a_person))

    # ── LLM (centre) ──────────────────────────────────────────────────────────
    LCX, LCY = 348, PY + 22
    draw_llm(d, LCX, LCY, 155, 125, a_llm, pulse)
    ct(d, "LLM", LCX, LCY, fonts["b_md"], fade(C_DARK, a_llm))

    # Arrow: LLM → answer
    arw(d, LCX + 78, LCY, 448, LCY, fade(C_GRAY, a_ans))

    # ── Answer bubble (right) ─────────────────────────────────────────────────
    ACX, ACY = 575, LCY
    draw_bubble(d, ACX, ACY, 224, 98, C_GREEN, a_ans, tail="down")
    ct(d, "No disease", ACX, ACY - 14, fonts["b_md"], fade(C_DARK, a_ans))
    draw_check(d, ACX, ACY + 20, 34, (38, 128, 62), a_ans)

    # ── Explanation bubble (bottom) ───────────────────────────────────────────
    ECX, ECY = W // 2, 378
    draw_bubble(d, ECX, ECY, 460, 92, C_YELLOW, a_exp, tail="up")
    draw_key(d, ECX - 175, ECY, 44, (175, 145, 55), a_exp)
    ct(d, '"Age is the decisive factor"',
       ECX + 20, ECY, fonts["b_sm"], fade(C_DARK, a_exp))

    ct(d, "Model answers & explains", W // 2, 30, fonts["xs"], fade(C_LIGHT, a_llm))
    return img

# ======
# ======
# SCENE 2 — Age morphs 60 → 30; LLM flips its answer
# ======
# ======

def scene2(t, fonts):
    """
    Left:   original patient (dimmed, age 60)
    →       big arrow + "?" in centre
    Right:  counterfactual patient slides in; age ticks 60 → 30 (highlighted)
    Bottom: new answer bubble (disease detected ✗)
    """
    img = Image.new("RGB", (W, H), BG)
    d   = ImageDraw.Draw(img)

    a_all  = ease(min(1.0, t * 1.6))
    slide  = ease(min(1.0, t * 2.0))
    age_t  = ease(max(0.0, min(1.0, t * 3.0 - 0.7)))
    age_v  = int(lerp(60, 30, age_t))
    hi     = 0.25 < t < 0.82          # highlight age during change
    a_ans  = ease(max(0.0, t * 2.2 - 1.5))
    pulse  = (math.sin(t * math.pi * 5) * 0.5 + 0.5)

    # ── Patient A — dimmed (left) ─────────────────────────────────────────────
    draw_person(d, 110, 168, 0.20 * a_all, C_BLUE)
    ct(d, "Age  60", 110, 278, fonts["b_sm"], fade(C_MED, 0.20 * a_all))

    # ── Centre: arrow + "?" ───────────────────────────────────────────────────
    arw(d, 180, 205, 310, 205, fade(C_GRAY, a_all), width=4, head=16)
    q_a = ease(max(0.0, t * 3.0 - 0.4))
    ct(d, "?", 245, 248, fonts["b_xl"], fade(C_MED, a_all * q_a))

    # ── LLM (centre-right) ────────────────────────────────────────────────────
    LCX, LCY = 400, 190
    draw_llm(d, LCX, LCY, 148, 118, a_all, pulse * a_all)
    ct(d, "LLM", LCX, LCY, fonts["b_md"], fade(C_DARK, a_all))

    # ── Counterfactual patient slides in (right) ───────────────────────────────
    px = int(lerp(W + 70, 608, slide))
    draw_person(d, px, 168, slide, C_BLUE)

    age_col = (200, 60, 60) if hi else C_DARK
    ct(d, f"Age  {age_v}", px, 278, fonts["b_md"], fade(age_col, slide))

    if hi:
        # Highlight ring around age label
        bw = 108
        cy_a = 278
        d.rounded_rectangle([px - bw//2 - 8, cy_a - 20, px + bw//2 + 8, cy_a + 20],
                             radius=6, outline=fade((200, 72, 72), slide * 0.85), width=2)

    # Arrow: new patient → LLM
    if slide > 0.15:
        arw(d, px - 58, 196, LCX + 74, LCY, fade(C_GRAY, a_all * min(1, slide * 3)))

    # ── New answer bubble (bottom centre) ─────────────────────────────────────
    if a_ans > 0.04:
        ACX, ACY = W // 2, 385
        draw_bubble(d, ACX, ACY, 310, 88, C_RED, a_ans, tail="up")
        ct(d, "Disease detected", ACX, ACY - 12, fonts["b_md"], fade(C_DARK, a_ans))
        draw_xmark(d, ACX, ACY + 18, 26, (165, 45, 45), a_ans)

    ct(d, "Same model  \u2014  different age  \u2014  different answer",
       W // 2, 30, fonts["xs"], fade(C_LIGHT, a_all))
    return img

# ======
# ======
# SCENE 3 — Observer with vs without explanation; NSG bar chart
# ======
# ======

def scene3(t, fonts):
    """
    Left column (cx=180):  observer — no explanation → ? → ✗ wrong
    Right column (cx=540): observer — has key/explanation → ✓ correct
    Bottom: accuracy bars + NSG uplift bracket
    """
    img = Image.new("RGB", (W, H), BG)
    d   = ImageDraw.Draw(img)

    a_lay = ease(min(1.0, t * 1.8))
    a_res = ease(max(0.0, t * 2.0 - 0.7))
    a_bar = ease(max(0.0, t * 2.0 - 1.0))
    a_nsg = ease(max(0.0, t * 2.6 - 1.9))

    LX, RX = W // 4, 3 * W // 4    # col centres: 180, 540

    # Vertical divider
    d.line([(W // 2, 52), (W // 2, 418)], fill=fade(C_GRAY, a_lay), width=1)

    # ── Headers ───────────────────────────────────────────────────────────────
    ct(d, "No explanation", LX, 68, fonts["b_sm"], fade(C_MED,   a_lay))
    ct(d, "With explanation", RX, 68, fonts["b_sm"], fade(C_MED, a_lay))

    # ── Observer person icons ─────────────────────────────────────────────────
    draw_person(d, LX, 122, a_lay, C_GRAY)
    draw_person(d, RX, 122, a_lay, C_GREEN)

    # ── ? vs key ──────────────────────────────────────────────────────────────
    ct(d, "?", LX, 215, fonts["b_xl"], fade(C_MED, a_lay))
    draw_key(d, RX, 215, 52, (175, 145, 55), a_lay)

    # ── Result boxes ──────────────────────────────────────────────────────────
    RW, RH = 168, 62
    # Left — wrong
    lx0, ly0 = LX - RW // 2, 256
    rr(d, lx0, ly0, lx0 + RW, ly0 + RH,
       fade(C_RED, a_res), fade(C_GRAY, a_res * 0.55), radius=10)
    ct(d, "Wrong", LX, ly0 + RH // 2 - 10, fonts["b_md"], fade((158, 46, 46), a_res))
    draw_xmark(d, LX, ly0 + RH // 2 + 16, 24, (158, 46, 46), a_res)
    # Right — correct
    rx0, ry0 = RX - RW // 2, 256
    rr(d, rx0, ry0, rx0 + RW, ry0 + RH,
       fade(C_GREEN, a_res), fade(C_GRAY, a_res * 0.55), radius=10)
    ct(d, "Correct", RX, ry0 + RH // 2 - 10, fonts["b_md"], fade((36, 126, 60), a_res))
    draw_check(d, RX, ry0 + RH // 2 + 18, 32, (36, 126, 60), a_res)

    # ── Accuracy bars ─────────────────────────────────────────────────────────
    BAR_BOT = 432
    BAR_MAX = 95
    BW      = 88

    h1 = int(BAR_MAX * 0.62 * a_bar)   # 59 px max
    h2 = int(BAR_MAX * 0.82 * a_bar)   # 78 px max

    if h1 > 0:
        rr(d, LX - BW//2, BAR_BOT - h1, LX + BW//2, BAR_BOT,
           fade(C_RED,   a_bar), fade(C_GRAY, a_bar * 0.45), radius=5)
    if h2 > 0:
        rr(d, RX - BW//2, BAR_BOT - h2, RX + BW//2, BAR_BOT,
           fade(C_GREEN, a_bar), fade(C_GRAY, a_bar * 0.45), radius=5)

    if a_bar > 0.1:
        ct(d, "62%", LX, BAR_BOT - h1 - 18, fonts["sm"], fade(C_MED, a_bar))
        ct(d, "82%", RX, BAR_BOT - h2 - 18, fonts["sm"], fade(C_MED, a_bar))
    d.line([(LX - BW//2 - 12, BAR_BOT), (RX + BW//2 + 12, BAR_BOT)],
           fill=fade(C_GRAY, a_bar), width=1)

    # ── NSG uplift bracket ────────────────────────────────────────────────────
    if a_nsg > 0.01 and h2 > h1 + 4:
        bc  = fade((95, 112, 185), a_nsg)
        lbc = fade((75,  95, 172), a_nsg)
        y_lo = BAR_BOT - h1
        y_hi = BAR_BOT - h2
        mx   = W // 2
        # Horizontal tick at y_lo (top of shorter bar)
        d.line([(LX + BW//2 + 5, y_lo), (RX - BW//2 - 5, y_lo)], fill=bc, width=2)
        # Vertical arrow from y_lo up to y_hi
        arw(d, mx, y_lo, mx, y_hi + 2, bc, width=2, head=9)
        ct(d, "NSG \u2248 26%", mx, y_hi - 22, fonts["b_sm"], lbc)

    ct(d, "Can an observer predict the model's answer?",
       W // 2, 30, fonts["xs"], fade(C_LIGHT, a_lay))
    return img

# ======
# FRAME COMPOSITION
# ======

def render_frames(fonts):
    scene_fns = [scene1, scene2, scene3]
    n = len(scene_fns)
    xf = XFADE / N_PER

    frames = []
    for fi in range(N_FRAMES):
        si    = min(fi // N_PER, n - 1)
        t_loc = (fi - si * N_PER) / N_PER

        main = scene_fns[si](t_loc, fonts)

        if t_loc < xf:
            prev = scene_fns[(si - 1) % n](1.0, fonts)
            main = Image.blend(prev, main, t_loc / xf)

        frames.append(main)
    return frames

def validate(frames):
    for i, f in enumerate(frames):
        px = list(f.getdata())
        if f.size != (W, H):
            print(f"  ⚠ Frame {i}: wrong size {f.size}")
            return False
        if all(p == BG for p in px):
            print(f"  ⚠ Frame {i}: blank")
            return False
    print(f"  ✓ All {len(frames)} frames OK ({W}×{H})")
    return True

def main():
    print("━" * 50)
    print("  NSG WebP Generator  (3 scenes · 14 s)")
    print("━" * 50)
    print("\n[1/4] Fonts …")
    fonts = make_fonts()
    print("[2/4] Rendering 210 frames …")
    frames = render_frames(fonts)
    print("[3/4] Validating …")
    validate(frames)
    print(f"[4/4] Saving → {OUT_PATH}")
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    frames[0].save(
        OUT_PATH,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=DELAY_MS,
        loop=0,
        lossless=True,   # crisp text rendering
    )
    kb = os.path.getsize(OUT_PATH) // 1024
    print(f"\n  ✓ Done!  {N_FRAMES} frames · {N_FRAMES/FPS:.1f} s · {DELAY_MS} ms/frame · {kb} KB")
    print(f"  ✓ {OUT_PATH}")
    print("━" * 50)

if __name__ == "__main__":
    main()
