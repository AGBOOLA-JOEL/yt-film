"""Check that everything the engine needs works on this computer, and suggest speed settings for it.

    python scripts/doctor.py            (use the .venv Python: .venv/bin/python on Mac, .venv\\Scripts\\python on Windows)
"""
import importlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "engine"))
ok_all = True


def say(ok, what, fix=""):
    global ok_all
    ok_all &= bool(ok) or fix.startswith("(optional)")
    print(f"  [{'ok' if ok else '!!'}] {what}" + ("" if ok else f"\n       -> {fix}"))


print(f"yt-film doctor · {platform.system()} {platform.release()} · {platform.machine()} · Python {sys.version.split()[0]}")
say((3, 10) <= sys.version_info[:2] <= (3, 12), "Python 3.10-3.12", "install Python 3.11 and re-run the setup script")
say(sys.prefix != sys.base_prefix, "running inside a virtual environment (.venv)",
    "(optional) run with .venv/bin/python (Mac) or .venv\\Scripts\\python (Windows)")
for mod in ("numpy", "cv2", "PIL", "scipy", "skimage", "soundfile"):
    try:
        importlib.import_module(mod)
        say(True, f"library {mod}")
    except Exception as e:  # noqa: BLE001
        say(False, f"library {mod}: {e}", "pip install -r engine/requirements.txt")
say(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg + ffprobe on PATH",
    "Mac: brew install ffmpeg · Windows: winget install Gyan.FFmpeg, then open a NEW terminal")
if shutil.which("ffmpeg"):
    enc = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    say("libx264" in enc, "ffmpeg has libx264", "install a full ffmpeg build (brew ffmpeg / Gyan.FFmpeg)")

import ytf  # noqa: E402

for role in ("type", "hand", "mono", "mono_bold", "stamp", "bold"):
    try:
        f = ytf.font(role)
        say(True, f"font {role:9s} {Path(f).name}")
    except SystemExit as e:
        say(False, f"font {role}", str(e))
w = None
try:
    if ytf.APPLE_SILICON:
        import mlx_whisper  # noqa: F401
        w = "mlx-whisper (Apple GPU)"
    else:
        import faster_whisper  # noqa: F401
        w = "faster-whisper (CPU" + (" / CUDA" if shutil.which("nvidia-smi") else "") + ")"
except ImportError:
    pass
say(w, f"Whisper word timings: {w}", "pip install -r engine/requirements.txt (needed for voice timings)")
key = ytf.setting("GEMINI_API_KEY")
say(key, "GEMINI_API_KEY found (TTS voice, music, crowd murmur, dubs, optional images)",
    "(optional) add GEMINI_API_KEY=... to .env, or record/import your own voice and music (see references/voice.md)")
print(f"  [..] channel name for the ending/dubs: {ytf.channel()!r} (YTF_CHANNEL in .env)")
if ytf.IS_WIN:
    say(os.environ.get("PYTHONUTF8") == "1", "PYTHONUTF8=1 (UTF-8 text on Windows)",
        "setx PYTHONUTF8 1   then open a new terminal (the setup script does this)")

# speed advice
sys.path.insert(0, str(REPO / "engine"))
from render_all import auto_jobs, ram_gb  # noqa: E402

cpu, ram = os.cpu_count() or 2, ram_gb()
jobs = auto_jobs(99, False)
print(f"\nThis computer: {cpu} cores, {ram:.0f} GB RAM -> renders {jobs} batch(es) at once (YTF_JOBS overrides).")
if jobs <= 2 or ram < 12:
    print("  Slow machine tips (references/performance.md):\n"
          "   - check shots with tools/stills.py and --preview renders; do full renders only when a batch is right\n"
          "   - YTF_X264_PRESET=faster in .env (bigger files, much quicker encodes)\n"
          "   - YTF_WHISPER_MODEL=small.en in .env (quicker word timings; check names by eye)\n"
          "   - render overnight with tools/render_all.py --changed, close the browser and other heavy apps")
print("\nAll good." if ok_all else "\nFix the [!!] lines above, then run this again.")
