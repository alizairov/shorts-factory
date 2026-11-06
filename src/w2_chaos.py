"""Chaos: 3 double pendulums starting 0.001 rad apart."""
import sys, math
import numpy as np, cairo
from common import *

L1 = L2 = 1.0
M1 = M2 = 1.0
GV = 9.81
PX = 210          # px per metre
CX, CY = W / 2, 820
DUR = 24.0
NF = int(DUR * FPS)
N = 3
COLS = [PAL[1], PAL[4], PAL[5]]
DIFF = math.radians(0.001)


def deriv(s):
    t1, w1, t2, w2 = s
    d = t2 - t1
    den1 = (M1 + M2) * L1 - M2 * L1 * math.cos(d) ** 2
    a1 = (M2 * L1 * w1 * w1 * math.sin(d) * math.cos(d) + M2 * GV * math.sin(t2) * math.cos(d)
          + M2 * L2 * w2 * w2 * math.sin(d) - (M1 + M2) * GV * math.sin(t1)) / den1
    den2 = (L2 / L1) * den1
    a2 = (-M2 * L2 * w2 * w2 * math.sin(d) * math.cos(d) + (M1 + M2) * GV * math.sin(t1) * math.cos(d)
          - (M1 + M2) * L1 * w1 * w1 * math.sin(d) - (M1 + M2) * GV * math.sin(t2)) / den2
    return np.array([w1, a1, w2, a2])


def rk4(s, h):
    k1 = deriv(s); k2 = deriv(s + h / 2 * k1); k3 = deriv(s + h / 2 * k2); k4 = deriv(s + h * k3)
    return s + h / 6 * (k1 + 2 * k2 + 2 * k3 + k4)


def simulate():
    S = [np.array([math.radians(120) + i * DIFF, 0, math.radians(-10), 0]) for i in range(N)]
    out = []
    sub = 20
    for f in range(NF):
        for _ in range(sub):
            S = [rk4(s, 1 / FPS / sub) for s in S]
        out.append([s.copy() for s in S])
    return out


def pts(s):
    t1, _, t2, _ = s
    x1 = CX + PX * L1 * math.sin(t1); y1 = CY + PX * L1 * math.cos(t1)
    x2 = x1 + PX * L2 * math.sin(t2); y2 = y1 + PX * L2 * math.cos(t2)
    return (x1, y1), (x2, y2)


def ease(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def make(states):
    tips = [[pts(s)[1] for s in st] for st in states]

    def draw(ctx, fi):
        t = fi / FPS
        ctx.set_source_rgb(0.05, 0.03, 0.11); ctx.paint()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
        # trails
        TL = 90
        for i in range(N):
            for k in range(max(1, fi - TL), fi + 1):
                a = (k - fi + TL) / TL
                ctx.set_source_rgba(*COLS[i], 0.85 * a)
                ctx.set_line_width(2 + 5 * a)
                ctx.move_to(*tips[k - 1][i]); ctx.line_to(*tips[k][i]); ctx.stroke()
        for i in range(N):
            (x1, y1), (x2, y2) = pts(states[fi][i])
            ctx.set_source_rgba(1, 1, 1, 0.75); ctx.set_line_width(7)
            ctx.move_to(CX, CY); ctx.line_to(x1, y1); ctx.line_to(x2, y2); ctx.stroke()
            glossy_ball(ctx, x1, y1, 14, (0.9, 0.9, 1), glow=False)
            glossy_ball(ctx, x2, y2, 22, COLS[i])
        glossy_ball(ctx, CX, CY, 10, (1, 1, 1), glow=False)
        label(ctx, "3 PENDULUMS", W / 2, 240, 88)
        label(ctx, "STARTED 0.001° APART", W / 2, 330, 60, col=grad(0.62))
        # divergence meter
        d = max(abs(states[fi][i][2] - states[fi][0][2]) for i in range(N))
        sync = d < 0.05
        txt = "PERFECTLY IN SYNC" if sync else "TOTAL CHAOS"
        col = (1, 1, 1) if sync else PAL[1]
        label(ctx, txt, W / 2, 1640, 76, col=col)
        label(ctx, f"{t:.1f}s", W / 2, 1740, 54, alpha=0.6)
        if t > DUR - 4:
            a = ease((t - DUR + 4) / 0.5)
            label(ctx, "THIS IS THE BUTTERFLY EFFECT", W / 2, 1860, 46, col=grad(0.18), alpha=a)
    return draw


def audio(states, path):
    tr = Track(DUR)
    music(tr, DUR, bpm=88, seed=31, vol=0.6, base=196)
    # each pendulum pings when its lower arm swings through the bottom
    for i in range(N):
        prev = None
        for f, st in enumerate(states):
            s = math.sin(st[i][2])
            if prev is not None and (prev < 0) != (s < 0) and math.cos(st[i][2]) > 0:
                tr.add(pluck(note(i * 2 + 5, 261.63), 0.4, 0.12, 8), f / FPS)
            prev = s
    tr.save(path, DUR)


if __name__ == "__main__":
    states = simulate()
    # print when they diverge
    for f in range(0, NF, 30):
        d = max(abs(states[f][i][2] - states[f][0][2]) for i in range(N))
        if d > 0.05:
            print("diverge at", f / FPS); break
    draw = make(states)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "w2d")
    else:
        audio(states, "w2d.wav"); encode(draw, NF, "w2d_v.mp4"); mux("w2d_v.mp4", "w2d.wav", "w2_4_chaos.mp4")
