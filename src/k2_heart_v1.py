"""Flat-vector explainer: your heart beats about 100,000 times a day."""
import sys, math, random
import numpy as np, cairo
import k1_stomach as K
from k1_stomach import *

DUR = 15.0
NF = int(DUR * FPS)
RED, RED2 = (0.95, 0.20, 0.32), (0.75, 0.10, 0.25)
BPM = 72
P = 60 / BPM
K.STOM = (610, 1050)


def beat(t):
    u = t % P
    return math.exp(-(u / 0.07) ** 2) + 0.6 * math.exp(-((u - 0.22) / 0.06) ** 2)


def heart_path(ctx, x, y, s):
    ctx.move_to(x, y + 95 * s)
    ctx.curve_to(x - 150 * s, y - 10 * s, x - 110 * s, y - 120 * s, x - 50 * s, y - 115 * s)
    ctx.curve_to(x - 15 * s, y - 112 * s, x, y - 85 * s, x, y - 70 * s)
    ctx.curve_to(x, y - 85 * s, x + 15 * s, y - 112 * s, x + 50 * s, y - 115 * s)
    ctx.curve_to(x + 110 * s, y - 120 * s, x + 150 * s, y - 10 * s, x, y + 95 * s); ctx.close_path()


def organ(ctx, x, y, t, xray):
    s = 0.62 * (1 + 0.09 * beat(t))
    g = cairo.RadialGradient(x, y, 10, x, y, 220)
    g.add_color_stop_rgba(0, 1, 0.5, 0.6, 0.55 * (0.4 + 0.6 * beat(t))); g.add_color_stop_rgba(1, 1, 0.5, 0.6, 0)
    ctx.set_source(g); ell(ctx, x, y, 220, 220); ctx.fill()
    a = 0.25 + 0.75 * xray
    heart_path(ctx, x, y, s * 1.08); ctx.set_source_rgba(1, 0.92, 0.85, a); ctx.fill()
    heart_path(ctx, x, y, s); ctx.set_source_rgba(*RED, a); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.35 * a); ell(ctx, x - 45 * s, y - 60 * s, 22 * s, 30 * s); ctx.fill()


K.ORGAN = organ


def valve_view(ctx, cx, cy, R, t):
    ctx.set_source_rgb(0.30, 0.06, 0.18); ctx.paint()
    # vessel walls
    ctx.set_source_rgb(*RED2); ctx.rectangle(cx - R, cy - R, R * 0.55, 2 * R); ctx.fill(); ctx.rectangle(cx + R * 0.45, cy - R, R * 0.55, 2 * R); ctx.fill()
    # blood cells flowing upward, faster when the valve is open
    u = (t % P) / P
    openk = math.sin(math.pi * cl(u / 0.45)) if u < 0.45 else 0.0
    rnd = random.Random(7)
    flow = t * 160 + 120 * math.floor(t / P)
    for k in range(26):
        x = cx + rnd.uniform(-R * 0.38, R * 0.38)
        y = cy + R - ((rnd.uniform(0, 2 * R) + flow + 220 * openk * rnd.random()) % (2 * R))
        if abs(y - cy) < 30 and openk < 0.2: continue
        ctx.set_source_rgb(*RED); ell(ctx, x, y, 22, 14); ctx.fill()
        ctx.set_source_rgb(*RED2); ell(ctx, x, y, 10, 5); ctx.fill()
    # two valve flaps hinged on the walls
    for sd in (-1, 1):
        hx = cx + sd * R * 0.45 * (1 if sd > 0 else 1)
        hx = cx - R * 0.45 if sd < 0 else cx + R * 0.45
        ang = (math.pi / 2 - 0.15) * openk
        tipx = hx - sd * R * 0.46 * math.cos(ang)
        tipy = cy - R * 0.46 * math.sin(ang)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(30)
        ctx.set_source_rgb(1, 0.85, 0.75); ctx.move_to(hx, cy); ctx.line_to(tipx, tipy); ctx.stroke()


def magnifier(ctx, t, a, k):
    mx, my, R = 540, 780, 270
    sx, sy = 540, 1500
    ctx.set_source_rgba(*LIME, a); ctx.set_line_width(14)
    ctx.move_to(sx, sy); ctx.line_to(mx, my + R * k); ctx.stroke(); ell(ctx, sx, sy, 24 * k, 24 * k); ctx.fill()
    ctx.save(); ell(ctx, mx, my, R * k, R * k); ctx.clip()
    ctx.push_group(); valve_view(ctx, mx, my, R, t); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()
    ctx.set_source_rgba(*LIME, a); ctx.set_line_width(16); ell(ctx, mx, my, R * k, R * k); ctx.stroke()
    return mx, my, R


def counter(t):
    u = cl((t - 9.6) / 2.4)
    return int(103680 * u ** 3)


def draw(ctx, fi):
    t = fi / FPS
    z = ease(cl((t - 2.9) / 1.4)) * (1 - ease(cl((t - 12.5) / 1.3)))
    g = cairo.LinearGradient(0, 0, 0, H)
    top = tuple(lerp(a, b, z) for a, b in zip((0.98, 0.45, 0.55), (0.36, 0.08, 0.30)))
    bot = tuple(lerp(a, b, z) for a, b in zip((1.0, 0.78, 0.55), (0.55, 0.12, 0.40)))
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot); ctx.set_source(g); ctx.paint()
    ctx.save(); ctx.translate(540, 1000)
    for k in range(14):
        ctx.rotate(math.pi / 7); ctx.move_to(0, 0); ctx.line_to(1400, -110); ctx.line_to(1400, 110); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.07 * (1 - z)); ctx.fill()
    ctx.restore()
    zoom = 1 + 3.4 * z
    fx, fy = lerp(540, K.STOM[0], z), lerp(1000, K.STOM[1], z)
    ctx.save(); ctx.translate(540, lerp(1000, 1500, z)); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy)
    K.character(ctx, t, z)
    ctx.restore()
    ma = cl((t - 5.0) / 0.25) * (1 - cl((t - 12.2) / 0.3))
    if ma > 0.01:
        mx, my, R = magnifier(ctx, t, ma, popk((t - 5.0) / 0.45))
        tagbox(ctx, "Valve", mx + 150, my - 60, 50, (0.95, 0.55, 0.30), a=ma * cl((t - 5.9) / 0.2), k=popk((t - 5.9) / 0.35))
        tagbox(ctx, "Blood", mx - 150, my + 160, 50, RED2, a=ma * cl((t - 6.6) / 0.2), k=popk((t - 6.6) / 0.35))
    tagbox(ctx, "Heart", 540, 1270, 64, RED2, a=cl((t - 4.2) / 0.2) * (1 - cl((t - 5.0) / 0.2)), k=popk((t - 4.2) / 0.35))
    # 24h clock next to the magnifier during the count
    if 9.4 < t < 12.4:
        a = cl((t - 9.4) / 0.2) * (1 - cl((t - 12.1) / 0.3)); cx, cy = 925, 650
        ctx.push_group()
        ctx.set_source_rgb(1, 1, 1); ell(ctx, cx, cy, 90, 90); ctx.fill()
        ctx.set_source_rgb(*RED2); ctx.set_line_width(10); ell(ctx, cx, cy, 90, 90); ctx.stroke()
        hand = 2 * math.pi * cl((t - 9.6) / 2.4) - math.pi / 2
        ctx.set_source_rgb(*INK); ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(cx, cy); ctx.line_to(cx + 65 * math.cos(hand), cy + 65 * math.sin(hand)); ctx.stroke()
        label(ctx, "24H", cx, cy + 135, 44, shadow=0.3)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    head_a = 1 - cl((t - 4.6) / 0.3) + cl((t - 13.4) / 0.3)
    tagbox(ctx, "HOW MANY BEATS", 540, 290, 80, (1, 1, 1), fg=RED2, a=head_a, pointer=False)
    tagbox(ctx, "IN ONE DAY?", 540, 400, 80, RED2, a=head_a, pointer=False)
    if 9.5 < t < 13.0:
        n = counter(t)
        a = cl((t - 9.5) / 0.2) * (1 - cl((t - 12.7) / 0.3))
        tagbox(ctx, f"{n:,}", 540, 400, 110 if n < 103680 else 120, (1, 1, 1), fg=RED2, a=a, k=popk((t - 12.0) / 0.4) if t > 12.0 else 1, pointer=False)
    ctx.set_source_rgb(1, 1, 1); ell(ctx, 130, 150, 66, 66); ctx.fill()
    ctx.set_source_surface(LOGO, 70, 90); ctx.paint()
    tagbox(ctx, "@Visual.Brainer", 360, 150, 38, (1, 1, 1), fg=INK, pointer=False)


def lubdub(amp=0.18):
    m = np.arange(int(SR * 0.18)) / SR
    return np.sin(2 * np.pi * 55 * m) * np.exp(-m * 28) * amp


def audio(path):
    tr = Track(DUR)
    pad(tr, DUR, 0.035)
    k = 0
    while k * P < DUR - 0.3:
        tt = k * P
        loud = 1.0 if (tt < 3 or 4.3 < tt < 12.5) else 0.6
        tr.add(lubdub(0.20 * loud), tt); tr.add(lubdub(0.13 * loud), tt + 0.22)
        k += 1
    tr.add(pk.whoosh(1.2, 0.08), 2.9); tr.add(pk.whoosh(1.2, 0.07), 12.5)
    for tt in (4.2, 5.0, 5.9, 6.6): tr.add(pop(0.11), tt)
    for i in range(24): tr.add(pop(0.03), 9.6 + 2.4 * ((i + 1) / 24) ** (1 / 3))
    tr.add(chime(1046, 0.08, 2.0), 12.0); tr.add(chime(1318, 0.05, 2.0), 12.1)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "k2b")
    else:
        audio("k2b.wav"); encode(draw, NF, "k2b_v.mp4"); mux("k2b_v.mp4", "k2b.wav", "k2_heart_103680.mp4")
