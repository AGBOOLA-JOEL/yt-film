# Telling the story so it can be followed

We narrate a **story**, not a biography. The film follows one line: what the main person wanted, the wrong (or wild)
thing they did to get it, how it grew, how it broke, and what it cost. Every passage pushes that line forward.
Background appears only when the story needs it, at the moment it needs it, in a sentence or two.

## What went wrong on Grant and Ward (Nov 2026)
- **A biography before the story:** of 69 passages, 15 came before the scheme began (Ward's village, the front pew,
  the train, the heiress, then Grant's life from Hardscrabble to Appomattox).
- **Explanation after explanation** with no "so" or "but" between them.
- **Every batch felt like a new start:** 11 of 14 batches faded to black at the end, most faded back in, and several
  opened by re-introducing ("Ferdinand Ward grew up in Geneseo..."). The film dipped to black every ~80 s.
- **Too many dates:** 40 years and months in 4,394 words, one every ~110 words (about every 45 s). Each date makes
  the viewer place it on a timeline in their head; after a few they stop trying and get lost.
- **Pictures held too long:** 46 of 168 shots held one picture for more than 8 s, a few for 15–20 s, while the
  narrator explained. The camera moved, but nothing new appeared.

## 1. The spine, before anything else
Before the outline and the image guide, write the **spine**: the question the film answers, then 8–12 beats where
each one follows from the last by **"but"** (a complication) or **"therefore / so"** (a consequence), never "and
then". (This is Trey Parker and Matt Stone's rule for South Park scenes; it works for any story.)

```
QUESTION  How did a 29-year-old with no money ruin the most famous man in America?
1  Ward wants to be rich fast, BUT he has nothing, SO he marries a banker's daughter and borrows her name.
2  He needs a bigger name, SO he courts Buck Grant, the ex-president's son.
3  With Grant's name on the door investors pour in, BUT there are no real profits, SO Ward pledges one bond three times.
...
```
Read it aloud. If it doesn't hold a stranger as a five-minute pitch, the film won't either. Keep it at the top of
`OUTLINE.md`; the image guide and the script are built on it, and it's shown to the user before the image guide.

## 2. The shape of the film
1. **Cold open (≤ 30 s):** the strangest true moment, mid-action (references/hooks.md). No backstory, no date list.
2. **The promise (one or two sentences):** say plainly what the viewer will find out ("How does a man with $80 in
   his pocket end up here? It starts with a young man who wanted to be rich, fast."). This is the first open loop.
3. **The drive arrives fast:** the deciding moment or first wrong act by about **15% of the film**. Backstory comes
   only as the one trait that drives it (Ward: "a disposition to be rich"), one or two passages per main person.
4. **The rise:** each beat raises the stakes. Keep the running numbers or the clock visible as they change ("$400,000
   in." "Four days left.").
5. **The turn and the fall:** the payoff the cold open promised; give it room.
6. **The cost and the twist, briefly:** what happened to the victim, to the person who did it, the irony. Only what
   answers the question; an epilogue of loose facts makes the end keep not-ending.

**Open loops:** at every act break, close the question you opened and open the next one before moving on ("He had
fooled the bank. Now he had to fool a president."). Viewers stay to have a question answered; a section that opens
no question is where they leave. Don't overdo "you won't believe what happens next"; the question must be real and
the film must pay it off.

**Re-hook every 2–3 minutes:** a reveal, a reversal, a number that shocks, a line of the person's own words. A
long stretch of explanation with no turn is where retention falls.

## 3. Every passage moves the line
For each passage in the outline write its job in one line: *what changes because of it*. A passage whose job is
"explains X" with nothing changing is cut or merged into the passage where X is used.
- **Join passages with cause, not order:** "So...", "But that meant...", "Which is why...", "The bill came due."
  Avoid "Meanwhile", "Now, about...", "Let's go back to...".
- **Explain a mechanism once, when the character uses it, and show what it causes straight after.** Never two
  explanation passages in a row.
- **One thread at a time:** finish one person's beat before going to another's, unless they're about to collide.
- **Plant early what pays off later,** just before it matters, not at the start.

## 4. Dates and time: anchor, don't list
- **One time anchor per act**, about **5–7 spoken dates in the whole film**. Say a year when the story jumps to a
  new era or when the date itself is the point ("on Christmas Eve, he slipped on the ice").
- **Everything else in relative time:** "three weeks later", "that winter", "by the next spring", "the morning after",
  "two years in". Relative time tells the viewer how much time passed, which is what they need; a date makes them
  do arithmetic.
- **Ages and stakes beat years:** "At 29, he ran the hottest firm on Wall Street" says more than "In 1881...".
- **Put the date on screen, not in the voice:** a place/date paper tag (`label="Wall Street · May 1884"`) when the
  setting changes. It orients without slowing the sentence.
- **Never two dates in one passage**, never a date in the first sentence of a batch, and no date in the cold open
  (unless the date is the hook).
- **Test:** remove every date from a passage and read it. If the order and the gap in time are still clear, leave
  them out.

## 5. Batches are cuts for the computer, not chapters
The voice and the render are split into batches of ~70–100 s; the viewer must never feel the seams.
- **Write the script as one continuous piece**, then split it into batches at a sentence where the story is
  *moving* (mid-act), not where it stops. Only 2–3 batch boundaries per film may fall on act breaks.
- **The first sentence of a batch continues the last sentence of the one before** (a "so", a "but", a reaction, the
  next action). Never re-introduce a person, a place or a time at the start of a batch.
- **No fade to black between batches.** A batch ends on a moving shot and the next begins with a straight cut (or
  continues the same picture or the same drawing). A fade out and in is allowed only at an act break, at most 2–3
  times per film: set `b.act_break = True` in that batch (`b.check()` flags any other fade at a seam).
- **The music carries across:** a cue continues from batch to batch (final.py), changing only at act breaks.
- Read the last sentence of each batch and the first of the next together; they should read as one paragraph.

## 6. Narrate for the pictures: show, then draw
The script decides what's on screen. Write each beat as **show → draw**:
- **SHOW (3–5 s):** a painted picture of the moment happening (W/M/F/D/P). The narrator says what happens.
- **DRAW (the rest of the sentence or two):** while the narrator explains *why* or *how*, something is drawn: a
  sketch inks itself on the picture or a base, numbers type, an arrow travels, a lifted object moves, a page fills,
  or the scene's `_lines` version draws itself. That is the point of illustration.
- **No picture sits alone for more than ~6 s.** If a sentence runs longer, either draw on it or cut to the next
  shot. Camera moves and living effects (smoke, flicker) don't count as new information. `b.check()` flags pictures
  with more than 6 s with nothing new drawn (`HOLD_BARE` in film.py).
- **Explanations live on drawings, not on held scenes:** the mechanism of the scheme, money flows, a map of where
  things happened, a timeline. Plan a sketch sheet panel or a base for every explanation passage.

So each script passage is written with its shots, in this form:

```
## P23 · One bond, three times
[SHOW S05d_vault (M) 0–4 s] [DRAW B02_bond: one bond, three banks, arrows 4–14 s] [SHOW S05e_ward_face (F)]
Ward had one bond. So he walked it into the first bank and borrowed against it. Then he walked the same bond
into a second bank, and a third.
```

## 7. Checks before recording the voice
1. **Retell:** after reading the script, retell it in five sentences that follow the spine. A section that doesn't
   appear in the retelling is a candidate to cut.
2. **15%:** the first wrong act or deciding moment comes by ~15% of the word count.
3. **But/therefore:** read only the first sentence of each passage in order; it should read as a story.
4. **No stacked explainers:** no two explanation passages in a row; each is followed by what it causes.
5. **Dates:** 5–7 spoken dates in the whole film, none at a batch start, never two in a passage
   (`script_check.py` counts them).
6. **Seams:** each batch's first sentence continues the last one; fades only at the 2–3 act breaks.
7. **Show → draw:** every passage longer than ~6 s of voice has something drawn in it.
8. **Facts:** every line still matches the fact list (OUTLINE.md). Following the line never means inventing links:
   if the sources don't connect two events, say so ("Nobody knows exactly when he started").

## Sources (research, Nov 2026)
- The "but / therefore" rule: Parker and Stone's NYU talk, summarised at [perell.com](https://perell.com/note/but-therefore-rule/)
  and [cheatsheet.com](https://www.cheatsheet.com/entertainment/south-park-trey-parker-and-matt-stone-1-rule.html/).
- Hooks, promise and re-hooks: [1of10 on George Blackman](https://1of10.com/blog/10-000-hours-of-youtube-scriptwriting-in-1hrs-9mins-george-blackman),
  [outlierkit](https://outlierkit.com/resources/youtube-hooks-and-retention/) (creator practice, not research).
- Open loops and the information gap (Loewenstein): [1of10](https://1of10.com/blog/storytelling-techniques-top-youtubers-use-to-keep-viewers-hooked).
- Time markers, anchors and relative time: [Engines of Narrative, "Keeping time"](https://enginesofnarrative.substack.com/p/keeping-time).
- Still pictures in documentaries: Ken Burns holds stills ~6–19 s, one idea each, timed to the narration
  ([Charlie Nelson](https://charlienelsonmedia.blogspot.com/2020/02/how-long-should-picture-be-held-in.html)); we are
  illustrated, so we hold less and draw more.
