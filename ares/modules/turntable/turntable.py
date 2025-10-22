from __future__ import annotations

import bpy

from ares.helpers import select_engine
from ares.modules.turntable_gen import create_turntable


def render_turntable(
    target=None,
    radius: float = 2.5,
    seconds: int = 4,
    fps: int = 24,
    mp4_path: str = "renders/turntable.mp4",
    samples: int = 32,
):
    scn = bpy.context.scene
    select_engine(scn)

    ct = create_turntable(radius=radius)
    if target is not None:
        # si un objet cible est donné, on l'utilise comme focus
        pass

    # setup sortie
    scn.render.filepath = mp4_path
    scn.render.fps = fps
    scn.frame_start = 1
    scn.frame_end = seconds * fps

    with bpy.context.temp_override(area=None, region=None, window=None):
        bpy.ops.render.render(animation=True)

    return ct
