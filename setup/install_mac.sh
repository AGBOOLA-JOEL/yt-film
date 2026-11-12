#!/usr/bin/env bash
# yt-film setup for macOS (Apple Silicon or Intel). Run from the repo folder:
#     bash setup/install_mac.sh
# Installs (only what's missing): Homebrew packages python@3.11 and ffmpeg, a Python environment in .venv with the
# engine's libraries and Whisper, and a .env settings file. Safe to run again.
set -e
cd "$(dirname "$0")/.."
REPO="$(pwd)"
echo "== yt-film setup (macOS) in $REPO"

if ! command -v brew >/dev/null 2>&1; then
  echo "Homebrew is needed first. Install it from https://brew.sh (one command), then run this again."
  exit 1
fi
command -v python3.11 >/dev/null 2>&1 || brew install python@3.11
command -v ffmpeg >/dev/null 2>&1 || brew install ffmpeg
PY="$(command -v python3.11)"

if [ ! -x .venv/bin/python ]; then
  echo "== creating .venv"
  "$PY" -m venv .venv
fi
.venv/bin/python -m pip install --upgrade pip wheel >/dev/null
echo "== installing libraries (a few minutes the first time)"
.venv/bin/python -m pip install -r engine/requirements.txt

# macOS already has American Typewriter, Bradley Hand, Courier New and Impact: no font download needed.
[ -f .env ] || { cp .env.example .env; echo "== made .env (add your GEMINI_API_KEY there)"; }

echo "== checking"
.venv/bin/python scripts/doctor.py || true
cat <<EOF

Done. The engine's Python is:  $REPO/.venv/bin/python
Next: open Claude Code in this folder and say "set up yt-film" or "make a film about ...".
To try the example:  .venv/bin/python scripts/new_project.py chadwick --example chadwick
EOF
