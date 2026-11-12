"""V4: Can 1 ball break all 10 rings in 30 seconds?"""
import sys, math, os
import numpy as np
from sat import *

NR, BR, TLIM = 10, 12, 30.0
RAD = [95 + 37 * k for k in range(NR)]
GAP = math.radians(46)
SEED = int(os.environ.get('SEED', '3'))


def ring_w(k, seed):
    rng = np.random.default_rng(seed * 100 + k); return (1 if k % 2 == 0 else -1) * rng.uniform(.7, 1.5)


def ring_a(k, t, seed):
    rng = np.random.default_rng(seed * 100 + k + 50); return rng.uniform(0, 2 * math.pi) + ring_w(k, seed) * t


def simulate(seed, dt=1 / 600, maxT=34.0):
    rng = np.random.default_rng(seed)
    p = np.array([0.0, -20.0]); v = np.array([rng.uniform(-300, 300), 0.0]); g = np.array([0.0, 1500.0])
    k = 0; t = 0.0; rec = []; hits = []; breaks = []; passing = False; t_done = None
    while t < maxT:
        v = v + g * dt; p = p + v * dt; d = np.linalg.norm(p)
        if k < NR:
            Rk = RAD[k]
            if d + BR >= Rk and not passing:
                ang = math.atan2(p[1], p[0]); off = (ang - ring_a(k, t, seed) + math.pi) % (2 * math.pi) - math.pi
                if abs(off) < GAP / 2 - BR / Rk and np.dot(v, p) > 0: passing = True
                else:
                    n = p / d; v = v - 2 * np.dot(v, n) * n; p = n * (Rk - BR - .01)
                    sp = np.linalg.norm(v)
                    if sp < 950: v *= 950 / sp
                    v = v + rng.normal(0, 25, 2); hits.append((t, k))
            if passing and d - BR > Rk:
                breaks.append((t, k)); k += 1; passing = False
                if k == NR: t_done = t
        rec.append((t, p[0], p[1], k))
        if t_done is not None and t > t_done + 1.5: break
        t += dt
    return np.array(rec), hits, breaks, t_done


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'scan':
    for s in range(120):
        rec, hits, br, td = simulate(s, dt=1 / 600)
        if td and 22 < td < 29.3: print(s, round(td, 1), [round(b[0], 1) for b in br])
    sys.exit()

REC, HITS, BREAKS, T_DONE = simulate(SEED)
TL = Timeline(T_DONE, speed=lambda s: 1.0, slow=.8, hold=2.2)


def draw_core(ctx, t):
    s = TL.s(t); i = min(len(REC) - 1, int(np.searchsorted(REC[:, 0], s)))
    _, x, y, k = REC[i]; k = int(k)
    background(ctx, t)
    done = s >= T_DONE; u = t - TL.t_end_video
    if done and u > 0: banner(ctx, "ALL 10 BROKEN!", f"with {TLIM - T_DONE:.1f} s to spare", u)
    else: header(ctx, "Can 1 ball break", [("all 10 rings in ", YEL), ("30 s?", YEL)], "It can only escape through the gaps")
    for j in range(NR):
        col = hue(.55 + j * .085, .65)
        bt = next((b for b in BREAKS if b[1] == j), None)
        if bt and s >= bt[0]:
            uu = s - bt[0]
            if uu < 1.0:                                          # shatter
                r = np.random.default_rng(j)
                for q in range(26):
                    a = r.uniform(0, 2 * math.pi); sp = r.uniform(120, 420)
                    px = CX + math.cos(a) * (RAD[j] + sp * uu); py = CY + math.sin(a) * (RAD[j] + sp * uu) + 700 * uu * uu
                    ctx.save(); ctx.translate(px, py); ctx.rotate(a + uu * 6); ctx.rectangle(-9, -3, 18, 6); ctx.set_source_rgba(*col, 1 - uu); ctx.fill(); ctx.restore()
                if uu < .2: glow(ctx, CX, CY, RAD[j] + 60, col, .35 * (1 - uu / .2))
            continue
        a = ring_a(j, s, SEED)
        ctx.new_path(); ctx.arc(CX, CY, RAD[j], a + GAP / 2, a - GAP / 2 + 2 * math.pi)
        ctx.set_line_width(11); ctx.set_source_rgb(*col); ctx.stroke()
        if j == k:
            for (ht, hk) in HITS:
                if hk == j and 0 <= s - ht < .2: ctx.new_path(); ctx.arc(CX, CY, RAD[j], a + GAP / 2, a - GAP / 2 + 2 * math.pi); ctx.set_line_width(22); ctx.set_source_rgba(1, 1, 1, .5 * (1 - (s - ht) / .2)); ctx.stroke()
    j0 = max(0, i - 220)
    for j in range(j0, i, 6):
        q = (j - j0) / max(1, i - j0); ctx.new_path(); ctx.arc(CX + REC[j, 1], CY + REC[j, 2], BR * q * .8, 0, 7); ctx.set_source_rgba(1, 1, 1, .3 * q); ctx.fill()
    glow(ctx, CX + x, CY + y, 50, (1, 1, 1), .5)
    ctx.new_path(); ball(ctx, CX + x, CY + y, BR, (1, .95, .8), spec=.7)
    if TL.rate(t) == 'slow' and not done: tag(ctx, "SLOW MOTION")
    left = max(0.0, TLIM - min(s, T_DONE))
    counters(ctx, ("TIME LEFT", f"{left:.1f}s", (1, .45, .4) if left < 5 else (1, 1, 1)), ("RINGS", f"{sum(1 for b in BREAKS if b[0] <= s)}/{NR}", YEL))


def audio(path):
    tr = Track(TL.DUR)
    notes(tr, TL, [(h[0], h[1] * 3 + n) for n, h in enumerate(HITS)], amp=.09, min_gap=.07)
    for n, (bt, j) in enumerate(BREAKS):
        vt = TL.v(bt); tr.add(thud(.18), vt); tr.add(shimmer(.03, 1.0), vt)
        for q, st in enumerate((0, 7, 12)): tr.add(marimba(261.63 * 2 ** ((j * 2 + st) / 12), .1, 1.2), vt + q * .05)
    payoff(tr, TL.v(T_DONE))
    tr.save(path, TL.DUR)


if __name__ == '__main__':
    print('DUR', round(TL.DUR, 1), 'done', round(T_DONE, 2), [round(b[0], 1) for b in BREAKS])
    if len(sys.argv) > 1: run(draw_core, TL, audio, 'v4_rings', sys.argv)
