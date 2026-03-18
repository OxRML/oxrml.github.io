# publications_gif/src/generate_lingolytoo.py

"""
  Phase 1  A word + its meaning fade in — large, centred.
           Bracket-style marks hint at morpheme structure.

  Phase 2  Letters scramble one-by-one into the obfuscated word
           while the meaning line stays perfectly still.
           (This is the KEY insight: orthography ≠ meaning.)

  Phase 3  Score bars rise side-by-side.
           A downward Δ arrow between them shows the performance drop.

  Fade     Slow white-out → seamless loop.
"""

from PIL import Image, ImageDraw, ImageFont
import math, os, random

# ── Canvas ───────────────────────────────────────────────── ← ADJUST
W, H  = 720, 450
FPS   = 20
SECS  = 10.0
N     = int(FPS * SECS)   # 200 frames

# ── Palette ──────────────────────────────────────────────── ← ADJUST
BG      = (255, 255, 255)
BLUE_C  = (195, 220, 245)   # original tint
PEACH_C = (250, 213, 190)   # obfuscated tint
BORD_B  = (135, 183, 222)
BORD_P  = (212, 158, 118)
BAR_B   = (150, 198, 232)
BAR_P   = (238, 172, 137)
COL_T   = ( 50,  55,  65)   # dark text
COL_S   = (140, 148, 162)   # muted text
COL_W1  = ( 75, 115, 170)   # original word — blue
COL_W2  = (185, 100,  60)   # obfuscated word — warm
COL_ARR = (180, 170, 200)   # annotation / arrow

# ── Content ──────────────────────────────────────────────── ← ADJUST
ORIG_WORD  = "Ufgent"
OBFU_WORD  = "Eqcawg"
MEANING    = "They flew"

# Extra pairs shown faintly in background (Phase 1 atmosphere)
BG_PAIRS = [
    ("Uzzlegh", "I ran"),
    ("Tufeg",   "She flew"),
    ("Ur ufgegh ara", "He did not fly"),
]

SCORE_ORIG = 0.79   # ← ADJUST
SCORE_OBFU = 0.58   # ← ADJUST

# ── Fonts (DejaVu Sans, 2× the original sizes) ─────────────── ← ADJUST
# Cross-platform font paths (Linux, macOS, Windows)
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",      # macOS
    "/Library/Fonts/Arial Bold.ttf",                          # macOS alt
    "C:/Windows/Fonts/arialbd.ttf",                           # Windows
]
FONT_PATHS_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",        # Linux
    "/System/Library/Fonts/Supplemental/Arial.ttf",           # macOS
    "/Library/Fonts/Arial.ttf",                               # macOS alt
    "C:/Windows/Fonts/arial.ttf",                             # Windows
]

def tf(paths, size):
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

F = {
    "word":   tf(FONT_PATHS_BOLD, 58),   # main word                    ← ADJUST
    "meaning":tf(FONT_PATHS_REG, 30),    # translation line
    "label":  tf(FONT_PATHS_BOLD, 26),   # bar heading / axis labels
    "score":  tf(FONT_PATHS_BOLD, 28),   # score numerals on bars
    "tiny":   tf(FONT_PATHS_REG, 20),    # footnote
    "bgpair": tf(FONT_PATHS_REG, 20),    # faint background pairs
}

# ── Scramble character pool ───────────────────────────────────────────────────
# Keeps the "alien language" feel while staying readable as letter-like shapes
POOL = "abcdefghijklmnopqrstuvwxyz"

# Per-character scramble seed so animation is deterministic
random.seed(42)
CHAR_SEEDS = [random.randint(0, 9999) for _ in range(max(len(ORIG_WORD), len(OBFU_WORD)))]

# ── Score bar layout ──────────────────────────────────────────────────────────
BW     = 120   # bar width           ← ADJUST
BH     = 180   # max bar height
BBASE  = H - 95
BCX    = W // 2
BGAP   = 60    # gap between bars
BOX    = BCX - BGAP // 2 - BW   # left (original) bar x
BRX    = BCX + BGAP // 2         # right (obfuscated) bar x

# ── Helpers ───────────────────────────────────────────────────────────────────
def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)

def ease_out(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 2

def phase(f, s, e):
    if f <= s: return 0.0
    if f >= e: return 1.0
    return ease((f - s) / (e - s))

def lerp(a, b, t): return a + (b - a) * t

def lc(c1, c2, t):
    t = max(0.0, min(1.0, float(t)))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def fc(col, vis): return lc(BG, col, vis)

def tw(font, text):
    """Text width via getbbox or fallback."""
    try:
        bb = font.getbbox(text)
        return bb[2] - bb[0]
    except AttributeError:
        return len(text) * 10

def tcx(draw, text, cx, y, font, fill):
    draw.text((cx - tw(font, text) // 2, y), text, font=font, fill=fill)

def rrect(draw, xy, r, fill=None, outline=None, w=1):
    try:
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=w)
    except AttributeError:
        draw.rectangle(xy, fill=fill, outline=outline, width=w)

# ── Scramble logic ────────────────────────────────────────────────────────────
# Phase 2 spans frames 50-130 (~4 s).
# Each character index `ci` starts scrambling at a slightly different frame
# so the effect ripples left→right.
P2_START = 50
P2_END   = 128
SETTLE_WINDOW = 22   # frames per char to scramble then settle  ← ADJUST

def scramble_char(ci, f, orig_ch, obfu_ch):
    """
    Return the character to display at frame f for character position ci.
    - Before its window: shows orig_ch
    - During scramble: flickers through POOL chars
    - After settle:    shows obfu_ch
    """
    stagger = ci * 10          # ← ADJUST ripple speed (frames between chars)
    win_s = P2_START + stagger
    win_e = win_s + SETTLE_WINDOW

    if f < win_s:
        return orig_ch, 0.0    # (char, blend_to_obfu 0=blue 1=warm)
    if f >= win_e:
        return obfu_ch, 1.0

    # Within the scramble window
    t = (f - win_s) / SETTLE_WINDOW
    if t < 0.7:
        # Flickering phase — deterministic pseudo-random per frame
        rng = random.Random(CHAR_SEEDS[ci] + f * 7)
        ch = rng.choice(POOL)
        if orig_ch.isupper():
            ch = ch.upper()
        return ch, t
    else:
        return obfu_ch, 1.0    # snap to final


# ── Phase renderers ────────────────────────────────────────────────────────────

def draw_bg_pairs(draw, vis):
    """Faint secondary word pairs for atmosphere (Phase 1)."""
    if vis <= 0: return
    for i, (src, tgt) in enumerate(BG_PAIRS):
        y = 60 + i * 40
        # left cluster
        draw.text((48, y), src, font=F["bgpair"], fill=fc(COL_W1, vis * 0.22))
        draw.text((48, y + 21), "→  " + tgt, font=F["bgpair"], fill=fc(COL_S, vis * 0.18))


def draw_word_phase(draw, word_chars, vis, meaning_vis):
    """
    Draw the large central word and its meaning below.
    word_chars: list of (char, blend) tuples — blend 0=blue, 1=warm
    """
    if vis <= 0: return

    # --- meaning line (always stays; separate vis so it persists through scramble)
    if meaning_vis > 0:
        tcx(draw, MEANING, W // 2, H // 2 + 22, F["meaning"], fc(COL_S, meaning_vis))

    # --- horizontal morpheme bracket  (subtle, decorative)
    bvis = vis * 0.35
    if bvis > 0:
        by = H // 2 - 8
        bx0 = W // 2 - 170
        bx1 = W // 2 + 170
        draw.line([(bx0, by), (bx1, by)], fill=fc(COL_S, bvis), width=1)
        for bx in (bx0, bx1):
            draw.line([(bx, by - 5), (bx, by + 5)], fill=fc(COL_S, bvis), width=1)

    # --- render characters individually so each can have its own colour
    total_w = sum(tw(F["word"], ch) + 2 for ch, _ in word_chars) - 2
    cx_start = W // 2 - total_w // 2
    cy = H // 2 - 74   # ← ADJUST vertical centre of word
    x = cx_start
    for (ch, blend) in word_chars:
        col = lc(COL_W1, COL_W2, blend)
        draw.text((x, cy), ch, font=F["word"], fill=fc(col, vis))
        x += tw(F["word"], ch) + 2


def draw_scores(draw, vis):
    """Two bars rising with a delta arrow between them."""
    if vis <= 0: return

    oh = int(BH * SCORE_ORIG * ease_out(vis))
    rh = int(BH * SCORE_OBFU * ease_out(vis))

    # Heading
    tcx(draw, "Reasoning Score", W // 2, BBASE - BH - 52,
        F["label"], fc(COL_T, vis))

    # Bars
    if oh > 4:
        rrect(draw, [BOX, BBASE - oh, BOX + BW, BBASE],
              r=10, fill=fc(BAR_B, vis))
    if rh > 4:
        rrect(draw, [BRX, BBASE - rh, BRX + BW, BBASE],
              r=10, fill=fc(BAR_P, vis))

    # Score labels
    if vis > 0.5:
        sv = min(1.0, (vis - 0.5) / 0.4)
        tcx(draw, f"{SCORE_ORIG:.2f}", BOX + BW // 2, BBASE - oh - 34,
            F["score"], fc(COL_T, sv))
        tcx(draw, f"{SCORE_OBFU:.2f}", BRX + BW // 2, BBASE - rh - 34,
            F["score"], fc(COL_T, sv))

    # Axis labels
    tcx(draw, "original",   BOX + BW // 2, BBASE + 8, F["tiny"], fc(COL_S, vis))
    tcx(draw, "obfuscated", BRX + BW // 2, BBASE + 8, F["tiny"], fc(COL_S, vis))

    # Delta arrow between bars (top of lower bar → top of lower bar, pointing down)
    # if vis > 0.65:
    #     dv = min(1.0, (vis - 0.65) / 0.3)
    #     mid_x = (BOX + BW + BRX) // 2
    #     y_orig = BBASE - oh
    #     y_obfu = BBASE - rh
    #     # Vertical arrow from orig-top down to obfu-top
    #     draw.line([(mid_x, y_orig + 4), (mid_x, y_obfu - 4)],
    #               fill=fc(BORD_P, dv), width=3)
        # Arrowhead pointing down
        # for dx_dy in ((-7, -10), (7, -10)):
        #     draw.line([(mid_x, y_obfu - 4),
        #                (mid_x + dx_dy[0], y_obfu - 4 + dx_dy[1])],
        #               fill=fc(BORD_P, dv), width=3)
        # Delta label
        # delta = SCORE_ORIG - SCORE_OBFU
        # tcx(draw, f"−{delta:.2f}", mid_x, (y_orig + y_obfu) // 2 - 12,
        #     F["tiny"], fc(BORD_P, dv))


# ── Per-frame renderer ─────────────────────────────────────────────────────────
def render(f):
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Phase schedule  ─────────────────────────────────────────── ← ADJUST
    # Phase 1: word fades in                 frames  0 – 42
    # Phase 2: letter scramble               frames 50 – 130
    # Phase 3: bars rise                     frames 138 – 175
    # Fade out                               frames 180 – 200

    p1_in    = phase(f,  0,  42)   # word appearance
    p_mean   = phase(f,  8,  42)   # meaning line lags slightly behind word
    p2_start = phase(f, 50, 130)   # overall scramble envelope
    p_fade   = phase(f, 138, 175)  # cards out / bars in
    p_out    = phase(f, 182, 200)  # fade to white

    # Cards visibility: present through scramble, gone for bars
    card_v    = (1.0 - p_fade) * p1_in
    meaning_v = (1.0 - p_fade) * max(p_mean, p1_in * 0.7)

    # BG pairs only in Phase 1
    bgpair_v = card_v * (1.0 - p2_start)
    draw_bg_pairs(draw, bgpair_v)

    # Build per-character display list
    word_chars = []
    for ci in range(len(ORIG_WORD)):
        orig_ch = ORIG_WORD[ci]
        obfu_ch = OBFU_WORD[ci] if ci < len(OBFU_WORD) else orig_ch
        ch, blend = scramble_char(ci, f, orig_ch, obfu_ch)
        word_chars.append((ch, blend))

    draw_word_phase(draw, word_chars, card_v, meaning_v)

    # Score bars
    draw_scores(draw, p_fade)

    # Fade to white
    if p_out > 0:
        img = Image.blend(img, Image.new("RGB", (W, H), BG), p_out)

    return img


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    out = "img/publications"
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "lingolytoo.webp")

    print(f"Rendering {N} frames ({W}×{H}, {FPS}fps, {SECS}s) …")
    frames = []
    for f in range(N):
        frames.append(render(f))
        if f % 40 == 0:
            print(f"  {f}/{N}")

    print("Saving animated WebP …")
    frames[0].save(
        path,
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=int(1000 / FPS),   # ms per frame
        lossless=True,              # crisp text rendering
    )
    print(f"Saved → {path}  ({os.path.getsize(path)/1024:.0f} KB)")

if __name__ == "__main__":
    main()