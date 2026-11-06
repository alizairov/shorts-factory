import sys, math
import numpy as np, cairo
from common import *

CX, CY = W / 2, H / 2
NR = 10
RAD = np.linspace(100, 500, NR)
RW = 12
GAP = math.radians(30)
SPD = np.array([(0.9 + 0.12 * i) * (1 if i % 2 == 0 else -1) for i in range(NR)])  # rad/s
BR = 16
V = 820.0
SUB = 6
MAXB = 60


def simulate(seed):
    rng = np.random.default_rng(seed)
    a0 = rng.uniform(0, 2 * math.pi)
    balls = [dict(p=np.zeros(2), v=V * np.array([math.cos(a0), math.sin(a0)]), born=0, ci=0)]
    broken = [None] * NR   # time broken
    gap0 = rng.uniform(0, 2 * math.pi, NR)
    events = []  # (t, kind, data)
    frames = []
    dt = 1 / FPS / SUB
    t = 0.0
    end = None
    while True:
        for _ in range(SUB):
            t += dt
            newb = []
            for b in balls:
                b["p"] += b["v"] * dt
                d = math.hypot(*b["p"])
                # innermost unbroken ring outside the ball
                j = next((k for k in range(NR) if broken[k] is None and RAD[k] > d - BR), None)
                if j is None:
                    continue
                R = RAD[j]
                if d + BR >= R - RW / 2 and d < R:
                    a = math.atan2(b["p"][1], b["p"][0])
                    gc = gap0[j] + SPD[j] * t
                    da = (a - gc + math.pi) % (2 * math.pi) - math.pi
                    in_gap = abs(da) < GAP / 2 - BR / R
                    if not in_gap:
                        n = b["p"] / d
                        vn = b["v"] @ n
                        if vn > 0:
                            b["v"] -= 2 * vn * n
                            tang = np.array([-n[1], n[0]])
                            b["v"] += tang * rng.uniform(-120, 120)
                            b["v"] *= V / math.hypot(*b["v"])
                            events.append((t, "bounce", (j, b["p"].copy())))
                        b["p"] = n * (R - RW / 2 - BR - 0.1)
                elif d > R and d - BR > R - RW / 2:
                    pass
                if d - BR > R + RW / 2 and broken[j] is None:
                    pass
                # passed through the gap
                if d > R and broken[j] is None:
                    broken[j] = t
                    events.append((t, "break", j))
                    if len(balls) + len(newb) < MAXB:
                        for s in (1,):
                            ang = math.atan2(b["v"][1], b["v"][0]) + s * 2.4 + rng.uniform(-.3, .3)
                            newb.append(dict(p=b["p"] * 0.3, v=V * np.array([math.cos(ang), math.sin(ang)]),
                                             born=t, ci=len(balls) + len(newb)))
            balls += newb
        frames.append(dict(t=t, balls=[(b["p"].copy(), b["ci"], b["born"]) for b in balls],
                           broken=list(broken), gap=[gap0[k] + SPD[k] * t for k in range(NR)]))
        if all(x is not None for x in broken) and end is None:
            end = t
        if end is not None and t > end + 2.5:
            break
        if t > 60:
            break
    return frames, events, end


rng2 = np.random.default_rng(5)
SHARDS = [[(rng2.uniform(0, 2 * math.pi), rng2.uniform(150, 650), rng2.uniform(4, 10), rng2.uniform(-1, 1))
           for _ in range(90)] for _ in range(NR)]


def ring_col(k):
    return grad(k / NR * 0.95)


def make_draw(frames, events):
    bounce_by_frame = {}
    for (t, kind, data) in events:
        if kind == "bounce":
            bounce_by_frame.setdefault(int(t * FPS), []).append(data)

    def draw(ctx, fi):
        fr = frames[min(fi, len(frames) - 1)]
        t = fr["t"]
        g = cairo.RadialGradient(CX, CY, 0, CX, CY, 1150)
        g.add_color_stop_rgb(0, 0.10, 0.04, 0.20)
        g.add_color_stop_rgb(1, 0.02, 0.01, 0.06)
        ctx.set_source(g)
        ctx.paint()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        # recent bounce glows on rings
        hits = {}
        for k in range(max(0, fi - 4), fi + 1):
            for (j, p) in bounce_by_frame.get(k, []):
                hits[j] = max(hits.get(j, 0), 1 - (fi - k) / 5)
        for k in range(NR):
            c = ring_col(k)
            bt = fr["broken"][k]
            if bt is None:
                fl = hits.get(k, 0)
                gc = fr["gap"][k]
                a0, a1 = gc + GAP / 2, gc - GAP / 2 + 2 * math.pi
                ctx.set_source_rgba(*c, 0.18 + 0.25 * fl)
                ctx.set_line_width(RW + 18 + 12 * fl)
                ctx.arc(CX, CY, RAD[k], a0, a1)
                ctx.stroke()
                ctx.set_source_rgb(*lighten(c, 0.35 * fl))
                ctx.set_line_width(RW)
                ctx.arc(CX, CY, RAD[k], a0, a1)
                ctx.stroke()
            else:
                age = t - bt
                if age < 1.6:
                    al = 1 - age / 1.6
                    # shockwave
                    ctx.set_source_rgba(*lighten(c, 0.4), al * 0.8)
                    ctx.set_line_width(6 * al + 1)
                    circle(ctx, CX, CY, RAD[k] + 260 * (age / 1.6) ** 0.6)
                    ctx.stroke()
                    for (a, sp, sz, rot) in SHARDS[k]:
                        dd = RAD[k] + sp * (1 - math.exp(-age * 3)) / 3
                        x = CX + math.cos(a) * dd
                        y = CY + math.sin(a) * dd + 250 * age * age
                        ctx.set_source_rgba(*c, al)
                        circle(ctx, x, y, sz * al + 1)
                        ctx.fill()
        # balls with trails
        for (p, ci, born) in fr["balls"]:
            c = grad(ci * 0.13 + 0.05)
            for back in range(6, 0, -1):
                j = fi - back
                if j < 0:
                    continue
                prev = next((q for (q, cj, _) in frames[j]["balls"] if cj == ci), None)
                if prev is None:
                    continue
                ctx.set_source_rgba(*c, 0.07 * (7 - back))
                circle(ctx, CX + prev[0], CY + prev[1], BR * (1 - back / 9))
                ctx.fill()
            sc = min(1, (t - born) / 0.15 + 0.2)
            glossy_ball(ctx, CX + p[0], CY + p[1], BR * sc, c)
    return draw


def audio(events, dur, path):
    tr = Track(dur)
    nb = 0
    for (t, kind, data) in events:
        if kind == "bounce":
            j = data[0]
            tr.add(pluck(note(NR - j + 3, 220), 0.25, 0.08, 14), t)
            nb += 1
        else:
            j = data
            for s in (0, 2, 4):
                tr.add(pluck(note(NR - j + 5 + s, 261.63), 1.0, 0.3, 4), t)
            n = len(np.arange(int(SR * 0.4)))
            tt = np.arange(n) / SR
            tr.add(np.random.default_rng(j).normal(0, 1, n) * np.exp(-tt * 14) * 0.18, t)
    tr.save(path, dur)


if __name__ == "__main__":
    if sys.argv[1] == "tune":
        for s in range(1, 25):
            f, e, end = simulate(s)
            print(s, end, len(f[-1]["balls"]))
        sys.exit()
    seed = int(sys.argv[2])
    frames, events, end = simulate(seed)
    draw = make_draw(frames, events)
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[3:]], "v1")
    else:
        dur = len(frames) / FPS
        audio(events, dur, "v1.wav")
        encode(draw, len(frames), "v1_video.mp4")
        mux("v1_video.mp4", "v1.wav", "reels_1_escape.mp4")
        print("dur", dur)
