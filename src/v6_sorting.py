import sys, math
import numpy as np, cairo
from common import *

N = 48
rng = np.random.default_rng(11)
START = rng.permutation(N)


def bubble(a):
    a = list(a); ops = []
    for i in range(len(a)):
        for j in range(len(a) - 1 - i):
            ops.append(("cmp", j, j + 1))
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                ops.append(("swap", j, j + 1))
    return ops


def quick(a):
    a = list(a); ops = []

    def qs(lo, hi):
        if lo >= hi:
            return
        p = a[hi]; i = lo
        for j in range(lo, hi):
            ops.append(("cmp", j, hi))
            if a[j] < p:
                a[i], a[j] = a[j], a[i]
                ops.append(("swap", i, j)); i += 1
        a[i], a[hi] = a[hi], a[i]
        ops.append(("swap", i, hi))
        qs(lo, i - 1); qs(i + 1, hi)
    qs(0, len(a) - 1)
    return ops


OPS = {"BUBBLE SORT": bubble(START), "QUICK SORT": quick(START)}
OPS_PER_SEC = 120
INTRO = 1.5
names = list(OPS)
lens = {k: len(v) for k, v in OPS.items()}
t_done = {k: INTRO + lens[k] / OPS_PER_SEC for k in names}
DUR = max(t_done.values()) + 3.0
NF = int(DUR * FPS)


def states(ops):
    a = list(START); snaps = [(list(a), None)]
    for op in ops:
        if op[0] == "swap":
            i, j = op[1], op[2]; a[i], a[j] = a[j], a[i]
        snaps.append((list(a), op))
    return snaps


SNAPS = {k: states(v) for k, v in OPS.items()}


def panel(ctx, name, top, t, finished_first):
    snaps = SNAPS[name]
    k = int(min(len(snaps) - 1, max(0, (t - INTRO) * OPS_PER_SEC)))
    arr, op = snaps[k]
    done = k == len(snaps) - 1
    x0, x1 = 60, W - 60
    bw = (x1 - x0) / N
    hmax = 560
    base = top + 640
    # panel card
    ctx.set_source_rgba(1, 1, 1, 0.05)
    ctx.rectangle(30, top, W - 60, 700); ctx.fill()
    hl = set(op[1:]) if (op and not done) else set()
    for i, v in enumerate(arr):
        h = 30 + (v + 1) / N * hmax
        c = grad(v / N * 0.95)
        if i in hl:
            c = (1, 1, 1)
        ctx.set_source_rgb(*c)
        ctx.rectangle(x0 + i * bw + 2, base - h, bw - 4, h); ctx.fill()
    label(ctx, name, 70, top + 70, 58, anchor="l")
    ops_done = k
    label(ctx, f"{ops_done:,} steps", W - 70, top + 70, 44, anchor="r", col=(1, 1, 1), alpha=0.7)
    if done:
        dt = t - t_done[name]
        a = ease_(dt / 0.3)
        txt = "WINNER" if finished_first else "DONE"
        col = grad(0.62) if finished_first else (1, 1, 1)
        ctx.set_source_rgba(0.05, 0.02, 0.12, 0.8 * a)
        ctx.rectangle(W / 2 - 300, top + 250, 600, 200); ctx.fill()
        label(ctx, txt, W / 2, top + 365, int(110 * (1 + 0.2 * (1 - a))), col=col, alpha=a)
        label(ctx, f"{t_done[name] - INTRO:.1f} seconds", W / 2, top + 425, 44, alpha=0.8 * a)


def ease_(u):
    u = min(max(u, 0), 1)
    return u * u * (3 - 2 * u)


def draw(ctx, fi):
    t = fi / FPS
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.08, 0.04, 0.17)
    g.add_color_stop_rgb(1, 0.02, 0.01, 0.06)
    ctx.set_source(g); ctx.paint()
    label(ctx, "SORTING RACE", W / 2, 150, 92)
    label(ctx, "SAME 48 BARS · WHO WINS?", W / 2, 225, 44, col=grad(0.45))
    first = min(t_done, key=t_done.get)
    panel(ctx, names[0], 290, t, names[0] == first)
    panel(ctx, names[1], 1020, t, names[1] == first)
    tm = max(0, t - INTRO)
    label(ctx, f"{min(tm, max(t_done.values()) - INTRO):.1f}s", W / 2, 1830, 60, col=(1, 1, 1), alpha=0.8)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=120, seed=5, vol=0.45, base=220)
    for name, pan in zip(names, (0, 1)):
        snaps = SNAPS[name]
        for k, (arr, op) in enumerate(snaps[1:], 1):
            if op[0] != "swap" or k % 2:
                continue
            tt = INTRO + k / OPS_PER_SEC
            v = arr[op[1]]
            f = 200 + v / N * 900 + pan * 100
            n = np.arange(int(SR * 0.05)) / SR
            tr.add(np.sin(2 * np.pi * f * n) * np.exp(-n * 60) * 0.05, tt)
        for st in (0, 4, 7, 12):
            tr.add(pluck(note(st, 261.63 * (1 + pan * 0.5)), 1.2, 0.15, 3), t_done[name])
    tr.save(path, DUR)


if __name__ == "__main__":
    print({k: round(v, 1) for k, v in t_done.items()}, "DUR", DUR)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "v6")
    else:
        audio("v6.wav")
        encode(draw, NF, "v6_video.mp4")
        mux("v6_video.mp4", "v6.wav", "reels_6_sorting.mp4")
