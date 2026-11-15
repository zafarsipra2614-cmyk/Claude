#!/usr/bin/env python3
"""Turn line art into marker strokes, so the engine can draw the image the way a person would.

Usage: trace.py <image.png> <out.strokes.json> [--scale S]

Dark pixels are ink. The ink is thinned to a one-pixel skeleton, the skeleton is walked into
continuous strokes (following the line, not jumping), the strokes are ordered so the marker moves
to the nearest unfinished line next, and each stroke gets a brush width wide enough to cover the
ink around it. Coordinates are multiplied by --scale (use it when the PNG is a resized render of an SVG).
Output: {"w", "h", "strokes": [{"w": brush, "p": [x0, y0, x1, y1, ...]}, ...]}
"""
import json, sys, argparse
import numpy as np
from PIL import Image
from scipy import ndimage
from skimage.morphology import skeletonize

NB = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    a, b = np.array(pts[0], float), np.array(pts[-1], float)
    ab = b - a
    n = np.hypot(*ab)
    P = np.array(pts, float)
    D = P - a
    d = np.abs(ab[0] * D[:, 1] - ab[1] * D[:, 0]) / n if n else np.hypot(D[:, 0], D[:, 1])
    i = int(np.argmax(d))
    if d[i] > eps:
        return rdp(pts[:i + 1], eps)[:-1] + rdp(pts[i:], eps)
    return [pts[0], pts[-1]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--threshold", type=int, default=150)
    a = ap.parse_args()

    im = Image.open(a.src).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
    g = np.asarray(Image.alpha_composite(bg, im).convert("L"))
    ink = g < a.threshold
    H, W = ink.shape
    dist = ndimage.distance_transform_edt(ink)
    # solid areas (hair, dark clothes) are coloured in afterwards with scribbles; lines are traced
    T = max(5.0, 0.0065 * max(W, H))
    core = dist > T
    fill = ndimage.binary_dilation(core, iterations=int(T) + 3) & ink
    fill = ndimage.binary_opening(fill, iterations=2)
    lab0, n0 = ndimage.label(fill)                 # small solid bits (eyes, dots) are drawn as lines
    big = np.bincount(lab0.ravel())
    keep = big >= (0.06 * max(W, H)) ** 2
    keep[0] = False
    fill = keep[lab0]
    sk = skeletonize(ink & ~fill)
    # tiny specks: keep them out of the walk, the final fade-in covers them
    left = sk.copy()
    ys, xs = np.nonzero(left)

    def deg(y, x):
        return sum(1 for dy, dx in NB if 0 <= y + dy < H and 0 <= x + dx < W and left[y + dy, x + dx])

    strokes, pos = [], np.array([0.0, 0.0])
    while True:
        ys, xs = np.nonzero(left)
        if len(ys) == 0:
            break
        # prefer line ends near the marker; otherwise any pixel (closed loops)
        d2 = (ys - pos[0]) ** 2 + (xs - pos[1]) ** 2
        order = np.argsort(d2)[:400]
        start = None
        for k in order:
            if deg(ys[k], xs[k]) <= 1:
                start = (ys[k], xs[k]); break
        if start is None:
            k = order[0]; start = (ys[k], xs[k])
        y, x = start
        path, dirv = [(y, x)], None
        left[y, x] = False
        while True:
            best, bs = None, -9
            for dy, dx in NB:
                ny, nx = y + dy, x + dx
                if 0 <= ny < H and 0 <= nx < W and left[ny, nx]:
                    s = 0 if dirv is None else (dy * dirv[0] + dx * dirv[1]) / np.hypot(dy, dx)
                    s -= 0.05 * (abs(dy) + abs(dx) == 2)  # slight preference for straight neighbours
                    if s > bs:
                        best, bs = (ny, nx, dy, dx), s
            if best is None:
                break
            y, x, dy, dx = best
            # smooth the walking direction so the stroke follows the curve, not pixel steps
            dirv = (dy, dx) if dirv is None else (0.6 * dirv[0] + 0.4 * dy, 0.6 * dirv[1] + 0.4 * dx)
            left[y, x] = False
            path.append((y, x))
        pos = np.array(path[-1], float)
        if len(path) < 4:
            continue
        r = max(dist[p] for p in path)
        pts = rdp([(px, py) for py, px in path], 1.2)
        strokes.append({"w": round(min(2 * r + 4, 90) * a.scale, 1),
                        "p": [round(v * a.scale, 1) for xy in pts for v in xy]})

    # colour in the solid areas with diagonal back-and-forth marker strokes, one area at a time
    lab, n = ndimage.label(fill)
    objs = ndimage.find_objects(lab)
    brush = max(14.0, 0.03 * max(W, H))
    step = brush * 0.62
    ang = np.radians(-32)
    du, dv = np.array([np.cos(ang), np.sin(ang)]), np.array([-np.sin(ang), np.cos(ang)])
    near_fill = ndimage.binary_dilation(fill, iterations=int(brush * .45))
    # line strokes that sit entirely inside a solid area are redundant: the colouring covers them
    def inside(st):
        P_ = np.array(st["p"], float).reshape(-1, 2) / a.scale
        xi = np.clip(P_[:, 0].astype(int), 0, W - 1); yi = np.clip(P_[:, 1].astype(int), 0, H - 1)
        return near_fill[yi, xi].all()
    strokes = [st for st in strokes if not inside(st)]
    comps = sorted(range(n), key=lambda i: (objs[i][0].start, objs[i][1].start))
    for i in comps:
        sl = objs[i]
        m = lab[sl] == i + 1
        if m.sum() < brush * brush:
            continue
        hh, ww = m.shape
        c = np.array([sl[1].start + ww / 2, sl[0].start + hh / 2])
        R = np.hypot(hh, ww) / 2 + 2
        us = np.arange(-R, R, 1.5)
        cur, prev, flip = [], None, False
        for v in np.arange(-R + step / 2, R, step):
            P_ = c + np.outer(us, du) + v * dv
            xi = (P_[:, 0] - sl[1].start).astype(int); yi = (P_[:, 1] - sl[0].start).astype(int)
            ok = (xi >= 0) & (xi < ww) & (yi >= 0) & (yi < hh)
            row = np.zeros(len(us), bool)
            row[ok] = m[yi[ok], xi[ok]]
            if not row.any():
                continue
            e = np.flatnonzero(np.diff(np.r_[0, row.astype(int), 0]))
            runs = [(us[s0] , us[s1 - 1]) for s0, s1 in zip(e[0::2], e[1::2])]
            if prev is not None:
                runs.sort(key=lambda r: abs((r[0] + r[1]) / 2 - prev))
            r = runs[0]
            a_, b_ = (r[1], r[0]) if flip else (r[0], r[1])
            if cur and abs((r[0] + r[1]) / 2 - prev) > (r[1] - r[0]) / 2 + brush * 2:
                strokes.append(cur); cur = []
            cur += [list(c + a_ * du + v * dv), list(c + b_ * du + v * dv)]
            prev, flip = (r[0] + r[1]) / 2, not flip
            for r2 in runs[1:]:
                if r2[1] - r2[0] > brush * .6:
                    strokes.append([list(c + r2[0] * du + v * dv), list(c + r2[1] * du + v * dv)])
        if cur:
            strokes.append(cur)
    strokes = [s if isinstance(s, dict) else
               {"w": round(brush * 1.25 * a.scale, 1), "p": [round(float(v) * a.scale, 1) for xy in s for v in xy]}
               for s in strokes]

    # one continuous pass: lines and colouring together, each next stroke the one nearest the marker,
    # drawn from whichever end is closer, starting at the top of the picture
    pool = strokes[:]
    ends = np.array([[st["p"][0], st["p"][1], st["p"][-2], st["p"][-1]] for st in pool], float)
    alive = np.ones(len(pool), bool)
    tops = np.minimum(ends[:, 1], ends[:, 3])
    pos = None
    ordered = []
    for _ in range(len(pool)):
        if pos is None:
            k = int(np.argmin(np.where(alive, tops, np.inf)))
            rev = ends[k, 3] < ends[k, 1]
        else:
            d0 = np.hypot(ends[:, 0] - pos[0], ends[:, 1] - pos[1])
            d1 = np.hypot(ends[:, 2] - pos[0], ends[:, 3] - pos[1])
            d = np.where(alive, np.minimum(d0, d1), np.inf)
            k = int(np.argmin(d)); rev = d1[k] < d0[k]
        st = pool[k]; alive[k] = False
        if rev:
            q = st["p"]; st = {"w": st["w"], "p": [v for i in range(len(q) - 2, -1, -2) for v in q[i:i + 2]]}
        ordered.append(st)
        pos = (st["p"][-2], st["p"][-1])
    strokes = ordered

    json.dump({"w": round(W * a.scale, 1), "h": round(H * a.scale, 1), "strokes": strokes}, open(a.out, "w"))
    tot = sum(sum(np.hypot(np.diff(s["p"][0::2]), np.diff(s["p"][1::2]))) for s in strokes)
    print(f"{a.src}: {len(strokes)} strokes, {tot:.0f} units of line")


if __name__ == "__main__":
    main()
