# publications_gif/src/generate_mwm.py

#!/usr/bin/env python3
"""
SCENE 1  0.5 – 3.8 s   Two nodes appear; dashed red gap + pulsing "?"
SCENE 2  3.8 – 7.8 s   8 practice icons arc in across the gap
SCENE 3  8.0 – 9.6 s   Gap heals → solid green arrow + "Construct Validity ✓"

EDIT GUIDE
  Colours    : C_* constants and ICON_FILLS / ICON_MARKS lists
  Positions  : PHE_CX/CY/R, SCO_CX/CY, BOX_*, ARR_*, ICON_Y/R constants
  Text       : string literals passed to ctext()
  Font sizes : size= argument in _font() calls at top of file
  Timing     : s / e arguments in ph(t, s, e) calls (in seconds)
  Speed      : FPS and TOTAL_SECS constants
"""

import math, os
from PIL import Image, ImageDraw, ImageFont

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════

W, H       = 720, 450          # canvas dimensions (px)
FPS        = 20                # frames per second — smoother animation
TOTAL_SECS = 10.0              # total loop duration (seconds)
N_FRAMES   = int(FPS * TOTAL_SECS)   # = 120

# ── Pastel palette ─────────────────────────────────────────────────────────────
BG     = (255, 255, 255)
C_PHE  = (188, 215, 244)       # Phenomenon circle fill — pastel blue
C_SCO  = (245, 212, 183)       # Score box fill        — pastel peach
C_BAD  = (218, 100, 100)       # gap arrow             — muted red
C_GOOD = ( 95, 172, 118)       # resolved arrow        — muted green
C_STR  = (172, 172, 188)       # node outlines
C_TXT  = ( 55,  55,  70)       # primary text
C_SUB  = (138, 138, 158)       # sub-labels
C_GAP  = (188,  55,  55)       # "?" symbol colour
C_GCV  = ( 48, 138,  76)       # "Construct Validity ✓" label colour

# 8 pastel fills for icon circles, and matching darker mark colours
ICON_FILLS = [
    (186, 218, 246), (200, 236, 196), (254, 228, 176),
    (220, 198, 242), (246, 210, 194), (192, 228, 222),
    (244, 200, 218), (208, 234, 192),
]
ICON_MARKS = [
    ( 92, 142, 188), ( 92, 165, 112), (192, 155,  72),
    (145, 110, 182), (182, 112,  82), ( 92, 155, 145),
    (172, 102, 140), (102, 162,  92),
]

# ── Fonts — all sizes are 2× the original 480×270 script values ───────────────
# Cross-platform font paths (Linux, macOS, Windows)
FONT_PATHS_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",        # Linux
    "/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",           # macOS
    "/Library/Fonts/Arial.ttf",                               # macOS alt
    "C:/Windows/Fonts/arial.ttf",                             # Windows
]
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",   # Linux
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",      # macOS
    "/Library/Fonts/Arial Bold.ttf",                          # macOS alt
    "C:/Windows/Fonts/arialbd.ttf",                           # Windows
]

def _font(size, bold=False):
    """Load font (supports ✓ ≠ etc.). Falls back gracefully."""
    paths = FONT_PATHS_BOLD if bold else FONT_PATHS_REG
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except OSError:
                continue
    # Fallback with explicit size for newer Pillow
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

F_NODE = _font(28, bold=True)   # node labels        (increased for readability)
F_SUB  = _font(20)               # sub-labels         (increased)
F_QUES = _font(58, bold=True)   # "?" symbol
F_CV   = _font(30, bold=True)   # "Construct Validity ✓" label (increased)

# ── Node geometry ──────────────────────────────────────────────────────────────
PHE_CX, PHE_CY = 108, 220       # Phenomenon circle centre
PHE_R          = 90              # radius — sized to hold "Phenomenon" at 22pt

SCO_CX, SCO_CY = 618, 220       # Benchmark score box centre
BOX_W, BOX_H   = 148, 90        # box dimensions
BOX_RAD        = 16             # corner radius

ARR_Y  = PHE_CY                  # horizontal arrow y
ARR_X1 = PHE_CX + PHE_R + 10    # 208 — arrow start (just outside circle)
ARR_X2 = SCO_CX - BOX_W//2 - 10 # 534 — arrow end   (just outside box)
ARR_MX = (ARR_X1 + ARR_X2) // 2  # 371 — midpoint

# ── 8 icon arc (spread between nodes, above the arrow) ───────────────────────
N_ICONS = 8
ICON_Y  = 100                    # y-centre of all icon circles
ICON_R  = 17                     # icon circle radius
_start  = ARR_X1 + ICON_R + 10  # 235 — leftmost icon centre
_end    = ARR_X2 - ICON_R - 10  # 507 — rightmost icon centre
ICON_XS = [int(_start + (_end - _start) * i / (N_ICONS - 1))
           for i in range(N_ICONS)]   # [235, 273, 312, …, 507]

# Arc connector endpoints (top of each node — polyline path above arrow)
ARC_L = (PHE_CX, PHE_CY - PHE_R)         # (108, 130) — top of PHE circle
ARC_R = (SCO_CX, SCO_CY - BOX_H // 2)   # (618, 175) — top of SCO box

# ═══════════════════════════════════════════════════════════════════════════════
# UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def ease(t):
    """Smooth-step easing, clamped to [0, 1]."""
    t = max(0., min(1., t))
    return t * t * (3. - 2. * t)

def ph(t, s, e):
    """
    Eased progress [0→1] from second s to e.
    t, s, e are all in seconds.
    Returns 0 before s, 1 after e, smooth ease in between.
    """
    if t <= s: return 0.
    if t >= e: return 1.
    return ease((t - s) / (e - s))

def lc(c1, c2, a):
    """Lerp two RGB tuples by alpha a ∈ [0, 1]."""
    a = max(0., min(1., a))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))

def ctext(draw, cx, cy, text, font, fill):
    """Draw text centred at pixel (cx, cy)."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)

def dashed(draw, x1, y1, x2, y2, col, dash=16, gap=10, w=3):
    """Draw a dashed line from (x1,y1) to (x2,y2)."""
    L = math.hypot(x2 - x1, y2 - y1)
    if L < 1: return
    dx, dy = (x2 - x1) / L, (y2 - y1) / L
    p = 0.
    while p < L:
        e_ = min(p + dash, L)
        draw.line([(x1+dx*p, y1+dy*p), (x1+dx*e_, y1+dy*e_)], fill=col, width=w)
        p += dash + gap

def arr_tip(draw, x2, y, col, sz=14, w=3):
    """Rightward arrowhead at (x2, y)."""
    for da in (0.40, -0.40):
        draw.line([(x2, y), (x2 - sz*math.cos(da), y - sz*math.sin(da))],
                  fill=col, width=w)

# ── 8 Icon mark drawing functions ─────────────────────────────────────────────
# Each: (draw, cx, cy, r, mark_colour) — r is the working radius inside the circle

def icon_lens(draw, cx, cy, r, c):
    """Magnifying glass — (1) Define the phenomenon"""
    lr = int(r * 0.56)
    draw.ellipse([cx-lr, cy-lr-1, cx+lr, cy+lr-1], outline=c, width=2)
    draw.line([(cx+int(lr*0.68), cy+int(lr*0.68)-1),
               (cx+r-1, cy+r-3)], fill=c, width=3)

def icon_target(draw, cx, cy, r, c):
    """Bullseye — (2) Measure only the phenomenon"""
    ro, ri = int(r*0.82), int(r*0.45)
    draw.ellipse([cx-ro, cy-ro, cx+ro, cy+ro], outline=c, width=2)
    draw.ellipse([cx-ri, cy-ri, cx+ri, cy+ri], outline=c, width=2)
    draw.ellipse([cx-4,  cy-4,  cx+4,  cy+4],  fill=c)

def icon_grid(draw, cx, cy, r, c):
    """2×2 grid — (3) Build a representative dataset"""
    s = int(r * 0.34); g = int(r * 0.13)
    for di in (-1, 1):
        for dj in (-1, 1):
            ox = cx + dj*(s + g); oy = cy + di*(s + g)
            draw.rectangle([ox-s, oy-s, ox+s, oy+s], outline=c, width=2)

def icon_recycle(draw, cx, cy, r, c):
    """Two arcs forming a recycle symbol — (4) Acknowledge reused datasets"""
    rr_ = int(r * 0.78)
    draw.arc([cx-rr_, cy-rr_, cx+rr_, cy+rr_], 215, 345, fill=c, width=2)
    ang = math.radians(345)
    ax, ay = int(cx + rr_*math.cos(ang)), int(cy + rr_*math.sin(ang))
    draw.line([(ax, ay), (ax-7, ay-4)], fill=c, width=2)
    draw.arc([cx-rr_, cy-rr_, cx+rr_, cy+rr_], 35, 165, fill=c, width=2)
    ang2 = math.radians(165)
    ax2, ay2 = int(cx + rr_*math.cos(ang2)), int(cy + rr_*math.sin(ang2))
    draw.line([(ax2, ay2), (ax2+7, ay2+4)], fill=c, width=2)

def icon_shield(draw, cx, cy, r, c):
    """Shield polygon — (5) Prepare for contamination"""
    pts = [
        (cx,       cy - r + 3),
        (cx + r-3, cy - r//2),
        (cx + r-3, cy + r//4),
        (cx,       cy + r - 3),
        (cx - r+3, cy + r//4),
        (cx - r+3, cy - r//2),
    ]
    draw.polygon(pts, outline=c, width=2)

def icon_bars(draw, cx, cy, r, c):
    """Bar chart — (6) Use statistical methods"""
    bw   = int(r * 0.28)
    base = cy + int(r * 0.74)
    for ox, h in zip([-int(r*0.52), 0, int(r*0.52)],
                     [int(r*0.52), int(r*0.82), int(r*0.64)]):
        draw.rectangle([cx+ox-bw, base-h, cx+ox+bw, base], outline=c, width=2)

def icon_scan(draw, cx, cy, r, c):
    """Document with lines — (7) Conduct an error analysis"""
    dw, dh = int(r*0.70), int(r*0.84)
    draw.rectangle([cx-dw, cy-dh, cx+dw, cy+dh], outline=c, width=2)
    for dy_ in [-int(r*0.36), 0, int(r*0.36)]:
        draw.line([(cx-dw+4, cy+dy_), (cx+dw-4, cy+dy_)], fill=c, width=2)

def icon_stamp(draw, cx, cy, r, c):
    """Large checkmark — (8) Justify construct validity"""
    s = r * 0.70
    pts = [
        (cx - s*0.55, cy + s*0.05),
        (cx - s*0.05, cy + s*0.55),
        (cx + s*0.75, cy - s*0.65),
    ]
    draw.line([pts[0], pts[1]], fill=c, width=3)
    draw.line([pts[1], pts[2]], fill=c, width=3)

ICON_FUNCS = [
    icon_lens, icon_target, icon_grid, icon_recycle,
    icon_shield, icon_bars, icon_scan, icon_stamp,
]

# ═══════════════════════════════════════════════════════════════════════════════
# FRAME LOOP
# ═══════════════════════════════════════════════════════════════════════════════

frames = []

for fi in range(N_FRAMES):
    t = fi / FPS          # current time in seconds

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # ── White envelope — seamless loop ────────────────────────────────────────
    # Fade in: 0→0.5s   |   Fade out: 9.5→10.0s
    env = max(1.0 - ph(t, 0.0, 0.5), ph(t, 9.5, 10.0))

    # ──────────────────────────────────────────────────────────────────────────
    # SCENE 1: Two nodes + dashed gap
    # ──────────────────────────────────────────────────────────────────────────

    # [A] Phenomenon node — blue circle — 0.5→1.7s
    pa = ph(t, 0.5, 1.7)
    if pa > 0:
        cx, cy, r = PHE_CX, PHE_CY, PHE_R
        draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                     fill=lc(BG, C_PHE, pa),
                     outline=lc(BG, C_STR, pa), width=3)
        # Node label + sub-label — adjust text here; adjust font sizes at top
        ctext(draw, cx, cy - 13, "Phenomenon", F_NODE, lc(BG, C_TXT, pa))
        ctext(draw, cx, cy + 14, "(abstract)",  F_SUB,  lc(BG, C_SUB, pa))

    # [B] Benchmark score node — peach rounded-rect — 1.0→2.1s
    sb = ph(t, 1.0, 2.1)
    if sb > 0:
        x1 = SCO_CX - BOX_W//2; y1 = SCO_CY - BOX_H//2
        x2 = SCO_CX + BOX_W//2; y2 = SCO_CY + BOX_H//2
        draw.rounded_rectangle([x1, y1, x2, y2], BOX_RAD,
                                fill=lc(BG, C_SCO, sb),
                                outline=lc(BG, C_STR, sb), width=3)
        ctext(draw, SCO_CX, SCO_CY - 13, "Benchmark", F_NODE, lc(BG, C_TXT, sb))
        ctext(draw, SCO_CX, SCO_CY + 14, "score",      F_SUB,  lc(BG, C_SUB, sb))

    # [C] Dashed red arrow — in: 2.0→2.9s, out: 7.9→8.5s
    bad_in  = ph(t, 2.0, 2.9)
    bad_out = ph(t, 7.9, 8.5)
    bad_a   = bad_in * (1.0 - bad_out)
    if bad_a > 0:
        c_arr = lc(BG, C_BAD, bad_a)
        dashed(draw, ARR_X1, ARR_Y, ARR_X2, ARR_Y, c_arr)
        arr_tip(draw, ARR_X2, ARR_Y, c_arr)

    # [D] Pulsing "?" — in: 2.6→3.3s, out: 3.6→4.4s
    q_in  = ph(t, 2.6, 3.3)
    q_out = ph(t, 3.6, 4.4)
    q_a   = q_in * (1.0 - q_out)
    if q_a > 0:
        # Gentle oscillation makes the "?" feel alive
        pulse = q_a * (1.0 + 0.06 * math.sin(t * 3.6))
        ctext(draw, ARR_MX, ARR_Y - 44, "?",
              F_QUES, lc(BG, C_GAP, min(1., pulse)))

    # ──────────────────────────────────────────────────────────────────────────
    # SCENE 2: 8 practice icons arc in across the gap
    # ──────────────────────────────────────────────────────────────────────────

    for i in range(N_ICONS):
        t0 = 3.8 + i * 0.48       # stagger: 0.48 s per icon — change to speed up/slow down
        ia = ph(t, t0, t0 + 0.55)
        if ia <= 0:
            continue

        ix, iy = ICON_XS[i], ICON_Y

        # ── Icon circle (filled) ───────────────────────────────────────────────
        draw.ellipse([ix-ICON_R, iy-ICON_R, ix+ICON_R, iy+ICON_R],
                     fill=lc(BG, ICON_FILLS[i], ia),
                     outline=lc(BG, ICON_MARKS[i], ia * 0.85), width=1)

        # ── Symbol mark inside circle ──────────────────────────────────────────
        ICON_FUNCS[i](draw, ix, iy, ICON_R - 4, lc(BG, ICON_MARKS[i], ia))

        # ── Arc connector lines (appear once icon is 55% visible) ─────────────
        if ia > 0.55:
            la = ease((ia - 0.55) / 0.45)
            c_ln = lc(BG, (160, 198, 160), la)

            if i == 0:
                # Top of PHE circle → first icon
                draw.line([ARC_L, (ix, iy)], fill=c_ln, width=2)
            else:
                # Previous icon → this icon (once previous is also settled)
                prev_t0  = 3.8 + (i-1) * 0.48
                prev_ia  = ph(t, prev_t0, prev_t0 + 0.55)
                if prev_ia > 0.55:
                    draw.line([(ICON_XS[i-1], ICON_Y), (ix, iy)], fill=c_ln, width=2)

            if i == N_ICONS - 1:
                # Last icon → top of SCO box
                draw.line([(ix, iy), ARC_R], fill=c_ln, width=2)

    # ──────────────────────────────────────────────────────────────────────────
    # SCENE 3: Gap heals — green arrow + "Construct Validity ✓"
    # ──────────────────────────────────────────────────────────────────────────

    # [G] Solid green arrow — 8.1→9.0s
    ga = ph(t, 8.1, 9.0)
    if ga > 0:
        c_g = lc(BG, C_GOOD, ga)
        draw.line([(ARR_X1, ARR_Y), (ARR_X2, ARR_Y)], fill=c_g, width=3)
        arr_tip(draw, ARR_X2, ARR_Y, c_g)

    # [H] "Construct Validity ✓" label — 8.6→9.5s
    cv_a = ph(t, 8.6, 9.5)
    if cv_a > 0:
        ctext(draw, ARR_MX, ARR_Y - 40, "Construct Validity  \u2713",
              F_CV, lc(BG, C_GCV, cv_a))

    # ── Apply white envelope ──────────────────────────────────────────────────
    if env > 0:
        img = Image.blend(img, Image.new("RGB", (W, H), BG), env)

    frames.append(img)


# ═══════════════════════════════════════════════════════════════════════════════
# SELF-REVIEW: scan border pixels for unintended clipping
# ═══════════════════════════════════════════════════════════════════════════════

MARGIN = 6
issues = []
for fi, fr in enumerate(frames):
    if fi % 4 != 0:
        continue      # sample every 4th frame for speed
    px = fr.load()
    for x in range(W):
        for y in list(range(MARGIN)) + list(range(H - MARGIN, H)):
            if px[x, y] != BG: issues.append(f"f{fi} ({x},{y})")
    for y in range(H):
        for x in list(range(MARGIN)) + list(range(W - MARGIN, W)):
            if px[x, y] != BG: issues.append(f"f{fi} ({x},{y})")

unique = list(dict.fromkeys(issues))[:8]
if unique:
    print("⚠️  Edge-clipping warnings:")
    for w in unique: print("   ", w)
else:
    print("✓  Self-review: no edge-clipping detected.")
print(f"✓  {len(frames)} frames  |  {W}×{H}px  |  {FPS}fps  |  {TOTAL_SECS}s loop")


# ═══════════════════════════════════════════════════════════════════════════════
# SAVE — animated WebP
# ═══════════════════════════════════════════════════════════════════════════════

OUT = "img/publications/mwm.webp"
os.makedirs(os.path.dirname(OUT), exist_ok=True)

frames[0].save(
    OUT,
    save_all=True,
    append_images=frames[1:],
    loop=0,                        # 0 = loop forever
    duration=int(1000 / FPS),      # ms per frame (83 ms @ 12 fps)
    lossless=True,                 # lossless WebP for crisp vector art
)
print(f"✓  Saved → {OUT}")