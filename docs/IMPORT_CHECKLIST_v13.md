# ✅ Blade v13 — Import Checklist (par module / par lot)

## 0) Pré-vol
- [ ] Source identifiée (chemin exact) et **taille totale** < 50 MB commitables.
- [ ] Licences/credits OK (pas de contenu tiers non autorisé).
- [ ] Scan secrets (mots de passe, tokens) → rien à purger.
- [ ] Arbo cible définie (`ares/`, `config/`, `tools/`, `tests/`, `docs/`).

## 1) Normalisation fichiers
- [ ] Encodage **UTF-8** (sans BOM) — vérifier fichiers texte.
- [ ] Fin de ligne **LF** (géré par .gitattributes).
- [ ] Pas de binaires lourds dans Git ( `.blend`, `.zip`, `.mp4` → hors repo).

## 2) Placement & renommage
- [ ] Fichiers placés dans le **dossier adéquat** (code → `ares/`, presets → `config/`, scripts → `tools/`, tests → `tests/`).
- [ ] Nommage clair et **imports relatifs** valides (`__init__.py` présents).
- [ ] Chemins constants (aucun chemin absolu dur codé).

## 3) Qualité & “Never Again”
- [ ] Pas de dépendance à `bpy.context.active_object/selected` après `bpy.ops`.
- [ ] UV Sphere → `radius` (jamais `diameter`).
- [ ] Track To → `TRACK_NEGATIVE_Z` / `UP_Y`.
- [ ] Scene nodes → **ne pas** réassigner `scene.node_tree`.
- [ ] Nodes → liens **Output → Input** uniquement.
- [ ] Matériaux → `ensure_material()` / `assign_material()` ; pas de Material supprimé.
- [ ] World/EEVEE → AO, Bloom, Soft Shadows activés par défaut via presets.
- [ ] Aucune `PointerProperty` stockée sur un Operator.

## 4) Dépendances & config
- [ ] Aucun import fantôme (modules inexistants).
- [ ] Options Blender fixées par **helpers/presets** (pas de magie dans les opérateurs).
- [ ] Variables d’environnement documentées si nécessaires.

## 5) Tests (headless)
- [ ] Ajout d’un **smoke test** (`tests/…`) exécutable en headless.
- [ ] Commande PowerShell prête (ex: `blender -b --python tests/<script>.py`).
- [ ] Sortie test claire (OK/FAIL + logs minimalistes).

## 6) Documentation
- [ ] Section dans `docs/` (but, limites, usage).
- [ ] Exemple d’appel minimal (script ou pas-à-pas).
- [ ] Points de vigilance (contexts, poll(), fallback API data-first).

## 7) Commit & push
- [ ] Commit **cohérent et complet** (pas de WIP, pas de diff partiel).
- [ ] Message clair: `feat(module): <résumé>` ou `chore(config): …`.
- [ ] `git push` OK, hook pré-commit **vert**.

## 8) After-import (rapide)
- [ ] Ajout à la **roadmap** (ce qui reste à faire).
- [ ] TODO techniques listés (petites dettes acceptées et tracées).
- [ ] Ticket / note dans `docs/IMPORT_PLAN_v13.md` mis à jour si nécessaire.
