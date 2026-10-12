import bpy, math, os
from mathutils import Vector
path=r'D:\pets\blender\cockatiel.blend'
bpy.ops.wm.open_mainfile(filepath=path)
# helpers
def smooth(o):
    if o.type=='MESH':
        for p in o.data.polygons:p.use_smooth=True

def uv(name,loc,scale,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=14, location=loc, rotation=rot)
    o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);smooth(o);return o

def cone(name,loc,r1,r2,depth,mat,rot=(0,0,0)):
    bpy.ops.mesh.primitive_cone_add(vertices=20,radius1=r1,radius2=r2,depth=depth,location=loc,rotation=rot)
    o=bpy.context.object;o.name=name;o.data.materials.append(mat);smooth(o);return o
# materials
mg=bpy.data.materials.get('Mat_Wing_Grey'); mw=bpy.data.materials.get('Mat_Wing_White'); mt=bpy.data.materials.get('Mat_Tail_Grey'); mb=bpy.data.materials.get('Mat_Body_Grey');
# remove prior adjustment objects
for o in list(bpy.data.objects):
    if o.name.startswith('Adj_'): bpy.data.objects.remove(o,do_unlink=True)
# add layered wing feathers, following reference scalloped pattern
for sign in (-1,1):
    for j,(z,depth,w,h,mat) in enumerate([(1.18,0.24,0.34,0.16,mw),(1.02,0.34,0.38,0.18,mg),(0.86,0.43,0.40,0.18,mg),(0.70,0.52,0.42,0.17,mt)]):
        o=uv(f'Adj_Wing_{sign}_{j}',(sign*(0.56+0.05*j),-0.46-depth,z),(w,0.13,h),mat,rot=(math.radians(-18),math.radians(sign*8),math.radians(-sign*8)))
# longer tail feathers, fan slightly
for j,(x,ang,length) in enumerate([(0,0,1.65),(-0.18,-0.08,1.45),(0.18,0.08,1.45),(-0.34,-0.16,1.20),(0.34,0.16,1.20)]):
    o=cone(f'Adj_Tail_{j}',(x,1.40,0.58),0.17,0.025,length,mt,rot=(math.radians(-72),ang,0))
# gray throat bib to separate yellow head from torso
uv('Adj_Bib',(0,-0.49,1.12),(0.45,0.10,0.40),mb)
# slightly enlarge head and narrow body for upright silhouette
head=bpy.data.objects.get('Cockatiel_Head'); body=bpy.data.objects.get('Cockatiel_Body')
if head: head.scale=(1.08,1.02,1.08)
if body: body.scale=(0.92,0.92,1.12)
# camera: centered 3/4 front like reference
cam=bpy.data.objects.get('Main_Camera')
if cam:
    cam.location=(2.65,-5.8,2.35); target=Vector((0,0.35,1.20)); cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler(); cam.data.lens=58
# tune lighting/background and color management
world=bpy.context.scene.world
if world and world.use_nodes:
    bg=world.node_tree.nodes.get('Background'); bg.inputs['Color'].default_value=(0.78,0.68,0.58,1); bg.inputs['Strength'].default_value=0.35
for o in bpy.data.objects:
    if o.type=='LIGHT': o.data.energy*=1.35
sc=bpy.context.scene
sc.view_settings.look='AgX - Medium High Contrast'
sc.view_settings.exposure=0.3
sc.render.resolution_x=800;sc.render.resolution_y=900;sc.render.resolution_percentage=100
sc.render.filepath=r'D:\pets\blender\cockatiel_preview.png'
bpy.ops.wm.save_as_mainfile(filepath=path)
try: bpy.ops.export_scene.gltf(filepath=r'D:\pets\blender\cockatiel.glb',export_format='GLB')
except: pass
try: bpy.ops.wm.obj_export(filepath=r'D:\pets\blender\cockatiel.obj')
except: pass
bpy.ops.render.render(write_still=True)
print('adjusted')

