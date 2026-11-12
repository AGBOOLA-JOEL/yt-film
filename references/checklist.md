# New film: checklist

**Start**
- [ ] Story agreed (or 3–5 candidates pitched with gap checks: story-finding.md). Working title + hook type (hooks.md).
- [ ] `python scripts/new_project.py <story>`; the user's routes known: images (image-generation.md), voice (Gemini
      or their own: voice.md), music (Lyria or their own: music.md), art style (art-styles.md).

**Facts**
- [ ] `OUTLINE.md`: verified fact list with sources. Unconfirmed points flagged, to be worded carefully.

**Images**
- [ ] `IMAGE_GUIDE.md` written for their route: spine, ~150 images with coverage, opener, blocks, bases, sheets,
      exact filenames and folders (+ `IMAGE_PROMPTS.jsonl` for the API route).
- [ ] Style card chosen → cast sheets in → character blocks rewritten to match the sheets.
- [ ] Scenes, faces, line versions, sheets (+ lines), bases in (`sort_images.py` for manual downloads).
- [ ] Every image checked: hands, faces, era, no text, shape. Redos listed. Stuck chat → resume guide.

**Script and sound**
- [ ] `SCRIPT.md` written from the images; every image placed (the unused-image check); like/follow line last.
- [ ] Voice: test script first; `BATCHES`/`GAPS` set; recorded (voice.py) or imported (import_voice.py).
- [ ] Pace: every batch ~140–160 wpm (`voice.py --pace` / `import_voice.py --check`). Whisper's spellings noted.
- [ ] Music cues made or supplied; `final.py` MUSIC map set.

**Picture** (no renders without the user's go-ahead)
- [ ] Gridded sheets in engine px (`egrid.py`); `<story>.py` LIVE table: smoke, breath, flames, lamps, weather.
- [ ] Each batch: words printed → shots on `seq.py` → `stills.py bN` (check ok) → sheet looked at → fixed.
- [ ] Nothing over a face or another word; nothing dark on dark; no picture held > ~6 s without something new;
      every sheet drawing used alone when named; marks varied (not a circle every time).
- [ ] New effects tested on two frames before any full render.
- [ ] Sound plan per batch: the right sound for the place, few whooshes, pencil quiet.
- [ ] With the user's OK: `render_all.py` (parallel, sized to the machine); the ending made once (cta.md).

**Finish**
- [ ] `final.py`; MP4 checked: 1920x1080, 24 fps, ≈ −14 LUFS, peak ≤ −1.5 dB, sample stills.
- [ ] Dubs if wanted (dubs.md); thumbnails guide (thumbnails.md); sources and credits for the description.
- [ ] Tell the user what was checked and what wasn't (e.g. not watched end to end).
