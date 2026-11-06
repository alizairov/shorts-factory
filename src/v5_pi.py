import sys, math
import numpy as np, cairo
from common import *

U = 250                      # px per unit
R = U / 2                    # diameter = 1
X0 = (W - math.pi * U) / 2   # 0 on the number line
LY = 1180                    # number line y
DUR = 18.0
NF = int(DUR * FPS)
T_ROLL0, T_ROLL1 = 3.0, 9.5
PI_DIGITS = "3.14159265358979323846264338327950288419716939937510"


def ease(u):
    u = min(max(u, 0), 1)
    return u * u * (3 - 2 * u)


def theta(t):
    return 2 * math.pi * ease((t - T_ROLL0) / (T_ROLL1 - T_ROLL0))


def draw(ctx, fi):
    t = fi / FPS
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, 0.07, 0.04, 0.16)
    g.add_color_stop_rgb(1, 0.02, 0.01, 0.06)
    ctx.set_source(g); ctx.paint()
    # subtle grid
    ctx.set_source_rgba(1, 1, 1, 0.04); ctx.set_line_width(1)
    for gx in range(0, W, 60):
        ctx.move_to(gx, 0); ctx.line_to(gx, H); ctx.stroke()
    for gy in range(0, H, 60):
        ctx.move_to(0, gy); ctx.line_to(W, gy); ctx.stroke()

    th = theta(t)
    cx, cy = X0 + th * R, LY - R
    # number line
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.set_source_rgba(1, 1, 1, 0.5); ctx.set_line_width(5)
    ctx.move_to(40, LY); ctx.line_to(W - 40, LY); ctx.stroke()
    for k in range(5):
        x = X0 + k * U
        ctx.move_to(x, LY - 16); ctx.line_to(x, LY + 16); ctx.stroke()
        label(ctx, str(k), x, LY + 80, 54, alpha=0.75)
    # unrolled circumference (gradient)
    seg = 40
    for k in range(seg):
        a0, a1 = th * k / seg, th * (k + 1) / seg
        ctx.set_source_rgb(*grad(k / seg * 0.95))
        ctx.set_line_width(14)
        ctx.move_to(X0 + a0 * R, LY); ctx.line_to(X0 + a1 * R, LY); ctx.stroke()
    # remaining circumference on the circle (the part not yet unrolled)
    for k in range(seg):
        s0, s1 = k / seg * 2 * math.pi, (k + 1) / seg * 2 * math.pi
        if s1 <= th:
            continue
        s0 = max(s0, th)
        a1 = math.pi / 2 + th - s0 + 2 * math.pi
        a0 = math.pi / 2 + th - s1 + 2 * math.pi
        ctx.set_source_rgb(*grad(k / seg * 0.95))
        ctx.set_line_width(14)
        ctx.arc(cx, cy, R, a0, a1)
        ctx.stroke()
    ctx.set_source_rgba(1, 1, 1, 0.12); ctx.set_line_width(3); circle(ctx, cx, cy, R); ctx.stroke()
    if t < T_ROLL0:
        a = ease(t / 0.6)
        ctx.set_source_rgba(1, 1, 1, 0.15 * a); circle(ctx, cx, cy, R); ctx.fill()
    # diameter marker
    if t < T_ROLL0 + 0.4:
        a = ease(t / 0.8) * (1 - ease((t - T_ROLL0) / 0.4))
        ctx.set_source_rgba(1, 1, 1, a); ctx.set_line_width(6)
        ctx.move_to(cx, cy - R + 8); ctx.line_to(cx, cy + R - 8); ctx.stroke()
        label(ctx, "1", cx + 44, cy + 18, 64, col=grad(0.62), alpha=a)
    # cycloid trail of the start point
    if th > 0:
        ctx.set_source_rgba(1, 1, 1, 0.55); ctx.set_line_width(4)
        ctx.set_dash([10, 12])
        n = 120
        for k in range(n + 1):
            a = th * k / n
            px = X0 + R * (a - math.sin(a)); py = LY - R * (1 - math.cos(a))
            (ctx.move_to if k == 0 else ctx.line_to)(px, py)
        ctx.stroke(); ctx.set_dash([])
    # the point
    px = X0 + R * (th - math.sin(th)); py = LY - R * (1 - math.cos(th))
    ctx.set_source_rgba(1, 0.36, 0.88, 0.3); circle(ctx, px, py, 26); ctx.fill()
    glossy_ball(ctx, px, py, 15, (1, 0.36, 0.88), glow=False)
    # spokes for rotation feel
    ctx.set_source_rgba(1, 1, 1, 0.25); ctx.set_line_width(3)
    for k in range(3):
        a = math.pi / 2 + th + k * 2 * math.pi / 3
        ctx.move_to(cx, cy); ctx.line_to(cx + R * math.cos(a), cy + R * math.sin(a)); ctx.stroke()
    circle(ctx, cx, cy, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()

    # hook
    a = 1 - ease((t - T_ROLL1 - 0.2) / 0.4)
    label(ctx, "ROLL A CIRCLE", W / 2, 330, 92, alpha=a)
    label(ctx, "WITH DIAMETER 1...", W / 2, 430, 80, col=grad(0.45), alpha=a)
    # reveal
    if t > T_ROLL1:
        b = ease((t - T_ROLL1) / 0.35)
        pop = 1 + 0.25 * (1 - ease((t - T_ROLL1) / 0.25))
        label(ctx, "π", W / 2, 520, int(260 * pop), col=grad(0.18), alpha=b)
        # landing marker
        lx = X0 + math.pi * U
        ctx.set_source_rgba(*grad(0.18), b); ctx.set_line_width(5)
        ctx.move_to(lx, LY + 110); ctx.line_to(lx, LY + 150); ctx.stroke()
        label(ctx, "3.14", lx, LY + 215, 58, col=grad(0.18), alpha=b)
    if t > T_ROLL1 + 1.2:
        c = ease((t - T_ROLL1 - 1.2) / 0.4)
        label(ctx, "IT ALWAYS LANDS AT π", W / 2, 680, 62, alpha=c)
    if t > T_ROLL1 + 2.6:
        # digit ticker
        n = int(min(len(PI_DIGITS), 4 + (t - T_ROLL1 - 2.6) * 7))
        s = PI_DIGITS[:n]
        ctx.select_font_face("DejaVu Sans Mono", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(54)
        lines = [s[i:i + 15] for i in range(0, len(s), 15)]
        for li, line in enumerate(lines):
            e = ctx.text_extents("0" * 15)
            x0 = W / 2 - e.width / 2
            for ci, ch in enumerate(line):
                gi = li * 15 + ci
                ctx.set_source_rgb(*grad(gi / 40))
                ctx.move_to(x0 + ci * e.x_advance / 15, 1560 + li * 70)
                ctx.show_text(ch)
    if t > DUR - 3.2:
        d = ease((t - DUR + 3.2) / 0.4)
        label(ctx, "...AND IT NEVER ENDS", W / 2, 1860, 52, col=grad(0.62), alpha=d)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=96, seed=3, vol=0.7, base=220)
    # rising tone while rolling
    n = np.arange(int(SR * (T_ROLL1 - T_ROLL0))) / SR
    f = 220 + 440 * (n / n[-1]) ** 2
    ph = 2 * np.pi * np.cumsum(f) / SR
    tr.add(np.sin(ph) * 0.06 * np.minimum(1, n * 3), T_ROLL0)
    for k, st in enumerate([0, 2, 4, 7, 9, 12]):
        tr.add(pluck(note(st, 261.63), 1.6, 0.18, 2.5), T_ROLL1 + k * 0.05)
    for k in range(48):
        tt = T_ROLL1 + 2.6 + k / 7
        if tt < DUR:
            tr.add(pluck(note(int(PI_DIGITS.replace('.', '')[k]) + 3, 523.25), 0.25, 0.05, 14), tt)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "v5")
    else:
        audio("v5.wav")
        encode(draw, NF, "v5_video.mp4")
        mux("v5_video.mp4", "v5.wav", "reels_5_pi.mp4")
        print("dur", DUR)
