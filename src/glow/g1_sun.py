"""How many Earths fit in the Sun? ~1.3 million (NASA). A glass Sun fills with tiny Earths."""
from fx import *
DUR = 14.0
SX, SY, R = 540, 1090, 400
T0, T1, T_SOLID, T_OUT = 0.4, 9.0, 9.2, 12.6
D = 10.5
PTS = [((i + .5 * (j % 2)) * D, j * D * .866) for j in range(-50, 51) for i in range(-50, 51)]
PTS = [p for p in PTS if p[0] ** 2 + p[1] ** 2 < (R - 9) ** 2]
_r = random.Random(4); PTS.sort(key=lambda p: -p[1] + _r.uniform(-14, 14)); N = len(PTS)
TA = [T0 + (T1 - T0) * ((k + 1) / N) ** (1 / 1.8) for k in range(N)]
COL = [(0.25, 0.6, 1.0), (0.35, 0.8, 0.75)]


def draw(ctx, t):
    bg(ctx, (0.05, 0.03, 0.16), (0.14, 0.05, 0.22)); stars(ctx, t)
    out = ease((t - T_OUT) / 1.2)
    solid = ease((t - T_SOLID) / .7) * (1 - out)
    frac = cl((t - T0) / (T1 - T0)) ** 1.8 * (1 - out)
    n = int(N * frac)
    glow(ctx, SX, SY, R * 1.7, ORNG, .22 + .35 * solid + .05 * math.sin(t * 3))
    ctx.set_source_rgba(0.12, 0.05, 0.10, .9); ctx.arc(SX, SY, R, 0, 7); ctx.fill()
    for c in (0, 1):                                   # settled Earths, two tints
        ctx.new_path()
        for k in range(c, n, 2):
            x, y = PTS[k]; ctx.new_sub_path(); ctx.arc(SX + x, SY + y, D * .47, 0, 7)
        ctx.set_source_rgb(*COL[c]); ctx.fill()
    if out == 0:
        for k in range(n, min(N, n + 260)):            # Earths still falling in
            u = (TA[k] - t) / .45
            if u > 1: break
            x, y = PTS[k]; yy = SY + y - u * u * 520
            if (x * x + (yy - SY) ** 2) < (R + 300) ** 2:
                ctx.set_source_rgb(*COL[k % 2]); ctx.arc(SX + x, yy, D * .47, 0, 7); ctx.fill()
    if solid > 0:
        ball(ctx, SX, SY, R, (1.0, 0.72, 0.18), solid, spec=.35)
        for k in range(10):
            a = k * .63 + t * .25
            glow(ctx, SX + math.cos(a) * R * .55, SY + math.sin(a * 1.3) * R * .55, 90, YEL, .25 * solid)
    ctx.set_source_rgba(1.0, 0.75, 0.3, .95); ctx.set_line_width(9); ctx.arc(SX, SY, R, 0, 7); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, .25); ctx.set_line_width(5); ctx.arc(SX, SY, R - 14, 3.5, 4.6); ctx.stroke()
    # Earth to scale (Sun is ~109 Earths wide)
    ex, ey, er = 110, 1560, R / 109
    p = (t * .9) % 1
    ctx.set_source_rgba(*CYAN, 1 - p); ctx.set_line_width(3); ctx.arc(ex, ey, 10 + 30 * p, 0, 7); ctx.stroke()
    ctx.set_source_rgb(*COL[0]); ctx.arc(ex, ey, er, 0, 7); ctx.fill()
    label(ctx, "EARTH, TO SCALE", 150, 1572, 32, col=CYAN, anchor="l", shadow=.4)
    # text
    a0 = 1 - cl((t - 9.2) / .3) + cl((t - 13.2) / .4)
    tagbox(ctx, "HOW MANY EARTHS", 540, 290, 78, WHITE, fg=INK, a=a0, pointer=False)
    tagbox(ctx, "FIT IN THE SUN?", 540, 395, 78, ORNG, fg=INK, a=a0, pointer=False)
    if t < 2.6: label(ctx, "1,000?   100,000?   MORE?", 540, 520, 44, col=YEL, alpha=cl(t / .3) * (1 - cl((t - 2.2) / .4)))
    if 2.4 < t < T_OUT + .3:
        v = int(1_300_000 * (frac if solid < 1 else 1)); done = t > T1
        label(ctx, f"{v:,}", 540, 560 if not done else 400, int((110 if not done else 150) * (popk((t - T1) / .5) if done else 1)), col=YEL if done else WHITE, alpha=cl((t - 2.4) / .3) * (1 - out), shadow=.5)
        if done: tagbox(ctx, "EARTHS", 540, 520, 70, YEL, fg=INK, a=cl((t - T1 - .3) / .3) * (1 - out), k=popk((t - T1 - .3) / .4), pointer=False)


def audio(path):
    tr = Track(DUR); pad(tr, DUR, .03)
    k = 0
    while k < 90:
        tt = T0 + (T1 - T0) * ((k + 1) / 90) ** (1 / 1.8); tr.add(pop(.018 + .012 * (k / 90)), tt); k += 1
    tr.add(pk.soft_noise(8.6, 60, .03), T0); tr.add(pk.whoosh(1.0, .08), T1 - .6)
    for i, f in enumerate([523, 659, 784, 1046]): tr.add(chime(f, .07, 2.5), T1 + .15 + i * .07)
    tr.add(pk.whoosh(1.2, .06), T_OUT); tr.save(path, DUR)


if __name__ == '__main__': main(draw, DUR, audio, 'g1_sun', sys.argv)
