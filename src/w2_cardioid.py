"""Times tables on a circle: connect n -> k*n (mod N) while k sweeps 2..10."""
import sys, math
import numpy as np, cairo
from common import *

N = 240
R = 450
CX, CY = W / 2, 1000
DUR = 24.0
NF = int(DUR * FPS)
K0, K1 = 2.0, 10.0
HOLDS = [2, 3, 4, 5, 10]


def kval(t):
    # glide with gentle pauses near the integer "named" shapes
    u = t / DUR
    k = K0 + (K1 - K0) * u
    nearest = round(k)
    if nearest in HOLDS:
        d = k - nearest
        k = nearest + d * min(1, abs(d) / 0.35) ** 2 * (1 if d >= 0 else 1)
    return k


NAMES = {2: "CARDIOID", 3: "NEPHROID", 4: "3 PETALS", 5: "4 PETALS", 10: "9 PETALS"}


def draw(ctx, fi):
    t = fi / FPS
    k = kval(t)
    ctx.set_source_rgb(0.04, 0.02, 0.09); ctx.paint()
    ctx.set_operator(cairo.OPERATOR_ADD)
    ctx.set_line_width(2.0)
    for n in range(N):
        a1 = 2 * math.pi * n / N - math.pi / 2
        a2 = 2 * math.pi * (k * n % N) / N - math.pi / 2
        c = grad(n / N)
        ctx.set_source_rgba(*c, 0.55)
        ctx.move_to(CX + R * math.cos(a1), CY + R * math.sin(a1))
        ctx.line_to(CX + R * math.cos(a2), CY + R * math.sin(a2))
        ctx.stroke()
    ctx.set_operator(cairo.OPERATOR_OVER)
    ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(3); circle(ctx, CX, CY, R); ctx.stroke()
    label(ctx, "JUST MULTIPLY", W / 2, 230, 92)
    label(ctx, "POINTS ON A CIRCLE", W / 2, 320, 64, col=grad(0.62))
    label(ctx, f"× {k:.2f}", W / 2, 1640, 120, col=grad((k - 2) / 8))
    nk = round(k)
    if abs(k - nk) < 0.03 and nk in NAMES:
        label(ctx, NAMES[nk], W / 2, 1750, 58, alpha=0.85)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=84, seed=41, vol=0.65, base=196)
    last = None
    for f in range(NF):
        nk = round(kval(f / FPS))
        if abs(kval(f / FPS) - nk) < 0.03 and nk != last and nk in NAMES:
            for j, st in enumerate([0, 4, 7]):
                tr.add(pluck(note(st + nk, 261.63), 1.4, 0.16, 3), f / FPS + j * 0.05)
            last = nk
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "w2e")
    else:
        audio("w2e.wav"); encode(draw, NF, "w2e_v.mp4"); mux("w2e_v.mp4", "w2e.wav", "w2_5_cardioid.mp4")
