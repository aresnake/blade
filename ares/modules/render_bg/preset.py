# SPDX-License-Identifier: MIT
# Path: ares/modules/render_bg/preset.py

import bpy

def apply_mp4_preset(scene: bpy.types.Scene):
    """Applique un preset MP4 (H.264) minimal et retourne les paramètres clefs."""
    scn = scene

    # Moteur (ARES / Never Again)
    scn.render.engine = "BLENDER_EEVEE"

    # Sortie vidéo MP4 H.264
    r = scn.render
    r.image_settings.file_format = "FFMPEG"
    ff = r.ffmpeg
    ff.format = "MPEG4"
    ff.codec = "H264"
    # Audio optionnel (si piste audio)
    try:
        ff.audio_codec = "AAC"
    except Exception:
        pass

    # Valeurs par défaut (UI peut les surcharger ensuite)
    defaults = {
        "filepath": "//renders/out.mp4",
        "fps": 24,
        "seconds": 4,
    }

    # NE PAS fixer le filepath ici: l'UI le posera juste après
    # (on retourne les valeurs pour que l'appelant décide)
    return defaults
