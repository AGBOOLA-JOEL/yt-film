# Short-form reels and serialized stories

Use this when the deliverable is a portrait reel or a story released in parts. Build from the research and source assets when a landscape master exists. Recut for a phone screen and design each part around its own question and payoff.

See the [Caesar sample episodes](../examples/caesar/README.md) and the [reusable character pop-ups](character-popups.md) for finished examples.

## Plan the episodes before commissioning art

- Use the audience, destination, aspect ratio, runtime limits, and part count supplied by the user. If the destination is unspecified, 1080 × 1920 portrait, H.264/AAC, and the source cadence (24 fps in yt-film) are good starting choices. Check current platform rules when the destination affects delivery. If the user asks for more than one minute per part, leave enough margin for pacing edits and check the actual encoded duration of each episode.
- Start part one with the surprising action or contradiction and bring in just enough context to understand it. Open every later part with a quick re-entry line and a relevant image so it works for someone who missed the previous one. Give each part a payoff before the next question. Break after a reversal, a threat dismissed as a joke, or a decision left unresolved. Let the final part answer the opening question.
- For the Caesar series, four cuts of about 1:20–1:30 ended on the approaching pirates, their laughter at Caesar's threat, the governor's delay, and the conclusion. These worked because the next part answered the previous part's open question. The number of parts came from the story and the requested runtime.
- Write for speech. Use short sentences, concrete verbs, and a question or aside when it sounds natural. Save the names and dates that help the viewer follow the action. Mark reconstructions as such and keep singular or disputed source claims attributed. Keep any source list in the end card or release notes when it would interrupt the spoken flow.
- Apply the requested audience and wording standard to both recorded dialogue and captions. For example, use a requested substitution such as “unalived” in the actual take, or soften a graphic line while preserving its meaning and source. Keep sensitive scenes and their sound cues restrained. Inspect the final export for the old wording if you replace a take.

## Lock the voice and the picture cues

Audition a short passage that contains a reveal, a quieter beat and any difficult names. Agree on the voice before generating a whole film. A scratch read is useful to cut picture when the user wants to settle narration later. Keep the narration, music, and effects as separate stems and retain dry takes and a timed script.

Choose image and voice providers independently. An available built-in image tool can create project assets even when the user has no image API billing. Save approved images under stable names in the project and keep the prompt and reference list with the edit. For speech, check that the chosen route works on a sample before committing to a batch. Pass credentials through the configured environment or a hidden prompt, and keep them out of the edit files and logs.

Work from the audio the viewer will hear. Use word timestamps for exact reveals and caption changes, and cue the important words to the corresponding reaction, number, map mark or cut. For an existing cut, give replacement lines picture windows. Rewrite and rerecord a line that would need a conspicuous speed increase, especially when it contains a joke or a pause. Trim extended dead air from the picture and all audio/caption tracks together. Leave breathing room where it serves a reveal.

Build captions from the approved script using the audio timings. Transcription can help locate words. Correct invented words, names, numbers and intentional rewrites against the recorded take. Use short phrases, strong contrast and occasional emphasis. Check the destination's interface on a phone so captions, faces and labels sit clear of buttons and bottom overlays.

A useful edit plan has one shared timebase and explicit source-to-episode offsets. Split, prepend the recap, and trim all tracks using the same boundaries.

| Cue | Picture and motion | Text or mark | Sound |
| --- | --- | --- | --- |
| The speaker names the island | Establish the coast, then reveal the map | Circle the island and draw a short leader to its name | Short pencil stroke and pin tap |
| The captain hears the higher price | Quick push and small settling correction | Counter lands on the new value, followed by a reaction | Light ticks, then one silver click |
| The narrator names Cornelia | Hold on the conversation and slide in her portrait | Name and relationship on a small card | Soft paper rustle |

## Reframe and animate with a reason

- Check existing cast sheets and scenes before generating. Ask for native 9:16 on new shots that need a whole face, gesture or object in portrait. Reframe a horizontal scene by subject, or set it in a larger portrait composition when both people or the geography matter. Check the start, middle, and end of the move for cut-off faces, hands and props.
- Generate cutaways where a fresh view improves a beat. A hand passing a pouch, dice landing on stone, a scale accepting silver, an oar entering the water, or a prison latch tells the audience something about the action. Use a close reaction or matching expression edit where the speaker's change of mood is the point. Reuse the approved style and only the relevant cast references. Recheck that unrelated reference characters did not appear in the new shot.
- Mix sharp moves with calm holds. Use a snap push for a reveal, a short lateral pan to find the reaction, and a slower drift or pullback for geography or suspense. If a little clumsiness fits the tone, let a few quick moves overshoot and settle. Keep the subject readable. Save a hard cut, paper wipe or punch zoom for a change in emphasis rather than applying the same transition to every cut.
- Pop in a person or prop on the word that introduces it. Use an isolated transparent PNG, a clean silhouette, and a small slide or overshoot with a brief hold. Reserve space so the insert leaves the face and captions readable. A dignified character introduction can move gently. A raised eyebrow, a bored face, a short stamp or a sketch mark can land more sharply on a comic beat.
- Use real coastlines on maps. Reveal one pin, circle or leader as the narrator names the place, and animate a dashed route in travel order. Separate closely spaced labels with leader lines. Mark a reconstructed route as approximate. Hold the finished map long enough to read at phone size.

## Give the edit a sound pass

Keep narration centered and intelligible. Mix a low room, shore, deck or campfire bed for place, then add short Foley tied to visible movement. Give distinct actions distinct sounds. A pouch can rustle, coins ring, dice rattle on stone, an oar splashes, and a latch clicks and settles. Use a short swipe on a paper transition, a pencil scratch as a line draws, a tap at the end of a map pin, and a small accent when a pop-up lands. Leave some cuts clean and let important pauses breathe. Keep closely spaced sounds from stacking into one loud hit.

Use gentle stereo placement for off-center actions and check the result on a phone speaker or in mono. Duck score, ambience and busy effects beneath the voice. Allow a quiet breath before a reveal, and use a lighter touch around a serious outcome. Reuse the engine's cue vocabulary where it fits, or synthesize isolated effects and mix them alongside the saved stems in the project renderer. Set loudness for the destination. About −14 LUFS integrated and pre-encode true peaks around −1.5 to −2 dBTP are useful starting points. Meter the delivered AAC because encoding can raise peak levels.

## Compose, export and check each part

The bundled `film.py` and `final.py` workflow is landscape. Keep its master and assets available, and build the portrait layout and episode timing in a project-specific compositor or editor. An OpenCV/Pillow compositor can use the existing still sources and FFmpeg can encode and mux each numbered episode. Reuse verified art, dry narration and stems. Save scene/overlay timing and pause trims in the edit plan so a revised voice or effect can be rebuilt without redoing the art.

1. Check representative vertical stills and a short section with audio before a long render. Use a reveal, a caption on a busy picture, a pop-up and a map when present. Check every episode opening and ending.
2. Export a numbered MP4 per episode. If the change was audio only on a locked cut, remux the audio with `-c:v copy`. Recompose affected sections when captions, timing or overlays change.
3. Check encoded dimensions, fps, duration, audio channels, loudness and true peak. Decode both tracks and spot-check the final frames around cuts and any wording changes. Use [video_stills.py](../scripts/video_stills.py) for portrait-safe contact sheets.

```bash
python scripts/check_reels.py --min-seconds 60 --fps 24 --stereo part-01.mp4 part-02.mp4
```

Use `--min-seconds 60` only when every part must be longer than a minute. The checker reports measured loudness and true peak so the mix can be judged against the chosen delivery targets. Deliver links in posting order with runtimes. Keep publication in the user's requested scope.
