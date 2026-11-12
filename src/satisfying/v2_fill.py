"""V2: Every wall hit = +1 ball. Can 1 ball fill the circle?"""
import sys, math
import numpy as np, pymunk
from sat import *

R, BR = 420, 13
TARGET = int(.80 * (R / BR) ** 2 // 10 * 10)          # 80 % packing of the circle


def simulate(maxT=60, dt=1 / 240):
    sp = pymunk.Space(); sp.gravity = (0, 0)
    N = 160
    for k in range(N):
        a0, a1 = 2 * math.pi * k / N, 2 * math.pi * (k + 1) / N
        s = pymunk.Segment(sp.static_body, ((R + 14) * math.cos(a0), (R + 14) * math.sin(a0)), ((R + 14) * math.cos(a1), (R + 14) * math.sin(a1)), 14)
        s.elasticity = 1.0; s.friction = 0; s.collision_type = 2; sp.add(s)
    rng = np.random.default_rng(5); balls = []; pending = []; hits = []; cool = {}; tnow = [0.0]
    def add(x, y, vx, vy):
        b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, BR)); b.position = (x, y); b.velocity = (vx, vy)
        c = pymunk.Circle(b, BR); c.elasticity = .98; c.friction = 0; c.collision_type = 1; sp.add(b, c); balls.append(b)
    def on_hit(arb, space, data):
        b = arb.shapes[0].body
        if len(balls) + len(pending) < TARGET and tnow[0] - cool.get(id(b), -9) > 1.6:
            cool[id(b)] = tnow[0]
            p = arb.contact_point_set.points[0].point_a; d = math.hypot(p.x, p.y) or 1
            pending.append((p.x * (R - 40) / d, p.y * (R - 40) / d))
        return True
    sp.on_collision(1, 2, begin=on_hit)
    add(0, -150, 300, 420)
    rec = []; t = 0.0; t_full = None
    while t < maxT:
        for (x, y) in pending:
            a = rng.uniform(0, 2 * math.pi); add(x, y, 500 * math.cos(a) - x * .3, 500 * math.sin(a) - y * .3); hits.append(t)
        pending.clear()
        tnow[0] = t; sp.step(dt)
        for b in balls:                                   # keep energy up, cap speed
            vx, vy = b.velocity; s = math.hypot(vx, vy)
            if s > 560: b.velocity = (vx * 560 / s, vy * 560 / s)
            elif s < 250 and t_full is None: b.velocity = (vx * 1.02 + 1, vy * 1.02)
        t += dt
        rec.append(np.array([b.position for b in balls], np.float32))
        if t_full is None and len(balls) >= TARGET: t_full = t
        if t_full and t > t_full + 1.6: break
    return rec, hits, t_full


REC, HITS, T_FULL = simulate()
DT = 1 / 240
TL = Timeline(T_FULL, speed=lambda s: 1.0 if s < 5 else min(2.5, 1 + (s - 5) * .2), slow=.9, hold=2.2)


def draw_core(ctx, t):
    s = TL.s(t); i = min(len(REC) - 1, int(s / DT)); P = REC[i]; n = len(P)
    background(ctx, t)
    done = s >= T_FULL; u = t - TL.t_end_video
    if done and u > 0: banner(ctx, "FULL!", f"1 ball became {TARGET:,} in {T_FULL:.0f} s", u)
    else: header(ctx, [("Every wall hit = ", (1, 1, 1)), ("+1 ball", YEL)], "Can they fill the circle?", f"Target: {TARGET:,} balls")
    ctx.set_line_width(8); ctx.set_source_rgb(.85, .9, 1); ctx.new_path(); ctx.arc(CX, CY, R + 4, 0, 7); ctx.stroke()
    for (ht) in HITS[-400:]:
        if 0 <= s - ht < .25: pass
    for k, (x, y) in enumerate(P):
        col = hue(.55 + k / TARGET * .9, .65)
        ctx.new_path(); ctx.arc(CX + x, CY + y, BR - .5, 0, 7); ctx.set_source_rgb(*col); ctx.fill()
        if n < 300: ctx.new_path(); ctx.arc(CX + x - 4, CY + y - 4, 3.5, 0, 7); ctx.set_source_rgba(1, 1, 1, .6); ctx.fill()
    if done and u > 0:
        glow(ctx, CX, CY, R * 1.2, YEL, .25 * max(0, 1 - u / 1.5))
    r = TL.rate(t)
    if r == 'slow' and not done: tag(ctx, "SLOW MOTION")
    elif r != 'slow' and r > 1.05 and not done: tag(ctx, f"SPEED x{r:.1f}")
    pct = min(100, n / TARGET * 100)
    counters(ctx, ("BALLS", f"{n:,}", (1, 1, 1)), ("FILLED", f"{pct:.0f}%", (.5, 1, .55) if pct >= 100 else YEL))


def audio(path):
    tr = Track(TL.DUR)
    notes(tr, TL, HITS, amp=.11, min_gap=.06)
    payoff(tr, TL.v(T_FULL))
    tr.save(path, TL.DUR)


if __name__ == '__main__':
    print('DUR', round(TL.DUR, 1), 'target', TARGET, 'full at', round(T_FULL, 1))
    if len(sys.argv) > 1: run(draw_core, TL, audio, 'v2_fill', sys.argv)
