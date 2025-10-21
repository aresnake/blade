from __future__ import annotations
from pathlib import Path
from typing import Sequence, Tuple

import bpy
import bmesh

# --- Materials ---
def ensure_principled_material(name: str = "ARES_Prim_Mat",
                               base_color: Tuple[float, float, float, float] = (0.8,0.8,0.8,1.0)) -> bpy.types.Material:
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name)
        mat.use_nodes = True
    nt = mat.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf is None:
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        nt.links.new(bsdf.outputs['BSDF'], next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), nt.nodes.new('ShaderNodeOutputMaterial')).inputs['Surface'])
    bsdf.inputs['Base Color'].default_value = base_color
    return mat

# --- Core mesh helper ---
def _create_mesh_object(name: str,
                        verts: Sequence[Tuple[float,float,float]],
                        faces: Sequence[Tuple[int,...]]) -> bpy.types.Object:
    me = bpy.data.meshes.new(name + "Mesh")
    me.from_pydata(list(verts), [], list(faces))
    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj

# --- Primitives (data-first) ---
def make_cube(name: str = "ARES_Cube", size: float = 1.0,
              color: Tuple[float,float,float,float] = (0.9,0.6,0.2,1.0)) -> bpy.types.Object:
    s = size * 0.5
    verts = [(-s,-s,-s),(s,-s,-s),(s,s,-s),(-s,s,-s),(-s,-s,s),(s,-s,s),(s,s,s),(-s,s,s)]
    faces = [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]
    obj = _create_mesh_object(name, verts, faces)
    mat = ensure_principled_material("ARES_Prim_Mat_Cube", color)
    obj.data.materials.clear(); obj.data.materials.append(mat)
    return obj

def make_plane(name: str = "ARES_Plane", size: float = 1.0,
               color: Tuple[float,float,float,float] = (0.7,0.7,0.7,1.0)) -> bpy.types.Object:
    s = size * 0.5
    verts = [(-s,-s,0),(s,-s,0),(s,s,0),(-s,s,0)]
    faces = [(0,1,2,3)]
    obj = _create_mesh_object(name, verts, faces)
    mat = ensure_principled_material("ARES_Prim_Mat_Plane", color)
    obj.data.materials.clear(); obj.data.materials.append(mat)
    return obj

def make_uvsphere(name: str = "ARES_Sphere", radius: float = 0.5, segments: int = 16, rings: int = 8,
                  color: Tuple[float,float,float,float] = (0.3,0.6,0.9,1.0)) -> bpy.types.Object:
    me = bpy.data.meshes.new(name + "Mesh")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=max(8, segments), v_segments=max(4, rings), radius=radius)
    bm.to_mesh(me); bm.free()
    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    mat = ensure_principled_material("ARES_Prim_Mat_Sphere", color)
    obj.data.materials.clear(); obj.data.materials.append(mat)
    return obj

# --- Quick preview via core turntable shim ---
def quick_preview_turntable(obj: bpy.types.Object,
                            seconds: int = 1,
                            fps: int = 24,
                            radius: float = 2.5,
                            samples: int = 16,
                            out_mp4: str | None = None) -> str:
    from ares.core import turntable as tt
    import os
    if out_mp4 is None:
        base = Path(bpy.path.abspath("//renders/preview"))
        base.mkdir(parents=True, exist_ok=True)
        out_mp4 = str(base / f"{obj.name}_preview.mp4")
    tt.create_turntable_rig(radius=radius)
    preset = tt.RenderPreset(res_x=1280, res_y=720, fps=fps, samples=samples)
    tt.render_turntable(target=obj, radius=radius, seconds=seconds, fps=fps, mp4_path=out_mp4, samples=samples, preset=preset)
    return out_mp4
