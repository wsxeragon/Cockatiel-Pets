import bpy, math
from mathutils import Vector
p=r'D:\pets\blender\cockatiel.blend'; bpy.ops.wm.open_mainfile(filepath=p)
# remove adjustment wing/bib objects
for o in list(bpy.data.objects):
    if o.name.startswith('Adj_Wing') or o.name=='Adj_Bib': bpy.data.objects.remove(o,do_unlink=True)
mg=bpy.data.materials.get('Mat_Wing_Grey'); mw=bpy.data.materials.get('Mat_Wing_White'); mt=bpy.data.materials.get('Mat_Tail_Grey')
def smooth(o):
  [setattr(f,'use_smooth',True) for f in o.data.polygons]
def uv(name,loc,scale,mat):
 bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=14,location=loc);o=bpy.context.object;o.name=name;o.scale=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);smooth(o)
for s in (-1,1):
 for j,(z,w,h,mat) in enumerate([(1.18,.24,.14,mw),(1.02,.27,.15,mg),(.86,.29,.15,mg),(.70,.30,.14,mt)]): uv(f'Adj_Wing_{s}_{j}',(s*(.56+.035*j),0.02,z),(w,.24,h),mat)
# camera straight front slightly above
cam=bpy.data.objects.get('Main_Camera');cam.location=(0,-6.6,2.25);t=Vector((0,0.15,1.25));cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=60
# richer colors
for n,c in [('Mat_Head',(0.95,0.62,0.08,1)),('Mat_Body_Grey',(0.32,0.34,0.38,1)),('Mat_Wing_Grey',(0.25,0.27,0.31,1)),('Mat_Wing_White',(0.82,0.82,0.78,1)),('Mat_Tail_Grey',(0.20,0.22,0.26,1)),('Mat_Cheek',(0.95,0.16,0.04,1))]:
 m=bpy.data.materials.get(n)
 if m and m.use_nodes:
  bs=m.node_tree.nodes.get('Principled BSDF');
  if bs: bs.inputs['Base Color'].default_value=c
sc=bpy.context.scene;sc.view_settings.exposure=-0.4
if sc.world and sc.world.use_nodes: sc.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.18
sc.render.filepath=r'D:\pets\blender\cockatiel_preview.png';bpy.ops.wm.save_as_mainfile(filepath=p);bpy.ops.render.render(write_still=True)
