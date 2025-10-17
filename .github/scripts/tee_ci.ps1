param(
  [Parameter(Mandatory=$true)][string]$Title,
  [Parameter(Mandatory=$true)][string]$CmdLine
)
$ErrorActionPreference = "Stop"
mkdir ci -ea 0 | Out-Null
if (-not (Test-Path 'ci/last.txt')) { New-Item -ItemType File -Path 'ci/last.txt' | Out-Null }
"`n=== $Title ===" | Tee-Object -FilePath 'ci/last.txt' -Append | Out-Null
# Exécute la ligne de commande dans cmd.exe pour compat max
cmd.exe /c $CmdLine 2>&1 | Tee-Object -FilePath 'ci/last.txt' -Append
