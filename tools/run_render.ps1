param(
  [string]$BlenderExe = "D:\blender-4.5.3-windows-x64\blender.exe"
)
Write-Host "=== ARES render run ==="
if (-not (Test-Path $BlenderExe)) { Write-Error "Blender exe introuvable: $BlenderExe"; exit 1 }

# Smoke
& $BlenderExe -b --python (Join-Path $PSScriptRoot "test_smoke.py")
if ($LASTEXITCODE -ne 0) { Write-Error "Smoke KO ($LASTEXITCODE)"; exit $LASTEXITCODE }

# Render 1 frame
$renderTest = Join-Path $PSScriptRoot "test_render_oneframe.py"
& $BlenderExe -b --python $renderTest
if ($LASTEXITCODE -ne 0) { Write-Error "Render KO ($LASTEXITCODE)"; exit $LASTEXITCODE }

# Ouvre le PNG si présent
$outPng = Join-Path $PSScriptRoot "..\dist\tt_frame1.png"
if (Test-Path $outPng) {
  Write-Host "Opening $outPng"
  Start-Process $outPng
} else {
  Write-Warning "PNG non trouvé: $outPng"
}