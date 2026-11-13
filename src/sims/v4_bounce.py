"""Visual Brain: same course, 4 bounciness levels. Which ball reaches the bottom first?"""
import sys, os, math
import pymunk
from simkit import *
EL = [.95, .7, .45, .2]; LCOL = [CYAN, GRN, GOLD, PINK]
LW, LX0, BRAD = 240, 45, 15
FIN = int(os.environ.get('FIN', '4200')); T_GO = 2.4
def lane_geo():
    segs, pegs, spins = [], [], []
    for r, y in enumerate(range(380, 1500, 75)):
        off = 30 if r % 2 else 60
        for x in range(off, LW - 44, 60):
            if x >= 44: pegs.append((x, y))
    for k, y in enumerate(range(1600, 2700, 160)):
        segs.append(((0, y), (LW - 55, y + 70)) if k % 2 == 0 else ((LW, y), (55, y + 70)))
    spins.append(((LW / 2, 2900), 150, 2.4))
    for r, y in enumerate(range(3100, 3900, 70)):
        off = 40 if r % 2 else 75
        for x in range(off, LW - 44, 70):
            if x >= 44: pegs.append((x, y))
    return segs, pegs, spins
SEGS, PEGS, SPINS = lane_geo()
def simulate(maxT=40):
    sp = pymunk.Space(); sp.gravity = (0, 1500); st = sp.static_body; balls = []; spinb = []; gates = []
    for li in range(4):
        ox = LX0 + li * 250
        for a, b in [((0, -200), (0, FIN + 300)), ((LW, -200), (LW, FIN + 300))] + SEGS:
            s = pymunk.Segment(st, (ox + a[0], a[1]), (ox + b[0], b[1]), 5); s.elasticity = 1.0; s.friction = .35; sp.add(s)
        for (x, y) in PEGS:
            c = pymunk.Circle(st, 8, (ox + x, y)); c.elasticity = 1.0; c.friction = .3; sp.add(c)
        for (p, L, w) in SPINS:
            kb = pymunk.Body(body_type=pymunk.Body.KINEMATIC); kb.position = (ox + p[0], p[1]); kb.angular_velocity = w; sp.add(kb)
            s = pymunk.Segment(kb, (-L / 2, 0), (L / 2, 0), 7); s.elasticity = 1.0; s.friction = .3; sp.add(s); spinb.append(kb)
        g = pymunk.Segment(st, (ox, 250), (ox + LW, 250), 5); sp.add(g); gates.append(g)
        b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, BRAD)); b.position = (ox + LW / 2 + 3, 200)
        c = pymunk.Circle(b, BRAD); c.elasticity = EL[li]; c.friction = .3; c.collision_type = 10 + li; sp.add(b, c); balls.append(b)
    hits = [[0] * 4]
    def mk(li):
        def post(arb, s, d):
            if arb.total_impulse.length > 120: hits[-1][li] += 1
        return post
    for li in range(4):
        if hasattr(sp, 'on_collision'): sp.on_collision(10 + li, None, post_solve=mk(li))
    F = []; H = []; fin = [None] * 4; sub = 8; dt = 1 / (FPS * sub)
    for fi in range(int(maxT * FPS)):
        t = fi / FPS; hits.append([0] * 4)
        if t >= T_GO:
            for g in gates:
                if g in sp.shapes: sp.remove(g)
        for _ in range(sub): sp.step(dt)
        ys = []
        for li, b in enumerate(balls):
            if fin[li] is None and b.position.y > FIN: fin[li] = t
            if fin[li] is not None and b.position.y > FIN + 120: b.velocity = (0, 0); b.position = (b.position.x, FIN + 120)
        F.append(([tuple(b.position) for b in balls], [k.angle for k in spinb[:1]]))
        H.append(hits[-1])
        dn = sorted(f for f in fin if f is not None)
        if len(dn) >= 3 and t > dn[2] + 2.8: break
    return F, H, fin
F, HITS, FIN_T = simulate()
DUR = len(F) / FPS
ORDER = sorted(range(4), key=lambda i: FIN_T[i] if FIN_T[i] is not None else 1e9)
CAM = []; c = 0
for fi, (pos, _) in enumerate(F):
    ys = sorted(p[1] for p in pos); lead = ys[-1]
    target = min(FIN - 1100, max(-100, lead - 1050)); c += (target - c) * .08; CAM.append(c)

def draw(ctx, t):
    backdrop(ctx); fi = min(len(F) - 1, int(t * FPS)); pos, ang = F[fi]; cy = CAM[fi]
    ctx.save(); ctx.translate(0, 420 - cy)
    for li in range(4):
        ox = LX0 + li * 250; col = LCOL[li]
        ctx.new_path(); rrect(ctx, ox, max(cy - 400, -200), LW, 2400, 18); ctx.set_source_rgba(*col, .05); ctx.fill()
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for x in (ox, ox + LW): ctx.move_to(x, cy - 400); ctx.line_to(x, min(FIN + 300, cy + 2200)); ctx.set_source_rgba(*col, .5); ctx.set_line_width(6); ctx.stroke()
        for a, b in SEGS:
            if cy - 400 < a[1] < cy + 2100: ctx.move_to(ox + a[0], a[1]); ctx.line_to(ox + b[0], b[1]); ctx.set_source_rgba(1, 1, 1, .8); ctx.set_line_width(10); ctx.stroke()
        for (x, y) in PEGS:
            if cy - 400 < y < cy + 2100: ctx.new_path(); ctx.arc(ox + x, y, 8, 0, 7); ctx.set_source_rgba(.8, .82, 1, .9); ctx.fill()
        for (p, L, w) in SPINS:
            a = w * max(0, t) if False else ang[0] if li == 0 else ang[0]
            dx, dy = math.cos(a) * L / 2, math.sin(a) * L / 2
            ctx.move_to(ox + p[0] - dx, p[1] - dy); ctx.line_to(ox + p[0] + dx, p[1] + dy); ctx.set_source_rgb(1, .5, .75); ctx.set_line_width(14); ctx.stroke()
            ctx.new_path(); ctx.arc(ox + p[0], p[1], 9, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        if t < T_GO: ctx.move_to(ox, 250); ctx.line_to(ox + LW, 250); ctx.set_source_rgb(1, 1, 1); ctx.set_line_width(8); ctx.stroke()
    # finish line
    for k in range(30):
        x = LX0 + k * 34; ctx.rectangle(x, FIN, 17, 17); ctx.rectangle(x + 17, FIN + 17, 17, 17)
    ctx.set_source_rgba(1, 1, 1, .85); ctx.fill()
    for li, (x, y) in enumerate(pos):
        glow(ctx, x, y, 55, LCOL[li], .7); ctx.new_path(); ball(ctx, x, y, BRAD, LCOL[li], spec=.7)
    ctx.restore()
    g = cairo.LinearGradient(0, 0, 0, 660); g.add_color_stop_rgba(0, *BG0, 1); g.add_color_stop_rgba(.88, .05, .04, .13, 1); g.add_color_stop_rgba(1, .05, .04, .13, 0)
    ctx.rectangle(0, 0, W, 660); ctx.set_source(g); ctx.fill()
    # live ranking
    done = [i for i in ORDER if FIN_T[i] is not None and FIN_T[i] <= t]
    rest = sorted([i for i in range(4) if i not in done], key=lambda i: -pos[i][1]); rank = done + rest
    for li in range(4):
        ox = LX0 + li * 250 + LW / 2; place = rank.index(li) + 1
        ctx.new_path(); rrect(ctx, ox - 95, 470, 190, 104, 22); ctx.set_source_rgba(0, 0, 0, .55); ctx.fill()
        ctx.new_path(); rrect(ctx, ox - 95, 470, 190, 104, 22); ctx.set_source_rgba(*LCOL[li], .9); ctx.set_line_width(4); ctx.stroke()
        label(ctx, f"{int(EL[li] * 100)}%", ox, 505, 44, col=LCOL[li], shadow=0)
        if t > T_GO:
            stuck = FIN_T[li] is None and len(done) >= 3
            label(ctx, "still bouncing" if stuck else ["1st", "2nd", "3rd", "4th"][place - 1], ox, 549, 24 if stuck else 30, col=PINK if stuck else ((1, 1, 1) if place > 1 else GOLD), shadow=0)
        else: label(ctx, "bounce", ox, 549, 26, col=(.62, .66, .8), shadow=0)
    w = ORDER[0]
    header(ctx, t, [(0, "Same course, 4 bounciness levels", "Which one wins? Pick now", GOLD),
                    (T_GO, "Same course, 4 bounciness levels", "Which one wins?", GOLD),
                    (FIN_T[w] + .1, f"{int(EL[w] * 100)}% bounce wins!", "Did you pick right?", LCOL[w])])
    if t < T_GO: tagbox(ctx, "3" if t < T_GO - 1.4 else "2" if t < T_GO - .7 else "1", 540, 1400, 110, (1, 1, 1), fg=INK, pointer=False, k=popk(((t - .3) % .7) / .3)) if t > .3 else None
    if T_GO <= t < T_GO + .6: tagbox(ctx, "GO!", 540, 1400, 110, GRN, fg=INK, pointer=False, k=popk((t - T_GO) / .3))
    if t > FIN_T[w]:
        u = t - FIN_T[w]; tagbox(ctx, "WINNER", LX0 + w * 250 + LW / 2, 650, 50, LCOL[w], fg=INK, pointer=True, k=popk(u / .4))

def audio(path):
    tr = Track(DUR); soft_bed(tr, DUR, 41, .012); scale = [0, 2, 4, 7, 9]; base = [72, 67, 60, 55]
    for j in range(3): tr.add(marimba(mtof(72), .4, .1), .3 + j * .7)
    tr.add(marimba(mtof(84), .6, .14), T_GO)
    last = [-1] * 4
    for fi, h in enumerate(HITS):
        t = fi / FPS
        for li in range(4):
            if h[li] and t - last[li] > .08:
                last[li] = t; tr.add(marimba(mtof(base[li] + scale[(fi // 3 + li) % 5]), .6, .05), t)
    for k, li in enumerate(ORDER):
        if FIN_T[li]: tr.add(piano(mtof(base[li] + 12), 2, .1 if k else .16), FIN_T[li])
    w = ORDER[0]
    for j, m in enumerate((60, 64, 67, 72, 76)): tr.add(piano(mtof(m), 2.5, .06), FIN_T[w] + .1 + j * .07)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('FIN', FIN, 'times', [round(x, 2) if x else None for x in FIN_T], 'order', [EL[i] for i in ORDER], 'DUR', round(DUR, 1))
    if len(sys.argv) > 1: main(draw, DUR, audio, 'v4_bounce', sys.argv, strength=.85, thr=.6)
