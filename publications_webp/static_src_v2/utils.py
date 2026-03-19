from PIL import Image, ImageDraw, ImageFont
import math
import os

W, H = 720, 450
BG = (255, 255, 255)

C_BLUE = (198, 220, 246)
C_PEACH = (248, 221, 205)
C_MINT = (204, 234, 214)
C_LAVENDER = (224, 212, 239)
C_CREAM = (255, 247, 230)
C_CORAL = (243, 205, 196)
C_GOLD = (251, 232, 182)
C_GRAY = (231, 232, 236)
C_TEAL = (205, 232, 231)

C_DARK = (55, 58, 75)
C_MID = (120, 124, 140)
C_LIGHT = (175, 179, 192)
C_POS = (150, 200, 165)
C_NEG = (223, 162, 162)

PALETTE = {
    "blue": C_BLUE,
    "peach": C_PEACH,
    "mint": C_MINT,
    "lavender": C_LAVENDER,
    "cream": C_CREAM,
    "coral": C_CORAL,
    "gold": C_GOLD,
    "gray": C_GRAY,
    "teal": C_TEAL,
}

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
    for path in paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


F_TEXT = get_font(24, True)
F_LABEL = F_TEXT
F_NOTE = F_TEXT
F_BIG = F_TEXT
F_SYMBOL = get_font(34, True)


def mix(c1, c2, t):
    t = max(0.0, min(1.0, t))
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def lighten(col, amount=0.35):
    return mix(col, BG, amount)


def darken(col, amount=0.2):
    return mix(col, (0, 0, 0), amount)


def new_image():
    return Image.new("RGB", (W, H), BG)


def centered_text(draw, cx, cy, text, font=F_LABEL, fill=C_DARK):
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    draw.text((int(cx - tw / 2), int(cy - th / 2)), text, font=font, fill=fill)


def left_text(draw, x, cy, text, font=F_LABEL, fill=C_DARK):
    bb = draw.textbbox((0, 0), text, font=font)
    th = bb[3] - bb[1]
    draw.text((int(x), int(cy - th / 2)), text, font=font, fill=fill)


def right_text(draw, x, cy, text, font=F_LABEL, fill=C_DARK):
    bb = draw.textbbox((0, 0), text, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    draw.text((int(x - tw), int(cy - th / 2)), text, font=font, fill=fill)


def rounded_box(draw, cx, cy, w, h, fill, radius=18, outline=None, width=2):
    if outline is None:
        outline = darken(fill, 0.15)
    draw.rounded_rectangle(
        [cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2],
        radius=radius,
        fill=fill,
        outline=outline,
        width=width,
    )


def circle(draw, cx, cy, r, fill, outline=None, width=2):
    if outline is None:
        outline = darken(fill, 0.15)
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=outline, width=width)


def arrow(draw, x1, y1, x2, y2, col=C_LIGHT, width=3, head=12):
    draw.line([(x1, y1), (x2, y2)], fill=col, width=width)
    ang = math.atan2(y2 - y1, x2 - x1)
    draw.polygon(
        [
            (x2, y2),
            (x2 - head * math.cos(ang - 0.38), y2 - head * math.sin(ang - 0.38)),
            (x2 - head * math.cos(ang + 0.38), y2 - head * math.sin(ang + 0.38)),
        ],
        fill=col,
    )


def draw_bar(draw, cx, base_y, w, h, frac, fill):
    track = lighten(fill, 0.7)
    rounded_box(draw, cx, base_y - h // 2, w, h, track, radius=8, outline=track, width=1)
    fh = max(8, int(h * frac))
    y0 = base_y - fh
    draw.rounded_rectangle(
        [cx - w // 2, y0, cx + w // 2, base_y],
        radius=8,
        fill=fill,
        outline=darken(fill, 0.12),
        width=2,
    )


def wave_points(x0, x1, cy, amp, cycles=2.0, steps=42):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = x0 + (x1 - x0) * t
        y = cy + math.sin(t * math.pi * 2 * cycles) * amp * (0.55 + 0.45 * math.sin(t * math.pi))
        pts.append((x, y))
    return pts


def draw_wave(draw, x0, x1, cy, amp, col, width=3, cycles=2.0):
    pts = wave_points(x0, x1, cy, amp, cycles=cycles)
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=col, width=width)


def draw_paper(draw, cx, cy, w, h, fill=C_CREAM, lines=3):
    x0 = cx - w // 2
    y0 = cy - h // 2
    x1 = cx + w // 2
    y1 = cy + h // 2
    draw.rectangle([x0, y0, x1, y1], fill=fill, outline=darken(fill, 0.15), width=2)
    fold = min(18, w // 5)
    draw.polygon([(x1 - fold, y0), (x1, y0), (x1, y0 + fold)], fill=lighten(fill, 0.1))
    ink = darken(fill, 0.32)
    for i in range(lines):
        ly = y0 + 14 + i * 12
        draw.line([(x0 + 10, ly), (x1 - 12 - (i % 2) * 18, ly)], fill=ink, width=2)


def draw_doc(draw, cx, cy, w, h, fill, lines=5):
    rounded_box(draw, cx, cy, w, h, fill, radius=12)
    ink = darken(fill, 0.32)
    top = cy - h // 2 + 18
    for i in range(lines):
        ly = top + i * ((h - 34) // max(1, lines - 1))
        draw.line([(cx - w // 2 + 16, ly), (cx + w // 2 - 22 - (i % 2) * 18, ly)], fill=ink, width=2)


def draw_chip(draw, cx, cy, w, h, fill):
    rounded_box(draw, cx, cy, w, h, fill, radius=16)
    dot = darken(fill, 0.3)
    for dx, dy in [(-18, -10), (0, -10), (18, -10), (-9, 10), (9, 10)]:
        circle(draw, cx + dx, cy + dy, 4, dot, outline=dot, width=1)


def draw_speech(draw, cx, cy, w, h, fill):
    rounded_box(draw, cx, cy, w, h, fill, radius=14)
    draw.polygon([(cx - 12, cy + h // 2 - 2), (cx + 4, cy + h // 2 - 2), (cx - 4, cy + h // 2 + 16)], fill=fill)


def draw_person(draw, cx, cy, fill=C_PEACH):
    circle(draw, cx, cy - 26, 16, fill)
    draw.arc([cx - 24, cy - 6, cx + 24, cy + 42], 0, 180, fill=darken(fill, 0.18), width=3)


def draw_check(draw, cx, cy, size=16, col=C_POS):
    draw.line([(cx - size, cy), (cx - size // 3, cy + size)], fill=col, width=4)
    draw.line([(cx - size // 3, cy + size), (cx + size, cy - size)], fill=col, width=4)


def draw_cross(draw, cx, cy, size=14, col=C_NEG):
    draw.line([(cx - size, cy - size), (cx + size, cy + size)], fill=col, width=4)
    draw.line([(cx + size, cy - size), (cx - size, cy + size)], fill=col, width=4)


def draw_spark(draw, cx, cy, r, fill):
    circle(draw, cx, cy, r, fill)
    for ang in [0, math.pi / 2, math.pi, 3 * math.pi / 2]:
        x0 = cx + math.cos(ang) * (r + 4)
        y0 = cy + math.sin(ang) * (r + 4)
        x1 = cx + math.cos(ang) * (r + 14)
        y1 = cy + math.sin(ang) * (r + 14)
        draw.line([(x0, y0), (x1, y1)], fill=darken(fill, 0.2), width=3)


def draw_matrix(draw, x0, y0, cell, values):
    for row_idx, row in enumerate(values):
        for col_idx, value in enumerate(row):
            fill = mix(BG, C_GOLD, 0.25 + value * 0.55)
            draw.rectangle(
                [
                    x0 + col_idx * cell,
                    y0 + row_idx * cell,
                    x0 + (col_idx + 1) * cell,
                    y0 + (row_idx + 1) * cell,
                ],
                fill=fill,
                outline=lighten(C_LIGHT, 0.2),
                width=1,
            )


def self_review(img):
    margin = 8
    for y in range(H):
        for x in range(W):
            if x < margin or x >= W - margin or y < margin or y >= H - margin:
                px = img.getpixel((x, y))
                if sum(abs(v - 255) for v in px) > 30:
                    return False
    return True


def save_image(img, name):
    out_path = f"img/publications/static/{name}.png"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    ok = self_review(img)
    if not ok:
        print(f"warning: edge content in {name}.png")
    img.save(out_path, "PNG")
    print(f"{'ok' if ok else 'warn'} {name}.png")
    return out_path
