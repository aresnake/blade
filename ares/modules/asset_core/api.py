from pathlib import Path

import bpy


def quick_export_glb(obj, out_path):
    """Export GLB rapide : applique transform & export l'objet sélectionné."""
    if obj is None:
        raise RuntimeError("No active object to export")
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    # Isoler l'objet
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Appliquer transforms (scale/rot)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    bpy.ops.export_scene.gltf(
        filepath=str(p),
        export_format="GLB",
        use_selection=True,
        export_apply=True,
        export_yup=True
    )
    return p
