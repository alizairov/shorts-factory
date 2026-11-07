"""Paper fact: is it a berry? Banana yes, strawberry no."""
import sys, math
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, SR, mux
from paper import paper, pin, rect_pts, ellipse_pts, path, TEX
from paperkit import *

DUR = 17.0
NF = int(DUR * FPS)
WALLC = (0.98, 0.86, 0.72); WALL2 = (0.95, 0.80, 0.64)
TABLE = (0.70, 0.48, 0.30); TABLE2 = (0.62, 0.41, 0.25)
GREENT = (0.36, 0.66, 0.38); REDT = (0.85, 0.32, 0.30)
BASKET = (0.80, 0.60, 0.35); BASKET2 = (0.70, 0.50, 0.28)
BL_X, BR_X, B_Y = 270, 810, 1230        # basket centres (BERRY left, NOT right)
HOLD_Y = 760

FRUITS = [  # name, is_berry
    ("STRAWBERRY", False), ("BANANA", True), ("TOMATO", True), ("RASPBERRY", False), ("GRAPES", True), ("WATERMELON", True)]
T0, SLOT = 0.0, 2.15
T_END = T0 + SLOT * len(FRUITS)
GUESS_FRAC = 0.55    # fraction of slot the fruit hovers before flying


def fruit_state(i, t):
    """returns (x, y, scale, rot) or None; plus landed flag"""
    ts0 = T0 + i * SLOT
    if t < ts0 - 0.4: return None
    name, berry = FRUITS[i]
    kk = sum(1 for j in range(i) if FRUITS[j][1] == berry)
    tx = (BL_X if berry else BR_X) + [-120, 120, 0, -60][kk % 4]
    land_y = B_Y - 115 - (25 if kk >= 2 else 0)
    if t < ts0:
        u = ease((t - ts0 + 0.4) / 0.4)
        return W / 2, -150 + (HOLD_Y + 150) * u, 1.45, 0, False
    th = ts0 + SLOT * GUESS_FRAC
    if t < th:
        return W / 2, HOLD_Y + 10 * math.sin((t - ts0) * 5), 1.45, 0.08 * math.sin((t - ts0) * 4), False
    u = min(1, (t - th) / 0.6)
    x = W / 2 + (tx - W / 2) * u
    y = HOLD_Y + (land_y - HOLD_Y) * u - 260 * math.sin(math.pi * u)
    return x, y, 1.45 - 0.75 * u, u * (1 if berry else -1) * 0.5, u >= 1


def draw_fruit(ctx, name, x, y, s, rot, seed):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(rot)
    if name == "BANANA":
        outer = [(-150 + 300 * k / 20, 40 - 90 * math.sin(math.pi * k / 20)) for k in range(21)]
        inner = [(150 - 300 * k / 20, 40 - 50 * math.sin(math.pi * (20 - k) / 20) + 30) for k in range(21)]
        paper(ctx, outer + inner, (0.98, 0.84, 0.30), seed=seed)
        paper(ctx, rect_pts(-170, 40, 30, 22), (0.45, 0.33, 0.18), seed=seed + 1, rough=0.6)
        paper(ctx, rect_pts(146, 50, 18, 18), (0.30, 0.22, 0.12), seed=seed + 2, rough=0.6)
    elif name == "STRAWBERRY":
        pts = [(0, 120)] + [(115 * math.cos(a), 115 * math.sin(a) * 0.8 - 20) for a in np.linspace(math.pi * 1.0, math.pi * 2.0, 18)]
        pts = [(0, 125), (-95, 10)] + pts[1:] + [(95, 10)]
        paper(ctx, pts, (0.92, 0.22, 0.25), seed=seed)
        for k in range(14):
            sx, sy = -60 + (k * 37) % 120, -30 + (k * 53) % 120 * 0.8
            if abs(sx) < 75 - sy * 0.5:
                ctx.set_source_rgb(0.98, 0.88, 0.45); ctx.save(); ctx.translate(sx, sy); ctx.scale(1, 1.6); ctx.arc(0, 0, 4, 0, 2 * math.pi); ctx.fill(); ctx.restore()
        for k in range(5):
            a = math.pi * (1.1 + k * 0.2)
            paper(ctx, [(0, -95), (75 * math.cos(a), -95 + 30 * math.sin(a) - 10), (20 * math.cos(a + 0.3), -105)], (0.30, 0.62, 0.32), seed=seed + 5 + k, shadow=(3, 4), rough=0.8)
    elif name == "TOMATO":
        paper(ctx, ellipse_pts(0, 0, 115, 100, 36), (0.90, 0.20, 0.18), seed=seed)
        for k in range(5):
            a = -math.pi / 2 + k * 2 * math.pi / 5
            paper(ctx, [(0, -85), (55 * math.cos(a), -85 + 25 * math.sin(a)), (12 * math.cos(a + 0.5), -88 + 6 * math.sin(a + 0.5))], (0.30, 0.60, 0.30), seed=seed + 3 + k, shadow=(2, 3), rough=0.6)
    elif name == "RASPBERRY":
        for row in range(5):
            for c in range(5 - abs(row - 2) + 2):
                bx = (c - (5 - abs(row - 2) + 1) / 2) * 34
                by = -60 + row * 32
                paper(ctx, ellipse_pts(bx, by, 22, 22, 14), (0.86, 0.20, 0.42) if (row + c) % 2 else (0.78, 0.16, 0.36), seed=seed + row * 7 + c, shadow=(2, 3), rough=0.5)
        paper(ctx, [(-40, -95), (0, -120), (40, -95), (0, -85)], (0.30, 0.60, 0.30), seed=seed + 50, shadow=(2, 3), rough=0.6)
    elif name == "GRAPES":
        paper(ctx, rect_pts(-5, -130, 10, 40), (0.45, 0.33, 0.18), seed=seed, rough=0.5)
        for row in range(5):
            n = 5 - row
            for c in range(n):
                gx = (c - (n - 1) / 2) * 46
                gy = -80 + row * 42
                paper(ctx, ellipse_pts(gx, gy, 26, 28, 16), (0.52, 0.30, 0.65) if (row + c) % 2 else (0.45, 0.25, 0.58), seed=seed + row * 9 + c + 3, shadow=(2, 3), rough=0.5)
    elif name == "WATERMELON":
        rind = [(170 * math.cos(a), 170 * math.sin(a)) for a in np.linspace(0, math.pi, 30)]
        paper(ctx, [(170, 0)] + rind + [(-170, 0)], (0.30, 0.62, 0.32), seed=seed)
        flesh = [(150 * math.cos(a), 150 * math.sin(a)) for a in np.linspace(0, math.pi, 30)]
        paper(ctx, [(150, 0)] + flesh + [(-150, 0)], (0.98, 0.36, 0.40), seed=seed + 1, shadow=(0, 0), rough=0.6)
        for k in range(9):
            a = 0.3 + k * 0.3
            ctx.set_source_rgb(0.15, 0.1, 0.1); ctx.arc(95 * math.cos(a), 95 * math.sin(a), 6, 0, 2 * math.pi); ctx.fill()
        ctx.scale(1, -1)
    ctx.restore()


def basket(ctx, x, y, label_txt, col, seed):
    paper(ctx, [(x - 230, y - 80), (x + 230, y - 80), (x + 190, y + 160), (x - 190, y + 160)], BASKET, seed=seed, shadow=(8, 12))
    for k in range(5):
        ctx.set_source_rgba(0.55, 0.38, 0.2, 0.5); ctx.set_line_width(5)
        ctx.move_to(x - 220 + k * 6, y - 40 + k * 44); ctx.line_to(x + 220 - k * 6, y - 40 + k * 44); ctx.stroke()
    paper(ctx, rect_pts(x - 240, y - 100, 480, 36), BASKET2, seed=seed + 1, shadow=(4, 6))
    tag(ctx, label_txt, x, y + 75, 52, col=(1, 1, 1), bg=col, seed=seed + 2)


def draw(ctx, fi):
    t = fi / FPS; ts = stop(t)
    textured_bg(ctx, WALLC, WALL2)
    for k in range(-1, 12):
        paper(ctx, rect_pts(k * 110, 0, 55, 1100), (0.96, 0.82, 0.68), seed=10 + k % 3, shadow=(0, 0), sh_a=0, rough=0.8)
    # table
    paper(ctx, rect_pts(-20, 1100, W + 40, 900), TABLE, seed=2, shadow=(0, -8), rough=1.2)
    for k in range(6):
        paper(ctx, rect_pts(-20, 1150 + k * 130, W + 40, 8), TABLE2, seed=30 + k, shadow=(0, 0), sh_a=0, rough=1.0)
    # baskets back
    basket(ctx, BL_X, B_Y, "BERRY", GREENT, 40)
    basket(ctx, BR_X, B_Y, "NOT A BERRY", REDT, 50)
    # fruits: landed ones first (inside baskets), then active
    for i, (name, berry) in enumerate(FRUITS):
        st = fruit_state(i, ts)
        if st is None: continue
        x, y, s, rot, landed = st
        draw_fruit(ctx, name, x, y, s, rot, 100 + i * 20)
        if not landed and (ts - T0 - i * SLOT) < SLOT * GUESS_FRAC + 0.1:
            tag(ctx, name, x, y - 250, 48, seed=300 + i, a=ease((ts - T0 - i * SLOT + 0.2) / 0.3))
        # verdict flash
        th = T0 + i * SLOT + SLOT * GUESS_FRAC + 0.6
        if th <= ts < th + 0.7:
            tx = BL_X if berry else BR_X
            tag(ctx, "✓" if berry else "✗", tx, B_Y - 170, 70, col=(1, 1, 1), bg=GREENT if berry else REDT, seed=400 + i, a=1 - ease((ts - th - 0.4) / 0.3))
    # front lip of baskets so fruit sits "inside"
    for (bx, sd) in ((BL_X, 60), (BR_X, 70)):
        paper(ctx, rect_pts(bx - 240, B_Y - 70, 480, 30), BASKET2, seed=sd, shadow=(4, 6))
    # text — top zone
    if ts < T_END + 0.3:
        banner(ctx, "IS IT A BERRY?", 330, 96, seed=1)
    else:
        banner(ctx, "BOTANY IS WEIRD.", 330, 92, seed=2, a=ease((ts - T_END - 0.3) / 0.3))
        banner(ctx, "BANANA = BERRY", 500, 60, col=(0.25, 0.55, 0.28), seed=3, a=ease((ts - T_END - 0.9) / 0.3))
    vignette(ctx, 0.25)


def audio(path):
    tr = Track(DUR)
    ambience(tr, DUR, 0.02)
    musicbox(tr, DUR, mel=(0, 2, 4, 7, 4, 2, 5, 4, 2, 0, 2, 4), gap=0.55, vol=0.06)
    for i, (name, berry) in enumerate(FRUITS):
        ts0 = T0 + i * SLOT
        tr.add(whoosh(0.4, 0.07), max(0, ts0 - 0.4))
        tr.add(tap(260, 0.12), max(0.01, ts0))
        th = ts0 + SLOT * GUESS_FRAC
        tr.add(whoosh(0.6, 0.09), th)
        tr.add(tap(180, 0.25), th + 0.6)
        tr.add(pluck(note(9 if berry else 2, 392), 0.8, 0.14, 4), th + 0.62)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(pluck(note(st + 5, 261.63), 1.4, 0.09, 3), T_END + 0.3 + j * 0.07)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "p3")
    else:
        audio("p3.wav"); encode(draw, NF, "p3_v.mp4"); mux("p3_v.mp4", "p3.wav", "p3_berry.mp4")
