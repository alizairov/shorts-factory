import sys, math
import numpy as np, cairo
from common import *

BR = 10.5
PR = 8
G = 2000.0
SUB = 5
NB = 15
BW = W / NB
BIN_TOP = 1290
FLOOR = 1830
ROWS = 15
PEGS = []
for r in range(ROWS):
    y = 330 + r * 62
    off = 0 if r % 2 == 0 else BW / 2
    x = off + BW / 2 if r % 2 == 0 else off
    xs = np.arange(BW / 2 if r % 2 == 0 else BW, W - 10, BW)
    for x in xs:
        PEGS.append((x, y))
PEGS = np.array(PEGS)
NBALL = 380
SPAWN_EVERY = 1  # frames


def simulate(seed=2):
    rng = np.random.default_rng(seed)
    n = NBALL
    p = np.zeros((n, 2)); v = np.zeros((n, 2))
    state = np.zeros(n, int)  # 0 waiting, 1 falling, 2 in bin, 3 settled
    binof = -np.ones(n, int)
    target = np.zeros(n)
    count = np.zeros(NB, int)
    settle_t = np.full(n, np.nan)
    peg_hit = []
    frames = []
    dt = 1 / FPS / SUB
    fi = 0
    t = 0.0
    while True:
        k = fi // SPAWN_EVERY
        if fi % SPAWN_EVERY == 0 and k < n:
            state[k] = 1
            p[k] = (W / 2 + rng.uniform(-6, 6), 170)
            v[k] = (rng.uniform(-30, 30), 0)
        for _ in range(SUB):
            t += dt
            act = np.where((state == 1) | (state == 2))[0]
            if len(act) == 0:
                continue
            v[act, 1] += G * dt
            p[act] += v[act] * dt
            fall = act[state[act] == 1]
            if len(fall):
                d = p[fall, None, :] - PEGS[None, :, :]
                dist = np.hypot(d[..., 0], d[..., 1])
                hit = dist < BR + PR
                for bi, pi in zip(*np.nonzero(hit)):
                    b = fall[bi]
                    nrm = d[bi, pi] / dist[bi, pi]
                    p[b] = PEGS[pi] + nrm * (BR + PR + 0.1)
                    vn = v[b] @ nrm
                    if vn < 0:
                        sx = np.sign(nrm[0]) if abs(nrm[0]) > 0.15 else rng.choice([-1, 1])
                        if rng.random() < 0.18:
                            sx = -sx
                        v[b] = (sx * rng.uniform(95, 140), -rng.uniform(40, 140))
                        peg_hit.append((t, pi))
                # walls
                lo = p[fall, 0] < BR; hi = p[fall, 0] > W - BR
                p[fall[lo], 0] = BR; v[fall[lo], 0] *= -0.5
                p[fall[hi], 0] = W - BR; v[fall[hi], 0] *= -0.5
                enter = fall[p[fall, 1] > BIN_TOP]
                for b in enter:
                    bn = int(np.clip(p[b, 0] // BW, 0, NB - 1))
                    binof[b] = bn
                    c = count[bn]; count[bn] += 1
                    col, row = c % 3, c // 3
                    target[b] = FLOOR - BR - row * (2 * BR + 0.5)
                    state[b] = 2
                    v[b, 0] = 0
                    p[b, 0] = bn * BW + BW / 2 + (col - 1) * (2 * BR + 1)
            inb = act[state[act] == 2]
            done = inb[p[inb, 1] >= target[inb]]
            p[done, 1] = target[done]
            state[done] = 3
            settle_t[done] = t
        frames.append(dict(t=t, p=p.copy(), state=state.copy()))
        fi += 1
        if (state == 3).sum() == n:
            break
    return frames, binof, settle_t, peg_hit, count


def make_draw(frames, binof, peg_hit):
    hit_frames = np.zeros((len(frames) + 2, len(PEGS)))
    for (t, pi) in peg_hit:
        hit_frames[min(int(t * FPS), len(frames)), pi] = 1
    bg_top, bg_bot = (0.95, 0.92, 1.0), (0.86, 0.80, 1.0)
    cols = [grad(b / NB * 0.98 + 0.0) for b in range(NB)]

    def draw(ctx, fi):
        fr = frames[min(fi, len(frames) - 1)]
        g = cairo.LinearGradient(0, 0, 0, H)
        g.add_color_stop_rgb(0, *bg_top); g.add_color_stop_rgb(1, *bg_bot)
        ctx.set_source(g); ctx.paint()
        # bins
        for b in range(NB):
            x = b * BW
            ctx.set_source_rgba(*cols[b], 0.16)
            ctx.rectangle(x + 3, BIN_TOP, BW - 6, FLOOR - BIN_TOP + 4)
            ctx.fill()
        ctx.set_source_rgb(0.20, 0.10, 0.38)
        ctx.set_line_width(5)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for b in range(NB + 1):
            ctx.move_to(b * BW, BIN_TOP + 10); ctx.line_to(b * BW, FLOOR + 6); ctx.stroke()
        ctx.move_to(0, FLOOR + 6); ctx.line_to(W, FLOOR + 6); ctx.stroke()
        # funnel
        ctx.set_line_width(8)
        ctx.move_to(W / 2 - 120, 90); ctx.line_to(W / 2 - 26, 175); ctx.stroke()
        ctx.move_to(W / 2 + 120, 90); ctx.line_to(W / 2 + 26, 175); ctx.stroke()
        # pegs with hit glow
        glow = np.zeros(len(PEGS))
        for k in range(5):
            j = fi - k
            if 0 <= j < len(hit_frames):
                glow = np.maximum(glow, hit_frames[j] * (1 - k / 5))
        for i, (x, y) in enumerate(PEGS):
            gl = glow[i]
            if gl > 0:
                c = grad(x / W)
                ctx.set_source_rgba(*c, 0.55 * gl)
                circle(ctx, x, y, PR + 10 * gl); ctx.fill()
            ctx.set_source_rgb(*((0.20, 0.10, 0.38) if gl == 0 else lighten(grad(x / W), 0.2)))
            circle(ctx, x, y, PR); ctx.fill()
        # balls
        for b in np.where(fr["state"] > 0)[0]:
            x, y = fr["p"][b]
            c = cols[binof[b]]
            ctx.set_source_rgba(0.2, 0.1, 0.38, 0.25)
            circle(ctx, x + 1.5, y + 2.5, BR); ctx.fill()
            glossy_ball(ctx, x, y, BR, c, glow=False)
    return draw


def audio(settle_t, binof, peg_hit, dur, path):
    tr = Track(dur)
    for t, b in zip(settle_t, binof):
        tr.add(pluck(note(NB - 1 - abs(b - NB // 2) * 2 + 2, 261.63), 0.35, 0.05, 12), t)
    rng = np.random.default_rng(0)
    tick = lambda: np.sin(2 * np.pi * 2600 * np.arange(300) / SR) * np.exp(-np.arange(300) / 40) * 0.02
    for (t, pi) in peg_hit[::3]:
        tr.add(tick(), t)
    tr.save(path, dur)


if __name__ == "__main__":
    frames, binof, settle_t, peg_hit, count = simulate()
    print("frames", len(frames), "counts", list(count))
    HOLD = 45
    draw = make_draw(frames, binof, peg_hit)
    nf = len(frames) + HOLD
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "v2")
    else:
        dur = nf / FPS
        audio(settle_t, binof, peg_hit, dur, "v2.wav")
        encode(draw, nf, "v2_video.mp4")
        mux("v2_video.mp4", "v2.wav", "reels_3_plinko.mp4")
        print("dur", dur)
