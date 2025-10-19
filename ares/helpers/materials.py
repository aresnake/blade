from __future__ import annotations

import bpy


def ensure_material(name: str) -> bpy.types.Material:
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if not mat.use_nodes:
        mat.use_nodes = True
    return mat


def assign_material(obj: bpy.types.Object, mat: bpy.types.Material):
    data = getattr(obj, "data", None)
    mats = getattr(data, "materials", None)
    if mats is not None and mat.name not in [m.name for m in mats]:
        mats.append(mat)


def create_principled_setup(mat: bpy.types.Material):
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    out = nt.nodes.get("Material Output")
    if bsdf:
        bsdf.location = (0, 0)
    has_link = any(
        (link.to_node == out) and (link.to_socket.name == "Surface")
        for link in nt.links
    )
    if not has_link:
        nt.links.new(bsdf.outputs.get("BSDF"), out.inputs.get("Surface"))
