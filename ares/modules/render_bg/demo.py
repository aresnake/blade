"""
Blade v13 — render_bg demo
- Construit une mini scène (caméra+light+triangle mesh data-first).
- Applique preset FFMPEG mp4 (H.264 + AAC).
- Rend une mini animation (5 frames) en headless.
"""
import bpy
from mathutils import Vector
from ares.helpers import select_engine, create_mesh_object, ensure_material, assign_material
from ares.modules.render_bg import apply_output_preset

def _ensure_camera():
    cam = next((o for o in bpy.data.objects if o.type == "CAMERA"), None)
    if cam is None:
        camdata = bpy.data.cameras.new("Camera")
        cam = bpy.data.objects.new("Camera", camdata)
        bpy.context.scene.collection.objects.link(cam)
    cam.location = (2.2, -2.2, 1.6)
    cam.rotation_euler = (1.05, 0.0, 0.85)
    if bpy.context.scene.camera is None:
        bpy.context.scene.camera = cam
    return cam

def _ensure_light():
    lamp = next((o for o in bpy.data.objects if o.type == "LIGHT"), None)
    if lamp is None:
        ldata = bpy.data.lights.new("Key", type="AREA")
        lamp = bpy.data.objects.new("Key", ldata)
        bpy.context.scene.collection.objects.link(lamp)
    lamp.location = (1.2, -0.7, 2.0)
    lamp.data.energy = 800
    return lamp

def _ensure_triangle():
    obj = bpy.data.objects.get("V13_Triangle")
    if obj is None:
        obj = create_mesh_object(
            name="V13_Triangle",
            verts=[(0,0,0),(1.1,0,0),(0.1,0.9,0)],
            edges=[(0,1),(1,2),(2,0)],
            faces=[(0,1,2)],
        )
        mat = ensure_material("V13_Mat")
        assign_material(obj, mat, slot_index=0)
    obj.location = (0,0,0)
    return obj

def render_demo(mp4_path="//renders/out.mp4", frame_count=5, fps=24):
    scn = bpy.context.scene
    engine = select_engine(scn)  # EEVEE / EEVEE_NEXT / fallback

    # caméra + lumière + objet
    _ensure_camera()
    _ensure_light()
    tri = _ensure_triangle()

    # animation courte (rotation simple)
    scn.frame_start = 1
    scn.frame_end = max(1, int(frame_count))
    tri.rotation_euler = (0.0, 0.0, 0.0)
    tri.keyframe_insert(data_path="rotation_euler", frame=scn.frame_start)
    tri.rotation_euler = (0.0, 0.0, 1.0)
    tri.keyframe_insert(data_path="rotation_euler", frame=scn.frame_end)

    # format sortie mp4
    res = apply_output_preset("config/render_output_defaults.yaml")
    # forcer le chemin (respecte preset/extension)
    scn.render.filepath = mp4_path
    scn.render.fps = int(fps)

    # sécurité: éviter écrasement concurrent → pas nécessaire ici (headless single run)
    print("[RENDER_BG_DEMO] engine:", engine)
    print("[RENDER_BG_DEMO] preset:", res)
    print("[RENDER_BG_DEMO] output:", scn.render.filepath, "fps:", scn.render.fps, "frames:", scn.frame_start, "→", scn.frame_end)

    # lancer rendu (animation)
    bpy.ops.render.render(animation=True, write_still=False, use_viewport=False)
    print("[RENDER_BG_DEMO] ✅ Render OK")
    return scn.render.filepath
