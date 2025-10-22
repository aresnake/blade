from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
SUMMARY = ROOT / "summary"

DIST.mkdir(exist_ok=True, parents=True)
SUMMARY.mkdir(exist_ok=True, parents=True)
