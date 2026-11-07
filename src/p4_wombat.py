"""Paper fact: wombats poop cubes (up to ~100 a day) — cubes don't roll away."""
import sys, math
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, SR, mux
from paper import paper, pin, rect_pts, ellipse_pts, path, TEX
from paperkit import *

DUR = 16.0
NF = int(DUR * FPS)
SKY1, SKY2 = (0.99, 0.80, 0.55), (0.96, 0.58, 0.40)
HILL1, HILL2, HILL3 = (0.86, 0.52, 0.32), (0.76, 0.42, 0.26), (0.62, 0.34, 0.20)
FUR, FUR2 = (0.55, 0.42, 0.32), (0.45, 0.33, 0.25)
POO = (0.42, 0.28, 0.18); POO_TOP = (0.55, 0.38, 0.25)
GROUND_Y = 1360
ROCK_X, ROCK_TOP = 330, 1225
T_CUBE0 = 1.0          # first cube
CUBE_DT = 0.55
N_CUBES = 5
T_100 = 5.0
T_ROLL = 9.0
T_END = 13.2


def ease_out(u):
    u = min(max(u, 0), 1); return 1 - (1 - u) ** 3


def cube(ctx, x, y, s, seed):
    """isometric-ish paper cube with its bottom-centre at (x, y)"""
    paper(ctx, rect_pts(x - s / 2, y - s, s, s), POO, seed=seed, shadow=(4, 6), rough=0.8)
    paper(ctx, [(x - s / 2, y - s), (x - s / 2 + s * 0.25, y - s - s * 0.22), (x + s / 2 + s * 0.25, y - s - s * 0.22), (x + s / 2, y - s)], POO_TOP, seed=seed + 1, shadow=(0, 0), sh_a=0, rough=0.6)
    paper(ctx, [(x + s / 2, y - s), (x + s / 2 + s * 0.25, y - s - s * 0.22), (x + s / 2 + s * 0.25, y - s * 0.22), (x + s / 2, y)], (0.35, 0.22, 0.14), seed=seed + 2, shadow=(0, 0), sh_a=0, rough=0.6)


def wombat(ctx, x, y, ts, facing=1):
    bob = 4 * math.sin(ts * 6)
    ctx.save(); ctx.translate(x, y); ctx.scale(facing, 1); ctx.translate(-x, -y)
    for lx in (-110, -40, 50, 120):
        paper(ctx, rect_pts(x + lx - 24, y - 40, 48, 60), FUR2, seed=500 + lx % 9, shadow=(4, 6), rough=0.8)
        pin(ctx, x + lx, y - 30, 6)
    paper(ctx, ellipse_pts(x, y - 120 + bob, 190, 120, 36), FUR, seed=510)
    paper(ctx, ellipse_pts(x - 40, y - 150 + bob, 110, 60, 24), (0.62, 0.48, 0.37), seed=511, shadow=(0, 0), sh_a=0, rough=1.2)
    hx, hy = x + 170, y - 150 + bob
    paper(ctx, ellipse_pts(hx, hy, 90, 75, 28), FUR, seed=512)
    for ex in (-35, 25):
        paper(ctx, [(hx + ex - 18, hy - 55), (hx + ex, hy - 100), (hx + ex + 18, hy - 55)], FUR2, seed=520 + ex, shadow=(3, 4), rough=0.6)
    paper(ctx, ellipse_pts(hx + 70, hy + 10, 36, 28, 16), (0.25, 0.18, 0.15), seed=530, shadow=(3, 4), rough=0.6)
    ctx.set_source_rgb(0.1, 0.07, 0.05); ctx.arc(hx + 25, hy - 15, 9, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(1, 1, 1); ctx.arc(hx + 28, hy - 18, 3, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(0.95, 0.5, 0.45, 0.5); ctx.arc(hx + 30, hy + 20, 12, 0, 2 * math.pi); ctx.fill()
    pin(ctx, hx - 50, hy + 20, 7)
    ctx.restore()


def background(ctx, ts):
    textured_bg(ctx, SKY1, SKY2)
    paper(ctx, ellipse_pts(250, 760, 120, 120, 36), (1.0, 0.92, 0.65), seed=5, shadow=(0, 0), sh_a=0)
    for k, (y0, col, amp) in enumerate([(1000, HILL1, 60), (1120, HILL2, 45), (1240, HILL3, 30)]):
        pts = [(x, y0 + amp * math.sin(x / (260 - k * 40) + k)) for x in range(-40, W + 80, 50)] + [(W + 40, H), (-40, H)]
        paper(ctx, pts, col, seed=10 + k, shadow=(0, -6), sh_a=0.25)
    # eucalyptus tree
    paper(ctx, [(940, GROUND_Y), (975, GROUND_Y), (965, 900), (950, 900)], (0.85, 0.80, 0.72), seed=20)
    for (dx, dy, r) in [(0, 830, 110), (-80, 880, 80), (80, 870, 85), (0, 760, 80)]:
        paper(ctx, ellipse_pts(957 + dx, dy + 6 * math.sin(ts + dx), r, r * 0.75, 22), (0.45, 0.60, 0.45), seed=21 + r, shadow=(5, 7))
    # ground
    paper(ctx, rect_pts(-20, GROUND_Y, W + 40, H - GROUND_Y + 20), (0.80, 0.62, 0.40), seed=30, shadow=(0, -6))
    for k in range(10):
        gx = 60 + k * 110
        paper(ctx, [(gx - 25, GROUND_Y + 10), (gx - 5, GROUND_Y - 50), (gx + 5, GROUND_Y + 10), (gx + 20, GROUND_Y - 40), (gx + 30, GROUND_Y + 10)], (0.70, 0.66, 0.35), seed=40 + k, shadow=(3, 4), rough=0.6)
    # flat rock
    paper(ctx, [(ROCK_X - 190, GROUND_Y + 10), (ROCK_X - 160, ROCK_TOP), (ROCK_X + 170, ROCK_TOP - 5), (ROCK_X + 200, GROUND_Y + 10)], (0.62, 0.60, 0.58), seed=50, shadow=(6, 9))


def cube_positions():
    pos = []
    for k in range(N_CUBES):
        pos.append((ROCK_X - 130 + k * 66 + (k % 2) * 6, ROCK_TOP - (k % 2) * 4))
    return pos


POS = cube_positions()


def draw(ctx, fi):
    t = fi / FPS; ts = stop(t)
    background(ctx, ts)
    # wombat walks in from left at t<1 and stands left of rock, rear towards rock
    wx = 730 + (1 - min(1, ts / 0.8)) * 80
    if ts > T_END - 1.4:
        wx = 300 - 500 * ease((ts - T_END + 1.4) / 1.4)
    # cubes
    for k in range(N_CUBES):
        tk = T_CUBE0 + k * CUBE_DT
        if ts < tk: continue
        u = ease_out((ts - tk) / 0.35)
        x0, y0 = wx - 250, 1170     # pops out of the rear (wombat faces left... rear on right side)
        x1, y1 = POS[k]
        x = x0 + (x1 - x0) * u
        y = y0 + (y1 - y0) * u - 140 * math.sin(math.pi * u)
        cube(ctx, x, y, 62, 600 + k * 5)
    # rolling ball vs cube demo
    if ts >= T_ROLL:
        k = ts - T_ROLL
        # ball dropped on the rock rolls off to the right and away
        bx = ROCK_X - 150 - 120 * ease((k - 0.5) / 1.6) if k > 0.5 else ROCK_X - 150
        by = (ROCK_TOP - 34 - 300 * (1 - min(1, k / 0.5)) ** 2) if k <= 0.5 else (ROCK_TOP - 34 + (GROUND_Y - ROCK_TOP) * ease((ROCK_X - 170 - bx) / 60) if bx < ROCK_X - 170 else ROCK_TOP - 34)
        ang = (bx - ROCK_X) / 34
        paper(ctx, ellipse_pts(bx, by, 34, 34, 20), (0.36, 0.22, 0.14), seed=700, shadow=(4, 6), rough=0.6)
        ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(4)
        ctx.move_to(bx, by); ctx.line_to(bx + 28 * math.cos(ang), by + 28 * math.sin(ang)); ctx.stroke()
        if k > 1.2:
            tag(ctx, "✗", max(bx, 70), by - 80, 56, col=(1, 1, 1), bg=(0.85, 0.32, 0.30), seed=701, a=ease((k - 1.2) / 0.3))
            tag(ctx, "✓", ROCK_X + 20, ROCK_TOP - 160, 56, col=(1, 1, 1), bg=(0.36, 0.66, 0.38), seed=702, a=ease((k - 1.5) / 0.3))
    ctx.save(); ctx.translate(wx, GROUND_Y + 10); ctx.scale(1.2, 1.2); ctx.translate(-wx, -(GROUND_Y + 10))
    wombat(ctx, wx, GROUND_Y + 10, ts, facing=1)
    ctx.restore()
    # text — top zone, very short
    if ts < T_100:
        banner(ctx, "THIS ANIMAL", 300, 84, seed=1)
        banner(ctx, "POOPS CUBES", 430, 96, col=(0.55, 0.32, 0.18), seed=2)
    elif ts < T_ROLL:
        banner(ctx, "UP TO 100", 320, 110, col=(0.55, 0.32, 0.18), seed=3, a=ease((ts - T_100) / 0.25))
        banner(ctx, "A DAY", 460, 80, seed=4, a=ease((ts - T_100 - 0.3) / 0.25))
    elif ts < T_END:
        banner(ctx, "CUBES DON'T", 300, 90, seed=5, a=ease((ts - T_ROLL) / 0.25))
        banner(ctx, "ROLL AWAY", 430, 96, col=(0.55, 0.32, 0.18), seed=6, a=ease((ts - T_ROLL - 0.3) / 0.25))
    else:
        banner(ctx, "WOMBATS.", 330, 120, col=(0.55, 0.32, 0.18), seed=7, a=ease((ts - T_END) / 0.25))
    vignette(ctx, 0.28)


def audio(path):
    tr = Track(DUR)
    ambience(tr, DUR, 0.025)
    # crickets / evening chirps
    for k in range(30):
        tt = 0.2 + k * 0.5 + (k % 3) * 0.07
        m = np.arange(int(SR * 0.05)) / SR
        tr.add(np.sin(2 * np.pi * 4200 * m) * np.exp(-m * 60) * 0.015, tt)
    musicbox(tr, DUR, mel=(0, 4, 7, 4, 5, 2, 4, 0), gap=0.7, vol=0.06)
    for k in range(N_CUBES):
        tk = T_CUBE0 + k * CUBE_DT
        tr.add(plop(320 + k * 20, 0.18), tk)
        tr.add(tap(240, 0.22), tk + 0.35)
    tr.add(pluck(note(10, 261.63), 1.2, 0.12, 3), T_100)
    tr.add(tap(300, 0.2), T_ROLL + 0.5)
    rr = soft_noise(1.8, 60, 0.08)
    tr.add(rr * np.sin(np.linspace(0, np.pi, len(rr))), T_ROLL + 0.5)
    tr.add(pluck(note(2, 392), 0.6, 0.12, 5), T_ROLL + 1.2)
    tr.add(pluck(note(9, 392), 0.6, 0.12, 5), T_ROLL + 1.5)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(pluck(note(st + 5, 261.63), 1.4, 0.09, 3), T_END + j * 0.07)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "p4")
    else:
        audio("p4.wav"); encode(draw, NF, "p4_v.mp4"); mux("p4_v.mp4", "p4.wav", "p4_wombat.mp4")
