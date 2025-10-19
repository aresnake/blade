# SPDX-License-Identifier: MIT
# Path: ares/modules/render_bg/preset.py

import contextlib

import bpy


def _select_engine(scn: bpy.types.Scene) -> None:
    """Choisit un moteur dispo, par ordre de préférence: EEVEE, EEVEE_NEXT, CYCLES."""
    enum_items = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items
    engines = {item.identifier for item in enum_items}

    target = None
    if "BLENDER_EEVEE" in engines:
        target = "BLENDER_EEVEE"
    elif "BLENDER_EEVEE_NEXT" in engines:
        target = "BLENDER_EEVEE_NEXT"
    elif "CYCLES" in engines:
        target = "CYCLES"

    if target:
        scn.render.engine = target


def apply_mp4_preset(scene: bpy.types.Scene):
    """Applique un preset MP4 (H.264) minimal et retourne les paramètres clefs."""
    scn = scene

    # Moteur (robuste à la version)
    _select_engine(scn)

    # Sortie vidéo MP4 H.264
    r = scn.render
    r.image_settings.file_format = "FFMPEG"
    ff = r.ffmpeg
    ff.format = "MPEG4"
    ff.codec = "H264"

    # Audio optionnel (si support dispo)
    with contextlib.suppress(Exception):
        ff.audio_codec = "AAC"

    # Valeurs par défaut (UI peut les surcharger ensuite)
    return {"filepath": "//renders/out.mp4", "fps": 24, "seconds": 4}
