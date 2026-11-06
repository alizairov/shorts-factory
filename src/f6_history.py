"""3 history timelines that break your brain."""
import sys, math
from story import *

FACT_LEN = 9.6
INTRO = 1.6
DUR = INTRO + 3 * FACT_LEN + 2.4
NF = int(DUR * FPS)
TLY = 1080           # timeline y
X0, X1 = 110, W - 110


def pyramid(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-90, 0); ctx.line_to(0, -110); ctx.line_to(90, 0); ctx.close_path(); ctx.set_source_rgb(*col); ctx.fill()
    ctx.move_to(0, -110); ctx.line_to(30, 0); ctx.line_to(90, 0); ctx.close_path(); ctx.set_source_rgba(0, 0, 0, 0.18); ctx.fill()
    ctx.restore()


def crown(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgb(*col)
    ctx.move_to(-70, 0); ctx.line_to(-70, -70); ctx.line_to(-35, -35); ctx.line_to(0, -90); ctx.line_to(35, -35); ctx.line_to(70, -70); ctx.line_to(70, 0); ctx.close_path(); ctx.fill()
    for dx in (-70, 0, 70):
        circle(ctx, dx, -78 if dx else -98, 10); ctx.fill()
    ctx.restore()


def rocket(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgb(*col)
    ctx.move_to(0, -120); ctx.curve_to(35, -80, 35, -30, 30, 0); ctx.line_to(-30, 0); ctx.curve_to(-35, -30, -35, -80, 0, -120); ctx.fill()
    ctx.move_to(-30, -30); ctx.line_to(-55, 5); ctx.line_to(-30, 0); ctx.fill(); ctx.move_to(30, -30); ctx.line_to(55, 5); ctx.line_to(30, 0); ctx.fill()
    ctx.set_source_rgb(0.1, 0.1, 0.2); circle(ctx, 0, -70, 12); ctx.fill()
    ctx.set_source_rgb(*ORNG); ctx.move_to(-18, 0); ctx.line_to(0, 35); ctx.line_to(18, 0); ctx.fill()
    ctx.restore()


def mammoth(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgb(*col)
    ctx.save(); ctx.scale(1, 0.75); circle(ctx, -10, -95, 75); ctx.fill(); ctx.restore()
    circle(ctx, 60, -95, 42); ctx.fill()
    for dx in (-60, -20, 15, 45):
        ctx.rectangle(dx - 12, -50, 24, 50); ctx.fill()
    ctx.set_line_width(18); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(90, -85); ctx.curve_to(110, -40, 95, -10, 110, 0); ctx.stroke()
    ctx.set_source_rgb(1, 0.97, 0.9); ctx.set_line_width(9)
    ctx.move_to(80, -70); ctx.curve_to(120, -50, 140, -80, 135, -105); ctx.stroke()
    ctx.restore()


def college(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgb(*col)
    ctx.move_to(-90, -80); ctx.line_to(0, -125); ctx.line_to(90, -80); ctx.close_path(); ctx.fill()
    for dx in (-70, -35, 0, 35, 70):
        ctx.rectangle(dx - 9, -78, 18, 68); ctx.fill()
    ctx.rectangle(-95, -12, 190, 12); ctx.fill()
    ctx.restore()


def stepped(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgb(*col)
    for k in range(4):
        w = 180 - k * 40
        ctx.rectangle(-w / 2, -(k + 1) * 26, w, 26); ctx.fill()
    ctx.rectangle(-18, -130, 36, 26); ctx.fill()
    ctx.restore()


FACTS = [
    dict(title=["CLEOPATRA LIVED CLOSER", "TO THE *MOON LANDING*", "THAN TO THE *PYRAMIDS*"],
         rng=(-2800, 2200),
         pts=[(-2560, "GREAT PYRAMID", "2560 BC", pyramid, YEL), (-50, "CLEOPATRA", "69–30 BC", crown, PINK), (1969, "MOON LANDING", "1969", rocket, CYAN)],
         gaps=[(-2560, -50, "~2,500 YEARS", YEL), (-50, 1969, "~2,000 YEARS", CYAN)]),
    dict(title=["*MAMMOTHS* WERE STILL", "ALIVE WHEN THE GREAT", "PYRAMID WAS BUILT"],
         rng=(-2800, -1700),
         pts=[(-2560, "GREAT PYRAMID", "2560 BC", pyramid, YEL), (-2000, "LAST MAMMOTHS", "~2000 BC", mammoth, ORNG)],
         gaps=[(-2560, -2000, "~500 YEARS TOGETHER", ORNG)]),
    dict(title=["*OXFORD UNIVERSITY*", "IS OLDER THAN", "THE *AZTECS*"],
         rng=(1000, 1600),
         pts=[(1096, "OXFORD", "teaching by 1096", college, LIME), (1325, "AZTEC CAPITAL", "founded 1325", stepped, PINK)],
         gaps=[(1096, 1325, "~230 YEARS EARLIER", LIME)]),
]


def xof(year, rng):
    a, b = rng
    return X0 + (X1 - X0) * (year - a) / (b - a)


def yr(y):
    return f"{-y} BC" if y < 0 else f"{y} AD"


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx); progress(ctx, t, DUR)
    if t < INTRO:
        lines(ctx, ["HISTORY IS", "*WEIRDER*", "THAN YOU THINK"], 700, 120, alpha=1.0)
        lines(ctx, ["3 timelines that break your brain"], 1200, 50, alpha=fade_in(t, 0.4), hl=YEL)
        return
    k = min(int((t - INTRO) / FACT_LEN), 2)
    lt = t - INTRO - k * FACT_LEN
    f = FACTS[k]
    a = window(lt, 0, FACT_LEN - 0.2, 0.3) if k < 2 else ease(lt / 0.3)
    label(ctx, f"{k + 1} / 3", W / 2, 150, 44, col=YEL, alpha=a)
    lines(ctx, f["title"], 260, 76, alpha=a)
    # axis
    ctx.set_source_rgba(1, 1, 1, 0.35 * a); ctx.set_line_width(6)
    ctx.move_to(X0, TLY); ctx.line_to(X1, TLY); ctx.stroke()
    lo, hi = f["rng"]
    span = hi - lo
    step = 1000 if span > 3000 else (200 if span >= 1000 else 100)
    for y in range((lo // step) * step, hi + 1, step):
        if lo <= y <= hi:
            x = xof(y, f["rng"])
            ctx.set_source_rgba(1, 1, 1, 0.3 * a); ctx.rectangle(x - 2, TLY - 12, 4, 24); ctx.fill()
            label(ctx, yr(y) if y else "0", x, TLY + 50, 26, alpha=0.45 * a)
    # points appear one by one
    for i, (y, name, date, icon, col) in enumerate(f["pts"]):
        ti = 0.6 + i * 1.0
        if lt < ti: continue
        u = pop((lt - ti) / 0.4)
        x = xof(y, f["rng"])
        b = ease((lt - ti) / 0.25) * a
        ctx.set_source_rgba(*col, b); circle(ctx, x, TLY, 16 * u); ctx.fill()
        up = i % 2 == 0 or len(f["pts"]) == 2
        iy = TLY - 190 if up else TLY - 190
        ctx.save(); ctx.translate(x, iy + 90); ctx.scale(u, u); ctx.translate(-x, -(iy + 90))
        icon(ctx, x, iy + 90, 0.9, col)
        ctx.restore()
        lx = min(max(x, 170), W - 170)
        label(ctx, name, lx, iy - 95, 40, col=col, alpha=b)
        label(ctx, date, lx, iy - 50, 32, alpha=0.75 * b)
    # gaps
    tg = 0.6 + len(f["pts"]) * 1.0 + 0.3
    for j, (ya, yb, txt, col) in enumerate(f["gaps"]):
        tj = tg + j * 0.9
        if lt < tj: continue
        u = eout((lt - tj) / 0.6)
        xa, xb = xof(ya, f["rng"]), xof(yb, f["rng"])
        gy = TLY + 120 + j * 150
        ctx.set_source_rgba(*col, a); ctx.rectangle(xa, gy, (xb - xa) * u, 30); ctx.fill()
        label(ctx, txt, (xa + xb) / 2, gy + 95, 50, col=col, alpha=ease((lt - tj - 0.3) / 0.3) * a)
    # punchline per fact
    tp = tg + len(f["gaps"]) * 0.9 + 0.8
    if lt > tp:
        c = ease((lt - tp) / 0.35) * a
        punch = ["The pyramids were *ancient* even to her.",
                 "Egyptians and mammoths *shared the planet*.",
                 "Oxford was already *229 years old*."][k]
        rich(ctx, punch, W / 2, 1640, 46, alpha=c, hl=YEL)
    if t > INTRO + 3 * FACT_LEN - 0.2:
        d = fade_in(t, INTRO + 3 * FACT_LEN - 0.2, 0.4)
        lines(ctx, ["Which one surprised you most?", "*Comment 1, 2 or 3*"], 1790, 48, alpha=d, hl=PINK)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=100, seed=606, vol=0.5, base=196)
    tr.add(boom(1.2, 0.35), 0.0); tr.add(ding(5), 0.4)
    for k, f in enumerate(FACTS):
        t0 = INTRO + k * FACT_LEN
        tr.add(whoosh(0.6, 0.12, k), t0 - 0.3)
        for i in range(len(f["pts"])):
            tr.add(ding(i * 2 + k + 2, 0.18), t0 + 0.6 + i * 1.0)
        tg = 0.6 + len(f["pts"]) * 1.0 + 0.3
        for j in range(len(f["gaps"])):
            tr.add(riser(0.6, 0.05), t0 + tg + j * 0.9)
        tp = tg + len(f["gaps"]) * 0.9 + 0.8
        for j, st in enumerate([0, 4, 7]):
            tr.add(ding(st + 7, 0.13), t0 + tp + j * 0.05)
    tr.save(path, DUR)


if __name__ == "__main__":
    print("DUR", DUR)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "f6")
    else:
        audio("f6.wav"); encode(draw, NF, "f6_v.mp4"); mux("f6_v.mp4", "f6.wav", "f6_history.mp4")
