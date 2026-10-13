"""Test script to procedurally draw the 3-piece comic sound burst wedges.
Based on user-uploaded reference media_1791854860602_20ba83b3.png.
"""
from PIL import Image, ImageDraw
from pathlib import Path

OUT_DIR = Path(r"D:\pets\test_bonk")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Color palette matching user's image:
# Outer: bright warm yellow (#ffcc00 / #ffd200)
# Inner: warm orange (#ff9900 / #ffa000)
# Optional pixel outline: dark ink (#353438) for contrast on any background
C_BURST_OUTER = "#fed000"
C_BURST_INNER = "#ff9a00"
C_BURST_INK = "#353438"

def draw_sound_burst(
    im,
    origin=(42, 22),
    scale=1.0,
    with_ink_outline=True,
    progress=1.0  # 0.0 to 1.0 (growth/fade)
):
    """Draw the 3 radiating wedge shockwave marks procedurally."""
    im = im.copy()
    d = ImageDraw.Draw(im)
    ox, oy = origin

    # Define the 3 wedge polygons relative to origin (ox, oy)
    # Scaled to fit comfortably on 100x80 canvas (around 22x22 area)
    
    # 1. TOP WEDGE (vertical, slightly tilted left)
    # Radiates towards top-left
    top_poly_outer = [
        (ox - 7 * scale, oy - 6 * scale),   # bottom-left narrow
        (ox - 3 * scale, oy - 7 * scale),   # bottom-right narrow
        (ox - 1 * scale, oy - 17 * scale),  # top-right wide
        (ox - 6 * scale, oy - 19 * scale),  # top-left wide
    ]
    top_poly_inner = [
        (ox - 6 * scale, oy - 8 * scale),
        (ox - 4 * scale, oy - 8 * scale),
        (ox - 2 * scale, oy - 16 * scale),
        (ox - 5 * scale, oy - 17 * scale),
    ]

    # 2. MIDDLE WEDGE (longest, diagonal towards top-right)
    mid_poly_outer = [
        (ox - 1 * scale, oy - 3 * scale),   # bottom-left narrow
        (ox + 2 * scale, oy - 7 * scale),   # top-left narrow
        (ox + 16 * scale, oy - 13 * scale), # top-right wide
        (ox + 18 * scale, oy - 7 * scale),  # right tip
        (ox + 13 * scale, oy - 3 * scale),  # bottom-right
    ]
    mid_poly_inner = [
        (ox + 1 * scale, oy - 4 * scale),
        (ox + 3 * scale, oy - 6 * scale),
        (ox + 14 * scale, oy - 11 * scale),
        (ox + 15 * scale, oy - 7 * scale),
        (ox + 11 * scale, oy - 4 * scale),
    ]

    # 3. BOTTOM WEDGE (shallow / horizontal towards bottom-right)
    bot_poly_outer = [
        (ox + 3 * scale, oy + 1 * scale),   # top-left narrow
        (ox + 4 * scale, oy + 5 * scale),   # bottom-left narrow
        (ox + 14 * scale, oy + 7 * scale),  # bottom-right wide
        (ox + 15 * scale, oy + 1 * scale),  # top-right wide
    ]
    bot_poly_inner = [
        (ox + 4 * scale, oy + 2 * scale),
        (ox + 5 * scale, oy + 4 * scale),
        (ox + 13 * scale, oy + 5 * scale),
        (ox + 13 * scale, oy + 2 * scale),
    ]

    wedges = [
        (top_poly_outer, top_poly_inner),
        (mid_poly_outer, mid_poly_inner),
        (bot_poly_outer, bot_poly_inner)
    ]

    for outer, inner in wedges:
        # Round coords to integers
        outer_pts = [(round(x), round(y)) for x, y in outer]
        inner_pts = [(round(x), round(y)) for x, y in inner]

        if with_ink_outline:
            # Draw ink border 1px around
            # Simple approach: draw slightly expanded polygon
            d.polygon(outer_pts, fill=C_BURST_INK, outline=C_BURST_INK)
            # Inset by 1px for yellow
            d.polygon(outer_pts, fill=C_BURST_OUTER)
            d.polygon(inner_pts, fill=C_BURST_INNER)
        else:
            d.polygon(outer_pts, fill=C_BURST_OUTER)
            d.polygon(inner_pts, fill=C_BURST_INNER)

    return im

# Test drawing just the burst icon at 10x scale to inspect pixel precision
canvas = Image.new("RGBA", (80, 80), (255, 255, 255, 0))
drawn = draw_sound_burst(canvas, origin=(35, 45), scale=1.8, with_ink_outline=False)
drawn_with_ink = draw_sound_burst(canvas, origin=(35, 45), scale=1.8, with_ink_outline=True)

drawn.save(OUT_DIR / "burst_raw.png")
drawn_with_ink.save(OUT_DIR / "burst_with_ink.png")
print("Saved raw burst tests.")
