#Requires -Version 5.1
# pre-commit.ps1 — Blade v13 guardrails
param()

# 1) Refuser les fichiers > 50 Mo (commit accidentels)
 = 50MB
 = git diff --cached --name-only | ForEach-Object {
   = Join-Path (Get-Location) 
  if (Test-Path ) {
     = (Get-Item ).Length
    if ( -gt ) { @{ Path = ; Size =  } }
  }
} | Where-Object {  }

if () {
  Write-Host "❌ Commit bloqué: fichiers > 50MB détectés:" -ForegroundColor Red
   | ForEach-Object { Write-Host (" - {0} ({1:N0} bytes)" -f .Path, .Size) }
  Write-Host "➡️  Ajoute ces fichiers dans .gitignore ou utilise Git LFS si nécessaire." -ForegroundColor Yellow
  exit 1
}

# 2) Bloquer certains formats (blend, zip) côté source par défaut
 = @(".blend", ".blend1", ".blend2", ".zip", ".7z", ".rar", ".mp4", ".mov")
 = git diff --cached --name-only | Where-Object {
   = [IO.Path]::GetExtension().ToLowerInvariant()
   -contains 
}

if () {
  Write-Host "❌ Commit bloqué: formats non autorisés détectés:" -ForegroundColor Red
   | ForEach-Object { Write-Host (" - {0}" -f ) }
  Write-Host "➡️  Place ces artefacts dans resources/ ou datasets/ et ajoute-les au .gitignore, ou utilise un stockage externe." -ForegroundColor Yellow
  exit 1
}

# 3) Vérif encodage UTF-8 (best effort)
 = @()
git diff --cached --name-only --diff-filter=ACM | ForEach-Object {
   = 
  if (Test-Path ) {
    try {
       = [IO.File]::ReadAllBytes()
      [Text.Encoding]::UTF8.GetString() | Out-Null
    } catch {
       += 
    }
  }
}
if (.Count -gt 0) {
  Write-Host "❌ Commit bloqué: fichiers non UTF-8 détectés:" -ForegroundColor Red
   | ForEach-Object { Write-Host (" - {0}" -f ) }
  Write-Host "➡️  Convertis en UTF-8 sans BOM (VS Code: Reopen with Encoding → UTF-8 → Save)." -ForegroundColor Yellow
  exit 1
}

Write-Host "✅ pre-commit: OK" -ForegroundColor Green
exit 0
