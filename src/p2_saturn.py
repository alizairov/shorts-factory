"""Paper fact: which planet would float in a (giant) bathtub? Saturn."""
import sys, math
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, SR, mux
from paper import paper, pin, rect_pts, ellipse_pts, path, TEX
from paperkit import *

DUR = 16.0
NF = int(DUR * FPS)
TILE = (0.70, 0.86, 0.82); TILE2 = (0.64, 0.80, 0.77)
TUB = (0.97, 0.96, 0.93); TUB_IN = (0.80, 0.82, 0.84)
WATER = (0.42, 0.70, 0.90); WATER2 = (0.30, 0.58, 0.84)
SURF_Y = 1000
TUB_X0, TUB_X1, TUB_TOP, TUB_BOT = 70, W - 70, 1000, 1450
BOTTOM_Y = 1410

PLANETS = [  # name, radius, colour, bands, ring, t_start
    ("EARTH", 72, (0.25, 0.52, 0.95), None, False, -0.6),
    ("MARS", 58, (0.90, 0.40, 0.25), None, False, 2.5),
    ("JUPITER", 150, (0.92, 0.72, 0.52), (0.78, 0.52, 0.36), False, 4.9),
    ("SATURN", 120, (0.96, 0.84, 0.55), (0.86, 0.70, 0.42), True, 8.1),
]
FALL = 0.9
SINK = 1.3
T_REVEAL = 9.6
T_WHY = 12.0


def planet_y(i, t):
    name, r, col, band, ring, ts0 = PLANETS[i]
    if t < ts0: return None
    land = ts0 + FALL
    if t < land:
        u = (t - ts0) / FALL
        return 120 + (SURF_Y - 120) * u * u
    if name != "SATURN":
        u = ease((t - land) / SINK)
        return SURF_Y + (BOTTOM_Y - r - SURF_Y) * u + 8 * math.sin((t - land) * 9) * (1 - u)
    # Saturn floats ~2/3 submerged and bobs
    float_y = SURF_Y + r * 0.35
    k = t - land
    return float_y + 40 * math.exp(-k * 2.2) * math.cos(k * 7) + 6 * math.sin(t * 2.2)


def draw_planet(ctx, x, y, r, col, band, ring, seed, back=False):
    if ring and back:
        ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.3)
        ctx.set_source_rgba(0.95, 0.85, 0.62, 1); ctx.set_line_width(r * 0.28)
        ctx.arc(0, 0, r * 1.75, math.pi, 2 * math.pi); ctx.stroke(); ctx.restore()
        return
    if back: return
    paper(ctx, ellipse_pts(x, y, r, r, 40), col, seed=seed, shadow=(6, 8))
    ctx.save(); ctx.arc(x, y, r - 2, 0, 2 * math.pi); ctx.clip()
    if band:
        for k in range(-4, 5):
            if k % 2 == 0: continue
            paper(ctx, rect_pts(x - r, y + k * r * 0.2 - r * 0.06, 2 * r, r * 0.12), band, seed=seed + k + 10, shadow=(0, 2), sh_a=0.15, rough=1.2)
    if col[2] > 0.9:  # earth continents
        for (dx, dy, rr) in [(-0.35, -0.2, 0.33), (0.3, 0.25, 0.28), (0.15, -0.5, 0.18)]:
            paper(ctx, ellipse_pts(x + dx * r, y + dy * r, rr * r, rr * r * 0.8, 16), (0.38, 0.78, 0.40), seed=seed + 30, shadow=(2, 3), rough=1.0)
    ctx.restore()
    if ring:
        ctx.save(); ctx.translate(x, y); ctx.scale(1, 0.3)
        ctx.set_source_rgba(0.98, 0.88, 0.65, 1); ctx.set_line_width(r * 0.28)
        ctx.arc(0, 0, r * 1.75, 0, math.pi); ctx.stroke(); ctx.restore()


XS = [-320, 330, -170, 170]
TK_X0, TK_X1, TK_TOP, TK_BOT = 80, W - 80, 760, 1440


def draw(ctx, fi):
    t = fi / FPS; ts = stop(t)
    textured_bg(ctx, TILE, TILE2)
    for gx in range(0, W + 1, 120):
        ctx.set_source_rgba(1, 1, 1, 0.45); ctx.rectangle(gx - 2, 0, 4, 1500); ctx.fill()
    for gy in range(0, 1500, 120):
        ctx.set_source_rgba(1, 1, 1, 0.45); ctx.rectangle(0, gy - 2, W, 4); ctx.fill()
    paper(ctx, rect_pts(-20, 1470, W + 40, 480), (0.86, 0.74, 0.62), seed=2, shadow=(0, -6), rough=1.2)
    # wooden stand
    paper(ctx, rect_pts(TK_X0 - 30, TK_BOT, TK_X1 - TK_X0 + 60, 50), (0.62, 0.42, 0.26), seed=3, shadow=(8, 10))
    for fx in (TK_X0 + 40, TK_X1 - 70):
        paper(ctx, rect_pts(fx, TK_BOT + 50, 30, 120), (0.55, 0.37, 0.22), seed=4 + fx % 5)
    # tank back pane
    ctx.set_source_rgba(1, 1, 1, 0.18); ctx.rectangle(TK_X0, TK_TOP, TK_X1 - TK_X0, TK_BOT - TK_TOP); ctx.fill()
    wave = lambda x, ph: SURF_Y + 9 * math.sin(x / 70 + ts * 2 + ph)
    # water back layer
    pts = [(x, wave(x, 0)) for x in range(TK_X0, TK_X1 + 1, 30)] + [(TK_X1, TK_BOT), (TK_X0, TK_BOT)]
    paper(ctx, pts, WATER2, seed=7, shadow=(0, 0), rough=0)
    # pebbles
    for k in range(14):
        px = TK_X0 + 40 + k * 63
        paper(ctx, ellipse_pts(px, TK_BOT - 18, 34, 18, 14), [(0.85, 0.80, 0.70), (0.75, 0.72, 0.68), (0.90, 0.75, 0.55)][k % 3], seed=300 + k, shadow=(2, 3), rough=0.8)
    # planets
    for i, (name, r, col, band, ring, ts0) in enumerate(PLANETS):
        y = planet_y(i, ts)
        if y is None: continue
        x = W / 2 + XS[i]
        draw_planet(ctx, x, y, r, col, band, ring, 100 + i * 10, back=True)
        draw_planet(ctx, x, y, r, col, band, ring, 100 + i * 10)
    # front water (translucent tint over everything below the surface)
    ctx.push_group()
    pts = [(x, wave(x, 1.3)) for x in range(TK_X0, TK_X1 + 1, 30)] + [(TK_X1, TK_BOT), (TK_X0, TK_BOT)]
    path(ctx, pts); ctx.set_source_rgb(*WATER); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(0.30)
    ctx.set_source_rgba(1, 1, 1, 0.85); ctx.set_line_width(6)
    for k, x in enumerate(range(TK_X0, TK_X1 + 1, 30)):
        (ctx.move_to if k == 0 else ctx.line_to)(x, wave(x, 1.3))
    ctx.stroke()
    # bubbles from sunk planets + splashes
    for i, (name, r, col, band, ring, ts0) in enumerate(PLANETS):
        x = W / 2 + XS[i]
        k = ts - (ts0 + FALL)
        if 0 <= k < 0.7:
            for d in range(9):
                a = math.pi + (d + 0.5) * math.pi / 9
                sp = (r * 0.9 + 120) * k / 0.7
                dx, dy = x + math.cos(a) * sp, SURF_Y + math.sin(a) * sp * 1.4 + 900 * k * k
                ctx.set_source_rgba(1, 1, 1, 0.9 * (1 - k / 0.7)); ctx.arc(dx, dy, 9 + r * 0.05, 0, 2 * math.pi); ctx.fill()
        if name != "SATURN" and 0 < k < 3:
            for b in range(4):
                bt = (k + b * 0.3) % 1.0
                by = BOTTOM_Y - r - bt * (BOTTOM_Y - r - SURF_Y)
                ctx.set_source_rgba(1, 1, 1, 0.7); ctx.set_line_width(3); ctx.arc(x + 20 * math.sin(b * 2 + ts * 3), by, 8, 0, 2 * math.pi); ctx.stroke()
    # glass frame + highlights
    ctx.set_source_rgba(0.85, 0.95, 1, 0.9); ctx.set_line_width(12)
    ctx.rectangle(TK_X0, TK_TOP, TK_X1 - TK_X0, TK_BOT - TK_TOP); ctx.stroke()
    for (hx, w) in ((TK_X0 + 40, 26), (TK_X0 + 90, 10)):
        ctx.set_source_rgba(1, 1, 1, 0.35); ctx.rectangle(hx, TK_TOP + 30, w, TK_BOT - TK_TOP - 60); ctx.fill()
    # name tags while falling
    for i, (name, r, col, band, ring, ts0) in enumerate(PLANETS):
        y = planet_y(i, ts)
        if y is None: continue
        if ts < ts0 + FALL + 0.6:
            x = W / 2 + XS[i]
            tag(ctx, name, x, y - r - 30 - (40 if ring else 0), 42, seed=200 + i, a=1 - ease((ts - ts0 - FALL - 0.2) / 0.4))
    # text — top reading zone only
    if ts < T_REVEAL:
        banner(ctx, "WHICH PLANET FLOATS?", 330, 76, seed=1)
    else:
        banner(ctx, "SATURN.", 340, 130, col=(0.80, 0.55, 0.15), seed=20, a=ease((ts - T_REVEAL) / 0.25))
        banner(ctx, "LIGHTER THAN WATER", 520, 60, seed=21, a=ease((ts - T_WHY) / 0.3))
    vignette(ctx)


def audio(path):
    tr = Track(DUR)
    ambience(tr, DUR, 0.03)
    musicbox(tr, DUR, vol=0.06)
    for i, (name, r, col, band, ring, ts0) in enumerate(PLANETS):
        land = max(0.05, ts0 + FALL)
        tr.add(whoosh(0.7, 0.10), max(0, land - 0.7))
        tr.add(splash(0.18 + r / 900), land)
        tr.add(plop(140 - r * 0.3, 0.3), land)
        if name != "SATURN":
            for b in range(6):
                tr.add(bubble(0.05), land + 0.2 + b * 0.22)
        else:
            for b in range(5):
                tr.add(pluck(note(7 + b % 3, 392), 0.5, 0.06, 6), land + 0.4 + b * 0.45)
    tr.add(pluck(note(12, 261.63), 1.5, 0.15, 3), T_REVEAL)
    tr.add(pluck(note(9, 261.63), 1.2, 0.10, 3), T_WHY)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "p2")
    else:
        audio("p2.wav"); encode(draw, NF, "p2_v.mp4"); mux("p2_v.mp4", "p2.wav", "p2_saturn.mp4")
