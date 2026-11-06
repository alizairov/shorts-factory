"""Monty Hall: simulate 1000 games, STAY vs SWITCH."""
import sys, math
import numpy as np, cairo
from common import *

GAMES = 1000
rng = np.random.default_rng(7)
car = rng.integers(0, 3, GAMES)
pick = rng.integers(0, 3, GAMES)
stay_win = (car == pick)
switch_win = ~stay_win
DEMO = 6.0                 # slow first game
SIM0, SIM1 = DEMO + 0.5, DEMO + 11.0
DUR = SIM1 + 3.5
NF = int(DUR * FPS)
PINK, LIME, CYAN = PAL[1], PAL[4], PAL[5]


def ease(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def door(ctx, x, y, w, h, open_u, content, c, hl=False):
    ctx.set_source_rgba(1, 1, 1, 0.08); ctx.rectangle(x, y, w, h); ctx.fill()
    if open_u > 0:
        label(ctx, content, x + w / 2, y + h / 2 + 22, 60, col=(1, 1, 1), alpha=open_u, shadow=0)
    ctx.set_source_rgb(*c)
    ctx.rectangle(x, y, w * (1 - 0.85 * open_u), h); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - open_u)); circle(ctx, x + w * (1 - 0.85 * open_u) - 26, y + h / 2, 10); ctx.fill()
    if hl:
        ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(8); ctx.rectangle(x - 6, y - 6, w + 12, h + 12); ctx.stroke()


def draw(ctx, fi):
    t = fi / FPS
    ctx.set_source_rgb(0.06, 0.03, 0.12); ctx.paint()
    label(ctx, "3 DOORS. 1 CAR.", W / 2, 220, 92)
    label(ctx, "SHOULD YOU SWITCH?", W / 2, 310, 66, col=LIME)
    # demo game: car behind door 2 (index 1), you pick 0, host opens 2
    dw, dh, gap = 270, 420, 45
    x0 = (W - 3 * dw - 2 * gap) / 2
    y0 = 450
    cols = [PAL[0], PAL[1], PAL[5]]
    if t < SIM0:
        contents = ["GOAT", "CAR", "GOAT"]
        for i in range(3):
            o = 0
            if i == 2:
                o = ease((t - 2.2) / 0.6)
            if i in (0, 1):
                o = ease((t - 4.4) / 0.6)
            door(ctx, x0 + i * (dw + gap), y0, dw, dh, o, contents[i], cols[i], hl=(i == 0 and t > 0.8 and t < 3.6) or (i == 1 and t >= 3.6))
        cap = ""
        if 0.8 <= t < 2.2: cap = "YOU PICK DOOR 1"
        elif 2.2 <= t < 3.6: cap = "HOST OPENS A GOAT"
        elif 3.6 <= t < 4.4: cap = "YOU SWITCH…"
        elif t >= 4.4: cap = "CAR!"
        label(ctx, cap, W / 2, 1000, 64, col=LIME if cap == "CAR!" else (1, 1, 1))
    # simulation counters
    u = (t - SIM0) / (SIM1 - SIM0)
    n = int(GAMES * min(1, max(0, u)) ** 1.6) if t >= SIM0 else 0
    if t >= SIM0 - 0.3:
        a = ease((t - SIM0 + 0.3) / 0.4)
        label(ctx, f"{n} GAMES PLAYED", W / 2, 520, 70, alpha=a)
        sw = int(switch_win[:n].sum()); st = n - sw
        bars = [("STAY", st, PINK), ("SWITCH", sw, LIME)]
        maxh = 760
        for i, (nm, v, c) in enumerate(bars):
            bx = 150 + i * 470
            h = maxh * v / GAMES
            ctx.set_source_rgba(1, 1, 1, 0.06); ctx.rectangle(bx, 700, 310, maxh); ctx.fill()
            ctx.set_source_rgb(*c); ctx.rectangle(bx, 700 + maxh - h, 310, h); ctx.fill()
            label(ctx, nm, bx + 155, 1550, 72, col=c, alpha=a)
            label(ctx, f"{v} wins", bx + 155, 1630, 48, alpha=a * 0.8)
            if n:
                label(ctx, f"{100 * v / n:.0f}%", bx + 155, 700 + maxh - h - 30, 80, alpha=a)
        # dot grid of recent games
    if t > SIM1 + 0.3:
        b = ease((t - SIM1 - 0.3) / 0.5)
        ctx.set_source_rgba(0.06, 0.03, 0.12, 0.85 * b); ctx.rectangle(0, 1690, W, 230); ctx.fill()
        label(ctx, "ALWAYS SWITCH", W / 2, 1800, 100, col=LIME, alpha=b)
        label(ctx, "YOU WIN 2 OUT OF 3", W / 2, 1880, 46, alpha=b)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=110, seed=51, vol=0.55, base=220)
    for tt in (0.8, 2.2, 3.6):
        tr.add(pluck(note(5, 261.63), 0.5, 0.18, 6), tt)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(pluck(note(st + 5, 261.63), 1.2, 0.15, 3), 4.4 + j * 0.05)
    prev = 0
    for f in range(int(SIM0 * FPS), int(SIM1 * FPS)):
        u = (f / FPS - SIM0) / (SIM1 - SIM0)
        n = int(GAMES * min(1, u) ** 1.6)
        if n // 25 != prev // 25:
            tr.add(pluck(note(int(switch_win[:max(n,1)].mean() * 10) + 3, 523.25), 0.12, 0.05, 20), f / FPS)
        prev = n
    for j, st in enumerate([0, 4, 7, 12, 16]):
        tr.add(pluck(note(st + 5, 261.63), 1.6, 0.15, 2.5), SIM1 + 0.3 + j * 0.05)
    tr.save(path, DUR)


if __name__ == "__main__":
    print("switch rate", switch_win.mean())
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "w2f")
    else:
        audio("w2f.wav"); encode(draw, NF, "w2f_v.mp4"); mux("w2f_v.mp4", "w2f.wav", "w2_6_monty.mp4")
