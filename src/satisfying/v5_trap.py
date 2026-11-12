"""V5: Its path becomes a wall. Every bounce cuts the space in two — how long until it's trapped?
Event-driven: the ball always moves inside a convex cell; each straight run from wall to wall is a
chord of that cell, so it splits the cell. The half without the ball gets painted."""
import sys, math, os
import numpy as np
from sat import *

L = 780; HALF = L / 2; BR = 11
SEED = int(os.environ.get('SEED', '4'))
END_FRAC = .002


def area(P):
    x, y = P[:, 0], P[:, 1]; return .5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def exit_point(P, p, d):
    best = None
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]; e = b - a
        M = np.array([[d[0], -e[0]], [d[1], -e[1]]])
        if abs(np.linalg.det(M)) < 1e-12: continue
        s, u = np.linalg.solve(M, a - p)
        if s > 1e-7 and -1e-9 <= u <= 1 + 1e-9 and (best is None or s < best[0]): best = (s, i)
    return best


def split(P, a, b):
    """cut convex polygon P by line a->b; return (left, right) polygons"""
    n = np.array([-(b - a)[1], (b - a)[0]]); side = (P - a) @ n
    L_, R_ = [], []
    for i in range(len(P)):
        p, q = P[i], P[(i + 1) % len(P)]; sp, sq = side[i], side[(i + 1) % len(P)]
        if sp >= -1e-9: L_.append(p)
        if sp <= 1e-9: R_.append(p)
        if (sp > 1e-9 and sq < -1e-9) or (sp < -1e-9 and sq > 1e-9):
            x = p + (q - p) * (sp / (sp - sq)); L_.append(x); R_.append(x)
    return np.array(L_), np.array(R_), n


def simulate(seed, speed=820.0, maxN=200):
    rng = np.random.default_rng(seed)
    cell = np.array([[-HALF, -HALF], [HALF, -HALF], [HALF, HALF], [-HALF, HALF]], float)
    p = np.array([rng.uniform(-200, 200), HALF]); a = rng.uniform(-2.5, -.65); d = np.array([math.cos(a), math.sin(a)])
    t = 0.0; legs = []; painted = []; A0 = area(cell); n = 0
    while n < maxN:
        r_ = exit_point(cell, p, d)
        if r_ is None: break
        s, i = r_
        q = p + d * s; dt = s / speed
        legs.append((t, dt, p.copy(), q.copy(), area(cell) / A0))
        e = cell[(i + 1) % len(cell)] - cell[i]; nrm = np.array([-e[1], e[0]]) / np.linalg.norm(e)
        d2 = d - 2 * np.dot(d, nrm) * nrm
        Lp, Rp, cn = split(cell, p, q)
        keep, lose = (Lp, Rp) if np.dot(d2, cn) > 0 else (Rp, Lp)
        t += dt; n += 1
        if len(lose) >= 3 and area(lose) > 1: painted.append((t, lose, n))
        cell = keep; p = q
        th = 0.0; dr = np.array([d2[0] * math.cos(th) - d2[1] * math.sin(th), d2[0] * math.sin(th) + d2[1] * math.cos(th)])
        d = dr if np.dot(dr, nrm) * np.dot(d2, nrm) > 0 and abs(np.dot(dr, nrm)) > .15 and exit_point(cell, p, dr) else d2
        if area(cell) / A0 < END_FRAC: break
        pass
    return legs, painted, t, n, area(cell) / A0, cell


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'scan':
    for s in range(300):
        legs, painted, T, n, fr, _ = simulate(s)
        if fr < END_FRAC and 14 < T < 22 and 22 <= n <= 60: print(s, round(T, 1), n)
    sys.exit()

LEGS, PAINTED, T_END, NB, FRAC, LAST = simulate(SEED)
LT = np.array([l[0] for l in LEGS])
TL = Timeline(T_END, speed=lambda s: 1.0, slow=1.0, hold=2.4)


def ball_at(s):
    i = max(0, min(len(LEGS) - 1, int(np.searchsorted(LT, s, 'right')) - 1)); t0, dt, a, b, _ = LEGS[i]
    u = min(1, max(0, (s - t0) / dt)); return a + (b - a) * u, i


def cell_area_old(s):
    A = L * L - sum(area(P) for (pt, P, k) in PAINTED if pt <= s); return max(0, A / (L * L))


def draw_core(ctx, t):
    s = min(TL.s(t), T_END); pos, i = ball_at(s)
    background(ctx, t)
    done = TL.s(t) >= T_END; u = t - TL.t_end_video
    if done and u > 0: banner(ctx, "TRAPPED!", f"in {FRAC * 100:.2f}% of the box", u)
    else: header(ctx, [("Its path ", (1, 1, 1)), ("becomes a WALL", YEL)], "How fast is it trapped?", "Every bounce cuts the space in two")
    ctx.save(); ctx.translate(CX, CY)
    ctx.rectangle(-HALF, -HALF, L, L); ctx.set_source_rgba(0, 0, 0, .25); ctx.fill()
    for (pt, P, k) in PAINTED:
        if pt > s: break
        uu = s - pt; col = hue(.55 + k * .137, .6, .95)
        ctx.new_path(); ctx.move_to(*P[0])
        for q in P[1:]: ctx.line_to(*q)
        ctx.close_path(); ctx.set_source_rgba(*col, .85); ctx.fill_preserve()
        if uu < .3: ctx.set_source_rgba(1, 1, 1, .6 * (1 - uu / .3)); ctx.fill_preserve()
        ctx.set_source_rgba(.05, .05, .12, 1); ctx.set_line_width(4); ctx.stroke()
    # finished walls + current trail
    for j in range(i):
        _, _, a, b, _ = LEGS[j]; ctx.move_to(*a); ctx.line_to(*b)
    ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(4); ctx.stroke()
    a = LEGS[i][2]; ctx.move_to(*a); ctx.line_to(*pos); ctx.set_source_rgba(1, .85, .3, .9); ctx.set_line_width(5); ctx.stroke()
    ctx.set_line_width(8); ctx.set_source_rgb(.85, .9, 1); ctx.rectangle(-HALF - 4, -HALF - 4, L + 8, L + 8); ctx.stroke()
    glow(ctx, pos[0], pos[1], 46, (1, .9, .5), .55)
    ctx.new_path(); ball(ctx, pos[0], pos[1], BR, (1, .9, .55), spec=.7)
    if done and u > 0:
        k = max(0, 1 - u / 1.2); glow(ctx, pos[0], pos[1], 260 * (1 - k) + 40, (1, .85, .3), .7 * k)
    ctx.restore()
    if TL.rate(t) == 'slow' and not done: tag(ctx, "SLOW MOTION")
    j = max(0, int(np.searchsorted(LT, s, 'right')) - 1); fr = (LEGS[j][4] if s < T_END else FRAC) * 100
    counters(ctx, ("BOUNCES", f"{min(i, NB)}", (1, 1, 1)), ("SPACE LEFT", f"{fr:.1f}%" if fr >= 1 else f"{fr:.2f}%", (1, .45, .4) if fr < 3 else YEL))


def audio(path):
    tr = Track(TL.DUR)
    notes(tr, TL, [l[0] + l[1] for l in LEGS], amp=.12, min_gap=.05)
    for (pt, P, k) in PAINTED:
        if area(P) > 20000: tr.add(thud(.08), TL.v(pt))
    payoff(tr, TL.v(T_END))
    tr.save(path, TL.DUR)


if __name__ == '__main__':
    print('DUR', round(TL.DUR, 1), 'bounces', NB, 'T', round(T_END, 1), 'frac', FRAC)
    if len(sys.argv) > 1: run(draw_core, TL, audio, 'v5_trap', sys.argv)
