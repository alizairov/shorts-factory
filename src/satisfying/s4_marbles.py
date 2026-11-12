"""SATISFYING 4: 50 numbered marbles race through lava bins — only one survives."""
import sys, colorsys
import pymunk, os
SEED = int(os.environ.get('SEED', '1'))
from fx import *
N, R = 50, 20
T_GO = 2.2
BIN_ROWS = [(1850, {1, 2, 4, 5}), (3150, {0, 2, 4, 6}), (4450, {1, 3, 5}), (5550, {3})]
FINAL_Y = BIN_ROWS[-1][0]
WORLD_H = FINAL_Y + 600
COLS = [colorsys.hsv_to_rgb(((i * .618) % 1), .65 + .3 * (i % 2), 1) for i in range(N)]

def bins(top):
    w = 1020 / 7; out = []
    for i in range(7): out.append((30 + i * w, 30 + (i + 1) * w))
    return out

def build():
    sp = pymunk.Space(); sp.gravity = (0, 1500); st = sp.static_body; segs = []; pegs = []; spin = []
    def seg(a, b, r=6, keep=True):
        s = pymunk.Segment(st, a, b, r); s.elasticity = .45; s.friction = .4; sp.add(s)
        if keep: segs.append((a, b, r))
        return s
    seg((30, -400), (30, WORLD_H)); seg((1050, -400), (1050, WORLD_H))
    gate = seg((30, 400), (1050, 400), keep=False)
    def pegfield(y0, y1, dy=95, dx=118):
        y = y0; k = 0
        while y < y1:
            off = 0 if k % 2 == 0 else dx / 2
            x = 105 + off
            while x < 985:
                c = pymunk.Circle(st, 10, (x, y)); c.elasticity = .5; c.friction = .3; sp.add(c); pegs.append((x, y)); x += dx
            y += dy; k += 1
    pegfield(560, 1350)
    def spinner(x, y, L, w, arms=1):
        b = pymunk.Body(body_type=pymunk.Body.KINEMATIC); b.position = (x, y); b.angular_velocity = w; sp.add(b)
        for a in range(arms):
            ang = a * math.pi / arms; dx, dy = math.cos(ang) * L / 2, math.sin(ang) * L / 2
            s = pymunk.Segment(b, (-dx, -dy), (dx, dy), 10); s.elasticity = .6; s.friction = .3; sp.add(s)
        spin.append((b, L, arms))
    spinner(290, 1560, 300, 2.6); spinner(790, 1560, 300, -2.6)
    def binrow(top, opens):
        bs = bins(top)
        for i, (x0, x1) in enumerate(bs):
            if i > 0: seg((x0 - 30, top + 50), (x0, top)); seg((x0, top), (x0 + 30, top + 50)); seg((x0 - 30, top + 50), (x0 - 30, top + 260)); seg((x0 + 30, top + 50), (x0 + 30, top + 260))
            if i not in opens: seg((x0 + (30 if i else 0), top + 260), (x1 - (30 if i < 6 else 0), top + 260))
    for top, op in BIN_ROWS: binrow(top, op)
    pegfield(2300, 2700, 110, 140)
    spinner(300, 2850, 260, 3.0, 2); spinner(780, 2850, 260, -3.0, 2)
    pegfield(3560, 3980, 100, 135); spinner(300, 4150, 280, 2.8); spinner(780, 4150, 280, -2.8)
    pegfield(4850, 5300, 100, 125)
    seg((30, FINAL_Y + 560), (1050, FINAL_Y + 560))
    balls = []
    for i in range(N):
        b = pymunk.Body(1, pymunk.moment_for_circle(1, 0, R)); b.position = (110 + (i % 10) * 95 + (i // 10 % 2) * 20 + random.Random(SEED * 1000 + i).uniform(-6, 6), 120 + (i // 10) * 52)
        c = pymunk.Circle(b, R); c.elasticity = .5; c.friction = .3; c.collision_type = 1; sp.add(b, c); balls.append((b, c))
    return sp, gate, balls, segs, pegs, spin

def lava_zone(x, y):
    for top, op in BIN_ROWS:
        if top + 120 < y < top + 300:
            for i, (x0, x1) in enumerate(bins(top)):
                if x0 <= x <= x1 and i not in op: return True
    return False

def simulate(maxT=40):
    sp, gate, balls, segs, pegs, spin = build()
    hits = [0]
    h = sp.on_collision(1, None, post_solve=lambda arb, s, d: hits.__setitem__(0, hits[0] + (1 if arb.total_impulse.length > 250 else 0))) if hasattr(sp, 'on_collision') else None
    alive = [True] * N; died = []; F = []; HITS = []; winner = None; t_win = None; closed = False
    sub = 6; dt = 1 / (FPS * sub)
    for fi in range(int(maxT * FPS)):
        t = fi / FPS; hits[0] = 0
        if t >= T_GO and gate in sp.shapes: sp.remove(gate)
        for s_ in range(sub): sp.step(dt)
        for i, (b, c) in enumerate(balls):
            if not alive[i]: continue
            x, y = b.position
            if lava_zone(x, y): alive[i] = False; died.append((t, i, x, y)); sp.remove(b, c)
            elif winner is None and y > FINAL_Y + 300: winner = i; t_win = t
        if winner is not None and not closed:
            x0, x1 = bins(FINAL_Y)[3]; s = pymunk.Segment(sp.static_body, (x0, FINAL_Y + 40), (x1, FINAL_Y + 40), 8); sp.add(s); closed = True
        F.append(([tuple(b.position) for b, c in balls], [b.angle for b, c in balls], list(alive), [(b.angle) for b, L, a in spin]))
        HITS.append(hits[0])
        if t_win and sum(alive) == 1 and t > t_win + 3.5 and all(t - d[0] > 2 for d in died[-1:]): break
    return F, HITS, died, winner, t_win, segs, pegs, [(b.position, L, a) for b, L, a in spin]

F, HITS, DIED, WIN, T_WIN, SEGS, PEGS, SPIN = simulate()
DUR = len(F) / FPS
T_ONE = max([d[0] for d in DIED] + [T_WIN or 0])

def camy_raw(fi):
    pos, ang, alive, _ = F[fi]
    ys = sorted(p[1] for p, a in zip(pos, alive) if a)
    if WIN is not None and fi / FPS > T_WIN: target = pos[WIN][1] - 1100
    else: target = ys[int(len(ys) * .8)] - 1000 if ys else 0
    return max(-60, min(WORLD_H - 1700, target))
CAM = []
c = camy_raw(0)
for fi in range(len(F)): c += (camy_raw(fi) - c) * .07; CAM.append(c)

def draw(ctx, t):
    fi = min(len(F) - 1, int(t * FPS + 1e-6)); pos, ang, alive, sang = F[fi]; cy = CAM[fi]
    bg(ctx, (.06, .04, .16), (.03, .02, .09))
    ctx.save(); ctx.translate(0, -cy)
    # lava + open bins
    for top, op in BIN_ROWS:
        if top + 400 < cy or top > cy + H: continue
        for i, (x0, x1) in enumerate(bins(top)):
            xa, xb = x0 + (30 if i else 0), x1 - (30 if i < 6 else 0)
            if i in op:
                ctx.new_path(); ctx.rectangle(xa, top + 60, xb - xa, 210); ctx.set_source_rgba(.4, 1, .5, .14); ctx.fill()
                for k in range(3):
                    yy = top + 110 + k * 50 + (t * 80 % 50); ctx.move_to((xa + xb) / 2 - 18, yy); ctx.line_to((xa + xb) / 2, yy + 16); ctx.line_to((xa + xb) / 2 + 18, yy)
                    ctx.set_source_rgba(.5, 1, .55, .7); ctx.set_line_width(6); ctx.stroke()
            else:
                g = cairo.LinearGradient(0, top + 110, 0, top + 270); g.add_color_stop_rgb(0, 1, .55, .1); g.add_color_stop_rgb(1, .8, .1, .1)
                ctx.new_path(); ctx.rectangle(xa, top + 120, xb - xa, 150); ctx.set_source(g); ctx.fill()
                for k in range(4):
                    bx = xa + (xb - xa) * ((k * .29 + .1) % 1); by = top + 125 - 8 * abs(math.sin(t * 3 + k * 2 + i))
                    ctx.new_path(); ctx.arc(bx, by, 7, 0, 7); ctx.set_source_rgb(1, .7, .2); ctx.fill()
                glow(ctx, (xa + xb) / 2, top + 150, 120, (1, .4, .1), .35)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for (a, b, r) in SEGS:
        if max(a[1], b[1]) < cy - 50 or min(a[1], b[1]) > cy + H + 50: continue
        ctx.move_to(*a); ctx.line_to(*b); ctx.set_source_rgb(.55, .5, 1); ctx.set_line_width(r * 2 + 2); ctx.stroke()
    if T_WIN and t >= T_WIN:
        x0, x1 = bins(FINAL_Y)[3]; ctx.move_to(x0, FINAL_Y + 40); ctx.line_to(x1, FINAL_Y + 40); ctx.set_source_rgb(1, .8, .25); ctx.set_line_width(16); ctx.stroke()
    if t < T_GO: ctx.move_to(30, 400); ctx.line_to(1050, 400); ctx.set_source_rgb(1, .8, .25); ctx.set_line_width(14); ctx.stroke()
    for (x, y) in PEGS:
        if cy - 30 < y < cy + H + 30: ctx.new_path(); ctx.arc(x, y, 10, 0, 7); ctx.set_source_rgb(.75, .7, 1); ctx.fill()
    for (p, L, arms), a in zip(SPIN, sang):
        for k in range(arms):
            aa = a + k * math.pi / arms; dx, dy = math.cos(aa) * L / 2, math.sin(aa) * L / 2
            ctx.move_to(p[0] - dx, p[1] - dy); ctx.line_to(p[0] + dx, p[1] + dy); ctx.set_source_rgb(1, .45, .7); ctx.set_line_width(22); ctx.stroke()
        ctx.new_path(); ctx.arc(p[0], p[1], 14, 0, 7); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    if FINAL_Y + 300 > cy:
        label(ctx, "FINISH", 540, FINAL_Y + 420, 70, col=(1, .85, .3))
    # deaths
    for (dt_, i, x, y) in DIED:
        u = t - dt_
        if 0 <= u < .8:
            ctx.new_path(); ball(ctx, x, y + 40 * u, R * (1 - u / .8), COLS[i], a=1 - u / .8)
            for k in range(6):
                ctx.new_path(); ctx.arc(x + (k - 2.5) * 12, y - 60 * u - k * 8 * u, 9 * (1 - u / .8), 0, 7); ctx.set_source_rgba(.9, .9, .9, .5 * (1 - u / .8)); ctx.fill()
    for i in range(N):
        if not alive[i]: continue
        x, y = pos[i]
        if y < cy - 40 or y > cy + H + 40: continue
        win = WIN == i and T_WIN and t > T_WIN
        if win: glow(ctx, x, y, 110, (1, .85, .3), .8)
        ctx.new_path(); ball(ctx, x, y, R * (1.25 if win else 1), COLS[i], spec=.6)
        label(ctx, str(i + 1), x, y + 1, 20 if not win else 26, col=INK, shadow=0)
    ctx.restore()
    n = sum(alive)
    ctx.new_path(); rrect(ctx, 330, 215, 420, 96, 48); ctx.set_source_rgba(0, 0, 0, .45); ctx.fill()
    ctx.new_path(); ctx.arc(386, 263, 20, 0, 7); ctx.set_source_rgb(1, .45, .3); ctx.fill()
    label(ctx, f"{n} LEFT", 575, 265, 58, col=(1, .85, .3) if n == 1 else (1, 1, 1), shadow=.3)
    if t < T_GO: tagbox(ctx, "PICK A NUMBER", 540, 640, 84, (1, .8, .25), fg=INK, pointer=False, k=popk(t / .4))
    if t < T_GO + .6 and t > T_GO - .5: tagbox(ctx, "GO!", 540, 640 if t >= T_GO else -500, 110, (.45, 1, .5), fg=INK, pointer=False, k=popk((t - T_GO) / .3))
    if T_WIN and t > T_ONE + .2:
        u = t - T_ONE - .2
        tagbox(ctx, f"#{WIN + 1} SURVIVED!", 540, 600, 92, COLS[WIN], fg=INK, pointer=False, k=popk(u / .45))
        tagbox(ctx, "WAS IT YOURS?", 540, 1400, 60, (1, 1, 1), fg=INK, pointer=False, k=popk((u - .8) / .4))
        r = random.Random(2)
        for k in range(70):
            x = r.uniform(0, W) + 40 * math.sin(u * 3 + k); y = -40 + r.uniform(0, 300) + 520 * u
            ctx.save(); ctx.translate(x, y); ctx.rotate(u * r.uniform(-6, 6)); ctx.rectangle(-9, -5, 18, 10); ctx.set_source_rgb(*COLS[k % N]); ctx.fill(); ctx.restore()

def tone(f0, f1, d, amp):
    m = np.arange(int(SR * d)) / SR; f = np.linspace(f0, f1, len(m)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m / (d / 3)) * np.minimum(1, m / .004) * amp
def audio(path):
    tr = Track(DUR); pad(tr, DUR, .035); g = np.random.default_rng(2)
    for k, f in enumerate((440, 440, 880)): tr.add(tone(f, f, .25, .12), T_GO - 1.0 + k * .5 if k < 2 else T_GO)
    for fi, n in enumerate(HITS):
        if n: 
            x = np.diff(np.r_[0, g.normal(0, 1, int(SR * .02))]) * np.exp(-np.arange(int(SR * .02)) / (SR * .003)); tr.add(x * min(.12, .03 * math.sqrt(n)), fi / FPS)
            tr.add(tone(1800 + 400 * (fi % 3), 1800, .05, min(.04, .012 * math.sqrt(n))), fi / FPS)
    last = -1
    for (dt_, i, x, y) in DIED:
        if dt_ - last < .06: continue
        last = dt_; x = g.normal(0, 1, int(SR * .45)); X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < 1500)] *= .2
        x = np.fft.irfft(X, len(x)); x = x / np.abs(x).max() * np.exp(-np.arange(len(x)) / (SR * .12)) * .09; tr.add(x, dt_); tr.add(tone(220, 90, .3, .1), dt_)
    if T_WIN:
        tr.add(chime(1046, .07, 1.4), T_WIN)
        for f in (523, 659, 784, 1046, 1318): tr.add(chime(f, .05, 2.4), T_ONE + .2)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('DUR', round(DUR, 1), 'winner', WIN, 'T_WIN', T_WIN, 'T_ONE', round(T_ONE, 1), 'alive', sum(F[-1][2]))
    for tt in (5, 8, 12, 16, 20): print(tt, sum(F[min(len(F)-1, tt * 30)][2]))
    if len(sys.argv) > 1: main(draw, DUR, audio, 's4_marbles', sys.argv, strength=.8, thr=.6)
