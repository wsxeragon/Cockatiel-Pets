import os
from PIL import Image, ImageDraw

BASE_DIR = r"D:\pets"
POSES_DIR = os.path.join(BASE_DIR, "2d", "official_poses")

# Load poses
def load_clean_pose(filename):
    p = os.path.join(POSES_DIR, filename)
    im = Image.open(p).convert("RGBA")
    w, h = im.size
    visited = set()
    components = []
    fg = set()
    for y in range(h):
        for x in range(w):
            if im.getpixel((x, y))[3] > 20:
                fg.add((x, y))
    for pt in fg:
        if pt in visited: continue
        comp = []
        q = [pt]
        visited.add(pt)
        while q:
            cx, cy = q.pop()
            comp.append((cx, cy))
            for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (1,1), (-1,1), (1,-1)]:
                nx, ny = cx + dx, cy + dy
                if (nx, ny) in fg and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    q.append((nx, ny))
        components.append(comp)
    keep = set()
    for c in components:
        if len(c) >= 300:
            keep.update(c)
    cleaned = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for pt in keep:
        cleaned.putpixel(pt, im.getpixel(pt))
    return cleaned.transpose(Image.Transpose.FLIP_LEFT_RIGHT)

alert_base = load_clean_pose("06_alert_警觉.png")
fly_base = load_clean_pose("08_flying_飞行.png")
hiss_base = load_clean_pose("07_hissing_哈气.png")

# Palette
C_DARK = (28, 24, 26, 255)
C_BEAK = (175, 140, 130, 255)
C_BEAK_LIGHT = (205, 175, 165, 255)
C_MOUTH_DARK = (25, 15, 20, 255)
C_TONGUE = (220, 115, 120, 255)
C_YELLOW = (248, 230, 84, 255)

# --- Test 1: Beak Open Variations on Alert Base ---
# In alert_base (width 173, height 219):
# The beak hook is at x in [0, 30], y in [70, 95]
# Let's verify coordinates in alert_base:
for y in range(70, 95, 5):
    xs = [x for x in range(alert_base.width) if alert_base.getpixel((x, y))[3] > 50]
    print(f'alert_base y={y}: min_x={min(xs)}')
