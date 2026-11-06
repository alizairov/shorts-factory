"""More atoms in one glass of water than glasses of water in all the oceans."""
import sys, math
import numpy as np
from story import *

ATOMS = "25,000,000,000,000,000,000,000,000"   # 2.5e25 atoms in a 250 ml glass
GLASSES = "5,300,000,000,000,000,000,000"       # 1.335e21 L of ocean / 0.25 L
T_Q, T_A, T_B, T_R = 0, 4.0, 11.5, 19.0
DUR = 27.0
NF = int(DUR * FPS)
rng = np.random.default_rng(5)
MOL = [(rng.uniform(140, 940), rng.uniform(640, 1300), rng.uniform(0, 6.3), rng.uniform(0.5, 1.5)) for _ in range(46)]


def glass(ctx, x, y, w, h, fill=0.8, a=1.0):
    ctx.set_source_rgba(0.3, 0.75, 1, 0.55 * a)
    top = y + h * (1 - fill)
    ctx.move_to(x + 6, top); ctx.line_to(x + w - 6, top); ctx.line_to(x + w - 16, y + h - 8); ctx.line_to(x + 16, y + h - 8); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.9 * a); ctx.set_line_width(7); ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(x, y); ctx.line_to(x + 12, y + h); ctx.line_to(x + w - 12, y + h); ctx.line_to(x + w, y); ctx.stroke()


def globe(ctx, x, y, r, a=1.0, t=0):
    glossy_ball(ctx, x, y, r, (0.15, 0.45, 1.0))
    ctx.save(); circle(ctx, x, y, r); ctx.clip()
    ctx.set_source_rgba(0.35, 0.8, 0.4, a)
    for (dx, dy, rr) in [(-0.4, -0.25, 0.3), (0.35, 0.2, 0.25), (0.05, -0.55, 0.16), (-0.1, 0.55, 0.14)]:
        circle(ctx, x + (dx + 0.05 * math.sin(t * 0.3)) * r, y + dy * r, rr * r); ctx.fill()
    ctx.restore()


def molecule(ctx, x, y, ang, s=1.0, a=1.0):
    for d in (-0.9, 0.9):
        hx, hy = x + 30 * s * math.cos(ang + d), y + 30 * s * math.sin(ang + d)
        glossy_ball(ctx, hx, hy, 11 * s, (0.95, 0.95, 1.0), glow=False)
    glossy_ball(ctx, x, y, 19 * s, (1.0, 0.3, 0.35), glow=False)


def counter(ctx, full, prog, y, size, col):
    n = int(len([c for c in full if c.isdigit()]) * prog)
    digits = [c for c in full if c.isdigit()]
    shown_digits = n
    # build string with same comma layout, unrevealed digits as random-ish rolling
    out = []; k = 0
    for ch in full:
        if ch.isdigit():
            out.append(ch if k < shown_digits else str((k * 7 + int(prog * 97)) % 10)); k += 1
        else:
            out.append(ch)
    s = "".join(out)
    label(ctx, s, W / 2, y, size, col=col)


def draw(ctx, fi):
    t = fi / FPS
    bg(ctx); progress(ctx, t, DUR)
    if t < T_A:
        lines(ctx, ["WHICH NUMBER", "IS *BIGGER*?"], 240, 96)
        a = fade_in(t, 0, 0.15)
        card(ctx, 70, 560, 450, 760, rgba=(1, 1, 1, 0.07 * a)); card(ctx, 560, 560, 450, 760, rgba=(1, 1, 1, 0.07 * a))
        label(ctx, "A", 295, 660, 90, col=CYAN, alpha=a); label(ctx, "B", 785, 660, 90, col=PINK, alpha=a)
        glass(ctx, 215, 760, 160, 240, a=a)
        globe(ctx, 785, 880, 130, a=a, t=t)
        lines(ctx, ["Atoms in", "*one glass*", "of water"], 0, 0, alpha=0)  # no-op keeps API symmetric
        for i, s in enumerate(["ATOMS IN", "ONE GLASS", "OF WATER"]):
            label(ctx, s, 295, 1110 + i * 58, 46, col=CYAN if i == 1 else (1, 1, 1), alpha=a)
        for i, s in enumerate(["GLASSES OF", "WATER IN ALL", "THE OCEANS"]):
            label(ctx, s, 785, 1110 + i * 58, 46, col=PINK if i == 2 else (1, 1, 1), alpha=a)
        b = fade_in(t, 1.6)
        lines(ctx, ["*Guess* before it's revealed…"], 1500, 58, alpha=b)
        return
    if t < T_B:
        lt = t - T_A
        lines(ctx, ["*A*: ATOMS IN ONE GLASS"], 240, 72, hl=CYAN)
        # zoom from glass into molecules
        z = eout(lt / 1.4)
        ga = 1 - z
        if ga > 0.01:
            ctx.save(); ctx.translate(W / 2, 950); ctx.scale(1 + 6 * z, 1 + 6 * z); ctx.translate(-W / 2, -950)
            glass(ctx, W / 2 - 120, 800, 240, 340, a=ga); ctx.restore()
        if z > 0.3:
            ma = ease((z - 0.3) / 0.5)
            card(ctx, 90, 560, W - 180, 800, rgba=(0.3, 0.75, 1, 0.12 * ma))
            for (x, y, a0, sp) in MOL:
                molecule(ctx, x + 12 * math.sin(t * 3 * sp + a0), y + 12 * math.cos(t * 2.5 * sp + a0), a0 + t * sp, 1.0, ma)
            rich(ctx, "250 ml · each molecule = 3 atoms (H₂O)".replace("₂", "2"), W / 2, 1420, 40, alpha=0.75 * ma)
        prog = eout((lt - 1.5) / 4.5)
        if lt > 1.5:
            counter(ctx, ATOMS, prog, 1600, 50, CYAN)
            if prog >= 0.999:
                rich(ctx, "*25 septillion* atoms", W / 2, 1720, 64, hl=CYAN, alpha=ease((lt - 6.1) / 0.3))
        return
    if t < T_R:
        lt = t - T_B
        lines(ctx, ["*B*: GLASSES IN ALL OCEANS"], 240, 72, hl=PINK)
        s = pop(lt / 0.5)
        ctx.save(); ctx.translate(W / 2, 960); ctx.scale(s, s); ctx.translate(-W / 2, -960)
        globe(ctx, W / 2, 960, 330, t=t)
        ctx.restore()
        # little glasses scooping water from the planet
        for k in range(6):
            u = ((lt * 0.7 + k / 6) % 1)
            gx = W / 2 + 420 * math.cos(k * 1.05 + 0.4) * (1 - u * 0.2)
            gy = 960 + 420 * math.sin(k * 1.05 + 0.4) * (1 - u * 0.2)
            glass(ctx, gx - 30, gy - 45, 60, 90, a=0.9 * math.sin(u * math.pi))
        rich(ctx, "1.34 billion km³ of ocean ÷ 250 ml", W / 2, 1420, 40, alpha=0.75)
        prog = eout((lt - 0.8) / 4.5)
        if lt > 0.8:
            counter(ctx, GLASSES, prog, 1600, 56, PINK)
            if prog >= 0.999:
                rich(ctx, "*5.3 sextillion* glasses", W / 2, 1720, 64, hl=PINK, alpha=ease((lt - 5.4) / 0.3))
        return
    lt = t - T_R
    lines(ctx, ["THE *GLASS* WINS"], 260, 110, hl=CYAN)
    # comparison: B as a tiny square, A as 4,700 of them
    a = fade_in(lt, 0)
    unit = 9
    cols = 69
    n = int(4700 * eout((lt - 0.3) / 3.2))
    x0 = (W - cols * unit) / 2
    for k in range(n):
        cx, cy = x0 + (k % cols) * unit, 520 + (k // cols) * unit
        ctx.set_source_rgba(*grad((k / 4700) * 0.3 + 0.55), 0.95); ctx.rectangle(cx, cy, unit - 2, unit - 2); ctx.fill()
    ctx.set_source_rgb(*PINK); ctx.rectangle(x0 - 40, 520 + 74 * unit, unit * 2, unit * 2); ctx.fill()
    rich(ctx, "*1 pink square* = glasses in all oceans", W / 2, 1250, 40, hl=PINK, alpha=a)
    rich(ctx, "*all squares* = atoms in one glass", W / 2, 1305, 40, hl=CYAN, alpha=a)
    if lt > 3.5:
        b = fade_in(lt, 3.5)
        label(ctx, "≈ 4,700×", W / 2, 1480, int(170 * pop((lt - 3.5) / 0.4)), col=YEL, alpha=b)
        lines(ctx, ["more atoms in one glass", "than glasses in every ocean."], 1620, 54, alpha=b)
    if lt > 5.6:
        lines(ctx, ["*Atoms are that small.*"], 1820, 56, alpha=fade_in(lt, 5.6), hl=LIME)


def audio(path):
    tr = Track(DUR)
    music(tr, DUR, bpm=100, seed=303, vol=0.5, base=196)
    tr.add(ding(2), 0.3); tr.add(ding(4), 1.0)
    for tt in (T_A, T_B, T_R):
        tr.add(whoosh(0.6, 0.13, int(tt)), tt - 0.35)
    tr.add(riser(4.5, 0.06), T_A + 1.5); tr.add(ding(9, 0.25), T_A + 6.0)
    tr.add(riser(4.5, 0.06), T_B + 0.8); tr.add(ding(11, 0.25), T_B + 5.3)
    for k in range(30):
        tr.add(pluck(note(k % 10 + 5, 523.25), 0.12, 0.03, 20), T_R + 0.3 + k * 0.1)
    tr.add(boom(1.6, 0.55), T_R + 3.5)
    for j, st in enumerate([0, 4, 7, 12]):
        tr.add(ding(st + 5, 0.14), T_R + 3.5 + j * 0.06)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "f3")
    else:
        audio("f3.wav"); encode(draw, NF, "f3_v.mp4"); mux("f3_v.mp4", "f3.wav", "f3_water.mp4")
