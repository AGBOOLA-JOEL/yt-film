# Art styles: the suggested look, and how to use your own

## The suggested look (what the Chadwick example uses)
**Egg-headed people in an era-accurate real world**, ink line with soft matte gouache in muted pastel colour, like a
hand-painted graphic novel. People share one stylised figure (an egg-shaped head, two small dark oval eyes, one line
for the mouth, no nose, ears or brows) and differ by hair, hats, clothes and build. The world around them is real and
detailed: the buildings, vehicles and objects of the place and year.

Why it works with this engine:
- **Faces the engine can animate**: two clean eyes and a mouth line can blink, glance, widen, smile, talk (signature.py).
- **No uncanny real faces**, and no likeness problems when telling true stories about real people.
- **Matte paint takes added layers well**: smoke, breath, flames, light, snow and drawings sit on it naturally.
- **Ink versions** of scenes and sketch sheets exist naturally, so pictures can draw themselves.

It is only a suggestion. The engine is not tied to it.

## Using another style
Anything flat enough to read well at 1080p works: watercolour, linocut, ligne claire comic, 1950s print, paper
cut-out, children's-book pastel, chalk pastel, noir ink wash, anime backgrounds, oil sketch, mid-century travel poster,
woodcut. Tell Claude the style (attach two or three example images if you have them) and it writes the opener and the
style card prompt for it. Keep these engine needs in mind:

| The engine does | So the style needs |
|---|---|
| eased camera moves over a still (push-ins, pans) | sharp focus everywhere, no baked-in depth of field or motion blur |
| acting faces | for faces you want to act: two clear eyes and a mouth that reads as a line or simple shape |
| living layers (smoke, flames, light, weather) | painted smoke/steam as soft separate shapes; no strong glow/bloom already painted in |
| drawing a scene in (ink, then paint) | a clean line version of a few scenes (`_lines`) |
| drawings made live on pages | sketch sheets with separate drawings + their line versions |
| typed labels and writing on objects | **no readable text** in the images; blank signs, papers and screens |
| cropping to 2:1 | key things away from the very top and bottom edges |

Photorealistic styles work technically but lose most of the charm (drawings, acting faces) and raise likeness
issues with real people; a stylised look is strongly recommended.

## Making your own look stand out
Pick the style, a palette and one or two signatures of your own (a recurring prop, a colour for one character, a
paper texture on every page) and keep them for every film. Change the ending (cta.md), the footnote art
(`assets/footnote/`: replace hand.png, note.png, board.png with your own drawings, same names) and the thumbnail
style, so your channel looks like you, not like the example.
