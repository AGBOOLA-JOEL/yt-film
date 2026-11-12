"""Gridded views of images in ENGINE source px (after the 2:1 crop and scale): python tools/egrid.py out.png NAME ..."""
import sys, cv2, numpy as np
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import film
out, names = sys.argv[1], sys.argv[2:]
tiles = []
for n in names:
    a = cv2.cvtColor(film.up(n), cv2.COLOR_RGB2BGR)[::2, ::2].copy()
    for x in range(0, a.shape[1], 100):
        cv2.line(a, (x, 0), (x, a.shape[0]), (0, 0, 255) if x % 200 == 0 else (0, 0, 160), 1)
        if x % 200 == 0: cv2.putText(a, str(x), (x + 3, 18), 0, 0.55, (0, 255, 255), 2)
    for y in range(0, a.shape[0], 100):
        cv2.line(a, (0, y), (a.shape[1], y), (0, 0, 255) if y % 200 == 0 else (0, 0, 160), 1)
        if y % 200 == 0 and y: cv2.putText(a, str(y), (3, y - 4), 0, 0.55, (0, 255, 255), 2)
    cv2.putText(a, n, (40, a.shape[0] - 15), 0, 1.0, (0, 255, 255), 2)
    tiles.append(a)
import os
cols = int(os.environ.get("COLS", 2)) if len(tiles) > 1 else 1
rows = [np.hstack(tiles[i:i + cols] + [np.zeros_like(tiles[0])] * (cols - len(tiles[i:i + cols]))) for i in range(0, len(tiles), cols)]
g = np.vstack(rows)
cv2.imwrite(out, cv2.resize(g, None, fx=min(1, 2400 / g.shape[1]), fy=min(1, 2400 / g.shape[1])))
