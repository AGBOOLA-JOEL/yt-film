"""Render batches in parallel, sized to this machine (Mac, Windows or Linux).

    python tools/render_all.py                    every shots_b*.py, as many at once as this machine can take
    python tools/render_all.py b3 b7              only these (after fixing them)
    python tools/render_all.py --jobs 2           force the number running at once
    python tools/render_all.py --preview          half size, 12 fps: fast check renders (renders/bN_preview.mp4)
    python tools/render_all.py --changed          only batches whose shots file is newer than their render
    python tools/render_all.py --cta              also render the ending (tools/cta.py)
    python tools/render_all.py --force            render even if the readability check complains

Each batch logs to renders/<b>.log. Renders run at low priority, so the computer stays usable.
How many at once: about one per 2 CPU cores and per 3 GB of free memory (YTF_JOBS in .env overrides). A slow
laptop gets 1-2; a 10-core Mac with 32 GB gets 5-8. See references/performance.md.
"""
import os
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import ytf  # noqa: E402


def ram_gb():
    try:
        if ytf.IS_WIN:
            import ctypes

            class MS(ctypes.Structure):
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong), ("ullTotalPhys", ctypes.c_ulonglong),
                            ("ullAvailPhys", ctypes.c_ulonglong), ("ullTotalPageFile", ctypes.c_ulonglong),
                            ("ullAvailPageFile", ctypes.c_ulonglong), ("ullTotalVirtual", ctypes.c_ulonglong),
                            ("ullAvailVirtual", ctypes.c_ulonglong), ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
            m = MS()
            m.dwLength = ctypes.sizeof(MS)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
            return m.ullTotalPhys / 2 ** 30
        if ytf.IS_MAC:
            return int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout) / 2 ** 30
        for line in open("/proc/meminfo"):
            if line.startswith("MemTotal"):
                return int(line.split()[1]) / 2 ** 20
    except Exception:  # noqa: BLE001
        pass
    return 8.0


def auto_jobs(n_batches, preview):
    if ytf.setting("YTF_JOBS"):
        return max(1, int(ytf.setting("YTF_JOBS")))
    cpu = os.cpu_count() or 2
    per_job = 1.5 if preview else 3.0  # GB a full-size batch render can reach (big images, layers, effects)
    by_ram = int((ram_gb() - 3) // per_job)  # leave ~3 GB for the system
    by_cpu = max(1, cpu // 2)
    return max(1, min(n_batches, by_ram, by_cpu))


def natural(s):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)]


def main():
    args = [a for a in sys.argv[1:]]
    preview, force, changed, cta = "--preview" in args, "--force" in args, "--changed" in args, "--cta" in args
    jobs = None
    if "--jobs" in args:
        jobs = int(args[args.index("--jobs") + 1])
        args.remove(args[args.index("--jobs") + 1])
    names = [a for a in args if not a.startswith("--")]
    if not names:
        names = sorted([p.stem[6:] for p in HERE.glob("shots_b*.py")], key=natural)
    if changed:
        def stale(b):
            out = ROOT / "renders" / f"{b}{'_preview' if preview else ''}.mp4"
            deps = [HERE / f"shots_{b}.py"] + [p for p in HERE.glob("*.py") if not p.name.startswith("shots_")]
            return not out.exists() or max(d.stat().st_mtime for d in deps if d.exists()) > out.stat().st_mtime
        names = [b for b in names if stale(b)]
    todo = [(b, HERE / f"shots_{b}.py") for b in names]
    if cta:
        todo.append(("cta", HERE / "cta.py"))
    missing = [str(p) for _, p in todo if not p.exists()]
    if missing:
        raise SystemExit(f"missing: {missing}")
    if not todo:
        print("nothing to render")
        return
    jobs = jobs or auto_jobs(len(todo), preview)
    cpu = os.cpu_count() or 2
    env = dict(os.environ, PYTHONUTF8="1", YTF_THREADS=str(max(1, cpu // jobs)))
    (ROOT / "renders").mkdir(exist_ok=True)
    print(f"{len(todo)} renders, {jobs} at a time ({cpu} cores, {ram_gb():.0f} GB RAM){' [preview]' if preview else ''}")
    flags = (["--preview"] if preview else []) + (["--force"] if force else [])
    kw = {}
    if ytf.IS_WIN:
        kw["creationflags"] = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
    elif hasattr(os, "nice"):
        kw["preexec_fn"] = lambda: os.nice(10)
    queue, running, done, failed, t0 = list(todo), {}, [], [], time.time()
    while queue or running:
        while queue and len(running) < jobs:
            b, script = queue.pop(0)
            log = open(ROOT / "renders" / f"{b}{'_preview' if preview else ''}.log", "w", encoding="utf-8")
            p = subprocess.Popen([sys.executable, str(script)] + flags, cwd=str(HERE), stdout=log, stderr=subprocess.STDOUT, env=env, **kw)
            running[b] = (p, log, time.time())
            print(f"  started {b}", flush=True)
        time.sleep(2)
        for b, (p, log, ts) in list(running.items()):
            if p.poll() is not None:
                log.close()
                del running[b]
                mins = (time.time() - ts) / 60
                if p.returncode == 0:
                    done.append(b)
                    print(f"  done    {b}  ({mins:.1f} min)", flush=True)
                else:
                    failed.append(b)
                    print(f"  FAILED  {b}  (see renders/{b}.log)", flush=True)
    print(f"finished in {(time.time() - t0) / 60:.1f} min: {len(done)} ok" + (f", failed: {failed}" if failed else ""))
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
