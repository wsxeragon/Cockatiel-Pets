import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

OUTPUT_DIR = r"D:\pets\blender"
os.makedirs(OUTPUT_DIR, exist_ok=True)

REF_IMAGE_PATH = os.path.join(OUTPUT_DIR, "reference_turnaround.jpg")
BLEND_FILE_PATH = os.path.join(OUTPUT_DIR, "cockatiel.blend")
GLB_FILE_PATH = os.path.join(OUTPUT_DIR, "cockatiel.glb")
OBJ_FILE_PATH = os.path.join(OUTPUT_DIR, "cockatiel.obj")
RENDER_FILE_PATH = os.path.join(OUTPUT_DIR, "cockatiel_preview.png")

# Reset Blender scene completely
bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------------------------------------------
# 1. SHADER MATERIALS (Warm Stylized Cartoon Palette)
# -------------------------------------------------------------
def make_mat(name, color, roughness=0.5, specular=0.5, is_head_grad=False):
    mat = bpy.data.materials.new(name=name)
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    if is_head_grad:
        # Procedural Front Sunny Yellow -> Back Soft Grey feather transition
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
        
        separate_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
        separate_xyz.location = (-220, 0)
        links.new(mapping.outputs['Vector'], separate_xyz.inputs['Vector'])
        
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-20, 0)
        # Front of head is -Y
        color_ramp.color_ramp.elements[0].position = 0.35
        color_ramp.color_ramp.elements[0].color = (0.98, 0.86, 0.28, 1.0) # Bright Yellow Front Face
        color_ramp.color_ramp.elements[1].position = 0.62
        color_ramp.color_ramp.elements[1].color = (0.50, 0.51, 0.55, 1.0) # Grey Back Nape
        
        links.new(separate_xyz.outputs['Y'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = color

    if 'Roughness' in bsdf.inputs:
        bsdf.inputs['Roughness'].default_value = roughness
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = specular

    return mat

mat_body_grey   = make_mat("Mat_Body_Grey",   (0.50, 0.51, 0.55, 1.0), roughness=0.55)
mat_head        = make_mat("Mat_Head",        (0.98, 0.86, 0.28, 1.0), roughness=0.5, is_head_grad=True)
mat_crest       = make_mat("Mat_Crest",       (0.98, 0.85, 0.25, 1.0), roughness=0.45)
mat_cheek       = make_mat("Mat_Cheek",       (0.98, 0.30, 0.15, 1.0), roughness=0.6)
mat_beak        = make_mat("Mat_Beak",        (0.66, 0.58, 0.55, 1.0), roughness=0.45)
mat_eye_pupil   = make_mat("Mat_Eye_Pupil",   (0.03, 0.03, 0.04, 1.0), roughness=0.04, specular=0.98)
mat_eye_shine   = make_mat("Mat_Eye_Shine",   (1.00, 1.00, 1.00, 1.0), roughness=0.1)
mat_wing_grey   = make_mat("Mat_Wing_Grey",   (0.48, 0.49, 0.53, 1.0), roughness=0.55)
mat_wing_white  = make_mat("Mat_Wing_White",  (0.96, 0.96, 0.97, 1.0), roughness=0.45)
mat_tail_grey   = make_mat("Mat_Tail_Grey",   (0.38, 0.39, 0.43, 1.0), roughness=0.55)
mat_feet        = make_mat("Mat_Feet",        (0.62, 0.50, 0.50, 1.0), roughness=0.5)

# Target collection
col = bpy.data.collections.new("Cockatiel_Character")
bpy.context.scene.collection.children.link(col)

def set_smooth(obj):
    for p in obj.data.polygons:
        p.use_smooth = True

def add_subsurf(obj, levels=1, render_levels=2):
    mod = obj.modifiers.new(name="Subdivision", type='SUBSURF')
    mod.levels = levels
    mod.render_levels = render_levels

# -------------------------------------------------------------
# 2. BODY / TORSO MODELING (Bird Stance: Tilted Backwards)
# -------------------------------------------------------------
# Body tilted along X-axis: breast high in front (-Y), back slopes down-backwards (+Y)
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=28, ring_count=20, radius=0.60,
    location=(0, 0.12, 0.90), rotation=(math.radians(24), 0, 0)
)
body_obj = bpy.context.active_object
body_obj.name = "Cockatiel_Body"
body_obj.data.materials.append(mat_body_grey)
col.objects.link(body_obj)
bpy.context.scene.collection.objects.unlink(body_obj)

bm = bmesh.new()
bm.from_mesh(body_obj.data)
for v in bm.verts:
    # Scale elongated along local body axis
    v.co.y *= 1.25  # longer torso
    # Puff chest forward (local -Y)
    if v.co.y < 0:
        v.co.y *= 1.20
        v.co.z *= 1.08
    # Round belly downward
    if v.co.z < 0:
        v.co.z *= 1.15
bm.to_mesh(body_obj.data)
bm.free()

set_smooth(body_obj)
add_subsurf(body_obj, levels=1)

# -------------------------------------------------------------
# 3. HEAD (Proud Upright Spherical Head)
# -------------------------------------------------------------
bpy.ops.mesh.primitive_uv_sphere_add(
    segments=28, ring_count=20, radius=0.50,
    location=(0, -0.12, 1.48)
)
head_obj = bpy.context.active_object
head_obj.name = "Cockatiel_Head"
head_obj.data.materials.append(mat_head)
col.objects.link(head_obj)
bpy.context.scene.collection.objects.unlink(head_obj)

bm = bmesh.new()
bm.from_mesh(head_obj.data)
for v in bm.verts:
    z_rel = v.co.z - 1.48
    if z_rel < 0:
        # Full cheeks
        v.co.x *= 1.08
    else:
        v.co.x *= 0.96
bm.to_mesh(head_obj.data)
bm.free()

set_smooth(head_obj)
add_subsurf(head_obj, levels=1)

# -------------------------------------------------------------
# 4. CREST (凤头冠羽 - Tall, Dynamic Backward Arcing Plumes)
# -------------------------------------------------------------
crest_specs = [
    # (name, location, rotation_euler, scale, backward_arc_curve)
    ("Crest_Center_Main", (0.00, -0.14, 1.96), (math.radians(-24), 0, 0), (0.10, 0.10, 0.58), 0.70),
    ("Crest_Front_Tip",   (0.00, -0.24, 1.92), (math.radians(-38), 0, 0), (0.09, 0.09, 0.46), 0.55),
    ("Crest_Left_Outer",  (-0.08, -0.13, 1.93), (math.radians(-20), math.radians(-14), 0), (0.07, 0.07, 0.48), 0.50),
    ("Crest_Right_Outer", (0.08, -0.13, 1.93), (math.radians(-20), math.radians(14), 0), (0.07, 0.07, 0.48), 0.50),
    ("Crest_Rear_Sub",    (0.00, -0.04, 1.90), (math.radians(-10), 0, 0), (0.07, 0.07, 0.38), 0.38),
]

for name, loc, rot, scl, curve_amt in crest_specs:
    bpy.ops.mesh.primitive_cone_add(vertices=14, radius1=1.0, radius2=0.03, depth=2.0, location=loc, rotation=rot)
    crest_obj = bpy.context.active_object
    crest_obj.name = name
    crest_obj.scale = scl
    crest_obj.data.materials.append(mat_crest)
    col.objects.link(crest_obj)
    bpy.context.scene.collection.objects.unlink(crest_obj)

    # Arc plume backward and upward at the tip
    bm = bmesh.new()
    bm.from_mesh(crest_obj.data)
    for v in bm.verts:
        if v.co.z > -0.5:
            t = (v.co.z + 0.5) / 1.5
            v.co.y += (t**2) * curve_amt
            v.co.x *= (1.0 - t * 0.38)
    bm.to_mesh(crest_obj.data)
    bm.free()

    set_smooth(crest_obj)
    add_subsurf(crest_obj, levels=1)

# -------------------------------------------------------------
# 5. BEAK (Authentic Hooked Cartoon Cockatiel Beak)
# -------------------------------------------------------------
# Upper beak curving downwards
bpy.ops.mesh.primitive_cone_add(
    vertices=14, radius1=0.15, radius2=0.012, depth=0.34,
    location=(0, -0.58, 1.40), rotation=(math.radians(105), 0, 0)
)
beak_upper = bpy.context.active_object
beak_upper.name = "Cockatiel_Beak_Upper"
beak_upper.data.materials.append(mat_beak)
col.objects.link(beak_upper)
bpy.context.scene.collection.objects.unlink(beak_upper)

bm = bmesh.new()
bm.from_mesh(beak_upper.data)
for v in bm.verts:
    # Hook the tip down towards -Z
    if v.co.z > 0:
        v.co.y -= (v.co.z**2) * 0.45
        v.co.z -= (v.co.z**2) * 0.35
    v.co.x *= 0.72
bm.to_mesh(beak_upper.data)
bm.free()

set_smooth(beak_upper)
add_subsurf(beak_upper, levels=1)

# Lower beak scoop
bpy.ops.mesh.primitive_cone_add(
    vertices=10, radius1=0.10, radius2=0.02, depth=0.18,
    location=(0, -0.53, 1.30), rotation=(math.radians(75), 0, 0)
)
beak_lower = bpy.context.active_object
beak_lower.name = "Cockatiel_Beak_Lower"
beak_lower.data.materials.append(mat_beak)
col.objects.link(beak_lower)
bpy.context.scene.collection.objects.unlink(beak_lower)
set_smooth(beak_lower)

# -------------------------------------------------------------
# 6. EYES & SPECULAR CATCHLIGHTS
# -------------------------------------------------------------
# Head center is (0, -0.12, 1.48), radius ~0.50
# At X = +/-0.33, Z = 1.48: Y_surf = -0.12 - sqrt(0.50^2 - 0.33^2) = -0.12 - 0.375 = -0.495
for side, sign in [("Left", -1), ("Right", 1)]:
    eye_loc = (sign * 0.34, -0.50, 1.48)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=14, radius=0.09, location=eye_loc)
    eye = bpy.context.active_object
    eye.name = f"Eye_Pupil_{side}"
    eye.scale = (0.75, 1.0, 1.0)
    eye.rotation_euler = (0, math.radians(-sign * 12), math.radians(-sign * 32))
    eye.data.materials.append(mat_eye_pupil)
    col.objects.link(eye)
    bpy.context.scene.collection.objects.unlink(eye)
    set_smooth(eye)

    # Catchlight Highlight Dot
    shine_loc = (sign * 0.35, -0.57, 1.52)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=0.03, location=shine_loc)
    shine = bpy.context.active_object
    shine.name = f"Eye_Shine_{side}"
    shine.data.materials.append(mat_eye_shine)
    col.objects.link(shine)
    bpy.context.scene.collection.objects.unlink(shine)
    set_smooth(shine)

# -------------------------------------------------------------
# 7. CHEEK BLUSH PATCHES (Signature Vibrant Orange Circles)
# -------------------------------------------------------------
# At X = +/-0.43, Z = 1.34: Y_surf = -0.12 - sqrt(0.48^2 - 0.43^2) = -0.12 - 0.21 = -0.33
for side, sign in [("Left", -1), ("Right", 1)]:
    cheek_loc = (sign * 0.43, -0.34, 1.34)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=14, radius=0.17, location=cheek_loc)
    cheek = bpy.context.active_object
    cheek.name = f"Cheek_Blush_{side}"
    cheek.scale = (0.42, 1.0, 0.95)
    cheek.rotation_euler = (math.radians(10), math.radians(-sign * 16), math.radians(-sign * 36))
    cheek.data.materials.append(mat_cheek)
    col.objects.link(cheek)
    bpy.context.scene.collection.objects.unlink(cheek)
    set_smooth(cheek)
    add_subsurf(cheek, levels=1)

# -------------------------------------------------------------
# 8. WINGS (Flanking Body with Iconic Crisp White Wing Bar)
# -------------------------------------------------------------
# Wings fold along the diagonal slant of the body towards the tail
for side, sign in [("Left", -1), ("Right", 1)]:
    # Grey Main Wing Body
    wing_loc = (sign * 0.52, 0.18, 0.96)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=22, ring_count=16, radius=0.50, location=wing_loc)
    wing = bpy.context.active_object
    wing.name = f"Wing_Grey_{side}"
    wing.scale = (0.34, 1.35, 0.60)
    # Tilted along flanks: down and back
    wing.rotation_euler = (math.radians(-38), math.radians(sign * 12), math.radians(-sign * 12))
    wing.data.materials.append(mat_wing_grey)
    col.objects.link(wing)
    bpy.context.scene.collection.objects.unlink(wing)

    bm = bmesh.new()
    bm.from_mesh(wing.data)
    for v in bm.verts:
        if v.co.y > 0:
            v.co.z *= 0.60
            v.co.x *= 0.70
    bm.to_mesh(wing.data)
    bm.free()

    set_smooth(wing)
    add_subsurf(wing, levels=1)

    # Crisp White Wing Stripe (Runs along lower edge of wing)
    stripe_loc = (sign * 0.56, 0.12, 0.85)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=18, ring_count=12, radius=0.35, location=stripe_loc)
    stripe = bpy.context.active_object
    stripe.name = f"Wing_Stripe_White_{side}"
    stripe.scale = (0.28, 1.15, 0.30)
    stripe.rotation_euler = (math.radians(-40), math.radians(sign * 12), math.radians(-sign * 12))
    stripe.data.materials.append(mat_wing_white)
    col.objects.link(stripe)
    bpy.context.scene.collection.objects.unlink(stripe)
    set_smooth(stripe)
    add_subsurf(stripe, levels=1)

# -------------------------------------------------------------
# 9. TAIL (Layered Long Feathers Extending Out Back)
# -------------------------------------------------------------
tail_feathers = [
    # Center primary long feather
    ("Tail_Center", (0.00, 1.15, 0.52), (math.radians(-32), 0, 0), (0.16, 1.10, 0.05)),
    # Flanking feathers
    ("Tail_Left",   (-0.08, 1.05, 0.56), (math.radians(-30), math.radians(-6), 0), (0.14, 0.98, 0.04)),
    ("Tail_Right",  (0.08, 1.05, 0.56), (math.radians(-30), math.radians(6), 0), (0.14, 0.98, 0.04)),
]

for name, loc, rot, scl in tail_feathers:
    bpy.ops.mesh.primitive_cylinder_add(vertices=14, radius=1.0, depth=2.0, location=loc, rotation=rot)
    tail_obj = bpy.context.active_object
    tail_obj.name = name
    tail_obj.scale = scl
    tail_obj.data.materials.append(mat_tail_grey)
    col.objects.link(tail_obj)
    bpy.context.scene.collection.objects.unlink(tail_obj)

    bm = bmesh.new()
    bm.from_mesh(tail_obj.data)
    for v in bm.verts:
        v.co.x *= 0.85
        if v.co.z > 0.2:
            v.co.x *= (1.0 - (v.co.z - 0.2) * 0.88)
    bm.to_mesh(tail_obj.data)
    bm.free()

    set_smooth(tail_obj)
    add_subsurf(tail_obj, levels=1)

# -------------------------------------------------------------
# 10. FEET & LEGS (Zygodactyl Gripping Claws on Ground Z=0)
# -------------------------------------------------------------
for side, sign in [("Left", -1), ("Right", 1)]:
    # Leg shaft
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=10, radius=0.06, depth=0.24,
        location=(sign * 0.20, 0.04, 0.16), rotation=(math.radians(-10), 0, 0)
    )
    leg = bpy.context.active_object
    leg.name = f"Leg_{side}"
    leg.data.materials.append(mat_feet)
    col.objects.link(leg)
    bpy.context.scene.collection.objects.unlink(leg)
    set_smooth(leg)

    # Toes (2 forward, 1 back)
    toes = [
        (f"Toe_Inner_{side}",  (sign * 0.16, -0.10, 0.03), (0, 0, math.radians(-sign * 15)), 0.16),
        (f"Toe_Middle_{side}", (sign * 0.24, -0.11, 0.03), (0, 0, math.radians(sign * 12)), 0.18),
        (f"Toe_Back_{side}",   (sign * 0.20, 0.18, 0.03),  (0, 0, math.radians(sign * 175)), 0.15),
    ]
    for toe_name, toe_loc, toe_rot, toe_len in toes:
        bpy.ops.mesh.primitive_cone_add(vertices=8, radius1=0.035, radius2=0.01, depth=toe_len, location=toe_loc, rotation=toe_rot)
        toe = bpy.context.active_object
        toe.name = toe_name
        toe.data.materials.append(mat_feet)
        col.objects.link(toe)
        bpy.context.scene.collection.objects.unlink(toe)
        set_smooth(toe)

# -------------------------------------------------------------
# 11. GROUND STUDIO PEDESTAL
# -------------------------------------------------------------
bpy.ops.mesh.primitive_cylinder_add(vertices=36, radius=2.4, depth=0.04, location=(0, 0.25, -0.02))
ground = bpy.context.active_object
ground.name = "Studio_Ground"
mat_ground = make_mat("Mat_Ground", (0.94, 0.90, 0.86, 1.0), roughness=0.90)
ground.data.materials.append(mat_ground)
set_smooth(ground)

# -------------------------------------------------------------
# 12. REFERENCE IMAGE EMPTY IN 3D VIEWPORT
# -------------------------------------------------------------
if os.path.exists(REF_IMAGE_PATH):
    try:
        ref_img = bpy.data.images.load(REF_IMAGE_PATH)
        empty = bpy.data.objects.new("Ref_Turnaround_Sheet", None)
        empty.empty_display_type = 'IMAGE'
        empty.data = ref_img
        empty.location = (0, 2.8, 1.3)
        empty.rotation_euler = (math.radians(90), 0, 0)
        empty.empty_display_size = 4.2
        bpy.context.scene.collection.objects.link(empty)
        print("Reference turnaround sheet linked in 3D scene!")
    except Exception as e:
        print("Notice: could not link ref empty:", e)

# -------------------------------------------------------------
# 13. WARM STUDIO LIGHTING & BEAUTY CAMERA
# -------------------------------------------------------------
# World background: warm pastel cream matching turnaround sheet
world = bpy.context.scene.world
if world is None:
    world = bpy.data.worlds.new("Studio_World")
    bpy.context.scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs['Color'].default_value = (0.96, 0.93, 0.89, 1.0)
    bg_node.inputs['Strength'].default_value = 0.85

# Key Light (Warm soft sunlight from front-left)
light_key = bpy.data.lights.new(name="Key_Light", type='AREA')
light_key.energy = 420
light_key.size = 2.6
light_key.color = (1.0, 0.97, 0.90)
obj_key = bpy.data.objects.new("Key_Light", light_key)
obj_key.location = (-2.8, -3.2, 3.0)
obj_key.rotation_euler = (math.radians(52), math.radians(-15), math.radians(-38))
bpy.context.scene.collection.objects.link(obj_key)

# Fill Light (Soft cool light from front-right)
light_fill = bpy.data.lights.new(name="Fill_Light", type='AREA')
light_fill.energy = 160
light_fill.size = 3.6
light_fill.color = (0.92, 0.96, 1.0)
obj_fill = bpy.data.objects.new("Fill_Light", light_fill)
obj_fill.location = (3.2, -2.4, 2.0)
obj_fill.rotation_euler = (math.radians(55), math.radians(20), math.radians(45))
bpy.context.scene.collection.objects.link(obj_fill)

# Rim Light (Back light for crest, wings, and tail contour)
light_rim = bpy.data.lights.new(name="Rim_Light", type='AREA')
light_rim.energy = 380
light_rim.size = 2.8
light_rim.color = (1.0, 0.96, 0.88)
obj_rim = bpy.data.objects.new("Rim_Light", light_rim)
obj_rim.location = (0.0, 3.4, 2.8)
obj_rim.rotation_euler = (math.radians(-45), 0, math.radians(180))
bpy.context.scene.collection.objects.link(obj_rim)

# Camera (Cute 3/4 Front Beauty View, 52mm lens)
cam = bpy.data.cameras.new("Main_Camera")
cam.lens = 52
obj_cam = bpy.data.objects.new("Main_Camera", cam)
# Elevated 3/4 beauty angle framing face, crest, wings, and extending tail
obj_cam.location = (-3.0, -3.8, 2.3)
target = Vector((0, 0.20, 1.15))
direction = target - obj_cam.location
rot_quat = direction.to_track_quat('-Z', 'Y')
obj_cam.rotation_euler = rot_quat.to_euler()
bpy.context.scene.collection.objects.link(obj_cam)
bpy.context.scene.camera = obj_cam

# Render settings
bpy.context.scene.render.engine = 'BLENDER_EEVEE'
bpy.context.scene.render.resolution_x = 1200
bpy.context.scene.render.resolution_y = 900
bpy.context.scene.render.film_transparent = False

# -------------------------------------------------------------
# 14. SAVE .BLEND & EXPORT .GLB / .OBJ & RENDER PREVIEW
# -------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=BLEND_FILE_PATH)
print(f"Saved Blender Project: {BLEND_FILE_PATH}")

try:
    bpy.ops.export_scene.gltf(filepath=GLB_FILE_PATH, export_format='GLB')
    print(f"Exported GLB: {GLB_FILE_PATH}")
except Exception as e:
    print("Notice: GLB export skipped:", e)

try:
    bpy.ops.wm.obj_export(filepath=OBJ_FILE_PATH)
    print(f"Exported OBJ: {OBJ_FILE_PATH}")
except Exception as e:
    print("Notice: OBJ export skipped:", e)

bpy.context.scene.render.filepath = RENDER_FILE_PATH
bpy.ops.render.render(write_still=True)
print(f"Rendered Preview Image: {RENDER_FILE_PATH}")

print("==================================================")
print("Cockatiel 3D Model successfully regenerated!")
print("==================================================")
