"""Sharks are older than trees — a scroll back through deep time."""
import sys, math
import numpy as np
from story import *

# (million years ago, title, subtitle, colour, icon)
EVENTS = [
    (0.3, "FIRST *HUMANS*", "300,000 years ago", PINK, "human"),
    (66, "DINOSAURS *DIE OUT*", "66 million years ago", YEL, "rex"),
    (230, "FIRST *DINOSAURS*", "230 million years ago", ORNG, "rex"),
    (385, "FIRST *TREES*", "385 million years ago", LIME, "tree"),
    (450, "FIRST *SHARKS*", "450 million years ago", CYAN, "shark"),
]
PX_PER_MY = 9.0       # timeline scale
TOP = 520             # screen y where "today" starts
STEP = 3.0
INTRO = 2.4
DUR = INTRO + STEP * (len(EVENTS) - 1) + 6.0
NF = int(DUR * FPS)


def ease_io(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def scroll_my(t):
    """which million-years-ago value sits at the focus line"""
    if t < INTRO: return EVENTS[0][0]
    k = (t - INTRO) / STEP
    i = min(int(k), len(EVENTS) - 2)
    u = ease_io(min(1, (k - i) / 0.55))
    a, b = EVENTS[i][0], EVENTS[i + 1][0]
    if t >= INTRO + STEP * (len(EVENTS) - 1):
        return EVENTS[-1][0]
    return a + (b - a) * u


def shark(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(-120, 0)
    ctx.curve_to(-60, -40, 40, -45, 110, -8)
    ctx.line_to(130, 0)
    ctx.curve_to(60, 30, -60, 30, -120, 0)
    ctx.close_path(); ctx.set_source_rgb(*col); ctx.fill()
    ctx.move_to(-10, -35); ctx.line_to(15, -85); ctx.line_to(35, -30); ctx.close_path(); ctx.fill()      # dorsal fin
    ctx.move_to(-110, 0); ctx.line_to(-165, -45); ctx.line_to(-150, 0); ctx.line_to(-165, 40); ctx.close_path(); ctx.fill()  # tail
    ctx.move_to(10, 15); ctx.line_to(-15, 50); ctx.line_to(35, 18); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(0.05, 0.05, 0.1); circle(ctx, 85, -10, 5); ctx.fill()
    ctx.restore()


def tree(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgb(0.55, 0.35, 0.2); ctx.rectangle(-12, -10, 24, 90); ctx.fill()
    ctx.set_source_rgb(*col)
    for (dx, dy, r) in [(0, -60, 55), (-45, -30, 40), (45, -30, 40), (0, -100, 38)]:
        circle(ctx, dx, dy, r); ctx.fill()
    ctx.restore()


def rex(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgb(*col)
    ctx.move_to(-120, 10); ctx.curve_to(-60, -30, 0, -40, 40, -50)
    ctx.line_to(70, -90); ctx.line_to(120, -85); ctx.line_to(125, -60); ctx.line_to(80, -55)
    ctx.curve_to(60, -20, 50, 10, 20, 20)
    ctx.line_to(30, 80); ctx.line_to(10, 80); ctx.line_to(0, 30); ctx.line_to(-30, 30); ctx.line_to(-30, 80); ctx.line_to(-50, 80)
    ctx.line_to(-50, 25); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(0.05, 0.05, 0.1); circle(ctx, 100, -75, 5); ctx.fill()
    ctx.restore()


def human(ctx, x, y, s, col):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.set_source_rgb(*col)
    circle(ctx, 0, -70, 22); ctx.fill()
    ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_source_rgb(*col)
    ctx.move_to(0, -45); ctx.line_to(0, 20); ctx.stroke()
    ctx.move_to(0, 20); ctx.line_to(-22, 80); ctx.stroke(); ctx.move_to(0, 20); ctx.line_to(22, 80); ctx.stroke()
    ctx.move_to(0, -30); ctx.line_to(-30, 10); ctx.stroke(); ctx.move_to(0, -30); ctx.line_to(30, 10); ctx.stroke()
    ctx.restore()


ICON = {"shark": shark, "tree": tree, "rex": rex, "human": human}
FOCUS_Y = 1120


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx); progress(ctx, t, DUR)
    my = scroll_my(t)
    lines(ctx, ["WHAT CAME FIRST:", "*SHARKS* OR *TREES*?"], 220, 84, hl=CYAN)
    # timeline axis (vertical), world y = my * PX_PER_MY, focus line fixed on screen
    off = FOCUS_Y - my * PX_PER_MY
    ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(6)
    ctx.move_to(160, max(380, off)); ctx.line_to(160, H); ctx.stroke()
    for m in range(0, 501, 50):
        y = off + m * PX_PER_MY
        if 380 < y < H:
            ctx.set_source_rgba(1, 1, 1, 0.4); ctx.rectangle(140, y - 2, 40, 4); ctx.fill()
            label(ctx, f"{m}", 105, y + 14, 34, alpha=0.5, anchor="r")
    label(ctx, "million years ago", 105, 395, 26, alpha=0.4, anchor="l")
    for i, (m, ti, sub, col, ic) in enumerate(EVENTS):
        y = off + m * PX_PER_MY
        if y < 330 or y > H + 200:
            continue
        circle(ctx, 160, y, 18); ctx.set_source_rgb(*col); ctx.fill()
        near = max(0, 1 - abs(y - FOCUS_Y) / 260)
        a = 0.35 + 0.65 * near
        if ic:
            ICON[ic](ctx, 860, y - 40, 0.9 + 0.4 * near, lighten(col, 0.0))
        rich(ctx, ti, 220, y + 18, 54, alpha=a, hl=col, anchor="l")
        if sub:
            rich(ctx, sub, 220, y + 70, 36, alpha=a * 0.7, anchor="l")
    # gap bracket between trees and sharks at the end
    tend = INTRO + STEP * (len(EVENTS) - 1)
    if t > tend + 0.6:
        b = fade_in(t, tend + 0.6, 0.4)
        y1, y2 = off + 385 * PX_PER_MY, off + 450 * PX_PER_MY
        ctx.set_source_rgba(*YEL, b); ctx.set_line_width(6)
        ctx.move_to(990, y1); ctx.line_to(1020, y1); ctx.line_to(1020, y2); ctx.line_to(990, y2); ctx.stroke()
        ctx.set_source_rgba(0.03, 0.01, 0.08, 0.9 * b); ctx.rectangle(0, 1380, W, 540); ctx.fill()
        label(ctx, "SHARKS ARE", W / 2, 1500, 76, alpha=b)
        label(ctx, "~65 MILLION YEARS", W / 2, 1600, 88, col=YEL, alpha=b)
        label(ctx, "OLDER THAN TREES", W / 2, 1700, 76, alpha=b)
        if t > tend + 2.8:
            c = fade_in(t, tend + 2.8, 0.4)
            lines(ctx, ["They survived *all 5* mass extinctions."], 1820, 46, alpha=c, hl=CYAN)
    if t < INTRO:
        lines(ctx, ["Let's travel *back in time*…"], 640, 58, alpha=fade_in(t, 0.4))


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=90, seed=505, vol=0.55, base=174.6)
    tr.add(ding(3), 0.5)
    for i in range(1, len(EVENTS)):
        ta = INTRO + STEP * (i - 1)
        tr.add(whoosh(0.7, 0.12, i), ta)
        tr.add(ding(i * 2 + 1), ta + STEP * 0.55)
    tend = INTRO + STEP * (len(EVENTS) - 1)
    tr.add(boom(1.6, 0.55), tend + 0.6)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(ding(st + 5, 0.14), tend + 0.6 + j * 0.06)
    tr.save(path, DUR)


if __name__ == "__main__":
    print("DUR", DUR)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "f5")
    else:
        audio("f5.wav"); encode(draw, NF, "f5_v.mp4"); mux("f5_v.mp4", "f5.wav", "f5_sharks.mp4")
