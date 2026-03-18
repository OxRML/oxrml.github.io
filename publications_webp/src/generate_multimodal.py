#publications_webp/src/generate_multimodal.py

"""
Paper Context:
This is a SYSTEMATIC REVIEW paper that:
- Reviews 50+ studies on multimodal ML in healthcare
- Covers imaging, text, time series, tabular data
- Key finding: effectiveness depends on specific data AND task

Visual Story:
Scene 1 (0-3.5s): Many small paper/study icons appear around edges
Scene 2 (3.5-6s): Papers flow into central "synthesis" circle → unified view
Scene 3 (6-8s): Four modality icons + "~task" indicator (effectiveness varies)

Frame and Scene timing Calculations:
Canvas: 720x450.
Frame calculation: FPS = 20, TOTAL = 10.0, N = int(FPS * TOTAL) = 200.
Scene timings: Scene 1 (0-3.5s) | Scene 2 (3.5-6s) | Scene 3 (6-8s).
"""

from PIL import Image, ImageDraw, ImageFont
import math, os, random

random.seed(42)

# ======
# CANVAS & TIMING
# ======
W, H = 720, 450
FPS = 20
TOTAL = 10.0
N = int(FPS * TOTAL)
OUT_PATH = "img/publications/multimodal.webp"

# ======
# PALETTE
# ======
BG = (255, 255, 255)
C_PAPER = (235, 238, 245)       # Study papers - light blue-gray
C_SYNTH = (255, 245, 225)       # Synthesis center - warm cream
C_IMAGE = (200, 220, 245)       # Imaging modality - blue
C_TEXT = (245, 220, 200)        # Text modality - peach
C_WAVE = (200, 235, 210)        # Time series - green
C_TABLE = (235, 210, 235)       # Tabular - purple
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

F_LG = get_font(30, True)
F_MD = get_font(24)
F_SM = get_font(20)

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
# STUDY PAPERS (scattered around edges)
# ======
# Generate 12 paper positions around the perimeter
papers = []
for i in range(12):
    angle = i * (2 * math.pi / 12) + random.uniform(-0.15, 0.15)
    r = 180 + random.uniform(-15, 15)
    x = 360 + r * math.cos(angle)
    y = 225 + r * math.sin(angle) * 0.75  # Elliptical
    papers.append((x, y, angle))

# ======
# DRAWING COMPONENTS
# ======

def draw_paper_icon(draw, x, y, size, alpha):
    """Small paper/study icon."""
    w, h = size, int(size * 1.3)
    x0, y0 = x - w//2, y - h//2
    fill = fbg(C_PAPER, alpha)
    outline = fbg(lc(C_PAPER, C_DARK, 0.25), alpha * 0.6)

    # Paper shape with folded corner
    draw.rectangle([x0, y0, x0+w, y0+h], fill=fill, outline=outline, width=1)
    # Folded corner
    corner_size = size // 4
    draw.polygon([(x0+w-corner_size, y0), (x0+w, y0+corner_size), (x0+w-corner_size, y0+corner_size)],
                fill=fbg(lc(C_PAPER, C_DARK, 0.1), alpha))
    # Lines
    if alpha > 0.4:
        line_col = fbg(C_MID, alpha * 0.3)
        for i in range(3):
            ly = y0 + 8 + i * 6
            draw.line([(x0+4, ly), (x0+w-6, ly)], fill=line_col, width=1)

def draw_synthesis_circle(draw, cx, cy, r, alpha, pulse=0.):
    """Central synthesis/review circle."""
    fill = fbg(C_SYNTH, alpha)
    outline = fbg(lc(C_SYNTH, C_DARK, 0.2), alpha)

    if pulse > 0.05:
        g = int(pulse * 15)
        draw.ellipse([cx-r-g, cy-r-g, cx+r+g, cy+r+g], fill=fbg(C_SYNTH, alpha * 0.3 * pulse))

    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=2)

def draw_modality_icon(draw, cx, cy, size, mod_type, alpha):
    """Draw one of 4 modality icons: image, text, wave, table."""
    s = size // 2

    if mod_type == "image":
        col = C_IMAGE
        fill = fbg(col, alpha)
        outline = fbg(lc(col, C_DARK, 0.25), alpha)
        draw.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=5, fill=fill, outline=outline, width=2)
        # Mountain
        if alpha > 0.4:
            m = fbg(lc(col, C_DARK, 0.3), alpha)
            draw.polygon([(cx-s+4, cy+s-4), (cx-4, cy-4), (cx+s-4, cy+s-4)], fill=m)

    elif mod_type == "text":
        col = C_TEXT
        fill = fbg(col, alpha)
        outline = fbg(lc(col, C_DARK, 0.25), alpha)
        draw.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=5, fill=fill, outline=outline, width=2)
        # Lines
        if alpha > 0.4:
            line_col = fbg(C_MID, alpha * 0.5)
            for i, w in enumerate([0.8, 0.6, 0.7]):
                ly = cy - s + 10 + i * 10
                draw.line([(cx-s+6, ly), (cx-s+6+int((size-12)*w), ly)], fill=line_col, width=2)

    elif mod_type == "wave":
        col = C_WAVE
        fill = fbg(col, alpha)
        outline = fbg(lc(col, C_DARK, 0.25), alpha)
        draw.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=5, fill=fill, outline=outline, width=2)
        # Wave
        if alpha > 0.4:
            wave_col = fbg((80, 150, 110), alpha)
            pts = [(cx-s+6, cy), (cx-s+12, cy-8), (cx, cy+10), (cx+s-12, cy-6), (cx+s-6, cy)]
            for i in range(len(pts)-1):
                draw.line([pts[i], pts[i+1]], fill=wave_col, width=2)

    elif mod_type == "table":
        col = C_TABLE
        fill = fbg(col, alpha)
        outline = fbg(lc(col, C_DARK, 0.25), alpha)
        draw.rounded_rectangle([cx-s, cy-s, cx+s, cy+s], radius=5, fill=fill, outline=outline, width=2)
        # Grid
        if alpha > 0.4:
            grid_col = fbg(C_MID, alpha * 0.4)
            # Vertical line
            draw.line([(cx, cy-s+5), (cx, cy+s-5)], fill=grid_col, width=1)
            # Horizontal line
            draw.line([(cx-s+5, cy), (cx+s-5, cy)], fill=grid_col, width=1)

# ======
# SCENE RENDERING
# ======

def render_frame(f):
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Scene timing with crossfades
    s1_a = (1 - ph(f, 3.0, 3.8)) * max(ph(f, 0.0, 0.5), 1 - ph(f, 7.5, 8.0))
    s2_a = ph(f, 3.2, 4.0) * (1 - ph(f, 5.5, 6.2))
    s3_a = ph(f, 5.8, 6.5) * (1 - ph(f, 7.5, 8.0))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 1: Many study papers appear around the edges
    # ════════════════════════════════════════════════════════════════════════

    if s1_a > 0.01:
        # Title
        title_a = ph(f, 0.3, 1.0) * s1_a
        if title_a > 0.3:
            tc(draw, 360, 50, "50+ studies reviewed", F_LG, fbg(C_MID, title_a))

        # Draw papers appearing one by one
        for i, (px, py, _) in enumerate(papers):
            p_a = ph(f, 0.3 + i*0.12, 0.9 + i*0.12) * s1_a
            if p_a > 0:
                draw_paper_icon(draw, px, py, 28, p_a)

        # "17 datasets" label
        ds_a = ph(f, 1.8, 2.5) * s1_a
        if ds_a > 0.3:
            tc(draw, 360, 225, "17 datasets", F_MD, fbg(C_LIGHT, ds_a))

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 2: Papers flow into central synthesis
    # ════════════════════════════════════════════════════════════════════════

    if s2_a > 0.01:
        # Central synthesis circle
        pulse = (math.sin(f / FPS * math.pi * 3) * 0.5 + 0.5) * s2_a
        draw_synthesis_circle(draw, 360, 225, 65, s2_a, pulse)

        # "Review" label in center
        if s2_a > 0.5:
            tc(draw, 360, 225, "Review", F_LG, fbg(C_DARK, s2_a * 0.8))

        # Papers moving toward center
        flow_prog = ph(f, 3.5, 5.0)
        for i, (px, py, _) in enumerate(papers):
            # Stagger the flow
            p_flow = max(0., min(1., (flow_prog - i*0.03) * 1.5))

            if p_flow < 1.0:
                curr_x = px + (360 - px) * p_flow
                curr_y = py + (225 - py) * p_flow
                curr_size = int(28 * (1 - p_flow * 0.7))
                curr_alpha = s2_a * (1 - p_flow * 0.8)
                if curr_alpha > 0.1 and curr_size > 8:
                    draw_paper_icon(draw, curr_x, curr_y, curr_size, curr_alpha)

    # ════════════════════════════════════════════════════════════════════════
    # SCENE 3: Four modalities + task-dependency indicator
    # ════════════════════════════════════════════════════════════════════════

    if s3_a > 0.01:
        # Title
        title_a = ph(f, 6.0, 6.6) * s3_a
        if title_a > 0.3:
            tc(draw, 360, 50, "Multimodal Fusion", F_LG, fbg(C_DARK, title_a))

        # Four modality icons in a row
        modalities = [
            (180, 180, "image"),
            (300, 180, "text"),
            (420, 180, "wave"),
            (540, 180, "table"),
        ]

        for i, (mx, my, mod_type) in enumerate(modalities):
            m_a = ph(f, 6.0 + i*0.15, 6.7 + i*0.15) * s3_a
            if m_a > 0:
                draw_modality_icon(draw, mx, my, 50, mod_type, m_a)

        # Fusion arrows pointing down
        arr_a = ph(f, 6.5, 7.0) * s3_a
        if arr_a > 0.3:
            arrow_col = fbg(C_LIGHT, arr_a)
            for mx, _, _ in modalities:
                draw.line([(mx, 210), (mx, 250)], fill=arrow_col, width=2)
            # Horizontal line connecting
            draw.line([(180, 260), (540, 260)], fill=arrow_col, width=2)
            # Down to output
            draw.line([(360, 260), (360, 300)], fill=arrow_col, width=2)
            draw.polygon([(355, 300), (365, 300), (360, 312)], fill=arrow_col)

        # Output box with "~task" indicating task dependency
        out_a = ph(f, 6.8, 7.3) * s3_a
        if out_a > 0.3:
            # Box
            fill = fbg((235, 245, 235), out_a)
            outline = fbg(C_LIGHT, out_a)
            draw.rounded_rectangle([300, 320, 420, 370], radius=8, fill=fill, outline=outline, width=2)

            # Checkmark (partial success)
            check_col = fbg((100, 170, 120), out_a)
            draw.line([(335, 345), (350, 358)], fill=check_col, width=3)
            draw.line([(350, 358), (375, 332)], fill=check_col, width=3)

        # "~task" indicator
        task_a = ph(f, 7.0, 7.4) * s3_a
        if task_a > 0.3:
            tc(draw, 360, 400, "Effectiveness varies by task", F_SM, fbg(C_MID, task_a))

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
