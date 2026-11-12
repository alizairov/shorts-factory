"""SATISFYING 5: one ball rolls down a zigzag, gates multiply it, needs 1,000,000 to open the vault."""
import sys
from fx import *
GATES = [("×5", lambda v: v * 5, 0), ("×10", lambda v: v * 10, 0), ("−90%", lambda v: v // 10, 1), ("×20", lambda v: v * 20, 0),
         ("×100", lambda v: v * 100, 0), ("÷2", lambda v: v // 2, 1), ("×20", lambda v: v * 20, 0), ("−1", lambda v: v - 1, 1),
         ("×10", lambda v: v * 10, 0), ("+9", lambda v: v + 9, 0)]
NSEG = len(GATES) + 1
Y0, SEG_DY, SLOPE, XL, XR = 700, 380, 110, 200, 880
Z = 1.2
T_START, TS, TD = 2.2, 1.05, .32
GOOD, BAD = (.45, 1, .5), (1, .3, .35)
GOAL = 1_000_000

def seg(k):
    d = 1 if k % 2 == 0 else -1; xs = XL if d > 0 else XR; ys = Y0 + k * SEG_DY
    return d, xs, ys
def seg_t(k): return T_START + k * (TS + TD)
T_GATE = [seg_t(k) + TS / 2 for k in range(len(GATES))]
VAL = [1]
for g in GATES: VAL.append(g[1](VAL[-1]))
LASTK = NSEG - 1
T_ARRIVE = seg_t(LASTK) + TS * .6                       # stops at the vault door
T_COIN0, T_COIN1 = T_ARRIVE + 1.3, T_ARRIVE + 2.6
T_OPEN = T_COIN1 + .05
DUR = T_OPEN + 3.6
VAULT_X = XL + .6 * (XR - XL) if LASTK % 2 == 0 else XR - .6 * (XR - XL)

def ball_pos(t):
    if t < T_START: d, xs, ys = seg(0); return xs, ys
    for k in range(NSEG):
        d, xs, ys = seg(k); t0 = seg_t(k)
        if k == LASTK:
            u = cl((t - t0) / TS); u = min(u, .6) if t < T_ARRIVE else .6
            return xs + d * u * (XR - XL), ys + SLOPE * u
        if t < t0 + TS:
            u = (t - t0) / TS; return xs + d * u * (XR - XL), ys + SLOPE * u
        if t < t0 + TS + TD:
            v = (t - t0 - TS) / TD; return xs + d * (XR - XL) + d * 30 * v, ys + SLOPE + (SEG_DY - SLOPE) * v * v
    return VAULT_X, seg(LASTK)[2] + SLOPE * .6

def value_at(t):
    n = sum(1 for tg in T_GATE if t >= tg); v = VAL[n]
    if t >= T_COIN1: v = GOAL
    return v, n
def shown(t):
    v, n = value_at(t)
    if n == 0: return 1.0
    prev = VAL[n - 1]; tg = T_GATE[n - 1]
    if t >= T_COIN1: prev, tg = VAL[-1], T_COIN1
    u = ease(cl((t - tg) / .45)); return math.exp(lerp(math.log(max(prev, 1)), math.log(max(v, 1)), u))

def cam(t):
    bx, by = ball_pos(t); vy = seg(LASTK)[2] + SLOPE
    if t < 1.2: return vy - 1050
    if t < T_START: return lerp(vy - 1050, seg(0)[2] - 820, ease((t - 1.2) / (T_START - 1.2)))
    return min(by - 820, vy - 1050)

def track(ctx, k):
    d, xs, ys = seg(k); xe = xs + d * (XR - XL); ye = ys + SLOPE
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(xs, ys + 34); ctx.line_to(xe, ye + 34); ctx.set_source_rgba(.4, .3, 1, .35); ctx.set_line_width(26); ctx.stroke()
    ctx.move_to(xs, ys + 30); ctx.line_to(xe, ye + 30); ctx.set_source_rgb(.55, .5, 1); ctx.set_line_width(12); ctx.stroke()

def gate(ctx, k, t):
    lab, _, bad = GATES[k]; d, xs, ys = seg(k); x = 540; y = ys + SLOPE / 2
    col = BAD if bad else GOOD; tg = T_GATE[k]; fl = cl(1 - (t - tg) / .3) if t >= tg else 0
    passed = t >= tg
    ctx.new_path(); rrect(ctx, x - 70, y - 250, 140, 270, 22); ctx.set_source_rgba(*col, (.12 if passed else .22) + .45 * fl); ctx.fill()
    ctx.new_path(); rrect(ctx, x - 70, y - 250, 140, 270, 22); ctx.set_source_rgba(*col, .5 if passed else 1); ctx.set_line_width(7); ctx.stroke()
    s = 1 + .3 * fl
    ctx.save(); ctx.translate(x, y - 180); ctx.scale(s, s); label(ctx, lab, 0, 0, 58 if len(lab) < 4 else 46, col=(1, 1, 1), alpha=.55 if passed else 1, shadow=.6); ctx.restore()
    if 0 <= t - tg < .5:
        r = random.Random(k); u = (t - tg) / .5
        for j in range(16):
            a = r.uniform(0, 6.28); dd = r.uniform(60, 220) * u
            ctx.new_path(); ctx.arc(x + math.cos(a) * dd, y - 80 + math.sin(a) * dd, 7 * (1 - u), 0, 7); ctx.set_source_rgba(*col, 1 - u); ctx.fill()

def vault(ctx, t):
    d, xs, ys = seg(LASTK); x = VAULT_X + d * 190; y = ys + SLOPE * .75
    shake = 0
    if T_ARRIVE < t < T_ARRIVE + .5: shake = 10 * math.sin(t * 90) * (1 - (t - T_ARRIVE) / .5)
    op = ease(cl((t - T_OPEN) / .6))
    ctx.save(); ctx.translate(x + shake, y)
    if op > 0: glow(ctx, 0, -160, 380 * op + 50, (1, .8, .3), .8)
    ctx.new_path(); rrect(ctx, -150, -360, 300, 390, 30); ctx.set_source_rgb(.22, .2, .32); ctx.fill()
    ctx.save(); ctx.translate(-d * 0, 0); ctx.scale(1 - .85 * op, 1)
    ctx.new_path(); rrect(ctx, -125, -335, 250, 340, 24); ctx.set_source_rgb(.45, .45, .58); ctx.fill()
    ctx.new_path(); ctx.arc(0, -165, 70, 0, 7); ctx.set_source_rgb(.3, .3, .42); ctx.fill()
    ctx.save(); ctx.translate(0, -165); ctx.rotate(t * 2 if t > T_COIN1 else 0)
    for a in range(3): ctx.rotate(2.09); ctx.rectangle(-6, -60, 12, 120); ctx.set_source_rgb(.7, .7, .82); ctx.fill()
    ctx.restore(); ctx.restore()
    locked = T_ARRIVE < t < T_OPEN
    tagbox(ctx, "1,000,000", 0, -400, 50, BAD if locked and (t * 4) % 1 < .5 else (1, .8, .25), fg=INK, pointer=True)
    ctx.restore()

def hud(ctx, t):
    v = shown(t)
    ctx.new_path(); rrect(ctx, 140, 215, 800, 46, 23); ctx.set_source_rgba(1, 1, 1, .12); ctx.fill()
    p = cl(math.log10(max(v, 1)) / 6)
    if p > 0: ctx.new_path(); rrect(ctx, 140, 215, max(46, 800 * p), 46, 23); ctx.set_source_rgb(*(GOOD if p < 1 else (1, .8, .25))); ctx.fill()
    label(ctx, "1", 120, 238, 34, col=(1, 1, 1), anchor="r", alpha=.7)
    label(ctx, "1M", 960, 238, 34, col=(1, .8, .25), anchor="l")

def coins(ctx, t):
    if t < T_OPEN: return
    u = t - T_OPEN; r = random.Random(3)
    for k in range(90):
        t0 = r.uniform(0, 1.2)
        if u < t0: continue
        uu = u - t0; x = 540 + r.uniform(-500, 500); y = -60 + r.uniform(0, 200) + 900 * uu * uu + 300 * uu
        ctx.save(); ctx.translate(x, y); ctx.scale(abs(math.cos(uu * 6 + k)) + .15, 1)
        ctx.new_path(); ctx.arc(0, 0, 22, 0, 7); ctx.set_source_rgb(1, .8, .25); ctx.fill(); ctx.new_path(); ctx.arc(0, 0, 14, 0, 7); ctx.set_source_rgb(1, .9, .5); ctx.fill(); ctx.restore()

def draw(ctx, t):
    bg(ctx, (.07, .04, .18), (.02, .02, .08)); cy = cam(t)
    ctx.save(); ctx.translate(0, -cy * .3); stars(ctx, t, 120, 2, ymax=H * 3); ctx.restore()
    ctx.save(); ctx.translate(540, 900); ctx.scale(Z, Z); ctx.translate(-540, -(cy + 900))
    for k in range(NSEG): track(ctx, k)
    vault(ctx, t)
    for k in range(len(GATES)): gate(ctx, k, t)
    bx, by = ball_pos(t); v = shown(t); r = 34 + 7 * math.log10(v + 1)
    if t > T_ARRIVE and t < T_OPEN: bx += 0
    if t >= T_OPEN: bx += 260 * ease(cl((t - T_OPEN) / .8)) * seg(LASTK)[0]; r *= 1 - .7 * ease(cl((t - T_OPEN - .3) / .6))
    glow(ctx, bx, by - r + 30, r * 2.6, (.5, .8, 1), .45)
    ball(ctx, bx, by - r + 30, r, (.45, .75, 1), spec=.8)
    # coin
    if T_COIN0 < t < T_COIN1 + .1:
        d, xs, ys = seg(LASTK); u = cl((t - T_COIN0) / (T_COIN1 - T_COIN0)); cxp = xs + d * u * .6 * (XR - XL) - d * 40; cyp = ys + SLOPE * .6 * u
        ctx.save(); ctx.translate(cxp, cyp + 4); ctx.rotate(u * 20); ctx.new_path(); ctx.arc(0, 0, 20, 0, 7); ctx.set_source_rgb(1, .8, .25); ctx.fill()
        ctx.new_path(); ctx.arc(0, 0, 12, 0, 7); ctx.set_source_rgb(1, .9, .5); ctx.fill(); ctx.restore()
        label(ctx, "+1", cxp, cyp - 50, 44, col=(1, .85, .3))
    # number over ball
    txt = f"{int(round(v)):,}" if t < T_COIN1 or True else ""
    if t < T_OPEN + .5:
        n = value_at(t)[1]; pk_ = popk(cl((t - T_GATE[n - 1]) / .35)) if n else 1
        bad = n and GATES[n - 1][2] and t - T_GATE[n - 1] < 1.0
        ctx.save(); ctx.translate(bx, by - 2 * r - 30); ctx.scale(pk_, pk_)
        label(ctx, txt, 0, 0, 64, col=BAD if bad else (1, 1, 1), shadow=.7); ctx.restore()
    ctx.restore()
    hud(ctx, t)
    if t < 1.3: tagbox(ctx, "NEED 1,000,000", 540, 1300, 64, (1, .8, .25), fg=INK, pointer=False, k=popk(t / .4))
    if T_ARRIVE + .2 < t < T_OPEN: tagbox(ctx, "1 SHORT!", 540, 1300, 74, BAD, pointer=False, k=popk((t - T_ARRIVE - .2) / .35))
    coins(ctx, t)
    if t > T_OPEN:
        u = t - T_OPEN
        if u < .3: ctx.set_source_rgba(1, .9, .6, .45 * (1 - u / .3)); ctx.paint()
        tagbox(ctx, "1,000,000!", 540, 1300, 96, (1, .8, .25), fg=INK, pointer=False, k=popk(u / .45))

# ---------------- audio ----------------
def tone(f0, f1, d, amp, sq=False):
    m = np.arange(int(SR * d)) / SR; f = np.linspace(f0, f1, len(m)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) if not sq else np.tanh(3 * np.sin(ph)) * .6
    return x * np.minimum(1, m / .005) * np.minimum(1, (d - m) / .05) * amp
def audio(path):
    tr = Track(DUR); pad(tr, DUR, .03)
    g = np.random.default_rng(1)
    for k in range(NSEG):                                            # rolling rumble per segment + landing thud
        t0 = seg_t(k); d = TS if k < LASTK else TS * .6
        x = g.normal(0, 1, int(SR * d)); X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[f > 260] = 0
        x = np.fft.irfft(X, len(x)); x = x / np.abs(x).max() * .07 * np.minimum(1, np.arange(len(x)) / 2000); tr.add(x, max(t0, T_START))
        if k: tr.add(tone(90, 40, .18, .25), t0)
    step = 0
    for k, (lab, _, bad) in enumerate(GATES):
        tg = T_GATE[k]
        if bad:
            for j, f in enumerate((330, 311, 294, 262)): tr.add(tone(f, f * .97, .22 if j < 3 else .5, .09, sq=True), tg + j * .2)
        else:
            step += 1; base = 392 * 2 ** (step * 2 / 12)
            for j, m in enumerate((1, 1.26, 1.5, 2)): tr.add(chime(base * m, .05, .8), tg + j * .055)
    tr.add(tone(110, 100, .5, .2, sq=True), T_ARRIVE); tr.add(tone(104, 96, .6, .2, sq=True), T_ARRIVE + .55)
    for j in range(6): tr.add(tone(2000, 2000, .03, .05), T_COIN0 + j * .2)
    tr.add(chime(1568, .08, 1.2), T_COIN1)
    m = np.arange(int(SR * 1.4)) / SR; tr.add(np.sin(2 * np.pi * (70 - 25 * m) * m) * np.exp(-m * 3) * .4, T_OPEN)
    for f in (523, 659, 784, 1046, 1318): tr.add(chime(f, .05, 2.4), T_OPEN + .05)
    for j in range(40): tr.add(chime(2200 + 400 * (j % 5), .02, .3), T_OPEN + .2 + j * .06)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('DUR', round(DUR, 1), VAL, 'arrive', round(T_ARRIVE, 1))
    if len(sys.argv) > 1: main(draw, DUR, audio, 's5_million', sys.argv, strength=.8, thr=.6)
