# Plan d'import v13 (sélectif)

## Sources locales
- D:\BLADE
- D:\V9
- D:\V10
- D:\BLAST
- Archives ZIP validées

## Ordre d'import (par lots)
1) **Config minimal** → `config/`
   - presets EEVEE/WORLD (yaml)
   - squelette FixBook (règles stables)
2) **Tools neutres** → `tools/`
   - Make helpers (packaging, verifs)
   - Lint/format (flake8/black cfg si besoin)
3) **Tests headless** → `tests/`
   - scaffolding pytest
   - scripts `blender -b --python ...` (smoke tests)
4) **Helpers Blender stables** → `ares/`
   - ensure_material(), link_object(), safe_set(), etc. (API data-first)
5) **Modules validés** (un par un)
   - citybot / animalgen / aura fx / render-bg…
   - pipeline: import → refonte légère → test → doc

## Exclusions initiales
- `.blend`, vidéos, archives → **hors Git** (resources/ local).
- Expérimentations instables non reproductibles.
- Dépendances non documentées.

## Definition of Done (DoD)
- Fichier complet (pas de diff partiel), docstring, tests min., lint OK.
- Respect “Never Again” + helpers communs.
- Script de test headless associé + sortie claire.
