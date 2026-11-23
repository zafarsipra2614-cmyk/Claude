#!/usr/bin/env python3
"""Turn line art into marker strokes, so the engine can draw the image the way a person would.

Usage: trace.py <image.png> <out.strokes.json> [--scale S]

Three stages, the way an illustrator works:
  1. sketch: a light, loose pencil outline of the whole figure (erased at the end)
  2. ink:    the whole picture as black line art, one continuous pass from the top; solid shapes
             get their outline here (saved as <name>.ink.png next to the strokes file)
  3. colour: one colour group at a time (all the blue, then all the black...), with back-and-forth strokes

Coordinates are multiplied by --scale (use it when the PNG is a resized render of an SVG).
Output: {"w", "h", "inkimg", "sketch": {"w", "strokes"}, "ink": [{"w", "p"}], "color": [{"w", "p", "c"}]}
"""
import json, argparse
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from skimage.morphology import skeletonize
from skimage.measure import find_contours

NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0], float), np.array(pts[-1], float)
    ab = b - a
    n = np.hypot(*ab)
    D = np.array(pts, float) - a
    d = np.abs(ab[0] * D[:, 1] - ab[1] * D[:, 0]) / n if n else np.hypot(D[:, 0], D[:, 1])
    i = int(np.argmax(d))
    if d[i] > eps:
        return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [pts[0], pts[-1]]


def walk_skeleton(sk, dist):
    """Walk a skeleton into strokes: (brush width, [(x, y), ...])."""
    H, W = sk.shape
    left = sk.copy()
    out, pos = [], (0.0, 0.0)

    def deg(y, x):
        return sum(1 for dy, dx in NB if 0 <= y + dy < H and 0 <= x + dx < W and left[y + dy, x + dx])

    while True:
        ys, xs = np.nonzero(left)
        if len(ys) == 0:
            return out
        d2 = (ys - pos[1]) ** 2 + (xs - pos[0]) ** 2
        order = np.argsort(d2)[:400]
        start = next(((ys[k], xs[k]) for k in order if deg(ys[k], xs[k]) <= 1), (ys[order[0]], xs[order[0]]))
        y, x = start
        path, dirv = [(y, x)], None
        left[y, x] = False
        while True:
            best, bs = None, -9
            for dy, dx in NB:
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and left[ny, nx]:
                    s = 0 if dirv is None else (dy * dirv[0] + dx * dirv[1]) / np.hypot(dy, dx)
                    s -= 0.05 * (abs(dy) + abs(dx) == 2)
                    if s > bs:
                        best, bs = (ny, nx, dy, dx), s
            if best is None:
                break
            y, x, dy, dx = best
            dirv = (dy, dx) if dirv is None else (0.6 * dirv[0] + 0.4 * dy, 0.6 * dirv[1] + 0.4 * dx)
            left[y, x] = False
            path.append((y, x))
        pos = (path[-1][1], path[-1][0])
        if len(path) >= 4:
            r = max(dist[p] for p in path)
            out.append((min(2 * r + 4, 90), rdp([(px, py) for py, px in path], 1.2)))


def chain(strokes, pos):
    """Order strokes nearest-first from pos, each drawn from its closer end. Returns (ordered, end pos)."""
    pool, out = list(strokes), []
    while pool:
        best = min(range(len(pool)), key=lambda i: min(np.hypot(pool[i][1][0][0] - pos[0], pool[i][1][0][1] - pos[1]),
                                                        np.hypot(pool[i][1][-1][0] - pos[0], pool[i][1][-1][1] - pos[1])))
        w, p = pool.pop(best)
        if np.hypot(p[-1][0] - pos[0], p[-1][1] - pos[1]) < np.hypot(p[0][0] - pos[0], p[0][1] - pos[1]):
            p = p[::-1]
        out.append((w, p))
        pos = p[-1]
    return out, pos


def hatch(m, off, brush, ang_deg=-32):
    """Back-and-forth colouring strokes inside boolean mask m (offset off = (x0, y0))."""
    step = brush * 0.62
    ang = np.radians(ang_deg)
    du, dv = np.array([np.cos(ang), np.sin(ang)]), np.array([-np.sin(ang), np.cos(ang)])
    hh, ww = m.shape
    c = np.array([ww / 2, hh / 2])
    R = np.hypot(hh, ww) / 2 + 2
    us = np.arange(-R, R, 1.5)
    out, cur, prev, flip = [], [], None, False
    for v in np.arange(-R + step / 2, R, step):
        P = c + np.outer(us, du) + v * dv
        xi, yi = P[:, 0].astype(int), P[:, 1].astype(int)
        ok = (xi >= 0) & (xi < ww) & (yi >= 0) & (yi < hh)
        row = np.zeros(len(us), bool)
        row[ok] = m[yi[ok], xi[ok]]
        if not row.any():
            continue
        e = np.flatnonzero(np.diff(np.r_[0, row.astype(int), 0]))
        runs = [(us[a], us[b - 1]) for a, b in zip(e[0::2], e[1::2])]
        if prev is not None:
            runs.sort(key=lambda r: abs((r[0] + r[1]) / 2 - prev))
        r = runs[0]
        a_, b_ = (r[1], r[0]) if flip else (r[0], r[1])
        if cur and abs((r[0] + r[1]) / 2 - prev) > (r[1] - r[0]) / 2 + brush * 2:
            out.append(cur); cur = []
        cur += [tuple(c + a_ * du + v * dv + off), tuple(c + b_ * du + v * dv + off)]
        prev, flip = (r[0] + r[1]) / 2, not flip
        for r2 in runs[1:]:
            if r2[1] - r2[0] > brush * .6:
                out.append([tuple(c + r2[0] * du + v * dv + off), tuple(c + r2[1] * du + v * dv + off)])
    if cur:
        out.append(cur)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--threshold", type=int, default=150)
    ap.add_argument("--label", help="name used in messages")
    a = ap.parse_args()
    name = a.label or a.src

    im = Image.open(a.src).convert("RGBA")
    rgb = np.asarray(Image.alpha_composite(Image.new("RGBA", im.size, (255, 255, 255, 255)), im).convert("RGB")).astype(int)
    g = rgb.mean(2)
    sat = rgb.max(2) - rgb.min(2)
    ink = (g < a.threshold) | ((sat > 60) & (g < 235))     # black lines and coloured (accent) areas
    H, W = ink.shape
    S = max(W, H)
    # art that touches its canvas edge is almost always cut off (a sliced arm, a chopped head)
    edges = {"top": ink[0].sum(), "bottom": ink[-1].sum(), "left": ink[:, 0].sum(), "right": ink[:, -1].sum()}
    cut = [k for k, v in edges.items() if v > 0.01 * (W if k in ("top", "bottom") else H)]
    if cut:
        print(f"WARNING {name}: the art touches the {' and '.join(cut)} edge of its canvas, so it is probably cut off. "
              "Fix the canvas (peep.js crops characters correctly) before using it.")
    dist = ndimage.distance_transform_edt(ink)

    # solid areas: thick ink, big enough to colour in (small dots like eyes stay lines)
    T = max(5.0, 0.016 * S)                     # thicker than ~3% of the picture = a solid area; bold lines stay lines
    fill = ndimage.binary_dilation(dist > T, iterations=int(T) + 3) & ink
    fill = ndimage.binary_opening(fill, iterations=2)
    lab0, _ = ndimage.label(fill)
    keep = np.bincount(lab0.ravel()) >= (0.06 * S) ** 2
    keep[0] = False
    fill = keep[lab0]
    lab0 = lab0 * fill

    # ---- colour groups: split solid areas by colour (blue clothes, black hair, grey glass...) ----
    key = (rgb // 40) @ np.array([10000, 100, 1])
    core = ndimage.binary_erosion(fill, iterations=2)
    groups_lab = np.zeros((H, W), int); n_lab = 0
    for kv in np.unique(key[core]):
        m = core & (key == kv)
        if m.sum() < (0.02 * S) ** 2:
            continue
        lab, n = ndimage.label(m)
        groups_lab[lab > 0] = lab[lab > 0] + n_lab; n_lab += n
    if n_lab:   # edge pixels and stray colours join their nearest group
        _, (iy, ix) = ndimage.distance_transform_edt(groups_lab == 0, return_indices=True)
        groups_lab = np.where(fill, groups_lab[iy, ix], 0)
    parts = []
    # white fills (skin, eye whites, bulb glass): only when the art has real transparency, so a white
    # background is never mistaken for a shape. They are painted during colouring, so nothing pops at the end.
    alpha = np.asarray(im)[..., 3]
    whites = None
    if (alpha < 20).mean() > 0.05:
        whites = ndimage.binary_opening((alpha > 200) & ~ink & ~fill, iterations=2)
        wl, nw = ndimage.label(whites)
        if nw:
            keep_w = np.bincount(wl.ravel()) >= (0.02 * S) ** 2; keep_w[0] = False
            whites = keep_w[wl]
    for k in range(1, n_lab + 1):
        m = groups_lab == k
        if m.sum() < 30:
            continue
        c = np.median(rgb[m & core] if (m & core).any() else rgb[m], axis=0)
        parts.append((m, "#%02x%02x%02x" % tuple(int(v) for v in c)))

    if whites is not None and whites.any():
        wl, nw = ndimage.label(whites)
        for k in range(1, nw + 1):
            parts.append((wl == k, "#ffffff"))

    # ---- the ink layer: the picture as black line art (lines + outlines of every solid shape) ----
    line_px = ink & ~fill
    edge_w = max(2, int(0.0025 * S))
    edges_px = np.zeros((H, W), bool)
    for m, c in parts:
        if c != "#ffffff":                       # white shapes already sit inside black lines
            edges_px |= m & ~ndimage.binary_erosion(m, iterations=edge_w)
    ink_layer = np.zeros((H, W, 4), np.uint8)
    ink_layer[line_px, :3] = rgb[line_px]
    ink_layer[edges_px, :3] = (31, 35, 40)
    ink_layer[line_px | edges_px, 3] = 255
    ink_path = a.out[:-len(".strokes.json")] + ".ink.png" if a.out.endswith(".strokes.json") else a.out + ".ink.png"
    Image.fromarray(ink_layer, "RGBA").save(ink_path)
    ink_any = line_px | edges_px

    def pack(w, p, c=None):
        d = {"w": round(w * a.scale, 1), "p": [round(float(v) * a.scale, 1) for q in p for v in q]}
        if c: d["c"] = c
        return d

    def covered(sts, scale=a.scale):
        cov = Image.new("L", (W, H), 0); cd = ImageDraw.Draw(cov)
        for st in sts:
            P = [(st["p"][i] / scale, st["p"][i + 1] / scale) for i in range(0, len(st["p"]), 2)]
            r = st["w"] / scale / 2
            if len(P) > 1: cd.line(P, fill=255, width=max(1, int(st["w"] / scale)), joint="curve")
            for q in (P[0], P[-1]): cd.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
        return np.asarray(cov) > 0

    # ---- 1. sketch: a light, loose pencil outline of the whole figure, erased later ----
    blob = ndimage.binary_fill_holes(ndimage.binary_closing(ink | fill, iterations=int(0.02 * S) + 1))
    blob_lab, nb = ndimage.label(blob)
    sketch = []
    rng = np.random.default_rng(7)
    for k in range(1, nb + 1):
        m = blob_lab == k
        if m.sum() < (0.05 * S) ** 2:
            continue
        for cnt in find_contours(np.pad(m, 1).astype(float), .5):
            if len(cnt) < 40:
                continue
            pts = rdp([(c[1] - 1, c[0] - 1) for c in cnt], 0.012 * S)
            for jit in (0.006, 0.0):            # two loose passes, like a pencil going round twice
                sketch.append([(x + rng.normal(0, jit * S), y + rng.normal(0, jit * S)) for x, y in pts])
    sketch_seq, pos = chain([(0, p) for p in sketch], (0, 0))

    # ---- 2. ink: every line and every outline, one continuous pass from the top ----
    near_fill = ndimage.binary_dilation(fill, iterations=int(0.012 * S))
    ink_strokes = []
    for w, p in walk_skeleton(skeletonize(line_px), dist):
        P = np.array(p)
        xi, yi = np.clip(P[:, 0].astype(int), 0, W - 1), np.clip(P[:, 1].astype(int), 0, H - 1)
        if not near_fill[yi, xi].all():
            ink_strokes.append((w, p))
    outline_w = max(8.0, 0.012 * S)
    for m, col in parts:
        if col == "#ffffff":
            continue
        for cnt in find_contours(np.pad(m, 1).astype(float), .5):
            if len(cnt) > 12:
                ink_strokes.append((outline_w, rdp([(c[1] - 1, c[0] - 1) for c in cnt], 1.5)))
    ink_seq, pos = chain(ink_strokes, pos)
    ink_out = [pack(w, p) for w, p in ink_seq]
    miss = ink_any & ~covered(ink_out)
    if miss.any():                                  # clean-up so the line art always ends complete
        extra, pos = chain(walk_skeleton(skeletonize(ndimage.binary_dilation(miss, iterations=2) & ink_any), dist), pos)
        ink_out += [pack(w + 6, p) for w, p in extra]

    # ---- 3. colour: one colour group at a time (all the blue, then the black...), top group first ----
    brush = max(14.0, 0.03 * S)
    colour_out = []
    by_colour = {}
    for m, c in parts:
        by_colour.setdefault(c, []).append(m)
    order = sorted(by_colour, key=lambda c: min(np.nonzero(m)[0].min() for m in by_colour[c]))
    for c in order:
        sts = []
        for m in by_colour[c]:
            ys, xs = np.nonzero(m)
            y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
            sts += [(brush * 1.25, h) for h in hatch(m[y0:y1, x0:x1], np.array([x0, y0]), brush)]
        seq, pos = chain(sts, pos)
        colour_out += [pack(w, p, c) for w, p in seq]
    paint = fill | (whites if whites is not None else False)
    miss = paint & ~covered(colour_out)
    miss = ndimage.binary_opening(miss)
    if miss.any():
        extra, pos = chain(walk_skeleton(skeletonize(ndimage.binary_dilation(miss, iterations=2) & paint), ndimage.distance_transform_edt(paint)), pos)
        colour_out += [pack(w + 6, p) for w, p in extra]

    left = (ink_any & ~covered(ink_out)) | (ndimage.binary_opening(paint & ~covered(colour_out)))
    pct = 100 * left.sum() / max((ink_any | paint).sum(), 1)
    if pct > 0.3:
        print(f"WARNING {name}: {pct:.1f}% of the picture is still not reached by the marker")

    out = {"w": round(W * a.scale, 1), "h": round(H * a.scale, 1), "inkimg": ink_path.rsplit("/", 1)[-1],
           "sketch": {"w": round(max(3.0, 0.0035 * S) * a.scale, 1), "strokes": [pack(0, p)["p"] for _, p in sketch_seq]},
           "ink": ink_out, "color": colour_out}
    json.dump(out, open(a.out, "w"))
    print(f"{name}: sketch {len(sketch_seq)}, ink {len(ink_out)}, colour {len(colour_out)} strokes in {len(order)} colour groups")

if __name__ == "__main__":
    main()
