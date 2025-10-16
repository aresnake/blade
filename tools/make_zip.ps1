param(
  [string]$OutDir = 'dist'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

# 1) Version depuis bl_info
$init = Join-Path $PSScriptRoot '..\ares\__init__.py'
$init = (Resolve-Path $init).Path
$txt  = Get-Content -LiteralPath $init -Raw
if (-not ($txt -match 'bl_info\s*=\s*\{[^}]*?version\D*\((?<maj>\d+)\s*,\s*(?<min>\d+)\s*,\s*(?<patch>\d+)')) {
  Write-Warning "Version non trouvée dans bl_info → fallback timestamp"
  $ver = (Get-Date -Format 'yyyyMMdd-HHmmss')
} else {
  $ver = "$([int]$Matches.maj).$([int]$Matches.min).$([int]$Matches.patch)"
}

# 2) Out dir
$out = Join-Path (Join-Path $PSScriptRoot '..') $OutDir
New-Item -ItemType Directory -Force -Path $out | Out-Null

# 3) ZIP path (overwrite safe)
$zip = Join-Path $out ("blade_ares-$ver.zip")
Remove-Item $zip -ErrorAction SilentlyContinue

# 4) Archive propre depuis Git
Push-Location (Join-Path $PSScriptRoot '..')
git rev-parse --is-inside-work-tree *> $null
if ($LASTEXITCODE) { throw 'Ce script doit être lancé dans un repo Git.' }
git archive --format=zip --output="$zip" HEAD ares
Pop-Location

# 5) Sanity: inspecte contenu & interdit __pycache__ / .pyc (avec Dispose)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipArchive = [IO.Compression.ZipFile]::OpenRead($zip)
try {
  $entries = $zipArchive.Entries
  $names   = $entries | Select-Object -First 12 -ExpandProperty FullName
  Write-Host "→ ZIP: $zip"
  Write-Host "→ Aperçu:"; $names | ForEach-Object { "   - $_" }

  $bad = $entries.FullName | ForEach-Object { $_ -replace '\\','/' } | Where-Object {
    $_ -match '/__pycache__/' -or $_ -like '*.pyc'
  }
  if ($bad) {
    throw "Artefacts indésirables détectés dans le ZIP:`n$($bad -join "`n")"
  }
}
finally {
  $zipArchive.Dispose()
}

Write-Host "`n✅ ZIP propre créé -> $zip"