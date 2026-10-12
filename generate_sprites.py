import os
from PIL import Image, ImageDraw

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "sprites")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Color Palette for Normal Grey Cockatiel (原始灰玄凤)
C_TRANS = (0, 0, 0, 0)
C_OUTLINE = (35, 35, 38, 255)
C_GREY_BODY = (120, 122, 125, 255)
C_GREY_LIGHT = (150, 153, 156, 255)
C_GREY_DARK = (80, 82, 85, 255)
C_WING_WHITE = (248, 248, 250, 255)
C_YELLOW_HEAD = (255, 225, 60, 255)
C_YELLOW_LIGHT = (255, 240, 110, 255)
C_CHEEK_ORANGE = (255, 80, 25, 255)
C_CREST_YELLOW = (255, 215, 35, 255)
C_BEAK = (65, 65, 70, 255)
C_BEAK_LIGHT = (90, 90, 95, 255)
C_EYE = (20, 20, 20, 255)
C_EYE_SHINE = (255, 255, 255, 255)
C_FEET = (220, 165, 155, 255)
C_NOTE_BLUE = (80, 190, 255, 255)
C_CRUMB = (180, 150, 110, 255)

def create_base_canvas():
    return Image.new("RGBA", (64, 64), C_TRANS)

def draw_cockatiel(
    crest_mode="normal",    # "normal", "alert", "low", "heart", "sing"
    eye_mode="open",        # "open", "blink", "squint", "closed", "shock"
    beak_mode="closed",     # "closed", "peck", "sing", "bite", "hiss", "chew"
    body_shape="normal",    # "normal", "waddle_left", "waddle_right", "fluff", "alert_thin", "hop", "bow"
    wing_mode="normal",     # "normal", "heart", "open_up", "open_down", "preen"
    bob_offset=(0, 0),      # (dx, dy)
    has_crumb=False,
    has_note=False
):
    img = create_base_canvas()
    draw = ImageDraw.Draw(img)

    bx, by = 26 + bob_offset[0], 36 + bob_offset[1]

    # --- FEET ---
    if body_shape == "hop":
        # Feet tucked up
        draw.rectangle([bx - 6, by + 16, bx - 3, by + 19], fill=C_FEET, outline=C_OUTLINE)
        draw.rectangle([bx + 4, by + 16, bx + 7, by + 19], fill=C_FEET, outline=C_OUTLINE)
    elif body_shape == "waddle_left":
        draw.rectangle([bx - 8, by + 19, bx - 3, by + 22], fill=C_FEET, outline=C_OUTLINE)
        draw.rectangle([bx + 4, by + 17, bx + 8, by + 20], fill=C_FEET, outline=C_OUTLINE)
    elif body_shape == "waddle_right":
        draw.rectangle([bx - 6, by + 17, bx - 2, by + 20], fill=C_FEET, outline=C_OUTLINE)
        draw.rectangle([bx + 5, by + 19, bx + 10, by + 22], fill=C_FEET, outline=C_OUTLINE)
    else:
        draw.rectangle([bx - 7, by + 19, bx - 2, by + 22], fill=C_FEET, outline=C_OUTLINE)
        draw.rectangle([bx + 3, by + 19, bx + 8, by + 22], fill=C_FEET, outline=C_OUTLINE)

    # --- TAIL FEATHERS ---
    if wing_mode in ["open_up", "open_down"]:
        # Spread tail
        draw.polygon([(bx - 4, by + 12), (bx - 14, by + 25), (bx - 2, by + 24)], fill=C_GREY_DARK, outline=C_OUTLINE)
    elif body_shape == "alert_thin":
        draw.polygon([(bx - 3, by + 12), (bx - 7, by + 27), (bx + 1, by + 25)], fill=C_GREY_DARK, outline=C_OUTLINE)
    else:
        draw.polygon([(bx - 4, by + 12), (bx - 12, by + 26), (bx - 1, by + 23)], fill=C_GREY_DARK, outline=C_OUTLINE)

    # --- BODY ---
    if body_shape == "fluff":
        # Round fluffy ball
        draw.ellipse([bx - 17, by - 6, bx + 16, by + 18], fill=C_GREY_BODY, outline=C_OUTLINE)
        draw.ellipse([bx - 14, by - 3, bx + 10, by + 15], fill=C_GREY_LIGHT)
    elif body_shape == "alert_thin":
        # Stretched stick
        draw.rounded_rectangle([bx - 9, by - 12, bx + 8, by + 18], radius=6, fill=C_GREY_BODY, outline=C_OUTLINE)
    elif body_shape == "bow":
        # Lowered body
        draw.ellipse([bx - 14, by - 2, bx + 13, by + 18], fill=C_GREY_BODY, outline=C_OUTLINE)
    else:
        # Standard pear shape body
        draw.ellipse([bx - 13, by - 7, bx + 13, by + 18], fill=C_GREY_BODY, outline=C_OUTLINE)
        draw.ellipse([bx - 10, by - 4, bx + 8, by + 14], fill=C_GREY_LIGHT)

    # --- WINGS ---
    if wing_mode == "heart":
        # Heart Wings (drooping, curved outward)
        draw.polygon([(bx - 14, by - 4), (bx - 22, by + 8), (bx - 12, by + 14)], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.polygon([(bx - 19, by + 1), (bx - 14, by + 10), (bx - 15, by + 3)], fill=C_WING_WHITE)
        draw.polygon([(bx + 8, by - 4), (bx + 18, by + 8), (bx + 10, by + 14)], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.polygon([(bx + 14, by + 1), (bx + 11, by + 10), (bx + 12, by + 3)], fill=C_WING_WHITE)
    elif wing_mode == "open_up":
        # Flying up
        draw.polygon([(bx - 10, by - 4), (bx - 25, by - 18), (bx - 6, by + 4)], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.polygon([(bx - 20, by - 12), (bx - 9, by - 1), (bx - 16, by - 3)], fill=C_WING_WHITE)
        draw.polygon([(bx + 6, by - 4), (bx + 23, by - 18), (bx + 8, by + 4)], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.polygon([(bx + 18, by - 12), (bx + 9, by - 1), (bx + 15, by - 3)], fill=C_WING_WHITE)
    elif wing_mode == "open_down":
        # Flying down
        draw.polygon([(bx - 10, by - 2), (bx - 24, by + 16), (bx - 5, by + 8)], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.polygon([(bx - 19, by + 8), (bx - 7, by + 5), (bx - 14, by + 12)], fill=C_WING_WHITE)
        draw.polygon([(bx + 8, by - 2), (bx + 22, by + 16), (bx + 6, by + 8)], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.polygon([(bx + 17, by + 8), (bx + 7, by + 5), (bx + 13, by + 12)], fill=C_WING_WHITE)
    elif wing_mode == "preen":
        # Wing pulled aside for preening
        draw.ellipse([bx - 13, by - 2, bx - 1, by + 14], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.rectangle([bx - 10, by + 1, bx - 5, by + 10], fill=C_WING_WHITE)
    else:
        # Normal folded wing with classic white wing bar
        draw.ellipse([bx - 12, by - 4, bx + 1, by + 15], fill=C_GREY_DARK, outline=C_OUTLINE)
        draw.polygon([(bx - 10, by - 1), (bx - 3, by + 3), (bx - 6, by + 12), (bx - 9, by + 8)], fill=C_WING_WHITE)

    # --- HEAD ---
    hx = bx + 2
    if body_shape == "bow":
        hy = by + 2  # Lowered head
    elif body_shape == "alert_thin":
        hy = by - 18 # High stretched head
    else:
        hy = by - 13 # Normal head

    # Head circle
    draw.ellipse([hx - 10, hy - 9, hx + 10, hy + 9], fill=C_YELLOW_HEAD, outline=C_OUTLINE)
    draw.ellipse([hx - 7, hy - 7, hx + 5, hy + 6], fill=C_YELLOW_LIGHT)

    # --- CHEEK PATCH (腮红) ---
    draw.ellipse([hx - 3, hy + 1, hx + 6, hy + 8], fill=C_CHEEK_ORANGE)

    # --- CREST (冠羽) ---
    if crest_mode == "alert":
        # Straight vertical high crest
        draw.polygon([(hx - 2, hy - 8), (hx + 1, hy - 26), (hx + 5, hy - 24), (hx + 2, hy - 8)], fill=C_CREST_YELLOW, outline=C_OUTLINE)
        draw.polygon([(hx - 4, hy - 8), (hx - 1, hy - 21), (hx + 1, hy - 20), (hx - 1, hy - 8)], fill=C_CREST_YELLOW)
    elif crest_mode == "low":
        # Relaxed / flattened back crest
        draw.polygon([(hx - 3, hy - 8), (hx - 15, hy - 13), (hx - 12, hy - 16), (hx + 1, hy - 8)], fill=C_CREST_YELLOW, outline=C_OUTLINE)
    elif crest_mode == "heart" or crest_mode == "sing":
        # Sassy curved forward crest
        draw.polygon([(hx - 1, hy - 8), (hx + 9, hy - 21), (hx + 13, hy - 17), (hx + 3, hy - 8)], fill=C_CREST_YELLOW, outline=C_OUTLINE)
    else:
        # Normal 45-degree cockatiel crest
        draw.polygon([(hx - 1, hy - 8), (hx + 5, hy - 20), (hx + 9, hy - 17), (hx + 3, hy - 8)], fill=C_CREST_YELLOW, outline=C_OUTLINE)
        draw.polygon([(hx - 3, hy - 8), (hx + 1, hy - 17), (hx + 5, hy - 15), (hx + 0, hy - 8)], fill=C_CREST_YELLOW)

    # --- EYE ---
    ex, ey = hx + 2, hy - 2
    if eye_mode == "blink" or eye_mode == "closed":
        # Curved line for happy closed eye ^_^
        draw.line([(ex - 2, ey + 1), (ex, ey - 1), (ex + 2, ey + 1)], fill=C_EYE, width=2)
    elif eye_mode == "squint":
        # Half open sleepy eye
        draw.line([(ex - 2, ey), (ex + 2, ey)], fill=C_EYE, width=2)
    elif eye_mode == "shock":
        # Huge round startled eye
        draw.ellipse([ex - 3, ey - 3, ex + 3, ey + 3], fill=C_EYE, outline=C_OUTLINE)
        draw.point((ex - 1, ey - 1), fill=C_EYE_SHINE)
    else:
        # Normal friendly round eye
        draw.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=C_EYE)
        draw.point((ex, ey - 1), fill=C_EYE_SHINE)

    # --- BEAK ---
    bx_beak, by_beak = hx + 8, hy + 2
    if beak_mode == "peck":
        draw.polygon([(bx_beak, by_beak), (bx_beak + 5, by_beak + 6), (bx_beak - 1, by_beak + 4)], fill=C_BEAK, outline=C_OUTLINE)
    elif beak_mode == "sing":
        draw.polygon([(bx_beak - 1, by_beak - 1), (bx_beak + 6, by_beak - 2), (bx_beak + 2, by_beak + 1)], fill=C_BEAK, outline=C_OUTLINE)
        draw.polygon([(bx_beak - 1, by_beak + 2), (bx_beak + 5, by_beak + 4), (bx_beak + 1, by_beak + 1)], fill=C_BEAK, outline=C_OUTLINE)
    elif beak_mode == "bite" or beak_mode == "hiss":
        # Open wide threatening beak
        draw.polygon([(bx_beak - 1, by_beak - 2), (bx_beak + 7, by_beak - 4), (bx_beak + 2, by_beak)], fill=C_BEAK, outline=C_OUTLINE)
        draw.polygon([(bx_beak - 1, by_beak + 3), (bx_beak + 6, by_beak + 5), (bx_beak + 2, by_beak + 1)], fill=C_BEAK, outline=C_OUTLINE)
        draw.ellipse([bx_beak, by_beak, bx_beak + 3, by_beak + 2], fill=(220, 60, 60, 255)) # pink mouth interior
    elif beak_mode == "chew":
        # Nibbling slightly open beak
        draw.polygon([(bx_beak, by_beak - 1), (bx_beak + 5, by_beak), (bx_beak, by_beak + 2)], fill=C_BEAK, outline=C_OUTLINE)
    else:
        # Standard hooked parrot beak
        draw.polygon([(bx_beak - 1, by_beak - 1), (bx_beak + 5, by_beak + 1), (bx_beak + 2, by_beak + 4), (bx_beak - 1, by_beak + 3)], fill=C_BEAK, outline=C_OUTLINE)

    # --- SPECIAL FX (Crumbs, Notes) ---
    if has_crumb:
        # Bits of chewed items flying
        draw.rectangle([bx_beak + 7, by_beak - 3, bx_beak + 9, by_beak - 1], fill=C_CRUMB)
        draw.rectangle([bx_beak + 9, by_beak + 4, bx_beak + 11, by_beak + 6], fill=C_CRUMB)
        draw.rectangle([bx_beak + 5, by_beak + 8, bx_beak + 6, by_beak + 9], fill=C_CRUMB)

    if has_note:
        # Musical note floating
        nx, ny = hx + 12, hy - 14
        draw.rectangle([nx, ny, nx + 2, ny + 6], fill=C_NOTE_BLUE)
        draw.rectangle([nx + 4, ny - 2, nx + 6, ny + 4], fill=C_NOTE_BLUE)
        draw.rectangle([nx, ny - 2, nx + 6, ny], fill=C_NOTE_BLUE)
        draw.ellipse([nx - 2, ny + 4, nx + 2, ny + 7], fill=C_NOTE_BLUE)
        draw.ellipse([nx + 2, ny + 2, nx + 6, ny + 5], fill=C_NOTE_BLUE)

    return img

def generate_all():
    sprites = {
        # IDLE
        "idle_0": draw_cockatiel(crest_mode="normal", eye_mode="open"),
        "idle_1": draw_cockatiel(crest_mode="normal", eye_mode="blink"),
        # WADDLE
        "waddle_0": draw_cockatiel(body_shape="waddle_left", bob_offset=(-1, 0)),
        "waddle_1": draw_cockatiel(body_shape="waddle_right", bob_offset=(1, 0)),
        # PECK
        "peck_0": draw_cockatiel(crest_mode="normal", beak_mode="closed", bob_offset=(0, 0)),
        "peck_1": draw_cockatiel(crest_mode="normal", beak_mode="peck", bob_offset=(1, 3)),
        # MISCHIEF CHEW
        "chew_0": draw_cockatiel(crest_mode="normal", beak_mode="chew", bob_offset=(1, 1), has_crumb=False),
        "chew_1": draw_cockatiel(crest_mode="normal", beak_mode="bite", bob_offset=(2, 2), has_crumb=True),
        # COMFORT FLUFF (Borb)
        "fluff_0": draw_cockatiel(crest_mode="low", eye_mode="squint", body_shape="fluff"),
        "fluff_1": draw_cockatiel(crest_mode="low", eye_mode="closed", body_shape="fluff"),
        # COMFORT PREEN
        "preen_0": draw_cockatiel(crest_mode="low", eye_mode="closed", wing_mode="preen", bob_offset=(-1, 1)),
        "preen_1": draw_cockatiel(crest_mode="low", eye_mode="squint", wing_mode="preen", bob_offset=(-2, 2)),
        # COMFORT BOW (求撸毛)
        "bow_0": draw_cockatiel(crest_mode="low", eye_mode="squint", body_shape="bow"),
        "bow_1": draw_cockatiel(crest_mode="low", eye_mode="closed", body_shape="bow"),
        # EXCITE HOP
        "hop_0": draw_cockatiel(crest_mode="alert", eye_mode="open", body_shape="normal", bob_offset=(0, 0)),
        "hop_1": draw_cockatiel(crest_mode="alert", eye_mode="open", body_shape="hop", bob_offset=(0, -6)),
        # EXCITE BOB (点头狂魔)
        "bob_0": draw_cockatiel(crest_mode="normal", bob_offset=(0, -2)),
        "bob_1": draw_cockatiel(crest_mode="alert", bob_offset=(0, 4)),
        # EXCITE HEART WINGS
        "heart_wings_0": draw_cockatiel(crest_mode="heart", wing_mode="heart", bob_offset=(-1, 0)),
        "heart_wings_1": draw_cockatiel(crest_mode="heart", wing_mode="heart", bob_offset=(1, 0)),
        # EXCITE SING
        "sing_0": draw_cockatiel(crest_mode="sing", beak_mode="sing", eye_mode="blink", has_note=True, bob_offset=(0, -1)),
        "sing_1": draw_cockatiel(crest_mode="sing", beak_mode="closed", eye_mode="open", has_note=False, bob_offset=(0, 1)),
        # FRIGHT ALERT
        "alert_0": draw_cockatiel(crest_mode="alert", eye_mode="shock", body_shape="alert_thin"),
        # FRIGHT BITE
        "bite_0": draw_cockatiel(crest_mode="alert", eye_mode="shock", beak_mode="bite", bob_offset=(3, -1)),
        # FRIGHT HISS
        "hiss_0": draw_cockatiel(crest_mode="alert", eye_mode="shock", beak_mode="hiss", bob_offset=(0, 2)),
        # FLY (Panic or Approach)
        "fly_0": draw_cockatiel(crest_mode="alert", wing_mode="open_up", bob_offset=(0, -3)),
        "fly_1": draw_cockatiel(crest_mode="alert", wing_mode="open_down", bob_offset=(0, 3)),
    }

    for name, img in sprites.items():
        out_path = os.path.join(ASSETS_DIR, f"{name}.png")
        img.save(out_path)
        print(f"Generated {out_path}")

if __name__ == "__main__":
    generate_all()
    print("All sprites generated successfully!")
