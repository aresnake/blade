param(
  [string]$BlenderExe = "D:\blender-4.5.3-windows-x64\blender.exe"
)
Write-Host "=== ARES dev run ==="
if (-not (Test-Path $BlenderExe)) {
  Write-Error "Blender exe introuvable: $BlenderExe"; exit 1
}
# Test headless
& $BlenderExe -b --python (Join-Path $PSScriptRoot "test_smoke.py")
if ($LASTEXITCODE -ne 0) { Write-Error "Smoke test KO ($LASTEXITCODE)"; exit $LASTEXITCODE }
Write-Host "Smoke test OK."

# Optionnel: zip local (équivalent CI)
$zip = Join-Path $PSScriptRoot "..\dist\blade_ares-local.zip"
Remove-Item $zip -ErrorAction SilentlyContinue
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory(
  (Join-Path $PSScriptRoot "..\ares"),
  $zip
)
Write-Host "ZIP local -> $zip"