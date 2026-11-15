"""Check portrait MP4s and measure the audio after encoding."""

import argparse
from fractions import Fraction
import json
import math
from pathlib import Path
import subprocess
import sys


def run_media(*args):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace", check=True)


def inspect(path, *, minimum, fps, stereo):
    probe = json.loads(run_media("ffprobe", "-v", "error", "-show_streams", "-show_format",
                                 "-of", "json", str(path)).stdout)
    picture = next((s for s in probe["streams"] if s["codec_type"] == "video"
                    and not s.get("disposition", {}).get("attached_pic")), None)
    sound = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
    if not picture or not sound:
        raise ValueError("expected a video track and an audio track")

    width, height = picture["width"], picture["height"]
    rate = Fraction(picture["avg_frame_rate"])
    duration = float(probe["format"]["duration"])
    if not math.isfinite(duration) or duration <= 0 or rate <= 0:
        raise ValueError("could not determine a valid runtime or frame rate")
    if (width, height) != (1080, 1920):
        raise ValueError(f"expected 1080 × 1920, got {width} × {height}")
    if fps is not None and rate != fps:
        raise ValueError(f"expected {float(fps):g} fps, got {float(rate):g} fps")
    if minimum is not None and duration <= minimum:
        raise ValueError(f"{duration:.3f}s must be longer than {minimum:g}s")
    if stereo and sound["channels"] != 2:
        raise ValueError(f"expected stereo, got {sound['channels']} audio channel(s)")

    # Decode the same streams we probed and meter the audio the viewer receives.
    meter = run_media("ffmpeg", "-hide_banner", "-nostats", "-xerror", "-i", str(path),
                      "-map", f"0:{picture['index']}", "-map", f"0:{sound['index']}",
                      "-af", "loudnorm=print_format=json", "-f", "null", "-").stderr
    end = meter.rfind("}") + 1
    stats = json.loads(meter[meter.rfind("{", 0, end):end])
    loudness, peak = float(stats["input_i"]), float(stats["input_tp"])
    if not math.isfinite(loudness) or not math.isfinite(peak):
        raise ValueError("the audio has no measurable programme loudness")
    return (f"{duration:.3f}s · {width}×{height} · {float(rate):g} fps · "
            f"{sound['channels']} audio channel(s) · {loudness:.2f} LUFS · {peak:.2f} dBTP")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("videos", nargs="+", type=Path)
    parser.add_argument("--min-seconds", type=float, help="each export must be strictly longer than this")
    parser.add_argument("--fps", type=Fraction, help="expected frame rate, e.g. 24 or 30000/1001")
    parser.add_argument("--stereo", action="store_true", help="require two encoded audio channels")
    opts = parser.parse_args()
    if opts.min_seconds is not None and (not math.isfinite(opts.min_seconds) or opts.min_seconds < 0):
        parser.error("--min-seconds must be a finite, nonnegative number")
    if opts.fps is not None and opts.fps <= 0:
        parser.error("--fps must be positive")
    ok = True
    for path in opts.videos:
        try:
            print(f"{path.name}: {inspect(path, minimum=opts.min_seconds, fps=opts.fps, stereo=opts.stereo)}", flush=True)
        except subprocess.CalledProcessError as exc:
            detail = exc.stderr.strip().splitlines()
            print(f"{path.name}: {Path(exc.cmd[0]).name} failed: {detail[-1] if detail else exc.returncode}", file=sys.stderr)
            ok = False
        except (OSError, ValueError, KeyError, ZeroDivisionError) as exc:
            print(f"{path.name}: {exc}", file=sys.stderr)
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
