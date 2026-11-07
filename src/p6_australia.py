"""Paper fact: Which is wider — the Moon (3,474 km) or Australia (~4,000 km east–west)?"""
import sys, math, random
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, mux
from paper import paper, rect_pts, ellipse_pts, path
from pbrand import *

DUR = 15.0
NF = int(DUR * FPS)
NAVY, NAVY2 = (0.16, 0.19, 0.34), (0.09, 0.10, 0.22)
SAND, SAND2 = (0.93, 0.62, 0.32), (0.84, 0.50, 0.26)
MOON, MOON2 = (0.82, 0.82, 0.80), (0.66, 0.66, 0.66)
PLUTO = (0.90, 0.78, 0.66)
AUS = [(113.5, -22.0), (114.0, -26.0), (115.0, -30.0), (115.0, -33.5), (117.0, -35.0), (120.0, -34.0), (123.5, -33.9), (126.0, -32.3),
       (129.0, -31.6), (131.5, -31.5), (134.0, -32.5), (135.5, -34.8), (137.5, -33.0), (137.8, -35.6), (139.5, -35.8), (140.5, -38.0),
       (143.5, -38.8), (146.3, -39.1), (148.0, -37.8), (150.0, -37.4), (150.8, -34.5), (152.5, -32.0), (153.6, -28.0), (153.0, -25.0),
       (150.8, -22.5), (149.0, -21.0), (146.3, -19.0), (145.4, -16.0), (145.3, -14.8), (143.5, -14.0), (142.5, -10.7), (141.6, -12.8),
       (141.5, -15.5), (140.8, -17.5), (139.3, -17.4), (137.0, -15.8), (135.5, -14.8), (136.8, -12.3), (135.9, -11.9), (133.0, -11.5),
       (132.0, -11.2), (130.2, -12.4), (129.5, -14.9), (127.8, -14.3), (126.0, -14.2), (124.5, -16.2), (122.2, -17.5), (121.0, -19.5),
       (118.8, -20.3), (116.8, -20.6), (114.2, -21.8)]
TAS = [(144.6, -40.7), (148.3, -40.9), (148.0, -43.2), (146.0, -43.6), (145.2, -42.2)]
LON0, LAT0 = 133.55, -25.0   # centre of the 113.5–153.6° E span
KX, KY = 100.9, 110.6        # km per degree at ~25° S
R_MOON, R_PLUTO = 1737, 1188


def aus_pts(cx, cy, p, poly):
    return [(cx + (lo - LON0) * KX * p, cy - (la - LAT0) * KY * p) for lo, la in poly]


def moon(ctx, x, y, r, a=1.0, seed=0):
    ctx.push_group()
    paper(ctx, ellipse_pts(x, y, r, r, 48), MOON, seed=seed, shadow=(6, 9), rough=1.4)
    for dx, dy, rr in [(-0.35, -0.3, 0.18), (0.3, 0.1, 0.24), (-0.1, 0.45, 0.12), (0.45, -0.4, 0.1), (-0.5, 0.2, 0.09)]:
        paper(ctx, ellipse_pts(x + dx * r, y + dy * r, rr * r, rr * r, 20), MOON2, seed=seed + 7, shadow=(2, 3), sh_a=0.2, rough=0.8)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def arrow(ctx, x0, x1, y, txt, a, seed):
    if a <= 0.01: return
    ctx.set_source_rgba(*CREAM, a); ctx.set_line_width(5)
    ctx.move_to(x0, y); ctx.line_to(x1, y); ctx.stroke()
    for x in (x0, x1):
        ctx.move_to(x, y - 18); ctx.line_to(x, y + 18); ctx.stroke()
    tag(ctx, txt, (x0 + x1) / 2, y + 18, 46, seed=seed, a=a)


def draw(ctx, fi):
    t = fi / FPS; ts = stop(t)
    textured_bg(ctx, NAVY, NAVY2)
    rnd = random.Random(1)
    for k in range(60):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        ctx.set_source_rgba(*CREAM, 0.35 + 0.35 * math.sin(ts * 2 + k)); ctx.arc(x, y, rnd.uniform(2, 4.5), 0, 2 * math.pi); ctx.fill()
    # side-by-side (small) -> stacked: Moon above Australia, same scale, edge guides
    z = ease(cl((ts - 3.0) / 1.2)) * (1 - ease(cl((ts - 12.6) / 1.4)))
    p = 0.115 + (0.155 - 0.115) * z
    ax, ay = 750 + (540 - 750) * z, 1080 + (1330 - 1080) * z
    mx = 225 + 6 * math.sin(ts * 1.6) * (1 - z) + (540 - 225) * z
    my = 1060 + 6 * math.cos(ts * 1.3) * (1 - z) + (780 - 1060) * z
    pl = ease(cl((ts - 8.6) / 0.8)) * (1 - ease(cl((ts - 12.0) / 0.6)))
    mx += pl * 800
    paper(ctx, aus_pts(ax, ay, p, AUS), SAND, seed=3, shadow=(7, 10), rough=1.0)
    paper(ctx, aus_pts(ax, ay, p, TAS), SAND2, seed=4, shadow=(4, 6), rough=0.6)
    rm = R_MOON * p
    if pl > 0.01:
        pd = 1 - ease(cl((ts - 9.2) / 0.5)); rp = R_PLUTO * p; py = 780 - pd * 900
        ctx.push_group()
        paper(ctx, ellipse_pts(540, py, rp, rp, 40), PLUTO, seed=12, shadow=(6, 8))
        paper(ctx, ellipse_pts(540 + 0.2 * rp, py + 0.2 * rp, 0.45 * rp, 0.4 * rp, 24), CREAM, seed=13, shadow=(2, 3), rough=0.8)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(min(1, pl * 2))
    moon(ctx, mx, my, rm, 1.0, seed=8)
    # guides from the Moon's (or Pluto's) edges down through Australia
    g = cl((ts - 4.3) / 0.4) * (1 - cl((ts - 12.2) / 0.3))
    if g > 0.01:
        half = rm + (R_PLUTO * p - rm) * cl((ts - 9.4) / 0.5)
        ctx.set_source_rgba(*CREAM, 0.8 * g); ctx.set_line_width(4); ctx.set_dash([16, 12])
        for sx in (-1, 1):
            ctx.move_to(540 + sx * half, 780); ctx.line_to(540 + sx * half, 1640); ctx.stroke()
        ctx.set_dash([])
        for sx in (-1, 1):   # highlight the part of Australia that sticks out
            ctx.set_source_rgba(1, 0.95, 0.6, 0.0)
    a1 = cl((ts - 4.8) / 0.3) * (1 - cl((ts - 8.5) / 0.3))
    a2 = cl((ts - 5.3) / 0.3) * (1 - cl((ts - 8.5) / 0.3))
    arrow(ctx, 540 - rm, 540 + rm, 780 - 20, "3,474 KM", a1, 21)
    w_aus = 4010 * p
    arrow(ctx, 540 - w_aus / 2, 540 + w_aus / 2, 1290, "4,000 KM", a2, 20)
    banner(ctx, "MOON OR AUSTRALIA?", 380, 80, a=window(ts, -1, 5.7) + fade_in(ts, 14.2), seed=1)
    banner(ctx, "AUSTRALIA WINS.", 380, 96, col=(0.80, 0.36, 0.16), a=window(ts, 5.9, 8.8), seed=2)
    banner(ctx, "PLUTO? EVEN SMALLER.", 380, 76, a=window(ts, 9.3, 12.2), seed=3)
    brand(ctx)
    vignette(ctx, 0.25)


def audio(path):
    tr = Track(DUR)
    ambience(tr, DUR, 0.02)
    musicbox(tr, DUR, vol=0.03, gap=0.8)
    tr.add(slide(0.5, 0.06), 0.0)
    tr.add(slide(1.0, 0.07), 3.0); tr.add(thud(0.22), 4.15); tr.add(rustle(0.3, 0.07), 4.15)
    tr.add(flick(0.06), 4.6); tr.add(flick(0.06), 5.3)
    tr.add(pluck(note(12, 261.63), 1.4, 0.12, 3), 5.9)
    tr.add(slide(0.7, 0.06), 8.6); tr.add(thud(0.16), 9.7); tr.add(rustle(0.25, 0.06), 9.7)
    tr.add(pluck(note(9, 261.63), 1.0, 0.09, 3), 9.3)
    tr.add(slide(1.2, 0.06), 12.4); tr.add(rustle(0.4, 0.05), 13.8)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "p6")
    else:
        audio("p6.wav"); encode(draw, NF, "p6_v.mp4"); mux("p6_v.mp4", "p6.wav", "p6_australia.mp4")
