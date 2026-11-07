"""Long horizontal (16:9) version: Which planet would float? Faster pacing, ambient pad audio, thumbnail."""
import sys, math, random
import numpy as np, cairo
import common, story
for _m in (common, story): _m.W, _m.H = 1920, 1080
from story import *
W, H = 1920, 1080
import paperkit as pk

DUR = 112.0
NF = int(DUR * FPS)
SC = [0, 10, 28, 46, 62, 80, 100]          # scene starts
TY = 132                                     # text baseline (top band)

PC = {"earth": (0.25, 0.55, 1.0), "mars": (0.92, 0.42, 0.25), "jupiter": (0.86, 0.68, 0.48),
      "saturn": (0.96, 0.86, 0.56), "neptune": (0.3, 0.45, 1.0), "uranus": (0.55, 0.9, 0.95),
      "venus": (0.96, 0.8, 0.5), "mercury": (0.66, 0.63, 0.6)}


def cl(u): return max(0.0, min(1.0, u))
def lerp(a, b, u): return a + (b - a) * u


def rings(ctx, x, y, r, tilt, front, alpha=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(1, max(tilt, 0.004))
    a0, a1 = (0, math.pi) if front else (math.pi, 2 * math.pi)
    for rr, w, a in [(1.32, 0.10, 0.35), (1.55, 0.26, 0.85), (1.9, 0.30, 0.7), (2.15, 0.08, 0.45)]:
        ctx.new_path(); ctx.arc(0, 0, rr * r, a0, a1)
        ctx.set_line_width(w * r); ctx.set_source_rgba(0.93, 0.84, 0.62, a * alpha); ctx.stroke()
    ctx.restore()
    if tilt < 0.06:
        ctx.set_source_rgba(0.95, 0.88, 0.7, alpha * (1 - tilt / 0.06)); ctx.set_line_width(3)
        ctx.move_to(x - 2.2 * r, y); ctx.line_to(x + 2.2 * r, y); ctx.stroke()


def planet(ctx, x, y, r, kind, alpha=1.0, tilt=0.3, ring=True, ocean=1.0):
    c = PC[kind]
    if kind == "saturn" and ring: rings(ctx, x, y, r, tilt, False, alpha)
    ctx.save(); circle(ctx, x, y, r); ctx.clip()
    if kind == "earth":
        land = (0.62, 0.5, 0.36)
        ctx.set_source_rgba(*[lerp(land[i], c[i], ocean) for i in range(3)], alpha); ctx.paint()
        ctx.set_source_rgba(0.35, 0.78, 0.4, alpha * (0.4 + 0.6 * ocean))
        for dx, dy, w, h in [(-0.35, -0.2, 0.45, 0.3), (0.3, 0.25, 0.35, 0.45), (0.1, -0.55, 0.3, 0.15)]:
            ctx.save(); ctx.translate(x + dx * r, y + dy * r); ctx.scale(w * r, h * r); circle(ctx, 0, 0, 1); ctx.restore(); ctx.fill()
    else:
        ctx.set_source_rgba(*c, alpha); ctx.paint()
        if kind in ("jupiter", "saturn"):
            for i in range(-4, 5):
                ctx.set_source_rgba(*lighten(c, -0.18 if i % 2 else 0.12), alpha * 0.6)
                ctx.rectangle(x - r, y + i * r * 0.22 - r * 0.06, 2 * r, r * 0.11); ctx.fill()
    g = cairo.RadialGradient(x - 0.35 * r, y - 0.4 * r, r * 0.1, x, y, r * 1.05)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.28 * alpha); g.add_color_stop_rgba(0.6, 0, 0, 0, 0)
    g.add_color_stop_rgba(1, 0.02, 0, 0.08, 0.55 * alpha)
    ctx.set_source(g); ctx.paint(); ctx.restore()
    if kind == "saturn" and ring: rings(ctx, x, y, r, tilt, True, alpha)


# ---------- tank (scenes 1 & 7) ----------
TX0, TX1, TY0, TY1, WL = 260, 1660, 330, 1010, 520
DROPS = [("jupiter", 560, 120, 0.15), ("earth", 900, 60, 1.1), ("mars", 1110, 42, 1.9), ("saturn", 1370, 92, 2.9)]
G = 3400


def t_hit(r): return math.sqrt(2 * (WL - (230 - r)) / G)


def drop_y(kind, r, t, t0):
    y0 = 230 - r; u = t - t0
    if u <= 0: return y0
    if u < t_hit(r): return y0 + 0.5 * G * u * u
    v = u - t_hit(r)
    if kind == "saturn":
        return WL - 0.15 * r + 40 * math.exp(-1.8 * v) * math.cos(6 * v)
    bottom = TY1 - r - 8
    return bottom - (bottom - WL) * math.exp(-2.2 * v)


def tank(ctx, t, saturn_alpha=1.0, wisps=0.0):
    ctx.move_to(TX0, TY1)
    for xx in range(TX0, TX1 + 1, 20):
        ctx.line_to(xx, WL + 6 * math.sin(xx * 0.015 + t * 2.0))
    ctx.line_to(TX1, TY1); ctx.close_path()
    g = cairo.LinearGradient(0, WL, 0, TY1); g.add_color_stop_rgba(0, 0.24, 0.94, 1, 0.42); g.add_color_stop_rgba(1, 0.1, 0.3, 0.9, 0.55)
    ctx.set_source(g); ctx.fill()
    for kind, x, r, t0 in DROPS:
        y = drop_y(kind, r, t, t0)
        a = saturn_alpha if kind == "saturn" else 1.0
        if a > 0.01: planet(ctx, x, y, r, kind, a)
        u = t - t0 - t_hit(r)
        if 0 < u < 0.8:
            ctx.save(); ctx.translate(x, WL); ctx.scale(1, 0.2)
            ctx.arc(0, 0, r + 260 * eout(u / 0.8), 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - u / 0.8)); ctx.set_line_width(4); ctx.stroke()
        if kind != "saturn" and 0 < u < 3:
            rnd = random.Random(int(x))
            for k in range(9):
                bu = (u * 0.9 + k / 9) % 1
                bx = x + rnd.uniform(-r, r) + 8 * math.sin(t * 3 + k)
                ctx.set_source_rgba(1, 1, 1, 0.5 * (1 - bu) * cl(1 - u / 3)); circle(ctx, bx, y - bu * (y - WL), 6); ctx.fill()
    if wisps > 0:
        rnd = random.Random(3)
        for k in range(260):
            ang = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.2, 1) * 420 * wisps
            px = 1370 + math.cos(ang) * d * 1.2 + 10 * math.sin(t + k)
            py = max(WL + 5, WL + math.sin(ang) * d * 0.5 + 80 * wisps)
            ctx.set_source_rgba(0.96, 0.86, 0.56, 0.6 * (1 - wisps) + 0.15); circle(ctx, px, py, rnd.uniform(3, 10)); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.65); ctx.set_line_width(6); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(TX0, TY0); ctx.line_to(TX0, TY1); ctx.line_to(TX1, TY1); ctx.line_to(TX1, TY0); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.12); ctx.rectangle(TX0 + 20, TY0 + 20, 14, TY1 - TY0 - 60); ctx.fill()


# ---------- scene 2 ----------
DENS = [("earth", 5.51), ("mercury", 5.43), ("venus", 5.24), ("mars", 3.93), ("neptune", 1.64), ("jupiter", 1.33), ("uranus", 1.27), ("saturn", 0.69)]


def cube(ctx, x, y, s, col, stripes=False, waves=False):
    ctx.set_source_rgb(*col); ctx.rectangle(x - s / 2, y - s, s, s); ctx.fill()
    ctx.set_source_rgb(*lighten(col, 0.25)); ctx.move_to(x - s / 2, y - s); ctx.line_to(x - s / 2 + 24, y - s - 24)
    ctx.line_to(x + s / 2 + 24, y - s - 24); ctx.line_to(x + s / 2, y - s); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(*lighten(col, -0.25)); ctx.move_to(x + s / 2, y - s); ctx.line_to(x + s / 2 + 24, y - s - 24)
    ctx.line_to(x + s / 2 + 24, y - 24); ctx.line_to(x + s / 2, y); ctx.close_path(); ctx.fill()
    ctx.save(); ctx.rectangle(x - s / 2, y - s, s, s); ctx.clip()
    if stripes:
        for i in range(5):
            ctx.set_source_rgba(*lighten(col, -0.15), 0.7); ctx.rectangle(x - s / 2, y - s + i * s / 5 + 6, s, s / 12); ctx.fill()
    if waves:
        ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(4)
        for i in range(3):
            yy = y - s * 0.75 + i * s * 0.25; ctx.move_to(x - s / 2, yy)
            for k in range(13): ctx.line_to(x - s / 2 + k * s / 12, yy + 6 * math.sin(k * 1.4))
            ctx.stroke()
    ctx.restore()


def scene2(ctx, t):
    u = t - 10
    if u < 6:
        th = -0.17 * ease(cl((u - 1.4) / 0.9)) + 0.025 * math.sin(u * 5) * math.exp(-max(0, u - 2.3) * 2)
        px, py, L = 960, 520, 420
        ctx.set_source_rgba(1, 1, 1, 0.8); ctx.move_to(px, py); ctx.line_to(px - 80, 960); ctx.line_to(px + 80, 960); ctx.close_path(); ctx.fill()
        ends = [(px - L * math.cos(th), py - L * math.sin(th)), (px + L * math.cos(th), py + L * math.sin(th))]
        ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(*ends[0]); ctx.line_to(*ends[1]); ctx.stroke()
        for i, (ex, ey) in enumerate(ends):
            pyb = ey + 200
            ctx.set_source_rgba(1, 1, 1, 0.6); ctx.set_line_width(3)
            ctx.move_to(ex, ey); ctx.line_to(ex - 110, pyb); ctx.move_to(ex, ey); ctx.line_to(ex + 110, pyb); ctx.stroke()
            ctx.set_source_rgba(1, 1, 1, 0.85); ctx.set_line_width(8); ctx.move_to(ex - 130, pyb); ctx.line_to(ex + 130, pyb); ctx.stroke()
            d = eout(cl((u - 0.1 - i * 0.4) / 0.45)); yy = pyb - 6 - (1 - d) * 600
            if i == 0: cube(ctx, ex, yy, 170, (0.15, 0.6, 1.0), waves=True)
            else:
                cube(ctx, ex, yy, 170, PC["saturn"], stripes=True); planet(ctx, ex, yy - 250, 38, "saturn", d)
        circle(ctx, px, py, 18); ctx.set_source_rgb(*YEL); ctx.fill()
        return
    v = u - 6
    x0, sc = 420, 220
    wx = x0 + sc
    for i, (k, d) in enumerate(DENS):
        y = 250 + i * 98
        g = ease(cl((v - 0.2 - i * 0.55) / 0.6))
        dim = 1.0 if v < 6 or k == "saturn" else 0.35
        if k == "saturn" and v > 6:
            a = ease(cl((v - 6) / 0.4))
            card(ctx, 180, y - 46, 1600, 92, 46, (*YEL, 0.14 * a * (0.8 + 0.2 * math.sin(v * 4))))
        planet(ctx, 300, y, 32, k, dim, tilt=0.3)
        col = YEL if k == "saturn" else PAL[i % 6]
        card(ctx, x0, y - 24, max(1, d * sc * g), 48, 24, (*col, 0.85 * dim))
        if g > 0.9: label(ctx, f"{d:.2f}", x0 + d * sc + 20, y, 36, alpha=dim * cl((g - 0.9) * 10), anchor="l")
    ctx.set_source_rgba(0.3, 0.95, 1, 0.9); ctx.set_line_width(5); ctx.set_dash([18, 12])
    ctx.move_to(wx, 195); ctx.line_to(wx, 1000); ctx.stroke(); ctx.set_dash([])
    label(ctx, "WATER = 1", wx, 1035, 34, col=CYAN)


# ---------- scene 3 ----------
def scene3(ctx, t):
    u = t - 28
    R, X, Y = 330, 820, 600
    cut = ease(cl((u - 0.4) / 1.4)) * math.pi / 2
    planet(ctx, X, Y, R, "saturn", tilt=0.22)
    if cut > 0.01:
        ctx.save(); ctx.move_to(X, Y); ctx.arc(X, Y, R, -math.pi / 2, -math.pi / 2 + cut); ctx.close_path(); ctx.clip()
        for rr, c in [(1.0, (0.12, 0.08, 0.3)), (0.62, (0.3, 0.2, 0.5)), (0.2, (0.55, 0.35, 0.25))]:
            circle(ctx, X, Y, R * rr); ctx.set_source_rgb(*c); ctx.fill()
        rnd = random.Random(5)
        for k in range(200):
            rr = R * rnd.uniform(0.22, 0.98); ang = rnd.uniform(-math.pi / 2, 0) + 0.1 * math.sin(u * 0.9 + k)
            he = k % 7 == 0
            ctx.set_source_rgba(*(PINK if he else (1, 1, 1)), 0.85); circle(ctx, X + rr * math.cos(ang), Y + rr * math.sin(ang), 7 if he else 5); ctx.fill()
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(3)
        ctx.move_to(X, Y - R); ctx.line_to(X, Y); ctx.line_to(X + R, Y); ctx.stroke()
        rings(ctx, X, Y, R, 0.22, True)
    a = ease(cl((u - 3) / 0.6))
    if a > 0:  # legend dots next to the planet
        for i, (c, s) in enumerate([((1, 1, 1), "H"), (PINK, "He")]):
            yy = 470 + i * 90
            ctx.set_source_rgba(*c, a); circle(ctx, 1560, yy, 16 if i else 12); ctx.fill()
            label(ctx, s, 1600, yy, 52, alpha=a, anchor="l")
    if u > 8:  # helium balloon floats up
        b = u - 8
        bx, by = 1580 + 18 * math.sin(b * 1.3), 1150 - 95 * b
        ctx.set_source_rgba(1, 1, 1, 0.6); ctx.set_line_width(2); ctx.move_to(bx, by + 75); ctx.curve_to(bx - 15, by + 130, bx + 15, by + 170, bx, by + 210); ctx.stroke()
        ctx.save(); ctx.translate(bx, by); ctx.scale(0.85, 1); circle(ctx, 0, 0, 75); ctx.restore(); ctx.set_source_rgb(*PINK); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.35); circle(ctx, bx - 22, by - 25, 16); ctx.fill()
        label(ctx, "He", bx, by + 5, 46)


# ---------- scene 4 ----------
R4, X4, Y4 = 420, 760, 600


def _pack():
    d = 28.0
    while True:
        pts = [((i + 0.5 * (j % 2)) * d, j * d * 0.866) for j in range(-35, 36) for i in range(-35, 36)]
        pts = [p for p in pts if p[0] ** 2 + p[1] ** 2 < (R4 - d * 0.55) ** 2]
        if len(pts) >= 764: break
        d -= 0.3
    rnd = random.Random(2); pts.sort(key=lambda p: -p[1] + rnd.uniform(-12, 12))
    return pts[:764], d


PACK, PD = _pack()
FILL0, FILLD = 0.8, 8.5


def scene4(ctx, t):
    u = t - 46
    planet(ctx, X4, Y4, R4, "saturn", alpha=0.25 + 0.75 * (1 - cl((u - 0.3) / 0.8)), tilt=0.2)
    ctx.set_source_rgba(*YEL, 0.8); ctx.set_line_width(4); circle(ctx, X4, Y4, R4); ctx.stroke()
    n = int(764 * cl((u - FILL0) / FILLD) ** 1.5)
    for k in range(n):
        x, y = PACK[k]
        age = (u - FILL0) - FILLD * (k / 764) ** (1 / 1.5)
        planet(ctx, X4 + x, Y4 + y, PD * 0.46 * (pop(cl(age / 0.3)) if age < 0.3 else 1), "earth")
    if u > FILL0:
        label(ctx, f"{n}", 1500, 560, 200, col=YEL if n == 764 else (1, 1, 1))
        planet(ctx, 1500, 760, 44, "earth"); label(ctx, "×", 1430, 760, 60, alpha=0.8)


# ---------- scene 5 ----------
def drop_shape(ctx, x, y, r):
    ctx.move_to(x, y - 2.0 * r)
    ctx.curve_to(x + 0.6 * r, y - 1.1 * r, x + r, y - 0.6 * r, x + r, y)
    ctx.arc(x, y, r, 0, math.pi)
    ctx.curve_to(x - r, y - 0.6 * r, x - 0.6 * r, y - 1.1 * r, x, y - 2.0 * r); ctx.close_path()


def scene5(ctx, t):
    u = t - 62
    drain = ease(cl((u - 0.5) / 4.0))
    z = ease(cl((u - 5.2) / 3.0))
    s = lerp(1.0, 46.0 / 330, z)
    ex, ey = lerp(960, 330, z), 600
    if z > 0:
        sr = 9.14 * 330 * s; sx = lerp(960 + 3000, 1180, z)
        planet(ctx, sx, ey, sr, "saturn", tilt=0.18, ring=False)
        if u > 9:
            a = ease(cl((u - 9) / 0.6))
            ctx.set_source_rgba(0.3, 0.95, 1, 0.8 * a); ctx.set_line_width(5); ctx.set_dash([20, 14])
            ctx.move_to(sx - sr - 40, ey - sr - 20); ctx.line_to(sx - sr - 40, ey + sr + 30); ctx.line_to(sx + sr + 40, ey + sr + 30)
            ctx.line_to(sx + sr + 40, ey - sr - 20); ctx.stroke(); ctx.set_dash([])
    planet(ctx, ex, ey, 330 * s, "earth", ocean=1 - drain)
    if drain > 0.01:
        dr = 35 * drain ** (1 / 3)
        dx, dy = ex, ey - (330 + 95) * s
        drop_shape(ctx, dx, dy, max(1.6, dr * s)); ctx.set_source_rgb(0.2, 0.62, 1.0); ctx.fill()
        if z > 0.9:
            p = (u * 0.9) % 1
            ctx.set_source_rgba(*YEL, 1 - p); ctx.set_line_width(4); circle(ctx, dx, dy, 12 + 55 * p); ctx.stroke()


# ---------- scene 6 ----------
ICE = [(random.Random(k).uniform(-100, 2020), random.Random(k + 99).uniform(220, 1040), random.Random(k + 7).uniform(12, 50), k) for k in range(140)]


def ice_chunk(ctx, x, y, s, k, a):
    rnd = random.Random(k); n = rnd.randint(5, 8)
    for i in range(n):
        ang = 2 * math.pi * i / n; rr = s * rnd.uniform(0.6, 1.0)
        (ctx.move_to if i == 0 else ctx.line_to)(x + rr * math.cos(ang), y + rr * math.sin(ang))
    ctx.close_path(); ctx.set_source_rgba(0.85, 0.95, 1, a); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(2); ctx.stroke()


def scene6(ctx, t):
    u = t - 80
    R, X, Y = 260, 960, 600
    zin = ease(cl((u - 0.4) / 2.2)) * (1 - ease(cl((u - 9.0) / 1.4)))
    tilt = lerp(0.32, 0.0, ease(cl((u - 10.4) / 2.0)))
    zs = lerp(1, 6, zin)
    ctx.save(); ctx.translate(X, Y); ctx.scale(zs, zs); ctx.translate(-lerp(X, X + 1.75 * R, zin), -Y)
    planet(ctx, X, Y, R, "saturn", tilt=tilt)
    ctx.restore()
    ia = cl((u - 2.4) / 0.7) * (1 - cl((u - 8.6) / 0.6))
    if ia > 0:
        for x, y, s, k in ICE:
            ice_chunk(ctx, (x + u * (25 + s)) % 2120 - 100, y + 6 * math.sin(u + k), s, k, ia * 0.9)
    if u > 12.4:
        a = ease(cl((u - 12.4) / 0.6))
        ctx.set_source_rgba(1, 1, 1, 0.8 * a); ctx.set_line_width(3)
        ctx.move_to(X - 2.15 * R, Y - 120); ctx.line_to(X + 2.15 * R, Y - 120); ctx.stroke()
        for sg in (-1, 1): ctx.move_to(X + sg * 2.15 * R, Y - 135); ctx.line_to(X + sg * 2.15 * R, Y - 105); ctx.stroke()
        label(ctx, "280,000 KM", X, Y - 165, 46, alpha=a)
        m = ease(cl((u - 13.6) / 0.6))
        if m > 0:
            mx, my, mr = 960, 870, 150
            ctx.set_source_rgba(1, 1, 1, 0.6 * m); ctx.set_line_width(3)
            ctx.move_to(X + 1.9 * R, Y + 4); ctx.line_to(mx + mr * 0.75, my - mr * 0.65); ctx.stroke()
            ctx.save(); circle(ctx, mx, my, mr * m); ctx.clip()
            ctx.set_source_rgb(0.05, 0.03, 0.14); ctx.paint()
            ctx.set_source_rgb(0.93, 0.84, 0.62); ctx.rectangle(mx - 200, my + 20, 400, 24); ctx.fill()
            hx, hy = mx + 30, my + 20
            ctx.set_source_rgb(*PINK); ctx.rectangle(hx, hy - 55, 48, 55); ctx.fill()
            ctx.move_to(hx - 8, hy - 55); ctx.line_to(hx + 24, hy - 84); ctx.line_to(hx + 56, hy - 55); ctx.close_path(); ctx.fill()
            ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(3); ctx.move_to(mx - 60, my + 20); ctx.line_to(mx - 60, my + 44); ctx.stroke()
            label(ctx, "10 M", mx - 115, my + 32, 32)
            ctx.restore()
            ctx.set_source_rgba(1, 1, 1, m); ctx.set_line_width(5); circle(ctx, mx, my, mr * m); ctx.stroke()


def scene7(ctx, t):
    u = t - 100
    w = ease(cl((u - 2.0) / 4.0))
    tank(ctx, 12 + u, saturn_alpha=1 - w, wisps=w)


TEXT = [(0, 3.6, "WHICH PLANET FLOATS?", (1, 1, 1), 84), (4.2, 9.7, "SATURN.", YEL, 110),
        (10.2, 15.7, "WHY?", (1, 1, 1), 100), (22.2, 27.7, "LIGHTER THAN WATER", YEL, 84),
        (29.5, 37.5, "MOSTLY GAS", (1, 1, 1), 90), (38.5, 45.6, "LIGHT AS A BALLOON", PINK, 84),
        (55.6, 61.6, "764 EARTHS INSIDE", YEL, 84), (62.4, 67.2, "ALL EARTH'S OCEANS", CYAN, 84),
        (70.5, 79.6, "NOT ENOUGH WATER", YEL, 84), (83.2, 88.8, "RINGS = WATER ICE", CYAN, 84),
        (93.8, 99.6, "~10 METERS THIN", YEL, 84), (103, 108.5, "IN THEORY.", (1, 1, 1), 96)]


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx)
    si = max(i for i, s in enumerate(SC) if t >= s)
    u = t - SC[si]
    k = 1 + 0.035 * ease(cl(u / 18))           # slow push-in for motion
    ctx.save(); ctx.translate(W / 2, H * 0.56); ctx.scale(k, k); ctx.translate(-W / 2, -H * 0.56)
    [tank, scene2, scene3, scene4, scene5, scene6, scene7][si](ctx, t)
    ctx.restore()
    if t > 108.5:  # end card
        a = ease(cl((t - 108.5) / 1.0))
        ctx.set_source_rgba(0.05, 0.02, 0.12, 0.85 * a); ctx.paint()
        planet(ctx, 960, 540, 90, "saturn", a, tilt=0.3)
    for t0, t1, s, col, size in TEXT:
        a = window(t, t0, t1, 0.25)
        if a > 0: pill(ctx, s, TY, size, col=col, alpha=a)
    f = max([0] + [1 - abs(t - b) / 0.22 for b in SC[1:]])
    if f > 0: ctx.set_source_rgba(0.05, 0.02, 0.12, 0.9 * f); ctx.paint()
    progress(ctx, t, DUR)


# ---------- audio: calm ambient pad + soft cues ----------
def pad(tr, dur, vol=0.05):
    chords = [[0, 3, 7, 10], [-4, 0, 3, 7], [-7, -3, 0, 5], [-5, -1, 2, 7]]  # Am7 Fmaj7 Dm-ish Em-ish (semitones from A)
    seg, ov = 9.0, 3.0
    n = int(dur / seg) + 1
    for i in range(n):
        L = seg + ov; tt = np.arange(int(SR * L)) / SR
        env = np.sin(np.pi * np.clip(tt / L, 0, 1)) ** 2
        sig = np.zeros_like(tt)
        for st in chords[i % 4]:
            f = 220 * 2 ** (st / 12)
            for det, a in [(1.0, 1.0), (1.003, 0.7), (0.5, 0.6), (2.0, 0.12)]:
                sig += a * np.sin(2 * np.pi * f * det * tt + st)
        sig *= (0.85 + 0.15 * np.sin(2 * np.pi * 0.15 * tt))
        tr.add(vol * env * sig / 8, i * seg - ov / 2 if i else 0)


def chime(f, amp=0.06, d=2.5):
    tt = np.arange(int(SR * d)) / SR
    return amp * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.01 * tt)) * np.exp(-tt * 2.2) * (1 - np.exp(-tt * 200))


def audio(path):
    tr = Track(DUR)
    pad(tr, DUR)
    for kind, x, r, t0 in DROPS:
        th = t0 + t_hit(r)
        tr.add(pk.splash(0.10, 0.6), th); tr.add(pk.plop(120 if kind != "saturn" else 240, 0.14), th)
        if kind != "saturn":
            for k in range(4): tr.add(pk.bubble(0.03), th + 0.3 + k * 0.3)
    for b in SC[1:]: tr.add(whoosh(0.5, 0.035, seed=b), b - 0.3)
    for tt, f in [(4.2, 880), (22.2, 988), (29.5, 660), (55.6, 1046), (70.5, 784), (83.2, 1175), (93.8, 880), (103, 660)]:
        tr.add(chime(f), tt)
    for i in range(8): tr.add(chime(440 * 2 ** ([0, 2, 3, 5, 7, 8, 10, 12][i] / 12), 0.025, 1.2), 16.4 + i * 0.55)
    for k in range(14): tr.add(chime(1320 + 40 * k, 0.015, 0.6), 46.8 + 8.5 * ((k + 1) / 14) ** (1 / 1.5))
    tr.add(pk.soft_noise(4.0, 80, 0.03), 62.5)
    tr.add(pk.soft_noise(6.0, 30, 0.02), 82.6)
    tr.add(pk.soft_noise(4.0, 60, 0.03), 102)
    tr.add(chime(440, 0.05, 4), 108.8)
    tr.save(path, DUR)


def thumbnail(out):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(s)
    bg(ctx)
    ctx.save(); ctx.translate(960, 640); ctx.scale(1.12, 1.12); ctx.translate(-960, -640); tank(ctx, 8.0); ctx.restore()
    label(ctx, "IT FLOATS?!", 960, 150, 190, col=YEL, shadow=0.6)
    ctx.set_source_rgb(*YEL); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(1470, 230); ctx.curve_to(1560, 260, 1590, 330, 1560, 400); ctx.stroke()
    ctx.move_to(1530, 370); ctx.line_to(1560, 410); ctx.line_to(1595, 375); ctx.stroke()
    s.write_to_png("thumb_full.png")
    from PIL import Image
    Image.open("thumb_full.png").convert("RGB").resize((1280, 720), Image.LANCZOS).save(out, quality=92)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "l2")
    elif sys.argv[1] == "thumb":
        thumbnail("l2_thumb.jpg")
    else:
        audio("l2.wav"); encode(draw, NF, "l2_v.mp4"); mux("l2_v.mp4", "l2.wav", "l2_saturn.mp4")
