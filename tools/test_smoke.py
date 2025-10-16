# -*- coding: utf-8 -*-
import os, sys, json, importlib
BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE not in sys.path:
    sys.path.insert(0, BASE)

try:
    import ares  # pris depuis BASE/ares
    importlib.reload(ares)
    from ares.modules import turntable_gen as tt
except Exception as e:
    print("[SMOKE] import KO:", e); sys.exit(2)

try:
    res = tt.create_turntable(radius=6.0, height=2.0, path_duration=120, fps=24)
    print("[SMOKE] OK")
    print(json.dumps({
        "have": sorted(list(res["objects"].keys())),
        "fps": res["settings"]["fps"],
        "engine": res["settings"]["engine"],
        "ares_file": getattr(ares, "__file__", "n/a"),
        "base": BASE
    }, ensure_ascii=False))
except Exception as e:
    print("[SMOKE] build KO:", e); sys.exit(3)