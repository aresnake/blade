from pathlib import Path
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/update_file.py <path/to/file>  (le contenu arrive sur stdin)")
        raise SystemExit(1)

    target = Path(sys.argv[1])
    code = sys.stdin.read()

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(code, encoding="utf-8")

    print(f"✅ Fichier écrit : {target.resolve()} (len={len(code)} chars)")

if __name__ == "__main__":
    main()
