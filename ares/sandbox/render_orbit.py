"""
ARES sandbox: render_orbit.py (CLI)
- Args: --seconds --fps --res 1280x720 --radius --height --outfile --engine
- Crée un rig d'orbite (360°), caméra TrackTo stricte.
- Rend une animation MP4 en headless (FFMPEG H.264 + AAC).
- Respect "Never Again": data-first, TrackTo strict, no active deps.
"""
from __future__ import annotations
from pathlib import Path
import argparse
import contextlib
import math
import sys

import bpy


# ---------- Helpers ----------
def repo_root_from_this_file() -> Path:
    # .../ares/sandbox/render_orbit.py  →  repo root = parents[2]
    return Path(__file__).resolve().parents[2]


def enum_render_engines() -> list[str]:
    try:
        prop = bpy.types.RenderSettings.bl_rna.properties["engine"]
        return [e.identifier for e in prop.enum_items]
    except Exception:
        return []


def choose_engine(preferred=("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES")) -> str | None:
    avail = enum_render_engines()
    for eng in preferred:
        if eng in avail:
            return eng
    return avail[0] if avail else None


def ensure_collection(name: str) -> bpy.types.Collection:
    coll = bpy.data.collections.get(name)
    if not coll:
        coll = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(coll)
    return coll


def link_only_to_collection(obj: bpy.types.Object, collection: bpy.types.Collection) -> bpy.types.Object:
    for coll in list(obj.users_collection):
        with contextlib.suppress(Exception):
            coll.objects.unlink(obj)
    if obj.name not in collection.objects:
        collection.objects.link(obj)
    return obj


def ensure_object(obj: bpy.types.Object, collection_name="ARES") -> bpy.types.Object:
    coll = ensure_collection(collection_name)
    return link_only_to_collection(obj, coll)


def set_eevee_defaults_if_available():
    eevee = getattr(bpy.context.scene, "eevee", None)
    if not eevee:
        return
    for attr, val in (("use_gtao", True), ("use_bloom", True), ("use_soft_shadows", True)):
        with contextlib.suppress(Exception):
            setattr(eevee, attr, val)


# ---------- Construction scène ----------
def ensure_target(name="ARES_Target") -> bpy.types.Object:
    tgt = bpy.data.objects.get(name)
    if tgt:
        return ensure_object(tgt)
    tgt = bpy.data.objects.new(name, None)
    tgt.empty_display_type = "PLAIN_AXES"
    tgt.location = (0.0, 0.0, 0.0)
    return ensure_object(tgt)


def ensure_camera(name="ARES_Cam", radius=6.0, height=2.0) -> bpy.types.Object:
    cam = bpy.data.objects.get(name)
    if not cam:
        cam_data = bpy.data.cameras.new(name)
        cam = bpy.data.objects.new(name, cam_data)
    cam.location = (radius * 0.707, -radius * 0.707, height)
    ensure_object(cam)
    # Track-To strict
    tgt = ensure_target()
    cns = next((c for c in cam.constraints if c.type == "TRACK_TO"), None)
    if not cns:
        cns = cam.constraints.new("TRACK_TO")
    cns.target = tgt
    cns.track_axis = "TRACK_NEGATIVE_Z"
    cns.up_axis = "UP_Y"
    bpy.context.scene.camera = cam
    return cam


def ensure_rig(name="TT_Rig") -> bpy.types.Object:
    rig = bpy.data.objects.get(name)
    if not rig:
        rig = bpy.data.objects.new(name, None)
        rig.empty_display_type = "PLAIN_AXES"
        rig.location = (0.0, 0.0, 0.0)
    return ensure_object(rig)


def parent(child: bpy.types.Object, parent_obj: bpy.types.Object):
    with contextlib.suppress(Exception):
        child.parent = parent_obj


# ---------- Animation ----------
def animate_orbit(rig: bpy.types.Object, frame_start: int, frame_end: int):
    rig.rotation_mode = "XYZ"
    rig.rotation_euler = (0.0, 0.0, 0.0)
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_start, index=-1)
    rig.rotation_euler = (0.0, 0.0, math.tau)  # 360°
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_end, index=-1)
    # Interpolation linéaire
    if rig.animation_data and rig.animation_data.action:
        for fcurves in rig.animation_data.action.fcurves:
            for kp in fcurves.keyframe_points:
                kp.interpolation = "LINEAR"


# ---------- Sortie & rendu ----------
def set_output_mp4(out_path: Path, fps: int, res_x: int, res_y: int):
    scn = bpy.context.scene
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scn.render.resolution_x = res_x
    scn.render.resolution_y = res_y
    scn.render.fps = fps
    scn.render.image_settings.file_format = "FFMPEG"
    scn.render.ffmpeg.format = "MPEG4"   # MP4
    scn.render.ffmpeg.codec = "H264"
    scn.render.ffmpeg.video_bitrate = 6000
    scn.render.ffmpeg.audio_codec = "AAC"
    scn.render.ffmpeg.audio_bitrate = 192
    scn.render.filepath = str(out_path)


def render_animation(frame_start: int, frame_end: int):
    scn = bpy.context.scene
    scn.frame_start = frame_start
    scn.frame_end = frame_end
    scn.frame_current = frame_start
    bpy.ops.render.render(animation=True, use_viewport=False)


# ---------- CLI ----------
def parse_res(res_str: str) -> tuple[int, int]:
    # "1920x1080" → (1920,1080)
    try:
        x, y = res_str.lower().split("x")
        return int(x), int(y)
    except Exception as e:
        raise argparse.ArgumentTypeError(f"Résolution invalide: '{res_str}' (attendu: LxH ex 1280x720)") from e


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description="ARES Orbit MP4 headless")
    parser.add_argument("--seconds", type=int, default=4, help="Durée en secondes (défaut: 4)")
    parser.add_argument("--fps", type=int, default=24, help="Images/seconde (défaut: 24)")
    parser.add_argument("--res", type=parse_res, default=(1280, 720), help="Résolution LxH, ex 1280x720")
    parser.add_argument("--radius", type=float, default=6.0, help="Rayon d'orbite caméra (défaut: 6.0)")
    parser.add_argument("--height", type=float, default=2.0, help="Hauteur caméra (défaut: 2.0)")
    parser.add_argument("--outfile", type=str, default="renders/orbit/orbit.mp4", help="Chemin de sortie relatif ou absolu")
    parser.add_argument("--engine", type=str, choices=["BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "CYCLES"], default=None, help="Force le moteur (sinon auto)")
    args = parser.parse_args(argv)

    scn = bpy.context.scene

    # Engine
    target_engine = args.engine or choose_engine()
    if target_engine:
        scn.render.engine = target_engine

    # Eevee toggles
    set_eevee_defaults_if_available()

    # Rig + camera
    rig = ensure_rig()
    cam = ensure_camera(radius=args.radius, height=args.height)
    parent(cam, rig)

    # Animation
    frame_start = 1
    frame_end = args.seconds * args.fps
    animate_orbit(rig, frame_start, frame_end)

    # Sortie (résout en ABS dans le repo si chemin relatif)
    out_path = Path(args.outfile)
    if not out_path.is_absolute():
        out_path = (repo_root_from_this_file() / out_path).resolve()
    set_output_mp4(out_path, fps=args.fps, res_x=args.res[0], res_y=args.res[1])

    # Render
    render_animation(frame_start, frame_end)
    print(f"[ARES] ORBIT_MP4 → {out_path}")
    print(f"[ARES] ENGINE = {scn.render.engine}")


if __name__ == "__main__":
    main()
