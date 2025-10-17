# Blade v13 — Socle & Règles

## Objectif
Base propre v13 pour (re)construire Blade/ARES sans dettes : arbo stricte, hooks qualité, imports sélectifs.

## Règles “Never Again” (résumé)
1) **EEVEE-only** par défaut.  
2) **Pas de dépendance** à active/selected après `bpy.ops`.  
3) **UV Sphere** : utiliser `radius` (jamais `diameter`).  
4) **Track To** : axes stricts `TRACK_NEGATIVE_Z`, `UP_Y`.  
5) **Scene nodes** : ne jamais réassigner `scene.node_tree`.  
6) **Nodes** : liens **Output → Input** uniquement.  
7) **Matériaux** : `ensure_material()` / `assign_material()` ; éviter tout Material supprimé.  
8) **Operators** : pas de `PointerProperty` stocké sur un Operator.  
9) **World/EEVEE** : AO, Bloom, Soft Shadows actifs par défaut.  
10) **Packaging** : imports relatifs valides, `__init__.py` partout.

## Conventions repo
- **.gitattributes** : texte en LF, binaires non normalisés.  
- **Hooks** : pré-commit bloque >50 MB & binaires lourds.  
- **Dossiers lourds** : `datasets/`, `resources/`, `logs/`, `summary/` non versionnés.  
- **Scripts** : PowerShell par défaut (Make/Dev), bash autorisé via Git.

## Dossiers
- `ares/` : add-on & modules (VIDE pour l’instant).  
- `config/` : YAML, presets, FixBook.  
- `tools/` : scripts Dev/Make/CI (non Blender).  
- `tests/` : tests (pytest + headless).  
- `resources/`, `datasets/` : lourds, **hors Git**.  
- `logs/`, `summary/` : sorties locales.  
- `docs/` : documentation.

## Flux
1) Import **sélectif** depuis anciennes versions → nettoyage → tests.  
2) D’abord **config/presets**, puis **helpers**, puis **modules**.  
3) CI locale (scripts) avant CI distante.
