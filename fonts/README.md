# fonts/

The setup scripts download four free fonts here (Windows and Linux need them; macOS already has good ones):

| File | Used for | Licence |
|---|---|---|
| `SpecialElite-Regular.ttf` | typewriter labels (dates, places, names) | Apache 2.0 |
| `Caveat.ttf` | handwriting on notes and pages | SIL OFL |
| `CourierPrime-Regular.ttf`, `CourierPrime-Bold.ttf` | counters, ledgers | SIL OFL |
| `Anton-Regular.ttf` | rubber stamps (FORGED, CLOSED) | SIL OFL |

Any `.ttf` here with one of these names wins over the system font, so you can swap in your own (keep the filename).
`python engine/ytf.py` prints which font each role is using on your machine.
