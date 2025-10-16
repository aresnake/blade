"""
Blade v13 — turntable
- Crée une caméra + contrainte Track To sur une cible.
- Anime une orbite circulaire (yaw) autour de la cible.
- Rend une courte séquence .mp4 via render_bg preset.
"""
import math
import bpy
from ares.helpers import select_engine, create_mesh_object, ensure_material, assign_material, link_object
from ares.modules.render_bg import apply_output_preset

def _ensure_target(name="Turntable_Target"):
    # Un petit empty (mesh minuscule) pour pointer TrackTo
    tgt = bpy.data.objects.get(name)
    if tgt is None:
        tgt = create_mesh_object(name=name, verts=[(0,0,0)], edges=[], faces=[])
    tgt.location = (0.0, 0.0, 0.0)
    return tgt

def _ensure_camera():
    cam = next((o for o in bpy.data.objects if o.type == "CAMERA"), None)
    if cam is None:
        camdata = bpy.data.cameras.new("Camera")
        cam = bpy.data.objects.new("Camera", camdata)
        bpy.context.scene.collection.objects.link(cam)
    if bpy.context.scene.camera is None:
        bpy.context.scene.camera = cam
    return cam

def _track_to(cam, target):
    # Ajoute/normalise une contrainte Track To (axes stricts)
    ct = next((c for c in cam.constraints if c.type == 'TRACK_TO'), None)
    if ct is None:
        ct = cam.constraints.new('TRACK_TO')
    ct.target = target
    ct.track_axis = 'TRACK_NEGATIVE_Z'
    ct.up_axis = 'UP_Y'
    return ct

def render_turntable(target=None, radius=2.5, seconds=4, fps=24, mp4_path="renders/turntable.mp4", samples=32):
    scn = bpy.context.scene
    engine = select_engine(scn)

    # cible & caméra
    tgt = target or _ensure_target()
    cam = _ensure_camera()
    _track_to(cam, tgt)

    # chemin circulaire (keyframes sur la position caméra)
    total_frames = max(1, int(seconds * fps))
    scn.frame_start = 1
    scn.frame_end = total_frames
    for f in (scn.frame_start, scn.frame_end):
        t = (f - scn.frame_start) / max(1, total_frames - 1)
        ang = t * 2.0 * math.pi  # 360°
        x = radius * math.cos(ang)
        y = radius * math.sin(ang)
        z = radius * 0.6
        cam.location = (x, y, z)
        cam.keyframe_insert(data_path="location", frame=f)

    # presets de rendu (mp4)
    apply_output_preset("config/render_output_defaults.yaml")
    scn.render.filepath = mp4_path
    scn.render.fps = int(fps)

    # samples viewport/render (best effort)
    if hasattr(scn, "eevee"):
        try:
            scn.eevee.taa_render_samples = int(samples)
            scn.eevee.taa_samples = min(16, int(samples))
        except Exception:
            pass

    bpy.ops.render.render(animation=True, write_still=False, use_viewport=False)
    print("[TURN] ✅ Render OK ->", scn.render.filepath)
    return scn.render.filepath
