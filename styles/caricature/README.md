# Caricature Stylesheet

Use this preset for round-headed caricatures, warm ink outlines, matte gouache, and paper overlays. It contains the settings used in the four *Caesar and the Pirates* reels. For a new story, make cast sheets for its characters using the prompt below, then apply the [JSON tokens](stylesheet.json) in your compositor or copy the layout into your editor. Scale the pixel values from the 1080 × 1920 reference canvas and check the result at phone size.

[See the style in six frames from the finished episodes](export-frames.jpg).

## Illustration

| Reference | Use |
| --- | --- |
| [Style card](style-card.png) | Matte gouache, warm ink outlines, muted color and historically grounded scenery |
| [Caesar cast sheet](caesar-cast.png) | Sandy waves, cream tunic, violet stripe and red-brown traveling cloak |
| [Pirate captain cast sheet](captain-cast.png) | Black beard, ochre-and-rust striped headscarf and sheepskin vest |
| [Blank paper base](paper-base.png) | Background for maps, number cards and credits |

**Prompt starter**

> A single full-bleed illustration in the matte gouache and ink style of the supplied reference. Use crisp warm ink outlines, faint paper grain and muted teal, chalk stone, ochre and terracotta. Draw simple round-headed stick caricatures with two small dark dot eyes, a clear mouth shape, thin ink limbs and rounded hands. Keep the clothing, props and setting grounded in the scene's place and period. Match only the supplied cast sheets for characters named in this shot. Use the style card for brushwork and color. Keep the subject within the safe crop, with space for the camera and captions. Leave lettering, labels and numerals for the edit.

Add the actual action and expression to every prompt. Use native 9:16 for close-ups and most action inserts, a wider source when geography or several characters matter, and genuine alpha for a single character or prop that pops up. For each expression cut, keep hair, costume, facial proportions and light consistent with the adjoining shot. Inspect the pose, hands, crop, and whether anyone from a reference image has appeared in the wrong scene.

## Color and typography

The matte is deep teal `#1B2A2C`. Cream `#FAEED4` carries headlines, captions, and inset borders. Gold `#FBC664` emphasizes a spoken word or a reaction mark. Charcoal ink `#27211C` and rust `#A43F36` carry labels, counters, map pins and routes over tan paper. Refer to the JSON for the card and map surface colors.

Use **Anton Regular** for the large hook and cliffhanger titles, **Arial Bold** for sentence-case captions, **Courier Prime Bold** for names and episode markers, and **Caveat Regular** for rare handwritten reactions. Use comparable fonts with similar weight and width when the original face is unavailable. The repo's font setup already supports the bundled font roles used by the pop-up demo.

## Portrait composition

- **Opening and cliffhanger:** darken the art behind the title. Start the headline near `(88, 290)` with one or two short lines. Put the series line above it. Keep just one title and let the image do the rest.
- **Story image:** play faces and inserts full-bleed. Put a wide scene in the cream-bordered window over a dim teal art-derived backdrop when the scene needs room. Keep the small part counter near the top right during the story.
- **Captions:** use about 62 px with a dark outline and shadow. Center short phrases in the lower-middle caption box. Use gold sparingly where a word carries the reveal. Check app controls on the target screen before settling the placement.
- **Maps and numbers:** use the paper base and rust for the count, circle or route the viewer is following. Put the spoken names at the ends of leader lines and keep the finished map readable.
- **Character cards:** place a single cutout on the cream card with a small name and optional role. Pair the slide or pop with a short sound. Use the [reusable overlay](../../references/character-popups.md) and move the card to an open area when it would cover a face.

The character designs, paper, and palette are an example preset for the reels skill. Choose different art and colors when a project calls for a different look.
