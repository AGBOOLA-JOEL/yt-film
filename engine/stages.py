"""Drawing order for a staged sketch (rough -> lines -> shaded -> wash), without redrawing anything.

The pixels on screen are always the original ChatGPT drawing; only *when* each pixel appears is computed here.
Ink is thinned to a skeleton, split at junctions into short "strokes", and the strokes are ordered like an artist
works: long contours first, then medium detail, then short hatching, each pass hopping to the nearest next stroke.
Every pixel inherits the time of its nearest stroke point (a dense time map), which also gives the regional
progress used to fade the earlier stage out under the next one. The wash is brushed in by colour group (sky, then
greens, then everything else), left to right with a ragged edge.

    .venv/bin/python tools/stages.py      -> build/stages.npz (cached; delete it to recompute)
"""
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage
from skimage import morphology
from skimage.color import rgb2hsv
from skimage.registration import phase_cross_correlation

ROOT = Path(__file__).resolve().parent.parent
INC, OUT = ROOT / "incoming", ROOT / "build"


def load(name):
    a = np.asarray(Image.open(INC / f"train_{name}.png").convert("RGB"), dtype=np.float32)
    pw = np.concatenate([a[:24, :24].reshape(-1, 3), a[:24, -24:].reshape(-1, 3), a[-24:, -24:].reshape(-1, 3)]).mean(0)
    d = np.clip(1 - a / pw, 0, 1)  # darkness per channel: 0 = paper
    return np.clip((d - 0.025) / 0.975, 0, 1)


def strokes(dg, thr, cuts=(45, 12), speed=(1.0, 0.75, 0.5), gap=10.0):
    """Ordered skeleton strokes -> (T in 0..1 per skeleton pixel, dense T map, pen track sorted by T)."""
    H, W = dg.shape
    mask = morphology.remove_small_objects(dg > thr, 6)
    sk = morphology.skeletonize(mask)
    nb = ndimage.convolve(sk.astype(np.uint8), np.ones((3, 3), np.uint8), mode="constant") - 1
    junc = ndimage.binary_dilation(sk & (nb > 2)) & sk
    lab, n = ndimage.label(sk & ~junc, structure=np.ones((3, 3)))
    idx = np.flatnonzero(lab)
    labs = lab.ravel()[idx]
    o = np.argsort(labs, kind="stable")
    groups = np.split(idx[o], np.flatnonzero(np.diff(labs[o])) + 1)
    br = []
    for g in groups:
        ys, xs = np.divmod(g, W)
        pts = np.stack([xs, ys], 1).astype(np.float32)
        if len(g) > 2:  # order pixels along the branch's main axis
            c = pts - pts.mean(0)
            ax = np.linalg.eigh(c.T @ c)[1][:, -1]
            g, pts = g[np.argsort(c @ ax)], pts[np.argsort(c @ ax)]
        L = len(g)
        br.append(dict(g=g, a=pts[0], b=pts[-1], L=L, p=0 if L >= cuts[0] else 1 if L >= cuts[1] else 2))
    # passes big -> small; greedy nearest stroke from where the pen is
    pen, seq = np.array([0.0, H * 0.4]), []
    for p in range(3):
        rest = [b for b in br if b["p"] == p]
        if not rest:
            continue
        A = np.array([b["a"] for b in rest]); B = np.array([b["b"] for b in rest])
        left = np.ones(len(rest), bool)
        for _ in range(len(rest)):
            da = np.where(left, ((A - pen) ** 2).sum(1), np.inf)
            db = np.where(left, ((B - pen) ** 2).sum(1), np.inf)
            i = int(min(da.argmin(), db.argmin(), key=lambda k: min(da[k], db[k])))
            fwd = da[i] <= db[i]
            left[i] = False
            b = rest[i]
            seq.append((b, fwd))
            pen = b["b"] if fwd else b["a"]
    dur = np.array([b["L"] * speed[b["p"]] + gap for b, _ in seq])
    start = np.concatenate([[0], np.cumsum(dur)[:-1]]) / dur.sum()
    Tsk = np.full(H * W, np.inf, np.float32)
    for (b, fwd), s, d in zip(seq, start, dur / dur.sum()):
        r = np.linspace(0, 1, b["L"], dtype=np.float32)
        Tsk[b["g"]] = s + (r if fwd else r[::-1]) * (d - gap / dur.sum())
    Tsk = Tsk.reshape(H, W)
    inds = ndimage.distance_transform_edt(~np.isfinite(Tsk), return_distances=False, return_indices=True)
    dense = Tsk[inds[0], inds[1]]
    ys, xs = np.nonzero(np.isfinite(Tsk))
    o = np.argsort(Tsk[ys, xs])
    track = np.stack([Tsk[ys, xs][o], xs[o], ys[o]], 1).astype(np.float32)
    return dense.astype(np.float32), track[:: max(1, len(track) // 6000)]


def wash_order(wash, shaded):
    rgb = np.clip(1 - wash, 0, 1)
    hsv = rgb2hsv(rgb)
    chroma = rgb.max(2) - rgb.min(2)
    col = chroma > 0.07
    hue = hsv[..., 0]
    grp = np.where((hue > 0.5) & (hue < 0.72), 0, np.where((hue > 0.13) & (hue < 0.46), 1, 2))
    spans = {0: (0.0, 0.42), 1: (0.28, 0.78), 2: (0.62, 1.0)}  # sky first, greens, then train and concrete
    H, W = col.shape
    rng = np.random.default_rng(3)
    noise = ndimage.gaussian_filter(rng.standard_normal((H, W)), 28)
    noise = (noise - noise.min()) / (noise.max() - noise.min())
    xs = np.arange(W)[None, :].repeat(H, 0)
    T = np.full((H, W), np.inf, np.float32)
    for g, (g0, g1) in spans.items():
        m = col & (grp == g)
        if not m.any():
            continue
        x0, x1 = xs[m].min(), xs[m].max()
        p = 0.72 * (xs[m] - x0) / max(1, x1 - x0) + 0.28 * noise[m]
        T[m] = g0 + (g1 - g0) * p
    inds = ndimage.distance_transform_edt(~np.isfinite(T), return_distances=False, return_indices=True)
    dense = T[inds[0], inds[1]]
    ys, xs2 = np.nonzero(col)
    o = np.argsort(T[ys, xs2])
    track = np.stack([T[ys, xs2][o], xs2[o], ys[o]], 1).astype(np.float32)
    return dense.astype(np.float32), track[:: max(1, len(track) // 6000)]


def build():
    f = OUT / "stages.npz"
    if f.exists():
        return dict(np.load(f))
    OUT.mkdir(exist_ok=True)
    rough, lines, shaded, wash = (load(n) for n in ("rough", "lines", "shaded", "wash"))
    ref = shaded.mean(2)
    for name in ("rough", "lines", "wash"):  # register every stage onto the finished drawing
        img = locals()[name]
        sh = phase_cross_correlation(ref, img.mean(2), upsample_factor=4)[0]
        img[:] = ndimage.shift(img, (sh[0], sh[1], 0), order=1, mode="constant")
    out = dict(rough=rough.mean(2).astype(np.float16), lines=lines.mean(2).astype(np.float16),
               shaded=shaded.astype(np.float16), wash=wash.astype(np.float16))
    # rough: one continuous pass (searching lines stay unbroken); lines: contours then the small bits
    for name, img, thr, cuts in (("rough", rough, 0.05, (0, 0)), ("lines", lines, 0.22, (12, 12)),
                                 ("shaded", shaded, 0.18, (45, 12))):
        out[f"T_{name}"], out[f"trk_{name}"] = strokes(img.mean(2), thr, cuts)
        print(name, "strokes ordered")
    # tone goes down as a soft front with a diagonal hatch grain, not as blocks
    H, W = out["T_shaded"].shape
    yy, xx = np.mgrid[0:H, 0:W]
    out["T_shaded"] = (ndimage.gaussian_filter(out["T_shaded"], 8) + 0.006 * np.sin((xx + yy) * 0.45)).astype(np.float32)
    out["T_wash"], out["trk_wash"] = wash_order(wash, shaded)
    np.savez_compressed(f, **out)
    return out


if __name__ == "__main__":
    s = build()
    for k, v in s.items():
        print(k, v.shape, v.dtype)
