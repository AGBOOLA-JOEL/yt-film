# Installing yt-film (macOS and Windows)

The fastest way: give Claude Code the repo link and say **"install this skill and set it up"**. Claude clones it,
runs the setup script for your system and fixes whatever `doctor.py` reports. The steps below are what it does, so
you can also do them by hand.

## What gets installed

| Tool | Why | Mac | Windows |
|---|---|---|---|
| **Git** | clone the repo | comes with Xcode tools (`xcode-select --install`) | `winget install Git.Git` |
| **Claude Code** | runs the skill | `npm i -g @anthropic-ai/claude-code` or the desktop app | same, or the desktop app |
| **Python 3.11** | the engine (3.10–3.12 work) | `brew install python@3.11` | `winget install Python.Python.3.11` |
| **FFmpeg** | every render, all audio, the final join | `brew install ffmpeg` | `winget install Gyan.FFmpeg` |
| Python libraries | numpy, OpenCV, Pillow, SciPy, scikit-image, soundfile | `engine/requirements.txt` | same |
| **Whisper** | word timings (shots are cued on the words) | `mlx-whisper` (Apple Silicon) | `faster-whisper` (CPU, or NVIDIA GPU) |
| Fonts | typewriter, handwriting, stamps | already on macOS | downloaded into `fonts/` by the setup |
| Gemini API key | voice, music, crowd murmur, dubs (optional images) | `.env` | `.env` |

No After Effects, no paid render service. Everything renders on your computer.

## 1. Get the repo where Claude finds it

Claude Code loads personal skills from `~/.claude/skills/<name>/`. Clone straight there:

**macOS** (Terminal):
```bash
git clone https://github.com/<you>/yt-film.git ~/.claude/skills/yt-film
```
**Windows** (PowerShell):
```powershell
git clone https://github.com/<you>/yt-film.git "$env:USERPROFILE\.claude\skills\yt-film"
```
Private repo: run `gh auth login` first (GitHub CLI), or use a personal access token when Git asks for a password.

Prefer it inside one project only? Clone into `<project>/.claude/skills/yt-film` instead. Either way, restart Claude
Code and ask *"what skills do you have?"*: `yt-film` should be listed.

## 2. Run the setup script

**macOS** (needs [Homebrew](https://brew.sh)):
```bash
cd ~/.claude/skills/yt-film && bash setup/install_mac.sh
```
**Windows 10/11** (needs winget, which ships with Windows 11 and "App Installer" on Windows 10):
```powershell
cd "$env:USERPROFILE\.claude\skills\yt-film"; powershell -ExecutionPolicy Bypass -File setup\install_windows.ps1
```
It installs only what's missing, creates `.venv` (the engine's own Python), installs the libraries and Whisper,
downloads the fonts (Windows), sets `PYTHONUTF8=1` (Windows), copies `.env.example` to `.env`, and runs the doctor.

**Windows notes**
- If FFmpeg or Python "isn't recognized" right after installing: close PowerShell, open a new one, run the script again.
- The engine's Python is `.venv\Scripts\python.exe`; on Mac it is `.venv/bin/python`. Claude uses it for every command.
- Keep projects on a local drive with a short path (e.g. `C:\films` or the default `%USERPROFILE%\yt-film-projects`),
  not inside OneDrive (syncing locks files mid-render). Set `YTF_WORKSPACE=C:/films` in `.env` if you like.
- Long paths: if Git or pip complains about path length, run once as admin:
  `reg add HKLM\SYSTEM\CurrentControlSet\Control\FileSystem /v LongPathsEnabled /t REG_DWORD /d 1 /f`
- Windows Defender can slow renders a lot by scanning every frame written: add your projects folder to its
  exclusions (Settings → Privacy & security → Windows Security → Virus & threat protection → Exclusions).
- Paths in commands can use forward slashes (`C:/films/my_story`); Python and FFmpeg accept them.

**Linux**: `sudo apt install python3.11 python3.11-venv ffmpeg fonts-dejavu`, then
`python3.11 -m venv .venv && .venv/bin/pip install -r engine/requirements.txt`, then download the fonts listed in
`fonts/README.md` into `fonts/`.

## 3. Add your settings

Open `.env` and fill in at least:
```
GEMINI_API_KEY=...            # https://aistudio.google.com/apikey (free tier is enough to try it)
YTF_CHANNEL=Your Channel      # written on the ending and kept in the dubbed end line
```
No Gemini key? You can still make films: record or generate the narration elsewhere (voice.md), bring your own
music (music.md), and skip the crowd murmur and dubs.

## 4. Check

```bash
.venv/bin/python scripts/doctor.py            # Mac
.venv\Scripts\python scripts\doctor.py        # Windows
```
Every line should say `[ok]`. It also tells you how many batches your computer can render at once and gives
slow-machine tips (performance.md).

## 5. Try the example (no API key needed)

```bash
.venv/bin/python scripts/new_project.py chadwick --example chadwick
cd ~/yt-film-projects/chadwick/tools
~/.claude/skills/yt-film/.venv/bin/python stills.py b1      # or just ask Claude: "show me stills of b1"
```
(Windows: `& "$env:USERPROFILE\.claude\skills\yt-film\.venv\Scripts\python.exe" stills.py b1`.)
`stills.py` builds a contact sheet of the batch in ~30 s without rendering. Render only when you decide to.

## Updating

```bash
cd ~/.claude/skills/yt-film && git pull
.venv/bin/python scripts/new_project.py <story> --update-engine     # refresh a project's tools/ (keeps its own files)
```
