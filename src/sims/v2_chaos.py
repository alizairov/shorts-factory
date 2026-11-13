"""Visual Brain: two balls 0.000001° apart. Circle: together forever. Stadium: chaos splits them."""
import sys
from simkit import *
CX, CY = 540, 1000
V = 900.0
DA = math.radians(1e-6)
P0, A0 = (-120.0, 70.0), 0.62
R_C, R_S, L_S = 360.0, 300.0, 180.0

def hit(p, d, L, R):
    best = None
    for sy in (-R, R):                                     # straight walls
        if abs(d[1]) > 1e-12:
            t = (sy - p[1]) / d[1]
            if t > 1e-9 and abs(p[0] + d[0] * t) <= L + 1e-9 and (best is None or t < best[0]): best = (t, (0.0, -1.0 if sy > 0 else 1.0))
    for cx, side in ((L, 1), (-L, -1)):                   # caps
        ox, oy = p[0] - cx, p[1]; b = ox * d[0] + oy * d[1]; c = ox * ox + oy * oy - R * R; disc = b * b - c
        if disc < 0: continue
        for t in (-b - math.sqrt(disc), -b + math.sqrt(disc)):
            if t > 1e-9:
                x = p[0] + d[0] * t
                if (x - cx) * side >= -1e-9 and (best is None or t < best[0]):
                    q = (x - cx, p[1] + d[1] * t); best = (t, (-q[0] / R, -q[1] / R))
    return best
def simulate(a, L, R, n):
    p = P0; d = (math.cos(a), math.sin(a)); pts = [(0.0, p[0], p[1])]; s = 0.0
    for _ in range(n):
        t, nn = hit(p, d, L, R); p = (p[0] + d[0] * t, p[1] + d[1] * t); s += t
        k = d[0] * nn[0] + d[1] * nn[1]; d = (d[0] - 2 * k * nn[0], d[1] - 2 * k * nn[1]); m = math.hypot(*d); d = (d[0] / m, d[1] / m)
        pts.append((s, p[0], p[1]))
    return pts
def pos(pts, s):
    lo, hi = 0, len(pts) - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if pts[mid][0] <= s: lo = mid
        else: hi = mid
    a, b = pts[lo], pts[min(lo + 1, len(pts) - 1)]
    u = 0 if b[0] == a[0] else (s - a[0]) / (b[0] - a[0])
    return (lerp(a[1], b[1], u), lerp(a[2], b[2], u)), lo

CA, CB = simulate(A0, 0, R_C, 1500), simulate(A0 + DA, 0, R_C, 1500)
SA, SB = simulate(A0, L_S, R_S, 3000), simulate(A0 + DA, L_S, R_S, 3000)
def gap(A, B, s): (a, _), (b, _) = pos(A, s), pos(B, s); return math.hypot(a[0] - b[0], a[1] - b[1])
# find split distance in stadium (gap > 6 px)
S_SPLIT = next(SA[i][0] for i in range(1, len(SA)) if gap(SA, SB, SA[i][0]) > 6)
N_SPLIT = next(i for i in range(len(SA)) if SA[i][0] >= S_SPLIT)

T_GO, T_MORPH0, T_MORPH1, T_GO2, T_SPLIT = 1.2, 8.0, 9.2, 9.6, 15.0
T_SLOW1, T_FAST, T_FINAL = 16.4, 16.8, 23.5
DUR = 27.5
m_pre = (S_SPLIT - V * 1.4) / (V * (T_SPLIT - T_GO2 - 1.4))
def mult(t):
    if t < T_GO: return 0
    if t < 3.0: return 1
    if t < 5.0: return 4
    if t < T_MORPH0: return 20
    if t < T_GO2: return 0
    if t < T_GO2 + 1.4: return 1
    if t < T_SPLIT - .5: return m_pre
    if t < T_SLOW1: return .35 if t >= T_SPLIT - .5 + .0 else m_pre
    if t < T_FAST: return 1
    return 40
# integrate sim distance per frame (each act separately)
NF = int(DUR * FPS) + 1; SC = np.zeros(NF); SS = np.zeros(NF); a1 = a2 = 0.0
for f in range(NF):
    t = f / FPS; m = mult(t) * V / FPS
    if t < T_MORPH0: a1 += m
    elif t >= T_GO2: a2 += m
    SC[f], SS[f] = a1, a2
# correct pre-split so split lands exactly at T_SPLIT
fs = int(T_SPLIT * FPS); SS *= 1.0; corr = S_SPLIT / SS[fs]
for f in range(NF):
    if f <= fs: SS[f] *= corr
    else: SS[f] = SS[f] - SS[fs] / corr + S_SPLIT if False else SS[f] + (corr - 1) * SS[fs] / corr

def shape(t):
    if t < T_MORPH0: return 0.0, R_C
    u = ease(cl((t - T_MORPH0 - .3) / (T_MORPH1 - T_MORPH0 - .3))); return lerp(0, L_S, u), lerp(R_C, R_S, u)
def boundary(ctx, L, R):
    ctx.new_path(); ctx.arc(CX + L, CY, R, -math.pi / 2, math.pi / 2); ctx.arc(CX - L, CY, R, math.pi / 2, 3 * math.pi / 2); ctx.close_path()
def trail(ctx, pts, lo, cur, col, a, w=2.4, start=0):
    if lo < start: return
    ctx.move_to(CX + pts[start][1], CY + pts[start][2])
    for q in pts[start + 1:lo + 1]: ctx.line_to(CX + q[1], CY + q[2])
    ctx.line_to(CX + cur[0], CY + cur[1]); ctx.set_source_rgba(*col, a); ctx.set_line_width(w); ctx.stroke()
def fmt_gap(g):
    if g < 1: return f"{g:.5f} px"
    return f"{g:,.0f} px"

def draw(ctx, t):
    backdrop(ctx); f = min(NF - 1, int(t * FPS)); L, R = shape(t)
    act2 = t >= T_MORPH0
    A, B = (SA, SB) if act2 else (CA, CB); s = SS[f] if act2 else SC[f]
    (pa, la), (pb, lb) = pos(A, s), pos(B, s); g = math.hypot(pa[0] - pb[0], pa[1] - pb[1])
    boundary(ctx, L, R); ctx.set_source_rgba(1, 1, 1, .85); ctx.set_line_width(5); ctx.stroke()
    fade = 1 - cl((t - T_MORPH0) / .4) if T_MORPH0 <= t < T_GO2 else 1
    show = not (T_MORPH0 <= t < T_GO2)
    if show or t < T_MORPH0 + .4:
        if T_MORPH0 <= t < T_GO2: A, B, s = CA, CB, SC[int(T_MORPH0 * FPS) - 1]; (pa, la), (pb, lb) = pos(A, s), pos(B, s)
        ctx.save(); ctx.set_operator(cairo.OPERATOR_ADD)
        k = 1.0 if (la < 60) else max(.3, (60 / la) ** .5)
        trail(ctx, A, la, pa, ORNG, .55 * k * fade); trail(ctx, B, lb, pb, CYAN, .55 * k * fade)
        ctx.restore()
        for p, col in ((pa, ORNG), (pb, CYAN)):
            glow(ctx, CX + p[0], CY + p[1], 55, col, .7 * fade)
        together = g < 6
        if together:
            ctx.new_path(); ctx.arc(CX + pa[0], CY + pa[1], 16, -math.pi / 2, math.pi / 2); ctx.set_source_rgba(*CYAN, fade); ctx.fill()
            ctx.new_path(); ctx.arc(CX + pa[0], CY + pa[1], 16, math.pi / 2, 3 * math.pi / 2); ctx.set_source_rgba(*ORNG, fade); ctx.fill()
        else:
            for p, col in ((pa, ORNG), (pb, CYAN)): ctx.new_path(); ball(ctx, CX + p[0], CY + p[1], 16, col, a=fade)
    if t < T_GO + .2 or T_GO2 - .2 < t < T_GO2 + .6:                 # launch arrow
        x, y = CX + P0[0], CY + P0[1]; a = A0
        ctx.move_to(x, y); ctx.line_to(x + 120 * math.cos(a), y + 120 * math.sin(a)); ctx.set_source_rgba(1, 1, 1, .6); ctx.set_line_width(4); ctx.stroke()
    if T_SPLIT - .3 < t < T_FAST + .6:
        u = t - (T_SPLIT - .3); tagbox(ctx, "SPLIT!", 540, 590, 74, PINK, pointer=False, k=popk(u / .35))
    if T_MORPH0 + .1 < t < T_GO2 + .4: tagbox(ctx, "CIRCLE → STADIUM", 540, 590, 56, (1, 1, 1), fg=INK, pointer=False, k=popk((t - T_MORPH0 - .1) / .35))
    if t >= T_GO and not (T_MORPH0 <= t < T_GO2):
        m = mult(t); speed_tag(ctx, m if m < 1 else round(m * (1 if not act2 or t >= T_FAST or t < T_GO2 + 1.4 else 1)), a=1)
    nb = (la if act2 else la)
    header(ctx, t, [(0, "Two balls, 0.000001° apart", "Will they ever split?", GOLD),
                    (T_MORPH0, "Same two balls", "Now in a different shape", ORNG),
                    (T_SPLIT - .3, f"Split after {N_SPLIT} bounces", "...and never meet again", PINK),
                    (T_FINAL, "This is chaos", "the butterfly effect", CYAN)])
    gc = GRN if g < 1 else (GOLD if g < 50 else PINK)
    stats(ctx, [("BOUNCES", f"{nb:,}", (1, 1, 1)), ("GAP", fmt_gap(g), gc)])

def audio(path):
    tr = Track(DUR); soft_bed(tr, DUR, 38, .012); scale = [0, 3, 5, 7, 10]
    def note_for(x, y): a = (math.atan2(y, x) + math.pi) / (2 * math.pi); k = int(a * 10); return 57 + 12 * (k // 5) + scale[k % 5]
    for act, (A, B, S, t0, t1) in enumerate(((CA, CB, SC, T_GO, T_MORPH0), (SA, SB, SS, T_GO2, DUR - .5))):
        for P, pan in ((A, 0), (B, 1)):
            last = -1; f = int(t0 * FPS)
            for i in range(1, len(P)):
                while f < NF - 1 and S[f] < P[i][0]: f += 1
                tt = f / FPS
                if tt > t1 or f >= NF - 1: break
                if tt - last < .07: continue
                last = tt; dense = mult(tt) > 5
                tr.add(marimba(mtof(note_for(P[i][1], P[i][2]) + (0 if pan == 0 else 0)), .7, .035 if dense else .09), tt)
    tr.add(piano(mtof(38), 3, .2), T_SPLIT); tr.add(piano(mtof(50), 3, .12), T_SPLIT + .02)
    for j, m in enumerate((50, 57, 62, 65, 69)): tr.add(piano(mtof(m), 3, .06), T_FINAL + j * .08)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('split dist', round(S_SPLIT), 'N_SPLIT', N_SPLIT, 'm_pre', round(m_pre, 2), 'circle bounces@8s', pos(CA, SC[int(7.9 * FPS)])[1], 'circle gap', gap(CA, CB, SC[int(7.9 * FPS)]))
    if len(sys.argv) > 1: main(draw, DUR, audio, 'v2_chaos', sys.argv, strength=.9, thr=.6)
