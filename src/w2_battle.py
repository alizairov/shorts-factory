"""Pink vs Lime: two balls fight for territory on a tile grid."""
import sys, math
import numpy as np, cairo
from common import *

GN = 32
TS = 30
GX0 = (W - GN * TS) / 2
GY0 = 520
PINK, LIME = PAL[1], PAL[4]
BR = 18
SPD = 1100
SUB = 6
DUR = 22.0
NF = int(DUR * FPS)


def simulate(seed):
    rng = np.random.default_rng(seed)
    grid = np.zeros((GN, GN), int)
    grid[:, GN // 2:] = 1  # 0 pink owns left, 1 lime owns right
    # ball of team k lives in opposite territory
    balls = []
    for team, cx in ((0, GN * 0.25), (1, GN * 0.75), (0, GN * 0.2), (1, GN * 0.8)):
        a = rng.uniform(0, 2 * math.pi)
        balls.append(dict(team=team, p=np.array([cx * TS, GN / 2 * TS + rng.uniform(-80, 80)]),
                          v=SPD * np.array([math.cos(a), math.sin(a)])))
    frames, hits = [], []
    dt = 1 / FPS / SUB
    t = 0
    for fi in range(NF):
        for _ in range(SUB):
            t += dt
            for b in balls:
                for ax in (0, 1):
                    b["p"][ax] += b["v"][ax] * dt
                    if b["p"][ax] < BR:
                        b["p"][ax] = BR; b["v"][ax] = abs(b["v"][ax])
                    if b["p"][ax] > GN * TS - BR:
                        b["p"][ax] = GN * TS - BR; b["v"][ax] = -abs(b["v"][ax])
                    # tile collision on this axis
                    lead = b["p"][ax] + math.copysign(BR, b["v"][ax])
                    other = b["p"][1 - ax]
                    i = int(lead // TS)
                    for off in (-BR * 0.7, 0, BR * 0.7):
                        j = int((other + off) // TS)
                        if 0 <= i < GN and 0 <= j < GN:
                            gx, gy = (i, j) if ax == 0 else (j, i)
                            if grid[gy, gx] == 1 - b["team"]:
                                grid[gy, gx] = b["team"]
                                b["v"][ax] *= -1
                                b["p"][ax] += b["v"][ax] * dt * 2
                                hits.append((t, b["team"], gx, gy))
                                break
                ang = math.atan2(b["v"][1], b["v"][0]) + rng.uniform(-0.002, 0.002)
                b["v"] = SPD * np.array([math.cos(ang), math.sin(ang)])
        frames.append(dict(grid=grid.copy(), balls=[(b["team"], b["p"].copy()) for b in balls]))
    return frames, hits


def make(frames, hits):
    flash = {}
    for (t, team, gx, gy) in hits:
        flash.setdefault(int(t * FPS), []).append((gx, gy))

    def draw(ctx, fi):
        fr = frames[min(fi, NF - 61)]
        ctx.set_source_rgb(0.06, 0.03, 0.12); ctx.paint()
        g = fr["grid"]
        pink_n = int((g == 0).sum()); lime_n = GN * GN - pink_n
        # board
        for y in range(GN):
            for x in range(GN):
                c = PINK if g[y, x] == 0 else LIME
                ctx.set_source_rgb(*c)
                ctx.rectangle(GX0 + x * TS + 1.5, GY0 + y * TS + 1.5, TS - 3, TS - 3); ctx.fill()
        for k in range(4):
            for (gx, gy) in (flash.get(fi - k, []) if fi < NF - 60 else []):
                ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - k / 4))
                ctx.rectangle(GX0 + gx * TS, GY0 + gy * TS, TS, TS); ctx.fill()
        for team, p in fr["balls"]:
            c = PINK if team == 0 else LIME
            ctx.set_source_rgba(0, 0, 0, 0.3); circle(ctx, GX0 + p[0] + 3, GY0 + p[1] + 5, BR); ctx.fill()
            glossy_ball(ctx, GX0 + p[0], GY0 + p[1], BR, lighten(c, 0.3), glow=False)
            ctx.set_source_rgb(0.06, 0.03, 0.12); ctx.set_line_width(5); circle(ctx, GX0 + p[0], GY0 + p[1], BR); ctx.stroke()
        # score bar
        tot = GN * GN
        bx, by, bw, bh = 90, 1560, W - 180, 54
        ctx.set_source_rgb(*LIME); ctx.rectangle(bx, by, bw, bh); ctx.fill()
        ctx.set_source_rgb(*PINK); ctx.rectangle(bx, by, bw * pink_n / tot, bh); ctx.fill()
        label(ctx, str(pink_n), bx, by + 130, 80, col=PINK, anchor="l")
        label(ctx, str(lime_n), bx + bw, by + 130, 80, col=LIME, anchor="r")
        label(ctx, "PINK", bx, by - 24, 46, col=PINK, anchor="l")
        label(ctx, "LIME", bx + bw, by - 24, 46, col=LIME, anchor="r")
        label(ctx, "PICK A SIDE", W / 2, 300, 100)
        label(ctx, "WHO OWNS MORE AT THE END?", W / 2, 390, 48, col=grad(0.0))
        if fi > NF - 60:
            a = min(1, (fi - NF + 60) / 12)
            win = "PINK WINS" if pink_n > lime_n else ("LIME WINS" if lime_n > pink_n else "IT'S A TIE!")
            ctx.set_source_rgba(0.06, 0.03, 0.12, 0.75 * a); ctx.rectangle(0, 860, W, 260); ctx.fill()
            label(ctx, win, W / 2, 1030, 130, col=PINK if pink_n > lime_n else (LIME if lime_n > pink_n else (1, 1, 1)), alpha=a)
    return draw


def audio(hits, path):
    tr = Track(DUR)
    music(tr, DUR, bpm=124, seed=8, vol=0.5, base=220)
    for (t, team, gx, gy) in hits:
        if t > (NF - 61) / FPS:
            continue
        tr.add(pluck(note(gy % 10 + (0 if team == 0 else 3), 392 if team == 0 else 330), 0.18, 0.06, 16), t)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(pluck(note(st + 5, 261.63), 1.4, 0.16, 3), (NF - 60) / FPS + j * 0.05)
    tr.save(path, DUR)


if __name__ == "__main__":
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    if sys.argv[1] == "tune":
        for s in range(1, 9):
            f, h = simulate(s); g = f[-1]["grid"]; print(s, (g == 0).sum(), len(h))
        sys.exit()
    frames, hits = simulate(seed)
    draw = make(frames, hits)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[3:]], "w2a")
    else:
        audio(hits, "w2a.wav"); encode(draw, NF, "w2a_v.mp4"); mux("w2a_v.mp4", "w2a.wav", "w2_1_battle.mp4")
