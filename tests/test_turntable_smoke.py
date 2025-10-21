import os
import sys
from pathlib import Path

def test_turntable_smoke(tmp_path=None):
    # --- Setup paths ---
    root = Path(r'D:\V13\workspace_v13')
    sys.path.insert(0, str(root))
    out_dir = root / 'renders' / 'test_turntable'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_mp4 = out_dir / 'smoke.mp4'

    # --- Import core shim ---
    from ares.core import turntable as tt  # stable API

    import bpy

    # --- Force VIDEO output (FFmpeg H.264 + AAC) ---
    scn = bpy.context.scene
    scn.render.filepath = str(out_mp4)           # Blender utilisera bien .mp4 si FFMPEG
    scn.render.image_settings.file_format = 'FFMPEG'
    scn.render.ffmpeg.format = 'MPEG4'           # conteneur MP4
    scn.render.ffmpeg.codec = 'H264'             # codec vidéo
    scn.render.ffmpeg.audio_codec = 'AAC'        # codec audio (même si muet)
    scn.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scn.render.ffmpeg.gopsize = 12
    scn.render.ffmpeg.max_b_frames = 2

    # --- Sujet minimal (data-first cube) ---
    mesh = bpy.data.meshes.new('SmokeMesh')
    mesh.from_pydata(
        [(-.5,-.5,-.5),(.5,-.5,-.5),(.5,.5,-.5),(-.5,.5,-.5),(-.5,-.5,.5),(.5,-.5,.5),(.5,.5,.5),(-.5,.5,.5)],
        [], [(0,1,2,3),(4,5,6,7),(0,1,5,4),(2,3,7,6),(1,2,6,5),(0,3,7,4)]
    )
    mesh.update()
    obj = bpy.data.objects.new('SmokeObj', mesh)
    bpy.context.scene.collection.objects.link(obj)

    # --- Ensure rig (idempotent) ---
    tt.create_turntable_rig(radius=2.5)

    # --- Render 1s @ 24 fps (rapide) ---
    preset = tt.RenderPreset(res_x=1280, res_y=720, fps=24, samples=16)
    tt.render_turntable(
        target=obj, radius=2.5, seconds=1, fps=None,
        mp4_path=str(out_mp4), samples=None, preset=preset
    )

    # --- Assertions ---
    assert out_mp4.exists(), f'mp4 not created: {out_mp4}'
    assert out_mp4.stat().st_size > 0, 'mp4 is empty'
