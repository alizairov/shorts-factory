"""S-003 · Fact story · About 90% of an iceberg's volume lies underwater."""
import sys, math
import numpy as np, cairo
from story import *

DUR = 16.0
NF = int(DUR * FPS)
WL = 790                      # waterline y
T_REVEAL, T_GAUGE, T_TIP, T_LOOP = 2.4, 6.0, 10.0, 13.0
ICE, ICE2, ICE_SH = (0.93, 0.98, 1.0), (0.78, 0.92, 1.0), (0.62, 0.82, 0.96)
SEA, SEA_D = (0.13, 0.62, 0.78), (0.05, 0.25, 0.45)


def berg_pts(bob):
    """iceberg outline: small tip above water, big body below (≈1/10 vs 9/10 area)"""
    top = [(470, WL - 120), (520, WL - 160), (585, WL - 140), (640, WL - 90), (665, WL)]
    below = [(735, WL + 60), (800, WL + 240), (790, WL + 470), (720, WL + 690), (600, WL + 820),
             (460, WL + 800), (330, WL + 650), (280, WL + 420), (300, WL + 200), (370, WL + 40)]
    pts = [(415, WL)] + top + below
    return [(x, y + bob) for x, y in pts]


def draw_berg(ctx, bob, t):
    pts = berg_pts(bob)
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path()
    g = cairo.LinearGradient(0, WL - 160, 0, WL + 820)
    g.add_color_stop_rgb(0, *ICE); g.add_color_stop_rgb(0.2, *ICE2); g.add_color_stop_rgb(1, *ICE_SH)
    ctx.set_source(g); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(5); ctx.stroke()
    # facets
    ctx.set_source_rgba(1, 1, 1, 0.35); ctx.set_line_width(3)
    for (a, b) in [((520, WL - 160 + bob), (560, WL + 200 + bob)), ((640, WL - 90 + bob), (700, WL + 400 + bob)), ((370, WL + 40 + bob), (450, WL + 600 + bob))]:
        ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()


def draw(ctx, fi):
    t = fi / FPS
    bob = 6 * math.sin(t * 1.6)
    # sky
    g = cairo.LinearGradient(0, 0, 0, WL)
    g.add_color_stop_rgb(0, 0.10, 0.05, 0.22); g.add_color_stop_rgb(1, 0.30, 0.16, 0.42)
    ctx.set_source(g); ctx.rectangle(0, 0, W, WL); ctx.fill()
    for k in range(40):
        sx, sy = (k * 137) % W, (k * 71) % (WL - 100)
        ctx.set_source_rgba(1, 1, 1, 0.25 + 0.2 * math.sin(t * 2 + k)); circle(ctx, sx, sy, 1.6); ctx.fill()
    # deep water background (behind ice)
    g = cairo.LinearGradient(0, WL, 0, H)
    g.add_color_stop_rgb(0, *SEA); g.add_color_stop_rgb(1, *SEA_D)
    ctx.set_source(g); ctx.rectangle(0, WL, W, H - WL); ctx.fill()
    draw_berg(ctx, bob, t)
    # opaque water layer that fades to transparent at the reveal, returns at the loop
    op = 1 - ease((t - T_REVEAL) / 0.8)
    op = max(op, ease((t - T_LOOP - 0.6) / 1.2))
    if op > 0.01:
        ctx.save(); ctx.rectangle(0, WL, W, H - WL); ctx.clip()
        g = cairo.LinearGradient(0, WL, 0, H)
        g.add_color_stop_rgba(0, *SEA, op); g.add_color_stop_rgba(1, *SEA_D, op)
        ctx.set_source(g); ctx.paint(); ctx.restore()
    # translucent tint even when "transparent" so it still reads as water
    ctx.set_source_rgba(*SEA, 0.22); ctx.rectangle(0, WL, W, H - WL); ctx.fill()
    # surface line with ripples
    ctx.set_source_rgba(1, 1, 1, 0.85); ctx.set_line_width(5)
    for k, x in enumerate(range(0, W + 1, 20)):
        y = WL + 6 * math.sin(x / 50 + t * 2.5)
        (ctx.move_to if k == 0 else ctx.line_to)(x, y)
    ctx.stroke()
    # bead gauge (right side)
    if t >= T_GAUGE:
        for b in range(10):
            by = WL - 70 + b * 78
            u = ease((t - T_GAUGE - 0.12 * b) / 0.25)
            ctx.set_source_rgba(1, 1, 1, 0.25); circle(ctx, 960, by, 28); ctx.fill()
            if b == 0:
                glint = ease((t - T_TIP) / 0.3)
                if glint > 0:
                    glossy_ball(ctx, 960, by, 28 * (0.6 + 0.4 * glint) * (1 + 0.15 * math.sin((t - T_TIP) * 6) * (t < T_TIP + 1)), (1, 1, 1))
            elif u > 0:
                glossy_ball(ctx, 960, by, 28 * u, CYAN, glow=False)
        # bracket labels
        ctx.set_source_rgba(1, 1, 1, 0.6); ctx.set_line_width(4)
        ctx.move_to(915, WL - 100); ctx.line_to(905, WL - 100); ctx.line_to(905, WL - 40); ctx.line_to(915, WL - 40); ctx.stroke()
    # text — top reading zone
    if t < T_REVEAL:
        pill(ctx, "HOW MUCH ICE", 300, 92)
        pill(ctx, "IS HIDDEN?", 430, 92, col=CYAN)
    elif t < T_GAUGE:
        a = ease((t - T_REVEAL - 0.4) / 0.3)
        pill(ctx, "ABOUT 90%", 330, 130, col=CYAN, alpha=a)
        pill(ctx, "BY VOLUME", 470, 64, alpha=a)
    elif t < T_TIP:
        pill(ctx, "ROUGHLY", 300, 70, alpha=ease((t - T_GAUGE) / 0.3))
        pill(ctx, "NINE TENTHS", 430, 100, col=CYAN, alpha=ease((t - T_GAUGE) / 0.3))
    elif t < T_LOOP:
        pill(ctx, "THE VISIBLE", 300, 80, alpha=ease((t - T_TIP) / 0.3))
        pill(ctx, "TENTH", 430, 110, col=YEL, alpha=ease((t - T_TIP) / 0.3))
    else:
        pill(ctx, "JUST THE TIP", 360, 110, col=CYAN, alpha=ease((t - T_LOOP) / 0.3))
    progress(ctx, t, DUR)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=80, seed=903, vol=0.35, base=174.6)
    # soft water laps
    for k in range(12):
        n = int(SR * 0.6); x = np.convolve(np.random.default_rng(k).normal(0, 1, n), np.ones(60) / 60, mode="same")
        tr.add(x * np.sin(np.linspace(0, np.pi, n)) ** 2 * 0.25, k * 1.35)
    m = np.arange(int(SR * 2.0)) / SR
    tr.add(np.sin(2 * np.pi * 110 * m) * np.sin(np.pi * m / 2.0) * 0.12, T_REVEAL)     # low glass swell
    tr.add(ding(9, 0.18), T_REVEAL + 0.4)
    for b in range(1, 10):
        tr.add(pluck(note(b, 523.25), 0.25, 0.06, 14), T_GAUGE + 0.12 * b)
    tr.add(ding(14, 0.2), T_TIP)
    tr.add(ding(7, 0.15), T_LOOP)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "s3")
    else:
        audio("s3.wav"); encode(draw, NF, "s3_v.mp4"); mux("s3_v.mp4", "s3.wav", "s003_iceberg.mp4")
