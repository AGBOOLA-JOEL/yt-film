"""Shared plumbing for the yt-film engine: where things live, fonts, the Gemini key, Whisper word timings, speed knobs.

Everything that used to be a hard-coded macOS path goes through here, so the same engine runs on macOS (Apple Silicon
or Intel), Windows 10/11 and Linux.

    import ytf
    ytf.SKILL                 the yt-film skill folder (holds assets/, fonts/, engine/)
    ytf.font("type")          a font path for: type, hand, hand_bold, mono, mono_bold, stamp, bold, seal
    ytf.gemini_key()          GEMINI_API_KEY from the environment or a .env file (project, skill, home)
    ytf.transcribe(wav)       [{"word", "start", "end"}, ...] with mlx-whisper (Apple Silicon) or faster-whisper
    ytf.channel()             your channel name (YTF_CHANNEL), used by the ending card and the dubs
    ytf.x264_preset()         ffmpeg preset for batch renders (YTF_X264_PRESET, default "medium")

Settings come from environment variables or a `.env` file (see .env.example in the repo root).
"""
import os
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


IS_WIN = os.name == "nt"
IS_MAC = sys.platform == "darwin"
APPLE_SILICON = IS_MAC and platform.machine() == "arm64"
SKILL = None  # set below


# ---------------------------------------------------------------- settings (.env)

def _env_files():
    """Where settings are looked for, nearest first: the project (tools/.., the current folder), then the repo."""
    cwd = Path.cwd()
    out = [cwd / ".env", cwd.parent / ".env", HERE / ".env", HERE.parent / ".env"]
    if SKILL is not None:
        out.append(SKILL / ".env")
    out.append(Path.home() / ".yt-film.env")
    seen, res = set(), []
    for p in out:
        if p not in seen:
            seen.add(p)
            res.append(p)
    return res


def setting(name, default=None):
    """An environment variable, or the first non-empty NAME=value line in the .env files (nearest first)."""
    if os.environ.get(name):
        return os.environ[name]
    for p in _env_files():
        if p.exists():
            for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line.startswith(name + "="):
                    v = line.split("=", 1)[1].split(" #")[0].strip().strip('"').strip("'")
                    if v:
                        return v
    return default


def _find_skill():
    """The repo/skill root: YTF_SKILL (env or a project's .env), else up from this file, else the usual install places."""
    env = setting("YTF_SKILL")
    if env and (Path(env).expanduser() / "assets" / "footnote").exists():
        return Path(env).expanduser()
    for p in [HERE, *HERE.parents]:
        if (p / "assets" / "footnote").exists() and (p / "SKILL.md").exists():
            return p
    for p in (Path.home() / ".claude" / "skills" / "yt-film", Path.home() / "yt-film"):
        if (p / "assets" / "footnote").exists():
            return p
    return HERE.parent


SKILL = _find_skill()
ASSETS = SKILL / "assets"


def gemini_key():
    k = setting("GEMINI_API_KEY")
    if not k:
        raise SystemExit("No GEMINI_API_KEY. Put it in a .env file in your project folder (GEMINI_API_KEY=...) or set it "
                         "as an environment variable. Get one at https://aistudio.google.com/apikey. "
                         "No key? Record the voice yourself and use scripts/import_voice.py instead.")
    return k


def channel():
    return setting("YTF_CHANNEL", "the channel")


def x264_preset():
    return setting("YTF_X264_PRESET", "medium")


def threads():
    """OpenCV threads per render process. Parallel batch renders each get 1-2 so the machine doesn't thrash."""
    n = setting("YTF_THREADS")
    return int(n) if n else 0


try:  # keep OpenCV from grabbing every core in every parallel render
    import cv2 as _cv2
    if threads():
        _cv2.setNumThreads(threads())
except Exception:  # noqa: BLE001
    pass


# ---------------------------------------------------------------- fonts

_WIN = Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
_MAC = Path("/System/Library/Fonts/Supplemental")
_LINUX = [Path("/usr/share/fonts"), Path.home() / ".local/share/fonts", Path.home() / ".fonts"]
# for each role: candidates in order. Names in the repo's fonts/ folder win (installed by setup), then the system.
FONTS = {
    "type": ["SpecialElite-Regular.ttf", _MAC / "AmericanTypewriter.ttc", _WIN / "cour.ttf", "DejaVuSansMono.ttf"],
    "hand": ["Caveat.ttf", _MAC / "Bradley Hand Bold.ttf", _WIN / "segoeprb.ttf",
             _WIN / "segoepr.ttf", _WIN / "comicbd.ttf", "DejaVuSans.ttf"],
    "mono": ["CourierPrime-Regular.ttf", _MAC / "Courier New.ttf", _WIN / "cour.ttf", "DejaVuSansMono.ttf"],
    "mono_bold": ["CourierPrime-Bold.ttf", _MAC / "Courier New Bold.ttf", _WIN / "courbd.ttf", "DejaVuSansMono-Bold.ttf"],
    "stamp": ["Anton-Regular.ttf", _MAC / "Impact.ttf", _WIN / "impact.ttf", "DejaVuSans-Bold.ttf"],
    "bold": [_MAC / "Arial Bold.ttf", _WIN / "arialbd.ttf", "DejaVuSans-Bold.ttf"],
    "seal": [_MAC / "Songti.ttc", _WIN / "simsun.ttc", _WIN / "msmincho.ttc", "NotoSerifCJK-Bold.ttc", "DejaVuSerif-Bold.ttf"],
}
FONTS["hand_bold"] = FONTS["hand"]
_font_cache = {}


def _search_linux(name):
    for root in _LINUX:
        if root.exists():
            for p in root.rglob(name):
                return p
    return None


def font(role):
    """Path to a font file for this role, the best one this machine has. Never fails: falls back to PIL's own font."""
    if role in _font_cache:
        return _font_cache[role]
    for c in FONTS[role]:
        if isinstance(c, str):
            for d in (SKILL / "fonts", HERE / "fonts"):
                if (d / c).exists():
                    _font_cache[role] = str(d / c)
                    return _font_cache[role]
            p = _search_linux(c) if not IS_WIN and not IS_MAC else None
            if p:
                _font_cache[role] = str(p)
                return _font_cache[role]
        elif Path(c).exists():
            _font_cache[role] = str(c)
            return _font_cache[role]
    try:  # Pillow >= 10 ships a scalable default font
        import PIL
        p = Path(PIL.__file__).parent / "fonts" / "DejaVuSans.ttf"
        if p.exists():
            _font_cache[role] = str(p)
            return _font_cache[role]
    except Exception:  # noqa: BLE001
        pass
    raise SystemExit(f"No font found for '{role}'. Run the setup script (it downloads free fonts into fonts/).")


# ---------------------------------------------------------------- word timings

WHISPER_MODEL = setting("YTF_WHISPER_MODEL")  # e.g. large-v3-turbo (default), medium.en, small.en (slow PCs)


_fw = None  # the faster-whisper model, loaded once


def transcribe(path, language=None):
    """Word timings of an audio file: [{"word": str, "start": s, "end": s}, ...].
    Apple Silicon uses mlx-whisper (fast, on the GPU); everything else uses faster-whisper (CPU int8, or CUDA if
    there's an NVIDIA GPU). Pick a smaller model with YTF_WHISPER_MODEL on slow machines."""
    path = str(path)
    backend = setting("YTF_WHISPER", "mlx" if APPLE_SILICON else "faster")
    if backend == "mlx":
        try:
            import mlx_whisper
            repo = {"large-v3-turbo": "mlx-community/whisper-large-v3-turbo", "medium.en": "mlx-community/whisper-medium.en-mlx",
                    "small.en": "mlx-community/whisper-small.en-mlx"}.get(WHISPER_MODEL or "large-v3-turbo",
                                                                          WHISPER_MODEL or "mlx-community/whisper-large-v3-turbo")
            res = mlx_whisper.transcribe(path, path_or_hf_repo=repo, word_timestamps=True, language=language)
            return [dict(word=w["word"], start=w["start"], end=w["end"]) for seg in res["segments"] for w in seg.get("words", [])]
        except ImportError:
            pass
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise SystemExit("No Whisper installed. Run the setup script, or: pip install faster-whisper")
    global _fw
    if _fw is None:
        device, ctype = "cpu", "int8"
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                device, ctype = "cuda", "float16"
        except Exception:  # noqa: BLE001
            pass
        _fw = WhisperModel(WHISPER_MODEL or "large-v3-turbo", device=device, compute_type=ctype)
    segs, _ = _fw.transcribe(path, word_timestamps=True, language=language, vad_filter=False)
    return [dict(word=w.word, start=w.start, end=w.end) for s in segs for w in (s.words or [])]


def ffmpeg_ok():
    import shutil
    return shutil.which("ffmpeg") and shutil.which("ffprobe")


if __name__ == "__main__":
    print("skill:", SKILL)
    for r in FONTS:
        print(f"font {r:10s}", font(r))
    print("channel:", channel(), "| x264:", x264_preset(), "| whisper:", WHISPER_MODEL or "large-v3-turbo")
