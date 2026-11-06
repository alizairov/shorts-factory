"""Why sunflowers use 137.5°: seeds placed by turning a fixed angle each time."""
import sys, math
import numpy as np, cairo
from common import *

GOLD = 360 * (1 - 1 / ((1 + 5 ** 0.5) / 2))   # 137.507...
SEEDS = 700
CX, CY = W / 2, 1000
SC = 17.5
# angle schedule: (time, angle)
KEYS = [(0, 90.0), (3.0, 90.0), (5.5, 120.0), (7.5, 120.0), (10, 135.0), (12, 135.0), (14.5, GOLD), (DUR := 22.0, GOLD)]
NF = int(DUR * FPS)


def ease(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def angle(t):
    for (t0, a0), (t1, a1) in zip(KEYS, KEYS[1:]):
        if t0 <= t <= t1:
            return a0 + (a1 - a0) * ease((t - t0) / max(t1 - t0, 1e-6))
    return KEYS[-1][1]


def draw(ctx, fi):
    t = fi / FPS
    a = angle(t)
    ctx.set_source_rgb(0.05, 0.03, 0.11); ctx.paint()
    grow = min(1, t / 2.5)
    n = int(SEEDS * grow)
    gold = abs(a - GOLD) < 0.01
    for i in range(n):
        th = math.radians(a * i)
        r = SC * math.sqrt(i)
        x, y = CX + r * math.cos(th), CY + r * math.sin(th)
        c = grad(i / SEEDS * 0.9)
        sz = 6 + 5 * (i / SEEDS)
        ctx.set_source_rgb(*c); circle(ctx, x, y, sz); ctx.fill()
    label(ctx, "PLACE A SEED,", W / 2, 230, 88)
    label(ctx, "TURN, REPEAT", W / 2, 320, 76, col=grad(0.62))
    txt = f"{a:.1f}°" if not gold else "137.5°"
    label(ctx, txt, W / 2, 1640, 130, col=(1, 0.85, 0.3) if gold else (1, 1, 1))
    if gold:
        b = ease((t - 14.6) / 0.5)
        label(ctx, "THE GOLDEN ANGLE", W / 2, 1740, 64, col=(1, 0.85, 0.3), alpha=b)
        label(ctx, "NO GAPS. THAT'S WHY SUNFLOWERS USE IT.", W / 2, 1830, 40, alpha=b)
    elif t > 3:
        label(ctx, "GAPS EVERYWHERE…", W / 2, 1740, 54, alpha=0.6)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=90, seed=61, vol=0.6, base=196)
    for i in range(0, SEEDS, 12):
        tt = 2.5 * i / SEEDS
        tr.add(pluck(note(i // 12 % 15, 392), 0.2, 0.05, 14), tt)
    for tt in (5.5, 10.0):
        tr.add(pluck(note(3, 196), 0.8, 0.14, 4), tt)
    for j, st in enumerate([0, 4, 7, 12, 16]):
        tr.add(pluck(note(st + 5, 261.63), 1.8, 0.15, 2.5), 14.5 + j * 0.06)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "w2g")
    else:
        audio("w2g.wav"); encode(draw, NF, "w2g_v.mp4"); mux("w2g_v.mp4", "w2g.wav", "w2_7_sunflower.mp4")
