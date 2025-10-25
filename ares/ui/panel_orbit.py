# ares/ui/panel_orbit.py — Panneau & opérateur UI pour lancer l''orbit MP4
# S''appuie sur ares/sandbox/render_orbit.py (CLI déjà en place).

from __future__ import annotations
import importlib
from pathlib import Path
import bpy

# --- Util: resolv repo root depuis ce fichier (au cas où l''outpath est relatif)
def _repo_root_from_this_file() -> Path:
    return Path(__file__).resolve().parents[2]

class ARES_OT_render_orbit(bpy.types.Operator):
    bl_idname = "ares.render_orbit"
    bl_label = "Render Orbit MP4"
    bl_description = "Rend une orbit 360° (MP4) via Eevee/Eevee Next/Cycles"
    bl_options = {"REGISTER", "UNDO"}

    seconds: bpy.props.IntProperty(name="Sec", default=4, min=1, max=120)
    fps: bpy.props.IntProperty(name="FPS", default=24, min=1, max=120)

    res_x: bpy.props.IntProperty(name="Res X", default=1280, min=64, max=8192)
    res_y: bpy.props.IntProperty(name="Res Y", default=720,  min=64, max=8192)

    radius: bpy.props.FloatProperty(name="Rayon", default=6.0, min=0.1, max=1000.0)
    height: bpy.props.FloatProperty(name="Hauteur", default=2.0, min=-1000.0, max=1000.0)

    engine: bpy.props.EnumProperty(
        name="Moteur",
        items=[
            ("AUTO", "Auto", "Choisir automatiquement"),
            ("BLENDER_EEVEE", "EEVEE", "Eevee"),
            ("BLENDER_EEVEE_NEXT", "EEVEE Next", "Eevee Next"),
            ("CYCLES", "Cycles", "Cycles"),
        ],
        default="AUTO",
    )

    outfile: bpy.props.StringProperty(
        name="MP4",
        description="Chemin de sortie (relatif au repo ou absolu)",
        default=str((_repo_root_from_this_file() / "renders" / "orbit" / "orbit.mp4").resolve()),
        subtype="FILE_PATH",
    )

    def execute(self, context):
        # Import du runner CLI existant
        try:
            from ares.sandbox import render_orbit as ro
        except Exception:
            # Permet le dev à chaud si le module n''est pas encore importable, en ajoutant le repo à sys.path
            import sys
            sys.path.append(str(_repo_root_from_this_file()))
            from ares.sandbox import render_orbit as ro

        # Reload pour le dev hot-reload
        ro = importlib.reload(ro)

        # Construire les argv façon CLI
        argv = [
            "--seconds", str(self.seconds),
            "--fps", str(self.fps),
            "--res", f"{self.res_x}x{self.res_y}",
            "--radius", str(self.radius),
            "--height", str(self.height),
            "--outfile", self.outfile,
        ]
        if self.engine != "AUTO":
            argv += ["--engine", self.engine]

        # Appel direct du main(argv) (rend depuis la session courante)
        try:
            ro.main(argv)
        except Exception as e:
            self.report({"ERROR"}, f"Orbit render failed: {e}")
            return {"CANCELLED"}

        self.report({"INFO"}, f"Orbit MP4 écrit: {self.outfile}")
        return {"FINISHED"}


class ARES_PT_orbit_panel(bpy.types.Panel):
    bl_label = "ARES — Orbit MP4"
    bl_idname = "ARES_PT_orbit_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "ARES"

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.prop(context.scene, "ares_orbit_seconds")
        col.prop(context.scene, "ares_orbit_fps")
        col.separator()
        col.prop(context.scene, "ares_orbit_res_x")
        col.prop(context.scene, "ares_orbit_res_y")
        col.separator()
        col.prop(context.scene, "ares_orbit_radius")
        col.prop(context.scene, "ares_orbit_height")
        col.separator()
        col.prop(context.scene, "ares_orbit_engine", text="Moteur")
        col.prop(context.scene, "ares_orbit_outfile")

        op = col.operator("ares.render_orbit", text="Render Orbit MP4", icon="RENDER_ANIMATION")
        op.seconds = context.scene.ares_orbit_seconds
        op.fps = context.scene.ares_orbit_fps
        op.res_x = context.scene.ares_orbit_res_x
        op.res_y = context.scene.ares_orbit_res_y
        op.radius = context.scene.ares_orbit_radius
        op.height = context.scene.ares_orbit_height
        op.engine = context.scene.ares_orbit_engine
        op.outfile = context.scene.ares_orbit_outfile


# --- Props de scène pour mémoriser les valeurs UI ---
def _default_outfile() -> str:
    return str((_repo_root_from_this_file() / "renders" / "orbit" / "orbit.mp4").resolve())

def register():
    from bpy.props import IntProperty, FloatProperty, EnumProperty, StringProperty

    bpy.utils.register_class(ARES_OT_render_orbit)
    bpy.utils.register_class(ARES_PT_orbit_panel)

    bpy.types.Scene.ares_orbit_seconds = IntProperty(name="Sec", default=4, min=1, max=120)
    bpy.types.Scene.ares_orbit_fps = IntProperty(name="FPS", default=24, min=1, max=120)
    bpy.types.Scene.ares_orbit_res_x = IntProperty(name="Res X", default=1920, min=64, max=8192)
    bpy.types.Scene.ares_orbit_res_y = IntProperty(name="Res Y", default=1080, min=64, max=8192)
    bpy.types.Scene.ares_orbit_radius = FloatProperty(name="Rayon", default=6.0, min=0.1, max=1000.0)
    bpy.types.Scene.ares_orbit_height = FloatProperty(name="Hauteur", default=2.0, min=-1000.0, max=1000.0)
    bpy.types.Scene.ares_orbit_engine = EnumProperty(
        name="Moteur",
        items=[
            ("AUTO", "Auto", "Choisir automatiquement"),
            ("BLENDER_EEVEE", "EEVEE", "Eevee"),
            ("BLENDER_EEVEE_NEXT", "EEVEE Next", "Eevee Next"),
            ("CYCLES", "Cycles", "Cycles"),
        ],
        default="AUTO",
    )
    bpy.types.Scene.ares_orbit_outfile = StringProperty(
        name="MP4",
        description="Chemin de sortie (relatif au repo ou absolu)",
        default=_default_outfile(),
        subtype="FILE_PATH",
    )

def unregister():
    for attr in (
        "ares_orbit_seconds","ares_orbit_fps","ares_orbit_res_x","ares_orbit_res_y",
        "ares_orbit_radius","ares_orbit_height","ares_orbit_engine","ares_orbit_outfile"
    ):
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)

    bpy.utils.unregister_class(ARES_PT_orbit_panel)
    bpy.utils.unregister_class(ARES_OT_render_orbit)
