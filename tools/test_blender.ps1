param(
  [string]$Blender = "D:\blender-4.5.3-windows-x64\blender.exe",
  [string[]]$PytestArgs = @("-q")  # ex. @("-q","-k","smoke")
)

$ErrorActionPreference = "Stop"

# Repo root = parent du dossier de ce script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Root = Resolve-Path (Join-Path $ScriptDir "..")

# Isoler les add-ons utilisateur + forcer l'import local
$env:PYTHONPATH = $Root
$env:BLENDER_USER_SCRIPTS = Join-Path $Root ".blank_scripts"
New-Item -ItemType Directory -Force -Path $env:BLENDER_USER_SCRIPTS | Out-Null

# Construire la ligne blender
$runner = Join-Path $ScriptDir "_pytest_in_blender.py"
$argList = @("-b", "--python", $runner)
if ($PytestArgs.Count -gt 0) { $argList += @("--") + $PytestArgs }

Write-Host "→ Running pytest in Blender..."
Write-Host "  BLENDER_USER_SCRIPTS = $env:BLENDER_USER_SCRIPTS"
Write-Host "  PYTHONPATH           = $env:PYTHONPATH"

& $Blender @argList
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }