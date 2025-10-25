"""
ARES sandbox: render_orbit.py
- Crée un rig d'orbite simple (360°), caméra TrackTo stricte.
- Auto-sélection de l'engine (EEVEE_NEXT-only OK).
- Rend une animation MP4 en headless, en chemin ABSOLU dans le repo.
Règles Never Again respectées (data-first, TrackTo strict, no active deps).
"""
from __future__ import annotations
from pathlib import Path
import math
import contextlib

import bpy

# ---------- Helpers de base ----------
def repo_root_from_this_file() -> Path:
    # .../ares/sandbox/render_orbit.py  →  repo root = parents[2]
    return Path(__file__).resolve().parents[2]

def enum_render_engines() -> list[str]:
    try:
        prop = bpy.types.RenderSettings.bl_rna.properties["engine"]
        return [e.identifier for e in prop.enum_items]
    except Exception:
        return []

def choose_engine(preferred=("BLENDER_EEVEE","BLENDER_EEVEE_NEXT","CYCLES")) -> str|None:
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
    # Unlink de toutes les collections existantes
    for coll in list(obj.users_collection):
        with contextlib.suppress(Exception):
            coll.objects.unlink(obj)
    # Link unique
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

# ---------- Animation orbit ----------
def animate_orbit(rig: bpy.types.Object, frame_start: int, frame_end: int):
    rig.rotation_mode = "XYZ"
    rig.rotation_euler = (0.0, 0.0, 0.0)
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_start, index=-1)
    rig.rotation_euler = (0.0, 0.0, math.tau)  # 360°
    rig.keyframe_insert(data_path="rotation_euler", frame=frame_end, index=-1)
    # Interpolation linéaire
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
    scn.render.ffmpeg.format = "MPEG4"   # conteneur MP4
    scn.render.ffmpeg.codec = "H264"
    scn.render.ffmpeg.video_bitrate = 6000
    scn.render.ffmpeg.audio_codec = "AAC"
    scn.render.ffmpeg.audio_bitrate = 192
    # Chemin ABSOLU (évite le C:\renders de Blender)
    scn.render.filepath = str(out_path)

def render_animation(frame_start: int, frame_end: int):
    scn = bpy.context.scene
    scn.frame_start = frame_start
    scn.frame_end = frame_end
    scn.frame_current = frame_start
    bpy.ops.render.render(animation=True, use_viewport=False)

# ---------- Main ----------
def main(seconds=4, fps=24, res=(1280, 720), radius=6.0, height=2.0):
    scn = bpy.context.scene

    # Engine auto (EEVEE / EEVEE_NEXT / CYCLES)
    target_engine = choose_engine()
    if target_engine:
        scn.render.engine = target_engine

    # Eevee defaults (safe)
    set_eevee_defaults_if_available()

    # Rig + camera
    rig = ensure_rig()
    cam = ensure_camera(radius=radius, height=height)
    parent(cam, rig)

    # Animation
    frame_start = 1
    frame_end = seconds * fps
    animate_orbit(rig, frame_start, frame_end)

    # Sortie
    root = repo_root_from_this_file()
    out_path = (root / "renders" / "orbit" / "orbit.mp4").resolve()
    set_output_mp4(out_path, fps=fps, res_x=res[0], res_y=res[1])

    # Render
    render_animation(frame_start, frame_end)
    print(f"[ARES] ORBIT_MP4 → {out_path}")
    print(f"[ARES] ENGINE = {scn.render.engine}")

if __name__ == "__main__":
    main()
