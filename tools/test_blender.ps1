# tools/test_blender.ps1
# Run pytest inside Blender (headless) with clean env + summary file.
# This version avoids inline --python-expr issues by writing a temp runner.py.

param(
  [string[]]$PytestArgs = @('-q'),
  [string]  $TestsPath  = 'tests',
  [switch]  $JUnit,
  [string]  $BlenderExe
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

# --- Repo root (robuste: script OU interactif) ---
$SelfPath  = if ($PSCommandPath) { $PSCommandPath } elseif ($MyInvocation.MyCommand.Path) { $MyInvocation.MyCommand.Path } else { $null }
if ($SelfPath) {
  $ScriptDir = Split-Path -Parent $SelfPath
  $RepoRoot  = Resolve-Path (Join-Path $ScriptDir '..') | ForEach-Object { $_.Path }
} else {
  $RepoRoot  = (Get-Location).Path
  $ScriptDir = Join-Path $RepoRoot 'tools'
}

# --- Paths ---
$SummaryDir = Join-Path $RepoRoot 'summary'
$DistDir    = Join-Path $RepoRoot 'dist'
$LogsDir    = Join-Path $RepoRoot 'logs'
$BlankDir   = Join-Path $RepoRoot '.blank_scripts'
$SummaryTxt = Join-Path $SummaryDir 'pytest_summary.txt'
$JUnitXml   = Join-Path $DistDir 'pytest-report.xml'
$RunnerPy   = Join-Path $DistDir '_pytest_runner.py'

foreach ($d in @($SummaryDir,$DistDir,$LogsDir,$BlankDir)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }

# --- Resolve Blender EXE ---
if ([string]::IsNullOrWhiteSpace($BlenderExe)) {
  if ($env:BLENDER_EXE) { $BlenderExe = $env:BLENDER_EXE }
}
if (-not (Test-Path $BlenderExe)) {
  throw "BLENDER_EXE introuvable. Fournis -BlenderExe '...blender.exe' ou exporte `$env:BLENDER_EXE."
}

# --- Environment isolation ---
$env:BLENDER_USER_SCRIPTS = $BlankDir
$env:PYTHONPATH = if ($env:PYTHONPATH) { "$RepoRoot;$env:PYTHONPATH" } else { "$RepoRoot" }

# --- Build pytest args ---
$finalArgs = @()
$finalArgs += $PytestArgs
if ($JUnit) { $finalArgs += @('--junitxml', $JUnitXml) }
if (-not [string]::IsNullOrWhiteSpace($TestsPath)) { $finalArgs += @($TestsPath) }

function New-PyListLiteral([string[]]$items) {
  $escaped = foreach($it in $items) {
    $t = $it -replace "\\","\\"; $t = $t -replace "'","\'"; "'$t'"
  }
  return "[" + ($escaped -join ",") + "]"
}
$PyList = New-PyListLiteral $finalArgs

# --- Python payload (will be written to runner.py) ---
$py = @"
import sys, os, time, pathlib
start = time.time()
repo = r'$RepoRoot'
sys.path.insert(0, repo)
os.environ['PYTHONPATH'] = repo + os.pathsep + os.environ.get('PYTHONPATH','')
args = $PyList

try:
    import pytest
except Exception as e:
    print('[ARES][pytest] ERROR: pytest non disponible dans Blender:', e)
    sys.exit(2)

ret = pytest.main(args)
dur = time.time() - start
print(f'[ARES][pytest] exit={ret} duration={dur:.2f}s args={args}')

summary_path = pathlib.Path(r'$SummaryTxt')
try:
    summary_path.write_text(f'Exit={ret}\\nDuration={dur:.2f}s\\nArgs={args}\\n', encoding='utf-8')
except Exception as e:
    print('[ARES][pytest] WARN: impossible d\'écrire le résumé:', e)

sys.exit(ret)
"@

# --- Write runner file ---
Set-Content -Path $RunnerPy -Value $py -Encoding UTF8
Write-Host "→ Runner Python écrit: $RunnerPy"

# --- Run Blender headless with file ---
Write-Host "→ Running pytest in Blender..."
Write-Host "  BLENDER_EXE          = $BlenderExe"
Write-Host "  BLENDER_USER_SCRIPTS = $env:BLENDER_USER_SCRIPTS"
Write-Host "  PYTHONPATH           = $env:PYTHONPATH"
Write-Host "  RepoRoot             = $RepoRoot"
Write-Host "  PytestArgs           = $($finalArgs -join ' ')"
Write-Host ""

& $BlenderExe -b --factory-startup --python $RunnerPy
$code = $LASTEXITCODE

if (Test-Path $SummaryTxt) {
  Write-Host "✅ Summary: $SummaryTxt"
  Get-Content -Path $SummaryTxt | Write-Host
} else {
  Write-Warning "Le fichier de résumé n'a pas été généré: $SummaryTxt"
}

if ($code -ne 0) {
  Write-Error "Pytest dans Blender a retourné un code de sortie $code."
  exit $code
} else {
  Write-Host "✅ Pytest terminé avec succès (exit=0)."
  exit 0
}
