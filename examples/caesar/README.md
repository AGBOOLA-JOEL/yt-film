# Caesar and the Pirates

Four finished portrait episodes in posting order. This is the [short-form workflow](../../references/short-form.md) example. The 1080 × 1920, 24 fps exports include timed captions and stereo narration, score and effects.

| Part | Watch | Length | Look for |
| --- | --- | --- | --- |
| 1 | [The Wrong Passenger](video/01%20-%20The%20Wrong%20Passenger.mp4) | 1:20 | The 20-to-50 counter, Cornelia's entrance around 0:25, and the ships closing in |
| 2 | [The Prisoner Who Raised His Ransom](video/02%20-%20The%20Prisoner%20Who%20Raised%20His%20Ransom.mp4) | 1:28 | Dice Foley, the poetry scroll around 0:54, and the crew laughing off the threat |
| 3 | [Caesar Came Back](video/03%20-%20Caesar%20Came%20Back.mp4) | 1:29 | The return route and oar splash around 0:49–0:54, then the waiting stamp |
| 4 | [The Governor Told Him to Wait](video/04%20-%20The%20Governor%20Told%20Him%20to%20Wait.mp4) | 1:28 | The latch around 0:20, the quiet after the verdict, and the conclusion |

The three transparent illustrations in [art/](art/) were generated with ImageGen for this series. Use them to try [the character pop-up effect](../../references/character-popups.md), or provide your own transparent PNGs. Run the standalone animation demo using the repository's Python environment and FFmpeg.

The [Caricature Stylesheet](../../styles/caricature/README.md) includes the original style card and cast references, the blank paper base, and the color, type and layout values used in the exports.

```bash
python examples/caesar/popup_demo.py popup-demo.mp4
```

The four episode MP4s are reference exports. The demo renders the reusable pop-up effect with the included artwork.
