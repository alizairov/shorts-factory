"""You never see the present: how old the light you see really is."""
import sys, math
import numpy as np
from story import *

ITEMS = [  # name, ago-text, kind, colour
    ("THE MOON", "1.3 SECONDS AGO", "moon", (0.82, 0.82, 0.9)),
    ("THE SUN", "8 MINUTES AGO", "sun", (1.0, 0.75, 0.2)),
    ("JUPITER", "ABOUT 43 MINUTES AGO", "jupiter", (0.92, 0.7, 0.5)),
    ("PLUTO", "5.5 HOURS AGO", "pluto", (0.85, 0.75, 0.68)),
    ("THE NEAREST STAR", "4.2 YEARS AGO", "star", (1.0, 0.55, 0.45)),
    ("ANDROMEDA GALAXY", "2.5 MILLION YEARS AGO", "galaxy", (0.75, 0.7, 1.0)),
]
INTRO = 2.6
STEP = 3.9
DUR = INTRO + STEP * len(ITEMS) + 4.0
NF = int(DUR * FPS)
OBJ_Y = 820
EARTH_Y = 1380
rng = np.random.default_rng(3)
STARS = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 2.2), rng.uniform(0, 6.3)) for _ in range(170)]
GAL = [(rng.normal(0, 1), rng.uniform(0, 2 * math.pi)) for _ in range(900)]


def obj(ctx, kind, x, y, r, c, t):
    if kind == "sun":
        for k, a in [(1.6, 0.08), (1.3, 0.15)]:
            ctx.set_source_rgba(1, 0.6, 0.1, a); circle(ctx, x, y, r * k); ctx.fill()
    if kind == "star":
        for k in range(6):
            ctx.set_source_rgba(*c, 0.10); circle(ctx, x, y, r * (0.5 + k * 0.35)); ctx.fill()
        ctx.set_source_rgba(1, 1, 1, 0.9); ctx.set_line_width(4)
        for a in (0, math.pi / 2):
            ctx.move_to(x - r * 2.2 * math.cos(a), y - r * 2.2 * math.sin(a)); ctx.line_to(x + r * 2.2 * math.cos(a), y + r * 2.2 * math.sin(a)); ctx.stroke()
        glossy_ball(ctx, x, y, r * 0.5, lighten(c, 0.4), glow=False); return
    if kind == "galaxy":
        ctx.save(); ctx.translate(x, y); ctx.rotate(-0.5); ctx.scale(1, 0.42)
        for (rr, a0) in GAL:
            d = abs(rr) * r * 0.9
            a = a0 + d / r * 2.2 + t * 0.05
            arm = 1 if int(a0 * 2 / math.pi) % 2 else -1
            ctx.set_source_rgba(*grad(min(abs(rr) / 3, 0.99) * 0.6 + 0.0), 0.7)
            circle(ctx, d * math.cos(a), d * math.sin(a) * arm, 4.5); ctx.fill()
        ctx.set_source_rgba(1, 0.95, 0.85, 0.9); circle(ctx, 0, 0, r * 0.18); ctx.fill()
        ctx.restore(); return
    glossy_ball(ctx, x, y, r, c, glow=kind != "moon")
    if kind == "jupiter":
        ctx.save(); circle(ctx, x, y, r); ctx.clip()
        for k in range(-4, 5):
            ctx.set_source_rgba(0.7, 0.45, 0.3, 0.35); ctx.rectangle(x - r, y + k * r * 0.22, 2 * r, r * 0.09); ctx.fill()
        ctx.restore()
    if kind in ("moon", "pluto"):
        for (dx, dy, rr) in [(-0.3, -0.2, 0.15), (0.3, 0.3, 0.1), (0.15, -0.4, 0.08)]:
            ctx.set_source_rgba(0, 0, 0, 0.15); circle(ctx, x + dx * r, y + dy * r, rr * r); ctx.fill()


def earth(ctx, x, y, r):
    glossy_ball(ctx, x, y, r, (0.2, 0.5, 1.0))
    ctx.save(); circle(ctx, x, y, r); ctx.clip()
    ctx.set_source_rgb(0.35, 0.85, 0.4)
    for (dx, dy, rr) in [(-0.35, -0.2, 0.32), (0.3, 0.25, 0.28), (0.1, -0.5, 0.18)]:
        circle(ctx, x + dx * r, y + dy * r, rr * r); ctx.fill()
    ctx.restore()
    # tiny person/eye looking up
    rich(ctx, "YOU", x, y + r + 60, 40, alpha=0.8)


def draw(ctx, fi):
    tt = fi / FPS
    bg(ctx)
    for (sx, sy, sr, ph) in STARS:
        ctx.set_source_rgba(1, 1, 1, 0.3 + 0.25 * math.sin(tt * 2 + ph)); circle(ctx, sx, sy, sr); ctx.fill()
    progress(ctx, tt, DUR)
    lines(ctx, ["YOU NEVER SEE", "*THE PRESENT*"], 230, 92)
    earth(ctx, W / 2, EARTH_Y, 80)
    if tt < INTRO:
        a = fade_in(tt, 0.3)
        lines(ctx, ["Light takes time to travel.", "So everything you see", "is already *in the past*."], 1640, 54, alpha=a)
        return
    i = min(int((tt - INTRO) / STEP), len(ITEMS) - 1)
    lt = tt - INTRO - i * STEP
    name, ago, kind, c = ITEMS[i]
    a = window(lt, 0, STEP - 0.1, 0.3) if i < len(ITEMS) - 1 or tt < INTRO + STEP * len(ITEMS) else 1
    a = window(lt, 0, STEP - 0.1, 0.3) if (i < len(ITEMS) - 1) else ease(lt / 0.3)
    s = pop(lt / 0.45)
    rad = {"moon": 90, "sun": 150, "jupiter": 130, "pluto": 60, "star": 70, "galaxy": 230}[kind]
    ctx.save(); ctx.translate(W / 2, OBJ_Y); ctx.scale(s * a + 0.001, s * a + 0.001); ctx.translate(-W / 2, -OBJ_Y)
    obj(ctx, kind, W / 2, OBJ_Y, rad, c, tt)
    ctx.restore()
    # light beam travelling down to Earth
    u = eout((lt - 0.3) / 1.4)
    y0, y1 = OBJ_Y + rad * 0.9, EARTH_Y - 90
    yb = y0 + (y1 - y0) * u
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for wdt, al in [(30, 0.10), (14, 0.3), (5, 0.95)]:
        ctx.set_source_rgba(1, 0.95, 0.6, al * a); ctx.set_line_width(wdt)
        ctx.move_to(W / 2, y0); ctx.line_to(W / 2, yb); ctx.stroke()
    if u > 0.02:
        ctx.set_source_rgba(1, 1, 0.8, a); circle(ctx, W / 2, yb, 10); ctx.fill()
    label(ctx, name, W / 2, 520, 64, col=lighten(c, 0.3), alpha=a)
    if lt > 1.5:
        b = ease((lt - 1.5) / 0.3) * a
        rich(ctx, "YOU SEE IT AS IT WAS", W / 2, 1610, 48, alpha=b * 0.8)
        label(ctx, ago, W / 2, 1720, 84 if len(ago) < 16 else 70, col=YEL, alpha=b)
    if i == len(ITEMS) - 1 and lt > 2.6:
        b = ease((lt - 2.6) / 0.4)
        lines(ctx, ["That light left before *our species* existed.", "Looking up = *looking back in time*."], 1815, 42, alpha=b, hl=PINK)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=84, seed=202, vol=0.5, base=174.6)
    for i in range(len(ITEMS)):
        t0 = INTRO + i * STEP
        tr.add(whoosh(0.5, 0.1, i), t0 - 0.3)
        tr.add(riser(1.4, 0.05), t0 + 0.3)
        tr.add(ding(i * 2 + 3), t0 + 1.6)
    tr.add(boom(1.8, 0.5), INTRO + (len(ITEMS) - 1) * STEP + 2.6)
    tr.save(path, DUR)


if __name__ == "__main__":
    print("DUR", DUR)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "f2")
    else:
        audio("f2.wav"); encode(draw, NF, "f2_v.mp4"); mux("f2_v.mp4", "f2.wav", "f2_light.mp4")
