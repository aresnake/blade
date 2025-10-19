param(
  [string]$Tag,
  [switch]$Install,
  [switch]$Release,
  [string]$Blender,
  [switch]$NoPurge
)

$ErrorActionPreference = "Stop"

# --- PATCH robustesse ---
if (-not $MyInvocation.MyCommand.Path) {
  # Si le script est collé directement dans la console
  $PSScriptRoot = Get-Location
} elseif (-not $PSScriptRoot) {
  $PSScriptRoot = Split-Path -Path $MyInvocation.MyCommand.Path -Parent
}
# -------------------------

$root    = try { (Resolve-Path (Join-Path $PSScriptRoot "..")).Path } catch { (Get-Location).Path }
$aresDir = Join-Path $root "ares"
$dist    = Join-Path $root "dist"

function Get-AresVersion {
  $init = Join-Path $aresDir "__init__.py"
  if (Test-Path $init) {
    $txt = Get-Content -Raw -Encoding utf8 $init
    $m = [regex]::Match($txt, "__version__\s*=\s*'([^']+)'")
    if ($m.Success) { return $m.Groups[1].Value }
  }
  try {
    $tag = (git describe --tags --abbrev=0) 2>$null
    if ($LASTEXITCODE -eq 0 -and $tag) { return $tag }
  } catch {}
  return ("v" + (Get-Date -Format "yyyy.MM.dd-HHmm"))
}

if (-not (Test-Path $aresDir)) { throw "Dossier introuvable: $aresDir" }
if (-not $Tag -or $Tag.Trim() -eq "") { $Tag = Get-AresVersion }

$zipName = "blade_ares-$Tag.zip"
$zipPath = Join-Path $dist $zipName

# --- Détection Blender ---
if ($Blender) {
  $blenderExe = $Blender
} else {
  $candidates = @(
    "D:\blender-4.5.3-clean\blender-4.5.3-windows-x64\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
  )
  $blenderExe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
}
$addonPath  = "$env:APPDATA\Blender Foundation\Blender\4.5\scripts\addons\ares"

Write-Host "=== ARES Packaging Tool ==="
Write-Host "Tag : $Tag"
Write-Host "Root: $root"
Write-Host "Zip : $zipPath`n"

# 1) Purge ancienne install utilisateur (sauf -NoPurge)
if (-not $NoPurge) {
  if (Test-Path $addonPath) {
    Write-Host "🧹 Suppression ancienne installation ARES: $addonPath"
    Remove-Item -Recurse -Force $addonPath
  }
}

# 2) (Re)création du ZIP — via un nom temporaire (anti-lock)
New-Item -ItemType Directory -Force -Path $dist | Out-Null
$zipTmp = Join-Path $dist ("tmp_" + [guid]::NewGuid().ToString() + ".zip")
Compress-Archive -Path $aresDir -DestinationPath $zipTmp -Force

# 3) Vérif du ZIP (et fermeture propre)
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zipH = $null
try {
  $zipH = [IO.Compression.ZipFile]::OpenRead((Resolve-Path $zipTmp))
  $first = $zipH.Entries | Select-Object -First 1 -ExpandProperty FullName
  if (-not $first -or $first -notmatch '^ares/') { throw "❌ ZIP mal structuré (pas de 'ares/' en racine)" }
} finally {
  if ($zipH) { $zipH.Dispose() }
}

# 4) Remplacer la cible en gérant les verrous
for ($i=1; $i -le 6; $i++) {
  try {
    if (Test-Path $zipPath) { Remove-Item -Force $zipPath }
    Move-Item -Force $zipTmp $zipPath
    break
  } catch {
    if ($i -eq 6) { throw "Impossible d'écraser $zipPath (toujours verrouillé)" }
    Start-Sleep -Milliseconds 500
  }
}
Write-Host "✅ ZIP OK: $zipPath"

# 5) Installation auto (optionnelle)
if ($Install) {
  if (-not (Test-Path $blenderExe)) { throw "Blender introuvable: $blenderExe (spécifie -Blender ...)" }
  & $blenderExe -b --factory-startup --python-expr `
    ("import bpy; p=r'"+ (Resolve-Path $zipPath).Path.Replace('\','\\') +
     "'; bpy.ops.preferences.addon_install(filepath=p); bpy.ops.preferences.addon_enable(module='ares'); bpy.ops.wm.save_userpref()")
  Write-Host "✅ ARES installé et activé."
}

# 6) Publication release GitHub (optionnelle)
if ($Release) {
  $rel = Join-Path $root "tools\release.ps1"
  if (Test-Path $rel) {
    Write-Host "`n🚀 Publication de la release GitHub..."
    & $rel -Tag $Tag -ZipPath $zipPath -SkipBuild
  } else {
    Write-Host "`nℹ️ tools\release.ps1 introuvable — publication manuelle nécessaire."
  }
}