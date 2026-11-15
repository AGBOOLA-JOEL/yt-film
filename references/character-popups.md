# Character and prop pop-ups

The [Caesar episodes](../examples/caesar/README.md) use ink-and-gouache cutouts that slide onto a cream paper card, settle, hold, and slip away. Use the same overlay with different art for a name reveal, a comic reaction, or a prop that explains the action. This effect works in a portrait compositor or the landscape engine.

## Art and staging

- Generate a single waist-up character or isolated prop on transparency. Use the relevant cast sheet and a matching scene as references. Preserve simple eyes, mouth and silhouette or substitute the project's own established style. Leave text to the compositor.
- Save a PNG with genuine alpha and check its edges in the composite. Name a character with their role or relationship when needed. Keep the title short enough to read on a phone.
- Anchor the card in screen space with room for the slide. Time its entrance to the name, reveal, or movement. Let it settle before the viewer reads the label. Use restrained bounce for a serious introduction and a quicker, slightly overshooting move for a joke.
- Give the animation a short sound at its entrance or landing. Use a soft paper rustle for an introduction and a brighter pop or prop-specific sound for a comic reveal. Leave room around the narrator's line.

## Use the same overlay in another film

```python
from pathlib import Path
from character_popup import CharacterPopup

cornelia = CharacterPopup(Path("incoming/06_popups/cornelia.png"), 24.56, 26.91,
                          title="CORNELIA", subtitle="Caesar's wife",
                          pos=(0.74, 0.44), width=0.42, bounce=0.047)

# In a landscape yt-film shot list, with a Batch named b.
b.overlay(cornelia, 24.56, 26.91)
b.fx("paper", 24.62, 24.94, db=-23)
```

Use `popup(frame, t)` in a custom compositor and pass `color_order="BGR"` when the frames come from OpenCV. Set `pos` and `width` for that layout. The overlay operates on the supplied frame, so apply it to a render buffer rather than the cached source still. For an expression change, use a matching alternate still or a face cue on an audited face. See [the engine guide](engine.md) for face cues.

Run `python examples/caesar/popup_demo.py /path/to/demo.mp4` from the repository with the engine environment. This renders the three supplied PNGs on portrait paper cards without an image or speech API.
