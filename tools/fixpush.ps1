param([string]$Msg = "chore: fixpush")
ruff check . --fix --unsafe-fixes
python -m py_compile (Get-ChildItem -Recurse -Filter *.py | % FullName) 2>$null
git add -A
git commit -m $Msg
git push
