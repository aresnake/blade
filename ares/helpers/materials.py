# Blade v13 — helpers.materials
# Never Again: toujours garantir un Material Output et éviter toute référence supprimée.
import bpy


def ensure_material(name="Material", use_nodes=True):
    """Retourne un matériau existant ou en crée un propre (nodes optionnels)."""
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name=name)
    mat.use_nodes = bool(use_nodes)
    if mat.use_nodes and mat.node_tree:
        # Garantir l'existence d'un Material Output
        nt = mat.node_tree
        out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
        if out is None:
            out = nt.nodes.new("ShaderNodeOutputMaterial")
            out.location = (300, 0)
        # Garantir un BSDF Principled minimal
        bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
        if bsdf is None:
            bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
            bsdf.location = (0, 0)
        # Lien Output ← Principled si non relié
        has_link = any(link.to_node == out and link.to_socket.name == "Surface" for link in nt.links)
        if not has_link:
            nt.links.new(bsdf.outputs.get("BSDF"), out.inputs.get("Surface"))
    return mat

def assign_material(obj, mat, slot_index=0):
    """Assigne mat à obj (crée slot si besoin) sans pointer des matériaux supprimés."""
    if obj is None or mat is None:
        return False
    if obj.type != "MESH":
        # On autorise l'assign sur autre type, mais en général on vise du MESH
        pass
    # Créer le slot si nécessaire
    if slot_index >= len(obj.material_slots):
        # ajouter des slots jusqu'à l'index demandé
        for _ in range(slot_index - len(obj.material_slots) + 1):
            obj.data.materials.append(None)
    obj.material_slots[slot_index].material = mat
    return True
