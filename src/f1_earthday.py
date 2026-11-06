"""Earth's 4.54-billion-year history squeezed into 24 hours."""
import sys, math
from story import *

AGE = 4.54e9
def hrs(years_ago): return 24 * (1 - years_ago / AGE)

EVENTS = [  # years ago, title, subtitle, color
    (3.8e9, "FIRST *LIFE*", "tiny cells in the ocean", CYAN),
    (2.4e9, "*OXYGEN* FILLS THE AIR", "thanks to bacteria", LIME),
    (538e6, "*ANIMALS* EXPLODE", "the Cambrian explosion", ORNG),
    (230e6, "*DINOSAURS* ARRIVE", "", PINK),
    (66e6, "DINOSAURS *WIPED OUT*", "an asteroid hits", YEL),
]
T0 = 3.0
MOVE, HOLD = 1.5, 1.9
keys = [(0, 0.0), (T0, 0.0)]
t = T0
for ya, *_ in EVENTS:
    t += MOVE; keys.append((t, hrs(ya)))
    t += HOLD; keys.append((t, hrs(ya)))
T_ZOOM = t
T_HUM = T_ZOOM + 2.6
T_HIST = T_HUM + 3.6
DUR = T_HIST + 4.4
NF = int(DUR * FPS)
CX, CY, R = W / 2, 930, 380


def clock_h(tt):
    for (a, ha), (b, hb) in zip(keys, keys[1:]):
        if a <= tt <= b:
            return ha + (hb - ha) * ease((tt - a) / (b - a))
    return keys[-1][1]


def hm(h):
    m = int(round(h * 60)); return f"{(m // 60) % 24:02d}:{m % 60:02d}"


def ang(h): return -math.pi / 2 + 2 * math.pi * h / 24


def draw(ctx, fi):
    tt = fi / FPS
    bg(ctx)
    progress(ctx, tt, DUR)
    zoomed = tt >= T_ZOOM
    h = clock_h(tt) if not zoomed else hrs(66e6)
    # header
    lines(ctx, ["IF EARTH'S HISTORY", "WAS *ONE DAY*…"], 230, 84)
    # clock face
    za = 1 - ease((tt - T_ZOOM) / 0.6)
    if za > 0:
        ctx.save(); ctx.translate(CX, CY); s = 1 + 0.25 * (1 - za); ctx.scale(s, s); ctx.translate(-CX, -CY)
        card(ctx, CX - R - 40, CY - R - 40, 2 * R + 80, 2 * R + 80, r=R + 40, rgba=(1, 1, 1, 0.05 * za))
        # elapsed arc (gradient)
        segs = 120
        for k in range(segs):
            h0 = 24 * k / segs; h1 = 24 * (k + 1) / segs
            if h0 >= h: break
            ctx.set_source_rgba(*grad(k / segs * 0.85), za)
            ctx.set_line_width(46)
            ctx.arc(CX, CY, R - 30, ang(h0), ang(min(h1, h)) + 0.002); ctx.stroke()
        for k in range(24):
            a = ang(k)
            big = k % 6 == 0
            ctx.set_source_rgba(1, 1, 1, (0.9 if big else 0.35) * za); ctx.set_line_width(6 if big else 3)
            ctx.move_to(CX + (R + 6) * math.cos(a), CY + (R + 6) * math.sin(a))
            ctx.line_to(CX + (R + (30 if big else 18)) * math.cos(a), CY + (R + (30 if big else 18)) * math.sin(a)); ctx.stroke()
            if big:
                label(ctx, f"{k:02d}:00", CX + (R + 82) * math.cos(a), CY + (R + 82) * math.sin(a) + 14, 34, alpha=0.7 * za)
        # event dots
        for ya, ti, sub, col in EVENTS:
            eh = hrs(ya)
            if h >= eh - 0.01:
                a = ang(eh)
                ctx.set_source_rgba(*col, za); circle(ctx, CX + (R - 30) * math.cos(a), CY + (R - 30) * math.sin(a), 16); ctx.fill()
                ctx.set_source_rgba(1, 1, 1, za); ctx.set_line_width(4); circle(ctx, CX + (R - 30) * math.cos(a), CY + (R - 30) * math.sin(a), 16); ctx.stroke()
        # hand
        a = ang(h)
        ctx.set_source_rgba(1, 1, 1, za); ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(CX, CY); ctx.line_to(CX + (R - 70) * math.cos(a), CY + (R - 70) * math.sin(a)); ctx.stroke()
        circle(ctx, CX, CY, 16); ctx.fill()
        label(ctx, hm(h), CX, CY + 130, 92, alpha=za)
        ctx.restore()
    # captions for events
    if tt < T0:
        a = fade_in(tt, 0.4)
        lines(ctx, ["00:00 — *EARTH IS BORN*", "4.54 billion years ago"], 1560, 62, alpha=a)
    for i, (ya, ti, sub, col) in enumerate(EVENTS):
        t_arrive = T0 + MOVE * (i + 1) + HOLD * i
        a = window(tt, t_arrive - 0.15, t_arrive + HOLD - 0.05, 0.2)
        if a > 0:
            rich(ctx, f"{hm(hrs(ya))}", W / 2, 1530, 110, alpha=a, base=col)
            rich(ctx, ti, W / 2, 1640, 64, alpha=a, hl=col)
            if sub:
                rich(ctx, sub, W / 2, 1720, 44, alpha=a * 0.75)
    # zoom into the last seconds
    if zoomed:
        a = fade_in(tt, T_ZOOM + 0.2, 0.5)
        sec = min(54, (tt - T_ZOOM) / 2.2 * 54)
        hh = f"23:59:{int(sec):02d}"
        card(ctx, 90, 650, W - 180, 520, rgba=(1, 1, 1, 0.07 * a))
        label(ctx, "LAST MINUTE OF THE DAY", W / 2, 740, 44, alpha=0.7 * a)
        label(ctx, hh, W / 2, 940, 190, col=YEL if tt < T_HUM else PINK, alpha=a)
        if tt >= T_HUM:
            b = fade_in(tt, T_HUM, 0.3)
            s = pop((tt - T_HUM) / 0.4)
            label(ctx, "HUMANS APPEAR", W / 2, 1090, int(80 * s), col=PINK, alpha=b)
            lines(ctx, ["We've existed for", "only the last *6 seconds*"], 1500, 64, alpha=b)
        if tt >= T_HIST:
            c = fade_in(tt, T_HIST, 0.3)
            ctx.set_source_rgba(0.04, 0.02, 0.1, 0.85 * c); ctx.rectangle(0, 1380, W, 420); ctx.fill()
            lines(ctx, ["All of written history —", "pyramids, empires, the internet —", "fits in the last *0.1 second*"], 1500, 60, alpha=c, hl=LIME)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=96, seed=101, vol=0.55, base=196)
    tr.add(ding(0, 0.25), 0.4)
    for i in range(len(EVENTS)):
        ta = T0 + MOVE * (i + 1) + HOLD * i
        tr.add(whoosh(0.5, 0.1, i), ta - 0.5)
        tr.add(ding(i * 2 + 2), ta)
    tr.add(riser(2.2, 0.08), T_ZOOM)
    tr.add(boom(), T_HUM); tr.add(ding(12, 0.3), T_HUM)
    tr.add(whoosh(0.5, 0.12, 9), T_HIST - 0.3)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(ding(st + 5, 0.15), T_HIST + 0.1 + j * 0.06)
    tr.save(path, DUR)


if __name__ == "__main__":
    print("DUR", DUR)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "f1")
    else:
        audio("f1.wav"); encode(draw, NF, "f1_v.mp4"); mux("f1_v.mp4", "f1.wav", "f1_earthday.mp4")
