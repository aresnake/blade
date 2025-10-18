import json
import math
import os
import sys

import bpy

# output path from argv after "--"
argv = sys.argv
out = argv[argv.index("--") + 1] if "--" in argv else os.path.join(os.getcwd(), "sanity.png")

# fresh scene
bpy.ops.wm.read_homefile(use_empty=True)

# robust engine select: prefer EEVEE_NEXT else fallback to CYCLES
engine_items = bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items.keys()
bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in engine_items else "CYCLES"

# eevee quality toggles (safe even if engine=fallback)
ee = bpy.context.scene.eevee
if hasattr(ee, "use_bloom"):
    ee.use_bloom = True
if hasattr(ee, "use_gtao"):
    ee.use_gtao = True

# resolution
bpy.context.scene.render.resolution_x = 640
bpy.context.scene.render.resolution_y = 480

# units
bpy.context.scene.unit_settings.system = "METRIC"
bpy.context.scene.unit_settings.scale_length = 1.0

# objects: sun + camera + cube
bpy.ops.object.light_add(type="SUN", location=(4, -4, 6))
bpy.ops.object.camera_add(location=(3, -3, 2), rotation=(math.radians(65), 0, math.radians(45)))
bpy.context.scene.camera = bpy.context.object
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0.0, 0.0, 0.0))
cube = bpy.context.object
cube.name = "ARES_SANITY_CUBE"

# simple principled material
mat = bpy.data.materials.new("mat_base")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
if bsdf:
    bsdf.inputs["Roughness"].default_value = 0.35
cube.data.materials.append(mat)

# proof JSON
proof = {
    "version": bpy.app.version_string,
    "engine": bpy.context.scene.render.engine,
    "units": "METERS",
    "objects": sorted(o.name for o in bpy.data.objects),
    "ok": True,
}
json_path = out.replace(".png", ".json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(proof, f, ensure_ascii=False, indent=2)

# render still
bpy.context.scene.render.filepath = out
bpy.ops.render.render(write_still=True)
print("[SANITY] wrote", out, "and", json_path)
