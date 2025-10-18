param(
  [Parameter(Mandatory=$true)][string]$BlenderExe,
  [Parameter(Mandatory=$true)][string]$OutPng
)
$old = Get-Location
$blDir = Split-Path $BlenderExe -Parent
$env:PYTHONPATH = ''
$env:PYTHONHOME = ''
$env:PYTHONNOUSERSITE = '1'
Set-Location $blDir
& $BlenderExe -b --factory-startup --python "$PSScriptRoot\blender_sanity.py" -- "$OutPng"
$code = $LASTEXITCODE
Set-Location $old
if ($code) { throw "Blender sanity failed ($code)" }