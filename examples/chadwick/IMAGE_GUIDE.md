# Carnegie's Daughter (Cassie Chadwick): ChatGPT image guide · v1

The suggested yt-film look (one option, see references/art-styles.md): egg-headed characters
in an era-accurate real world, ink line with matte gouache, single scenes with camera moves, sketchbook sheets drawn
live, **Style A** throughout. **No 2D cutouts, no 2.5D.** Told by a **narrator** (third person). Facts, sources and
the real photos: `OUTLINE.md`.

**Real photos** again: her 1904 portrait, Carnegie in 1905, the Euclid Avenue house, the Carnegie mansion, the Ohio
Penitentiary. I download them into `incoming/05_photos/` (after your OK). In ChatGPT they're used **only as
references** for clothes, hair and buildings; faces stay egg faces.

## Story spine

**Hook type: "the document"** (an object on screen being read, typed as we watch). No "go back" line.

*A folded paper falls on a Fifth Avenue pavement. A lawyer picks it up. I type it on the note as he reads: "…I
promise to pay to the order of Cassie L. Chadwick… two million dollars… Andrew Carnegie." "It was a forgery. The
woman who dropped it — on purpose — had been forging things since she was thirteen. For the next two years, banks
across Ohio would lend her millions on the strength of that one name, without ever opening the envelope."*
Then straight into the story: *"She was born Elizabeth Bigley, in a railway town in Ontario."*

The beats in order:
1. **New York, c.1902** (hook, *plays as a comic page*): the carriage, the mansion door, the dropped note.
2. **Ontario, 1857–1879**: the railway family, a silent girl, the forged letter at 13, "Heiress to $15,000", the
   Woodstock trial where she pulls faces at the jury and walks free.
3. **Cleveland, 1880s**: her sister's furniture, Madame Lydia DeVere the clairvoyant, a doctor who keeps her 12 days.
4. **The names, 1883–1893**: Marie LaRose, Mrs Hoover, a baby son, a forged name in Toledo, the Ohio Penitentiary,
   parole.
5. **Dr Chadwick, 1893–1897**: the house on the west side, a kind widowed doctor, the faint, the marriage, Euclid
   Avenue's Millionaires' Row.
6. **Snubbed**: the neighbours never come.
7. **New York, c.1902, from inside** (*plays as a comic page*): the "chance" meeting with Dillon, the ride, the
   housekeeper and the maid's references, the wave, the secret.
8. **The sealed envelope**: Wade Park Bank, Iri Reynolds, the receipt nobody questions; the whisper spreads.
9. **Queen of Ohio, 1902–1904**: Oberlin's bank, Beckwith's own savings, diamonds, 30 closets, the gold organ, the
   parties.
10. **November–December 1904**: Newton's loan called in, Carnegie's one-line denial, the run on Oberlin, the envelope
    opened, the arrest in a New York hotel bed with $100,000 strapped to her.
11. **The trial, March 1905**: Carnegie in the gallery (reportedly), seven counts, 14 years; Beckwith dies, Spear
    goes to prison.
12. **The end**: the penitentiary with her trunks, blindness, death on her 50th birthday, a grave in Woodstock, and a
    paper on a pavement.

---

## How many images

| Group | Count | Status |
|---|---|---|
| Style card (Style A, new era) | 1 | to make |
| Cast sheets | 9 | to make |
| Footnote hand, the note, the board | 0 | already made (`yt-film/assets/footnote/`) |
| Scenes, with W / M / F / D / P coverage | 125 | to make |
| Scene line versions (scenes that draw themselves) | 4 | to make |
| Sketch sheets | 9 | to make |
| Sheet line versions | 9 | to make |
| Bases (blank story objects) | 7 | to make |
| Real photos (Commons, downloaded by me) | ~8 | after your OK |
| **Total to generate** | **164** | |

About a third of the scenes are EDITs of the picture just before. Every image will be placed in the script.

## Where to save

Everything goes under **`<your project>/incoming/`**, in the subfolder
shown, with the exact filename. Download the original PNG, not a screenshot. If an agent (Codex, a script) saves the files,
give it that **full path**.

```
incoming/00_style/    style_card.png
incoming/01_cast/     betsy, lydia, cassie, cassie_1905, leroy, dillon, reynolds, beckwith, carnegie   (refs/ for photos)
incoming/02_scenes/   S01a ... S12i and the *_lines scenes
incoming/03_sheets/   X01 ... X09 and their *_lines versions
incoming/04_bases/    B01 ... B07
incoming/05_photos/   the real archive photos (I download these)
```

Scene filenames are **beat number + shot letter**: `S07f_hall.png` is group 7, sixth shot.

## How to work in ChatGPT

- **One chat for the whole guide** (group headings only). Ask for **landscape** every time.
- Paste the **opener** once at the start, then the prompts in order, top to bottom.
- **Always attach:** `00_style/style_card.png`, plus the cast sheet of everyone named in CAPITALS in the image. For
  sheets, also attach `03_sheets/X01_ontario.png` once it exists. Where a row says *(ref: …)*, also attach that photo
  from `05_photos/` with: *"Use the attached photo only for the building / clothes / layout; paint it in our style,
  egg faces."* The photos carry printed captions (her name, "1904", a postcard title): **never copy any of it**.
- **EDIT** rows keep the same camera and objects. If ChatGPT redraws the scene:
  *"Too different. Redo as a strict edit of the previous image: same camera, same framing, only change what I asked."*
- **FACE** rows: use the face prompt below, right after the shot it comes from.
- If a character drifts: *"Match the attached character sheet exactly: same hair, clothes, height. Change nothing else."*
- **How we know her across 35 years**: always **dark-brown hair** and a **cameo brooch at the throat** (it travels
  from the farm girl's plain collar to the queen's lace). Thin and plain as a girl; dark and theatrical as Lydia;
  **stout, upright and dressed like a duchess** as Mrs Chadwick (high pompadour, lace collar to the chin, huge
  feathered hats, a fur muff she keeps things in). The **muff** is her prop: the note comes out of it.
- **Beards never cover the mouth line**: Carnegie's, Beckwith's and Reynolds's white beards sit on the chin and jaw
  **below** the mouth line, which stays clearly visible.
- **Check hands on every image with people.** Extra hand → *"She has an extra hand. Redo with exactly two arms and
  two hands, nothing else changed."*
- **No emblems, no brands**: no US eagles, seals or flags with stars on notes or buildings, no bank names or logos,
  no portraits on banknotes (banknotes are plain green-grey engraved paper), no real newspaper mastheads.
- **No readable text anywhere**: notes, cards, letters, receipts, ledgers, telegrams, newspapers, signs and brass
  plates stay blank or illegible. I write every word live.
- **No guns**: police and marshals carry nothing in their hands but papers or hats.
- If ChatGPT refuses something, drop that element and add `(skipped X)` to the filename. I'll handle it in the edit.

### Opener (paste once, before the first prompt)
```
Every image from here on follows these rules.
WORLD: grounded editorial illustration of the real world: confident ink line with matte gouache colour, like a hand-painted graphic novel. Everything is era-accurate to North America from the 1860s to 1907: small railway towns and farms in Ontario, Canada (wooden houses, rail lines, grain sheds, snow and maples); Cleveland, Ohio (Public Square, horse trams then electric streetcars, smoke from the lake-front mills, and Euclid Avenue's "Millionaires' Row" of stone mansions behind lawns and elms); Toledo and Columbus, Ohio (the stone Ohio Penitentiary); the small college town of Oberlin, Ohio; and New York's Fifth Avenue around 1902 (grand mansions, iron fences, grand hotels). Real architecture, period vehicles (horse carriages and broughams, hansom cabs, streetcars, steam trains), period interiors (gaslight and early electric lamps, velvet and lace, heavy oak bank counters with brass grilles, safes and vaults, rolltop desks, candlestick telephones, oil lamps). Clothes of the 1870s–1900s: bustles and then high lace collars, leg-of-mutton sleeves, huge feathered hats, furs and muffs for women; frock coats, waistcoats, watch chains, bowlers and top hats for men. Believable materials and everyday wear: scuffed floors, worn velvet, coal smoke, slush on the streets. Natural, unglamorous light. Muted real-world colour: Cleveland sandstone and soot grey, deep plum, bottle green, banker's black, old gold, with the warm cream of paper as a recurring note. The setting tells the story: it is always clear where and when we are.
PEOPLE: every person is the same stylised figure, matching the attached character sheets: an egg-shaped head, wider at the bottom, no chin, plain warm cream skin with soft shading on one side; two small solid dark oval eyes set wide apart; one thin line for the mouth (expressions come from the mouth line, head tilt and body pose); the two eyes and the mouth line are always clearly visible, never covered by hair, hats, veils, beards, glasses or hands (they are animated); no nose, no ears, no eyebrows. Hair, hats, beards, moustaches and glasses sit on the egg head as simple shapes; beards stay below the mouth line. Simple rounded hands. Every person has exactly two arms and two hands. People differ by hair, hats, clothes, build, height and accessories, never by face. They are painted with the same gouache and the same light as the world, standing in it with proper shadows and contact, never pasted on.
NEVER: blood, wounds, guns or any weapon, anyone dead or dying, eagles, seals, coats of arms, flags with stars or emblems, bank or company names and logos, portraits on banknotes, readable text or letters anywhere (signs, notes, cards, letters, receipts, ledgers, telegrams, newspapers, brass plates stay blank or illegible), shiny or glossy rendering, glow, bloom, lens flare, HDR, neon, orange-and-teal movie grading, god rays, airbrushing, 3D-render or plastic look, realistic human faces, flat vector style, anime, watermarks, borders.
FOR ANIMATION: everything in sharp focus (no depth-of-field blur, no motion blur); smoke, steam, fog, snow, rain and candle flames are painted as soft separate shapes that don't cross anyone's face; the main subject inside the central 70% of the frame, nobody cut off by the edges, and some calm areas (sky, wall, floor, ground) left for notes I will draw on later. Landscape format.
When I say EDIT: change only what I ask; keep the same camera, framing, light and every object in place.
```

### Face prompt (for every FACE row)
```
EDIT: the same moment, with the camera pushed in close on [NAME]: head and shoulders fill the middle of the frame, the same light, the same background now further behind. Expression: [EXPRESSION]. The two eyes and the mouth line are clearly visible. Keep the hair, hat and clothes exactly as on the attached character sheet. If a hand is visible, it is one of exactly two.
```

## Character blocks (I rewrite them to match the sheets once they exist)

Her look as Mrs Chadwick comes from the 1904 portrait (`chadwick_1904.jpg`). Attach it to the CASSIE sheets with:
*"Use the attached photo only for her hair, build and clothes; the face stays the egg face."*

- **BETSY** (1867–1879, age 10–21): `BETSY: Elizabeth "Betsy" Bigley, a thin, quiet Ontario farm girl, slightly round-shouldered, dark-brown hair parted in the middle and pulled back into a plain bun (a single plait as a child), a faded blue-grey calico dress with a small white collar fastened with a little cameo brooch, a brown wool shawl, scuffed boots; when she dresses up (1879) a borrowed dark-green jacket and a small hat with one feather.`
- **LYDIA** (1880–1893, age 23–35): `LYDIA: the same woman as a Cleveland clairvoyant in her late twenties, fuller in the figure, dark-brown hair piled high and curled at the front, a deep plum velvet dress with a bustle and a high neck, a black lace shawl, long jet earrings, the cameo brooch at her throat, several rings; as "Mrs Hoover" the same woman in black mourning silk.`
- **CASSIE** (1897–1904, age 40–47): `CASSIE: Mrs Cassie Chadwick, a stout, upright, imposing woman in her forties, dark-brown curly hair piled high on top with a curled fringe, a high upright collar to the chin with the cameo brooch and a long string of pearls, a dark plum-and-black silk gown with big puffed leg-of-mutton sleeves and a bodice trimmed with black braid and beads, a narrow waist, a huge black hat with ostrich feathers outdoors, a dark fur stole and a round fur muff she keeps her hands (and papers) in; diamond rings on both hands; moves slowly and grandly.` (ref: chadwick_1904.jpg)
- **CASSIE 1905** (1904–1907, age 47–50): `CASSIE 1905: the same woman, heavier and greyer at the temples, the pompadour flatter, a plain black silk dress with the lace collar and the cameo brooch, a small black hat with a short veil lifted up off the face (eyes and mouth always visible), no jewellery but one ring; tired and still proud.` (ref: chadwick_1904.jpg)
- **LEROY** (Dr Leroy S. Chadwick): `LEROY: a gentle, slightly stooped Cleveland physician in his fifties, a widower, thinning grey hair, neat grey side-whiskers on the jaw below the mouth line, small round wire spectacles (eyes visible through them), a black frock coat, a grey waistcoat with a watch chain, a black doctor's bag; a silk top hat outdoors.`
- **DILLON** (the Cleveland lawyer): `DILLON: a well-groomed Cleveland lawyer in his early forties, medium build, short dark hair parted in the middle, a thick dark moustache (above the mouth line, not covering it), a grey morning suit, pale grey gloves, a dark bowler hat, a silver-topped cane; eager, a little vain.`
- **REYNOLDS** (Iri Reynolds, Wade Park Bank): `REYNOLDS: an elderly Cleveland bank officer in his sixties, thin and upright, white hair combed straight back, a short white chin beard below the mouth line, gold-rimmed spectacles (eyes visible), a black frock coat, a high white collar and a black string tie, black sleeve protectors at his desk; trusted, careful, proud.`
- **BECKWITH** (Charles T. Beckwith, Oberlin bank president): `BECKWITH: an elderly small-town bank president in his late sixties, portly and kindly, a full white beard on the jaw and chin below the mouth line, bald on top with white hair at the sides, a black frock coat, a grey waistcoat and gold watch chain.`
- **CARNEGIE** (Andrew Carnegie, c.1902–1905): `CARNEGIE: the Scottish-born steel millionaire in his late sixties, a very short, compact man (a head shorter than the others), white hair, a full, rounded, neatly trimmed white beard on the jaw and chin below the mouth line (the mouth line clearly visible above it), a black frock coat and waistcoat, a wing collar and a black bow tie, a silk top hat outdoors; brisk and amused.` (ref: carnegie_1905.jpg)
- **No sheet, written into the prompts:** `SPEAR: a thin middle-aged bank cashier with a brown moustache, black sleeve protectors, a green eyeshade (eyes visible below it).` `NEWTON: Herbert Newton, a lean Massachusetts banker in his fifties in a grey suit, clean-shaven, grey hair.` `ALICE: Betsy's older sister, a plain Cleveland housewife in an apron.` `SPRINGSTEEN: Dr Wallace Springsteen, a stern older doctor with a grey beard below the mouth line and a Civil War veteran's dark blue coat.` `HOUSEKEEPER: a Scottish housekeeper in her fifties in a black dress, a white apron and cap.` `BANKERS: Ohio bankers of 1900 in black frock coats and wing collars, beards and moustaches.` `SOCIETY LADIES: Euclid Avenue society women of 1900 in pale gowns and big hats.` `REPORTERS: 1904 newspapermen in bowlers and overcoats with notebooks; a photographer with a box camera on a tripod.` `POLICE: 1904 American policemen and detectives in dark coats and helmets or bowlers, nothing in their hands.` `TOWNSPEOPLE: Oberlin townspeople of 1904: farmers, shopkeepers, college students in caps, women in shawls.`

---

## Step 0 · Style card (Style A only) · 1 image
(For a first film there is nothing to attach: the opener describes the style. Later films attach this card.)
```
Make a style card in exactly the attached style (the same ink line, the same matte gouache, the same light), for a new film: Cleveland, Ohio, a grey winter afternoon in 1903, Euclid Avenue's "Millionaires' Row": a wide snowy avenue lined with bare elms and big sandstone mansions behind iron fences. A black horse-drawn carriage has stopped at the kerb; a stout, imposing egg-headed woman with dark hair in a high pompadour, a high lace collar, a huge black feathered hat, a fur stole and a round fur muff steps down from it, helped by a coachman; a footman carries a stack of gift boxes up the steps of her house. On the porch across the street two society ladies in pale gowns turn away. Coal smoke over the rooftops. One single picture, no panels, no captions.
```
Save as `00_style/style_card.png`. **No B version**: Style A. If it drifts:
*"Closer to the attached cards: thinner confident ink line, flatter matte gouache, softer daylight."*

## Step 1 · Cast sheets · 9 images
```
A character sheet on a plain light-grey background, same style as the attached card: [CHARACTER BLOCK]. Show: full body front, three-quarter and side views, a back view, and a row of four head close-ups (neutral, sly, worried, shocked). The two eyes and the mouth line clear in every head. Exactly two arms and two hands in every view. Even studio light, no scenery, no text.
```
Save as `01_cast/betsy.png`, `lydia.png`, `cassie.png`, `cassie_1905.png`, `leroy.png`, `dillon.png`, `reynolds.png`,
`beckwith.png`, `carnegie.png`. Attach `betsy.png` to the LYDIA sheet, and `lydia.png` to both CASSIE sheets, so she
stays one woman. For `betsy.png` add: *"Also one small extra figure in the corner: the same girl at 10 with a single
plait, in a smaller version of the same dress."* For `carnegie.png` add: *"He is very short: show a plain standing
man of average height beside him in grey outline for scale."*

---

## Step 2 · Scenes (all saved in `02_scenes/`; attach the style card and the cast sheet of everyone in the image)

### Group 1 (the hook: the note on the pavement, New York c.1902) · 9 images · *S01a–S01f play as a comic page*
Keep each subject in the **centre third** of S01a–S01f so I can crop tall and wide panels from them.
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 11 | `S01a_fifth_ave.png` | W | New York, Fifth Avenue, a bright cold morning c.1902: a grand new red-brick and stone mansion behind an iron fence and a garden; a black closed carriage waits at the kerb, coachman on the box, horse's breath steaming; a few carriages further up the avenue. *(ref: carnegie_mansion_1902.jpg)* |
| 12 | `S01b_dillon_waits.png` | M | Inside the waiting carriage: DILLON [block] sits on the leather seat, checking his pocket watch, glancing at the mansion through the window. |
| 13 | `S01c_doorway.png` | P | Dillon's view through the carriage window: at the top of the mansion's steps, CASSIE [block] stands in the open doorway, turning to wave back into the house; a figure in the dim hall behind. |
| 14 | `S01d_trip.png` | M | CASSIE [block] stepping up into the carriage, one foot on the step, a folded paper slipping from her fur muff and falling; the coachman holding the door. |
| 15 | `S01e_paper_falls.png` | D | Close at pavement level: a long folded paper lying on the stone pavement beside the carriage wheel, the hem of a dark silk gown just above it. |
| 16 | `S01f_reads.png` | D | DILLON's gloved hands holding the unfolded paper: a long promissory note with an ornate engraved border, a blank cartouche, rows of fine illegible handwriting, and a bold illegible signature at the foot. The paper fills most of the frame. |
| 17 | `S01g_dillon_face.png` | F | FACE of S01b, DILLON, holding the paper: astonished, mouth a small open "o", head pulled back. |
| 18 | `S01h_cassie_face.png` | F | EDIT: inside the carriage, CASSIE [block] sitting opposite, eyes lowered, a tiny secret smile at one corner of the mouth line, hands back in the muff. |
| 19 | `S01i_drive_off.png` | W | The carriage pulling away down Fifth Avenue between mansions and bare trees, seen from behind, other carriages and a hansom cab passing. |

### Group 2 (Ontario, 1857–1879) · 11 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 20 | `S02a_town.png` | W | A small Ontario railway town in the 1860s, late winter: a single-track railway line, a wooden station and water tower, a grain shed, a scatter of clapboard houses, snow and bare maples, smoke from chimneys. |
| 21 | `S02b_father.png` | M | A section gang of railway workers in caps and wool coats levering a rail with long bars; one of them is her father (a lean bearded man, beard below the mouth line); little BETSY, aged 10 [block], watches from a fence. *(attach betsy)* |
| 22 | `S02c_kitchen.png` | M | A crowded farmhouse kitchen at supper: a big family round a table, an oil lamp, a mother at the stove; BETSY [block] (10) sits apart on a stool by the window, silent, staring at nothing. |
| 23 | `S02d_betsy_face.png` | F | FACE of S02c, BETSY: far away, mouth a straight line, head tilted slightly, as if not hearing. |
| 24 | `S02e_letter.png` | M | Night, the same kitchen, everyone asleep: BETSY [block] (13) at the table by an oil lamp, copying the handwriting of an old letter onto a fresh sheet with a steel pen, tongue-tip concentration. |
| 25 | `S02f_letter_d.png` | D | Close on her hands: the old letter and her copy side by side, the same flowing illegible handwriting, a pen and an ink bottle. |
| 26 | `S02g_woodstock.png` | W | Woodstock, Ontario, 1879: a brick main street with shops and awnings, horse sleighs, a bank on the corner, a stone county courthouse at the end of the street. |
| 27 | `S02h_card.png` | D | A gloved hand offering a small calling card with a fancy printed border and one line of illegible copperplate, across a shop counter. |
| 28 | `S02i_courtroom.png` | M | A small 1879 Ontario courtroom: BETSY [block] (21) in the dock, pulling a strange crooked face at the jury; twelve bearded jurors lean back startled; a judge in a black robe frowns. |
| 29 | `S02j_face_pull.png` | F | FACE of S02i, BETSY: mouth twisted into a wobbly crooked line, head cocked oddly, eyes wide and blank. |
| 30 | `S02k_train.png` | M | A steam train at the little station, BETSY [block] at a carriage window with a carpetbag on her lap, looking out; snow; her father on the platform, hat in hand. |

### Group 3 (Cleveland, the 1880s) · 11 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 31 | `S03a_cleveland.png` | W | Cleveland, Ohio, early 1880s: Public Square with its trees and monument, horse-drawn streetcars, brick and stone blocks, mill smoke drifting over from the lake front. |
| 32 | `S03b_furniture.png` | M | A modest Cleveland parlour: two men carry a sofa and a clock out of the front door; ALICE [block] in her apron protests, hands up; through the window a cart piled with her furniture. |
| 33 | `S03c_alice_face.png` | F | FACE of S03b, ALICE: shocked and angry, mouth wide open, shoulders up. |
| 34 | `S03d_garden_st.png` | W | A brick terraced house in Cleveland at dusk, a gas lamp; a blank brass plate beside the door; a woman in a widow's veil (lifted) hesitates on the step. |
| 35 | `S03e_seance.png` | M | A heavily draped parlour lit by two candles: LYDIA [block] at a round table with a crystal ball on a velvet cloth, her hands spread over it; an anxious widow client opposite. *(attach lydia)* |
| 36 | `S03f_crystal.png` | D | Close on LYDIA's ringed hands hovering over the crystal ball; beside it, a small pile of silver dollars the client has laid down. |
| 37 | `S03g_wedding.png` | M | November 1882, a small Cleveland church: LYDIA [block] in a dove-grey dress marries SPRINGSTEEN [block]; a minister, two witnesses, pale autumn light. |
| 38 | `S03h_paper.png` | D | A breakfast table: a folded morning newspaper with columns of tiny illegible text and an engraved portrait of an egg-headed woman with piled dark hair; a cup of coffee overturned beside it. |
| 39 | `S03i_thrown_out.png` | M | The front steps of a doctor's house: SPRINGSTEEN [block] in the doorway pointing outward; three creditors in bowlers on the steps waving bills; LYDIA [block] going down with a hatbox. |
| 40 | `S03j_lydia_face.png` | F | FACE of S03i, LYDIA: unbothered, mouth a small neat flat line, chin raised. |
| 41 | `S03k_hats.png` | M | A rented room: LYDIA [block] packs a trunk; laid out on the bed, a row of very different hats and a widow's veil, as if for different women. |

### Group 4 (the names, and prison, 1883–1893) · 9 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 42 | `S04a_farm.png` | M | An Ohio farmhouse kitchen in the 1880s: LYDIA [block] beside a big shy farmer in braces, who signs a paper at the table; she watches the pen. |
| 43 | `S04b_hoover.png` | M | A Cleveland bedroom: LYDIA [block] as Mrs Hoover in black mourning silk, rocking a cradle with a baby boy; a man's portrait on the wall with a black ribbon. |
| 44 | `S04c_toledo_shop.png` | M | Toledo, 1889: a fine shop counter with silks and silverware; LYDIA [block] signs a paper with a flourish while the bowing shopkeeper wraps parcels. |
| 45 | `S04d_toledo_court.png` | M | A Toledo courtroom 1889: LYDIA [block] standing before a judge with a white moustache; a lawyer beside her; spectators. |
| 46 | `S04e_pen.png` | W | The Ohio Penitentiary in Columbus, 1889: a long, high grey stone wall with watchtowers at the corners, behind it a huge castellated cell block with chimneys smoking; a gate; a prison wagon drawn by two horses at the gate. *(ref: ohio_pen.jpg)* |
| 47 | `S04f_sewing.png` | M | The women's sewing room of the penitentiary: rows of women prisoners in striped dresses at treadle sewing machines; LYDIA [block], in stripes, sews neatly; a matron watches. |
| 48 | `S04g_sew_face.png` | F | FACE of S04f, LYDIA: patient and calculating, eyes raised from the work, mouth a straight line. |
| 49 | `S04h_parole.png` | D | A governor's desk in 1893: a parole paper with an illegible signature, a pen, an inkwell, a pair of spectacles. |
| 50 | `S04i_gate.png` | W | Autumn 1893: LYDIA [block] in a plain dark coat walks out of the penitentiary gate with a carpetbag, leaves blowing, the long wall and a watchtower behind her. *(ref: ohio_pen.jpg)* |

### Group 5 (Dr Chadwick, 1893–1897) · 9 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 51 | `S05a_westside.png` | W | Cleveland's west side at night, 1890s: a large wooden house with lamplit curtained windows, a carriage at the gate, a gas lamp, wet street. |
| 52 | `S05b_parlour.png` | M | The front parlour of that house: several young women in day dresses on sofas, LYDIA [block] (as Mrs Hoover, in plum velvet) presiding by the piano; at the door LEROY [block] with his doctor's bag, looking around in mild confusion. *(attach lydia, leroy)* |
| 53 | `S05c_leroy_face.png` | F | FACE of S05b, LEROY: dawning understanding, mouth a small "o", head drawn back. |
| 54 | `S05d_faint.png` | M | LYDIA [block] swooning dramatically into an armchair, the back of one hand to her forehead; LEROY [block] rushing to catch her arm; the young women stare. |
| 55 | `S05e_explains.png` | M | Later, the parlour quiet: LYDIA [block] sitting up, one hand on her heart, explaining earnestly; LEROY [block] listening kindly, hat in his hands. |
| 56 | `S05f_wedding.png` | M | 1897, a quiet wedding in a Cleveland parlour: CASSIE [block] in grey silk and LEROY [block] before a minister; a single bouquet; a small boy in a sailor suit (her son) at her side. *(attach cassie, leroy)* |
| 57 | `S05g_euclid.png` | W | Euclid Avenue, Cleveland, c.1898, "Millionaires' Row": a wide avenue under tall elms, great stone mansions set back behind lawns and iron fences, carriages, a streetcar. *(ref: chadwick_house.jpg)* |
| 58 | `S05h_arrives.png` | M | A carriage at the Chadwick house on Euclid Avenue (a big square three-storey Italianate brick house with a flat roof, arched windows, a deep columned front porch and a side bay): LEROY [block] helps CASSIE [block] down; a maid and a butler wait on the steps. *(ref: chadwick_house.jpg)* |
| 59 | `S05i_neighbours.png` | P | Cassie's view across the avenue: two SOCIETY LADIES [block] on a neighbouring porch turn their backs and go inside. |

### Group 6 (snubbed on the Row) · 5 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 60 | `S06a_tea.png` | M | CASSIE's [block] grand parlour set for a ladies' tea: silver urn, cakes on stands, twelve gilt chairs — all empty; CASSIE alone on a sofa; a tall clock. |
| 61 | `S06b_hurt_face.png` | F | FACE of S06a, CASSIE: hurt, mouth turning down at the corners, head held very straight. |
| 62 | `S06c_cards.png` | D | A silver tray on a hall table, piled with unopened envelopes and returned calling cards, all blank. |
| 63 | `S06d_window.png` | M | Inside a neighbour's mansion: two SOCIETY LADIES [block] part the lace curtains to peer across the avenue at the Chadwick house, smirking. |
| 64 | `S06e_dusk.png` | W | The Chadwick house at dusk in snow, every window lit, no carriages at the gate, the avenue empty. |

### Group 7 (New York, c.1902: the lie, from inside) · 12 images · *S07b–S07g play as a comic page*
Keep each subject in the **centre third** of S07b–S07g.
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 65 | `S07a_holland.png` | W | New York, c.1902: the entrance of a grand Fifth Avenue hotel of brownstone and granite, doormen, carriages and hansom cabs, ladies in big hats. |
| 66 | `S07b_lobby.png` | M | The hotel's marble and mahogany lobby: CASSIE [block] "bumps into" DILLON [block] by a palm; both seem surprised, she with a gloved hand at her lace collar, he lifting his bowler. |
| 67 | `S07c_favour.png` | M | The same lobby, a moment later: CASSIE [block] leans in confidingly, asking a favour; DILLON [block] bows, delighted. |
| 68 | `S07d_ride.png` | M | Inside a carriage riding up Fifth Avenue: CASSIE [block] calm, looking out; DILLON [block] beside her, curious. Mansions passing in the window. |
| 69 | `S07e_mansion.png` | W | The grand Fifth Avenue mansion from S01a seen from the carriage door: CASSIE [block] climbing the steps alone; DILLON's bowler at the carriage window. *(ref: carnegie_mansion_1902.jpg)* |
| 70 | `S07f_hall.png` | M | Inside the mansion: a grand panelled entrance hall with a staircase; a HOUSEKEEPER [block] listens politely as CASSIE [block] shows her a letter of reference and asks about a maid. |
| 71 | `S07g_housekeeper_face.png` | F | FACE of S07f, the HOUSEKEEPER: polite and puzzled, mouth a small flat line, head tilted. |
| 72 | `S07h_muff.png` | D | Close, low in the hall: CASSIE's gloved hand slipping a long folded paper out of her fur muff, hidden behind her skirt. |
| 73 | `S07i_wave.png` | M | From inside the hall looking out through the open front door: CASSIE [block] on the top step turning to wave back to the HOUSEKEEPER; the carriage at the kerb beyond. |
| 74 | `S07j_secret.png` | M | Inside the carriage: CASSIE [block] with a finger near her lips (not covering the mouth line), confiding; DILLON [block] holding the unfolded note, leaning close. |
| 75 | `S07k_cassie_tears.png` | F | FACE of S07j, CASSIE: tearful and confiding, mouth trembling slightly, head bowed. |
| 76 | `S07l_dillon_oath.png` | F | FACE of S07j, DILLON: solemn, one hand on his heart, mouth a firm line: sworn to secrecy. |

### Group 8 (the sealed envelope, Cleveland) · 10 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 77 | `S08a_bank.png` | W | Cleveland c.1902: a solid stone corner bank building with tall arched windows and a blank stone panel over the door, an electric streetcar passing, snow at the kerb. |
| 78 | `S08b_office.png` | M | A bank officer's panelled office: DILLON [block] introduces CASSIE [block] to REYNOLDS [block]; she hands over a large brown envelope; he takes it with both hands. *(attach dillon, cassie, reynolds)* |
| 79 | `S08c_seal.png` | D | REYNOLDS's hands tying string round the brown envelope and pressing a red wax seal onto it at a desk; a stick of sealing wax, a candle. |
| 80 | `S08d_receipt.png` | D | REYNOLDS's hand writing on a bank receipt form with a steel pen; illegible handwriting, an illegible signature. |
| 81 | `S08e_vault.png` | M | A bank vault with a great round steel door open: REYNOLDS [block] slides the sealed envelope into a small deposit box among rows of boxes. |
| 82 | `S08f_reynolds_face.png` | F | FACE of S08e, REYNOLDS: proud and trustworthy, mouth a small satisfied line, chin up. |
| 83 | `S08g_club.png` | M | A gentlemen's club smoking room, leather armchairs: DILLON [block] whispers behind his hand to two BANKERS [block], who lean in, wide-eyed. |
| 84 | `S08h_boardroom.png` | M | A bank boardroom with a long table: five BANKERS [block] whispering in pairs, heads together. |
| 85 | `S08i_desk.png` | D | A banker's desk: CASSIE's gloved hand slides the receipt across; the banker's hand slides back a thick bundle of plain engraved banknotes. |
| 86 | `S08j_banker_face.png` | F | FACE of a BANKER from S08i: greedy delight, mouth a wide smile. |

### Group 9 (Queen of Ohio, 1902–1904) · 14 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 87 | `S09a_oberlin.png` | W | Oberlin, Ohio, c.1903: a small college town around a green square of elms, red-brick shops, a modest stone bank on the corner, students in caps, a horse and buggy. |
| 88 | `S09b_beckwith_office.png` | M | A small-town bank president's office: BECKWITH [block] and SPEAR [block] lean over a desk as CASSIE [block] shows them the receipt; a safe, a rolltop desk. *(attach beckwith, cassie)* |
| 89 | `S09c_beckwith_face.png` | F | FACE of S09b, BECKWITH: dazzled, mouth an open smile, head tilted toward her. |
| 90 | `S09d_counting.png` | D | SPEAR's hands counting bundles of plain engraved banknotes into a black leather bag on the counter behind a brass grille. |
| 91 | `S09e_own_money.png` | M | BECKWITH [block], alone at his desk at night, writes out a cheque from his own personal cheque book; a photograph of his wife on the desk. |
| 92 | `S09f_jeweller.png` | M | A Cleveland jeweller's: CASSIE [block] tries on a heavy diamond necklace before a mirror; the jeweller and his assistant bow, trays of rings on the counter. |
| 93 | `S09g_dressmaker.png` | M | A dressmaker's salon: CASSIE [block] stands on a low box being measured; bolts of silk and velvet everywhere; three seamstresses with pins. |
| 94 | `S09h_closets.png` | D | A long dressing room in the Euclid house: a row of open wardrobe closets, each full of gowns, hat boxes stacked to the ceiling. |
| 95 | `S09i_organ.png` | M | The parlour: a gilded pipe organ with gold pipes against the wall; CASSIE [block] plays it, a few guests in evening dress listen. |
| 96 | `S09j_dinner.png` | W | A grand dinner party in the Euclid house: a long table under a chandelier, twenty guests in evening dress, footmen with silver dishes; CASSIE [block] at the head. |
| 97 | `S09k_gift.png` | D | One place setting at the dinner: on the plate, a small open velvet box with a gold watch in it, a folded napkin. |
| 98 | `S09l_christmas.png` | M | Christmas: CASSIE [block] beside a tall tree handing wrapped presents to a line of children and mothers at her door. |
| 99 | `S09m_queen_face.png` | F | FACE of S09j, CASSIE: radiant, mouth a broad proud smile, head high. |
| 100 | `S09n_night.png` | W | The Euclid Avenue house at night, every window blazing, carriages queuing at the gate, snow. |

### Group 10 (November–December 1904: it falls) · 15 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 101 | `S10a_brookline.png` | W | Brookline, Massachusetts, autumn 1904: a leafy street of brick and clapboard houses, a small brick bank, yellow leaves. |
| 102 | `S10b_newton.png` | M | NEWTON [block] at his desk reading a letter, frowning; a pile of letters and a ledger. |
| 103 | `S10c_court_clerk.png` | M | A Cleveland courthouse clerk's office: a lawyer in a bowler hands a thick bundle of papers across the counter to a clerk. |
| 104 | `S10d_telegram.png` | D | A silver tray on Cassie's hall table holding a single telegram envelope; a maid's hand. |
| 105 | `S10e_reporters.png` | M | Outside the Euclid Avenue gate: a crowd of REPORTERS [block] with notebooks, a photographer with a box camera on a tripod, a policeman at the gate. |
| 106 | `S10f_carnegie_office.png` | M | New York, a book-lined office: CARNEGIE [block] dictating to a secretary at a typewriter, shaking his head, one hand raised. *(attach carnegie; ref: carnegie_1905.jpg)* |
| 107 | `S10g_carnegie_face.png` | F | FACE of S10f, CARNEGIE: mild amused disbelief, mouth a small crooked half-smile, head tilted. |
| 108 | `S10h_run.png` | W | Oberlin in December snow: a crowd of TOWNSPEOPLE [block] pressing at the closed doors of the little stone bank, waving bank books, a policeman on the steps. |
| 109 | `S10i_empty.png` | M | Inside the Oberlin bank: SPEAR [block] behind the brass grille with empty drawers pulled out; BECKWITH [block] grey-faced in the background, sitting heavily. |
| 110 | `S10j_beckwith_face.png` | F | FACE of S10i, BECKWITH: devastated, mouth sagging, head bowed. |
| 111 | `S10k_opened.png` | M | The Wade Park bank office: REYNOLDS [block] and two plain-clothes inspectors stand over the desk as the brown envelope is cut open; papers slide out. |
| 112 | `S10l_forgeries.png` | D | The papers from the envelope spread on the desk: crude notes with clumsy ornate borders and a wobbly illegible signature, the broken red wax seal beside them. |
| 113 | `S10m_breslin.png` | W | New York, a December night 1904: a tall new hotel on Broadway with lit windows; a police carriage at the kerb; snow falling. |
| 114 | `S10n_arrest.png` | M | A hotel bedroom: CASSIE 1905 [block] sitting up in bed, the covers to her chest, a thick money belt on the coverlet; two POLICE detectives and a doctor at the door, hats off. *(attach cassie_1905)* |
| 115 | `S10o_defiant_face.png` | F | FACE of S10n, CASSIE 1905: defiant, mouth a hard straight line, chin up. |

### Group 11 (the trial, March 1905) · 10 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 116 | `S11a_courthouse.png` | W | Cleveland, March 1905: the stone federal building, a crowd in the slushy street, umbrellas, a streetcar. |
| 117 | `S11b_courtroom.png` | W | A packed federal courtroom: ladies in big hats in the gallery, REPORTERS sketching, a judge at the high bench, the jury box. |
| 118 | `S11c_defence.png` | M | CASSIE 1905 [block] at the defence table in black, veil lifted, her lawyer beside her leaning in to whisper. |
| 119 | `S11d_prosecutor.png` | M | The prosecutor, a tall man with a moustache, turns to the jury holding up one of the notes, other hand open. |
| 120 | `S11e_carnegie.png` | M | In the gallery among the spectators: CARNEGIE [block], very small, top hat on his knee, watching with interest. *(attach carnegie)* |
| 121 | `S11f_note_pov.png` | P | Carnegie's view from the gallery: the forged note held up in the prosecutor's hand, the judge beyond. |
| 122 | `S11g_verdict.png` | M | The jury foreman stands to give the verdict; the jurors behind him; the court silent. |
| 123 | `S11h_verdict_face.png` | F | FACE of S11c, CASSIE 1905: she sinks, mouth trembling into a wobbly line, head dropping. |
| 124 | `S11i_beckwith_home.png` | M | BECKWITH [block] at home in an armchair by a cold fireplace, a blanket over his knees, very old now; a window with snow. |
| 125 | `S11j_spear.png` | M | SPEAR [block] in an overcoat walking down courthouse steps between two marshals (nothing in their hands). |

### Group 12 (the end) · 10 images
| # | Save as | Shot | Prompt |
|---|---|---|---|
| 126 | `S12a_trunks.png` | W | January 1906, the Ohio Penitentiary gate: a delivery wagon piled with leather trunks, a rolled rug and a velvet armchair; guards staring. *(ref: ohio_pen.jpg)* |
| 127 | `S12b_cell.png` | M | A prison cell made strange: a Turkish rug on the stone floor, a lamp with a silk shade, a velvet armchair, open trunks of gowns; CASSIE 1905 [block] sits upright in the chair. |
| 128 | `S12c_hospital.png` | M | 1907, the prison hospital: CASSIE 1905 [block] in a white iron bed, staring straight ahead unseeing; a nurse in white beside her. |
| 129 | `S12d_rings.png` | D | The bedside table: a china dish holding her last ring and the cameo brooch, a glass of water. |
| 130 | `S12e_woodstock.png` | W | Woodstock, Ontario, October 1907: a small cemetery among red and gold maples, a handful of mourners round a plain coffin, a church spire. |
| 131 | `S12f_tourists.png` | W | Euclid Avenue, 1908: a sightseeing horse-drawn wagon of tourists in boaters and hats stopped outside the Chadwick house, people pointing. *(ref: chadwick_house.jpg)* |
| 132 | `S12g_oberlin_build.png` | W | Oberlin, a few years later: a new stone building going up on the college green, workmen on scaffolding, students passing. |
| 133 | `S12h_carnegie_reads.png` | M | CARNEGIE [block] in his library in an armchair reading a newspaper (blank columns), a small private smile. |
| 134 | `S12i_pavement.png` | D | The same Fifth Avenue pavement as S01e, empty now: only a single blank folded paper by the kerb and a few autumn leaves. |
| 135 | `S12j_mansion_today.png` | W | The same Fifth Avenue mansion as S01a, quiet, no carriage, early evening, lamps lit. |

### Scenes that draw themselves · 4 images
```
EDIT: the exact same picture as an illustrator's pen-and-ink drawing: remove all colour and painted shading, keep only black ink outlines and ink hatching on pure white paper. Same composition, nothing moved.
```
| # | Save as |
|---|---|
| 136 | `02_scenes/S01a_fifth_ave_lines.png` |
| 137 | `02_scenes/S05g_euclid_lines.png` |
| 138 | `02_scenes/S09j_dinner_lines.png` |
| 139 | `02_scenes/S11b_courtroom_lines.png` |

---

## Step 3 · Sketch sheets · 18 images
Attach the style card and the cast sheets of anyone shown; after the first sheet, also attach `03_sheets/X01_ontario.png`.
Start every sheet prompt with:
```
A page from an illustrator's sketchbook: four separate drawings in confident pen-and-ink with fine hatching and a watercolour wash, on pure white paper, arranged left to right with clear white space between them (I will link them later). Neat, accurate drawings of real places and objects, not icons and not cartoons; the people are the egg-headed figures from the attached sheets, drawn in ink. No text, letters, numbers, arrows, frames, boxes, flags, logos, emblems or insignia. Landscape.
```
| # | Save as | The four drawings |
|---|---|---|
| 140 | `03_sheets/X01_ontario.png` | 1) a clapboard Ontario farmhouse with a maple; 2) a railway handcar on a track; 3) an oil lamp beside a pen and ink bottle; 4) the girl BETSY with her plait. *(attach betsy)* |
| 141 | `03_sheets/X02_forger.png` | 1) a steel pen nib and an open ink bottle; 2) two letters side by side in the same handwriting (illegible); 3) a small calling card with a fancy border; 4) a folded promissory note tied with ribbon. |
| 142 | `03_sheets/X03_names.png` | 1) a crystal ball on a velvet cloth; 2) a widow's veiled hat; 3) a gold wedding ring; 4) a travelling trunk spilling different hats. |
| 143 | `03_sheets/X04_prison.png` | 1) the long wall and corner watchtower of the Ohio Penitentiary; 2) a treadle sewing machine; 3) a ring of big iron keys; 4) a carpetbag. *(ref: ohio_pen.jpg)* |
| 144 | `03_sheets/X05_carnegie.png` | 1) CARNEGIE standing, small, in his top hat; 2) a Bessemer steel converter pouring sparks; 3) a classical public library building; 4) the Fifth Avenue mansion front. *(attach carnegie)* |
| 145 | `03_sheets/X06_envelope.png` | 1) a large brown envelope tied with string and a wax seal; 2) a round bank vault door; 3) a small deposit box; 4) a thick bundle of plain engraved banknotes. |
| 146 | `03_sheets/X07_queen.png` | 1) a diamond necklace; 2) the gilded pipe organ; 3) a gown on a dressmaker's form; 4) a closed carriage with two horses. |
| 147 | `03_sheets/X08_fall.png` | 1) a telegram envelope; 2) a small stone bank with a crowd at its doors; 3) a money belt; 4) a reporter's box camera on a tripod. |
| 148 | `03_sheets/X09_end.png` | 1) a judge's gavel on its block; 2) a leather trunk; 3) a plain gravestone under a maple; 4) CASSIE 1905 seated very upright in her velvet chair. *(attach cassie_1905)* |

**Line versions** (one EDIT per sheet, right after each), saved as `03_sheets/X0n_<name>_lines.png`, images 149–157:
```
EDIT: the exact same page and drawings, with all colour and all painted shading removed: only the black ink lines and ink hatching remain, on pure white paper. Same drawings, same positions and sizes, nothing redrawn or moved.
```

---

## Step 4 · Bases · 7 images
Real objects from the story that I draw on live. **Keep them empty**: no map shapes, no marks, no writing.
(B09, the cream board for the comic pages, and B10, the tea-stained footnote note, are already made: `assets/footnote/`.)

| # | Save as | Prompt |
|---|---|---|
| 158 | `04_bases/B01_note.png` | Seen straight down: one long 1900s promissory note on dark wood, cream paper with an ornate engraved border and an empty cartouche at the top, completely blank inside, a few faint ruled lines, folded creases. It fills most of the frame. |
| 159 | `04_bases/B02_card.png` | Seen straight down: one large Victorian calling card on green baize, thick cream card with a thin fancy border, completely blank. |
| 160 | `04_bases/B03_map.png` | A 1900s cloth wall map of the Great Lakes region (Ontario, Ohio, New York) hanging on a wall, lakes and land as soft pale colour areas but **no coastline drawn, no borders, no names**: aged blank cloth in pale blue and cream. |
| 161 | `04_bases/B04_ledger.png` | Seen straight down: a bank ledger open flat, two cream pages with faint ruled columns and no writing at all, a steel pen at one edge. |
| 162 | `04_bases/B05_envelope.png` | Seen straight down: a large brown manila envelope on a dark desk, the front completely blank, string wound round a button, a red wax seal at one corner. |
| 163 | `04_bases/B06_telegram.png` | Seen straight down: a 1904 telegram form, printed boxes and ruled lines, completely blank, a pencil beside it. |
| 164 | `04_bases/B07_newspaper.png` | Seen straight down: a December 1904 newspaper front page laid flat, columns of tiny illegible text, a large empty white box in the upper half where a headline and an engraved portrait would go. |

---

## What I draw live (no images needed)
| Idea | Drawn as | Used for |
|---|---|---|
| **The note** (B01, S01f) | the note's words type themselves as Dillon reads: *pay to the order of Cassie L. Chadwick… two million dollars… Andrew Carnegie*; later a red FORGED stamp | the hook, the envelope opened |
| **The names** (B02) | the calling card retypes itself: Miss Bigley, Heiress to $15,000 → Madame Lydia DeVere → Marie LaRose → Mrs Hoover → Mrs Cassie L. Chadwick, each crossed out | her aliases |
| **The map** (B03) | Great Lakes coastlines drawn in, then her route inked town by town: Woodstock → Cleveland → Toledo → Columbus → Cleveland → New York → Oberlin → Brookline, dates typed | the life in one line |
| **The ledger** (B04) | loans written in bank by bank, a running total climbing to "about $2,000,000", interest rates beside them | Queen of Ohio |
| **The envelope** (B05) | "not to be opened" typed, then a tally of months it stays shut; a cut line at the end | the sealed envelope |
| **The telegram** (B06) | Carnegie's denial types itself: "has not signed a note in more than thirty years" | the fall |
| **The newspaper** (B07) | her 1904 photo prints in as halftone; the nicknames type one by one: Queen of Swindlers, Duchess of Diamonds, High Priestess of Fraudulent Finance | the arrest |
| **The whisper** | a dotted route from Dillon to banker to banker on X06, branching ("he told one man, who told…") | the secret spreading |
| **Real photos** | period prints slide in when named: her 1904 portrait, Carnegie 1905, the Euclid house, the Carnegie mansion, the penitentiary | those beats |
| **Stamps** | NOT GUILTY (1879), 9½ YEARS, LOAN APPROVED, FORGED, CLOSED, 14 YEARS | the beats |
| **Footnotes** (B10, host hand) | 1 the carriage story is Dillon's word; 2 her calling card; 3 McKinley's parole; 4 "Iri, not Ira"; 5 died on her 50th birthday | |
| **Living stills** | horse breath (S01a), candle flames (S02e, S03e), chimney smoke (S02a, S05a), snow (S06e, S09n, S10h, S10m), mill smoke (S03a), leaves (S04i, S12e, S12i), Bessemer sparks (X05) | those shots |
| **Comic pages** (B09) | the hook (S01a–S01f), the lie from inside (S07b–S07g) | |
| **Insets** | X01's girl with the plait drawn beside CASSIE in S09m ("the railway girl"); X05's small Carnegie beside S11e | |

## Facts to check before the script
- The carriage scene is a later retelling (no first name for Dillon in the solid sources); footnote 1, "according to the lawyer".
- Year and house of the visit: say "around 1902" and "his mansion on Fifth Avenue", no street number.
- Loan totals vary ($633k to $20M): say "millions"; Oberlin's loss varies ($200k–$800k): say "most of its money".
- Carnegie at the trial: several secondary sources, no primary yet — "reportedly"; check the 1905 papers.
- Partly deaf as a child, first forgery at 13: Abbott's *Smithsonian* piece — read it in full before the script.
- Carnegie and the Oberlin building (S12g): word as "a few years later, Carnegie's money paid for a building in Oberlin" only if confirmed; otherwise S12g plays as "Oberlin, rebuilt".

When a group is saved, tell me. I check every image (hands, faces, beards, era details) as they come in. Then we
write the narrator script from the images and build batch 1.
