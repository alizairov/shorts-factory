"""Flat-vector explainer: bone vs concrete under a press — bone is ~4–5× stronger in compression."""
import sys, math, random
import numpy as np, cairo
import k1_stomach as K
from k1_stomach import *

DUR = 15.0
NF = int(DUR * FPS)
K.GLOW = False
K.ORGAN = lambda ctx, x, y, t, xray: None
K.T_SMILE, K.LOOK = 13.4, (99, 99)
BONE, BONE2 = (0.99, 0.95, 0.84), (0.90, 0.82, 0.66)
CONC, CONC2 = (0.66, 0.66, 0.68), (0.52, 0.52, 0.55)
STEEL, STEEL2 = (0.40, 0.46, 0.62), (0.28, 0.32, 0.46)
BASE_Y = 1380
COLS = [330, 750]          # concrete, bone
T_PRESS, T_CRACK, T_ZOOM = 2.6, 4.9, 7.6


def press_y(t):
    d = ease(cl((t - T_PRESS) / 2.0)) * (1 - ease(cl((t - 12.6) / 1.2)))
    return lerp(560, 780, d)


def bone_shape(ctx, x, top, bot, w):
    r = w * 0.42
    ctx.new_path()
    for yy in (top, bot):
        ctx.new_sub_path(); ctx.arc(x - r * 0.9, yy, r, 0, 2 * math.pi)
        ctx.new_sub_path(); ctx.arc(x + r * 0.9, yy, r, 0, 2 * math.pi)
    ctx.rectangle(x - w * 0.36, top, w * 0.72, bot - top)


def crack_pieces(t):
    """concrete: intact -> cracked -> pieces fall -> reassemble at the end (loop)"""
    c = cl((t - T_CRACK) / 0.25)
    fall = ease(cl((t - T_CRACK - 0.4) / 0.9)) * (1 - ease(cl((t - 13.0) / 1.0)))
    return c * (1 - ease(cl((t - 13.0) / 1.0))), fall


def scene(ctx, t):
    # floor + platform
    ctx.set_source_rgb(0.33, 0.18, 0.42); ctx.rectangle(-2000, BASE_Y + 40, 6000, 3000); ctx.fill()
    py = press_y(t)
    # press frame
    ctx.set_source_rgb(*STEEL2); rrect(ctx, 80, 380, 60, BASE_Y - 340, 20); ctx.fill(); rrect(ctx, 940, 380, 60, BASE_Y - 340, 20); ctx.fill()
    rrect(ctx, 60, 360, 960, 70, 24); ctx.fill()
    ctx.set_source_rgb(*STEEL); rrect(ctx, 500, 400, 80, py - 400, 10); ctx.fill()
    rrect(ctx, 150, py, 780, 70, 18); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.15); rrect(ctx, 165, py + 10, 750, 16, 8); ctx.fill()
    ctx.set_source_rgb(*STEEL2); rrect(ctx, 120, BASE_Y, 840, 60, 18); ctx.fill()
    top = py + 70
    squash = 6 * ease(cl((t - T_PRESS - 1.2) / 1.0))
    # concrete pillar
    c, fall = crack_pieces(t)
    x0, w = COLS[0], 220
    if fall < 0.02:
        ctx.set_source_rgb(*CONC); rrect(ctx, x0 - w / 2, top, w, BASE_Y - top, 10); ctx.fill()
        rnd = random.Random(2)
        for k in range(30):
            ctx.set_source_rgb(*CONC2); ell(ctx, x0 + rnd.uniform(-w / 2 + 15, w / 2 - 15), rnd.uniform(top + 15, BASE_Y - 15), rnd.uniform(4, 9), rnd.uniform(3, 7)); ctx.fill()
        if c > 0:
            ctx.set_source_rgba(*INK, c); ctx.set_line_width(7); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
            ctx.move_to(x0 - 20, top); ctx.line_to(x0 + 25, top + 140); ctx.line_to(x0 - 30, top + 290); ctx.line_to(x0 + 30, top + 450); ctx.line_to(x0 - 10, BASE_Y); ctx.stroke()
            ctx.move_to(x0 + 25, top + 140); ctx.line_to(x0 + w / 2, top + 210); ctx.stroke()
    else:
        rnd = random.Random(9)
        for k in range(14):
            pw, ph = rnd.uniform(50, 100), rnd.uniform(50, 110)
            sx, sy = x0 + rnd.uniform(-w / 2 + 30, w / 2 - 30), rnd.uniform(top + 40, BASE_Y - 60)
            ex, ey = sx + rnd.uniform(-140, 140), BASE_Y - ph / 2 - rnd.uniform(0, 40)
            x, y = lerp(sx, ex, fall), lerp(sy, ey, fall)
            ctx.save(); ctx.translate(x, y); ctx.rotate(rnd.uniform(-1.2, 1.2) * fall)
            ctx.set_source_rgb(*(CONC if k % 2 else CONC2)); rrect(ctx, -pw / 2, -ph / 2, pw, ph, 8); ctx.fill(); ctx.restore()
        if fall > 0.5:   # dust puffs
            for k in range(8):
                a = 0.5 * (1 - cl((t - T_CRACK - 0.9) / 1.5))
                ctx.set_source_rgba(0.9, 0.88, 0.9, a); ell(ctx, x0 + (k - 3.5) * 40, BASE_Y - 20 - 30 * math.sin(k), 45, 30); ctx.fill()
    # bone pillar (holds)
    xb = COLS[1]
    bone_shape(ctx, xb, top + 75, BASE_Y - 42 + squash * 0, 170); ctx.set_source_rgb(*BONE2)
    ctx.save(); ctx.translate(6, 8); bone_shape(ctx, xb, top + 75, BASE_Y - 42, 170); ctx.restore(); ctx.fill()
    bone_shape(ctx, xb, top + 75, BASE_Y - 42, 170); ctx.set_source_rgb(*BONE); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.5); rrect(ctx, xb - 45, top + 90, 22, BASE_Y - top - 180, 11); ctx.fill()


def trabecular(ctx, cx, cy, R, t):
    ctx.set_source_rgb(0.80, 0.30, 0.36); ctx.paint()
    rnd = random.Random(4)
    pts = [(cx + rnd.uniform(-R, R), cy + rnd.uniform(-R, R)) for _ in range(70)]
    ctx.set_source_rgb(*BONE); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i, (x, y) in enumerate(pts):
        near = sorted(pts, key=lambda p: (p[0] - x) ** 2 + (p[1] - y) ** 2)[1:4]
        for (x2, y2) in near:
            ctx.set_line_width(14 + 4 * math.sin(i)); ctx.move_to(x, y); ctx.line_to(x2, y2); ctx.stroke()
    # hard outer shell band
    ctx.set_source_rgb(*BONE2); ctx.rectangle(cx - R, cy - R, R * 0.38, 2 * R); ctx.fill()
    ctx.set_source_rgb(*BONE); ctx.rectangle(cx - R, cy - R, R * 0.32, 2 * R); ctx.fill()
    ctx.set_source_rgba(0.6, 0.45, 0.35, 0.4); ctx.set_line_width(3)
    for k in range(6):
        ctx.move_to(cx - R + 12 + k * 14, cy - R); ctx.line_to(cx - R + 12 + k * 14, cy + R); ctx.stroke()


def draw(ctx, fi):
    t = fi / FPS
    z = ease(cl((t - T_ZOOM) / 1.2)) * (1 - ease(cl((t - 12.2) / 1.0)))
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *[lerp(a, b, z) for a, b in zip((0.42, 0.62, 1.0), (0.30, 0.12, 0.45))])
    g.add_color_stop_rgb(1, *[lerp(a, b, z) for a, b in zip((0.66, 0.85, 1.0), (0.50, 0.20, 0.55))])
    ctx.set_source(g); ctx.paint()
    zoom = 1 + 1.6 * z
    fx, fy = lerp(540, COLS[1], z), lerp(1000, 1100, z)
    ctx.save(); ctx.translate(540, lerp(1000, 1350, z)); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy)
    scene(ctx, t)
    ctx.restore()
    # little character watching from the bottom-right corner
    ca = 1 - z
    if ca > 0.02:
        ctx.push_group(); ctx.translate(870, 1440); ctx.scale(0.36, 0.36); ctx.translate(-540, -640)
        K.character(ctx, t, 0)
        ctx.identity_matrix(); ctx.pop_group_to_source(); ctx.paint_with_alpha(ca)
    ma = cl((t - 8.6) / 0.25) * (1 - cl((t - 12.0) / 0.3))
    if ma > 0.01:
        mx, my, R = 540, 760, 270
        k = popk((t - 8.6) / 0.45)
        ctx.set_source_rgba(*LIME, ma); ctx.set_line_width(14); ctx.move_to(540, 1300); ctx.line_to(mx, my + R * k); ctx.stroke()
        ell(ctx, 540, 1300, 24 * k, 24 * k); ctx.fill()
        ctx.save(); ell(ctx, mx, my, R * k, R * k); ctx.clip()
        ctx.push_group(); trabecular(ctx, mx, my, R, t); ctx.pop_group_to_source(); ctx.paint_with_alpha(ma); ctx.restore()
        ctx.set_source_rgba(*LIME, ma); ctx.set_line_width(16); ell(ctx, mx, my, R * k, R * k); ctx.stroke()
        tagbox(ctx, "Hard shell", mx - 150, my - 120, 48, (0.85, 0.55, 0.25), a=ma * cl((t - 9.4) / 0.2), k=popk((t - 9.4) / 0.35))
        tagbox(ctx, "Honeycomb", mx + 110, my + 60, 48, (0.55, 0.35, 0.75), a=ma * cl((t - 10.0) / 0.2), k=popk((t - 10.0) / 0.35))
    ha = 1 - cl((t - T_CRACK) / 0.3) + cl((t - 13.6) / 0.3)
    tagbox(ctx, "BONE OR CONCRETE?", 540, 300, 80, (1, 1, 1), fg=STEEL2, a=ha, pointer=False)
    tagbox(ctx, "BONE WINS.", 540, 300, 100, (0.95, 0.75, 0.25), fg=INK, a=cl((t - T_CRACK - 0.3) / 0.25) * (1 - cl((t - 8.3) / 0.3)), k=popk((t - T_CRACK - 0.3) / 0.4), pointer=False)
    tagbox(ctx, "4–5× STRONGER", 540, 300, 92, (1, 1, 1), fg=(0.55, 0.35, 0.75), a=cl((t - 10.6) / 0.25) * (1 - cl((t - 13.3) / 0.3)), k=popk((t - 10.6) / 0.4), pointer=False)
    ctx.set_source_rgb(1, 1, 1); ell(ctx, 130, 150, 66, 66); ctx.fill()
    ctx.set_source_surface(LOGO, 70, 90); ctx.paint()
    tagbox(ctx, "@Visual.Brainer", 360, 150, 38, (1, 1, 1), fg=INK, pointer=False)


def hum(d, amp=0.05):
    m = np.arange(int(SR * d)) / SR
    return (np.sin(2 * np.pi * 70 * m) + 0.4 * np.sin(2 * np.pi * 140 * m)) * np.sin(np.pi * m / d) * amp


def crackle(amp=0.3):
    r = np.random.default_rng(3); n = int(SR * 0.6); x = np.zeros(n)
    for p in r.integers(0, n - 400, 60):
        L_ = r.integers(40, 300); x[p:p + L_] += r.normal(0, 1, L_) * np.exp(-np.arange(L_) / (L_ / 4))
    return x / np.max(np.abs(x)) * np.exp(-np.arange(n) / SR * 5) * amp


def audio(path):
    tr = Track(DUR)
    pad(tr, DUR, 0.035)
    tr.add(hum(2.2, 0.06), T_PRESS); tr.add(pk.whoosh(0.8, 0.05), T_PRESS)
    tr.add(crackle(0.22), T_CRACK)
    for k in range(6): tr.add(pk.tap(150 + 30 * k, 0.12), T_CRACK + 0.5 + k * 0.13)
    tr.add(pop(0.12), T_CRACK + 0.3); tr.add(chime(1046, 0.07, 1.6), T_CRACK + 0.35)
    tr.add(pk.whoosh(1.2, 0.07), T_ZOOM); tr.add(pk.whoosh(1.0, 0.06), 12.2)
    for tt in (8.6, 9.4, 10.0, 10.6): tr.add(pop(0.10), tt)
    tr.add(hum(1.2, 0.04), 12.6); tr.add(chime(1318, 0.05, 1.8), 13.4)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "k3")
    else:
        audio("k3.wav"); encode(draw, NF, "k3_v.mp4"); mux("k3_v.mp4", "k3.wav", "k3_bone.mp4")
