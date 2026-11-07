"""Paper fact: Which weighs more — a cloud or an elephant? (a cumulus cloud ≈ 500 t ≈ 100 elephants, USGS)"""
import sys, math, random
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, SR, mux
from paper import paper, pin, rect_pts, ellipse_pts, path
from paperkit import *

DUR = 16.0
NF = int(DUR * FPS)
SKY, SKY2 = (0.62, 0.82, 0.93), (0.84, 0.92, 0.95)
GREY, GREY2 = (0.63, 0.65, 0.71), (0.52, 0.54, 0.61)
WOOD, WOOD2 = (0.66, 0.45, 0.28), (0.55, 0.37, 0.22)
CLOUD = (0.99, 0.98, 0.96)
FX, FY, L, HANG = 540, 1020, 290, 190   # fulcrum, half-beam, string length
TH0 = -0.30                              # cloud side down
T_LAND, T_REV, T_ADD0, T_ADD1, T_UP, T_BACK, T_RET = 0.35, 2.2, 3.2, 9.0, 10.2, 13.4, 14.6


def cl(u): return max(0.0, min(1.0, u))


def count(t):
    if t < T_ADD0: return 1
    if t < T_RET: return 1 + int(99 * cl((t - T_ADD0) / (T_ADD1 - T_ADD0)) ** 2)
    return max(1, 100 - int(99 * cl((t - T_RET) / 0.6)))


def cloud_on(t):          # 1 = cloud sits on the pan, 0 = gone up in the sky
    if t < T_UP: return 1.0
    if t < T_BACK: return 1 - ease(cl((t - T_UP) / 0.5))
    return ease(cl((t - T_BACK - 0.6) / 0.6))


def beam_angle(t):
    n = count(t); c = cloud_on(t)
    if t < T_REV:
        th = 0.0
    else:
        th = TH0 * (1 - (n - 1) / 99) * c + 0.30 * (1 - c) * (n / 100)
        if t < T_REV + 0.6: th *= popu((t - T_REV) / 0.6)
    if t > T_RET + 0.6: th *= 1 - ease(cl((t - T_RET - 0.6) / 0.8))     # back to frame-0 pose (loop)
    th += 0.035 * math.exp(-6 * max(0, t - T_LAND)) * math.sin(14 * max(0, t - T_LAND)) if t > T_LAND else 0
    return th


def puff(ctx, x, y, s, seed, a=1.0):
    ctx.push_group()
    for k, (dx, dy, r) in enumerate([(-0.55, 0.05, 0.42), (-0.15, -0.3, 0.55), (0.35, -0.18, 0.48), (0.7, 0.08, 0.36), (0.1, 0.12, 0.5)]):
        paper(ctx, ellipse_pts(x + dx * s, y + dy * s, r * s, r * s * 0.92, 28), CLOUD, seed=seed + k, shadow=(4, 6), sh_a=0.18, rough=1.6)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a)


def elephant(ctx, x, y, s, seed=0):
    """paper elephant, side view facing left; (x, y) = between the feet on the ground"""
    for dx in (55, -55):
        paper(ctx, rect_pts(x + dx * s - 16 * s, y - 80 * s, 32 * s, 80 * s), GREY2, seed=seed + 1, shadow=(3, 4), rough=1.0)
    paper(ctx, ellipse_pts(x + 10 * s, y - 110 * s, 118 * s, 74 * s, 36), GREY, seed=seed + 2, shadow=(5, 7))
    for dx in (85, -25):
        paper(ctx, rect_pts(x + dx * s - 17 * s, y - 85 * s, 34 * s, 85 * s), GREY, seed=seed + 3, shadow=(3, 5), rough=1.0)
    trunk = [(x - 125 * s, y - 150 * s), (x - 165 * s, y - 120 * s), (x - 168 * s, y - 60 * s), (x - 185 * s, y - 40 * s),
             (x - 178 * s, y - 28 * s), (x - 150 * s, y - 55 * s), (x - 145 * s, y - 115 * s), (x - 110 * s, y - 135 * s)]
    paper(ctx, trunk, GREY, seed=seed + 4, shadow=(4, 5), rough=1.0)
    paper(ctx, ellipse_pts(x - 105 * s, y - 145 * s, 58 * s, 54 * s, 30), GREY, seed=seed + 5, shadow=(4, 6))
    paper(ctx, ellipse_pts(x - 70 * s, y - 140 * s, 38 * s, 52 * s, 24), GREY2, seed=seed + 6, shadow=(3, 4), rough=1.2)
    paper(ctx, [(x - 130 * s, y - 112 * s), (x - 158 * s, y - 92 * s), (x - 128 * s, y - 100 * s)], CREAM, seed=seed + 7, shadow=(2, 2), rough=0.4)
    ctx.set_source_rgb(*INK); ctx.arc(x - 125 * s, y - 160 * s, 6 * s, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*GREY2); ctx.set_line_width(5 * s); ctx.move_to(x + 125 * s, y - 130 * s); ctx.line_to(x + 145 * s, y - 80 * s); ctx.stroke()


def mini(ctx, x, y, s):
    """tiny flat elephant for the pile (no texture — 100 of them)"""
    ctx.set_source_rgba(0.12, 0.08, 0.05, 0.25)
    ctx.save(); ctx.translate(x + 2, y - 70 * s + 3); ctx.scale(120 * s, 78 * s); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    ctx.set_source_rgb(*GREY)
    ctx.save(); ctx.translate(x, y - 70 * s); ctx.scale(118 * s, 74 * s); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore(); ctx.fill()
    ctx.arc(x - 105 * s, y - 115 * s, 55 * s, 0, 2 * math.pi); ctx.fill()
    ctx.rectangle(x - 170 * s, y - 115 * s, 30 * s, 95 * s); ctx.fill()
    for dx in (-60, 70): ctx.rectangle(x + dx * s - 16 * s, y - 40 * s, 32 * s, 40 * s); ctx.fill()
    ctx.set_source_rgb(*GREY2); ctx.arc(x - 72 * s, y - 112 * s, 34 * s, 0, 2 * math.pi); ctx.fill()


PILE = []
for k in range(100):
    row, col = divmod(k, 10)
    PILE.append(((col - 4.5) * 33 + (row % 2) * 8, -row * 27))


def drops(t):
    """cloud broken into droplets that spread through the sky"""
    s = ease(cl((t - T_UP - 0.4) / 1.6)) * (1 - ease(cl((t - T_BACK) / 0.9)))
    rnd = random.Random(4)
    out = []
    for k in range(140):
        ang = rnd.uniform(0, 2 * math.pi); d = rnd.uniform(0, 1) ** 0.6
        bx, by = 170 * d * math.cos(ang), 85 * d * math.sin(ang)
        out.append((bx * (1 + 2.6 * s), by * (1 + 4.0 * s) - 60 * s * math.sin(t * 1.5 + k), rnd.uniform(5, 11)))
    return s, out


def draw(ctx, fi):
    t = fi / FPS; ts = stop(t)
    textured_bg(ctx, SKY, SKY2)
    # background drifting paper clouds + sun
    paper(ctx, ellipse_pts(900, 180, 90, 90, 30), (0.98, 0.82, 0.42), seed=40, shadow=(4, 6), rough=1.5)
    for k, (bx, by, bs) in enumerate([(160, 700, 90), (880, 820, 70), (420, 1450, 60)]):
        puff(ctx, (bx + ts * 18 * (k + 1)) % (W + 300) - 150, by, bs, 50 + k * 7, 0.75)
    # hills + ground
    paper(ctx, [(-30, 1560), (250, 1440), (560, 1520), (860, 1420), (W + 30, 1500), (W + 30, H + 20), (-30, H + 20)], (0.56, 0.74, 0.46), seed=60, shadow=(0, -6), rough=1.5)
    paper(ctx, rect_pts(-20, 1600, W + 40, 400), (0.47, 0.66, 0.40), seed=61, shadow=(0, -6), rough=1.5)
    # stand
    paper(ctx, [(FX, FY), (FX - 110, 1600), (FX + 110, 1600)], WOOD2, seed=70, shadow=(8, 10))
    th = beam_angle(ts)
    c, s_ = math.cos(th), math.sin(th)
    ends = [(FX - L * c, FY - L * s_), (FX + L * c, FY + L * s_)]
    bw = 22
    pts = [(FX - L * c - bw * s_ / 2 * -1, FY - L * s_ - bw * c / 2), (FX + L * c + bw * s_ / 2, FY + L * s_ - bw * c / 2),
           (FX + L * c - bw * s_ / 2, FY + L * s_ + bw * c / 2), (FX - L * c + bw * s_ / 2 * -1, FY - L * s_ + bw * c / 2)]
    pts = [(FX + (-L) * c - (-bw / 2) * s_, FY + (-L) * s_ + (-bw / 2) * c), (FX + L * c - (-bw / 2) * s_, FY + L * s_ + (-bw / 2) * c),
           (FX + L * c - (bw / 2) * s_, FY + L * s_ + (bw / 2) * c), (FX + (-L) * c - (bw / 2) * s_, FY + (-L) * s_ + (bw / 2) * c)]
    for i, (ex, ey) in enumerate(ends):
        py = ey + HANG
        ctx.set_source_rgba(*INK, 0.7); ctx.set_line_width(3)
        ctx.move_to(ex, ey); ctx.line_to(ex - 160, py); ctx.move_to(ex, ey); ctx.line_to(ex + 160, py); ctx.stroke()
        paper(ctx, rect_pts(ex - 180, py, 360, 24), WOOD, seed=80 + i, shadow=(5, 7), rough=1.2)
        if i == 0:
            co = cloud_on(ts)
            if co > 0.02:
                lift = (1 - co) * 500
                puff(ctx, ex, py - 95 - lift, 200, 10, min(1, co * 1.5))
        else:
            n = count(ts)
            land = cl((ts - 0.05) / (T_LAND - 0.05))
            if n == 1 or ts < T_ADD0 + 0.2:
                elephant(ctx, ex + 20, py - (1 - land ** 2) * 700, 0.85, seed=20)
            else:
                for k in range(n):
                    dx, dy = PILE[k]
                    mini(ctx, ex + dx + 12, py + dy, 0.105)
            if ts > T_ADD0 + 0.2 and n > 1:
                tag(ctx, f"×{n}", ex, py - 330, 64, seed=90, col=INK)
    paper(ctx, pts, WOOD, seed=71, shadow=(6, 8))
    pin(ctx, FX, FY, 13)
    # the cloud up in the sky, broken into droplets + rising warm air
    sp, dl = drops(ts)
    if sp > 0.01:
        cx, cy = ends[0][0] + 120 * sp, 760
        for k in range(3):
            ax = 300 + k * 240; ay = 1350 - ((ts * 180 + k * 160) % 520)
            paper(ctx, [(ax, ay), (ax - 26, ay + 40), (ax - 9, ay + 40), (ax - 9, ay + 110), (ax + 9, ay + 110), (ax + 9, ay + 40), (ax + 26, ay + 40)],
                  (0.98, 0.72, 0.52), seed=100 + k, shadow=(3, 4), rough=0.8)
        for k, (dx, dy, r) in enumerate(dl):
            ctx.set_source_rgba(0.12, 0.08, 0.05, 0.15); ctx.arc(cx + dx + 2, cy + dy + 3, r, 0, 2 * math.pi); ctx.fill()
            ctx.set_source_rgba(0.97, 0.99, 1.0, 1); ctx.arc(cx + dx, cy + dy, r, 0, 2 * math.pi); ctx.fill()
        if sp < 0.35:
            puff(ctx, cx, cy, 200, 10, 1 - sp / 0.35)
    # text
    banner(ctx, "CLOUD OR ELEPHANT?", 380, 78, a=window(ts, -1, T_ADD1 - 0.4) + fade_in(ts, 15.2), seed=1)
    banner(ctx, "100 ELEPHANTS.", 380, 96, col=(0.80, 0.32, 0.20), a=window(ts, T_ADD1 - 0.1, T_UP), seed=2)
    banner(ctx, "WHY DOESN'T IT FALL?", 380, 74, a=window(ts, T_UP + 0.2, T_RET), seed=3)
    vignette(ctx, 0.25)


def window(t, t0, t1, d=0.25):
    return cl((t - t0) / d) * cl((t1 - t) / d)


def fade_in(t, t0, d=0.3):
    return cl((t - t0) / d)


# ---------- natural paper sounds ----------
_g = np.random.default_rng(5)


def rustle(d, amp=0.1, rate=260, grain=(60, 260)):
    n = int(SR * d); x = np.zeros(n + 400)
    for p in (_g.random(int(rate * d)) * n).astype(int):
        L_ = _g.integers(*grain); m = np.arange(L_)
        x[p:p + L_] += _g.normal(0, 1, L_) * np.exp(-m / (L_ / 4)) * _g.uniform(0.2, 1)
    x = x[:n]; x = x - 0.85 * np.concatenate([[0], x[:-1]])
    env = np.sin(np.pi * np.arange(n) / n) ** 0.6
    return x / (np.max(np.abs(x)) + 1e-9) * env * amp


def slide(d=0.5, amp=0.08):
    x = soft_noise(d, 6, 1.0) + 0.3 * rustle(d, 1.0, 120)
    m = np.arange(len(x)) / len(x)
    return x * np.sin(np.pi * m) ** 1.5 * amp


def thud(amp=0.3):
    m = np.arange(int(SR * 0.3)) / SR
    return (np.sin(2 * np.pi * 70 * m) * np.exp(-m * 18) + 0.3 * np.sin(2 * np.pi * 140 * m) * np.exp(-m * 30)) * amp


def flick(amp=0.05):
    return rustle(0.05, amp, 900, (30, 90))


def audio(path):
    tr = Track(DUR)
    ambience(tr, DUR, 0.02)
    musicbox(tr, DUR, vol=0.03, gap=0.8)
    tr.add(slide(0.4, 0.07), 0.0); tr.add(thud(0.32), T_LAND); tr.add(rustle(0.25, 0.08), T_LAND)
    tr.add(slide(0.5, 0.07), T_REV - 0.1); tr.add(thud(0.28), T_REV + 0.35); tr.add(rustle(0.4, 0.07), T_REV + 0.35)
    prev = 1
    for f in range(int(T_ADD0 * FPS), int(T_ADD1 * FPS)):
        n = count(f / FPS)
        if n != prev and (n <= 12 or n % 4 == 0 or n == 100): tr.add(flick(0.05), f / FPS)
        prev = n
    tr.add(pluck(note(12, 261.63), 1.4, 0.12, 3), T_ADD1)
    tr.add(rustle(1.2, 0.06, 180), T_UP); tr.add(slide(1.0, 0.05), T_UP + 0.3)
    tr.add(rustle(0.9, 0.05, 160), T_BACK)
    tr.add(thud(0.22), T_BACK + 1.2)
    tr.add(rustle(0.6, 0.06, 400, (30, 120)), T_RET)
    tr.add(pluck(note(9, 261.63), 1.0, 0.08, 3), 15.2)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "p5")
    else:
        audio("p5.wav"); encode(draw, NF, "p5_v.mp4"); mux("p5_v.mp4", "p5.wav", "p5_cloud.mp4")
