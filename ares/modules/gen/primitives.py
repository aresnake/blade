from __future__ import annotations

from collections.abc import Sequence

import bmesh
import bpy

from ares.core.turntable import RenderPreset, render_turntable


# ---------------------------------------------------------------------------
# Materials
# ---------------------------------------------------------------------------
def ensure_principled_material(
    name: str = "ARES_Prim_Mat",
    base_color: tuple[float, float, float, float] = (0.8, 0.8, 0.8, 1.0),
) -> bpy.types.Material:
    """Retourne un matériau Principled garanti, crée si absent."""
    mat = bpy.data.materials.get(name)
    if not mat:
        mat = bpy.data.materials.new(name=name)
        mat.use_nodes = True

    nt = mat.node_tree
    nodes = nt.nodes
    links = nt.links

    # Node Principled
    principled = next((n for n in nodes if n.type == "BSDF_PRINCIPLED"), None)
    if principled is None:
        principled = nodes.new("ShaderNodeBsdfPrincipled")
        principled.location = (-200, 0)

    principled.inputs["Base Color"].default_value = base_color

    # Output Material (garanti)
    out = next((n for n in nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None:
        out = nodes.new("ShaderNodeOutputMaterial")
        out.location = (200, 0)

    # Link Surface si non lié
    if not principled.outputs["BSDF"].is_linked:
        links.new(principled.outputs["BSDF"], out.inputs["Surface"])

    return mat


# ---------------------------------------------------------------------------
# Core mesh helper (data-first)
# ---------------------------------------------------------------------------
def _create_mesh_object(
    name: str,
    verts: Sequence[tuple[float, float, float]],
    faces: Sequence[tuple[int, ...]],
) -> bpy.types.Object:
    """Crée un mesh object à partir de listes de vertices/faces (sans bpy.ops)."""
    me = bpy.data.meshes.new(name + "Mesh")
    me.from_pydata(list(verts), [], list(faces))
    me.update()

    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)
    return obj


# ---------------------------------------------------------------------------
# Primitives (data-first)
# ---------------------------------------------------------------------------
def make_cube(
    name: str = "ARES_Cube",
    size: float = 1.0,
    color: tuple[float, float, float, float] = (0.9, 0.6, 0.2, 1.0),
) -> bpy.types.Object:
    """Cube data-first, matériau simple Principled."""
    s = size * 0.5
    verts = [
        (-s, -s, -s),
        (s, -s, -s),
        (s, s, -s),
        (-s, s, -s),
        (-s, -s, s),
        (s, -s, s),
        (s, s, s),
        (-s, s, s),
    ]
    faces = [
        (0, 1, 2, 3),
        (4, 5, 6, 7),
        (0, 1, 5, 4),
        (1, 2, 6, 5),
        (2, 3, 7, 6),
        (3, 0, 4, 7),
    ]
    obj = _create_mesh_object(name, verts, faces)
    mat = ensure_principled_material("ARES_Prim_Mat_Cube", color)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def make_plane(
    name: str = "ARES_Plane",
    size: float = 1.0,
    color: tuple[float, float, float, float] = (0.7, 0.7, 0.7, 1.0),
) -> bpy.types.Object:
    """Plane data-first, matériau simple Principled."""
    s = size * 0.5
    verts = [(-s, -s, 0.0), (s, -s, 0.0), (s, s, 0.0), (-s, s, 0.0)]
    faces = [(0, 1, 2, 3)]
    obj = _create_mesh_object(name, verts, faces)
    mat = ensure_principled_material("ARES_Prim_Mat_Plane", color)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


def make_uvsphere(
    name: str = "ARES_Sphere",
    radius: float = 0.5,
    segments: int = 16,
    rings: int = 8,
    color: tuple[float, float, float, float] = (0.3, 0.6, 0.9, 1.0),
) -> bpy.types.Object:
    """UV Sphere via bmesh (no-ops), matériau simple Principled."""
    me = bpy.data.meshes.new(name + "Mesh")
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(
            bm,
            u_segments=max(8, segments),
            v_segments=max(4, rings),
            radius=radius,
        )
        bm.to_mesh(me)
    finally:
        bm.free()

    me.update()
    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)

    mat = ensure_principled_material("ARES_Prim_Mat_Sphere", color)
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return obj


# ---------------------------------------------------------------------------
# Preview MP4 (headless) — chemin ABSOLU sous <repo>/renders/preview/*.mp4
# ---------------------------------------------------------------------------
def render_preview_mp4(
    repo_root: str,
    seconds: int = 1,
    fps: int = 24,
    res_x: int = 1280,
    res_y: int = 720,
    samples: int = 16,
    out_name: str = "preview",
) -> str:
    """Génère une preview MP4 sous <repo>/renders/preview/<out_name>.mp4 en headless.

    Retourne le chemin absolu du MP4 demandé.
    """
    from pathlib import Path

    root = Path(repo_root).resolve()
    p = (root / "renders" / "preview" / f"{out_name}.mp4").resolve()
    p.parent.mkdir(parents=True, exist_ok=True)

    preset = RenderPreset(res_x=res_x, res_y=res_y, fps=fps, samples=samples)

    render_turntable(
        target=None,
        radius=2.0,
        seconds=seconds,
        fps=fps,
        mp4_path=str(p),
        samples=samples,
        preset=preset,
    )
    return str(p)
