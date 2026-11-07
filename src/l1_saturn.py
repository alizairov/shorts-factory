"""3-minute Fact story: Which planet would float? (Saturn) — 7 visual scenes, minimal text."""
import sys, math, random
import numpy as np, cairo
from story import *
import paperkit as pk

DUR = 180.0
NF = int(DUR * FPS)
B = [15, 45, 75, 105, 135, 165]
CX, CY = 540, 1060

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
        base = tuple(lerp(land[i], c[i], ocean) for i in range(3))
        ctx.set_source_rgba(*base, alpha); ctx.paint()
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


# ---------- scene 1 / 7: the tank ----------
TX0, TX1, TY0, TY1, WL = 150, 930, 800, 1560, 980
DROPS = [("jupiter", 330, 92, 0.2), ("earth", 540, 46, 2.6), ("mars", 650, 32, 4.6), ("saturn", 790, 70, 7.0)]


def drop_y(kind, r, t, t0):
    y0, g = 640 - r, 2600
    u = t - t0
    if u <= 0: return y0
    hit = math.sqrt(2 * (WL - y0) / g)
    if u < hit: return y0 + 0.5 * g * u * u
    v = u - hit
    if kind == "saturn":
        return WL - 0.15 * r + 38 * math.exp(-1.6 * v) * math.cos(5 * v)
    bottom = TY1 - r - 8
    return bottom - (bottom - WL) * math.exp(-1.5 * v)


def tank(ctx, t, saturn_alpha=1.0, wisps=0.0):
    # water
    ctx.move_to(TX0, TY1)
    for xx in range(TX0, TX1 + 1, 20):
        ctx.line_to(xx, WL + 5 * math.sin(xx * 0.02 + t * 2.0))
    ctx.line_to(TX1, TY1); ctx.close_path()
    g = cairo.LinearGradient(0, WL, 0, TY1); g.add_color_stop_rgba(0, 0.24, 0.94, 1, 0.42); g.add_color_stop_rgba(1, 0.1, 0.3, 0.9, 0.55)
    ctx.set_source(g); ctx.fill()
    for kind, x, r, t0 in DROPS:
        y = drop_y(kind, r, t, t0)
        a = saturn_alpha if kind == "saturn" else 1.0
        if a > 0.01: planet(ctx, x, y, r, kind, a)
        u = t - t0 - math.sqrt(2 * (WL - 640 + r) / 2600)
        if 0 < u < 0.9:  # splash ring
            ctx.save(); ctx.translate(x, WL); ctx.scale(1, 0.22)
            ctx.arc(0, 0, r + 220 * eout(u / 0.9), 0, 2 * math.pi); ctx.restore()
            ctx.set_source_rgba(1, 1, 1, 0.7 * (1 - u / 0.9)); ctx.set_line_width(4); ctx.stroke()
        if kind != "saturn" and 0 < u < 4:  # bubbles while sinking
            rnd = random.Random(int(x))
            for k in range(8):
                bu = (u * 0.8 + k / 8) % 1
                bx = x + rnd.uniform(-r, r) + 8 * math.sin(t * 3 + k)
                by = y - bu * (y - WL)
                ctx.set_source_rgba(1, 1, 1, 0.5 * (1 - bu) * cl(1 - u / 4)); circle(ctx, bx, by, 5); ctx.fill()
    if wisps > 0:
        rnd = random.Random(3)
        for k in range(220):
            ang = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0.2, 1) * 330 * wisps
            px = 790 + math.cos(ang) * d * 1.3 + 10 * math.sin(t + k)
            py = max(WL + 5, WL + math.sin(ang) * d * 0.6 + 60 * wisps)
            ctx.set_source_rgba(0.96, 0.86, 0.56, 0.6 * (1 - wisps) + 0.15); circle(ctx, px, py, rnd.uniform(3, 9)); ctx.fill()
    # glass
    ctx.set_source_rgba(1, 1, 1, 0.65); ctx.set_line_width(6); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(TX0, TY0); ctx.line_to(TX0, TY1); ctx.line_to(TX1, TY1); ctx.line_to(TX1, TY0); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.12); ctx.rectangle(TX0 + 18, TY0 + 20, 14, TY1 - TY0 - 60); ctx.fill()


# ---------- scene 2: scale + density bars ----------
DENS = [("earth", 5.51), ("mercury", 5.43), ("venus", 5.24), ("mars", 3.93), ("neptune", 1.64), ("jupiter", 1.33), ("uranus", 1.27), ("saturn", 0.69)]


def cube(ctx, x, y, s, col, stripes=False, waves=False):
    ctx.set_source_rgb(*col); ctx.rectangle(x - s / 2, y - s, s, s); ctx.fill()
    ctx.set_source_rgba(*lighten(col, 0.25), 1); ctx.move_to(x - s / 2, y - s); ctx.line_to(x - s / 2 + 22, y - s - 22)
    ctx.line_to(x + s / 2 + 22, y - s - 22); ctx.line_to(x + s / 2, y - s); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(*lighten(col, -0.25), 1); ctx.move_to(x + s / 2, y - s); ctx.line_to(x + s / 2 + 22, y - s - 22)
    ctx.line_to(x + s / 2 + 22, y - 22); ctx.line_to(x + s / 2, y); ctx.close_path(); ctx.fill()
    ctx.save(); ctx.rectangle(x - s / 2, y - s, s, s); ctx.clip()
    if stripes:
        for i in range(5):
            ctx.set_source_rgba(*lighten(col, -0.15), 0.7); ctx.rectangle(x - s / 2, y - s + i * s / 5 + 6, s, s / 12); ctx.fill()
    if waves:
        ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(4)
        for i in range(3):
            yy = y - s * 0.75 + i * s * 0.25
            ctx.move_to(x - s / 2, yy)
            for k in range(13): ctx.line_to(x - s / 2 + k * s / 12, yy + 6 * math.sin(k * 1.4))
            ctx.stroke()
    ctx.restore()


def scene2(ctx, t):
    if t < 25:
        u = t - 15
        th = -0.16 * ease(cl((u - 3.0) / 1.5)) + 0.02 * math.sin(u * 3) * math.exp(-max(0, u - 4.5))
        px, py, L = 540, 1000, 300
        ctx.set_source_rgba(1, 1, 1, 0.8); ctx.move_to(px, py); ctx.line_to(px - 70, 1420); ctx.line_to(px + 70, 1420); ctx.close_path(); ctx.fill()
        ends = [(px - L * math.cos(th), py - L * math.sin(th)), (px + L * math.cos(th), py + L * math.sin(th))]
        ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(*ends[0]); ctx.line_to(*ends[1]); ctx.stroke()
        for i, (ex, ey) in enumerate(ends):
            pyb = ey + 180
            ctx.set_source_rgba(1, 1, 1, 0.6); ctx.set_line_width(3)
            ctx.move_to(ex, ey); ctx.line_to(ex - 100, pyb); ctx.move_to(ex, ey); ctx.line_to(ex + 100, pyb); ctx.stroke()
            ctx.set_source_rgba(1, 1, 1, 0.85); ctx.set_line_width(8); ctx.move_to(ex - 120, pyb); ctx.line_to(ex + 120, pyb); ctx.stroke()
            dropin = eout(cl((u - 0.4 - i * 0.6) / 0.6))
            yy = pyb - 6 - (1 - dropin) * 500
            if i == 0: cube(ctx, ex, yy, 150, (0.15, 0.6, 1.0), waves=True)
            else:
                cube(ctx, ex, yy, 150, PC["saturn"], stripes=True)
                planet(ctx, ex, yy - 230, 34, "saturn", dropin)
        circle(ctx, px, py, 16); ctx.set_source_rgb(*YEL); ctx.fill()
        return
    u = t - 25
    x0, sc = 210, 140
    wx = x0 + sc
    for i, (k, d) in enumerate(DENS):
        y = 770 + i * 92
        g = ease(cl((u - 0.5 - i * 1.3) / 1.0))
        dim = 1.0 if u < 14 or k == "saturn" else 0.35
        planet(ctx, 120, y, 30, k, dim, tilt=0.3)
        col = YEL if k == "saturn" else PAL[i % 6]
        card(ctx, x0, y - 22, max(1, d * sc * g), 44, 22, (*col, 0.85 * dim))
        if g > 0.9: label(ctx, f"{d:.2f}", x0 + d * sc + 18, y, 34, alpha=dim * cl((g - 0.9) * 10), anchor="l")
    ctx.set_source_rgba(0.3, 0.95, 1, 0.9); ctx.set_line_width(5); ctx.set_dash([18, 12])
    ctx.move_to(wx, 720); ctx.line_to(wx, 1460); ctx.stroke(); ctx.set_dash([])
    label(ctx, "WATER = 1", wx, 690, 34, col=CYAN)
    if u > 14:
        a = ease(cl((u - 14) / 0.5)); y = 770 + 7 * 92
        ctx.set_source_rgba(*YEL, 0.25 * a * (0.7 + 0.3 * math.sin(u * 5))); card(ctx, 70, y - 50, 940, 100, 50, (*YEL, 0.18 * a))


# ---------- scene 3: cutaway ----------
def scene3(ctx, t):
    u = t - 45
    R = 260
    cut = ease(cl((u - 1.0) / 2.0)) * math.pi / 2
    planet(ctx, CX, CY, R, "saturn", tilt=0.22)
    if cut > 0.01:
        ctx.save(); ctx.move_to(CX, CY); ctx.arc(CX, CY, R, -math.pi / 2, -math.pi / 2 + cut); ctx.close_path(); ctx.clip()
        for rr, c in [(1.0, (0.12, 0.08, 0.3)), (0.62, (0.3, 0.2, 0.5)), (0.2, (0.55, 0.35, 0.25))]:
            circle(ctx, CX, CY, R * rr); ctx.set_source_rgb(*c); ctx.fill()
        rnd = random.Random(5)
        for k in range(160):
            rr = R * rnd.uniform(0.22, 0.98); a0 = rnd.uniform(-math.pi / 2, 0)
            ang = a0 + 0.08 * math.sin(u * 0.7 + k)
            x = CX + rr * math.cos(ang); y = CY + rr * math.sin(ang)
            he = k % 7 == 0
            ctx.set_source_rgba(*(PINK if he else (1, 1, 1)), 0.85); circle(ctx, x, y, 7 if he else 5); ctx.fill()
        ctx.restore()
        ctx.set_source_rgba(1, 1, 1, 0.8); ctx.set_line_width(3)
        ctx.move_to(CX, CY - R); ctx.line_to(CX, CY); ctx.line_to(CX + R, CY); ctx.stroke()
        rings(ctx, CX, CY, R, 0.22, True)
    if u > 17:  # helium balloon rising next to it
        b = u - 17
        bx, by = 180 + 15 * math.sin(b * 1.3), 1500 - 60 * b
        ctx.set_source_rgba(1, 1, 1, 0.6); ctx.set_line_width(2); ctx.move_to(bx, by + 70); ctx.curve_to(bx - 15, by + 120, bx + 15, by + 160, bx, by + 200); ctx.stroke()
        ctx.save(); ctx.translate(bx, by); ctx.scale(0.85, 1); circle(ctx, 0, 0, 70); ctx.restore()
        ctx.set_source_rgb(*PINK); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.35); circle(ctx, bx - 22, by - 25, 16); ctx.fill()
        label(ctx, "He", bx, by + 5, 44)


# ---------- scene 4: 764 Earths ----------
R4 = 380


def _pack():
    d = 26.0
    while True:
        pts = []
        for j in range(-30, 31):
            for i in range(-30, 31):
                x = (i + 0.5 * (j % 2)) * d; y = j * d * 0.866
                if x * x + y * y < (R4 - d * 0.55) ** 2: pts.append((x, y))
        if len(pts) >= 764: break
        d -= 0.3
    rnd = random.Random(2)
    pts.sort(key=lambda p: -p[1] + rnd.uniform(-12, 12))
    return pts[:764], d


PACK, PD = _pack()


def scene4(ctx, t):
    u = t - 75
    planet(ctx, CX, CY, R4, "saturn", alpha=0.25 + 0.75 * (1 - cl((u - 1) / 1.5)), tilt=0.2)
    ctx.set_source_rgba(*YEL, 0.8); ctx.set_line_width(4); circle(ctx, CX, CY, R4); ctx.stroke()
    n = int(764 * cl((u - 2.5) / 15.0) ** 1.6)
    for k in range(n):
        x, y = PACK[k]
        age = (u - 2.5) - 15.0 * (k / 764) ** (1 / 1.6)
        s = pop(cl(age / 0.35)) if age < 0.35 else 1
        planet(ctx, CX + x, CY + y, PD * 0.46 * s, "earth")
    if u > 2.5:
        label(ctx, f"{n}", CX, 600, 120, col=YEL if n == 764 else (1, 1, 1))


# ---------- scene 5: all oceans vs Saturn ----------
def drop_shape(ctx, x, y, r):
    ctx.move_to(x, y - 2.0 * r)
    ctx.curve_to(x + 0.6 * r, y - 1.1 * r, x + r, y - 0.6 * r, x + r, y)
    ctx.arc(x, y, r, 0, math.pi)
    ctx.curve_to(x - r, y - 0.6 * r, x - 0.6 * r, y - 1.1 * r, x, y - 2.0 * r); ctx.close_path()


def scene5(ctx, t):
    u = t - 105
    drain = ease(cl((u - 1.5) / 6.0))
    z = ease(cl((u - 10.0) / 5.0))
    s = lerp(1.0, 41.6 / 300, z)
    ex = lerp(CX, 115, z); ey = CY
    dr = 32 * drain ** (1 / 3)
    dx, dy = ex + lerp(0, 0, z), ey - (300 + 90) * s
    if z > 0:
        sr = 9.14 * 300 * s
        sx = lerp(CX + 2700, 645, z)
        planet(ctx, sx, ey, sr, "saturn", tilt=0.18, ring=False)
        if u > 17:  # the tub you would need
            a = ease(cl((u - 17) / 0.8))
            ctx.set_source_rgba(0.3, 0.95, 1, 0.8 * a); ctx.set_line_width(5); ctx.set_dash([20, 14])
            ctx.move_to(sx - sr - 40, ey - sr - 60); ctx.line_to(sx - sr - 40, ey + sr + 40); ctx.line_to(sx + sr + 40, ey + sr + 40)
            ctx.line_to(sx + sr + 40, ey - sr - 60); ctx.stroke(); ctx.set_dash([])
    planet(ctx, ex, ey, 300 * s, "earth", ocean=1 - drain)
    if drain > 0.01:
        drop_shape(ctx, dx, dy - (1 - z) * 40 * drain, max(1.5, dr * s))
        ctx.set_source_rgb(0.2, 0.62, 1.0); ctx.fill()
        if z > 0.9:
            p = (u * 0.9) % 1
            ctx.set_source_rgba(*YEL, 1 - p); ctx.set_line_width(4); circle(ctx, dx, dy, 12 + 50 * p); ctx.stroke()


# ---------- scene 6: rings ----------
ICE = [(random.Random(k).uniform(-100, 1180), random.Random(k + 99).uniform(740, 1420), random.Random(k + 7).uniform(10, 46), k) for k in range(90)]


def ice_chunk(ctx, x, y, s, k, a):
    rnd = random.Random(k)
    n = rnd.randint(5, 8)
    for i in range(n):
        ang = 2 * math.pi * i / n; rr = s * rnd.uniform(0.6, 1.0)
        (ctx.move_to if i == 0 else ctx.line_to)(x + rr * math.cos(ang), y + rr * math.sin(ang))
    ctx.close_path(); ctx.set_source_rgba(0.85, 0.95, 1, a); ctx.fill_preserve()
    ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(2); ctx.stroke()


def scene6(ctx, t):
    u = t - 135
    R = 200
    zin = ease(cl((u - 1.5) / 4.0)) * (1 - ease(cl((u - 15.0) / 2.0)))
    tilt = lerp(0.32, 0.0, ease(cl((u - 17.5) / 3.5)))
    zs = lerp(1, 7, zin)
    fx, fy = CX + 1.75 * R, CY + 0.32 * 1.75 * R * 0.0
    ctx.save(); ctx.translate(CX, CY); ctx.scale(zs, zs); ctx.translate(-lerp(CX, fx, zin), -CY)
    planet(ctx, CX, CY, R, "saturn", tilt=tilt)
    ctx.restore()
    ia = cl((u - 5.0) / 1.0) * (1 - cl((u - 14.0) / 1.0))
    if ia > 0:
        for x, y, s, k in ICE:
            xx = (x + u * (18 + s)) % 1280 - 100
            ice_chunk(ctx, xx, y + 6 * math.sin(u + k), s, k, ia * 0.9)
    if u > 21.5:  # width arrow + magnifier on the thin edge
        a = ease(cl((u - 21.5) / 0.8))
        ctx.set_source_rgba(1, 1, 1, 0.8 * a); ctx.set_line_width(3)
        ctx.move_to(CX - 2.15 * R, CY - 110); ctx.line_to(CX + 2.15 * R, CY - 110); ctx.stroke()
        for sgn in (-1, 1):
            ctx.move_to(CX + sgn * 2.15 * R, CY - 125); ctx.line_to(CX + sgn * 2.15 * R, CY - 95); ctx.stroke()
        label(ctx, "280,000 KM", CX, CY - 150, 40, alpha=a)
        m = ease(cl((u - 23) / 0.8))
        if m > 0:
            mx, my, mr = 540, 1300, 130
            ctx.set_source_rgba(1, 1, 1, 0.6 * m); ctx.set_line_width(3)
            ctx.move_to(CX + 1.9 * R, CY + 4); ctx.line_to(mx + mr * 0.7, my - mr * 0.7); ctx.stroke()
            ctx.save(); circle(ctx, mx, my, mr * m); ctx.clip()
            ctx.set_source_rgb(0.05, 0.03, 0.14); ctx.paint()
            ctx.set_source_rgb(0.93, 0.84, 0.62); ctx.rectangle(mx - 200, my + 10, 400, 22); ctx.fill()
            # tiny house standing on the ring slab, taller than the ring is thick
            hx, hy = mx + 40, my + 10
            ctx.set_source_rgb(*PINK); ctx.rectangle(hx, hy - 50, 44, 50); ctx.fill()
            ctx.move_to(hx - 8, hy - 50); ctx.line_to(hx + 22, hy - 76); ctx.line_to(hx + 52, hy - 50); ctx.close_path(); ctx.fill()
            ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(3)
            ctx.move_to(mx - 60, my + 10); ctx.line_to(mx - 60, my + 32); ctx.stroke()
            label(ctx, "10 M", mx - 120, my + 21, 30)
            ctx.restore()
            ctx.set_source_rgba(1, 1, 1, m); ctx.set_line_width(5); circle(ctx, mx, my, mr * m); ctx.stroke()


# ---------- scene 7 ----------
def scene7(ctx, t):
    u = t - 165
    w = ease(cl((u - 5.0) / 5.0))
    tank(ctx, 20 + u, saturn_alpha=1 - w, wisps=w)


TEXT = [(0, 6.5, "WHICH PLANET FLOATS?", (1, 1, 1), 76), (8.8, 14.6, "SATURN.", YEL, 110),
        (16, 24.5, "WHY?", (1, 1, 1), 110), (39, 44.6, "LIGHTER THAN WATER", YEL, 80),
        (47.5, 61, "MOSTLY GAS", (1, 1, 1), 96), (90, 104.6, "764 EARTHS INSIDE", YEL, 80),
        (106.5, 114, "ALL EARTH'S OCEANS", CYAN, 80), (122.5, 134.6, "NOT ENOUGH WATER", YEL, 80),
        (141.5, 149.5, "RINGS = WATER ICE", CYAN, 80), (158, 164.6, "~10 METERS THIN", YEL, 80),
        (170, 176, "IN THEORY.", (1, 1, 1), 96), (177.2, 999, "WHICH PLANET FLOATS?", (1, 1, 1), 76)]


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx)
    if t < 15: tank(ctx, t)
    elif t < 45: scene2(ctx, t)
    elif t < 75: scene3(ctx, t)
    elif t < 105: scene4(ctx, t)
    elif t < 135: scene5(ctx, t)
    elif t < 165: scene6(ctx, t)
    elif t < 177: scene7(ctx, t)
    else:  # loop back to frame 0
        k = ease(cl((t - 177) / 1.2))
        if k < 1:
            ctx.push_group(); scene7(ctx, t); ctx.pop_group_to_source(); ctx.paint_with_alpha(1 - k)
        ctx.push_group(); tank(ctx, 0); ctx.pop_group_to_source(); ctx.paint_with_alpha(k)
    for t0, t1, s, col, size in TEXT:
        a = window(t, t0, t1) if t1 < 900 else fade_in(t, t0)
        if a > 0: pill(ctx, s, 330, size, col=col, alpha=a)
    f = max([0] + [1 - abs(t - b) / 0.35 for b in B])
    if f > 0:
        ctx.set_source_rgba(0.05, 0.02, 0.12, 0.92 * f); ctx.paint()
    progress(ctx, t, DUR)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=76, seed=31, vol=0.32, base=196)
    for kind, x, r, t0 in DROPS:
        th = t0 + math.sqrt(2 * (WL - 640 + r) / 2600)
        for off in (0, 165):
            if kind == "saturn" and off: continue
            tr.add(pk.splash(0.16, 0.6), th + off)
            tr.add(pk.plop(140 if kind != "saturn" else 260, 0.22), th + off)
            if kind != "saturn":
                for k in range(5): tr.add(pk.bubble(0.04), th + off + 0.4 + k * 0.35)
    tr.add(ding(12, 0.12), 8.8)
    for b in B: tr.add(whoosh(0.5, 0.06, seed=b), b - 0.3)
    tr.add(pluck(note(2, 196), 0.6, 0.12, 5), 15.4); tr.add(pluck(note(4, 196), 0.6, 0.12, 5), 16.0)
    tr.add(pluck(note(0, 130.8), 1.2, 0.16, 3), 18.2)
    for i in range(8): tr.add(pluck(note(9 - i, 392), 0.5, 0.09, 7), 25.6 + i * 1.3)
    tr.add(ding(14, 0.13), 39)
    tr.add(riser(2.0, 0.05), 45.5); tr.add(ding(9, 0.1), 48)
    for k in range(40):
        tt = 77.5 + 15.0 * ((k + 1) / 40) ** (1 / 1.6)
        tr.add(pluck(note(k % 10, 523.25), 0.25, 0.05, 12), tt)
    tr.add(ding(16, 0.14), 92.6)
    tr.add(pk.soft_noise(5.0, 60, 0.05), 106.5); tr.add(riser(2.5, 0.05), 115); tr.add(ding(7, 0.12), 122.5)
    tr.add(pk.soft_noise(8.0, 20, 0.03), 140)
    for k in range(6): tr.add(pluck(note(12 + k, 523.25), 0.3, 0.05, 10), 141 + k * 1.3)
    tr.add(ding(11, 0.12), 158)
    tr.add(pk.soft_noise(5.0, 40, 0.05), 170); tr.add(ding(5, 0.1), 170)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "l1")
    else:
        audio("l1.wav"); encode(draw, NF, "l1_v.mp4"); mux("l1_v.mp4", "l1.wav", "l1_saturn.mp4")
