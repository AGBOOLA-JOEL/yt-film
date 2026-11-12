"""Dubbed audio tracks for a finished film: the narration translated, read by Orus in the target language, each
passage fitted into its English slot (same start time, never running into the next passage), and mixed with the
film's own effects stems and score exactly as final.py does. The picture is not touched; the track has the film's
exact length, ready for YouTube Studio -> Languages -> Add dub.

    python tools/dub.py            (Spanish + French; other codes: pt de hi it ja id)
    -> <project>/dubs/out/<film>_<lang>.m4a   (work files in <project>/dubs/<lang>/)

See references/dubs.md (also how to dub a voice you recorded yourself).

Needs the project's voice/ (passage wavs' word timings), renders/bN.mp4 + bN_fx.npy, audio/music/, tools/voice.py
and tools/final.py (BATCHES, MUSIC, levels). Translation: Gemini (text), cached in dubs/<lang>/translation.json.
The voice is recorded in ~3-minute chunks (one TTS request each: the cap is ~100 requests a day); Whisper finds
where each passage starts and the chunk is cut in the pause before it. A passage that will not fit is recorded alone.
"""
import ast
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import ndimage, signal

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
FILM = ROOT.name
sys.argv = [sys.argv[0]] + [a for a in sys.argv[1:]]
LANGS_ARG = [a for a in sys.argv[1:] if not a.startswith("-")]
_argv = sys.argv
sys.argv = [sys.argv[0]]
sys.path.insert(0, str(HERE))
import voice as V  # noqa: E402  (the film's own passages, batches, synth, tighten)
import ytf  # noqa: E402
sys.argv = _argv

SR = 48000
LANGS = {"es": "Spanish (neutral Latin American)", "pt": "Brazilian Portuguese", "fr": "French", "de": "German",
         "hi": "Hindi", "it": "Italian", "ja": "Japanese", "id": "Indonesian"}
TEXT_MODEL = ytf.setting("YTF_DUB_MODEL", "gemini-3.1-pro-preview")  # any Gemini text model
OUT_DIR = Path(ytf.setting("YTF_DUB_OUT", str(ROOT / "dubs" / "out")))
MAX_SPEED, MIN_SPEED = 1.42, 1.12
# Your end line, translated by hand (models read "like the video" as "similar to the video"). {ch} = YTF_CHANNEL.
# CTA_MARK: words that identify the end-line passage in SCRIPT.md (it gets the line below instead of a translation).
CTA_MARK = ytf.setting("YTF_CTA_MARK", "like the video")
CTA_LINE = {"es": "Si esta historia se quedó contigo, dale me gusta al video y sigue a {ch} para más.",
            "pt": "Se essa história ficou com você, curta o vídeo e siga {ch} para mais.",
            "fr": "Si cette histoire vous a marqué, likez la vidéo et suivez {ch} pour en voir plus.",
            "de": "Wenn dich diese Geschichte bewegt hat, like das Video und folge {ch} für mehr.",
            "hi": "अगर यह कहानी आपके दिल में रह गई, तो वीडियो को लाइक करें और ऐसी और कहानियों के लिए {ch} को फ़ॉलो करें।",
            "it": "Se questa storia ti è rimasta dentro, metti mi piace al video e segui {ch} per altre storie."}


def final_settings():
    """BATCHES, MUSIC, MUSIC_DB, DUCK_DB, XF from the film's final.py (read, not imported: it needs the film engine)."""
    src = (HERE / "final.py").read_text(encoding="utf-8")
    out = {}
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ("BATCHES", "MUSIC", "XF"):
            out[node.targets[0].id] = ast.literal_eval(node.value)
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Tuple):
            names = [t.id for t in node.targets[0].elts]
            if "MUSIC_DB" in names:
                vals = ast.literal_eval(node.value)
                out.update(dict(zip(names, vals)))
    return out


def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def decode(p):
    r = subprocess.run(["ffmpeg", "-v", "error", "-i", str(p), "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32).copy()


def read48(p):
    x, sr = sf.read(str(p), dtype="float32")
    x = x if x.ndim == 1 else x.mean(1)
    return signal.resample_poly(x, SR, sr).astype(np.float32) if sr != SR else x


def gemini_json(prompt):
    body = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"responseMimeType": "application/json"}}
    req = urllib.request.Request(f"{V.API}/models/{TEXT_MODEL}:generateContent", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "x-goog-api-key": str(V.KEY)})
    import time
    for attempt in range(6):
        if attempt:
            time.sleep(15 * attempt)
        try:
            with urllib.request.urlopen(req, timeout=600) as r:
                d = json.loads(r.read())
            txt = "".join(p.get("text", "") for p in d["candidates"][0]["content"]["parts"])
            return json.loads(txt)
        except Exception as e:  # noqa: BLE001
            print(f"    translate retry {attempt + 1}: {str(e)[:120]}", flush=True)
    raise SystemExit("translation failed")


GUIDE = ("You translate the narration of a history documentary for a DUBBED voice track. Rules: natural, spoken, "
         "gripping documentary narration in {lang}, as a native narrator would say it; keep every fact, name, date and "
         "number exactly (write numbers and years as words, the way they are spoken); keep every hedge and qualifier exactly "
         "(around, about, nearly, reportedly, the story goes, according to one account: the film's facts depend on them); "
         "keep personal names as they are "
         "(the channel name stays as it is); quoted lines and document text are translated. LENGTH: each "
         "passage must fit the seconds given when read at a calm narrator pace, so aim for about the same number of "
         "syllables as the English, never more; shorten wording rather than lose facts. Return JSON: an object mapping "
         "each id to its translation, nothing else.")


def translate(lang, items):
    f = ROOT / "dubs" / lang / "translation.json"
    if f.exists():
        return json.loads(f.read_text(encoding="utf-8"))
    f.parent.mkdir(parents=True, exist_ok=True)
    payload = [{"id": k, "seconds": round(s, 1), "english": t} for k, t, s in items]
    out = gemini_json(GUIDE.format(lang=LANGS[lang]) + "\n\n" + json.dumps(payload, ensure_ascii=False))
    if isinstance(out, list):  # [{"id":..., "translation":...}] also accepted
        out = {o["id"]: next(v for k, v in o.items() if k != "id") for o in out}
    missing = [k for k, _, _ in items if k not in out]
    if missing:
        raise SystemExit(f"translation missing {missing}")
    f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def shorten(lang, text, english, seconds, now):
    out = gemini_json(f"This {LANGS[lang]} dubbing line reads in {now:.1f} s but must fit {seconds:.1f} s. Rewrite it about "
                      f"{int(100 * (1 - seconds / now)) + 8}% shorter, same facts, natural narration. English original: "
                      f"{json.dumps(english)}. Current: {json.dumps(text, ensure_ascii=False)}. Return JSON {{\"text\": ...}}.")
    return out["text"]


def synth(text, st):
    """V.synth with patience. The TTS model has a daily request cap (100/day on Tier 1): when the API says so, sleep
    until its reset (it gives "retry in 10h22m37s") and carry on, so one run finishes over several days by itself.
    Other failures (network blips, per-minute 429s) get a growing pause."""
    import time
    k = 0
    while True:
        try:
            return V.synth(text, st)
        except SystemExit:
            wait = daily_cap_wait()
            if wait:
                print(f"    daily TTS cap reached; sleeping {wait / 3600:.1f} h until it resets", flush=True)
                time.sleep(wait)
                continue
            k += 1
            if k > 40:
                raise RuntimeError("TTS failed after 40 rounds")
            w = min(300, 30 * k)
            print(f"    tts round {k} failed; waiting {w} s", flush=True)
            time.sleep(w)


def daily_cap_wait():
    """Seconds until the daily TTS cap resets (+2 min), or 0 when the refusal is not the daily cap."""
    body = {"model": V.MODEL, "input": [{"type": "user_input", "content": [{"type": "text", "text": "Hola."}]}],
            "response_format": {"type": "audio"}, "generation_config": {"speech_config": [{"voice": V.VOICE}]}}
    req = urllib.request.Request(V.API + "/interactions", json.dumps(body).encode(),
                                 {"Content-Type": "application/json", "x-goog-api-key": str(V.KEY)})
    import time
    msg = ""
    for _ in range(3):  # the connection itself is flaky at times: ask up to three times
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                r.read()
            return 0
        except urllib.error.HTTPError as e:
            msg = e.read().decode("utf-8", "ignore")
            break
        except Exception:  # noqa: BLE001
            time.sleep(20)
    if "per day" not in msg:
        return 0
    m = re.search(r"retry in (?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?", msg)
    h, mi, se = (int(x or 0) for x in m.groups()) if m else (1, 0, 0)
    return h * 3600 + mi * 60 + se + 120


def style(lang):
    return V.STYLE + f"; speaking {LANGS[lang]} natively, with natural {LANGS[lang]} intonation"


def atempo(x, sr, speed):
    tmp_i, tmp_o = ROOT / "dubs" / f"_ai_{os.getpid()}_{id(x)}.wav", ROOT / "dubs" / f"_ao_{os.getpid()}_{id(x)}.wav"
    sf.write(tmp_i, x, sr)
    chain = ",".join(f"atempo={v:.4f}" for v in ([speed] if speed <= 2 else [2.0, speed / 2]))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp_i), "-af", chain, str(tmp_o)], check=True)
    y, _ = sf.read(str(tmp_o), dtype="float32")
    tmp_i.unlink(); tmp_o.unlink()
    return y if y.ndim == 1 else y.mean(1)


def passage_audio(lang, pid, text, english, slot):
    """The passage in the target language, sped to fit `slot` seconds: 1.25x like English when it fits, up to
    MAX_SPEED, else the wording is shortened (twice at most)."""
    d = ROOT / "dubs" / lang
    for attempt in range(3):
        raw = d / f"{pid}_raw{attempt or ''}.wav"
        tag = raw.with_suffix(".txt")
        if raw.exists() and tag.exists() and tag.read_text(encoding="utf-8") != text:
            raw.unlink()
        if not raw.exists():
            tag.write_text(text, encoding="utf-8")
            raw.write_bytes(synth(text, style(lang)))
        x, sr = sf.read(str(raw), dtype="float32")
        x = x if x.ndim == 1 else x.mean(1)
        x = V.tighten(x, sr)
        natural = len(x) / sr / V.SPEED
        if natural <= slot:
            speed = max(MIN_SPEED, V.SPEED * natural / slot) if natural < 0.8 * slot else V.SPEED
            speed = min(speed, V.SPEED)
            return atempo(x, sr, speed), sr, text, speed
        need = V.SPEED * natural / slot
        if need <= MAX_SPEED or attempt == 2:
            return atempo(x, sr, min(need, 1.6)), sr, text, min(need, 1.6)
        text = shorten(lang, text, english, slot, len(x) / sr / MAX_SPEED)
    raise RuntimeError(pid)


CHUNK_S = 170  # one TTS request reads about this many seconds of narration (the daily cap counts requests)


def chunks(order, slots):
    """Consecutive passages grouped into ~CHUNK_S of English slots: one recording each."""
    out, cur, t = [], [], 0.0
    for pid in order:
        if cur and t + slots[pid][2] > CHUNK_S:
            out.append(cur); cur, t = [], 0.0
        cur.append(pid); t += slots[pid][2]
    return out + ([cur] if cur else [])


def _norm(t):
    return "".join(c for c in t.lower() if c.isalnum())


def chunk_pieces(lang, pids, tr):
    """Record the chunk in one request, find where each passage starts with Whisper, cut in the pause before it.
    Returns {pid: (audio, sr)}; a passage it cannot place is left out (the caller records it on its own)."""
    import difflib
    d = ROOT / "dubs" / lang
    raw = d / f"chunk_{pids[0]}-{pids[-1]}.wav"
    text = "\n\n".join(tr[p] for p in pids)
    tag = raw.with_suffix(".txt")
    if raw.exists() and (not tag.exists() or tag.read_text(encoding="utf-8") != text):
        raw.unlink()
    if not raw.exists():
        print(f"  {FILM} {lang} recording {pids[0]}-{pids[-1]} ({len(pids)} passages)", flush=True)
        raw.write_bytes(synth(text, style(lang)))
        tag.write_text(text, encoding="utf-8")
    x, sr = sf.read(str(raw), dtype="float32")
    x = x if x.ndim == 1 else x.mean(1)
    wj = raw.with_suffix(".words.json")
    if wj.exists() and wj.stat().st_mtime >= raw.stat().st_mtime:
        words = json.loads(wj.read_text(encoding="utf-8"))
    else:
        words = [[w["word"], w["start"], w["end"]] for w in ytf.transcribe(raw, language=lang)]  # mlx or faster-whisper
        wj.write_text(json.dumps(words, ensure_ascii=False), encoding="utf-8")
    T, starts = "", []
    for p in pids:
        starts.append(len(T)); T += _norm(tr[p])
    W, owner = "", []
    for i, (w, _, _) in enumerate(words):
        n = _norm(w); W += n; owner += [i] * len(n)
    t2w = {}
    for a, b, size in difflib.SequenceMatcher(None, T, W, autojunk=False).get_matching_blocks():
        for k in range(size):
            t2w[a + k] = b + k
    rms = np.sqrt(np.convolve(x ** 2, np.ones(int(0.02 * sr)) / int(0.02 * sr), mode="same"))
    cuts = [0]
    for j, s0 in enumerate(starts[1:], 1):
        hit = next((t2w[c] for c in range(s0, min(s0 + 25, starts[j + 1] if j + 1 < len(starts) else len(T))) if c in t2w), None)
        if hit is None:
            cuts.append(None); continue
        wi = owner[min(hit, len(owner) - 1)]
        t_on = words[wi][1]
        t_prev = words[wi - 1][2] if wi else 0.0
        a, b = int(max(t_prev, t_on - 1.5) * sr), int(t_on * sr)
        cuts.append(a + int(np.argmin(rms[a:b])) if b > a else b)
    cuts.append(len(x))
    out = {}
    for j, p in enumerate(pids):
        a, b = cuts[j], cuts[j + 1]
        if a is None or b is None or b - a < 0.3 * sr or (j and cuts[j] <= (cuts[j - 1] or 0)):
            continue
        out[p] = (x[a:b].copy(), sr)
    return out


def fit(x, sr, slot):
    """Speed a piece to its slot like passage_audio: 1.25x when it fits, slower if short; None when it needs > MAX_SPEED."""
    nz = np.flatnonzero(np.abs(x) > 10 ** (-42 / 20))
    x = x[max(0, nz[0] - int(0.05 * sr)): nz[-1] + int(0.15 * sr)] if len(nz) else x
    x = V.tighten(x, sr)
    natural = len(x) / sr / V.SPEED
    if natural <= slot:
        speed = min(V.SPEED, max(MIN_SPEED, V.SPEED * natural / slot) if natural < 0.8 * slot else V.SPEED)
        return atempo(x, sr, speed), speed
    need = V.SPEED * natural / slot
    return (atempo(x, sr, need), need) if need <= MAX_SPEED else (None, need)


def english_slots():
    """Per passage: (batch, start s, slot s) from the English word timings; a slot runs to the next passage's start."""
    slots = {}
    for b, pids in V.BATCHES.items():
        if b == "test":
            continue
        w = json.loads((ROOT / "voice" / f"{b}_words.json").read_text(encoding="utf-8"))
        st = {}
        for x in w["words"]:
            st.setdefault(x["p"], [x["s"], x["e"]])
            st[x["p"]][1] = x["e"]
        L = dur(ROOT / "renders" / f"{b}.mp4")
        pids = [p for p in pids if p in st]  # a passage Whisper heard nothing in keeps no slot (warned)
        for i, p in enumerate(pids):
            s0 = st[p][0]
            nxt = st[pids[i + 1]][0] if i + 1 < len(pids) else min(L - 0.4, w["duration"] + 0.8)
            slots[p] = (b, s0, nxt - s0 - 0.25)
    return slots


def mix(lang, voices, F):
    """The film's audio rebuilt with the dubbed voice (same stems, score, ducking and loudness as final.py)."""
    B = [b for b in F["BATCHES"] if (ROOT / "renders" / f"{b}.mp4").exists()]  # an ending you skipped is left out
    def src(b, kind):
        return {"mp4": ROOT / "renders" / f"{b}.mp4", "fx": ROOT / "renders" / f"{b}_fx.npy"}[kind]
    lens = [dur(src(b, "mp4")) for b in B]
    starts = np.concatenate([[0], np.cumsum(lens)[:-1]])
    n = int(sum(lens) * SR)
    voice, fx, mus = (np.zeros(n, np.float32) for _ in range(3))
    for b, t0, L in zip(B, starts, lens):
        i0, m = int(t0 * SR), int(L * SR)
        if b in voices:
            vo = voices[b]
            vo = vo * 0.5 / (np.percentile(np.abs(vo), 99.9) + 1e-9) if np.abs(vo).max() > 0 else vo
            voice[i0:i0 + min(len(vo), m)] = vo[:m]
        f = np.load(src(b, "fx"))
        fx[i0:i0 + min(len(f), m)] += f[:m]
    XF = F.get("XF", 3.0)
    runs, cur = [], None
    for b, t0, L in zip(B, starts, lens):
        cue, off = F["MUSIC"][b]
        if off is None and cur is not None:
            cur[2] += L
        else:
            cur = [cue, t0, L, off or 0.0]
            runs.append(cur)
    xf = int(XF * SR)
    for cue, t0, L, off in runs:
        x = decode(ROOT / "audio" / "music" / f"{cue}.mp3")
        i0 = max(0, int(t0 * SR) - (xf // 2 if t0 > 0 else 0))
        m = min(n - i0, int(L * SR) + (xf if t0 > 0 else 0))
        total, body = x[int(off * SR):], x[int(20 * SR):]
        while len(total) < m:
            mid = total[-xf:] * np.linspace(1, 0, xf) + body[:xf] * np.linspace(0, 1, xf)
            total = np.concatenate([total[:-xf], mid, body[xf:]])
        seg = total[:m].astype(np.float32).copy()
        seg = seg / (np.sqrt(np.mean(seg ** 2)) + 1e-9)
        k = min(xf, m // 4)
        seg[:k] *= np.linspace(0, 1, k)
        seg[-k:] *= np.linspace(1, 0, k)
        mus[i0:i0 + m] += seg
    venv = ndimage.uniform_filter1d(np.abs(voice), int(0.25 * SR))
    talk = np.clip(venv / (np.percentile(venv, 95) * 0.25), 0, 1)
    quiet = ndimage.uniform_filter1d(ndimage.minimum_filter1d(1 - talk, int(0.7 * SR)).astype(np.float32), int(0.5 * SR))
    duck = 10 ** (F["DUCK_DB"] * talk / 20) * 10 ** (F.get("SWELL_DB", 7) * quiet / 20)  # the score rises in the pauses, as in final.py
    mus *= np.sqrt(np.mean(voice ** 2)) * 10 ** (F["MUSIC_DB"] / 20) * duck
    end = int(2.5 * SR)
    mus[-end:] *= np.linspace(1, 0, end)
    y = voice + mus + fx
    d = ROOT / "dubs" / lang
    raw = d / "mix_raw.wav"
    sf.write(raw, (y / (np.abs(y).max() + 1e-9) * 0.9).astype(np.float32), SR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"{FILM}_{lang}.m4a"
    # loudness exactly as final.py: a two-pass loudnorm to -14.5, then limit the spikes and normalise to -14 LUFS
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-14.5:TP=-1.5:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    i = r.stderr.rfind("{")
    mj = json.loads(r.stderr[i:r.stderr.find("}", i) + 1])
    wav = d / "mix_norm.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af",
                    f"loudnorm=I=-14.5:TP=-1.5:LRA=11:measured_I={mj['input_i']}:measured_TP={mj['input_tp']}:"
                    f"measured_LRA={mj['input_lra']}:measured_thresh={mj['input_thresh']}:offset={mj['target_offset']}:linear=true",
                    "-ar", str(SR), str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(wav), "-af",
                    "alimiter=limit=0.45:attack=0.5:release=40:level=false,loudnorm=I=-14:TP=-2:LRA=11,aresample=48000",
                    "-c:a", "aac", "-b:a", "256k", "-t", f"{sum(lens):.3f}", str(out)], check=True)
    wav.unlink()
    raw.unlink()
    return out, sum(lens)


def dub(lang):
    P = V.passages()
    slots = english_slots()
    items = [(k, P[k], slots[k][2]) for k in P if k in slots]
    tr = translate(lang, items)
    for k, t, _ in items:  # the fixed end line
        if CTA_MARK.lower() in t.lower() and lang in CTA_LINE:
            tr[k] = CTA_LINE[lang].format(ch=ytf.channel())
    log = {}
    voices = {}
    order = [p for b, pids in V.BATCHES.items() if b != "test" for p in pids if p in slots]
    pieces = {}
    for ch in chunks(order, slots):
        pieces.update(chunk_pieces(lang, ch, tr))
    for b, pids in V.BATCHES.items():
        if b == "test":
            continue
        L = dur(ROOT / "renders" / f"{b}.mp4")
        vb = np.zeros(int(L * SR), np.float32)
        for p in pids:
            if p not in slots:
                print(f"  warning: {p} has no English timing, skipped", flush=True)
                continue
            _, s0, slot = slots[p]
            x, text, speed = None, tr[p], None
            if p in pieces:
                x, speed = fit(*pieces[p], slot)
                sr = pieces[p][1]
            if x is None:  # not placed, or too long for its slot: record this passage on its own (shortened if needed)
                print(f"  {p}: recorded on its own", flush=True)
                x, sr, text, speed = passage_audio(lang, p, tr[p], P[p], slot)
            x = signal.resample_poly(x, SR, sr).astype(np.float32) if sr != SR else x
            i0 = int(s0 * SR)
            vb[i0:i0 + len(x)] += x[:len(vb) - i0]
            log[p] = dict(text=text, speed=round(speed, 3), seconds=round(len(x) / SR, 2), slot=round(slot, 2),
                          solo=p not in pieces)
        voices[b] = vb
        print(f"  {FILM} {lang} {b} done", flush=True)
    (ROOT / "dubs" / lang / "log.json").write_text(json.dumps(log, ensure_ascii=False, indent=1), encoding="utf-8")
    out, L = mix(lang, voices, final_settings())
    fast = sum(1 for v in log.values() if v["speed"] > 1.32)
    print(f"{FILM} {lang}: wrote {out} ({dur(out):.2f} s, film {L:.2f} s; {fast} passages read faster than 1.32x)", flush=True)


if __name__ == "__main__":
    langs = LANGS_ARG or ["es", "fr"]  # default: Spanish and French
    with ThreadPoolExecutor(max_workers=int(ytf.setting("YTF_DUB_JOBS", str(min(2, len(langs)))))) as ex:  # 2 at once: more trips the TTS rate limit
        for f in [ex.submit(dub, l) for l in langs]:
            f.result()
