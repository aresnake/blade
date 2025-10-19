from __future__ import annotations

import bpy

from ares.helpers import select_engine


def render_demo():
    scn = bpy.context.scene
    engine = select_engine(scn)
    res = (scn.render.resolution_x, scn.render.resolution_y)

    print("[RENDER_BG_DEMO] engine:", engine)
    print("[RENDER_BG_DEMO] preset:", res)
    print("[RENDER_BG_DEMO] output:", scn.render.filepath)
    print(
        "[RENDER_BG_DEMO] fps/frames:",
        scn.render.fps,
        (scn.frame_start, "→", scn.frame_end),
    )

    # lancer rendu (animation)
    bpy.ops.render.render(animation=True)
