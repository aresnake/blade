<#
ARES • Blender PyTest Runner (temp file variant)
-----------------------------------------------
Exécute PyTest *dans* Blender headless en écrivant un script .py temporaire.
#>

param(
  [string]$BlenderExe,
  [string]$Workspace,
  [string[]]$PytestArgs = @("-q")
)

$ErrorActionPreference = "Stop"

function Resolve-BlenderExe {
  param([string]$Given)
  if ($Given -and (Test-Path $Given)) { return (Resolve-Path $Given).Path }
  if ($env:BLENDER_EXE -and (Test-Path $env:BLENDER_EXE)) { return (Resolve-Path $env:BLENDER_EXE).Path }
  $candidates = @(
    "D:\blender-4.5.3-clean\blender-4.5.3-windows-x64\blender.exe",
    "C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
  )
  foreach ($c in $candidates) { if (Test-Path $c) { return $c } }
  throw "BLENDER_EXE introuvable. Fournis -BlenderExe ou défini `$env:BLENDER_EXE."
}

$bl   = Resolve-BlenderExe -Given $BlenderExe
$root = if ($Workspace) { (Resolve-Path $Workspace).Path } else { (Resolve-Path ".").Path }

Write-Host "▶ Using Blender:" $bl
Write-Host "▶ Workspace   :" $root
Write-Host "▶ PytestArgs  :" ($PytestArgs -join " ")

# 1) Construire le script Python temporaire
$pytestArgsList = ($PytestArgs | ForEach-Object { "'$_'" }) -join ", "
$pyCode = @"
import sys
sys.path.insert(0, r'$root')
try:
    import pytest
except Exception as e:
    raise SystemExit(f'pytest non installé dans le Python de Blender: {e}')
args = [$pytestArgsList]
raise SystemExit(pytest.main(args))
"@

$tmp = [System.IO.Path]::Combine([System.IO.Path]::GetTempPath(), "ares_blender_pytest_runner.py")
Set-Content -Path $tmp -Value $pyCode -Encoding UTF8

# 2) Exécuter Blender headless avec --python <tmpfile>
$startInfo = @{
  FilePath     = $bl
  ArgumentList = @("-b","--factory-startup","--python", $tmp)
  NoNewWindow  = $true
  Wait         = $true
  PassThru     = $true
}
$proc = Start-Process @startInfo

# 3) Nettoyage + sortie
Remove-Item -ErrorAction SilentlyContinue $tmp

if ($proc.ExitCode -ne 0) {
  Write-Error "PyTest failed with exit code $($proc.ExitCode)"
  exit $proc.ExitCode
} else {
  Write-Host "✅ PyTest passed."
}
