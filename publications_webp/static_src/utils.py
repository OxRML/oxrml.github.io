# publications_webp/static_src/utils.py
"""
Shared utilities for static publication image generation.
Minimal text, strong visual storytelling, crisp rendering.
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ======
# CANVAS
# ======
W, H = 720, 450
BG = (255, 255, 255)

# ======
# PALETTE (pastel, consistent with animations)
# ======
C_BLUE = (195, 220, 245)
C_PEACH = (250, 213, 190)
C_MINT = (200, 235, 210)
C_LAVENDER = (218, 205, 235)
C_CREAM = (255, 248, 230)
C_CORAL = (245, 195, 190)
C_GOLD = (255, 235, 180)
C_GRAY = (230, 230, 232)
C_TEAL = (195, 225, 225)

C_DARK = (55, 58, 75)
C_MID = (118, 122, 138)
C_LIGHT = (170, 175, 188)

# Semantic colors
C_POS = (175, 215, 190)  # green - positive/success
C_NEG = (235, 185, 185)  # red - negative/error

# ======
# FONTS - Large, crisp text
# ======
FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "C:/Windows/Fonts/arial.ttf",
]
FONT_PATHS_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
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

# Standard font sizes - LARGE for readability
F_TITLE = get_font(32, True)   # Main labels only
F_LABEL = get_font(26, True)   # Secondary labels
F_SMALL = get_font(20)         # Minimal use
F_SYMBOL = get_font(42, True)  # Symbols like ≠, ✓, ✗

# ======
# COLOR UTILITIES
# ======
def lc(c1, c2, t):
    """Linear interpolate between two colors."""
    t = max(0., min(1., t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))

def darken(col, amount=0.2):
    return lc(col, (0, 0, 0), amount)

def lighten(col, amount=0.3):
    return lc(col, (255, 255, 255), amount)

# ======
# DRAWING UTILITIES
# ======
def tc(draw, cx, cy, text, font, fill):
    """Draw centered text."""
    bb = draw.textbbox((0, 0), text, font=font)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    draw.text((int(cx - tw/2), int(cy - th/2)), text, font=font, fill=fill)
    return (cx - tw//2, cy - th//2, cx + tw//2, cy + th//2)  # Return bbox

def rrect(draw, xy, r, fill=None, outline=None, width=2):
    """Draw rounded rectangle."""
    try:
        draw.rounded_rectangle(xy, radius=r, fill=fill, outline=outline, width=width)
    except AttributeError:
        draw.rectangle(xy, fill=fill, outline=outline, width=width)

def draw_arrow(draw, x1, y1, x2, y2, col, width=3, head=12):
    """Draw arrow with proper head."""
    import math
    draw.line([(x1, y1), (x2, y2)], fill=col, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    draw.polygon([
        (x2, y2),
        (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4)),
        (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4)),
    ], fill=col)

def draw_circle(draw, cx, cy, r, fill, outline=None, width=2):
    """Draw filled circle."""
    if outline is None:
        outline = darken(fill, 0.15)
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fill, outline=outline, width=width)

def draw_box(draw, cx, cy, w, h, fill, r=10, outline=None, width=2):
    """Draw rounded box."""
    if outline is None:
        outline = darken(fill, 0.15)
    rrect(draw, [cx-w//2, cy-h//2, cx+w//2, cy+h//2], r=r, fill=fill, outline=outline, width=width)

def draw_bar(draw, cx, bot_y, w, h, fill, frac=1.0):
    """Draw vertical bar (no label - minimal text)."""
    # Track
    track_col = lighten(fill, 0.6)
    rrect(draw, [cx - w//2, bot_y - h, cx + w//2, bot_y], r=6, fill=track_col)

    # Fill
    fh = int(h * frac)
    if fh > 6:
        rrect(draw, [cx - w//2, bot_y - fh, cx + w//2, bot_y], r=6, fill=fill)

def new_image():
    """Create new blank image."""
    return Image.new("RGB", (W, H), BG)

def self_review(img):
    """Check for edge clipping - content should not touch edges."""
    issues = []
    margin = 8

    for y in range(H):
        for x in range(W):
            if x < margin or x >= W - margin or y < margin or y >= H - margin:
                px = img.getpixel((x, y))
                if abs(px[0] - 255) + abs(px[1] - 255) + abs(px[2] - 255) > 30:
                    issues.append((x, y))
                    if len(issues) > 5:
                        return False, issues

    return len(issues) == 0, issues

def save_image(img, name):
    """Save image with quality check."""
    out_path = f"img/publications/static/{name}.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Self-review
    ok, issues = self_review(img)
    if not ok:
        print(f"  Warning: {name} has edge clipping at {issues[:3]}...")

    img.save(out_path, "PNG")
    print(f"{'✓' if ok else '⚠'} {name}.png")
    return out_path
