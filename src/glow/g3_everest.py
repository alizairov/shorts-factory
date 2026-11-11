"""Could the ocean hide Mount Everest? Everest 8,849 m; Challenger Deep ~10,935 m -> ~2 km of water above the peak."""
from fx import *
DUR = 14.0
S = 0.085                                        # px per metre
DEEP, EV = 10935, 8849
T0, T1, T_BACK = 1.2, 6.8, 12.4
MT = [(-260, 0), (-150, -300), (-90, -420), (-40, -600), (0, -752), (50, -560), (110, -380), (170, -250), (260, 0)]
SNOW = [(0, -752), (-45, -585), (-18, -612), (5, -572), (28, -616), (55, -545)]
_r = random.Random(6); BUB = [(_r.uniform(0, W), _r.uniform(0, 1), _r.uniform(3, 8)) for _ in range(45)]


def draw(ctx, t):
    back = ease((t - T_BACK) / 1.3)
    sink = ease((t - T0) / (T1 - T0)) * (1 - back)
    cam = ease((sink - .25) / .5)
    z, sy = lerp(.62, 1.0, cam), lerp(1180, 590, cam)
    base = sink * DEEP                                # depth of Everest's base (m)
    # sky
    bg(ctx, (0.07, 0.10, 0.32), (0.55, 0.45, 0.65))
    glow(ctx, 860, sy - 120 * z, 420, (1, .8, .5), .5); ball(ctx, 860, sy - 120 * z, 46 * z, (1, .85, .45))
    ctx.save(); ctx.translate(540, sy); ctx.scale(z, z); ctx.translate(-540, 0)
    # mountain
    by = base * S
    ctx.move_to(540 + MT[0][0], by)
    for x, y in MT[1:]: ctx.line_to(540 + x, by + y)
    ctx.close_path(); g = cairo.LinearGradient(280, 0, 800, 0); g.add_color_stop_rgb(0, .62, .60, .72); g.add_color_stop_rgb(.5, .50, .47, .60); g.add_color_stop_rgb(1, .30, .28, .42)
    ctx.set_source(g); ctx.fill()
    ctx.move_to(540 + SNOW[0][0], by + SNOW[0][1])
    for x, y in SNOW[1:]: ctx.line_to(540 + x, by + y)
    ctx.close_path(); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    # water over it
    g = cairo.LinearGradient(0, 0, 0, DEEP * S); g.add_color_stop_rgba(0, .15, .75, .9, .62); g.add_color_stop_rgba(.25, .05, .35, .7, .55); g.add_color_stop_rgba(1, .02, .06, .28, .62)
    ctx.set_source(g); ctx.rectangle(-1500, 0, 4000, 1400); ctx.fill()
    for k in range(6):                                # light shafts
        x = 100 + k * 190 + 30 * math.sin(t * .5 + k)
        gg = cairo.LinearGradient(0, 0, 0, 420); gg.add_color_stop_rgba(0, 1, 1, .9, .16); gg.add_color_stop_rgba(1, 1, 1, .9, 0)
        ctx.set_source(gg); ctx.move_to(x, 0); ctx.line_to(x + 70, 0); ctx.line_to(x + 150, 420); ctx.line_to(x - 40, 420); ctx.close_path(); ctx.fill()
    for x, ph, r in BUB:
        u = (ph + t * .08) % 1; ctx.set_source_rgba(1, 1, 1, .25); ctx.arc(x + 12 * math.sin(t + ph * 9), 920 * (1 - u), r, 0, 7); ctx.fill()
    # seabed basin
    bed = [(-1500, 300), (120, 330), (190, 880), (230, DEEP * S), (850, DEEP * S), (890, 880), (960, 330), (2600, 300), (2600, 1500), (-1500, 1500)]
    ctx.move_to(*bed[0]); [ctx.line_to(*p) for p in bed[1:]]; ctx.close_path()
    g = cairo.LinearGradient(0, 300, 0, 1000); g.add_color_stop_rgb(0, .16, .20, .36); g.add_color_stop_rgb(1, .04, .04, .12); ctx.set_source(g); ctx.fill()
    # surface line
    ctx.set_source_rgba(1, 1, 1, .85); ctx.set_line_width(5 / z); ctx.move_to(-1500, 0)
    for x in range(-1500, 2600, 30): ctx.line_to(x, 5 * math.sin(x * .02 + t * 2.2))
    ctx.stroke()
    # depth marks on the right wall
    for d, txt in [(200, "SUNLIGHT ENDS"), (3800, "TITANIC"), (DEEP, "DEEPEST POINT")]:
        a = cl((base - d + 900) / 900) * (1 - back) if d < DEEP else cl((t - T1) / .4) * (1 - back)
        if a > 0:
            ctx.set_source_rgba(1, 1, 1, .6 * a); ctx.set_line_width(3); ctx.set_dash([10, 8]); ctx.move_to(815, d * S); ctx.line_to(1010, d * S); ctx.stroke(); ctx.set_dash([])
            label(ctx, txt, 1040, d * S - 12, 26, col=WHITE, alpha=a, anchor="r", shadow=.5)
    # depth of the base
    if T0 < t < T_BACK:
        tagbox(ctx, f"{int(base):,} m", 150, by - 20, 44, YEL, fg=INK, pointer=False, a=cl((t - T0) / .3) * (1 - back))
    # gap above the peak
    ga = cl((t - T1 - .5) / .4) * (1 - back)
    if ga > 0:
        py = (DEEP - EV) * S
        ctx.set_source_rgba(*YEL, ga); ctx.set_line_width(6); ctx.move_to(540, 8); ctx.line_to(540, py - 8); ctx.stroke()
        for yy, dd in ((8, 16), (py - 8, -16)):
            ctx.move_to(524, yy + dd); ctx.line_to(540, yy); ctx.line_to(556, yy + dd); ctx.stroke()
        glow(ctx, 540, py / 2, 200, YEL, .25 * ga)
        tagbox(ctx, "2 KM OF WATER", 760, py / 2 + 30, 46, YEL, fg=INK, pointer=False, a=ga, k=popk((t - T1 - .5) / .4))
    ctx.restore()
    a0 = 1 - cl((t - T1 - .3) / .3) + cl((t - 13.3) / .4)
    tagbox(ctx, "CAN THE OCEAN", 540, 290, 80, WHITE, fg=INK, a=a0, pointer=False)
    tagbox(ctx, "HIDE EVEREST?", 540, 395, 80, CYAN, fg=INK, a=a0, pointer=False)
    a1 = cl((t - T1 - 1.6) / .3) * (1 - cl((t - 12.2) / .3))
    tagbox(ctx, "EASILY.", 540, 300, 110, YEL, fg=INK, a=a1, k=popk((t - T1 - 1.6) / .4), pointer=False)


def audio(path):
    tr = Track(DUR); pad(tr, DUR, .03)
    tr.add(pk.splash(.14, .6), T0 + .25); tr.add(pk.soft_noise(T1 - T0 + 5, 14, .05), T0 + .3)
    for k in range(18): tr.add(pk.bubble(.03), T0 + .5 + k * .3)
    for i, tt in enumerate([T0 + .9, T0 + 2.9]): tr.add(chime(660 - i * 120, .04, 1.2), tt)
    m = np.arange(int(SR * .9)) / SR; tr.add(np.sin(2 * np.pi * 45 * m) * np.exp(-m * 5) * .4, T1 - .05)
    tr.add(pop(.1), T1 + .5); tr.add(chime(784, .06, 2), T1 + .5)
    for i, f in enumerate([523, 784, 1046]): tr.add(chime(f, .07, 2.5), T1 + 1.6 + i * .08)
    tr.add(pk.whoosh(1.3, .07), T_BACK); tr.save(path, DUR)


if __name__ == '__main__': main(draw, DUR, audio, 'g3_everest', sys.argv, strength=.8, thr=.7)
