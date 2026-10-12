"""Reference-inspired pixel sprites on a fixed 100x80 grid."""
from pathlib import Path
from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / "assets" / "sprites"
C = dict(ink="#353438", grey="#69696d", light="#88878a", dark="#505055",
         white="#f5f1df", yellow="#fff081", shade="#eacb67", cheek="#e99342",
         beak="#a99b9a", foot="#bba5a5")


def bird(head=(0, 0), lift=0, step=0, wing="fold", puff=0, eye="open",
         crest="normal", mouth="closed", crumbs=False, note=0):
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C
    # Reference faces left. A shared 72px ground line anchors all land poses.
    d.polygon([(61, 47+lift), (96, 51+lift), (98, 54+lift),
               (68, 56+lift), (60, 52+lift)], fill=c["ink"])
    d.polygon([(63, 48+lift), (95, 52+lift), (92, 54+lift),
               (67, 53+lift)], fill=c["dark"])
    d.line([(71, 51+lift), (92, 53+lift)], fill=c["light"])
    if wing.startswith("fly"):
        far = {"fly_up": [(52,42),(73,11),(80,7),(69,40)],
               "fly_mid": [(53,43),(82,27),(96,28),(66,49)],
               "fly_down": [(54,43),(80,63),(83,66),(59,50)]}[wing]
        d.polygon([(x,y+lift) for x,y in far], fill=c["dark"])
    if wing.startswith("fly"):
        for x in (47, 57):
            d.line([(x,57+lift),(x-2,64+lift),(x+1,65+lift)], fill=c["foot"], width=2)
    else:
        # In each stride only one leg changes position; the other stays planted.
        feet = [(46,42),(58,55)]
        if step == 1:
            feet = [(44,37),(58,55)]
        elif step == 2:
            feet = [(46,42),(58,65)]
        for x, toe in feet:
            d.line([(x,66+lift),(toe,72)], fill=c["ink"], width=3)
            d.line([(x,66+lift),(toe,72)], fill=c["foot"], width=2)
            d.line([(toe-3,72),(toe+2,72)], fill=c["foot"], width=2)
    d.ellipse((34-puff,32+lift-puff,72+puff,69+lift), fill=c["ink"])
    d.ellipse((36-puff,34+lift-puff,70+puff,67+lift), fill=c["grey"])
    d.ellipse((38-puff,39+lift,57,64+lift), fill=c["light"])
    if puff:
        for x,y in [(35,48),(34,56),(39,64),(70,42)]:
            d.rectangle((x-2,y+lift,x+1,y+lift+2), fill=c["light"])
    if wing.startswith("fly"):
        wing_shape = {"fly_up": [(48,43),(56,26),(64,7),(69,10),(65,35),(56,51)],
                      "fly_mid": [(48,43),(67,29),(89,23),(92,28),(66,46),(54,52)],
                      "fly_down": [(48,43),(61,49),(81,68),(76,71),(54,55)]}[wing]
        d.polygon([(x,y+lift) for x,y in wing_shape], fill=c["ink"])
        white_shape = {"fly_up": [(52,42),(61,23),(65,13),(62,33),(55,46)],
                       "fly_mid": [(52,42),(69,32),(85,27),(66,42),(55,48)],
                       "fly_down": [(52,46),(62,52),(77,66),(72,65),(55,52)]}[wing]
        d.polygon([(x,y+lift) for x,y in white_shape], fill=c["white"])
    else:
        if wing=="heart":
            d.polygon([(49,38+lift),(66,45+lift),(72,62+lift),(59,56+lift)], fill=c["ink"])
        else:
            d.polygon([(48,38+lift),(65,43+lift),(76,54+lift),(63,62+lift),(48,55+lift)], fill=c["ink"])
        d.polygon([(49,40+lift),(65,44+lift),(73,53+lift),(61,57+lift),(49,52+lift)], fill=c["dark"])
        d.polygon([(49,46+lift),(54,48+lift),(61,56+lift),(72,55+lift),
                   (65,61+lift),(56,59+lift)], fill=c["white"])
    hx, hy = 33+head[0], 33+head[1]+lift
    d.ellipse((hx-13,hy-13,hx+13,hy+13), fill=c["ink"])
    d.ellipse((hx-12,hy-12,hx+11,hy+12), fill=c["yellow"])
    d.polygon([(hx+6,hy-9),(hx+12,hy-5),(hx+13,hy+9),(hx+6,hy+12)], fill=c["white"])
    d.ellipse((hx-3,hy+1,hx+8,hy+11), fill=c["cheek"])
    if crest=="low":
        d.polygon([(hx-4,hy-11),(hx+8,hy-15),(hx+17,hy-13),(hx+5,hy-9)], fill=c["shade"])
        d.line([(hx-2,hy-12),(hx+16,hy-14)], fill=c["yellow"], width=3)
    elif crest=="alert":
        d.polygon([(hx-5,hy-10),(hx-1,hy-28),(hx+2,hy-30),(hx+3,hy-11)], fill=c["shade"])
        d.polygon([(hx,hy-11),(hx+7,hy-25),(hx+9,hy-24),(hx+4,hy-9)], fill=c["yellow"])
    else:
        d.polygon([(hx-7,hy-11),(hx+1,hy-21),(hx+14,hy-26),
                   (hx+12,hy-19),(hx+3,hy-10)], fill=c["shade"])
        d.polygon([(hx-5,hy-12),(hx+2,hy-20),(hx+13,hy-25),
                   (hx+10,hy-20),(hx+1,hy-11)], fill=c["yellow"])
    if eye=="open":
        d.ellipse((hx-8,hy-5,hx-4,hy), fill=c["ink"])
        d.point((hx-7,hy-4), fill=c["white"])
    elif eye=="wide":
        d.ellipse((hx-9,hy-7,hx-3,hy+1), fill=c["ink"])
        d.point((hx-7,hy-5), fill=c["white"])
    else:
        d.line([(hx-9,hy-2),(hx-6,hy-1),(hx-3,hy-2)], fill=c["ink"], width=2)
    # Large rounded upper mandible with a downward hook, as in the reference.
    # The small lower mandible sits behind it; opening the mouth moves only that
    # lower piece. Keep the existing grey-pink beak colour.
    opened = mouth in ("bite", "hiss", "sing")
    if mouth == "sing":
        d.polygon([(hx-11,hy+4),(hx-14,hy+6),(hx-13,hy+8),
                   (hx-10,hy+7)], fill=c["ink"])
        d.line([(hx-13,hy+6),(hx-11,hy+6)], fill=c["beak"])
    elif opened:
        d.polygon([(hx-11,hy+4),(hx-14,hy+7),(hx-13,hy+10),
                   (hx-10,hy+9),(hx-8,hy+6)], fill=c["ink"])
        d.polygon([(hx-11,hy+7),(hx-13,hy+8),(hx-12,hy+9),
                   (hx-10,hy+8)], fill=c["beak"])
    else:
        d.polygon([(hx-11,hy+4),(hx-13,hy+6),(hx-11,hy+8),
                   (hx-9,hy+6)], fill=c["ink"])
        d.polygon([(hx-11,hy+5),(hx-12,hy+6),(hx-10,hy+7)], fill=c["beak"])
    upper = [(hx-10,hy-2),(hx-13,hy-2),(hx-15,hy),
             (hx-16,hy+2),(hx-16,hy+4),(hx-14,hy+6),
             (hx-13,hy+8),(hx-13,hy+5),(hx-10,hy+2)]
    d.polygon(upper, fill=c["ink"])
    d.polygon([(hx-11,hy-1),(hx-13,hy-1),(hx-15,hy+1),
               (hx-15,hy+4),(hx-13,hy+6),(hx-13,hy+5),
               (hx-10,hy+2)], fill=c["beak"])
    d.point((hx-14,hy+1), fill="#c8b8b5")
    if note:
        # A beamed pair has unmistakable note heads and stems, rather than
        # round particles that can read as droplets. Move it up and out.
        nx = hx - (28 if note == 1 else 32)
        ny = hy - (11 if note == 1 else 18)
        music = "#78c9ea"
        d.rectangle((nx+2,ny+1,nx+3,ny+9), fill=music)
        d.rectangle((nx+9,ny,nx+10,ny+8), fill=music)
        d.polygon([(nx+2,ny+1),(nx+9,ny),(nx+10,ny+2),
                   (nx+3,ny+3)], fill=music)
        d.ellipse((nx-1,ny+8,nx+3,ny+11), fill=music)
        d.ellipse((nx+6,ny+7,nx+10,ny+10), fill=music)
    if crumbs:
        for x,y in [(hx-23,hy+10),(hx-27,hy+5),(hx-25,hy+15)]:
            d.rectangle((x,y,x+2,y+2), fill=c["shade"])
    return im


def sleeping_bird(puff=0, head=0, zzz=0):
    im = Image.new("RGBA", (100, 80))
    d = ImageDraw.Draw(im)
    c = C
    d.polygon([(61, 56), (97, 61), (98, 66),
               (67, 69), (59, 64)], fill=c["ink"])
    d.polygon([(64, 57), (95, 62), (92, 65),
               (66, 66)], fill=c["dark"])
    d.line([(71, 61), (93, 63)], fill=c["light"])

    top = 45 - puff
    d.ellipse((30-puff, top, 79+puff, 71), fill=c["ink"])
    d.ellipse((32-puff, top+2, 77+puff, 69), fill=c["grey"])
    d.polygon([(35, 59), (62, 55), (75, 63),
               (69, 70), (38, 70)], fill=c["light"])
    d.polygon([(44, 53), (66, 54), (76, 62),
               (67, 69), (45, 65)], fill=c["ink"])
    d.polygon([(46, 55), (65, 56), (73, 62),
               (65, 67), (47, 64)], fill=c["dark"])
    d.line([(49, 64), (69, 64)], fill=c["white"], width=2)

    hx, hy = 24, 60 + head
    d.ellipse((hx-13, hy-13, hx+13, hy+13), fill=c["ink"])
    d.ellipse((hx-12, hy-12, hx+11, hy+12), fill=c["yellow"])
    d.polygon([(hx+6, hy-9), (hx+12, hy-5),
               (hx+13, hy+9), (hx+6, hy+12)], fill=c["white"])
    d.ellipse((hx-3, hy+1, hx+8, hy+11), fill=c["cheek"])
    d.polygon([(hx-6, hy-11), (hx+7, hy-15),
               (hx+18, hy-10), (hx+7, hy-8)], fill=c["shade"])
    d.line([(hx-4, hy-12), (hx+17, hy-11)],
           fill=c["yellow"], width=3)
    d.line([(hx-9, hy-2), (hx-6, hy-1), (hx-3, hy-2)],
           fill=c["ink"], width=2)

    d.polygon([(hx-11, hy+4), (hx-13, hy+6),
               (hx-11, hy+8), (hx-9, hy+6)], fill=c["ink"])
    d.polygon([(hx-11, hy+5), (hx-12, hy+6),
               (hx-10, hy+7)], fill=c["beak"])
    upper = [(hx-10, hy-2), (hx-13, hy-2), (hx-15, hy),
             (hx-16, hy+2), (hx-16, hy+4), (hx-14, hy+6),
             (hx-13, hy+8), (hx-13, hy+5), (hx-10, hy+2)]
    d.polygon(upper, fill=c["ink"])
    d.polygon([(hx-11, hy-1), (hx-13, hy-1), (hx-15, hy+1),
               (hx-15, hy+4), (hx-13, hy+6), (hx-13, hy+5),
               (hx-10, hy+2)], fill=c["beak"])
    d.point((hx-14, hy+1), fill="#c8b8b5")

    if zzz:
        zc = "#8bb8d0"
        zx = 72 + (2 if zzz == 2 else 0)
        zy = 8 if zzz == 1 else 4
        for ox, oy, size in [(0, 7, 5), (8, 0, 4)]:
            x, y = zx + ox, zy + oy
            d.line([(x, y), (x+size, y), (x, y+size),
                    (x+size, y+size)], fill=zc, width=1)
    return im


def generate_all():
    OUT.mkdir(parents=True, exist_ok=True)
    frames = {
        "idle_0": {}, "idle_1": {"eye":"closed"},
        "waddle_0": {},
        "waddle_1": {"step":1,"head":(-1,0)},
        "waddle_2": {},
        "waddle_3": {"step":2,"head":(0,1)},
        "peck_0": {"head":(-2,3)}, "peck_1": {"head":(-5,10)},
        "chew_0": {"head":(-2,2)}, "chew_1": {"head":(-4,3),"mouth":"bite","crumbs":True},
        "fluff_0": {"puff":3,"eye":"closed","crest":"low"},
        "fluff_1": {"puff":5,"eye":"closed","crest":"low","lift":-1},
        "preen_0": {"head":(4,4),"eye":"closed"}, "preen_1": {"head":(7,7),"eye":"closed"},
        "bow_0": {"head":(-5,8),"eye":"closed","crest":"low"},
        "bow_1": {"head":(-8,13),"eye":"closed","crest":"low"},
        "hop_0": {}, "hop_1": {"lift":-5,"step":1},
        "bob_0": {"head":(0,-2)}, "bob_1": {"head":(-3,5)},
        "heart_wings_0": {"wing":"heart"}, "heart_wings_1": {"wing":"heart","head":(0,-1)},
        "sing_0": {"mouth":"sing","note":1},
        "sing_1": {"mouth":"sing","note":2,"head":(0,-1)},
        "sing_2": {"mouth":"closed","head":(0,-1)},
        "alert_0": {"head":(0,-4),"crest":"alert","eye":"wide"},
        "bite_0": {"head":(-8,-1),"crest":"alert","eye":"wide","mouth":"bite"},
        "bite_1": {"head":(-3,0),"crest":"alert","eye":"wide","mouth":"bite"},
        "hiss_0": {"head":(-2,2),"crest":"alert","eye":"wide","mouth":"hiss"},
        "fly_0": {"wing":"fly_up","lift":-5,"crest":"alert"},
        "fly_1": {"wing":"fly_mid","lift":-5,"crest":"alert"},
        "fly_2": {"wing":"fly_down","lift":-5,"crest":"alert"},
        "sleep_0": {"sleeping":True,"puff":0,"head":-1,"zzz":1},
        "sleep_1": {"sleeping":True,"puff":2,"head":0,"zzz":2},
        "wake_0": {"sleeping":True,"puff":0,"head":-1},
        "wake_1": {"crest":"alert","eye":"wide","head":(0,-2)},
    }
    for name, kwargs in frames.items():
        sprite = sleeping_bird(**kwargs) if kwargs.pop("sleeping", False) else bird(**kwargs)
        sprite.save(OUT / f"{name}.png")
    return len(frames)


if __name__ == "__main__":
    print(f"Generated {generate_all()} pixel sprites")
