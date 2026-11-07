"""Paper-cutout fun fact: an octopus has 3 hearts, blue blood, and one heart stops when it swims."""
import sys, math
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, SR, mux, label, FONT
from paper import paper, pin, rect_pts, ellipse_pts, rough_poly, path, TEX

DUR = 20.0
NF = int(DUR * FPS)
STEP = 12
T_Q, T_3, T_JOB, T_BLUE, T_SWIM, T_END = 0.0, 2.8, 7.2, 10.8, 14.4, 18.6

SEA_TOP = (0.20, 0.55, 0.62); SEA_BOT = (0.08, 0.27, 0.36)
SAND = (0.93, 0.83, 0.62); SAND2 = (0.87, 0.75, 0.52)
OCTO = (0.93, 0.47, 0.55); OCTO2 = (0.83, 0.36, 0.46)
CREAM = (0.98, 0.95, 0.87); INK = (0.16, 0.12, 0.14)
RED = (0.86, 0.22, 0.26); BLUE = (0.22, 0.45, 0.92); GREY = (0.55, 0.55, 0.58)
WEED = [(0.32, 0.62, 0.42), (0.24, 0.52, 0.38), (0.45, 0.70, 0.40)]
rng = np.random.default_rng(4)
BUBBLES = [(rng.uniform(80, W - 80), rng.uniform(0, 1), rng.uniform(10, 26), rng.uniform(0.5, 1.2)) for _ in range(22)]


def ease(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def popu(u):
    u = min(max(u, 0), 1)
    return u * (1 + 0.35 * math.sin(u * math.pi))


def banner(ctx, txt, y, size, col=INK, bg=CREAM, a=1.0, seed=0, hl=None):
    """text on a torn paper strip"""
    if a <= 0: return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(size)
    w = ctx.text_extents(txt).x_advance
    pad = size * 0.45
    ctx.push_group()
    paper(ctx, rect_pts(W / 2 - w / 2 - pad, y - size * 0.95, w + 2 * pad, size * 1.35), bg, seed=seed, shadow=(5, 7), rough=2.0)
    label(ctx, txt, W / 2, y, size, col=hl or col, shadow=0)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def heart(ctx, x, y, s, col, seed):
    pts = []
    for k in range(48):
        tt = 2 * math.pi * k / 48
        hx = 16 * math.sin(tt) ** 3
        hy = -(13 * math.cos(tt) - 5 * math.cos(2 * tt) - 2 * math.cos(3 * tt) - math.cos(4 * tt))
        pts.append((x + hx * s, y + hy * s))
    paper(ctx, pts, col, seed=seed, shadow=(4, 6), rough=0.9)


def background(ctx, ts):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *SEA_TOP); g.add_color_stop_rgb(1, *SEA_BOT)
    ctx.set_source(g); ctx.paint()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); ctx.set_source_surface(TEX, 0, 0); ctx.paint(); ctx.restore()
    # paper light rays
    for i in range(4):
        x = 150 + i * 260 + 30 * math.sin(ts * 0.4 + i)
        ctx.move_to(x, 0); ctx.line_to(x + 90, 0); ctx.line_to(x + 260, 1500); ctx.line_to(x + 120, 1500); ctx.close_path()
        ctx.set_source_rgba(1, 1, 0.95, 0.05); ctx.fill()
    # far wave layers
    for j, (yy, col) in enumerate([(1250, (0.12, 0.38, 0.45)), (1330, (0.10, 0.33, 0.40))]):
        pts = [(x, yy + 30 * math.sin(x / 140 + j + ts * 0.3)) for x in range(-40, W + 80, 60)] + [(W + 40, H), (-40, H)]
        paper(ctx, pts, col, seed=20 + j, shadow=(0, -6), sh_a=0.2, rough=1.0)
    # seaweed
    for i, bx in enumerate([90, 230, 860, 990]):
        segs, L = 7, 70
        x, y = bx, 1560
        for k in range(segs):
            a = math.pi + 0.18 * math.sin(ts * 1.4 + i + k * 0.6)
            nx, ny = x + L * math.sin(a), y + L * math.cos(a)
            w = 34 - k * 3
            pts = [(x - w / 2, y), (x + w / 2, y), (nx + w / 2 - 3, ny), (nx - w / 2 + 3, ny)]
            paper(ctx, pts, WEED[(i + k) % 3], seed=30 + i * 10 + k, shadow=(4, 6), rough=1.0)
            x, y = nx, ny
    # sand
    pts = [(x, 1500 + 25 * math.sin(x / 200)) for x in range(-40, W + 80, 60)] + [(W + 40, H + 20), (-40, H + 20)]
    paper(ctx, pts, SAND, seed=40, shadow=(0, -8), sh_a=0.25)
    for i, (px, pr) in enumerate([(150, 40), (330, 26), (700, 34), (920, 48), (520, 20)]):
        paper(ctx, ellipse_pts(px, 1620 + (i % 2) * 60, pr * 1.4, pr, 18), SAND2 if i % 2 else (0.75, 0.70, 0.66), seed=50 + i, shadow=(4, 6))


def bubbles(ctx, ts):
    for (bx, ph, r, sp) in BUBBLES:
        y = 1600 - ((ts * 120 * sp + ph * 1600) % 1700)
        x = bx + 14 * math.sin(ts * 2 + ph * 9)
        ctx.set_source_rgba(1, 1, 1, 0.25); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.7); ctx.set_line_width(3); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
        ctx.set_source_rgba(1, 1, 1, 0.8); ctx.arc(x - r * 0.35, y - r * 0.35, r * 0.25, 0, 2 * math.pi); ctx.fill()


def octopus(ctx, cx, cy, ts, swim=0.0):
    """paper octopus; returns mantle centre"""
    # tentacles behind
    for i in range(8):
        base_a = math.pi * (0.15 + 0.7 * i / 7)          # spread under the mantle
        x = cx + 135 * math.cos(base_a)
        y = cy + 80
        segs = 9
        for k in range(segs):
            curl = 0.35 * math.sin(ts * 2.2 - k * 0.7 + i) * (1 - swim * 0.7)
            lean = (i - 3.5) * 0.17 * (1 + k * 0.12) * (1 - swim * 0.8)
            a = lean + curl + swim * (0.15 * (i - 3.5) / 3.5)
            L = 58 - k * 2.5 + swim * 10
            w = 54 - k * 5.2
            nx, ny = x + L * math.sin(a), y + L * math.cos(a)
            col = OCTO if (i % 2) else OCTO2
            pts = [(x - w / 2, y), (x + w / 2, y), (nx + w / 2 - 2, ny), (nx - w / 2 + 2, ny)]
            paper(ctx, pts, col, seed=100 + i * 10 + k, shadow=(4, 6), rough=0.8)
            if k % 2 == 0 and k < 6:
                ctx.set_source_rgba(1, 0.85, 0.85, 0.9); ctx.arc((x + nx) / 2 + 6, (y + ny) / 2, max(3, w * 0.14), 0, 2 * math.pi); ctx.fill()
            x, y = nx, ny
    # mantle (head)
    sq = 1 + 0.04 * math.sin(ts * 2.2) - swim * 0.08
    pts = [(cx + 175 * math.cos(a) * sq, cy - 60 + 215 * math.sin(a) / sq) for a in np.linspace(math.pi, 2 * math.pi, 26)]
    pts += [(cx + 175 * sq, cy - 60), (cx + 150, cy + 90), (cx - 150, cy + 90), (cx - 175 * sq, cy - 60)]
    paper(ctx, pts, OCTO, seed=180, shadow=(8, 11))
    # spots
    for (dx, dy, r) in [(-70, -180, 18), (60, -200, 13), (95, -120, 15), (-100, -90, 11)]:
        paper(ctx, ellipse_pts(cx + dx, cy + dy, r, r, 12), OCTO2, seed=190 + r, shadow=(2, 3), rough=0.5)
    # eyes
    for ex in (-62, 62):
        paper(ctx, ellipse_pts(cx + ex, cy + 30, 36, 40, 20), CREAM, seed=200 + ex, shadow=(3, 4), rough=0.7)
        blink = 1 if ((ts + 2.0) % 4.5) > 0.15 else 0.15
        ctx.set_source_rgb(*INK); ctx.save(); ctx.translate(cx + ex + 6, cy + 36); ctx.scale(1, blink)
        ctx.arc(0, 0, 15, 0, 2 * math.pi); ctx.fill(); ctx.restore()
        ctx.set_source_rgb(1, 1, 1); ctx.arc(cx + ex + 11, cy + 30, 5 * blink, 0, 2 * math.pi); ctx.fill()
    return cx, cy - 110


def draw(ctx, fi):
    t = fi / FPS
    ts = math.floor(t * STEP) / STEP
    background(ctx, ts)
    bubbles(ctx, ts)
    # octopus position: bob; jets up during swim beat
    swim = ease((ts - T_SWIM) / 0.6) * (1 - ease((ts - (T_END - 0.6)) / 0.8))
    cy = 1040 + 20 * math.sin(ts * 1.6) - 260 * swim
    cx = W / 2 + 10 * math.sin(ts * 0.9)
    ctx.save(); ctx.translate(cx, cy); ctx.scale(1.15, 1.15); ctx.translate(-cx, -cy)
    mx, my = octopus(ctx, cx, cy, ts, swim)

    # cut-away window + hearts
    if ts >= T_3:
        wa = ease((ts - T_3) / 0.25)
        paper(ctx, ellipse_pts(mx, my, 140 * wa + 1, 100 * wa + 1, 30), CREAM, seed=300, shadow=(4, 6), rough=1.2)
        blue = ease((ts - T_BLUE - 0.4) / 0.8)
        for k, (dx, dy, s) in enumerate([(-72, 12, 2.4), (72, 12, 2.4), (0, -12, 3.6)]):
            tk = T_3 + 0.35 + k * 0.6
            if ts < tk: continue
            u = popu((ts - tk) / 0.35)
            beat = 1 + 0.08 * max(0, math.sin((ts - tk) * 2 * math.pi * 1.1)) ** 6
            stopped = k == 2 and swim > 0.5
            col = tuple(RED[i] + (BLUE[i] - RED[i]) * blue for i in range(3))
            if stopped:
                col = GREY; beat = 1
            heart(ctx, mx + dx, my + dy, s * u * beat, col, seed=310 + k)
    ctx.restore()
    if ts >= T_3:
        # labels
        if T_JOB <= ts < T_BLUE:
            a = ease((ts - T_JOB) / 0.3) * (1 - ease((ts - T_BLUE + 0.3) / 0.3))
            banner(ctx, "2 HEARTS → GILLS", 1820 - 120, 52, a=a, seed=320)
            banner(ctx, "1 HEART → BODY", 1820, 52, a=ease((ts - T_JOB - 0.6) / 0.3) * (1 - ease((ts - T_BLUE + 0.3) / 0.3)), seed=321)

    # headline strips (always something on screen from frame 1)
    if ts < T_3:
        banner(ctx, "HOW MANY HEARTS", 240, 76, seed=1)
        banner(ctx, "DOES AN OCTOPUS HAVE?", 350, 64, seed=2)
        banner(ctx, "guess before it opens…", 1800, 44, bg=(0.95, 0.88, 0.70), a=ease((t - 0.6) / 0.4), seed=3)
    elif ts < T_BLUE:
        banner(ctx, "THREE.", 260, 120, hl=RED, seed=4)
    elif ts < T_SWIM:
        banner(ctx, "AND ITS BLOOD", 240, 76, seed=5)
        banner(ctx, "IS BLUE", 360, 100, hl=BLUE, seed=6)
        banner(ctx, "copper instead of iron", 1800, 46, bg=(0.82, 0.90, 1.0), a=ease((ts - T_BLUE - 0.8) / 0.4), seed=7)
    elif ts < T_END:
        banner(ctx, "WHEN IT SWIMS,", 240, 70, seed=8)
        banner(ctx, "ONE HEART STOPS", 350, 76, hl=RED, seed=9)
        banner(ctx, "so octopuses prefer to crawl", 1800, 44, a=ease((ts - T_SWIM - 1.2) / 0.4), seed=10)
    else:
        banner(ctx, "NATURE IS WEIRD.", 260, 84, seed=11)
        banner(ctx, "follow for more paper facts", 1800, 44, bg=(0.95, 0.88, 0.70), seed=12)
    # soft vignette
    g = cairo.RadialGradient(W / 2, H / 2, 520, W / 2, H / 2, 1250)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0.05, 0.08, 0.35)
    ctx.set_source(g); ctx.paint()


def audio(path):
    tr = Track(DUR)
    r = np.random.default_rng(9)
    # underwater bed: low-passed noise swell
    n = int(SR * DUR)
    x = r.normal(0, 1, n)
    for w in (400, 400):
        x = np.convolve(x, np.ones(w) / w, mode="same")
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.10 * (0.8 + 0.2 * np.sin(np.arange(n) / SR * 0.6))
    tr.add(x, 0)
    # bubble plops
    for k in range(40):
        tt = r.uniform(0, DUR - 0.2)
        m = np.arange(int(SR * 0.08)) / SR
        f = 500 + 2500 * m / 0.08
        tr.add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m * 40) * 0.05, tt)
    # music box
    mel = [0, 4, 2, 4, 5, 4, 2, 0, 2, 4, 7, 5, 4, 2, 4, 0]
    for i, st in enumerate(mel * 2):
        tr.add(pluck(note(st + 5, 261.63), 1.0, 0.07, 4), 0.2 + i * 0.62)
    # heartbeats (soft lub-dub) while hearts are visible
    def thump(f=60, d=0.18, a=0.35):
        m = np.arange(int(SR * d)) / SR
        return np.sin(2 * np.pi * f * m) * np.exp(-m * 22) * a
    for k in range(3):
        tr.add(pluck(note(5 + k * 2, 392), 0.6, 0.18, 6), T_3 + 0.35 + k * 0.6)
    tt = T_3 + 1.8
    while tt < T_END:
        if not (T_SWIM + 0.6 < tt < T_END - 0.6):
            tr.add(thump(), tt); tr.add(thump(52, 0.16, 0.25), tt + 0.18)
        tt += 0.9
    tr.add(pluck(note(10, 261.63), 1.4, 0.12, 3), T_BLUE + 0.4)
    # soft whoosh for the swim
    m = np.arange(int(SR * 0.8)) / SR
    wh = np.convolve(r.normal(0, 1, len(m)), np.ones(30) / 30, mode="same") * np.sin(np.pi * m / 0.8) ** 2 * 0.25
    tr.add(wh, T_SWIM)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "p1")
    else:
        audio("p1.wav"); encode(draw, NF, "p1_v.mp4"); mux("p1_v.mp4", "p1.wav", "p1_octopus.mp4")
