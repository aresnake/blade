import os
import sys

import pytest

# Repo root = dossier parent de /tools
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)

# Évite un import venant d'un add-on utilisateur
sys.modules.pop("ares", None)

# Ex.: blender.exe -b --python tools/_pytest_in_blender.py -- -q -k test_public_api
# tout ce qui suit le `--` est passé à pytest
pytest_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["-q"]
raise SystemExit(pytest.main(pytest_args))
