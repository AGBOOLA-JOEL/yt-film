# Claude is the driver: go past the base set

The engine ships a base set of effects, sounds, transitions and ways to illustrate. That set is a floor. The pitfall
in every film, landscape or portrait, is to reach only for what is already defined, so every story ends up with the
same rain, the same red circle, the same whoosh. The base keeps films consistent; what makes one film worth watching
is what was made for that story alone.

So past the base settings Claude pieces the film together and is expected to get creative. Reuse a base effect when
it truly fits. When the story has something the base does not cover, make it for this film, or look it up.

## The creative pass (do it for every film, before the shot lists)

Read the script and the image guide, then write down, in the project's `OUTLINE.md` or the batch notes:

1. **What this story has that no other story has.** Its objects (a ransom purse, a forged cheque, a match), its
   places and weather (a sea crossing, a prison yard, snow on a mountain), its period media (telegraph, newsprint,
   wax seals, radio), its recurring idea (a number that keeps rising, a lie that keeps growing).
2. **Three to six things made for it.** Aim for at least one of each kind across the film:
   - a **picture effect** (spray off the bow, ink bleeding through a letter, a candle guttering, dust in a cell);
   - a **transition** that belongs to the story (a sail wiping across, a wax seal stamping the next shot in, a
     page turn, a comic panel breaking out, glass shattering away);
   - a **sound** (the oar in the water, the latch of that particular door, a market, a ship's timber);
   - an **illustration device** (a ledger that fills in, a route drawn in travel order, a tally scratched on a wall,
     a counter, a stamped verdict, a comic page, a sketch that corrects itself).
3. **Where each one lands.** On a real beat of the narration, once or as a motif that returns two or three times.
   A device used on every shot stops being seen.

Then build the shot lists with the base set and these together.

## How to add something (the engine's open doors)

Nothing here needs a change to the engine. Put the film's own pieces in its film module (`<film>.py`, as `chad.py`
and `grant.py` do) and call them from the shot lists.

| You want | Write | Use it with |
| --- | --- | --- |
| Something over the finished frame (a card, a counter, a stamp, a vignette, a frame-wide wash) | `f(img, t, shot, cam) -> img` | `b.overlay(f, t0, t1)`, or `post=[f]` on one shot |
| Something that changes the picture itself and moves with the camera (a flag stirring, water, a flicker, a lifted object) | `f(img2x, t) -> img2x` on the 2x source | `src_fx=[f]` on a shot |
| A transition | `f(a, b, u) -> frame`, u from 0 to 1 | `trans=(f, seconds)`, or name it: `film.TRANSITIONS["sail"] = f` then `trans=("sail", 0.5)` |
| A synthesised sound | `@film.sfx_kind("anvil")` on `f(e, L, sr, rng) -> samples` | `b.fx("anvil", t, db=-16)` |
| A recorded sound | a WAV in `audio/sfx/` | `b.fx("wav", t0, t1, path=..., db=-18)` |
| A whole shot drawn by code | an object with `img2x(t)` and `pen(t)` | `b.custom(t0, obj, cam, img)` |
| A drawing on a page or on the picture | `Marks`, `Page`, `Paper` (strokes, text, lifts from a sheet) | any shot |

Build from the helpers already there: `film.ease`, `film.glow`, `film._hit` / `_bp` / `_lp` / `_place` for sound,
`reel.put` to lay an RGBA picture on the frame, `fx2.Live`, `fx2.Lift`, `fx2.Draw`, `fx3.Scrap`.

`film.sfx_kinds()` lists every sound the engine knows. A sound name it does not know is reported by `b.check()` and
printed at render time; it used to pass in silence.

## Looking things up

- **Sounds the synthesiser can't make well** (a real crowd in a language, a specific animal, a period machine): look
  for a recording that is CC0 or public domain, ask the user before downloading, save it under `audio/sfx/` and
  note the source and licence in `audio/sfx/SOURCES.md`. Trim and level it; play it with the `wav` kind.
- **Events and real detail**: when a beat turns on what something looked or sounded like (the ship type, the coin,
  the uniform, how a telegraph office worked), look it up and let the detail drive the effect, the drawing or the
  sound. A specific true detail beats a generic effect.
- **Technique**: when a look is wanted that the engine has never done (a zoetrope flicker, a woodcut reveal, a
  split screen), work out how it is built, write it as one of the functions above, and test it on stills first.

## The rules that still hold

- The voice leads. Effects sit under it, never crowd the narration, and stay realistic; drawn lines and labels
  must contrast with what is under them; nothing unreadable passes `b.check()`.
- One strong idea per beat. Do not stack a transition, an effect, a pop-up and a sound on the same word.
- Vary the marks and the hooks from film to film; do not repeat last film's signature move as this film's.
- Test on stills (`b.still(t)`) and a short preview before a full render.

## After the film

What worked and would serve other stories moves into the engine (`fx2.py`, `fx3.py`, `reel.py`, the sound list) and
gets a line in `references/engine.md`. What was particular to the story stays in that film's module and its example
folder. That is how the base grows without every film looking like the base.
