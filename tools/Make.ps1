param(
  [ValidateSet('hello','check','clean')][string]$Task = 'check'
)

switch ($Task) {
  'hello' { Write-Host 'Make: hello (v13 ready)' -ForegroundColor Green; break }
  'check' {
    Write-Host 'Make: check workspace' -ForegroundColor Cyan
    'ares','config','tools','tests','resources','datasets','audio_samples','logs','summary','docs' | ForEach-Object {
      if (-not (Test-Path )) { Write-Host ('❌ {0} manquant' -f ) -ForegroundColor Red } else { Write-Host ('✅ {0}' -f ) -ForegroundColor Green }
    }
    break
  }
  'clean' {
    Write-Host 'Make: clean temp/logs' -ForegroundColor Yellow
    Remove-Item -Recurse -Force .\logs\*,.\summary\* -ErrorAction SilentlyContinue
    break
  }
}
