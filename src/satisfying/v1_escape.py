"""V1: Every bounce shrinks the gap. Can the ball escape before it closes?"""
import sys, math, os
import numpy as np
from sat import *

R, BR = 410, 16
GAP0, SHRINK = 34.0, .92
SEED = int(os.environ.get('SEED', '7'))


def simulate(seed, maxT=40.0, dt=1 / 960):
    rng = np.random.default_rng(seed)
    a = rng.uniform(0, 2 * np.pi); sp = 760.0
    p = np.array([0.0, -120.0]); v = sp * np.array([math.cos(a), math.sin(a)])
    gap = GAP0; gc = -90.0; w = 22.0                               # gap centre (deg), rotation deg/s
    rec = []; ev = []; near = []; t = 0.0; esc = None; n = 0
    while t < maxT:
        gc_t = gc + w * t
        p = p + v * dt; d = np.linalg.norm(p)
        if esc is None and d + BR >= R:
            ang = math.degrees(math.atan2(p[1], p[0])); off = (ang - gc_t + 180) % 360 - 180
            if abs(off) < gap / 2 - math.degrees(BR / R) * .6:
                esc = t; ev.append((t, 'esc', gap))
            else:
                nrm = p / d; v = v - 2 * np.dot(v, nrm) * nrm; p = nrm * (R - BR - .01)
                n += 1; gap *= SHRINK; v *= 1.025
                v = np.dot(np.array([[math.cos(.004), -math.sin(.004)], [math.sin(.004), math.cos(.004)]]), v)
                ev.append((t, 'hit', gap))
                if abs(off) < gap / 2 + 9: near.append(t)
        rec.append((t, p[0], p[1], gc_t, gap, n))
        if esc is not None and t > esc + 1.6: break
        t += dt
    return rec, ev, near, esc, n


if __name__ == '__main__' and len(sys.argv) > 1 and sys.argv[1] == 'scan':
    for s in range(200):
        rec, ev, near, esc, n = simulate(s)
        if esc and 26 <= n <= 40 and 13 < esc < 24: print(s, 'bounces', n, 'esc', round(esc, 1), 'gap', round(ev[-1][2], 2), 'near', len(near))
    sys.exit()

REC, EV, NEAR, ESC, NB = simulate(SEED)
RT = np.array([r[0] for r in REC]); ARR = np.array([r[1:] for r in REC])
TL = Timeline(ESC, speed=lambda s: 1.0, slow=.8, hold=2.2)
HITS = [e for e in EV if e[1] == 'hit']


def state(s):
    i = min(len(RT) - 1, int(np.searchsorted(RT, s))); return ARR[i], i


def draw_core(ctx, t):
    s = TL.s(t); (x, y, gc, gap, n), i = state(s)
    background(ctx, t)
    done = s >= ESC + .05; u = t - TL.t_end_video
    if done and u > 0: banner(ctx, "ESCAPED!", f"through a {ev_gap:.1f}° gap", u)
    else: header(ctx, "Can the ball escape", "before the gap closes?", "Every bounce shrinks the gap by 8%")
    # wall
    hot = 1 - gap / GAP0
    col = (1, 1 - .55 * hot, 1 - .75 * hot)
    a0 = math.radians(gc + gap / 2); a1 = math.radians(gc - gap / 2 + 360)
    ctx.set_line_width(10); ctx.set_source_rgb(*col); ctx.new_path(); ctx.arc(CX, CY, R + 5, a0, a1); ctx.stroke()
    for aa in (a0, a1):
        ex, ey = CX + (R + 5) * math.cos(aa), CY + (R + 5) * math.sin(aa)
        glow(ctx, ex, ey, 40, col, .6); ctx.new_path(); ctx.arc(ex, ey, 9, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    # hit flashes on wall
    for (ht, _, g) in HITS:
        if 0 <= s - ht < .35:
            j = int(np.searchsorted(RT, ht)); hx, hy = ARR[j][0], ARR[j][1]; k = 1 - (s - ht) / .35
            glow(ctx, CX + hx * R / (R - BR), CY + hy * R / (R - BR), 70, (.5, .9, 1), .7 * k)
    # trail
    j0 = max(0, i - 260)
    for j in range(j0, i, 4):
        k = (j - j0) / max(1, i - j0)
        ctx.new_path(); ctx.arc(CX + ARR[j][0], CY + ARR[j][1], BR * .7 * k, 0, 7); ctx.set_source_rgba(.45, .85, 1, .35 * k); ctx.fill()
    glow(ctx, CX + x, CY + y, 60, (.5, .9, 1), .5)
    ctx.new_path(); ball(ctx, CX + x, CY + y, BR, (.55, .9, 1), spec=.7)
    if any(0 <= s - nt < .7 for nt in NEAR) and not done: tag(ctx, "SO CLOSE!", 1384, 1.0, YEL)
    elif TL.rate(t) == "slow" and not done: tag(ctx, "SLOW MOTION")
    gcol = (1, .45, .4) if gap < 6 else YEL
    counters(ctx, ("BOUNCES", f"{int(n)}", (1, 1, 1)), ("GAP", f"{gap:.1f}°", gcol))


ev_gap = [e for e in EV if e[1] == 'esc'][0][2]


def audio(path):
    tr = Track(TL.DUR)
    notes(tr, TL, [h[0] for h in HITS], amp=.13)
    for nt in NEAR: tr.add(marimba(1568, .05, .4), TL.v(nt) + .05)
    payoff(tr, TL.v(ESC))
    tr.save(path, TL.DUR)


if __name__ == '__main__':
    print('DUR', round(TL.DUR, 1), 'bounces', NB, 'esc', round(ESC, 2), 'gap', round(ev_gap, 2))
    if len(sys.argv) > 1: run(draw_core, TL, audio, 'v1_escape', sys.argv)
