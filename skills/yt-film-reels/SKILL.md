---
name: yt-film-reels
description: >-
  Create or revise vertical illustrated Reels, Shorts, and serialized social stories with yt-film. Use when
  the user wants phone-first framing, episodes with hooks and cliffhangers, conversational narration, timed
  captions, character pop-ups, animated map callouts, Foley, or numbered portrait MP4s. Use the landscape
  yt-film skill for long-form documentaries and explainers.
---

# yt-film reels

Use [short-form production](../../references/short-form.md) for the full workflow. Watch [Caesar and the Pirates](../../examples/caesar/README.md) for a finished four-part example. The root [yt-film skill](../../SKILL.md) covers landscape films.

Use the [Caricature Stylesheet](../../styles/caricature/README.md) when the user wants the matte gouache and ink look from the sample. It includes art references, prompts, colors, type and portrait layout values.

1. Use the requested destination, audience, format, and runtime. For a series, choose the question each episode answers and the turn that sends viewers to the next one. Add a short re-entry line to later episodes. Inventory usable art, narration, stems, and timing before generating anything.
2. Audition the voice and write for speech. Fit revised takes to picture windows and cue the reveal, caption, transition, or Foley on what is actually said. Keep dry voice separate from music and effects. Apply the user's language choices consistently to the audio and captions.
3. Compose for portrait. Generate cutaways for missing actions and reactions. Use the [character animation style](../../references/character-popups.md) for cast and prop introductions. Mix quick moves with holds, draw maps in story order, and leave room for captions and app controls.
4. Add separate passes for ambience, action Foley, transition and animation cues, and the score. Keep speech clear and give important pauses room. Check stills and short playback before the full export, then check each encoded MP4 with [check_reels.py](../../scripts/check_reels.py). Deliver in posting order with runtimes.

The bundled long-form renderer outputs landscape. Use a portrait compositor or editor driven by the project cues. Keep the edit plan and separate stems for revisions.
