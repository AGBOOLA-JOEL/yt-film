"""Start a film project: a folder with the engine copied into tools/ and every folder the pipeline expects.

    python scripts/new_project.py my_story                   -> <workspace>/my_story/
    python scripts/new_project.py chadwick --example chadwick   the finished example, ready to re-render
    python scripts/new_project.py my_story --dir D:/films     choose where (else YTF_WORKSPACE, else ~/yt-film-projects)
    python scripts/new_project.py my_story --update-engine    refresh tools/ with this repo's engine (keeps your shot files)
    python scripts/new_project.py my_film --format explainer --look clean
                                                              a format (spine template in OUTLINE.md) and an engine
                                                              look (YTF_LOOK in .env); see references/formats.md
                                                              and references/art-styles.md

The project layout:
    my_story/
      OUTLINE.md  IMAGE_GUIDE.md  SCRIPT.md  TEST_SCRIPT.md
      incoming/00_style 01_cast 02_scenes 03_sheets 04_bases 05_photos   <- your generated images go here
      tools/      the engine (film.py, fx2.py, seq.py ...) + your film's files (<story>.py, shots_b1.py ...)
      voice/      narration and word timings          audio/music/  score cues      audio/walla/  crowd murmur
      build/      caches (safe to delete)              renders/      batch renders and the final film
      .env        your settings (copied from .env.example the first time)
"""
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FOLDERS = ["incoming/00_style", "incoming/01_cast", "incoming/02_scenes", "incoming/03_sheets", "incoming/04_bases",
           "incoming/05_photos", "build/edit", "voice", "audio/music", "audio/walla", "renders", "dubs"]
TEMPLATES = {
    "OUTLINE.md": "# {name}: facts and sources\n\nEvery fact the narrator will state, with its source. Mark anything with only one source "
                  "or that can't be confirmed (the script then says \"reportedly\" or words around it).\n\n| # | Fact | Source | Strength |\n|---|---|---|---|\n",
    "SCRIPT.md": "# {name}: narration\n\nOne `## ` passage per beat. Lines starting with `[` are notes (shots), never read aloud.\n\n---\n\n"
                 "## P01 · the hook\n[SHOTS: S01a, S01b]\nThe strangest true moment of the story, in a few short sentences.\n\n"
                 "## P02 · ...\n[SHOTS: ...]\n...\n",
    "TEST_SCRIPT.md": "# {name}: 30-second test\n\n---\n\n## T01\nA short line to test the drawing.\n\n## T02\nAnother.\n\n## T03\nAnother.\n\n## T04\nAnother.\n\n## T05\nThe end of the test.\n",
    "IMAGE_GUIDE.md": "# {name}: image guide\n\nWritten by Claude from references/image-guide.md (ask: \"write the image guide\").\n",
}


SPINES = {  # the spine template each format starts from (references/formats.md)
    "story": ["what someone wanted", "BUT ... SO the decision / the first wrong act  [DRIVE]", "SO it grew ...",
              "BUT ...", "SO it broke ...", "the cost, and the twist"],
    "explainer": ["the puzzling fact", "the naive answer, BUT it fails", "SO the real mechanism, step 1  [DRIVE]",
                  "THEREFORE step 2 ...", "THEREFORE step 3 ...", "what it means for you"],
    "countdown": ["the promise of the list", "number N: hook, turn, payoff", "number N-1 (stronger) ...", "...",
                  "number 1: the strongest, pays off the title  [DRIVE on the first entry]"],
    "rise-fall": ["the problem it solved", "SO the breakthrough  [DRIVE]", "THEREFORE the boom (numbers)",
                  "BUT the mistake / the rival", "SO the fall", "what's left today"],
    "storytime": ["the setup in one breath", "BUT what went wrong  [DRIVE]", "SO it got worse", "the moment",
                  "what changed"],
    "kids": ["a small hero wants something", "SO they try  [DRIVE]", "BUT it goes wrong", "SO they help / are helped",
             "the one thing they learn"],
    "summary": ["the big claim", "BUT why it's surprising", "idea 1 + its example story  [DRIVE]", "idea 2 ...",
                "idea 3 ...", "the strongest objection", "what to take away"],
    "case-study": ["the result (the number)", "the situation", "SO the move  [DRIVE]", "THEREFORE the numbers as it played out",
                   "BUT the reckoning", "the lesson"],
    "news": ["what happened, in one sentence", "the background you need (only that)", "the players and what each wants  [DRIVE]",
             "SO what happens next"],
}


def spine_text(fmt):
    beats = "\n".join(f"{i}. {b}" for i, b in enumerate(SPINES[fmt], 1))
    return (f"## Spine (format: {fmt}; references/storytelling.md and references/formats.md)\n\n"
            f"QUESTION: the one question this film answers\n\n{beats}\n\n"
            "Join every beat to the last with BUT or THEREFORE/SO, never \"and then\". Show this to the user before the "
            "image guide.\n\n")


def workspace(args):
    if "--dir" in args:
        return Path(args[args.index("--dir") + 1]).expanduser()
    sys.path.insert(0, str(REPO / "engine"))
    import ytf
    return Path(ytf.setting("YTF_WORKSPACE", str(Path.home() / "yt-film-projects"))).expanduser()


def copy_engine(tools, keep_existing):
    tools.mkdir(parents=True, exist_ok=True)
    for f in (REPO / "engine").iterdir():
        if f.name in ("__pycache__",) or f.suffix == ".pyc":
            continue
        dst = tools / f.name
        if f.is_dir():
            shutil.copytree(f, dst, dirs_exist_ok=True)
        elif not (keep_existing and dst.exists() and f.name in ("voice.py", "music.py", "final.py", "walla.py")):
            shutil.copy2(f, dst)  # the film's own copies of these hold its batches / cues: kept when updating


def main():
    args = sys.argv[1:]
    names = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or args[i - 1] not in ("--dir", "--example", "--format", "--look"))]
    fmt = args[args.index("--format") + 1] if "--format" in args else "story"
    look_name = args[args.index("--look") + 1] if "--look" in args else None
    if fmt not in SPINES:
        raise SystemExit(f"unknown --format {fmt!r}: choose from {', '.join(SPINES)}")
    if look_name:
        sys.path.insert(0, str(REPO / "engine"))
        from look import PRESETS
        if look_name not in PRESETS:
            raise SystemExit(f"unknown --look {look_name!r}: choose from {', '.join(PRESETS)}")
    if not names:
        print(__doc__)
        sys.exit(1)
    name = names[0]
    proj = workspace(args) / name
    if "--update-engine" in args:
        copy_engine(proj / "tools", keep_existing=True)
        print("engine updated in", proj / "tools")
        return
    if proj.exists() and any(proj.iterdir()) and "--example" not in args:
        raise SystemExit(f"{proj} already exists (use --update-engine to refresh its engine)")
    for d in FOLDERS:
        (proj / d).mkdir(parents=True, exist_ok=True)
    copy_engine(proj / "tools", keep_existing=False)
    if "--example" in args:
        ex = REPO / "examples" / args[args.index("--example") + 1]
        for item in ex.iterdir():
            if item.name in ("look", "README.md", "research"):
                continue
            dst = proj / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst)
        print("example copied: voice, music, images and shot lists are in place")
    else:
        for fname, text in TEMPLATES.items():
            p = proj / fname
            if not p.exists():
                body = text.format(name=name)
                if fname == "OUTLINE.md":
                    head, rest = body.split("\n\n", 1)
                    body = head + "\n\n" + spine_text(fmt) + rest
                p.write_text(body, encoding="utf-8")
    env = proj / ".env"
    if not env.exists() and (REPO / ".env").exists():
        shutil.copy2(REPO / ".env", env)
    elif not env.exists():
        shutil.copy2(REPO / ".env.example", env)
    text = env.read_text(encoding="utf-8")
    if "YTF_SKILL=" not in text:  # the project finds the shared art (footnote hand, note, board) and fonts here
        env.write_text(text.rstrip("\n") + f"\n\n# where the yt-film repo lives (assets/, fonts/)\nYTF_SKILL={REPO.as_posix()}\n", encoding="utf-8")
    text = env.read_text(encoding="utf-8")
    if "YTF_FORMAT=" not in text:
        text = text.rstrip("\n") + f"\n\n# the film's format (references/formats.md); story_check.py reads it\nYTF_FORMAT={fmt}\n"
        env.write_text(text, encoding="utf-8")
    if look_name and "YTF_LOOK=" not in text:
        env.write_text(text.rstrip("\n") + f"\n\n# the engine look (references/art-styles.md): gouache clean noir chalk comic storybook blueprint\nYTF_LOOK={look_name}\n", encoding="utf-8")
    print("project ready:", proj, f"(format: {fmt}, look: {look_name or 'gouache'})")
    print("next: open it in Claude Code and say what the film is about, or see the README's 'From title to final film'.")


if __name__ == "__main__":
    main()
