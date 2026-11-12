"""V3: Each bounce makes the ball 5% bigger. When does it get stuck?"""
import sys, math
import numpy as np
from sat import *

L = 780; HALF = L / 2; R0, GROW = 22.0, 1.08


def simulate(dt=1 / 1200):
    x, y = -120.0, 60.0; vx, vy = 930.0, -720.0; r = R0
    rec = []; hits = []; stamps = []; t = 0.0; n = 0; t_stuck = None
    while True:
        x += vx * dt; y += vy * dt; hit = None
        if x + r > HALF: x = HALF - r; vx = -abs(vx); hit = (HALF, y)
        elif x - r < -HALF: x = -HALF + r; vx = abs(vx); hit = (-HALF, y)
        if y + r > HALF: y = HALF - r; vy = -abs(vy); hit = (x, HALF)
        elif y - r < -HALF: y = -HALF + r; vy = abs(vy); hit = (x, -HALF)
        if hit and t_stuck is None:
            n += 1; stamps.append((t, x, y, r)); r = min(HALF, r * GROW); hits.append((t, n, hit))
            x = max(-HALF + r, min(HALF - r, x)); y = max(-HALF + r, min(HALF - r, y))
            if r >= HALF - .5: t_stuck = t; r = HALF
        rec.append((t, x, y, r, n))
        if t_stuck is not None and t > t_stuck + 1.5: break
        t += dt
    return np.array(rec), hits, stamps, t_stuck, n


REC, HITS, STAMPS, T_STUCK, NB = simulate()
TL = Timeline(T_STUCK, speed=lambda s: 1.0, slow=1.0, hold=2.2)


def draw_core(ctx, t):
    s = TL.s(t); i = min(len(REC) - 1, int(np.searchsorted(REC[:, 0], s)))
    _, x, y, r, n = REC[i]; n = int(n)
    background(ctx, t)
    done = s >= T_STUCK; u = t - TL.t_end_video
    if done and u > 0: banner(ctx, "STUCK!", f"after {NB} bounces", u)
    else: header(ctx, [("Every bounce: ", (1, 1, 1)), ("8% BIGGER", YEL)], "When does it get STUCK?", "The box never changes size")
    x0, y0 = CX - HALF, CY - HALF
    # ghost rings: the size it had at every bounce
    for k, (st, sx, sy, sr) in enumerate(STAMPS):
        if st > s: break
        ctx.new_path(); ctx.arc(CX + sx, CY + sy, sr, 0, 7); ctx.set_source_rgba(*hue(k / 40), .22); ctx.set_line_width(2); ctx.stroke()
    # box, walls flash on hit
    ctx.set_line_width(9); ctx.set_source_rgb(.85, .9, 1); ctx.rectangle(x0 - 4, y0 - 4, L + 8, L + 8); ctx.stroke()
    for (ht, k, (hx, hy)) in HITS:
        if 0 <= s - ht < .3: glow(ctx, CX + hx, CY + hy, 90, hue(k / 40), .8 * (1 - (s - ht) / .3))
    col = hue(n / 40)
    glow(ctx, CX + x, CY + y, r * 1.6, col, .35)
    ctx.new_path(); ball(ctx, CX + x, CY + y, r, col, spec=.6)
    if r > 60: txt(ctx, f"×{r / R0:.1f}", CX + x, CY + y, min(120, r * .45), (1, 1, 1), .9)
    if done and u > 0:
        k = max(0, 1 - u / .6); ctx.set_source_rgba(1, 1, 1, .22 * k); ctx.paint()
    if TL.rate(t) == 'slow' and not done: tag(ctx, "SLOW MOTION")
    counters(ctx, ("BOUNCES", f"{n}", (1, 1, 1)), ("SIZE", f"×{r / R0:.1f}", YEL))


def audio(path):
    tr = Track(TL.DUR)
    # bigger ball -> lower note: pitch follows size
    notes(tr, TL, [(h[0], h[1]) for h in HITS], amp=.12, min_gap=.05, pitch=lambda st, k: note_freq(k, 523.25 * (R0 / (R0 * GROW ** k)) ** .25))
    payoff(tr, TL.v(T_STUCK), base=130.81)
    tr.save(path, TL.DUR)


if __name__ == '__main__':
    print('DUR', round(TL.DUR, 1), 'bounces', NB, 'stuck', round(T_STUCK, 1))
    if len(sys.argv) > 1: run(draw_core, TL, audio, 'v3_grow', sys.argv)
