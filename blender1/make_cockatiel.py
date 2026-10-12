import bpy, math, os
from mathutils import Vector
# clear
bpy.ops.wm.read_factory_settings(use_empty=True)
# materials
def mat(name, color, rough=0.6, metallic=0.0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value=(*color,1); bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metallic
    return m
Y=mat('warm yellow',(0.95,0.68,0.12)); Y2=mat('crest golden',(1.0,0.78,0.18)); G=mat('body gray',(0.30,0.31,0.34)); G2=mat('wing gray',(0.22,0.23,0.26)); W=mat('wing white',(0.90,0.89,0.84)); OR=mat('cheek orange',(0.95,0.22,0.06)); BEAK=mat('beak lavender gray',(0.42,0.34,0.43)); DARK=mat('eye black',(0.015,0.012,0.01),0.25); IRIS=mat('eye highlight',(1,1,1),0.15); FOOT=mat('feet pink brown',(0.35,0.20,0.20));
def smooth(obj):
    if obj.type=='MESH':
        for p in obj.data.polygons: p.use_smooth=True
    return obj
def uv(name, loc, scale, material, seg=48, rings=24):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material); return smooth(o)
def ico(name, loc, scale, material, sub=3):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, location=loc); o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False, rotation=False, scale=True); o.data.materials.append(material); return smooth(o)
def cone(name, loc, r1, r2, depth, material, rot=(0,0,0), verts=32):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rot); o=bpy.context.object; o.name=name; o.data.materials.append(material); return smooth(o)
def cyl_between(name,a,b,r,material,verts=24):
    a,b=Vector(a),Vector(b); d=b-a; mid=(a+b)/2
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d.length, location=mid)
    o=bpy.context.object; o.name=name; o.data.materials.append(material); o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); return smooth(o)
# body and head
uv('Body',(0,0,2.55),(1.38,0.78,1.85),G)
uv('Chest',(0,-0.08,3.35),(1.20,0.70,1.30),G)
uv('Head',(0,-0.02,4.65),(1.10,0.78,1.12),Y)
# face lower gray bib
uv('Bib',(0,-0.70,3.85),(0.78,0.26,0.72),G)
# eyes, cheek patches
for sx in (-1,1):
    uv('Eye', (sx*0.48,-0.70,4.82),(0.20,0.12,0.27), DARK)
    uv('Eye_glint',(sx*0.43,-0.815,4.92),(0.055,0.025,0.075),IRIS,24,12)
    uv('Cheek',(sx*0.78,-0.69,4.42),(0.25,0.10,0.30),OR)
# beak layered
cone('Upper_beak',(0,-0.93,4.58),0.34,0.08,0.58,BEAK,rot=(math.radians(90),0,0))
cone('Lower_beak',(0,-0.98,4.34),0.22,0.03,0.36,BEAK,rot=(math.radians(90),0,0))
# crest feathers
for i,(x,z,s,r) in enumerate([(-0.40,5.64,0.55,-0.20),(-0.20,5.86,0.78,-0.10),(0,6.02,0.95,0),(0.20,5.86,0.78,0.10),(0.40,5.64,0.55,0.20)]):
    o=cone('Crest_%02d'%i,(x,0,z),0.16,0.025,s,Y2,rot=(0,r,0),verts=20)
# wings: layered teardrops on sides
for sx in (-1,1):
    side=sx
    uv('Wing_base',(1.05*sx,0.02,3.15),(0.58,0.42,1.30),G2)
    for j,(z,sc,matl) in enumerate([(3.70,0.90,W),(3.42,0.82,G),(3.15,0.75,G),(2.88,0.68,G2)]):
        o=uv('Wing_feather_%s_%02d'%(sx,j),(1.16*sx,-0.43,z),(0.38*sc,0.16,0.28*sc),matl)
        o.rotation_euler[1]=math.radians(-18*sx)
# tail feathers, pointed cones elongated
for i,(x,y,z,sc,ang) in enumerate([(0,0,1.05,1.0,0),(-0.28,0,1.12,0.90,-0.08),(0.28,0,1.12,0.90,0.08)]):
    o=cone('Tail_%02d'%i,(x,y,z),0.24*sc,0.035,2.65*sc,G2,rot=(0,ang,0),verts=24)
# feet legs
for sx in (-1,1):
    x=0.42*sx
    cyl_between('Leg',(x,-0.02,1.18),(x,-0.10,0.52),0.11,FOOT)
    uv('FootPalm',(x,-0.18,0.45),(0.25,0.16,0.10),FOOT)
    for k,dx in enumerate((-0.18,0,0.18)):
        cyl_between('Toe',(x,-0.18,0.44),(x+dx*sx,-0.46-0.04*abs(k-1),0.28),0.055,FOOT,16)
        cone('Claw',(x+dx*sx,-0.46-0.04*abs(k-1),0.25),0.06,0.015,0.18,FOOT,rot=(math.radians(90),0,0),verts=12)
# ground
bpy.ops.mesh.primitive_plane_add(size=30, location=(0,0,0)); ground=bpy.context.object; ground.name='Ground'; ground.data.materials.append(mat('ground',(0.72,0.62,0.52)))
# backdrop world
bpy.context.scene.world = bpy.data.worlds.new('World') if bpy.context.scene.world is None else bpy.context.scene.world
bpy.context.scene.world.color=(0.055,0.035,0.025)
# camera
bpy.ops.object.camera_add(location=(0,-15,4.0)); cam=bpy.context.object; bpy.context.scene.camera=cam
def track(obj,pt): obj.rotation_euler=(Vector(pt)-obj.location).to_track_quat('-Z','Y').to_euler()
track(cam,(0,0,3.1)); cam.data.lens=58
# lights
bpy.ops.object.light_add(type='AREA', location=(-4,-6,8)); key=bpy.context.object; key.data.energy=1100; key.data.shape='DISK'; key.data.size=5; track(key,(0,0,3))
bpy.ops.object.light_add(type='AREA', location=(4,-3,5)); fill=bpy.context.object; fill.data.energy=650; fill.data.size=4; track(fill,(0,0,3))
bpy.ops.object.light_add(type='AREA', location=(0,3,6)); rim=bpy.context.object; rim.data.energy=800; rim.data.size=3; track(rim,(0,0,3))
# render
sc=bpy.context.scene; sc.render.engine='BLENDER_EEVEE'; sc.render.resolution_x=600; sc.render.resolution_y=700; sc.render.resolution_percentage=100
sc.render.image_settings.file_format='PNG'; out='D:/pets/blender1/cockatiel_preview.png'; sc.render.filepath=out
sc.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath='D:/pets/blender1/cockatiel_cartoon.blend')
bpy.ops.render.render(write_still=True)
print('SAVED',out)


