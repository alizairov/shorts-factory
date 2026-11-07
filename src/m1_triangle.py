"""Fact story (π-video format): why a triangle's angles always add to 180° — shown by tearing off the corners."""
import sys, math
import numpy as np, cairo
from story import *

DUR = 16.0
NF = int(DUR * FPS)
COLS = [PINK, YEL, CYAN]
LINE_Y = 1420
# triangle shapes to morph between (vertices), loops back to the first
SHAPES = [[(200, 1050), (880, 1050), (420, 640)], [(160, 1050), (920, 1050), (780, 700)], [(260, 1050), (820, 1050), (540, 560)]]
T_CUT, T_MOVE, T_DONE, T_MORPH = 1.2, 2.2, 5.2, 7.5


def tri_at(t):
    if t < T_MORPH: return SHAPES[0]
    k = (t - T_MORPH) / 2.6
    i = int(k) % len(SHAPES); j = (i + 1) % len(SHAPES)
    u = ease(min(1, (k - int(k)) / 0.5))
    return [(a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u) for a, b in zip(SHAPES[i], SHAPES[j])]


def angles(P):
    out = []
    for i in range(3):
        a, b, c = P[i], P[(i + 1) % 3], P[(i + 2) % 3]
        a1 = math.atan2(b[1] - a[1], b[0] - a[0]); a2 = math.atan2(c[1] - a[1], c[0] - a[0])
        d = (a2 - a1) % (2 * math.pi)
        if d > math.pi: a1, a2, d = a2, a1, 2 * math.pi - d
        out.append((a1, d))
    return out


def wedge(ctx, x, y, r, a0, d, col, alpha=1.0):
    ctx.move_to(x, y); ctx.arc(x, y, r, a0, a0 + d); ctx.close_path()
    ctx.set_source_rgba(*col, alpha); ctx.fill()


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx)
    ctx.set_source_rgba(1, 1, 1, 0.04); ctx.set_line_width(1)
    for g in range(0, W, 60): ctx.move_to(g, 0); ctx.line_to(g, H); ctx.stroke()
    for g in range(0, H, 60): ctx.move_to(0, g); ctx.line_to(W, g); ctx.stroke()
    P = tri_at(t)
    ang = angles(P)
    R = 110
    # triangle outline
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(6); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*P[0]); ctx.line_to(*P[1]); ctx.line_to(*P[2]); ctx.close_path(); ctx.stroke()
    # target: half-circle on the straight line, wedges laid side by side
    cx = W / 2
    ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(5)
    ctx.move_to(120, LINE_Y); ctx.line_to(W - 120, LINE_Y); ctx.stroke()
    start = math.pi
    move = ease((t - T_MOVE) / 2.2) if t < T_MORPH else 1.0
    for i, (a0, d) in enumerate(ang):
        x, y = P[i]
        # wedge in place (fades once moved away)
        wedge(ctx, x, y, R, a0, d, COLS[i], 0.35 if t >= T_CUT else ease(t / 0.4) * 0.95)
        if t < T_CUT:
            continue
        # torn copy travels to the line; its arc rotates to sit next to the previous one
        tx, ty = x + (cx - x) * move, y + (LINE_Y - y) * move
        ra = a0 + (start - a0) * move
        lift = 1 + 0.12 * math.sin(math.pi * move)
        wedge(ctx, tx, ty, R * lift, ra, d, COLS[i])
        start += d
    # 180° arc check
    if t > T_DONE:
        a = ease((t - T_DONE) / 0.5)
        ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(6)
        ctx.arc(cx, LINE_Y, R + 30, math.pi, 2 * math.pi); ctx.stroke()
        label(ctx, "180°", cx, LINE_Y + 110, int(110 * pop((t - T_DONE) / 0.4)), col=YEL, alpha=a)
    # minimal text
    if t < T_DONE:
        pill(ctx, "WHY 180°?", 330, 120)
    else:
        pill(ctx, "ANY TRIANGLE.", 300, 80, alpha=ease((t - T_DONE - 1.5) / 0.3))
        pill(ctx, "ALWAYS 180°.", 420, 96, col=YEL, alpha=ease((t - T_MORPH) / 0.3))
    progress(ctx, t, DUR)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=88, seed=77, vol=0.35, base=196)
    for i in range(3):
        tr.add(soft_noise(0.18, 6, 0.08) if False else pluck(note(4 + i * 2, 523.25), 0.4, 0.10, 8), T_CUT + i * 0.15)
    for i in range(3):
        tr.add(pluck(note(7 + i * 2, 392), 0.6, 0.12, 6), T_MOVE + 1.4 + i * 0.25)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(pluck(note(st + 5, 261.63), 1.4, 0.12, 3), T_DONE + j * 0.06)
    for k in range(3):
        tr.add(ding(9 + k, 0.12), T_MORPH + 0.5 + k * 2.6)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "m1")
    else:
        audio("m1.wav"); encode(draw, NF, "m1_v.mp4"); mux("m1_v.mp4", "m1.wav", "m1_triangle.mp4")
