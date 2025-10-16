# === Preflight shell ===
. "$PSScriptRoot\ShellInfo.ps1"
$__si = Get-BladeShellInfo
Write-Host ("Shell: {0} | Zip: {1}" -f $__si.Edition + " " + $__si.Version, $__si.ZipStrategy) -ForegroundColor DarkCyan
param(
  [ValidateSet("hello","check","clean","pack")]
  [string]$Task = "check"
)

switch ($Task) {
  "hello" {
    Write-Host "Make: hello (v13 ready)" -ForegroundColor Green
    return
  }
  "check" {
    Write-Host "Make: check workspace" -ForegroundColor Cyan
    $dirs = @("ares","config","tools","tests","resources","datasets","audio_samples","logs","summary","docs")
    foreach ($d in $dirs) {
      if (Test-Path $d) {
        Write-Host ("✅ {0}" -f $d) -ForegroundColor Green
      } else {
        Write-Host ("❌ {0} manquant" -f $d) -ForegroundColor Red
      }
    }
    return
  }
  "clean" {
    Write-Host "Make: clean temp/logs" -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\logs\*,.\summary\* -ErrorAction SilentlyContinue
    return
  }
  "pack" {
    Write-Host "Make: pack add-on" -ForegroundColor Cyan
    & powershell -NoProfile -File .\tools\Package.ps1
    return
  }
}

