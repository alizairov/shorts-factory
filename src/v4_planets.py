import sys, math
import numpy as np, cairo
from common import *

# name, diameter km, base color, band color or None, ring
P = [
    ("MOON", 3474, (0.75, 0.74, 0.80), None, False),
    ("MERCURY", 4879, (0.62, 0.55, 0.52), None, False),
    ("MARS", 6779, (0.93, 0.38, 0.22), None, False),
    ("VENUS", 12104, (0.98, 0.80, 0.45), None, False),
    ("EARTH", 12742, (0.20, 0.50, 1.00), (0.40, 0.85, 0.35), False),
    ("NEPTUNE", 49244, (0.25, 0.40, 1.00), (0.40, 0.60, 1.00), False),
    ("URANUS", 50724, (0.45, 0.92, 0.95), None, False),
    ("SATURN", 116460, (0.95, 0.80, 0.50), (0.85, 0.65, 0.38), True),
    ("JUPITER", 139820, (0.90, 0.62, 0.42), (0.98, 0.88, 0.75), False),
    ("SUN", 1392700, (1.00, 0.72, 0.15), None, False),
]
EARTH = 12742
STEP = 1.75
SUN_HOLD = 3.6
BASE_Y = 1240
GAP = 0.18
DUR = STEP * (len(P) - 1) + SUN_HOLD + 0.6
NF = int(DUR * FPS)

# world x positions (km), planets sit on a common baseline, left to right
xs = []
x = 0
for i, p in enumerate(P):
    if i:
        x += P[i - 1][1] / 2 + p[1] / 2 + GAP * max(P[i - 1][1], p[1]) * 0.5
    xs.append(x)

rng = np.random.default_rng(4)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 2.4), rng.uniform(0, 6.28)) for _ in range(160)]


def ease(u):
    u = min(max(u, 0), 1)
    return u * u * (3 - 2 * u)


def cam(t):
    """Return (scale px/km, center x km) — eased between planet focus states."""
    k = min(t / STEP, len(P) - 1)
    i = int(k)
    u = ease((k - i) / 0.55)  # move quickly, then hold

    def st(n):
        target = 0.36 if n < len(P) - 1 else 0.62
        s = W * target / P[n][1]
        cx = xs[n] - (W * 0.08) / s if n < len(P) - 1 else xs[n]
        return math.log(s), cx

    a, b = st(max(i - 1, 0)), st(i)
    ls = a[0] + (b[0] - a[0]) * u
    cx = a[1] + (b[1] - a[1]) * u
    return math.exp(ls), cx


def draw_planet(ctx, x, y, r, p, t):
    name, d, c, band, ring = p
    if r < 0.4:
        ctx.set_source_rgb(*c); circle(ctx, x, y, 0.6); ctx.fill(); return
    if name == "SUN":
        for gr, a in [(1.5, 0.08), (1.25, 0.14), (1.1, 0.25)]:
            ctx.set_source_rgba(1, 0.6, 0.1, a); circle(ctx, x, y, r * gr); ctx.fill()
    if ring:
        ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.28)
        ctx.set_source_rgba(0.95, 0.85, 0.65, 0.75); ctx.set_line_width(r * 0.22)
        ctx.arc(0, 0, r * 1.75, math.pi, 2 * math.pi); ctx.stroke(); ctx.restore()
    ctx.save()
    circle(ctx, x, y, r); ctx.clip()
    ctx.set_source_rgb(*c); ctx.paint()
    if band and name in ("JUPITER", "SATURN", "NEPTUNE"):
        for k in range(-5, 6):
            ctx.set_source_rgba(*band, 0.55 if k % 2 else 0.25)
            ctx.rectangle(x - r, y + k * r * 0.17, 2 * r, r * 0.08 + abs(k) * r * 0.01); ctx.fill()
        if name == "JUPITER":
            ctx.set_source_rgba(0.85, 0.35, 0.25, 0.9)
            ctx.save(); ctx.translate(x + r * 0.3, y + r * 0.35); ctx.scale(1, 0.6)
            circle(ctx, 0, 0, r * 0.16); ctx.fill(); ctx.restore()
    if name == "EARTH":
        ctx.set_source_rgb(*band)
        for (dx, dy, rr) in [(-0.35, -0.2, 0.32), (0.3, 0.25, 0.28), (0.1, -0.45, 0.18), (-0.1, 0.5, 0.15)]:
            circle(ctx, x + dx * r, y + dy * r, rr * r); ctx.fill()
    if name in ("MOON", "MERCURY"):
        for (dx, dy, rr) in [(-0.3, -0.2, 0.14), (0.3, 0.3, 0.1), (0.15, -0.4, 0.08), (-0.2, 0.4, 0.12)]:
            ctx.set_source_rgba(0, 0, 0, 0.18); circle(ctx, x + dx * r, y + dy * r, rr * r); ctx.fill()
    if name == "SUN":
        for k in range(30):
            a = k * 2.4 + t * 0.2
            ctx.set_source_rgba(1, 0.95, 0.5, 0.12)
            circle(ctx, x + math.cos(a) * r * (0.2 + 0.7 * ((k * 37) % 10) / 10),
                   y + math.sin(a) * r * (0.2 + 0.7 * ((k * 53) % 10) / 10), r * 0.12); ctx.fill()
    # shading
    g = cairo.RadialGradient(x - r * 0.4, y - r * 0.4, r * 0.1, x, y, r * 1.05)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.35)
    g.add_color_stop_rgba(0.5, 1, 1, 1, 0.0)
    g.add_color_stop_rgba(1, 0, 0, 0, 0.0 if name == "SUN" else 0.45)
    ctx.set_source(g); ctx.paint()
    ctx.restore()
    if ring:
        ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.28)
        ctx.set_source_rgba(0.95, 0.85, 0.65, 0.85); ctx.set_line_width(r * 0.22)
        ctx.arc(0, 0, r * 1.75, 0, math.pi); ctx.stroke(); ctx.restore()


def fmt(n):
    return f"{n:,} km"


def draw(ctx, fi):
    t = fi / FPS
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.10, 0.05, 0.22)
    g.add_color_stop_rgb(1, 0.02, 0.01, 0.07)
    ctx.set_source(g); ctx.paint()
    for (sx, sy, sr, ph) in STARS:
        ctx.set_source_rgba(1, 1, 1, 0.35 + 0.3 * math.sin(t * 2 + ph))
        circle(ctx, sx, sy, sr); ctx.fill()
    s, cx = cam(t)
    cur = min(int(t / STEP), len(P) - 1)
    for i, p in enumerate(P):
        if i > cur:
            continue
        r = p[1] / 2 * s
        x = W / 2 + (xs[i] - cx) * s
        y = BASE_Y - r if p[0] != "SUN" else BASE_Y - r * 0.85
        if x + r * 2 < -50 or x - r * 2 > W + 50:
            continue
        pop = ease((t - i * STEP) / 0.35)
        draw_planet(ctx, x, y + (1 - pop) * 60, r * (0.6 + 0.4 * pop), p, t)
    # caption for current planet
    p = P[cur]
    a = ease((t - cur * STEP) / 0.3)
    col = lighten(p[2], 0.15)
    label(ctx, p[0], W / 2, 1450, 120, col=col, alpha=a)
    label(ctx, fmt(p[1]), W / 2, 1540, 58, alpha=0.9 * a)
    ratio = p[1] / EARTH
    sub = "= EARTH" if p[0] == "EARTH" else (f"{ratio:.1f}x EARTH" if ratio >= 1 else f"{ratio:.2f}x EARTH")
    if p[0] == "SUN":
        sub = "109x EARTH"
    label(ctx, sub, W / 2, 1625, 50, col=grad(0.2), alpha=0.95 * a)
    # hook
    label(ctx, "PLANET SIZES", W / 2, 250, 96)
    label(ctx, "TO SCALE", W / 2, 345, 70, col=grad(0.62))
    # progress dots
    for i in range(len(P)):
        on = i <= cur
        ctx.set_source_rgba(*(grad(i / len(P)) if on else (1, 1, 1)), 1 if on else 0.2)
        circle(ctx, W / 2 + (i - (len(P) - 1) / 2) * 44, 1760, 11 if i == cur else 8); ctx.fill()
    if t > STEP * (len(P) - 1) + 1.4:
        b = ease((t - STEP * (len(P) - 1) - 1.4) / 0.4)
        label(ctx, "1.3 MILLION EARTHS", W / 2, 520, 70, col=(1, 0.85, 0.3), alpha=b)
        label(ctx, "FIT INSIDE THE SUN", W / 2, 600, 56, alpha=b)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=100, seed=1, vol=0.8, base=196)
    for i in range(len(P)):
        tt = i * STEP
        n = np.arange(int(SR * 0.6)) / SR
        sweep = np.sin(2 * np.pi * (300 + 900 * n) * n) * np.exp(-n * 9) * 0.12
        tr.add(sweep, tt)
        tr.add(pluck(note(10 - i, 130.81), 1.2, 0.35, 3), tt + 0.05)
    tsun = STEP * (len(P) - 1)
    n = np.arange(int(SR * 2.5)) / SR
    tr.add(np.sin(2 * np.pi * 55 * n) * np.exp(-n * 1.5) * 0.6, tsun)
    for k, st in enumerate([0, 2, 4, 5, 7]):
        tr.add(pluck(note(st + 5, 261.63), 1.5, 0.15, 3), tsun + 1.4 + k * 0.06)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "v4")
    else:
        audio("v4.wav")
        encode(draw, NF, "v4_video.mp4")
        mux("v4_video.mp4", "v4.wav", "reels_4_planets.mp4")
        print("dur", DUR)
