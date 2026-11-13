"""Check the script's story flow before the voice is recorded (references/storytelling.md, section 7):

    python tools/story_check.py            reads SCRIPT.md and BATCHES from tools/voice.py

Reports: spoken dates (aim for 5-7 in the whole film, never two in a passage, none in a batch's first sentence),
passages that start with a scene-shift phrase ("Meanwhile", "Let's go back"), where the first passage tagged
[DRIVE] falls (aim: by ~15% of the words), and every batch seam (the last sentence of one batch and the first of
the next, to read together: they should read as one paragraph).

Mark the passage where the deciding moment or the first wrong act happens by putting `[DRIVE]` on its marker line.
"""
import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
YEAR_DIGITS = r"\b(1[0-9]{3}|20[0-9]{2})\b"
YEAR_WORDS = r"\b(?:eighteen|nineteen|seventeen|sixteen|twenty)[ -](?:hundred|oh|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety)(?:[ -](?:and[ -])?(?:one|two|three|four|five|six|seven|eight|nine))?\b"
DAYS = r"\b(?:Christmas Eve|Christmas Day|New Year's (?:Eve|Day)|Thanksgiving|Easter)\b"
SHIFTS = re.compile(r"^(Meanwhile|Now, about|Let's go back|Back in|Years earlier|To understand|But first)", re.I)


DRIVE_BY = {"story": 0.15, "explainer": 0.25, "countdown": 0.10, "rise-fall": 0.20, "storytime": 0.15, "kids": 0.20,
            "summary": 0.20, "case-study": 0.15, "news": 0.25}  # where the [DRIVE] passage should start, by format


def fmt():
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import ytf
        return (ytf.setting("YTF_FORMAT") or "story").strip().lower()
    except Exception:  # noqa: BLE001
        return "story"


def passages():
    s = (ROOT / "SCRIPT.md").read_text(encoding="utf-8")
    body = s.split("\n---\n", 1)[1] if "\n---\n" in s else s
    out = []
    for m in re.finditer(r"^## (P\d+)[^\n]*\n(.*?)(?=^## |\Z)", body, re.S | re.M):
        lines = m.group(2).splitlines()
        marks = " ".join(l for l in lines if l.strip().startswith("`"))
        text = " ".join(l.strip() for l in lines if l.strip() and not l.strip().startswith("`"))
        out.append((m.group(1), text, "[DRIVE]" in marks or "[DRIVE]" in m.group(0).split("\n", 1)[0]))
    return out


def batches():
    f = ROOT / "tools" / "voice.py"
    if not f.exists():
        return {}
    for node in ast.parse(f.read_text(encoding="utf-8")).body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "BATCHES" for t in node.targets):
            b = ast.literal_eval(node.value)
            return {k: v for k, v in b.items() if k != "test"}
    return {}


def dates(text):
    found = re.findall(YEAR_DIGITS, text) + re.findall(YEAR_WORDS, text, re.I)
    found += re.findall(rf"\b(?:{MONTHS})\b(?:\s+\d{{1,2}})?", text) + re.findall(DAYS, text)
    return found


def sentences(text):
    return [x.strip() for x in re.split(r"(?<=[.!?])\s+", text) if x.strip()]


def main():
    ps = passages()
    if not ps:
        sys.exit("no passages found in SCRIPT.md (## Pnn blocks)")
    words = [len(t.split()) for _, t, _ in ps]
    total = sum(words)
    problems = []
    all_dates = []
    for (p, t, _), n in zip(ps, words):
        d = dates(t)
        all_dates += [(p, x) for x in d]
        if len(d) > 1:
            problems.append(f"{p}: {len(d)} dates in one passage ({', '.join(d)}): keep one, make the rest relative")
        if SHIFTS.match(t):
            problems.append(f"{p}: starts with a scene-shift phrase ({t.split(',')[0][:30]}...): link it by cause instead")
    print(f"{total} words, {len(ps)} passages")
    print(f"spoken dates: {len(all_dates)} (aim 5-7 for a whole film; one every {total // max(1, len(all_dates))} words)")
    drive = [i for i, (_, _, d) in enumerate(ps) if d]
    if drive:
        at = sum(words[:drive[0]]) / total
        limit = DRIVE_BY.get(fmt(), 0.15)
        flag = "" if at <= limit else f"  <- later than {limit:.0%}: shorten what comes before"
        print(f"the drive ({ps[drive[0]][0]}) starts at {at:.0%} of the words{flag}")
    else:
        print("no passage marked [DRIVE]: mark the deciding moment / first wrong act to check it comes by ~15%")
    B = batches()
    idx = {p: i for i, (p, _, _) in enumerate(ps)}
    order = [b for b in B if B[b] and B[b][0] in idx]
    if order:
        print("\nseams (read each pair as one paragraph):")
    for a, b in zip(order, order[1:]):
        last = sentences(ps[idx[B[a][-1]]][1]) if B[a][-1] in idx else [""]
        first = sentences(ps[idx[B[b][0]]][1])
        print(f"  {a} ... {last[-1] if last else ''}\n  {b} {first[0] if first else ''}\n")
        if first and dates(first[0]):
            problems.append(f"{b}: first sentence has a date ({', '.join(dates(first[0]))}): continue from {a} instead")
        if first and re.search(r"\b(grew up|was born|had been born)\b", first[0]):
            problems.append(f"{b}: first sentence re-introduces someone: continue the story from {a}")
    print("problems:" if problems else "story check ok")
    for x in problems:
        print("  " + x)


if __name__ == "__main__":
    main()
