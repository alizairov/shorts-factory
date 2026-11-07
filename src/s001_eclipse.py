"""S-001 · Fact story · Leaf gaps project crescent Suns during a partial eclipse."""
import sys, math
import numpy as np, cairo
from story import *

DUR = 16.0
NF = int(DUR * FPS)
T_SKY, T_GAP, T_PATCH, T_LOOP = 2.4, 6.0, 10.0, 13.0
GOLD = (1.0, 0.80, 0.30)
GROUND_Y = 1080
rng = np.random.default_rng(21)
SPOTS = [(rng.uniform(90, 990), rng.uniform(GROUND_Y + 40, 1560), rng.uniform(26, 42), rng.uniform(0, 6.3)) for _ in range(34)]
LEAVES = [(rng.uniform(-40, 1120), rng.uniform(650, 930), rng.uniform(40, 80), rng.uniform(0, 6.3)) for _ in range(70)]
GAP_X, GAP_Y = 560, 900
SUN_C = (400, 650)
IMG_C = (560 + (560 - 400) * (1380 - 900) / (900 - 650), 1380)


def crescent(ctx, x, y, r, dx, dy, col, a=1.0, sx=1.0, sy=1.0):
    """disc with an offset disc removed; (dx,dy) is the direction of the covering disc"""
    ctx.push_group()
    ctx.save(); ctx.translate(x, y); ctx.scale(sx, sy)
    ctx.set_source_rgb(*col); circle(ctx, 0, 0, r); ctx.fill()
    ctx.set_operator(cairo.OPERATOR_CLEAR); circle(ctx, dx * r * 0.62, dy * r * 0.62, r * 0.98); ctx.fill()
    ctx.restore()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def canopy(ctx, t, dim=0.0, keep_gap=False):
    sway = 14 * math.sin(t * 1.3)
    ctx.set_source_rgba(0.35, 0.24, 0.18, 1 - dim * 0.7); ctx.set_line_width(26); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(W + 40, 560); ctx.curve_to(800, 640 + sway * 0.3, 400, 760, -40, 820 + sway * 0.5); ctx.stroke()
    for (lx, ly, r, ph) in LEAVES:
        x = lx + sway * (1 - (ly - 650) / 400) + 6 * math.sin(t * 2 + ph)
        if keep_gap and abs(x - GAP_X) < 90 and abs(ly - GAP_Y) < 90:
            continue
        col = [(0.42, 0.85, 0.40), (0.30, 0.70, 0.35), (0.72, 1.0, 0.24)][int(ph * 10) % 3]
        ctx.save(); ctx.translate(x, ly); ctx.rotate(ph); ctx.scale(1, 0.55)
        ctx.set_source_rgba(*col, 1 - dim); circle(ctx, 0, 0, r); ctx.fill(); ctx.restore()


def ground(ctx, t):
    g = cairo.LinearGradient(0, GROUND_Y, 0, H)
    g.add_color_stop_rgb(0, 0.20, 0.12, 0.34); g.add_color_stop_rgb(1, 0.10, 0.05, 0.20)
    ctx.set_source(g); ctx.rectangle(0, GROUND_Y, W, H - GROUND_Y); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.05); ctx.set_line_width(2)
    for k in range(9):
        y = GROUND_Y + 30 + k * k * 9
        ctx.move_to(0, y); ctx.line_to(W, y); ctx.stroke()


def spots(ctx, t, a=1.0, stagger=False):
    sway = 14 * math.sin(t * 1.3)
    for i, (x, y, r, ph) in enumerate(SPOTS):
        u = ease((t - T_PATCH - i * 0.03) / 0.35) if stagger else 1
        if u <= 0: continue
        flick = 0.75 + 0.25 * math.sin(t * 3 + ph)
        crescent(ctx, x + sway * 0.6 + 4 * math.sin(t * 2 + ph), y, r * u, 0.7, 0.35, GOLD, a * flick, sx=1.0, sy=0.55)


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx)
    ground(ctx, t)
    if t < T_SKY:
        canopy(ctx, t)
        spots(ctx, t)
    elif t < T_GAP:
        k = ease((t - T_SKY) / 0.6)
        canopy(ctx, t, dim=0.5 * k)
        spots(ctx, t, a=1 - 0.5 * k)
        # sky inset: the partly eclipsed Sun
        sx, sy = W / 2, 820
        ctx.set_source_rgba(0.06, 0.03, 0.14, 0.9 * k); circle(ctx, sx, sy, 190); ctx.fill()
        for rr, al in ((170, 0.12), (140, 0.2)):
            ctx.set_source_rgba(1, 0.7, 0.2, al * k); circle(ctx, sx, sy, rr); ctx.fill()
        crescent(ctx, sx, sy, 120 * (0.6 + 0.4 * k), -0.7, -0.35, GOLD, k)
        mx = sx - 120 * 0.62 * 0.7 * k
        ctx.set_source_rgba(0.06, 0.03, 0.14, 0.0); circle(ctx, mx, sy, 1); ctx.fill()
    elif t < T_PATCH:
        k = ease((t - T_GAP) / 0.5)
        canopy(ctx, t, dim=0.75, keep_gap=True)
        # leaf band with a single gap
        ctx.set_source_rgba(0.30, 0.70, 0.35, 0.95)
        ctx.rectangle(0, GAP_Y - 22, GAP_X - 14, 44); ctx.fill()
        ctx.rectangle(GAP_X + 14, GAP_Y - 22, W - GAP_X - 14, 44); ctx.fill()
        # the Sun crescent
        for rr, al in ((110, 0.12), (90, 0.2)):
            ctx.set_source_rgba(1, 0.7, 0.2, al * k); circle(ctx, *SUN_C, rr); ctx.fill()
        crescent(ctx, *SUN_C, 70, -0.7, -0.35, GOLD, k)
        # two rays from the crescent's horns cross at the gap
        r = ease((t - T_GAP - 0.5) / 1.5)
        horns = [(SUN_C[0] + 40, SUN_C[1] - 50), (SUN_C[0] + 40, SUN_C[1] + 50)]
        for hx, hy in horns:
            ex = GAP_X + (GAP_X - hx) * (IMG_C[1] - GAP_Y) / (GAP_Y - hy)
            ey = IMG_C[1]
            px = hx + (GAP_X - hx) * min(1, r * 2); py = hy + (GAP_Y - hy) * min(1, r * 2)
            ctx.set_source_rgba(1, 0.9, 0.5, 0.9); ctx.set_line_width(4)
            ctx.move_to(hx, hy); ctx.line_to(px, py); ctx.stroke()
            if r > 0.5:
                u = (r - 0.5) * 2
                ctx.move_to(GAP_X, GAP_Y); ctx.line_to(GAP_X + (ex - GAP_X) * u, GAP_Y + (ey - GAP_Y) * u); ctx.stroke()
        if r > 0.95:
            a2 = ease((t - T_GAP - 2.0) / 0.4)
            crescent(ctx, IMG_C[0], IMG_C[1], 80 * a2 + 1, 0.7, 0.35, GOLD, a2, sx=1.0, sy=0.55)
        ctx.set_source_rgba(1, 1, 1, 0.9); circle(ctx, GAP_X, GAP_Y, 7); ctx.fill()
    else:
        canopy(ctx, t)
        spots(ctx, t, stagger=(t < T_LOOP))
    # text — top zone
    if t < T_SKY:
        pill(ctx, "WHO DREW", 300, 96)
        pill(ctx, "THESE CRESCENTS?", 430, 80, col=YEL)
    elif t < T_GAP:
        a = ease((t - T_SKY - 0.3) / 0.3)
        pill(ctx, "ONE PARTLY", 300, 80, alpha=a)
        pill(ctx, "ECLIPSED SUN", 420, 90, col=YEL, alpha=a)
    elif t < T_PATCH:
        a = ease((t - T_GAP) / 0.3)
        pill(ctx, "ONE GAP.", 300, 90, alpha=a)
        pill(ctx, "ONE IMAGE.", 420, 90, col=YEL, alpha=ease((t - T_GAP - 2.0) / 0.3))
    elif t < T_LOOP:
        pill(ctx, "A WHOLE SKY", 300, 90, alpha=ease((t - T_PATCH) / 0.3))
        pill(ctx, "BELOW", 420, 90, col=YEL, alpha=ease((t - T_PATCH) / 0.3))
    else:
        pill(ctx, "LOOK DOWN", 360, 120, col=YEL, alpha=ease((t - T_LOOP) / 0.3))
    progress(ctx, t, DUR)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=84, seed=901, vol=0.32, base=196)
    # leaf whisper
    for k in range(10):
        n = int(SR * 0.9)
        x = np.random.default_rng(100 + k).normal(0, 1, n)
        x = np.convolve(x, np.ones(6) / 6, mode="same") * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.03
        tr.add(x, k * 1.6)
    tr.add(ding(7, 0.2), T_SKY + 0.3)
    tr.add(pluck(note(9, 784), 0.4, 0.1, 8), T_GAP + 0.5)
    tr.add(pluck(note(11, 784), 0.4, 0.1, 8), T_GAP + 1.3)
    tr.add(ding(12, 0.18), T_GAP + 2.0)
    for i in range(14):
        tr.add(pluck(note(i % 10 + 5, 523.25), 0.3, 0.05, 10), T_PATCH + i * 0.1)
    tr.add(ding(5, 0.15), T_LOOP)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "s1")
    else:
        audio("s1.wav"); encode(draw, NF, "s1_v.mp4"); mux("s1_v.mp4", "s1.wav", "s001_eclipse.mp4")
