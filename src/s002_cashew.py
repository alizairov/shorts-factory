"""S-002 · Paper cutout · The cashew grows in a shell beneath the cashew apple."""
import sys, math
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, SR, mux
from paper import paper, pin, rect_pts, ellipse_pts, path, TEX
from paperkit import *

DUR = 16.0
NF = int(DUR * FPS)
T_REVEAL, T_OPEN, T_MATCH, T_LOOP = 2.4, 6.0, 10.0, 13.0
BG1, BG2 = (0.98, 0.90, 0.66), (0.93, 0.78, 0.52)
LEAF, LEAF2 = (0.36, 0.62, 0.34), (0.27, 0.52, 0.30)
APPLE, APPLE2 = (0.93, 0.33, 0.22), (0.98, 0.62, 0.25)
SHELL, SHELL_IN = (0.56, 0.58, 0.40), (0.42, 0.40, 0.28)
KERNEL = (0.98, 0.92, 0.78)
PIVOT = (560, 600)
ROPE = 300


def kidney(cx, cy, s, rot=0.0, n=44):
    """solid cashew / kidney-bean outline with a dent on one side"""
    out = []
    for k in range(n):
        a = 2 * math.pi * k / n
        r = 1 - 0.55 * math.exp(-((a - math.pi / 2) / 0.45) ** 2)
        x, y = 1.15 * r * math.cos(a), 0.72 * r * math.sin(a)
        xr = x * math.cos(rot) - y * math.sin(rot); yr = x * math.sin(rot) + y * math.cos(rot)
        out.append((cx + xr * s, cy + yr * s))
    return out


def leaf_pts(x, y, L, w, ang, n=14):
    pts = []
    for k in range(n + 1):
        u = k / n
        pts.append((u * L, w * math.sin(math.pi * u)))
    for k in range(n, -1, -1):
        u = k / n
        pts.append((u * L, -w * math.sin(math.pi * u)))
    return [(x + px * math.cos(ang) - py * math.sin(ang), y + px * math.sin(ang) + py * math.cos(ang)) for px, py in pts]


def apple_pts(cx, cy, rot):
    pts = []
    for k in range(36):
        a = 2 * math.pi * k / 36
        r = 1 + 0.18 * math.sin(a)                     # wider at the bottom
        x, y = 0.78 * r * math.cos(a), 1.0 * math.sin(a)
        pts.append((x, y))
    out = []
    for x, y in pts:
        X, Y = x * 160, y * 200
        xr = X * math.cos(rot) - Y * math.sin(rot); yr = X * math.sin(rot) + Y * math.cos(rot)
        out.append((cx + xr, cy + yr))
    return out


def swing(t):
    if t < T_REVEAL: return 0.05 * math.sin(t * 2.2)
    if t < T_REVEAL + 1.2: return 0.05 * math.sin(t * 2.2) + 0.35 * math.sin(math.pi * (t - T_REVEAL) / 1.2) * 0.6
    if t < T_LOOP: return 0.04 * math.sin(t * 2.0)
    return 0.05 * math.sin(t * 2.2) + 0.25 * math.sin(math.pi * min(1, (t - T_LOOP) / 1.5))


def draw(ctx, fi):
    t = fi / FPS; ts = stop(t)
    textured_bg(ctx, BG1, BG2)
    # background foliage
    for i, (x, y, L, ang) in enumerate([(-60, 1500, 420, -0.5), (W + 60, 1450, 440, math.pi + 0.5), (-80, 1800, 460, -0.2), (W + 80, 1780, 480, math.pi + 0.25), (W / 2 - 40, 1950, 380, -1.4)]):
        paper(ctx, leaf_pts(x, y, L, 90, ang + 0.03 * math.sin(ts + i)), LEAF2 if i % 2 else LEAF, seed=10 + i, shadow=(6, 9))
    # branch
    paper(ctx, [(-40, 560), (W + 40, 520), (W + 40, 560), (-40, 610)], (0.45, 0.30, 0.18), seed=20, shadow=(6, 9))
    for i, x in enumerate([60, 250, 820, 1000]):
        a = 0.9 if i % 2 else 2.2
        paper(ctx, leaf_pts(x, 575, 230, 55, a + 0.04 * math.sin(ts * 1.5 + i)), LEAF if i % 2 else LEAF2, seed=30 + i, shadow=(5, 7))
    # hanging cashew apple + nut
    ang = swing(ts)
    ax = PIVOT[0] + ROPE * math.sin(ang); ay = PIVOT[1] + ROPE * math.cos(ang)
    ctx.set_source_rgb(0.35, 0.25, 0.15); ctx.set_line_width(10)
    ctx.move_to(*PIVOT); ctx.line_to(ax, ay - 200); ctx.stroke()
    paper(ctx, apple_pts(ax, ay, ang), APPLE, seed=40)
    ctx.set_source_rgba(1, 0.8, 0.6, 0.35); ctx.save(); ctx.translate(ax - 50, ay - 60); ctx.scale(1, 1.6); ctx.arc(0, 0, 28, 0, 2 * math.pi); ctx.fill(); ctx.restore()
    # shell under the apple
    bx = ax + 230 * math.sin(ang); by = ay + 230 * math.cos(ang) + 50
    open_u = ease((ts - T_OPEN) / 0.5) * (1 - ease((ts - T_LOOP) / 0.6))
    paper(ctx, kidney(bx, by, 140, ang + math.pi), SHELL, seed=50)
    if open_u > 0.01:
        paper(ctx, kidney(bx, by + 6, 118, ang + math.pi), SHELL_IN, seed=51, shadow=(0, 0), sh_a=0, rough=0.6)
        paper(ctx, kidney(bx, by + 6, 100 * open_u, ang + math.pi), KERNEL, seed=52, shadow=(2, 3), rough=0.6)
        # flap lifting like a paper lid
        hx, hy = bx - 150, by
        ctx.save(); ctx.translate(hx, hy); ctx.rotate(-1.9 * open_u); ctx.translate(-hx, -hy)
        paper(ctx, kidney(bx, by, 140, ang + math.pi)[22:] + kidney(bx, by, 140, ang + math.pi)[:1], (0.64, 0.66, 0.48), seed=53, shadow=(5, 8))
        ctx.restore()
        pin(ctx, hx, hy, 9)
    # leaf that hides the nut at the very start
    hide = 1 - ease((ts - T_REVEAL) / 0.6)
    if hide > 0.01:
        lx = bx - 40 - 500 * (1 - hide)
        paper(ctx, leaf_pts(lx - 200, by + 40, 440, 120, -0.15), LEAF, seed=60, shadow=(8, 11))
    # loose kernel: turns on the right, then slides onto the seed
    if ts < T_LOOP:
        if ts < T_MATCH:
            kx, ky, kr, ks = 870, 1080, ts * 0.8, 100
        else:
            u = ease((ts - T_MATCH) / 1.0)
            kx = 870 + (bx - 870) * u; ky = 1080 + (by + 6 - 1080) * u
            kr = T_MATCH * 0.8 * (1 - u) + (ang + math.pi) * u; ks = 100
        a = 1 if ts < T_MATCH + 1.3 else 1 - ease((ts - T_MATCH - 1.3) / 0.3)
        if a > 0.01:
            ctx.push_group(); paper(ctx, kidney(kx, ky, ks, kr), KERNEL, seed=70, shadow=(5, 7)); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
        if ts > T_MATCH + 1.0 and ts < T_LOOP:
            ctx.set_source_rgba(0.95, 0.55, 0.20, 0.9); ctx.set_line_width(5); ctx.set_dash([12, 10])
            pts = kidney(bx, by + 6, 112, ang + math.pi)
            ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]; ctx.close_path(); ctx.stroke(); ctx.set_dash([])
    # text — top zone
    if ts < T_REVEAL:
        banner(ctx, "WHERE DOES", 270, 84, seed=1)
        banner(ctx, "THE CASHEW GROW?", 390, 76, col=(0.80, 0.30, 0.20), seed=2)
    elif ts < T_OPEN:
        banner(ctx, "UNDER THE", 270, 80, seed=3, a=ease((ts - T_REVEAL - 0.4) / 0.3))
        banner(ctx, "CASHEW APPLE", 390, 84, col=(0.80, 0.30, 0.20), seed=4, a=ease((ts - T_REVEAL - 0.5) / 0.3))
    elif ts < T_MATCH:
        banner(ctx, "INSIDE THIS SHELL", 320, 80, seed=5, a=ease((ts - T_OPEN) / 0.3))
    elif ts < T_LOOP:
        banner(ctx, "FOUND IT", 320, 110, col=(0.25, 0.50, 0.25), seed=6, a=ease((ts - T_MATCH - 1.0) / 0.3))
    else:
        banner(ctx, "ONE LITTLE HOOK", 320, 90, seed=7, a=ease((ts - T_LOOP) / 0.3))
    vignette(ctx, 0.25)


def audio(path):
    tr = Track(DUR)
    ambience(tr, DUR, 0.02)
    musicbox(tr, DUR, mel=(0, 4, 7, 9, 7, 4, 2, 4), gap=0.6, vol=0.06)
    tr.add(tap(300, 0.2), 0.2)
    tr.add(whoosh(0.8, 0.10), T_REVEAL)
    tr.add(pluck(note(4, 261.63), 1.2, 0.14, 3), T_REVEAL + 0.5)
    tr.add(soft_noise(0.25, 10, 0.12), T_OPEN)               # paper flick
    tr.add(pluck(note(9, 392), 0.8, 0.12, 4), T_OPEN + 0.3)
    tr.add(whoosh(0.9, 0.07), T_MATCH)
    tr.add(tap(220, 0.25), T_MATCH + 1.0)
    tr.add(pluck(note(12, 392), 1.0, 0.14, 3), T_MATCH + 1.05)
    tr.add(whoosh(0.9, 0.08), T_LOOP)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "s2")
    else:
        audio("s2.wav"); encode(draw, NF, "s2_v.mp4"); mux("s2_v.mp4", "s2.wav", "s002_cashew.mp4")
