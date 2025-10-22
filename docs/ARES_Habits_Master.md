# ARES Habits Master — Règles & Réflexes Pro (v2025-10-20)

> Standard pro Blade/ARES — Blender **4.5.x LTS** — Mode **Shell-First** — Repo **v13** : `D:\V13\workspace_v13`

---

## 0) Daily (5 min)
- `cd D:\V13\workspace_v13`
- Blender: `D:\blender-4.5.3-windows-x64\blender.exe` (alias `bl` si défini)
- `git status` (**q** pour quitter un pager)
- Smoke tests (py_compile) ou headless rapide via tools
- Lire `logs/` si doute ; viser **1 livrable concret/jour**

---

## 1) Tech (Python/Addon)
- Un fichier = une responsabilité ; imports relatifs ; `__init__.py` partout
- Docstrings standard ; **logs > print** ; pas de magic numbers (constantes/enums)
- Idempotence ; fallbacks explicites (créer si manquant)
- Tests rejouables (headless) ; artefacts dans `dist/`, `logs/`, `summary/`

---

## 2) Blender 4.5.x “Never Again”
- **Data-first, Ops-last** : privilégier `bpy.data`/`bmesh`, éviter `bpy.ops` (contexte fragile)
- Pas de dépendance à `active_object/selected` post-ops ; récupérer la ref immédiatement
- **EEVEE** par défaut ; TrackTo strict: `TRACK_NEGATIVE_Z`, `UP_Y`
- Ne pas réassigner `scene.node_tree` ; `scene.use_nodes = True` puis modifier
- Nodes: **Output → Input** uniquement ; Materials: garantir **Material Output**
- `safe_set()` pour props instables ; animer via **ShaderNodeMath** intermédiaire
- Lighting par défaut (Sun rim + Area fill + World simple) ; **Filmic**
- Contact au sol: Z offset −0.003…−0.005 m

---

## 3) Workflow (Shell-First)
- Toujours préciser **console + `cd`** ; bloc unique prêt à coller ; `Ctrl+C` si bloqué
- Packaging propre (pas de caches dans ZIP)
- Commits atomiques ; courte revue avant push ; tags clairs

---

## 4) Tests headless (rapide)
- Scénarios minimaux (objet actif, matériau, nodes) pour éviter faux positifs
- Export JUnit si possible ; résumés dans `summary/`

---

## 5) Turntable standard ARES
- Empty **TT_Rig** + NURBS **TT_Path** (Follow Path) ; caméra parente ; Track-To strict
- Sortie **.mp4 H.264 + AAC** (FFmpeg interne) ; variante 20 images “worksheet”

---

## 6) FixBook (erreurs → solutions)
- Chaque erreur consignée : *problem → cause → guard → fix → test*
- Helpers: `safe_set`, `link_if`, `ensure_*`, `find_or_create_*` ; mini-tests en preuve

---

## 7) IA / Codex
- Structurer en **Intent → Action → Résultat** ; logs enrichis (observabilité)
- Pas d’override silencieux des banques vocales ; dériver vers `intents_pending.yaml`

---

## 8) Clore une session proprement
- Bilan = fait + artefacts (paths) + tests verts ; une seule **prochaine étape** claire