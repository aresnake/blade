from __future__ import annotations

import bpy


def ensure_material(name: str) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if not mat.use_nodes:
        mat.use_nodes = True
    return mat


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material):
    if obj.data and hasattr(obj.data, "materials"):
        if mat.name not in [m.name for m in obj.data.materials]:
            obj.data.materials.append(mat)


def create_principled_setup(mat: bpy.types.Material):
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    out = nt.nodes.get("Material Output")
    if bsdf:
        bsdf.location = (0, 0)
    # Lien Output ← Principled si non relié
    has_link = any(
        (link.to_node == out) and (link.to_socket.name == "Surface")
        for link in nt.links
    )
    if not has_link:
        nt.links.new(bsdf.outputs.get("BSDF"), out.inputs.get("Surface"))
