"""SATISFYING 2: 1 ball vs a 10,000 HP boss. Pick-a-gate runner, one trap, and a straggler finish."""
import sys
from fx import *
CROWD_Y, SPEED = 1380, 620
PAIRS = [("+9", "×2", 0, None), ("−5", "×10", 1, None), ("×5", "÷2", 1, 'slide'), ("×100", "−40", 0, None), ("×2", "+4,999", 1, None)]
VALS = [1, 10, 100, 50, 5000, 9999]
GOODCOL, BADCOL = (.45, 1, .5), (1, .3, .35)
def is_bad(lab): return lab[0] in "−÷"
T_PAIR = [4.2 + 2.5 * k for k in range(len(PAIRS))]
T_BOSS_IN, T_FIGHT, T_FIGHT_END = 16.0, 17.0, 19.6
T_STRAG0, T_HIT = 20.7, 21.9
DUR = T_HIT + 3.4
BOSS_HP = 10000

def pair_x(k, t):
    base = (300, 780)
    if PAIRS[k][3] == 'slide': off = -480 * ease(cl((t - (T_PAIR[k] - .8)) / .6))
    else: off = 0
    return base[0] + off, base[1] + off
def crowd_x(t):
    pts = [(0, 540), (2.6, 540)]
    for k, (a, b, ch, sl) in enumerate(PAIRS):
        tgt = (300, 780)[ch] if not sl else 300
        pts.append((T_PAIR[k] - 1.6, None)); pts.append((T_PAIR[k] - .9, tgt)); pts.append((T_PAIR[k] + .4, tgt))
    pts.append((T_BOSS_IN, 540))
    x = 540
    clean = []
    for tt, v in pts:
        if v is None: v = clean[-1][1] if clean else 540
        clean.append((tt, v))
    for (t0, a), (t1, b) in zip(clean, clean[1:]):
        if t0 <= t <= t1: return lerp(a, b, ease((t - t0) / max(1e-3, t1 - t0)))
    return clean[-1][1] if t > clean[-1][0] else 540
def crowd_n(t):
    n = sum(1 for tp in T_PAIR if t >= tp); v = VALS[n]
    if t >= T_FIGHT: v = int(VALS[-1] * (1 - ease(cl((t - T_FIGHT) / (T_FIGHT_END - T_FIGHT)))))
    return v, n
def shown_n(t):
    v, n = crowd_n(t)
    if t >= T_FIGHT or n == 0: return v
    u = ease(cl((t - T_PAIR[n - 1]) / .4)); a = VALS[n - 1]
    return int(round(math.exp(lerp(math.log(a), math.log(v), u))))
def boss_hp(t):
    if t < T_FIGHT: return BOSS_HP
    if t < T_HIT: return BOSS_HP - (VALS[-1] - crowd_n(t)[0])
    return 0
def boss_y(t):
    if t < 2.4: return 520
    if t < 3.4: return lerp(520, -500, ease((t - 2.4) / 1.0))
    if t < T_BOSS_IN: return -500
    return lerp(-500, 470, ease((t - T_BOSS_IN) / 1.0))

PHI = math.pi * (3 - math.sqrt(5))
def crowd_pts(n, cx, cy, t, seed=0):
    nv = min(n, 260); out = []
    sc = 15
    for i in range(nv):
        r = sc * math.sqrt(i + .5); a = i * PHI
        out.append((cx + r * math.cos(a) + 3 * math.sin(t * 9 + i), cy + r * math.sin(a) * .8 + 4 * math.sin(t * 11 + i * 1.7)))
    return out

def road(ctx, t):
    ctx.new_path(); ctx.rectangle(90, 0, 900, H); ctx.set_source_rgba(.25, .2, .5, .35); ctx.fill()
    off = (t * SPEED) % 160
    for k in range(-1, 14):
        y = k * 160 + off; ctx.new_path(); rrect(ctx, 530, y, 20, 80, 10); ctx.set_source_rgba(1, 1, 1, .12); ctx.fill()
    for x in (90, 990):
        ctx.new_path(); ctx.rectangle(x - 8, 0, 16, H); ctx.set_source_rgb(.55, .5, 1); ctx.fill()

def gate(ctx, x, y, lab, t_pass, t, chosen):
    bad = is_bad(lab); col = BADCOL if bad else GOODCOL
    fl = cl(1 - (t - t_pass) / .3) if (t >= t_pass and chosen) else 0
    w = 400
    ctx.new_path(); rrect(ctx, x - w / 2, y - 70, w, 140, 26); ctx.set_source_rgba(*col, .2 + .5 * fl); ctx.fill()
    ctx.new_path(); rrect(ctx, x - w / 2, y - 70, w, 140, 26); ctx.set_source_rgb(*col); ctx.set_line_width(8); ctx.stroke()
    label(ctx, lab, x, y + 3, 84 if len(lab) < 5 else 70, col=(1, 1, 1), shadow=.6)

def boss(ctx, t):
    y = boss_y(t)
    if y < -300: return
    hp = boss_hp(t); dead = t >= T_HIT; u = t - T_HIT
    hit = T_FIGHT < t < T_FIGHT_END or (T_HIT - .05 < t < T_HIT + .1)
    shake = (8 * math.sin(t * 70) if hit else 0) + (3 * math.sin(t * 40) if hp == 1 and t < T_HIT else 0)
    ctx.save(); ctx.translate(540 + shake, y)
    if not dead:
        s = 1 + .03 * math.sin(t * 4)
        ctx.scale(s, s)
        glow(ctx, 0, 0, 420, (1, .2, .25), .35)
        for k in range(16):
            a = k * math.pi / 8 + t * .3; ctx.save(); ctx.rotate(a); ctx.move_to(-34, -230); ctx.line_to(0, -330); ctx.line_to(34, -230); ctx.close_path(); ctx.set_source_rgb(.45, .08, .14); ctx.fill(); ctx.restore()
        g = cairo.RadialGradient(-60, -80, 20, 0, 0, 300); g.add_color_stop_rgb(0, .95, .25, .3); g.add_color_stop_rgb(1, .35, .04, .1)
        ctx.new_path(); rrect(ctx, -240, -240, 480, 480, 70); ctx.set_source(g); ctx.fill()
        ctx.set_source_rgba(1, .6, .3, .55 + .3 * math.sin(t * 6)); ctx.set_line_width(7)
        for (a, b) in [((-120, -140), (-30, -40)), ((-30, -40), (60, -90)), ((-30, -40), (10, 90)), ((10, 90), (110, 150)), ((60, -90), (150, -40))]:
            ctx.move_to(*a); ctx.line_to(*b); ctx.stroke()
        # HP bar
        ctx.new_path(); rrect(ctx, -300, 290, 600, 70, 35); ctx.set_source_rgba(0, 0, 0, .6); ctx.fill()
        p = hp / BOSS_HP
        if p > 0: ctx.new_path(); rrect(ctx, -294, 296, max(58, 588 * p), 58, 29); ctx.set_source_rgb(1, .3, .35); ctx.fill()
        label(ctx, f"{hp:,} HP", 0, 326, 50, col=(1, 1, 1), shadow=.6)
    else:
        r = random.Random(9)
        for k in range(40):
            a = r.uniform(0, 6.28); d = r.uniform(200, 900) * u; sz = r.uniform(20, 60) * max(0, 1 - u / 1.6)
            ctx.save(); ctx.translate(math.cos(a) * d, math.sin(a) * d + 600 * u * u); ctx.rotate(u * r.uniform(-8, 8)); ctx.rectangle(-sz / 2, -sz / 2, sz, sz)
            ctx.set_source_rgb(.85, .2, .28); ctx.fill(); ctx.restore()
        if u < .4: glow(ctx, 0, 0, 700 * (u / .4 + .2), (1, .85, .5), .9 * (1 - u / .4))
    ctx.restore()

def draw(ctx, t):
    bg(ctx, (.08, .04, .18), (.03, .02, .09)); road(ctx, t)
    for k, (a, b, ch, sl) in enumerate(PAIRS):
        y = CROWD_Y - (T_PAIR[k] - t) * SPEED
        if -150 < y < H + 150:
            xa, xb = pair_x(k, min(t, T_PAIR[k]))
            gate(ctx, xa, y, a, T_PAIR[k], t, ch == 0 and not sl); gate(ctx, xb, y, b, T_PAIR[k], t, ch == 1 or bool(sl))
            if sl and xa < 540 < xb: pass
    boss(ctx, t)
    # crowd
    v, n = crowd_n(t); sv = shown_n(t); cx = crowd_x(t)
    if t >= T_FIGHT and t < T_FIGHT_END + .2:                       # stream into the boss
        r = random.Random(int(t * 30))
        for k in range(60):
            u = r.random(); x = lerp(cx, 540 + r.uniform(-200, 200), u); y = lerp(CROWD_Y, boss_y(t) + 240, u)
            ctx.new_path(); ctx.arc(x, y, 9, 0, 7); ctx.set_source_rgb(.45, .85, 1); ctx.fill()
    if v > 0:
        cy = CROWD_Y if t < T_FIGHT else lerp(CROWD_Y, 1250, ease((t - T_FIGHT) / .6))
        pts = crowd_pts(max(1, sv if t < T_FIGHT else v), cx, cy, t)
        bad = n and is_bad((PAIRS[n - 1][0], PAIRS[n - 1][1])[1 if PAIRS[n - 1][3] else PAIRS[n - 1][2]]) and t - T_PAIR[n - 1] < 1.2
        col = (1, .45, .5) if bad else (.45, .85, 1)
        glow(ctx, cx, cy, 60 + 9 * math.sqrt(len(pts)) * 1.6, col, .35)
        for (x, y) in pts: ctx.new_path(); ball(ctx, x, y, 11, col, spec=.6)
        pk_ = popk(cl((t - T_PAIR[n - 1]) / .35)) if n and t < T_FIGHT else 1
        ry = cy - 15 * math.sqrt(len(pts)) * .8 - 70 if t < T_FIGHT else cy + 15 * math.sqrt(len(pts)) * .8 + 80
        ctx.save(); ctx.translate(cx, ry); ctx.scale(pk_, pk_); label(ctx, f"{sv:,}" if t < T_FIGHT else f"{v:,}", 0, 0, 80, col=(1, .45, .5) if bad else (1, 1, 1), shadow=.7); ctx.restore()
    # straggler: one ball that tripped at the first gate
    if T_PAIR[0] + .3 < t < T_HIT:
        if t < T_STRAG0: sx, sy, a = crowd_x(t - .9) + 30, 1720 + 10 * abs(math.sin(t * 5)), .55
        else:
            u = ease((t - T_STRAG0) / (T_HIT - T_STRAG0)); sx, sy, a = lerp(crowd_x(T_STRAG0 - .9) + 30, 540, u), lerp(1720, boss_y(t) + 250, u), 1
        if t > T_STRAG0: glow(ctx, sx, sy, 90, (1, .85, .3), .8)
        ctx.new_path(); ball(ctx, sx, sy, 13, (1, .85, .3) if t > T_STRAG0 else (.45, .85, 1), a=a, spec=.7)
        if t > T_STRAG0 - .2: label(ctx, "+1", sx + 50, sy - 30, 54, col=(1, .85, .3))
    # captions
    if t < 2.6:
        k = popk(t / .4)
        tagbox(ctx, "1  vs  10,000", 540, 980, 100, (1, 1, 1), fg=INK, pointer=False, k=k)
    if n >= 3 and T_PAIR[2] + .1 < t < T_PAIR[2] + 1.6: tagbox(ctx, "NOOO!", 540, 900, 90, BADCOL, pointer=False, k=popk((t - T_PAIR[2] - .1) / .3))
    if T_FIGHT_END + .1 < t < T_HIT: tagbox(ctx, "1 HP LEFT!", 540, 1000, 96, BADCOL, pointer=False, k=popk((t - T_FIGHT_END - .1) / .35))
    if t > T_HIT + .4:
        u = t - T_HIT - .4
        tagbox(ctx, "THE LAST ONE!", 540, 760, 96, (1, .85, .3), fg=INK, pointer=False, k=popk(u / .45))
        r = random.Random(2)
        for k in range(70):
            x = r.uniform(0, W) + 40 * math.sin(u * 3 + k); y = -40 + r.uniform(0, 300) + 520 * u
            ctx.save(); ctx.translate(x, y); ctx.rotate(u * r.uniform(-6, 6)); ctx.rectangle(-9, -5, 18, 10); ctx.set_source_rgb(*[(1, .85, .3), (.45, .85, 1), (.45, 1, .5)][k % 3]); ctx.fill(); ctx.restore()

def tone(f0, f1, d, amp, sq=False):
    m = np.arange(int(SR * d)) / SR; f = np.linspace(f0, f1, len(m)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) if not sq else np.tanh(3 * np.sin(ph)) * .6
    return x * np.minimum(1, m / .005) * np.minimum(1, (d - m) / .05) * amp
def audio(path):
    tr = Track(DUR); pad(tr, DUR, .035); g = np.random.default_rng(3)
    k = 0; beat = 60 / 120                                                  # marching pulse
    while k * beat < T_FIGHT:
        tr.add(tone(90, 50, .12, .12), k * beat); k += 1
    step = 0
    for i, (a, b, ch, sl) in enumerate(PAIRS):
        lab = (a, b)[1 if sl else ch]
        if is_bad(lab):
            for j, f in enumerate((330, 311, 294, 262)): tr.add(tone(f, f * .97, .2 if j < 3 else .5, .1, sq=True), T_PAIR[i] + j * .18)
        else:
            step += 1; base = 392 * 2 ** (step * 2 / 12)
            for j, m in enumerate((1, 1.26, 1.5, 2)): tr.add(chime(base * m, .05, .8), T_PAIR[i] + j * .055)
    tr.add(tone(60, 40, 1.0, .25), T_BOSS_IN)
    for j in range(int((T_FIGHT_END - T_FIGHT) * 25)):
        tt = T_FIGHT + j / 25; x = np.diff(np.r_[0, g.normal(0, 1, 900)]) * np.exp(-np.arange(900) / 120); tr.add(x * .12, tt)
        if j % 3 == 0: tr.add(tone(500 + 15 * j, 480 + 15 * j, .05, .03), tt)
    for j in range(3): tr.add(tone(70, 50, .15, .3), T_FIGHT_END + .2 + j * .45); tr.add(tone(70, 50, .12, .22), T_FIGHT_END + .38 + j * .45)
    tr.add(tone(900, 1800, 1.1, .04), T_STRAG0)
    m = np.arange(int(SR * 1.5)) / SR; tr.add(np.sin(2 * np.pi * (70 - 25 * m) * m) * np.exp(-m * 3) * .45, T_HIT)
    tr.add(g.normal(0, 1, int(SR * .6)) * np.exp(-np.arange(int(SR * .6)) / (SR * .12)) * .12, T_HIT)
    for f in (523, 659, 784, 1046, 1318): tr.add(chime(f, .05, 2.4), T_HIT + .1)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('DUR', round(DUR, 1))
    if len(sys.argv) > 1: main(draw, DUR, audio, 's2_boss', sys.argv, strength=.8, thr=.6)
