# tools/run_headless_smoke.ps1 — lance le test headless avec Blender
param(
  [string]$BlenderExe = $env:BLENDER_EXE
)

if (-not $BlenderExe -or -not (Test-Path $BlenderExe)) {
  # Fallback ordi3 (confirmé)
  $BlenderExe = "D:\blender-4.5.3-windows-x64\blender.exe"
}

if (-not (Test-Path $BlenderExe)) {
  Write-Host "❌ Blender introuvable. Renseigne BLENDER_EXE ou adapte le chemin dans ce script." -ForegroundColor Red
  exit 1
}

Write-Host "▶ Headless smoke via: $BlenderExe" -ForegroundColor Cyan
& $BlenderExe -b -noaudio -P "tests/smoke_blender.py"
$code = $LASTEXITCODE
if ($code -ne 0) {
  Write-Host "❌ Smoke test a retourné code $code" -ForegroundColor Red
  exit $code
}
Write-Host "✅ Smoke test OK" -ForegroundColor Green
