"""On Venus a day is longer than a year (and the Sun rises in the west)."""
import sys, math
import numpy as np
from story import *

YEAR, DAY = 224.7, 243.0          # Earth days: orbit, sidereal rotation (retrograde)
T_SIM0 = 3.2
SIM_LEN = 15.0                    # seconds to show 260 Earth days
DAYS_TOTAL = 260
T_END = T_SIM0 + SIM_LEN
DUR = T_END + 7.0
NF = int(DUR * FPS)
CX, CY, OR = W / 2, 990, 320
rng = np.random.default_rng(9)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 2.0)) for _ in range(140)]


def days_at(t):
    if t < T_SIM0: return 0.0
    u = min(1, (t - T_SIM0) / SIM_LEN)
    return DAYS_TOTAL * u


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx)
    for (sx, sy, sr) in STARS:
        ctx.set_source_rgba(1, 1, 1, 0.35); circle(ctx, sx, sy, sr); ctx.fill()
    progress(ctx, t, DUR)
    lines(ctx, ["ON VENUS, A *DAY* IS", "LONGER THAN A *YEAR*"], 220, 80)
    d = days_at(t)
    orbit_frac = d / YEAR
    spin_frac = d / DAY
    # orbit path
    ctx.set_source_rgba(1, 1, 1, 0.18); ctx.set_line_width(3); ctx.set_dash([10, 14]); circle(ctx, CX, CY, OR); ctx.stroke(); ctx.set_dash([])
    # completed orbit arc
    if orbit_frac > 0:
        ctx.set_source_rgb(*YEL); ctx.set_line_width(8)
        ctx.arc(CX, CY, OR, -math.pi / 2, -math.pi / 2 + 2 * math.pi * min(orbit_frac, 1)); ctx.stroke()
    # sun
    for k, a in [(2.0, 0.06), (1.5, 0.12)]:
        ctx.set_source_rgba(1, 0.6, 0.1, a); circle(ctx, CX, CY, 80 * k); ctx.fill()
    glossy_ball(ctx, CX, CY, 80, (1, 0.75, 0.2))
    # venus
    oa = -math.pi / 2 + 2 * math.pi * orbit_frac
    vx, vy = CX + OR * math.cos(oa), CY + OR * math.sin(oa)
    vr = 70
    glossy_ball(ctx, vx, vy, vr, (0.95, 0.75, 0.45))
    # retrograde spin marker (a flag on the surface), starts pointing up
    sa = -math.pi / 2 - 2 * math.pi * spin_frac
    mx, my = vx + vr * math.cos(sa), vy + vr * math.sin(sa)
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(6)
    ctx.move_to(vx, vy); ctx.line_to(mx, my); ctx.stroke()
    glossy_ball(ctx, mx, my, 14, PINK, glow=False)
    # spin progress ring around venus
    ctx.set_source_rgb(*PINK); ctx.set_line_width(8)
    if spin_frac > 0:
        ctx.arc_negative(vx, vy, vr + 18, -math.pi / 2, -math.pi / 2 - 2 * math.pi * min(spin_frac, 1)); ctx.stroke()
    # counters
    card(ctx, 70, 1430, 450, 230); card(ctx, 560, 1430, 450, 230)
    label(ctx, "1 YEAR (orbit)", 295, 1495, 38, col=YEL)
    label(ctx, f"{min(d, YEAR):.0f} / 225", 295, 1600, 76)
    label(ctx, "1 DAY (spin)", 785, 1495, 38, col=PINK)
    label(ctx, f"{min(d, DAY):.0f} / 243", 785, 1600, 76)
    label(ctx, "Earth days passed", W / 2, 1730, 40, alpha=0.6)
    label(ctx, f"{d:.0f}", W / 2, 1810, 70, alpha=0.9)
    if t < T_SIM0:
        lines(ctx, ["*Pink flag* = one full spin (a day)", "*Yellow path* = one orbit (a year)"], 440, 44, alpha=fade_in(t, 0.3), hl=PINK)
    # year complete moment
    ty = T_SIM0 + SIM_LEN * YEAR / DAYS_TOTAL
    if ty <= t < T_END + 0.4:
        a = window(t, ty, T_SIM0 + SIM_LEN * DAY / DAYS_TOTAL - 0.3, 0.2)
        rich(ctx, "YEAR DONE… *DAY ISN'T*", W / 2, 450, 60, alpha=a, hl=PINK)
    td = T_SIM0 + SIM_LEN * DAY / DAYS_TOTAL
    if td <= t < T_END + 0.3:
        rich(ctx, "*FINALLY* — ONE DAY", W / 2, 450, 60, alpha=fade_in(t, td + 0.1, 0.2), hl=LIME)
    if t >= T_END + 0.3:
        b = fade_in(t, T_END + 0.3, 0.4)
        ctx.set_source_rgba(0.03, 0.01, 0.09, 0.97 * b); ctx.rectangle(0, 360, W, 1560); ctx.fill()
        lines(ctx, ["A day on Venus:", "*243* Earth days", "", "A year on Venus:", "*225* Earth days"], 640, 74, alpha=b)
        if t > T_END + 2.6:
            c = fade_in(t, T_END + 2.6, 0.4)
            lines(ctx, ["And it spins *backwards* —", "the Sun rises in the *west*."], 1430, 62, alpha=c, hl=PINK)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=92, seed=404, vol=0.55, base=196)
    tr.add(ding(2), 0.4); tr.add(ding(4), 1.6)
    tr.add(riser(2.0, 0.06), T_SIM0 - 0.5)
    for k in range(1, 27):
        tt = T_SIM0 + SIM_LEN * (k * 10) / DAYS_TOTAL
        tr.add(pluck(note(k % 5 + 5, 392), 0.15, 0.03, 18), tt)
    tr.add(ding(9, 0.28), T_SIM0 + SIM_LEN * YEAR / DAYS_TOTAL)
    tr.add(boom(1.4, 0.45), T_SIM0 + SIM_LEN * DAY / DAYS_TOTAL)
    tr.add(ding(12, 0.25), T_SIM0 + SIM_LEN * DAY / DAYS_TOTAL)
    tr.add(whoosh(0.6, 0.12, 4), T_END)
    tr.add(ding(7, 0.2), T_END + 2.6)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "f4")
    else:
        audio("f4.wav"); encode(draw, NF, "f4_v.mp4"); mux("f4_v.mp4", "f4.wav", "f4_venus.mp4")
