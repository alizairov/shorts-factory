"""A thousand / million / billion / trillion seconds as time."""
import sys, math
import numpy as np, cairo
from common import *

ITEMS = [
    ("1 THOUSAND", "seconds", "16 MINUTES", 1e3),
    ("1 MILLION", "seconds", "11.5 DAYS", 1e6),
    ("1 BILLION", "seconds", "31.7 YEARS", 1e9),
    ("1 TRILLION", "seconds", "31,700 YEARS", 1e12),
]
STEP = 3.6
T0 = 1.4
DUR = T0 + STEP * len(ITEMS) + 2.6
NF = int(DUR * FPS)


def ease(u):
    u = min(max(u, 0), 1); return 1 - (1 - u) ** 3


def draw(ctx, fi):
    t = fi / FPS
    ctx.set_source_rgb(0.06, 0.03, 0.12); ctx.paint()
    label(ctx, "HOW LONG IS", W / 2, 230, 84)
    label(ctx, "A BILLION SECONDS?", W / 2, 325, 72, col=grad(0.62))
    cur = int((t - T0) // STEP) if t >= T0 else -1
    cur = min(cur, len(ITEMS) - 1)
    # log-scale bars, rescaled so the newest is full width
    top = 470
    for i, (a, b, c, v) in enumerate(ITEMS):
        if i > cur:
            continue
        ti = t - T0 - i * STEP
        u = ease(ti / 1.6)
        maxv = ITEMS[cur][3]
        prev_max = ITEMS[max(cur - 1, 0)][3]
        k = ease((t - T0 - cur * STEP) / 1.2)
        scale_v = math.exp(math.log(prev_max) + (math.log(maxv) - math.log(prev_max)) * k)
        frac = min(1, v / scale_v) * (u if i == cur else 1)
        y = top + i * 330
        col = grad(i / 4 * 0.9)
        ctx.set_source_rgba(1, 1, 1, 0.07); ctx.rectangle(80, y + 100, W - 160, 70); ctx.fill()
        ctx.set_source_rgb(*col); ctx.rectangle(80, y + 100, max(6, (W - 160) * frac), 70); ctx.fill()
        wa = label(ctx, a, 80, y + 70, 64, anchor="l")
        label(ctx, b, 80 + 18 + wa, y + 70, 40, anchor="l", alpha=0.6)
        if ti > 1.2:
            al = ease((ti - 1.2) / 0.4)
            pop = 1 + 0.15 * (1 - al)
            label(ctx, "= " + c, W - 80, y + 250, int(70 * pop), col=col, anchor="r", alpha=al)
    if t > T0 + STEP * len(ITEMS) - 0.6:
        a = ease((t - T0 - STEP * len(ITEMS) + 0.6) / 0.5)
        label(ctx, "31,700 YEARS AGO = THE ICE AGE", W / 2, 1830, 44, alpha=a)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=92, seed=21, vol=0.6, base=196)
    for i in range(len(ITEMS)):
        t0 = T0 + i * STEP
        n = np.arange(int(SR * 1.5)) / SR
        f = 200 + 600 * (1 - np.exp(-n * 2)) * (1 + i * 0.4)
        tr.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.07 * np.exp(-n * 1.5), t0)
        for k, st in enumerate([0, 4, 7]):
            tr.add(pluck(note(st + i * 2, 261.63), 1.2, 0.16, 3), t0 + 1.2 + k * 0.05)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "w2c")
    else:
        audio("w2c.wav"); encode(draw, NF, "w2c_v.mp4"); mux("w2c_v.mp4", "w2c.wav", "w2_3_billion.mp4")
