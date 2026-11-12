# yt-film setup for Windows 10 / 11. Run from the repo folder in PowerShell:
#     powershell -ExecutionPolicy Bypass -File setup\install_windows.ps1
# Installs (only what's missing): Python 3.11 and FFmpeg with winget, a Python environment in .venv with the engine's
# libraries and Whisper, four free fonts into fonts\, UTF-8 mode for Python, and a .env settings file. Safe to re-run.
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)
$Repo = (Get-Location).Path
Write-Host "== yt-film setup (Windows) in $Repo"

function Refresh-Path {
  $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
  Write-Host "winget is missing: install 'App Installer' from the Microsoft Store, then run this again." -ForegroundColor Yellow
  exit 1
}

# Python 3.11 (the py launcher finds it even if 'python' points somewhere else)
$hasPy = $false
try { & py -3.11 --version *> $null; if ($LASTEXITCODE -eq 0) { $hasPy = $true } } catch {}
if (-not $hasPy) {
  Write-Host "== installing Python 3.11"
  winget install -e --id Python.Python.3.11 --accept-source-agreements --accept-package-agreements
  Refresh-Path
}

# FFmpeg (renders, audio, the final join)
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host "== installing FFmpeg"
  winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
  Refresh-Path
}
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host "FFmpeg was installed but this window can't see it yet: close PowerShell, open a new one, run this again." -ForegroundColor Yellow
  exit 1
}

# Python reads and writes UTF-8 everywhere (scripts have curly quotes, accents, dashes)
[Environment]::SetEnvironmentVariable("PYTHONUTF8", "1", "User")
$env:PYTHONUTF8 = "1"

if (-not (Test-Path ".venv\Scripts\python.exe")) {
  Write-Host "== creating .venv"
  & py -3.11 -m venv .venv
}
$Py = Join-Path $Repo ".venv\Scripts\python.exe"
& $Py -m pip install --upgrade pip wheel | Out-Null
Write-Host "== installing libraries (a few minutes the first time)"
& $Py -m pip install -r engine\requirements.txt

# free fonts for the typewriter labels, handwriting, counters and stamps (Windows lacks the macOS ones)
$fonts = @{
  "SpecialElite-Regular.ttf" = "https://raw.githubusercontent.com/google/fonts/main/apache/specialelite/SpecialElite-Regular.ttf";
  "Caveat.ttf"               = "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf";
  "CourierPrime-Regular.ttf" = "https://raw.githubusercontent.com/google/fonts/main/ofl/courierprime/CourierPrime-Regular.ttf";
  "CourierPrime-Bold.ttf"    = "https://raw.githubusercontent.com/google/fonts/main/ofl/courierprime/CourierPrime-Bold.ttf";
  "Anton-Regular.ttf"        = "https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf"
}
foreach ($f in $fonts.Keys) {
  $dst = Join-Path $Repo "fonts\$f"
  if (-not (Test-Path $dst)) {
    try { Invoke-WebRequest -Uri $fonts[$f] -OutFile $dst -UseBasicParsing; Write-Host "   font $f" }
    catch { Write-Host "   couldn't download $f (the engine falls back to a Windows font)" -ForegroundColor Yellow }
  }
}

if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env"; Write-Host "== made .env (add your GEMINI_API_KEY there)" }

Write-Host "== checking"
& $Py scripts\doctor.py

Write-Host ""
Write-Host "Done. The engine's Python is:  $Py"
Write-Host "Next: open Claude Code in this folder and say 'set up yt-film' or 'make a film about ...'."
Write-Host "To try the example:  .venv\Scripts\python scripts\new_project.py chadwick --example chadwick"
