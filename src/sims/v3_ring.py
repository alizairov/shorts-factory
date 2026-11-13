"""Visual Brain: every bounce paints the ring red. Can it fill 100% before 20 s run out?"""
import sys, math
from simkit import *
R, BR, G = 400.0, 22.0, 1400.0
X0, VX, W, UP, TLIM = 84.87789403712063, 68.22398237138918, 6, .03, 20.0
CX, CY = 540, 1000
def sim(dt=1/900):
    painted = np.zeros(360, bool); x, y, vx, vy = X0, -150.0, VX, 0.0; t = 0.0; P = []; H = []; full = None
    while True:
        vy += G * dt; x += vx * dt; y += vy * dt; t += dt
        d = math.hypot(x, y)
        if d > R - BR:
            nx, ny = x / d, y / d; vn = vx * nx + vy * ny
            if vn > 0:
                vx -= 2 * vn * nx; vy -= 2 * vn * ny; s = math.hypot(vx, vy)
                k = min(1 + UP, 3400 / s) if s * (1 + UP) > 3400 else 1 + UP; vx *= k; vy *= k
                a = int(round(math.degrees(math.atan2(ny, nx)))) % 360
                idx = [(a + j) % 360 for j in range(-W, W + 1)]; new = [i for i in idx if not painted[i]]
                painted[idx] = True; H.append((t, a, new, int(painted.sum()), s))
                if painted.all(): full = t
            x, y = nx * (R - BR), ny * (R - BR)
        P.append((t, x, y))
        if full is not None: break
    return np.array(P), H, full
PTS, HITS, T_FULL = sim()
T0 = 1.3; SLOW_AT = T_FULL - .9; SLOW = .35
def simt(vt):
    s = vt - T0
    if s <= 0: return 0.0
    if s < SLOW_AT: return s
    s2 = SLOW_AT + (s - SLOW_AT) * SLOW
    return min(s2, T_FULL + (s - SLOW_AT - (T_FULL - SLOW_AT) / SLOW) if s2 >= T_FULL else s2)
T_FULL_V = T0 + SLOW_AT + (T_FULL - SLOW_AT) / SLOW
DUR = T_FULL_V + 3.6
def state(st):
    i = min(len(PTS) - 1, int(st * 900)); return PTS[i]
def painted_at(st):
    p = np.zeros(360, bool); last = {}
    for (t, a, new, tot, s) in HITS:
        if t > st: break
        for i in new: p[i] = True; last[i] = t
    return p, last

def draw(ctx, t):
    backdrop(ctx); st = simt(t); p, last = painted_at(st); n = int(p.sum()); pct = n / 360 * 100
    done = t >= T_FULL_V; left = max(0.0, TLIM - st)
    # ring base
    ctx.new_path(); ctx.arc(CX, CY, R + 14, 0, 2 * math.pi); ctx.set_source_rgba(1, 1, 1, .1); ctx.set_line_width(26); ctx.stroke()
    # painted runs
    for i in range(360):
        if not p[i]: continue
        a0, a1 = math.radians(i - .5), math.radians(i + .5 + .3)
        age = st - last[i]; fl = cl(1 - age / .5)
        col = (1, .32 + .5 * fl, .25 + .6 * fl) if not done else (1, .3 + .4 * cl(1 - (t - T_FULL_V) / 1.2), .3)
        ctx.new_path(); ctx.arc(CX, CY, R + 14, a0, a1); ctx.set_source_rgb(*col); ctx.set_line_width(26 + 10 * fl); ctx.stroke()
    if not done and pct > 93:                                         # highlight remaining gaps
        pu = .5 + .5 * math.sin(t * 14)
        for i in range(360):
            if not p[i]:
                a = math.radians(i); x, y = CX + (R + 14) * math.cos(a), CY + (R + 14) * math.sin(a)
                glow(ctx, x, y, 70, (1, 1, 1), .8 * pu); ctx.new_path(); ctx.arc(x, y, 8, 0, 7); ctx.set_source_rgba(1, 1, 1, pu); ctx.fill()
    glow(ctx, CX, CY, 520, (1, .3, .25), .25 * pct / 100 + (.4 * cl(1 - (t - T_FULL_V) / 1.5) if done else 0))
    # ball + trail
    i = min(len(PTS) - 1, int(st * 900))
    tr = PTS[max(0, i - 90):i + 1:6]
    for k in range(1, len(tr)):
        a = k / len(tr); ctx.move_to(CX + tr[k - 1][1], CY + tr[k - 1][2]); ctx.line_to(CX + tr[k][1], CY + tr[k][2])
        ctx.set_source_rgba(1, .8, .6, .5 * a); ctx.set_line_width(BR * 1.4 * a); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.stroke()
    bx, by = CX + PTS[i][1], CY + PTS[i][2]
    glow(ctx, bx, by, 80, (1, .6, .4), .7); ctx.new_path(); ball(ctx, bx, by, BR, (1, .93, .85), spec=.8)
    # hit flash
    for (ht, a, new, tot, s) in HITS:
        if 0 <= st - ht < .25:
            u = (st - ht) / .25; ar = math.radians(a)
            ctx.new_path(); ctx.arc(CX + (R + 14) * math.cos(ar), CY + (R + 14) * math.sin(ar), 20 + 60 * u, 0, 7); ctx.set_source_rgba(1, .7, .5, .8 * (1 - u)); ctx.set_line_width(4); ctx.stroke()
    # timer in centre
    tc = PINK if left < 3 and not done else (1, 1, 1)
    if done: tc = GRN
    pulse = 1 + (.06 * math.sin(t * 20) if (left < 3 and not done) else 0)
    ctx.save(); ctx.translate(CX, CY); ctx.scale(pulse, pulse)
    label(ctx, f"{left:0.1f}s" if not done else f"{TLIM - T_FULL:0.2f}s", 0, -10, 120, col=tc, shadow=.5)
    label(ctx, "LEFT" if not done else "TO SPARE", 0, 75, 34, col=(.62, .66, .8), shadow=0)
    ctx.restore()
    if T0 + SLOW_AT - .05 < t < T_FULL_V + .2: speed_tag(ctx, .35, y=1475)
    if not done and pct > 93: tagbox(ctx, f"{360 - n}° LEFT", 540, 520, 56, (1, 1, 1), fg=INK, pointer=False)
    if done: tagbox(ctx, "100% RED!", 540, 520, 84, GRN, fg=INK, pointer=False, k=popk((t - T_FULL_V) / .4))
    header(ctx, t, [(0, "Every bounce paints the ring", "Can it reach 100% in 20 s?", GOLD), (T_FULL_V, "It made it", f"with {TLIM - T_FULL:0.2f} s to spare", GRN)])
    nb = sum(1 for h in HITS if h[0] <= st)
    stats(ctx, [("BOUNCES", f"{nb}", (1, 1, 1)), ("RED", f"{pct:0.1f}%" if pct < 100 else "100%", (1, .45, .35) if pct < 100 else GRN)])

def audio(path):
    tr = Track(DUR); soft_bed(tr, DUR, 40, .012); scale = [0, 2, 4, 7, 9]
    def vt_of(st):
        if st < SLOW_AT: return T0 + st
        return T0 + SLOW_AT + (st - SLOW_AT) / SLOW
    last = -1
    for (t, a, new, tot, s) in HITS:
        vt = vt_of(t)
        if vt - last < .06: continue
        last = vt; k = int(tot / 360 * 14); m = 60 + 12 * (k // 5) + scale[k % 5]
        tr.add(marimba(mtof(m), .8, .1 if new else .04), vt)
        if new: tr.add(marimba(mtof(m + 12), .5, .03), vt + .02)
    for j in range(7):                                                   # clock ticks last seconds
        st = TLIM - 3 + j * .5
        if st < T_FULL: tr.add(marimba(1800, .08, .05), vt_of(st))
    for j, m in enumerate((60, 64, 67, 72, 76, 79)): tr.add(piano(mtof(m), 3, .08), T_FULL_V + j * .07)
    tr.add(piano(mtof(36), 3, .2), T_FULL_V)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('T_FULL', round(T_FULL, 2), 'hits', len(HITS), 'DUR', round(DUR, 1), 'T_FULL_V', round(T_FULL_V, 1))
    if len(sys.argv) > 1: main(draw, DUR, audio, 'v3_ring', sys.argv, strength=.9, thr=.6)
