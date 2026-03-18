# publications_gif/src/generate_helpmed.py

"""
  Act 1 — The Trial
      Clinical vignette card with medical cross fans out into
      four colour-coded RCT arms (GPT-4o · Llama 3 · Command R+ · Control).
      Icons + colour carry the message; minimal text.

  Act 2 — The Contrast
      Split canvas.  Left: stethoscope → 95 % green bar (LLM direct).
      Right: patient silhouette --→ LLM terminal → 34 % rose bar (RCT arm).
      Both bars animate simultaneously — the height difference is the story.

  Act 3 — The Gap
      Bars freeze.  A calibrated bracket fades in at centre: "−61 pp".
      Medical cross anchors the clinical frame.

  Fade to white → seamless loop.
"""

from PIL import Image, ImageDraw, ImageFont
import math, os, shutil

# ─────────────────────────────────────────────────────────────────
# CANVAS & TIMING
# ─────────────────────────────────────────────────────────────────
W, H     = 720, 450
FRAME_MS = 55          # ~18 fps
N        = 226         # frames → 12.4 s loop

# ─────────────────────────────────────────────────────────────────
# PALETTE  — muted clinical tones
# ─────────────────────────────────────────────────────────────────
BG      = (255, 255, 255)
C_SLATE = (88,  110, 130)
C_MID   = (155, 170, 182)
C_SAGE  = (130, 185, 155)   # LLM-alone / success
C_ROSE  = (210, 128, 138)   # human+LLM / warning
C_AMBER = (215, 170,  85)   # red-flag accent
C_TRACK = (228, 228, 224)   # bar background
C_CARD  = (240, 243, 246)   # vignette card fill
C_GPT   = (115, 160, 210)
C_LLAMA = (135, 195, 160)
C_CMD   = (185, 155, 210)
C_CTRL  = (200, 195, 180)

# ─────────────────────────────────────────────────────────────────
# FONTS  — 2× the original sizes
# ─────────────────────────────────────────────────────────────────
# Cross-platform font paths (Linux, macOS, Windows)
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

def _f(size, bold=False):
    paths = FONT_PATHS_BOLD if bold else FONT_PATHS_REG
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    # Fallback with explicit size for newer Pillow
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()

F_TINY = _f(22)          # footnote / axis labels   (was 9, then 18)
F_SM   = _f(26)          # pill labels               (was 11, then 22)
F_MD   = _f(30)          # bracket labels            (was 13, then 26)
F_LG   = _f(36, True)    # scene descriptor          (was 16, then 32)
F_XL   = _f(56, True)    # big percentage number     (was 24, then 48)

# ─────────────────────────────────────────────────────────────────
# ACT TIMING (frame indices)
# ─────────────────────────────────────────────────────────────────
# Act 1 — RCT arms
A1_FADEIN  = (0,  22)
A1_ARMS    = (14, 78)     # arms stagger in
A1_FADEOUT = (78, 90)

# Act 2 — parallel bars (no fade-out; flows directly into act 3)
A2_FADEIN  = (90, 110)
A2_FILL    = (106, 158)
A2_HOLD    = (158, 170)   # bars freeze at max before act 3

# Act 3 — gap bracket (bars remain; bracket fades on top)
A3_BRACKET = (170, 198)   # bracket draws in
A3_HOLD    = (198, 215)
A3_FADEOUT = (212, 222)

FADE_START = 222          # cross-fade to white before loop

# ─────────────────────────────────────────────────────────────────
# BAR GEOMETRY  (scaled for 720 × 450)
# ─────────────────────────────────────────────────────────────────
BAR_BOT = 410   # y of bar bottom
BAR_W   = 72    # bar width
BAR_H   = 220   # full-track height

# Left / right bar centres (split at x=360)
BX_L = 185      # LLM-alone bar
BX_R = 540      # Human+LLM bar

# ─────────────────────────────────────────────────────────────────
# MATH / COLOUR HELPERS
# ─────────────────────────────────────────────────────────────────

def ease(t):
    t = max(0., min(1., t))
    return t * t * (3. - 2. * t)

def pt(f, s, e):
    if e <= s: return 1.
    return max(0., min(1., (f - s) / (e - s)))

def lerp(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def fbg(col, a):
    """Blend col → white at alpha (1=colour, 0=white)."""
    a = max(0., min(1., a))
    return tuple(int(BG[i] + (col[i] - BG[i]) * a) for i in range(3))

def tc(draw, cx, cy, text, font, fill):
    """Centre text at (cx, cy)."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]; th = bb[3] - bb[1]
    draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)

# ─────────────────────────────────────────────────────────────────
# ICON PRIMITIVES  — thin-stroke, no solid cartoon fills
# ─────────────────────────────────────────────────────────────────

def draw_medical_cross(draw, cx, cy, r=14, col=(175, 58, 68), lw=2):
    """Outlined ⊕ medical cross in a circle."""
    draw.ellipse([cx-r, cy-r, cx+r, cy+r],
                 outline=col, width=lw, fill=lerp(col, BG, 0.88))
    arm = int(r * 0.54); hw = max(1, lw - 1)
    draw.rectangle([cx - hw, cy - arm, cx + hw, cy + arm], fill=col)
    draw.rectangle([cx - arm, cy - hw, cx + arm, cy + hw], fill=col)


def draw_stethoscope(draw, cx, cy, s=1., col=C_SLATE, lw=2):
    """
    Minimalist stethoscope.
    cx/cy = chest-piece centre.  Tubing arcs up to two earpieces.
    Adjust cx/cy to reposition; s to resize.
    """
    sw = max(1, round(lw * s))
    cr = round(9 * s)    # chest-piece radius
    # Chest piece
    draw.ellipse([cx-cr, cy-cr, cx+cr, cy+cr],
                 outline=col, width=sw, fill=lerp(col, BG, 0.84))
    draw.ellipse([cx-3, cy-3, cx+3, cy+3], fill=col)   # membrane dot
    # Tubing
    top_y = cy - round(46 * s)
    mid_y = cy - round(23 * s)
    sep   = round(22 * s)
    for sign in (-1, 1):
        pts = [
            (cx,           cy - cr),
            (cx,           mid_y),
            (cx + sign*sep, mid_y - round(10*s)),
            (cx + sign*sep, top_y),
        ]
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i+1]], fill=col, width=sw)
        er = max(2, round(4 * s))
        draw.ellipse([cx+sign*sep-er, top_y-er,
                      cx+sign*sep+er, top_y+er], fill=col)


def draw_patient(draw, cx, cy, s=1., col=C_SLATE, lw=2):
    """
    Thin-outline patient silhouette.
    cx/cy = torso centre.  Head floats above; body tapers slightly.
    """
    sw  = max(1, round(lw))
    hr  = round(13 * s)
    hcy = cy - round(40 * s)   # head centre y
    draw.ellipse([cx-hr, hcy-hr, cx+hr, hcy+hr],
                 outline=col, width=sw, fill=lerp(col, BG, 0.10))
    bw = round(18 * s)
    body = [
        (cx - bw,            cy - round(10*s)),
        (cx + bw,            cy - round(10*s)),
        (cx + bw + round(4*s), cy + round(40*s)),
        (cx - bw - round(4*s), cy + round(40*s)),
    ]
    draw.polygon(body, outline=col, fill=lerp(col, BG, 0.90))


def draw_terminal(draw, cx, cy, s=1., col=C_SLATE, lw=1):
    """
    Flat 'LLM window' icon: rounded rect with title bar + two text stubs.
    cx/cy = centre of the window.  s = scale; lw = outline width.
    """
    bw = round(32 * s); bh = round(25 * s)
    draw.rounded_rectangle([cx-bw, cy-bh, cx+bw, cy+bh],
                            radius=round(6*s), outline=col, width=lw,
                            fill=lerp(col, BG, 0.91))
    th = round(8 * s)   # title-bar height
    draw.rounded_rectangle([cx-bw, cy-bh, cx+bw, cy-bh+th],
                            radius=round(6*s), fill=lerp(col, BG, 0.68))
    draw.rectangle([cx-bw, cy-bh+round(4*s), cx+bw, cy-bh+th],
                   fill=lerp(col, BG, 0.68))
    # Three dot controls in title bar
    for dx in (-round(9*s), 0, round(9*s)):
        draw.ellipse([cx+dx-2, cy-bh+2, cx+dx+2, cy-bh+th-2],
                     fill=lerp(col, BG, 0.28))
    # Two text-stub lines inside body
    lc = lerp(col, BG, 0.54)
    base = cy - bh + th
    for dy, fw in ((round(9*s), 0.88), (round(18*s), 0.66)):
        ll = round((bw * 1.7 - 8) * fw)
        draw.rounded_rectangle([cx-ll//2, base+dy-1, cx+ll//2, base+dy+1],
                                radius=1, fill=lc)


def draw_clinical_card(draw, x, y, w, h, lines, col, a=1.):
    """
    Clinical vignette card: rounded rect + colour header + stub lines.
    x/y = top-left corner.  lines = number of text stubs.
    """
    bg  = fbg(C_CARD, a)
    bdr = fbg(col, a)
    hdr = fbg(lerp(col, BG, 0.42), a)
    txt = fbg(C_MID, a)
    draw.rounded_rectangle([x, y, x+w, y+h],
                            radius=5, fill=bg, outline=bdr, width=1)
    # Header strip
    draw.rounded_rectangle([x, y, x+w, y+16], radius=5, fill=hdr)
    draw.rectangle([x, y+10, x+w, y+16], fill=hdr)
    # Stub text lines
    lx = x + 8
    for i in range(lines):
        ly = y + 24 + i * 11
        if ly + 4 > y + h - 4: break
        lw = round(w * 0.82 * (0.48 + 0.52 * ((i*7+3) % 10) / 10))
        draw.rounded_rectangle([lx, ly, lx+lw, ly+4],
                                radius=2, fill=txt)


def draw_arrow(draw, x1, y1, x2, y2, col, lw=1, hs=8, dash=False):
    """Thin directed arrow, optionally dashed."""
    if dash:
        dx, dy = x2-x1, y2-y1
        dist = math.hypot(dx, dy)
        if dist < 2: return
        seg = 8; gap = 5; tot = seg + gap
        for i in range(int(dist / tot)):
            t0 = i * tot / dist
            t1 = min(1., (i * tot + seg) / dist)
            draw.line([(round(x1+dx*t0), round(y1+dy*t0)),
                       (round(x1+dx*t1), round(y1+dy*t1))],
                      fill=col, width=lw)
    else:
        draw.line([(x1, y1), (x2, y2)], fill=col, width=lw)
    ang = math.atan2(y2-y1, x2-x1)
    for side in (1, -1):
        draw.line([(x2, y2),
                   (round(x2 - hs*math.cos(ang - side*0.40)),
                    round(y2 - hs*math.sin(ang - side*0.40)))],
                  fill=col, width=lw)


def draw_vbar(draw, cx, bot, bw, bh, frac, fill_col, trk_a=1.):
    """Vertical bar: filled from the bottom up."""
    draw.rounded_rectangle([cx-bw//2, bot-bh, cx+bw//2, bot],
                            radius=5, fill=fbg(C_TRACK, trk_a))
    fh = round(bh * max(0., min(1., frac)))
    if fh >= 5:
        draw.rounded_rectangle([cx-bw//2, bot-fh, cx+bw//2, bot],
                                radius=5, fill=fill_col)


# ─────────────────────────────────────────────────────────────────
# ACT RENDERERS
# ─────────────────────────────────────────────────────────────────

def act1(draw, f):
    """
    Act 1 — The Trial
    Clinical card + medical cross (left) → animated trunk → 4 arm pills (right).
    No scene header. Icons and colour tell the story.

    Card:      x=55, y=143, w=108, h=168   (centre ≈ canvas midpoint y=227)
    Cross:     cx=109, cy=124
    Trunk:     y=227, from x=164 to branch x=330
    Arms:      y=[82, 178, 274, 370]  (spacing 96 px, centred at y=226)
    Pills:     cx=560, half-width=105
    """
    a_in  = ease(pt(f, *A1_FADEIN))
    a_ani = ease(pt(f, *A1_ARMS))
    a_out = 1. - ease(pt(f, *A1_FADEOUT))
    a     = a_in * a_out

    TRUNK_Y  = 227
    BRANCH_X = 330
    CARD_R   = 164   # right edge of card

    # Clinical vignette card
    draw_clinical_card(draw, 55, 143, 108, 168,
                       lines=12, col=C_SLATE, a=a)
    draw_medical_cross(draw, 109, 124, r=13,
                       col=fbg((175, 58, 68), a), lw=2)
    # "10 scenarios" note below card
    tc(draw, 109, 322, "10 scenarios", F_TINY, fbg(C_MID, a))

    # Animated trunk arrow (grows rightward as a_ani progresses)
    if a > 0.04:
        tx2 = CARD_R + round((BRANCH_X - CARD_R) * a_ani)
        draw_arrow(draw, CARD_R, TRUNK_Y, tx2, TRUNK_Y,
                   fbg(C_MID, a), lw=2)

    # Four arm pills — stagger in with small delay each
    arm_ys     = [82, 178, 274, 370]
    arm_cols   = [C_GPT, C_LLAMA, C_CMD, C_CTRL]
    arm_labels = ["GPT-4o", "Llama 3", "Command R+", "Control"]

    for i, (ay, ac, al) in enumerate(zip(arm_ys, arm_cols, arm_labels)):
        # Each arm fades in 12 frames after the previous
        arm_a = ease(pt(f, A1_ARMS[0] + i*10,
                           A1_ARMS[0] + i*10 + 22)) * a_out
        if arm_a < 0.02: continue

        mc = fbg(C_MID, arm_a)

        # Vertical connector from trunk to arm y
        draw.line([(BRANCH_X, TRUNK_Y), (BRANCH_X, ay)],
                  fill=mc, width=1)
        # Horizontal branch to pill
        draw_arrow(draw, BRANCH_X, ay, 350, ay, mc, lw=1, hs=6)

        # Pill badge (rx=105 from centre)
        pill_cx = 560
        draw.rounded_rectangle(
            [pill_cx - 105, ay - 20, pill_cx + 105, ay + 20],
            radius=20,
            fill=lerp(ac, BG, 0.80),
            outline=lerp(ac, C_SLATE, 0.22), width=1
        )
        # Coloured indicator dot on left of pill
        dot_x = pill_cx - 80
        draw.ellipse([dot_x-6, ay-6, dot_x+6, ay+6],
                     fill=fbg(ac, arm_a * 0.9))
        # Arm label
        tc(draw, pill_cx + 8, ay, al, F_SM,
           fbg(lerp(ac, C_SLATE, 0.40), arm_a))


def act2(draw, f):
    """
    Act 2 — The Contrast
    Split canvas at x=360.
    Left: stethoscope → large green bar (95 %).
    Right: patient silhouette --→ LLM terminal → rose bar (34 %).
    Both bars animate simultaneously.

    Left stethoscope:  cx=185, cy=95,  s=1.25
    Right patient:     cx=468, cy=78,  s=0.95
    Right terminal:    cx=562, cy=92,  s=1.05
    Left bar:          cx=185
    Right bar:         cx=540
    Numbers "95%"/"34%": y=152
    """
    a_in  = ease(pt(f, *A2_FADEIN))
    a_bar = ease(pt(f, *A2_FILL))
    # Act 2 never fades out (act 3 inherits the full bars)
    a = a_in

    col_l = fbg(C_SLATE, a)
    col_m = fbg(C_MID,   a)

    # ── Thin vertical divider ────────────────────────
    for dy in range(30, 420, 10):
        draw.line([(360, dy), (360, dy+5)],
                  fill=fbg(C_TRACK, a), width=1)

    # ── LEFT COLUMN — LLM alone ──────────────────────
    # Stethoscope (cx=185, cy=118, scale=1.25)
    # Earpieces reach up to cy - 46*1.25 = 118-58 = 60 px — clears label.
    draw_stethoscope(draw, 185, 118, s=1.25, col=col_l, lw=2)

    # Small column label (top-left, y=34 — well above earpieces at y≈60)
    tc(draw, 185, 34, "LLM direct", F_TINY, fbg(C_MID, a * 0.7))

    # "95%" rising number — appears as bar fills
    pct_l = round(a_bar * 95)
    tc(draw, 185, 152,
       f"{pct_l}%", F_XL,
       fbg(C_SAGE, min(1., a_bar * 2.5) * a))

    # Left bar
    draw_vbar(draw, 185, BAR_BOT, BAR_W, BAR_H,
              frac=a_bar * 0.95,
              fill_col=fbg(C_SAGE, a),
              trk_a=a)

    # Bar bottom label
    tc(draw, 185, BAR_BOT + 22, "conditions identified", F_TINY, col_m)

    # ── RIGHT COLUMN — Human + LLM ───────────────────
    # Patient silhouette (cx=468, cy=78, s=0.95)
    draw_patient(draw, 468, 78, s=0.95, col=col_l, lw=2)

    # Dashed arrow patient → terminal (horizontal, y≈85)
    # Patient right edge ≈ 468 + 18*0.95 = 485
    # Terminal left edge ≈ 562 - 32 = 530
    if a > 0.08:
        draw_arrow(draw, 490, 85, 528, 87,
                   col_m, lw=1, hs=6, dash=True)

    # LLM terminal (cx=562, cy=92, s=1.05)
    draw_terminal(draw, 562, 92, s=1.05, col=col_l, lw=1)

    # Arrow from terminal down to bar track
    if a > 0.08:
        draw_arrow(draw, 562, 118, 540, 188,
                   col_m, lw=1, hs=6)

    # Small column label
    tc(draw, 540, 34, "Human + LLM", F_TINY, fbg(C_MID, a * 0.7))

    # "34%" rising number
    pct_r = round(a_bar * 34)
    tc(draw, 540, 152,
       f"{pct_r}%", F_XL,
       fbg(C_ROSE, min(1., a_bar * 2.5) * a))

    # Right bar
    draw_vbar(draw, 540, BAR_BOT, BAR_W, BAR_H,
              frac=a_bar * 0.34,
              fill_col=fbg(C_ROSE, a),
              trk_a=a)

    tc(draw, 540, BAR_BOT + 22, "conditions identified", F_TINY, col_m)


def act3(draw, f):
    """
    Act 3 — The Gap
    Bars stay frozen at 95 % / 34 %.
    A bracket animates in at the centre with "−61 pp".
    Medical cross top-right reinforces the clinical frame.

    Bracket spine:  x=362
    y_hi (95 % bar top):  BAR_BOT − BAR_H×0.95 ≈ 201
    y_lo (34 % bar top):  BAR_BOT − BAR_H×0.34 ≈ 335
    mid_y:                ≈ 268
    """
    a_out  = 1. - ease(pt(f, *A3_FADEOUT))
    a_brk  = ease(pt(f, *A3_BRACKET)) * a_out
    a_bars = a_out           # bars visible as long as scene is

    col_m  = fbg(C_MID, a_bars)

    # ── Frozen bars ───────────────────────────────────
    # Thin divider
    for dy in range(30, 420, 10):
        draw.line([(360, dy), (360, dy+5)],
                  fill=fbg(C_TRACK, a_bars), width=1)

    draw_vbar(draw, BX_L, BAR_BOT, BAR_W, BAR_H,
              frac=0.95, fill_col=fbg(C_SAGE, a_bars), trk_a=a_bars)
    draw_vbar(draw, BX_R, BAR_BOT, BAR_W, BAR_H,
              frac=0.34, fill_col=fbg(C_ROSE, a_bars), trk_a=a_bars)

    tc(draw, BX_L, 152, "95%", F_XL, fbg(C_SAGE, a_bars))
    tc(draw, BX_R, 152, "34%", F_XL, fbg(C_ROSE, a_bars))

    tc(draw, BX_L, BAR_BOT + 22, "LLM direct",   F_TINY, col_m)
    tc(draw, BX_R, BAR_BOT + 22, "Human + LLM",  F_TINY, col_m)

    # Medical cross — top right
    draw_medical_cross(draw, 658, 36, r=16,
                       col=fbg((175, 58, 68), a_bars), lw=2)

    # ── Bracket ──────────────────────────────────────
    if a_brk < 0.02: return

    bc    = fbg(C_ROSE, a_brk)
    bc_m  = fbg(C_MID,  a_brk)

    # Bar tops
    y_hi  = BAR_BOT - round(BAR_H * 0.95)   # ≈ 201
    y_lo  = BAR_BOT - round(BAR_H * 0.34)   # ≈ 335
    mid_y = (y_hi + y_lo) // 2              # ≈ 268

    # Spine x between the two bar inner edges
    # Left bar right edge: BX_L + BAR_W//2 = 185+36=221
    # Right bar left edge: BX_R - BAR_W//2 = 540-36=504
    sp_x = (221 + 504) // 2    # 362

    # Animate bracket: grows from mid_y outward
    half_h = round((mid_y - y_hi) * a_brk)
    y_top  = mid_y - half_h
    y_bot  = mid_y + half_h

    draw.line([(sp_x, y_top), (sp_x, y_bot)], fill=bc, width=2)

    # Tick marks only once bracket is nearly full
    if a_brk > 0.75:
        tick_a = ease((a_brk - 0.75) / 0.25)
        tick_c = fbg(C_ROSE, tick_a * a_out)
        for yt in (y_hi, y_lo):
            draw.line([(sp_x - 8, yt), (sp_x + 8, yt)],
                      fill=tick_c, width=2)

    # Labels appear once bracket is open
    if a_brk > 0.55:
        la = ease((a_brk - 0.55) / 0.45)
        tc(draw, sp_x, mid_y - 18, "−61 pp",    F_MD,   fbg(C_ROSE, la * a_out))
        tc(draw, sp_x, mid_y + 18, "p < 0.001", F_TINY, fbg(C_MID,  la * a_out))


# ─────────────────────────────────────────────────────────────────
# MASTER FRAME COMPOSER
# ─────────────────────────────────────────────────────────────────

def render_frame(f):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    if f < 90:
        act1(draw, f)
    elif f < 170:
        act2(draw, f)
    elif f < FADE_START:
        act3(draw, f)
    else:
        # Cross-fade to white → seamless loop back to act 1 (white background)
        act3(draw, FADE_START - 1)
        t   = ease(pt(f, FADE_START, N - 1))
        img = Image.blend(img, Image.new("RGB", (W, H), BG), t)

    return img


# ─────────────────────────────────────────────────────────────────
# RENDER — SELF-REVIEW — SAVE
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"Rendering {N} frames  {W}×{H} px  {N*FRAME_MS/1000:.1f} s …")
    frames = []
    for f in range(N):
        frames.append(render_frame(f))
        if f % 40 == 0:
            print(f"  {f}/{N}")

    # ── Self-review ─────────────────────────────────
    print("Self-review …")
    issues = 0
    for i, fr in enumerate(frames):
        px = fr.getdata()
        clipped = sum(1 for r, g, b in px if r < 8 and g < 8 and b < 8)
        if clipped:
            print(f"  ⚠  frame {i}: {clipped} near-black pixels")
            issues += 1
    if not issues:
        print("  ✓ no clipping issues")

    # ── Save animated WebP ──────────────────────────
    out_webp   = "img/publications/helpmed.webp"
    os.makedirs(os.path.dirname(out_webp), exist_ok=True)

    frames[0].save(
        out_webp,
        format="WEBP",
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        lossless=True,   # crisp text rendering
    )

    kb = os.path.getsize(out_webp) / 1024
    print(f"✓  {out_webp}  ({kb:.0f} KB)\n✓")