#!/usr/bin/env python3
"""Turn line art into marker strokes, so the engine can draw the image the way a person would.

Usage: trace.py <image.png> <out.strokes.json> [--scale S]

The marker finishes each element before moving to the nearest next one:
  - line parts: groups of nearby lines (a face with its eyes and mouth, a hand) traced along
    their skeleton, one continuous stroke after another
  - solid shapes: each connected dark area (hair, a sweater) is outlined along its real edge,
    then coloured in with back-and-forth strokes, as one piece
Parts are drawn top first, then always the nearest unfinished part. Coordinates are multiplied
by --scale (use it when the PNG is a resized render of an SVG).
Output: {"w", "h", "strokes": [{"w": brush, "p": [x0, y0, x1, y1, ...]}, ...]}
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
    T = max(5.0, 0.0065 * S)
    fill = ndimage.binary_dilation(dist > T, iterations=int(T) + 3) & ink
    fill = ndimage.binary_opening(fill, iterations=2)
    lab0, _ = ndimage.label(fill)
    keep = np.bincount(lab0.ravel()) >= (0.06 * S) ** 2
    keep[0] = False
    fill = keep[lab0]
    lab0 = lab0 * fill

    parts = lab0                                # each connected solid shape is drawn whole: outline, then colour in

    # line parts: nearby lines grouped (a face with its features), traced along the skeleton
    lines_ink = ink & ~fill
    grp, _ = ndimage.label(ndimage.binary_dilation(lines_ink, iterations=int(0.012 * S) + 2))
    near_fill = ndimage.binary_dilation(fill, iterations=int(0.012 * S))
    groups = {}
    for w, p in walk_skeleton(skeletonize(lines_ink), dist):
        P = np.array(p)
        xi, yi = np.clip(P[:, 0].astype(int), 0, W - 1), np.clip(P[:, 1].astype(int), 0, H - 1)
        if near_fill[yi, xi].all():
            continue                            # an edge of a solid area: its outline covers it
        groups.setdefault(int(grp[yi[0], xi[0]]), []).append((w, p))

    brush = max(14.0, 0.03 * S)
    units = [("lines", st) for st in groups.values()]
    for k in range(1, int(parts.max()) + 1):
        m = parts == k
        if m.sum() < brush * brush:
            continue
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        mm = m[y0:y1, x0:x1]
        outline = []
        for cnt in find_contours(np.pad(mm, 1).astype(float), .5):
            if len(cnt) > 12:
                outline.append((max(8.0, 0.012 * S), rdp([(c[1] + x0 - 1, c[0] + y0 - 1) for c in cnt], 1.5)))
        units.append(("solid", (outline, [(brush * 1.25, h) for h in hatch(mm, np.array([x0, y0]), brush)])))

    # draw part by part: top part first, then always the nearest unfinished part; finish it, move on
    def ends_of(u):
        kind, d = u
        sts = d if kind == "lines" else d[0] + d[1]
        return np.array([q for _, p in sts for q in (p[0], p[-1])], float)
    ends = [ends_of(u) for u in units]
    pos, done, strokes = None, [False] * len(units), []
    for _ in range(len(units)):
        if pos is None:
            k = min(range(len(units)), key=lambda i: ends[i][:, 1].min())
            pos = tuple(ends[k][np.argmin(ends[k][:, 1])])
        else:
            k = min((i for i in range(len(units)) if not done[i]),
                    key=lambda i: np.hypot(ends[i][:, 0] - pos[0], ends[i][:, 1] - pos[1]).min())
        done[k] = True
        kind, d = units[k]
        if kind == "lines":
            seq, pos = chain(d, pos)
        else:
            out_seq, pos = chain(d[0], pos)      # outline the part
            fill_seq, pos = chain(d[1], pos)     # then colour it in
            seq = out_seq + fill_seq
        strokes += [{"w": round(w * a.scale, 1), "p": [round(float(v) * a.scale, 1) for q in p for v in q]} for w, p in seq]

    # make sure the drawing ends complete: any ink the brush missed gets clean-up strokes at the end
    def covered(sts):
        cov = Image.new("L", (W, H), 0); cd = ImageDraw.Draw(cov)
        for st in sts:
            P = [(st["p"][i] / a.scale, st["p"][i + 1] / a.scale) for i in range(0, len(st["p"]), 2)]
            r = st["w"] / a.scale / 2
            if len(P) > 1: cd.line(P, fill=255, width=max(1, int(st["w"] / a.scale)), joint="curve")
            for q in (P[0], P[-1]): cd.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=255)
        return np.asarray(cov) > 0
    miss = ink & ~covered(strokes)
    miss = ndimage.binary_opening(miss) | (miss & (dist > 1.5))
    if miss.any():
        extra, _ = chain(walk_skeleton(skeletonize(ndimage.binary_dilation(miss, iterations=2) & ink), dist), pos or (0, 0))
        strokes += [{"w": round((w + 6) * a.scale, 1), "p": [round(float(v) * a.scale, 1) for q in p for v in q]} for w, p in extra]
        left = ink & ~covered(strokes)
    else:
        left = miss
    pct = 100 * left.sum() / max(ink.sum(), 1)
    if pct > 0.3:
        print(f"WARNING {name}: {pct:.1f}% of the ink is still not reached by the marker")

    json.dump({"w": round(W * a.scale, 1), "h": round(H * a.scale, 1), "strokes": strokes}, open(a.out, "w"))
    tot = sum(sum(np.hypot(np.diff(s["p"][0::2]), np.diff(s["p"][1::2]))) for s in strokes)
    print(f"{name}: {len(units)} parts, {len(strokes)} strokes, {tot:.0f} units of line")


if __name__ == "__main__":
    main()
