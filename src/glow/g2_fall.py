"""Bowling ball vs feather: in air the ball wins; with no air they land together (Apollo 15, 1971)."""
from fx import *
DUR = 13.0
TX = [290, 790]; TW, TOP, BOT = 400, 600, 1580
T_DROP, FALL, T_BACK = 2.0, 1.7, 11.6
Y0 = 760
_r = random.Random(2); MOL = [(_r.uniform(-170, 170), _r.uniform(TOP + 40, BOT - 40), _r.uniform(0, 7)) for _ in range(70)]


def fall(t, floor, dur):
    u = cl((t - T_DROP) / dur); back = ease((t - T_BACK) / 1.0)
    return lerp(lerp(Y0, floor, u * u), Y0, back)


def feather(ctx, x, y, rot, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    ctx.move_to(-78, 0); ctx.curve_to(-40, -34, 40, -34, 82, -4); ctx.curve_to(40, 30, -40, 30, -78, 0)
    g = cairo.LinearGradient(0, -30, 0, 30); g.add_color_stop_rgba(0, 1, 1, 1, a); g.add_color_stop_rgba(1, .75, .88, 1, a); ctx.set_source(g); ctx.fill()
    ctx.set_source_rgba(.45, .6, .85, a); ctx.set_line_width(4); ctx.move_to(-104, 2); ctx.line_to(82, -4); ctx.stroke()
    ctx.set_line_width(2)
    for k in range(-3, 4): ctx.move_to(k * 20, 0); ctx.line_to(k * 20 + 14, -22); ctx.move_to(k * 20, 0); ctx.line_to(k * 20 + 14, 20)
    ctx.stroke(); ctx.restore()


def bowl(ctx, x, y, r=64):
    ball(ctx, x, y, r, (0.55, 0.2, 0.85))
    for dx, dy in [(-14, -22), (12, -26), (2, -4)]:
        ctx.set_source_rgba(0.1, 0.02, 0.2, .9); ctx.arc(x + dx, y + dy, 7, 0, 7); ctx.fill()


def tube(ctx, cx, t, air):
    g = cairo.LinearGradient(cx - TW / 2, 0, cx + TW / 2, 0)
    g.add_color_stop_rgba(0, 1, 1, 1, .10); g.add_color_stop_rgba(.5, 1, 1, 1, .03); g.add_color_stop_rgba(1, 1, 1, 1, .10)
    rrect(ctx, cx - TW / 2, TOP, TW, BOT - TOP, 50); ctx.set_source(g); ctx.fill()
    ctx.save(); rrect(ctx, cx - TW / 2, TOP, TW, BOT - TOP, 50); ctx.clip()
    for k, (dx, y, ph) in enumerate(MOL):
        if air < 1:                                    # sucked out through the top
            y = y - (1 - air) ** 1 * (y - TOP + 80) - 0
        a = .55 * (1 if air >= 1 else cl(air * 3 + .15) if y > TOP else 0)
        ctx.set_source_rgba(*CYAN, a); ctx.arc(cx + dx + 14 * math.sin(t * 1.3 + ph), y + 14 * math.cos(t * 1.1 + ph), 6, 0, 7); ctx.fill()
    ctx.restore()
    rrect(ctx, cx - TW / 2, TOP, TW, BOT - TOP, 50); ctx.set_source_rgba(1, 1, 1, .7); ctx.set_line_width(6); ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, .25); ctx.set_line_width(8); ctx.move_to(cx - TW / 2 + 26, TOP + 70); ctx.line_to(cx - TW / 2 + 26, BOT - 70); ctx.stroke()


def ring(ctx, x, y, u, col):
    if 0 < u < 1:
        ctx.save(); ctx.translate(x, y); ctx.scale(1, .28); ctx.set_source_rgba(*col, 1 - u); ctx.set_line_width(8); ctx.arc(0, 0, 40 + 170 * u, 0, 7); ctx.stroke(); ctx.restore()


def draw(ctx, t):
    bg(ctx, (0.04, 0.05, 0.18), (0.10, 0.06, 0.26)); stars(ctx, t, 40, 3)
    airR = cl(1 - t / 1.5) if t < T_BACK else cl((t - T_BACK - .4) / .9)
    tube(ctx, TX[0], t, 1); tube(ctx, TX[1], t, airR)
    tagbox(ctx, "AIR", TX[0], 575, 54, CYAN, fg=INK, pointer=False)
    tagbox(ctx, "NO AIR", TX[1], 575, 54, PINK, pointer=False)
    fb, ff = BOT - 70, BOT - 34
    land = T_DROP + FALL
    for i, cx in enumerate(TX):
        by = fall(t, fb, FALL * (1.04 if i == 0 else 1))
        bx, fx_ = cx - 85, cx + 90
        if i == 0:
            u = cl((t - T_DROP) / 6.2); back = ease((t - T_BACK) / 1.0)
            fy = lerp(lerp(Y0, ff, u ** .9), Y0, back); sway = math.sin((t - T_DROP) * 2.4) * 55 * (1 - u) * (t > T_DROP)
            feather(ctx, fx_ + sway, fy, .5 * math.cos((t - T_DROP) * 2.4) * (1 - u) * (t > T_DROP))
            ring(ctx, bx, BOT - 10, (t - land) / .6, CYAN)
        else:
            fy = fall(t, ff, FALL); feather(ctx, fx_, fy, 0)
            ring(ctx, cx, BOT - 10, (t - land) / .7, YEL); ring(ctx, cx, BOT - 10, (t - land - .15) / .7, PINK)
            if land < t < T_BACK: glow(ctx, cx, BOT - 40, 260, YEL, .35 * (1 - cl((t - land) / 1.5)) + .08)
        bounce = 26 * math.exp(-5 * (t - land)) * abs(math.sin(9 * (t - land))) if land < t < T_BACK else 0
        bowl(ctx, bx, by - bounce)
    for k, tt in enumerate([.9, 1.25, 1.6]):
        if tt < t < tt + .35: label(ctx, str(3 - k), 540, 1130, int(190 * popk((t - tt) / .3)), col=WHITE, alpha=1 - cl((t - tt - .2) / .15), shadow=.5)
    a0 = 1 - cl((t - 3.9) / .3) + cl((t - 12.4) / .4)
    tagbox(ctx, "WHICH LANDS FIRST?", 540, 330, 80, WHITE, fg=INK, a=a0, pointer=False)
    a1 = cl((t - 4.1) / .3) * (1 - cl((t - 8.0) / .3))
    tagbox(ctx, "NO AIR?", 540, 290, 84, PINK, a=a1, k=popk((t - 4.1) / .4), pointer=False)
    tagbox(ctx, "THEY LAND TOGETHER.", 540, 400, 70, YEL, fg=INK, a=a1 * cl((t - 4.5) / .3), k=popk((t - 4.5) / .4), pointer=False)
    a2 = cl((t - 8.3) / .3) * (1 - cl((t - 12.0) / .3))
    tagbox(ctx, "TESTED ON THE MOON", 540, 290, 72, WHITE, fg=INK, a=a2, k=popk((t - 8.3) / .4), pointer=False)
    tagbox(ctx, "APOLLO 15 · 1971", 540, 395, 64, CYAN, fg=INK, a=a2 * cl((t - 8.7) / .3), k=popk((t - 8.7) / .4), pointer=False)


def audio(path):
    tr = Track(DUR); pad(tr, DUR, .03)
    tr.add(pk.whoosh(1.4, .09), 0.0)
    for tt in (.9, 1.25, 1.6): tr.add(chime(660, .06, .5), tt)
    tr.add(chime(990, .07, .8), T_DROP); tr.add(pk.whoosh(1.5, .05), T_DROP + .2)
    land = T_DROP + FALL; m = np.arange(int(SR * .4)) / SR
    thud = np.sin(2 * np.pi * 62 * m) * np.exp(-m * 14)
    tr.add(thud * .35, land); tr.add(thud * .3, land + .05); tr.add(pop(.1), land)
    for i, f in enumerate([784, 1046, 1318]): tr.add(chime(f, .06, 2), land + .1 + i * .08)
    tr.add(pk.soft_noise(4.0, 30, .02), land + .3); tr.add(pop(.05), T_DROP + 6.2)
    tr.add(pop(.09), 4.1); tr.add(pop(.09), 4.5); tr.add(pop(.09), 8.3); tr.add(pop(.09), 8.7)
    tr.add(pk.whoosh(1.2, .07), T_BACK); tr.save(path, DUR)


if __name__ == '__main__': main(draw, DUR, audio, 'g2_fall', sys.argv)
