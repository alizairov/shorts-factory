"""Visual Brain: Guess the melody (Für Elise, public domain). Every corner plays the next note."""
import sys, colorsys
from simkit import *
MEL = [(76,1),(75,1),(76,1),(75,1),(76,1),(71,1),(74,1),(72,1),(69,3),(60,1),(64,1),(69,1),(71,3),(64,1),(68,1),(71,1),(72,3),
       (64,1),(76,1),(75,1),(76,1),(75,1),(76,1),(71,1),(74,1),(72,1),(69,3),(60,1),(64,1),(69,1),(71,3),(64,1),(72,1),(71,1),(69,5)]
NAMES = 'C C# D D# E F F# G G# A A# B'.split()
STAGES = [3, 5, 9, 13, 22, 35]
UNIT = [.25, .23, .21, .19, .18, .18]
CX, CY, RAD = 540, 990, 390
T_INTRO, MORPH, GAP = 1.0, .55, .45

def poly(n):
    return [(CX + RAD * math.sin(2 * math.pi * i / n), CY - RAD * math.cos(2 * math.pi * i / n)) for i in range(n)]
def heart(n):
    ts = np.linspace(0, 2 * math.pi, 4000); x = 16 * np.sin(ts) ** 3; y = -(13 * np.cos(ts) - 5 * np.cos(2 * ts) - 2 * np.cos(3 * ts) - np.cos(4 * ts))
    d = np.r_[0, np.cumsum(np.hypot(np.diff(x), np.diff(y)))]; s = np.linspace(0, d[-1], n, endpoint=False)
    xs, ys = np.interp(s, d, x), np.interp(s, d, y)
    return [(CX + 25 * a, CY + 25 * b + 45) for a, b in zip(xs, ys)]
SHAPES = [poly(n) for n in STAGES[:-1]] + [heart(STAGES[-1])]

# timeline: per stage, note times
SCHED = []; t = T_INTRO
for k, n in enumerate(STAGES):
    if k: t += MORPH
    ts = []
    for i in range(n): ts.append(t); t += MEL[i][1] * UNIT[k]
    SCHED.append((ts[0], ts, t)); t += GAP
T_END = SCHED[-1][2]
DUR = T_END + 3.2
def stage_at(t):
    k = 0
    for i, (s, ts, e) in enumerate(SCHED):
        if t >= s - MORPH: k = i
    return k
def hue(m): return colorsys.hsv_to_rgb(((m % 12) / 12 * .8 + .55) % 1, .55, 1)

def shape_pts(k, t):
    s = SCHED[k][0]
    if k == 0 or t >= s: return SHAPES[k]
    u = ease(cl((t - (s - MORPH)) / MORPH)); A, B = SHAPES[k - 1], SHAPES[k]
    out = []
    for i in range(len(B)):
        j = i * len(A) / len(B); a0 = A[int(j) % len(A)]; a1 = A[(int(j) + 1) % len(A)]; f = j - int(j)
        ax, ay = lerp(a0[0], a1[0], f), lerp(a0[1], a1[1], f)
        out.append((lerp(ax, B[i][0], u), lerp(ay, B[i][1], u)))
    return out

def dot_pos(k, t, pts):
    s, ts, e = SCHED[k]; n = len(pts)
    if t < s: return pts[0], -1
    for i in range(n):
        t1 = ts[i + 1] if i + 1 < n else e
        if t < t1:
            u = (t - ts[i]) / (t1 - ts[i]); u = ease(u) * .3 + u * .7
            a, b = pts[i], pts[(i + 1) % n]
            return (lerp(a[0], b[0], u), lerp(a[1], b[1], u)), i
    return pts[0], n - 1

def draw(ctx, t):
    backdrop(ctx); k = stage_at(t); s, ts, e = SCHED[k]; pts = shape_pts(k, t); n = len(pts)
    final = k == len(STAGES) - 1 and t > e
    # outline
    ctx.set_line_join(cairo.LINE_JOIN_ROUND)
    ctx.move_to(*pts[0]); [ctx.line_to(*p) for p in pts[1:]]; ctx.close_path()
    ctx.set_source_rgba(1, 1, 1, .22); ctx.set_line_width(4); ctx.stroke()
    p, cur = dot_pos(k, t, pts)
    # lit edges
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for i in range(max(-1, cur) + 1):
        a, b = pts[i], (pts[(i + 1) % n] if i < cur else p)
        col = hue(MEL[i][0]); ctx.move_to(*a); ctx.line_to(*b); ctx.set_source_rgb(*col); ctx.set_line_width(8); ctx.stroke()
    if final:
        u = ease(cl((t - e) / .8))
        ctx.move_to(*pts[0]); [ctx.line_to(*q) for q in pts[1:]]; ctx.close_path()
        g = cairo.RadialGradient(CX, CY - 60, 30, CX, CY, 420); g.add_color_stop_rgba(0, 1, .55, .7, .85 * u); g.add_color_stop_rgba(1, .9, .2, .45, .55 * u)
        ctx.set_source(g); ctx.fill()
        glow(ctx, CX, CY, 520, (1, .4, .6), .35 * u)
    # corners
    for i, (x, y) in enumerate(pts):
        hit = i <= cur and t >= s
        th = ts[i] if i < len(ts) else 1e9; fl = cl(1 - (t - th) / .35) if t >= th else 0
        if fl > 0:
            ctx.new_path(); ctx.arc(x, y, 14 + 50 * (1 - fl), 0, 7); ctx.set_source_rgba(*hue(MEL[i][0]), .7 * fl); ctx.set_line_width(4); ctx.stroke()
            glow(ctx, x, y, 70, hue(MEL[i][0]), .7 * fl)
        ctx.new_path(); ctx.arc(x, y, 9 + 5 * fl, 0, 7); ctx.set_source_rgb(*(hue(MEL[i][0]) if hit else (.45, .45, .6))); ctx.fill()
        if n <= 22:
            dx, dy = x - CX, y - CY; d = math.hypot(dx, dy) or 1
            label(ctx, NAMES[MEL[i][0] % 12], x + dx / d * 44, y + dy / d * 44, 30 if n < 15 else 24, col=hue(MEL[i][0]) if hit else (.5, .52, .65), shadow=0)
    if not final and t >= s - .05:
        glow(ctx, p[0], p[1], 60, (1, 1, 1), .8); ctx.new_path(); ctx.arc(p[0], p[1], 13, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    # progress dots
    for j in range(len(STAGES)):
        x = 540 + (j - 2.5) * 54; done = j < k or (j == k and t > e)
        ctx.new_path(); ctx.arc(x, 520, 13 if j == k else 10, 0, 7)
        if done or j == k: ctx.set_source_rgb(*(GOLD if j == k else (.75, .78, .95))); ctx.fill()
        else: ctx.set_source_rgba(1, 1, 1, .35); ctx.set_line_width(3); ctx.stroke()
    label(ctx, "?", 540 + 3.4 * 54, 520, 34, col=(1, 1, 1), alpha=.6, shadow=0)
    header(ctx, t, [(0, "Guess the song", "before the last shape", GOLD), (T_END + .2, "Did you get it?", "Name it in the comments", PINK)])
    label(ctx, "every corner plays the next note", 540, 455, 30, col=(.62, .66, .8), alpha=1 if t < T_END else 0, shadow=0)
    notes = sum(1 for kk, (s2, ts2, e2) in enumerate(SCHED) for x in ts2 if x <= t)
    stats(ctx, [("NOTES", f"{notes}", GOLD), ("CORNERS", f"{n}", CYAN)])

def audio(path):
    tr = Track(DUR); soft_bed(tr, DUR, 45, .012)
    for k, (s, ts, e) in enumerate(SCHED):
        for i, tt in enumerate(ts):
            m = MEL[i][0]; tr.add(piano(mtof(m), 1.8, .16), tt)
            if i in (8, 12, 16, 26, 30) or (k == len(STAGES) - 1 and i == len(ts) - 1): tr.add(piano(mtof({69: 45, 71: 40, 72: 45}.get(m, 45)), 2.2, .07), tt)
        if k: tr.add(marimba(mtof(81 + k * 2), .6, .025), s - MORPH)
    for j, m in enumerate((57, 60, 64, 69, 72, 76)): tr.add(piano(mtof(m), 3.0, .07), T_END + .15 + j * .09)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('DUR', round(DUR, 1), 'stage starts', [round(s[0], 1) for s in SCHED])
    if len(sys.argv) > 1: main(draw, DUR, audio, 'v1_melody', sys.argv, strength=.9, thr=.6)
