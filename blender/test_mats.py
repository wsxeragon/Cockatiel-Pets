import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler, Matrix

# Clear all existing objects in scene
bpy.ops.wm.read_factory_settings(use_empty=True)

# -------------------------------------------------------------
# 1. MATERIALS SETUP (Stylized Cartoon Shading)
# -------------------------------------------------------------
def create_material(name, base_color, roughness=0.5, specular=0.5, is_head_gradient=False):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (400, 0)
    
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    if is_head_gradient:
        # Procedural Front Yellow -> Back Grey feather gradient
        tex_coord = nodes.new(type='ShaderNodeTexCoord')
        tex_coord.location = (-600, 0)
        
        mapping = nodes.new(type='ShaderNodeMapping')
        mapping.location = (-400, 0)
        links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
        
        separate_xyz = nodes.new(type='ShaderNodeSeparateXYZ')
        separate_xyz.location = (-220, 0)
        links.new(mapping.outputs['Vector'], separate_xyz.inputs['Vector'])
        
        color_ramp = nodes.new(type='ShaderNodeValToRGB')
        color_ramp.location = (-50, 0)
        # Gradient along Y axis (Front is +Y, Back is -Y)
        color_ramp.color_ramp.elements[0].position = 0.35
        color_ramp.color_ramp.elements[0].color = (0.58, 0.58, 0.62, 1.0) # Back Grey
        color_ramp.color_ramp.elements[1].position = 0.65
        color_ramp.color_ramp.elements[1].color = (0.98, 0.88, 0.38, 1.0) # Front Yellow
        
        links.new(separate_xyz.outputs['Y'], color_ramp.inputs['Fac'])
        links.new(color_ramp.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = base_color

    if 'Roughness' in bsdf.inputs:
        bsdf.inputs['Roughness'].default_value = roughness
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = specular

    return mat

# Material Palette based on reference turnaround
mat_body_grey   = create_material("Mat_Body_Grey",   (0.58, 0.58, 0.62, 1.0), roughness=0.55)
mat_body_belly  = create_material("Mat_Body_Belly",  (0.68, 0.68, 0.72, 1.0), roughness=0.55)
mat_head        = create_material("Mat_Head",        (0.98, 0.88, 0.38, 1.0), roughness=0.5, is_head_gradient=True)
mat_crest       = create_material("Mat_Crest",       (0.98, 0.87, 0.34, 1.0), roughness=0.5)
mat_cheek       = create_material("Mat_Cheek",       (0.98, 0.38, 0.20, 1.0), roughness=0.6)
mat_beak        = create_material("Mat_Beak",        (0.62, 0.56, 0.54, 1.0), roughness=0.45)
mat_nostril     = create_material("Mat_Nostril",     (0.40, 0.36, 0.35, 1.0), roughness=0.6)
mat_eye_pupil   = create_material("Mat_Eye_Pupil",   (0.04, 0.04, 0.05, 1.0), roughness=0.05, specular=0.9)
mat_eye_shine   = create_material("Mat_Eye_Shine",   (1.00, 1.00, 1.00, 1.0), roughness=0.1)
mat_wing_grey   = create_material("Mat_Wing_Grey",   (0.54, 0.54, 0.58, 1.0), roughness=0.55)
mat_wing_white  = create_material("Mat_Wing_White",  (0.96, 0.96, 0.97, 1.0), roughness=0.45)
mat_tail_grey   = create_material("Mat_Tail_Grey",   (0.42, 0.42, 0.46, 1.0), roughness=0.55)
mat_feet        = create_material("Mat_Feet",        (0.60, 0.50, 0.50, 1.0), roughness=0.5)

print("Materials created successfully!")
