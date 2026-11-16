# Portrait reel proof: the opening of the Grant film

The first 39 seconds of the Grant film (the general's last $210), rendered by the film engine in portrait mode
from the same pictures, voice and score as the landscape film. It shows the explainer set working in a reel:

- a headline with a series label, an episode badge and word-timed captions with gold emphasis (`reel.py`);
- a wide picture reframed by subject (each pile close as it is named), sums typed onto the picture, a drawn circle;
- the same picture shown whole in a framed window, with the total typed and underlined inside it;
- a whip cut and a flash cut, firelight, faces reframed from wide pictures, a typed name;
- the question drawn live on a blank page, with the captions kept up over it;
- sounds tied to what is seen: coins, a pop on the total, paper swipes on the cuts, a clock, a fire.

`shots_reel.py` is the shot file. It needs the Grant project (its `incoming/`, `voice/b1_*` and `audio/music/`);
copy it into that project's `tools/` and run:

```bash
python tools/shots_reel.py --portrait
```

Add `--stills out.png` for a contact sheet of twelve frames instead of a render. `grant_reel_proof.mp4` is the
result (720 x 1280 copy). See [portrait mode](../../references/portrait.md).
