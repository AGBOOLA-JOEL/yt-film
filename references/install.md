# Installing yt-film (macOS and Windows)

The fastest way: paste the install prompt from the top of the [README](../README.md) into Claude Code. Claude
follows the runbook below. Everything after it is the same work done by hand.

## Install runbook (for Claude)

Follow these steps in order. Work out the system first and use its commands throughout. Say what each step is
doing in one line; don't stop between steps unless a step says to ask.

**0. Find out where you are.** OS (`uname -s` / `$env:OS`), CPU (Apple Silicon or Intel/AMD), RAM, free disk, and
whether `git`, `python3.11` (Windows: `py -3.11`), `ffmpeg` and the package manager (macOS: `brew`; Windows:
`winget`; Linux: `apt`) exist. Tell the user in two lines what is there and what is missing.

**1. The repo.** Target `~/.claude/skills/yt-film` (macOS/Linux) or `%USERPROFILE%\.claude\skills\yt-film`
(Windows). If it exists and is this repo, `git pull`; else
`git clone https://github.com/AGBOOLA-JOEL/yt-film.git <target>`. No git: ask, then install it
(`xcode-select --install` / `winget install Git.Git` / `sudo apt install git`).

**2. System tools (ask first).** If Homebrew (macOS) or winget (Windows) is missing, give the user the official
install step (https://brew.sh; Windows 10: "App Installer" from the Microsoft Store) and wait: it needs their
password or a store install. For Python 3.11 and FFmpeg the setup script installs what's missing; tell the user
it will and why ("Python runs the engine, FFmpeg encodes every video and sound"), and get a yes before running it.
Linux: `sudo apt install python3.11 python3.11-venv ffmpeg fonts-dejavu` (the user runs sudo).

**3. Setup script.** From the repo folder:
- macOS: `bash setup/install_mac.sh`
- Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File setup\install_windows.ps1`
- Linux: `python3.11 -m venv .venv && .venv/bin/pip install -r engine/requirements.txt`, fonts from `fonts/README.md`
It is safe to run again. On Windows, if Python or FFmpeg "isn't recognized" right after installing, they are on the
PATH only in a new terminal: run the script again from a fresh PowerShell (or call them by full path).

**4. Doctor.** `.venv/bin/python scripts/doctor.py` (Windows `.venv\Scripts\python scripts\doctor.py`). Fix every
`[!!]` line using its hint and the troubleshooting table (`references/troubleshooting.md`), then run it again until
everything says `[ok]`. Don't move on with a failing line unless the user agrees (e.g. no Gemini key yet).

**5. Settings (`.env` in the repo folder).** Ask for the channel name and set `YTF_CHANNEL`. Ask whether they have
a Gemini API key (free at https://aistudio.google.com/apikey; voice, music, crowd murmur, dubs). **The key is theirs
to paste:** open or name the file and the line (`GEMINI_API_KEY=`) and let them paste it; never type, print, log or
store the key anywhere else. No key is fine: they can bring their own voice (voice.md) and music (music.md).
Optional: `YTF_WORKSPACE` (where films live; on Windows a short local path such as `C:/films`, not OneDrive) and
`YTF_LOOK` (their engine look, `references/art-styles.md`).

**6. Prove it works (no API key, no render).**
```
.venv/bin/python scripts/new_project.py chadwick --example chadwick
cd <workspace>/chadwick/tools && <repo>/.venv/bin/python stills.py b1
```
Show the user `renders/stills_b1.jpg` (it takes about 30 s). If it fails, read the error, fix, and re-run.

**7. Optional extras (ask).** Depth effects: `.venv/bin/python -m pip install torch transformers` (about 1 GB), then
`python tools/depth.py` per film. Slow machine or 8 GB RAM: suggest `YTF_JOBS=1` and the tips in performance.md.

**8. Finish.** Summarise in a few lines: where the skill is, what was installed, what the doctor says, what is left
for the user (their key, Homebrew, a restart). Tell them to **restart Claude Code** so the skill loads, then ask
*"what skills do you have?"* (yt-film should be listed) and start a film with *"Start a new yt-film project"*.

---

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
git clone https://github.com/AGBOOLA-JOEL/yt-film.git ~/.claude/skills/yt-film
```
**Windows** (PowerShell):
```powershell
git clone https://github.com/AGBOOLA-JOEL/yt-film.git "$env:USERPROFILE\.claude\skills\yt-film"
```

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
