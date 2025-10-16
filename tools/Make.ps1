param(
  [ValidateSet("hello","check","clean","pack")]
  [string]$Task = "check"
)

# === Preflight shell (facultatif/robuste) ===
$si = $null
$ShellInfoPath = Join-Path $PSScriptRoot "ShellInfo.ps1"
if (Test-Path $ShellInfoPath) {
  . $ShellInfoPath
  try { $si = Get-BladeShellInfo } catch { $si = $null }
}
if ($si) {
  Write-Host ("Shell: {0} {1} | Zip: {2}" -f $si.Edition, $si.Version, $si.ZipStrategy) -ForegroundColor DarkCyan
} else {
  Write-Host "Shell: (unknown) | Zip: (auto)" -ForegroundColor DarkCyan
}

switch ($Task) {
  "hello" {
    Write-Host "Make: hello (v13 ready)" -ForegroundColor Green
    return
  }
  "check" {
    Write-Host "Make: check workspace" -ForegroundColor Cyan
    $dirs = @("ares","config","tools","tests","resources","datasets","audio_samples","logs","summary","docs")
    foreach ($d in $dirs) {
      if (Test-Path $d) { Write-Host ("✅ {0}" -f $d) -ForegroundColor Green }
      else              { Write-Host ("❌ {0} manquant" -f $d) -ForegroundColor Red }
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
    & powershell -NoProfile -File (Join-Path $PSScriptRoot "Package.ps1")
    return
  }
}
