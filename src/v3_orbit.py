import sys, math
import numpy as np, cairo
from common import *

T = 20.0            # perfect loop: everything realigns at T
N = 28
CX, CY = W / 2, H / 2
R_IN, R_OUT = 70, 480
radii = np.linspace(R_IN, R_OUT, N)
cycles = np.arange(1, N + 1)          # ring i makes i+1 turns in T
NF = int(T * FPS)


def ang(i, t):
    return -math.pi / 2 + 2 * math.pi * cycles[i] * t / T


def pos(i, t):
    a = ang(i, t)
    return CX + radii[i] * math.cos(a), CY + radii[i] * math.sin(a)


def draw(ctx, fi):
    t = fi / FPS
    g = cairo.RadialGradient(CX, CY, 0, CX, CY, 1100)
    g.add_color_stop_rgb(0, 0.09, 0.05, 0.18)
    g.add_color_stop_rgb(1, 0.02, 0.01, 0.05)
    ctx.set_source(g)
    ctx.paint()
    # faint orbit guides
    for i in range(N):
        ctx.set_source_rgba(*grad(i / N), 0.10)
        ctx.set_line_width(2)
        circle(ctx, CX, CY, radii[i])
        ctx.stroke()
    # trails (arcs behind each ball)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(N):
        c = grad(i / N)
        a1 = ang(i, t)
        span = min(1.4, 0.06 * cycles[i] + 0.25)
        steps = 10
        for k in range(steps):
            s0 = a1 - span * (k + 1) / steps
            s1 = a1 - span * k / steps
            ctx.set_source_rgba(*c, 0.55 * (1 - k / steps))
            ctx.set_line_width(14 * (1 - k / steps) + 2)
            ctx.arc(CX, CY, radii[i], s0, s1)
            ctx.stroke()
    # connecting curve through all balls
    pts = [pos(i, t) for i in range(N)]
    for i in range(N - 1):
        ctx.set_source_rgba(*grad(i / N), 0.9)
        ctx.set_line_width(4)
        ctx.move_to(*pts[i])
        ctx.line_to(*pts[i + 1])
        ctx.stroke()
    # flash when passing top
    for i in range(N):
        ph = (cycles[i] * t / T) % 1.0
        d = min(ph, 1 - ph) * T / cycles[i]   # seconds from top
        fl = max(0, 1 - d / 0.12) if ph < 0.5 else 0
        x, y = pts[i]
        c = grad(i / N)
        if fl > 0:
            ctx.set_source_rgba(*lighten(c, 0.5), 0.6 * fl)
            circle(ctx, x, y, 16 + 10 * fl)
            ctx.fill()
        glossy_ball(ctx, x, y, 13 + 3 * fl, c)
    # core
    glossy_ball(ctx, CX, CY, 26, (1, 1, 1), glow=False)


def audio(path):
    tr = Track(T)
    for i in range(N):
        for k in range(cycles[i] + 1):
            tt = k * T / cycles[i]
            if tt <= T:
                tr.add(pluck(note(i, 196.0), 0.6, 0.22, 7), tt)
    tr.save(path, T)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "v3")
    else:
        audio("v3.wav")
        encode(draw, NF, "v3_video.mp4")
        mux("v3_video.mp4", "v3.wav", "reels_2_orbit.mp4")
