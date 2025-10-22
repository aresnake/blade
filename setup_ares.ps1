# Initialise/complète l’ossature ARES Core LTS v13 (création si manquant).
# ⚠️ Ne supprime/réécrit rien — ajoute uniquement les dossiers/fichiers absents.

$root = (Get-Location).Path
$dirs = @(
  "ares/core","ares/ui","ares/config","ares/tools","ares/logs",
  "tests","docs_core",".github/workflows"
)

foreach ($d in $dirs) {
  $p = Join-Path $root $d
  if (-not (Test-Path $p)) { New-Item -ItemType Directory -Path $p -Force | Out-Null }
}

# Fichiers placeholders (créés seulement s’ils n’existent pas)
function Ensure-File($path, $content) {
  if (-not (Test-Path $path)) { $content | Set-Content -Encoding utf8 $path }
}

Ensure-File (Join-Path $root "ares/__init__.py")        '"""ARES Core LTS v13 — package root"""'
Ensure-File (Join-Path $root "tests/__init__.py")       '"""pytest package"""'
Ensure-File (Join-Path $root "docs_core/README.md")     "# ARES Core LTS v13"
Ensure-File (Join-Path $root "requirements.txt")        "pyyaml`npytest"

Write-Host "✅ ARES v13: structure vérifiée/créée (non destructive)." -ForegroundColor Green
