"""Render batches in parallel, sized to this machine (Mac, Windows or Linux).

    python tools/render_all.py                    every shots_b*.py, as many at once as this machine can take
    python tools/render_all.py b3 b7              only these (after fixing them)
    python tools/render_all.py --jobs 2           force the number running at once
    python tools/render_all.py --preview          half size, 12 fps: fast check renders (renders/bN_preview.mp4)
    python tools/render_all.py --changed          only batches whose shots file is newer than their render
    python tools/render_all.py --cta              also render the ending (tools/cta.py)
    python tools/render_all.py --force            render even if the readability check complains

Each batch logs to renders/<b>.log. Renders run at low priority, so the computer stays usable.
How many at once: about one per 2 CPU cores and per 2 GB of FREE memory (counted when you start, with your apps
open), leaving 2 GB for the system; YTF_JOBS in .env overrides. Before starting each further batch it checks free
memory again and waits if there isn't room, so the computer never runs out of memory and starts swapping (seven
renders at once on a 16 GB Mac froze it and made every render ~15x slower). An 8 GB laptop gets 1; a 16 GB machine
with a browser open gets 2-4. See references/performance.md.
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


def free_gb():
    """Memory available to new programs right now (GB), or None if it can't be read."""
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
            return m.ullAvailPhys / 2 ** 30
        if ytf.IS_MAC:
            out = subprocess.run(["vm_stat"], capture_output=True, text=True).stdout
            page = int(re.search(r"page size of (\d+)", out).group(1))
            n = sum(int(re.search(rf"{k}:\s+(\d+)", out).group(1)) for k in ("Pages free", "Pages inactive", "Pages speculative"))
            return n * page / 2 ** 30
        for line in open("/proc/meminfo"):
            if line.startswith("MemAvailable"):
                return int(line.split()[1]) / 2 ** 20
    except Exception:  # noqa: BLE001
        pass
    return None


PER_JOB = {False: 2.0, True: 1.0}  # GB one batch render reaches at full size / preview (measured 1.1-1.4 GB at 1080p)
RESERVE = 2.0  # GB left for the system and the user's apps


def auto_jobs(n_batches, preview):
    if ytf.setting("YTF_JOBS"):
        return max(1, int(ytf.setting("YTF_JOBS")))
    cpu = os.cpu_count() or 2
    per_job = PER_JOB[preview]
    by_total = int((ram_gb() - 3) // per_job)
    free = free_gb()
    by_free = int((free - RESERVE) // per_job) if free is not None else by_total
    by_cpu = max(1, cpu // 2)
    return max(1, min(n_batches, by_total, by_free, by_cpu))


def room_for_another(preview):
    """True when there is free memory for one more render (always True if it can't be measured)."""
    free = free_gb()
    return free is None or free >= PER_JOB[preview] + RESERVE / 2


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
    free = free_gb()
    print(f"{len(todo)} renders, {jobs} at a time ({cpu} cores, {ram_gb():.0f} GB RAM"
          f"{f', {free:.1f} GB free' if free is not None else ''}){' [preview]' if preview else ''}")
    if free is not None and free < PER_JOB[preview] + RESERVE:
        print("  little free memory: close the browser and other heavy apps for a faster render (references/performance.md)")
    flags = (["--preview"] if preview else []) + (["--force"] if force else [])
    kw = {}
    if ytf.IS_WIN:
        kw["creationflags"] = getattr(subprocess, "BELOW_NORMAL_PRIORITY_CLASS", 0)
    elif hasattr(os, "nice"):
        kw["preexec_fn"] = lambda: os.nice(10)
    queue, running, done, failed, t0 = list(todo), {}, [], [], time.time()
    waiting = False
    while queue or running:
        while queue and len(running) < jobs:
            if running and not room_for_another(preview):  # never start a render into a full memory
                if not waiting:
                    print(f"  waiting for free memory before starting {queue[0][0]}", flush=True)
                    waiting = True
                break
            waiting = False
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
