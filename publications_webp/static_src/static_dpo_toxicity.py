# publications_webp/static_src/static_dpo_toxicity.py
"""
DPO: Not just toxic neurons (2.5-24%), but 4 distributed neuron groups.
Visual: Single red neurons (X) vs 4 colored groups with arrows (✓).
Minimal text: just X and ✓ marks.
"""

import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils import *

def generate():
    img = new_image()
    draw = ImageDraw.Draw(img)

    # === LEFT: Old theory - few toxic neurons ===
    old_cx = 170
    old_cy = 225

    # Simple neural network with few red neurons
    layers = [
        [(old_cx - 50, 130), (old_cx - 50, 180), (old_cx - 50, 230), (old_cx - 50, 280), (old_cx - 50, 330)],
        [(old_cx, 155), (old_cx, 205), (old_cx, 255), (old_cx, 305)],
        [(old_cx + 50, 180), (old_cx + 50, 230), (old_cx + 50, 280)],
    ]

    toxic_positions = {(0, 1), (1, 2)}  # Only 2 red neurons

    # Draw connections first (faint)
    for li in range(len(layers) - 1):
        for n1 in layers[li]:
            for n2 in layers[li + 1]:
                draw.line([n1, n2], fill=lighten(C_LIGHT, 0.4), width=1)

    # Draw neurons
    for li, layer in enumerate(layers):
        for ni, (nx, ny) in enumerate(layer):
            if (li, ni) in toxic_positions:
                draw_circle(draw, nx, ny, 14, C_CORAL)
            else:
                draw_circle(draw, nx, ny, 14, C_GRAY)

    # X mark below
    x_cx, x_cy = old_cx, 380
    x_size = 20
    draw.line([(x_cx - x_size, x_cy - x_size), (x_cx + x_size, x_cy + x_size)], fill=C_NEG, width=5)
    draw.line([(x_cx + x_size, x_cy - x_size), (x_cx - x_size, x_cy + x_size)], fill=C_NEG, width=5)

    # === ARROW between ===
    draw_arrow(draw, 280, 225, 360, 225, C_MID, width=4, head=14)

    # === RIGHT: Our finding - 4 neuron groups ===
    new_cx = 530
    group_colors = [C_CORAL, C_PEACH, C_MINT, C_TEAL]

    # 2x2 grid of neuron groups
    positions = [
        (new_cx - 70, 150),  # top-left
        (new_cx + 70, 150),  # top-right
        (new_cx - 70, 300),  # bottom-left
        (new_cx + 70, 300),  # bottom-right
    ]

    for i, ((gx, gy), col) in enumerate(zip(positions, group_colors)):
        # Group circle
        draw_circle(draw, gx, gy, 55, lighten(col, 0.3), outline=darken(col, 0.1), width=3)

        # Neurons inside group
        for dx, dy in [(-15, -15), (15, -10), (-10, 12), (12, 15), (0, 0)]:
            draw_circle(draw, gx + dx, gy + dy, 10, col)

        # Arrow showing direction (up for anti-toxic, down for toxic reduction)
        arr_col = darken(col, 0.3)
        if i < 2:  # Top row - down arrows (reduce toxicity)
            draw.line([(gx, gy + 60), (gx, gy + 85)], fill=arr_col, width=4)
            draw.polygon([(gx - 8, gy + 78), (gx + 8, gy + 78), (gx, gy + 92)], fill=arr_col)
        else:  # Bottom row - up arrows (promote anti-toxicity)
            draw.line([(gx, gy - 60), (gx, gy - 85)], fill=arr_col, width=4)
            draw.polygon([(gx - 8, gy - 78), (gx + 8, gy - 78), (gx, gy - 92)], fill=arr_col)

    # Checkmark below
    check_x, check_y = new_cx, 395
    draw.line([(check_x - 15, check_y), (check_x - 4, check_y + 18)], fill=darken(C_POS, 0.2), width=5)
    draw.line([(check_x - 4, check_y + 18), (check_x + 20, check_y - 12)], fill=darken(C_POS, 0.2), width=5)

    return save_image(img, "dpo_toxicity")

if __name__ == "__main__":
    generate()
