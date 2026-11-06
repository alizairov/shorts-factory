"""1/2 + 1/4 + 1/8 + ... = 1, shown by filling a square."""
import sys, math
from fractions import Fraction
import numpy as np, cairo
from common import *

S = 900
X0, Y0 = (W - S) / 2, 560
STEPS = 14
times = []
t = 1.6
for k in range(STEPS):
    times.append(t)
    t += max(0.42, 1.0 - k * 0.09)
T_END = t
DUR = T_END + 3.2
NF = int(DUR * FPS)

# rectangles: alternate vertical / horizontal halving of the remaining area
rects = []
x, y, w, h = X0, Y0, S, S
for k in range(STEPS):
    if k % 2 == 0:
        rects.append((x, y, w / 2, h)); x += w / 2; w /= 2
    else:
        rects.append((x, y, w, h / 2)); y += h / 2; h /= 2


def ease(u):
    u = min(max(u, 0), 1); return 1 - (1 - u) ** 3


def draw(ctx, fi):
    t = fi / FPS
    ctx.set_source_rgb(0.06, 0.03, 0.12); ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.06); ctx.rectangle(X0, Y0, S, S); ctx.fill()
    n = sum(1 for tt in times if t >= tt)
    for k in range(n):
        rx, ry, rw, rh = rects[k]
        u = ease((t - times[k]) / 0.35)
        c = grad(k / 9)
        ctx.set_source_rgb(*c)
        if k % 2 == 0:
            ctx.rectangle(rx + 3, ry + 3, (rw - 6) * u, rh - 6)
        else:
            ctx.rectangle(rx + 3, ry + 3, rw - 6, (rh - 6) * u)
        ctx.fill()
        if k < 6:
            fs = [110, 90, 70, 54, 40, 30][k]
            label(ctx, f"1/{2 ** (k + 1)}", rx + rw / 2, ry + rh / 2 + fs * 0.35, fs, col=(0.06, 0.03, 0.12), alpha=u, shadow=0)
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(6); ctx.rectangle(X0, Y0, S, S); ctx.stroke()
    label(ctx, "1", X0 - 40, Y0 + S / 2 + 20, 60, alpha=0.6)
    label(ctx, "1", X0 + S / 2, Y0 + S + 75, 60, alpha=0.6)
    # formula
    terms = ["1/2", "1/4", "1/8", "1/16", "1/32"]
    shown = " + ".join(terms[:min(n, 5)]) + (" + …" if n > 5 else "")
    if n:
        label(ctx, "DOES IT EVER REACH 1?", W / 2, 240, 78)
        label(ctx, shown, W / 2, 370, 58 if n < 4 else 50, col=grad(0.45))
    total = 1 - 0.5 ** n
    if n and t <= T_END:
        s = f"{total:.{min(max(2, n // 1), 8)}f}".rstrip("0") if n < STEPS else "0.99993896…"
        label(ctx, s, W / 2, 1640, 110, col=grad(0.62))
    elif not n:
        label(ctx, "ADD HALF, THEN", W / 2, 330, 80)
        label(ctx, "HALF OF WHAT'S LEFT…", W / 2, 420, 64, col=grad(0.62))
    if t > T_END:
        a = ease((t - T_END) / 0.5)
        ctx.set_source_rgba(0.06, 0.03, 0.12, 0.6 * a); ctx.rectangle(0, 1520, W, 260); ctx.fill()
        label(ctx, "= 1", W / 2, 1700, int(170 * (1 + 0.2 * (1 - a))), col=grad(0.62), alpha=a)
        label(ctx, "INFINITE STEPS. FINITE ANSWER.", W / 2, 1830, 46, alpha=a)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=100, seed=12, vol=0.6, base=220)
    for k, tt in enumerate(times):
        tr.add(pluck(note(k, 261.63), 0.8, 0.22, 5), tt)
    for k, st in enumerate([0, 4, 7, 12, 16]):
        tr.add(pluck(note(st + 5, 261.63), 1.8, 0.14, 2.5), T_END + k * 0.05)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "w2b")
    else:
        audio("w2b.wav"); encode(draw, NF, "w2b_v.mp4"); mux("w2b_v.mp4", "w2b.wav", "w2_2_series.mp4")
