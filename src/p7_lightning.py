"""Paper fact: Which is hotter — lightning (~28,000 °C, NOAA) or the Sun's surface (~5,500 °C)? About 5×."""
import sys, math, random
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, mux
from paper import paper, rect_pts, ellipse_pts, path
from pbrand import *

DUR = 14.0
NF = int(DUR * FPS)
SKY, SKY2 = (0.36, 0.40, 0.56), (0.62, 0.62, 0.70)
RED, SUNC, BOLT = (0.88, 0.28, 0.22), (0.98, 0.72, 0.28), (0.99, 0.88, 0.36)
GLASS = (0.96, 0.95, 0.92)
TX = [330, 750]
TOP, BOT, TW = 760, 1520, 86        # tube top/bottom, tube width
TMAX = 30000


def yT(T): return BOT - (BOT - TOP) * T / TMAX


def temps(t):
    up = ease(cl((t - 1.4) / 3.2))
    sun = 5500 * ease(cl((t - 1.4) / 1.6))
    bolt = 28000 * up
    cool = ease(cl((t - 12.2) / 1.2))
    return sun * (1 - cool), bolt * (1 - cool)


def sun_icon(ctx, x, y, r, t):
    for k in range(10):
        a = k * math.pi / 5 + t * 0.4
        pts = [(x + (r + 8) * math.cos(a - 0.15), y + (r + 8) * math.sin(a - 0.15)), (x + (r + 50) * math.cos(a), y + (r + 50) * math.sin(a)),
               (x + (r + 8) * math.cos(a + 0.15), y + (r + 8) * math.sin(a + 0.15))]
        paper(ctx, pts, SUNC, seed=30 + k, shadow=(3, 4), rough=0.6)
    paper(ctx, ellipse_pts(x, y, r, r, 36), (0.99, 0.80, 0.34), seed=29, shadow=(5, 7))


def bolt_icon(ctx, x, y, s, a=1.0):
    ctx.push_group()
    for dx, dy, r in [(-60, 0, 60), (0, -25, 75), (65, 0, 58), (0, 20, 60)]:
        paper(ctx, ellipse_pts(x + dx * s, y - 40 * s + dy * s, r * s, r * s * 0.85, 26), (0.78, 0.80, 0.86), seed=40 + dx % 7, shadow=(4, 6), rough=1.2)
    pts = [(x + 5 * s, y + 10 * s), (x - 40 * s, y + 110 * s), (x - 5 * s, y + 110 * s), (x - 30 * s, y + 200 * s), (x + 45 * s, y + 80 * s),
           (x + 10 * s, y + 80 * s), (x + 35 * s, y + 10 * s)]
    paper(ctx, pts, BOLT, seed=45, shadow=(4, 6), rough=0.5)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def thermo(ctx, x, T, col, seed):
    paper(ctx, rect_pts(x - TW / 2, TOP - 20, TW, BOT - TOP + 40), GLASS, seed=seed, shadow=(6, 9), rough=1.2)
    paper(ctx, ellipse_pts(x, BOT + 40, 78, 78, 32), GLASS, seed=seed + 1, shadow=(6, 9))
    paper(ctx, ellipse_pts(x, BOT + 40, 58, 58, 32), col, seed=seed + 2, shadow=(0, 0), rough=0.8)
    y = yT(T)
    paper(ctx, rect_pts(x - TW / 2 + 18, y, TW - 36, BOT + 10 - y), col, seed=seed + 3, shadow=(0, 0), rough=0.6)
    for k in range(1, 6):   # tick marks
        yy = yT(k * 5000)
        ctx.set_source_rgba(*INK, 0.35); ctx.set_line_width(3); ctx.move_to(x + TW / 2 - 4, yy); ctx.line_to(x + TW / 2 + 16, yy); ctx.stroke()


def draw(ctx, fi):
    t = fi / FPS; ts = stop(t)
    textured_bg(ctx, SKY, SKY2)
    flash = max(0.0, 1 - abs(ts - 0.25) / 0.25) + 0.6 * max(0.0, 1 - abs(ts - 0.75) / 0.15) + 0.5 * max(0.0, 1 - abs(ts - 4.6) / 0.2)
    paper(ctx, [(-30, 1700), (300, 1640), (700, 1690), (W + 30, 1630), (W + 30, H + 20), (-30, H + 20)], (0.40, 0.52, 0.38), seed=5, shadow=(0, -6), rough=1.5)
    sT, bT = temps(ts)
    sun_icon(ctx, TX[0], 600, 70, ts)
    bolt_icon(ctx, TX[1], 520, 1.0, 1.0)
    thermo(ctx, TX[0], sT, SUNC, 10)
    thermo(ctx, TX[1], bT, RED, 20)
    if ts > 3.0:
        tag(ctx, "5,500°C", TX[0] - 150 if ts > 3.0 else TX[0], yT(sT) + 15, 44, seed=50, a=cl((ts - 3.0) / 0.3) * (1 - cl((ts - 12.0) / 0.3)))
    if ts > 4.6:
        tag(ctx, "28,000°C", TX[1] + 140, yT(bT) + 15, 44, seed=51, a=cl((ts - 4.6) / 0.3) * (1 - cl((ts - 12.0) / 0.3)))
    # 5 suns stacked next to the lightning column
    for k in range(5):
        a = cl((ts - 8.0 - k * 0.45) / 0.3) * (1 - cl((ts - 12.0) / 0.3))
        if a > 0.01:
            y0, y1 = yT((k + 1) * 5500), yT(k * 5500)
            ctx.push_group()
            paper(ctx, rect_pts(TX[1] - 250, y0 + 4, 110, y1 - y0 - 8), SUNC, seed=60 + k, shadow=(4, 6), rough=1.0)
            paper(ctx, ellipse_pts(TX[1] - 195, (y0 + y1) / 2, 30, 30, 20), (0.99, 0.86, 0.45), seed=70 + k, shadow=(2, 3), rough=0.6)
            ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    if flash > 0:
        ctx.set_source_rgba(1, 0.98, 0.9, 0.45 * min(1, flash)); ctx.paint()
    banner(ctx, "LIGHTNING OR THE SUN?", 380, 74, a=window(ts, -1, 5.3) + fade_in(ts, 13.2), seed=1)
    banner(ctx, "5× HOTTER.", 380, 110, col=(0.80, 0.26, 0.18), a=window(ts, 5.5, 12.0), seed=2)
    brand(ctx)
    vignette(ctx, 0.25)


def rumble(d=1.8, amp=0.12):
    x = soft_noise(d, 400, 1.0)
    m = np.arange(len(x)) / len(x)
    return x * np.exp(-m * 3) * np.minimum(1, m * 30) * amp


def audio(path):
    tr = Track(DUR)
    ambience(tr, DUR, 0.02)
    musicbox(tr, DUR, vol=0.03, gap=0.8)
    tr.add(rustle(0.25, 0.08, 500, (30, 120)), 0.2); tr.add(rumble(2.0, 0.14), 0.4)
    tr.add(slide(1.6, 0.06), 1.4); tr.add(flick(0.06), 3.0)
    tr.add(slide(3.0, 0.05), 1.6)
    tr.add(rustle(0.3, 0.08, 500, (30, 120)), 4.5); tr.add(rumble(1.5, 0.10), 4.6); tr.add(flick(0.06), 4.6)
    tr.add(pluck(note(12, 261.63), 1.4, 0.12, 3), 5.5)
    for k in range(5): tr.add(thud(0.12), 8.0 + k * 0.45); tr.add(flick(0.04), 8.0 + k * 0.45)
    tr.add(slide(1.2, 0.05), 12.2)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "p7")
    else:
        audio("p7.wav"); encode(draw, NF, "p7_v.mp4"); mux("p7_v.mp4", "p7.wav", "p7_lightning.mp4")
