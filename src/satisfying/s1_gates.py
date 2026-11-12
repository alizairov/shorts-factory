"""SATISFYING: 1 cannon, multiplier gates, glowing brick wall. No voice, no characters."""
import sys
from fx import *
FPSS = 3; DT = 1 / (FPS * FPSS)
COLS, ROWS, BW, BH, BY0 = 18, 16, 60, 34, 360
GA_Y, GB_Y, CAN_Y, CEIL = 1440, 1180, 1720, 330
T_FIRE, T_MEGA = 1.6, 16.0
GATECOL = {2: (.35, .75, 1), 5: (1, .45, .75), 3: (.55, 1, .45), 10: (1, .8, .2)}
HPCOL = {5: (.75, .35, 1), 4: (1, .35, .6), 3: (1, .55, .2), 2: (1, .85, .25), 1: (.5, 1, .45)}
BALLCOL = [(.4, .9, 1), (.35, .75, 1), (1, .45, .75), (.55, 1, .45), (1, .8, .2)]

def gates_at(t):
    """list of (x0, x1, y, mult, colour-index, id)"""
    gs = [(40, 535, GA_Y, 3, 1, 0), (545, 1040, GA_Y, 5, 2, 1)]
    if t < T_MEGA: gs += [(40, 535, GB_Y, 4, 3, 2), (545, 1040, GB_Y, 2, 1, 3)]
    else: gs += [(40, 1040, GB_Y, 20, 4, 4)]
    return gs
def cannon_x(t): return 540 + 400 * math.sin((t - T_FIRE) * 2 * math.pi / 3.6)

# ---------------- simulation ----------------
def simulate(maxT=30.0):
    rng = np.random.default_rng(4)
    hp = np.zeros((ROWS, COLS), int)
    for r in range(ROWS): hp[r] = 12 if r < 4 else 9 if r < 8 else 7 if r < 12 else 5
    HP0 = hp.sum()
    bx = np.zeros(0); by = np.zeros(0); vx = np.zeros(0); vy = np.zeros(0); bc = np.zeros(0, int); fl = np.zeros(0, int)
    F = []; breaks = []; hitlog = []; gatelog = []; shots = []; t_end = None; nextshot = T_FIRE
    n = int(maxT * FPS)
    for fi in range(n):
        hits = 0; gp = {}
        for s in range(FPSS):
            t = (fi * FPSS + s) * DT
            if t >= nextshot and t_end is None:
                rate = 12 if t < T_MEGA else 16
                nextshot += 1 / rate; cx = cannon_x(t)
                bx = np.append(bx, cx); by = np.append(by, CAN_Y - 70); vx = np.append(vx, rng.uniform(-40, 40)); vy = np.append(vy, -1500.)
                bc = np.append(bc, 0); fl = np.append(fl, 0); shots.append(t)
            bx += vx * DT; by += vy * DT
            m = bx < 20; vx[m] = abs(vx[m]); m = bx > 1060; vx[m] = -abs(vx[m]); m = by < CEIL; vy[m] = abs(vy[m])
            # gates
            for (x0, x1, gy, mult, ci, gid) in gates_at(t):
                bit = 1 << gid
                m = (vy < 0) & (by < gy) & (by - vy * DT >= gy) & (bx >= x0) & (bx <= x1) & ((fl & bit) == 0)
                idx = np.nonzero(m)[0]
                if len(idx):
                    fl[idx] |= bit; bc[idx] = ci; gp[gid] = gp.get(gid, 0) + len(idx)
                    k = mult - 1; rep = np.repeat(idx, k)
                    nx = bx[rep] + rng.uniform(-22, 22, len(rep)); nvx = vx[rep] + rng.uniform(-160, 160, len(rep))
                    bx = np.concatenate([bx, nx]); by = np.concatenate([by, by[rep] + rng.uniform(0, 30, len(rep))]); vx = np.concatenate([vx, nvx])
                    vy = np.concatenate([vy, vy[rep] * rng.uniform(.92, 1.05, len(rep))]); bc = np.concatenate([bc, bc[rep]]); fl = np.concatenate([fl, fl[rep]])
            if t > T_MEGA + 1.5 and len(bx):
                rc = np.nonzero(hp.sum(0) > 0)[0]
                if len(rc):
                    tx = rc * BW + BW / 2.0; j = np.abs(bx[:, None] - tx[None, :]).argmin(1)
                    vx += np.clip(tx[j] - bx, -300, 300) * 6 * DT
            # bricks
            c = (bx // BW).astype(int); r = ((by - BY0) // BH).astype(int)
            inside = (r >= 0) & (r < ROWS) & (c >= 0) & (c < COLS)
            kill = np.zeros(len(bx), bool)
            for i in np.nonzero(inside)[0]:
                if hp[r[i], c[i]] > 0:
                    hp[r[i], c[i]] -= 1; kill[i] = True; hits += 1
                    if hp[r[i], c[i]] == 0: breaks.append((t, int(r[i]), int(c[i]), int(bc[i])))
            kill |= (by > 1650) & (vy > 0)
            keep = ~kill; bx, by, vx, vy, bc, fl = bx[keep], by[keep], vx[keep], vy[keep], bc[keep], fl[keep]
            if t_end is None and hp.sum() == 0: t_end = t
        F.append((bx.astype(np.float32).copy(), by.astype(np.float32).copy(), bc.copy(), hp.copy()))
        hitlog.append(hits); gatelog.append(gp)
        if t_end is not None and fi / FPS > t_end + 3.0: break
    return F, HP0, breaks, hitlog, gatelog, shots, t_end

F, HP0, BREAKS, HITS, GATES, SHOTS, T_END = simulate()
DUR = len(F) / FPS
GFLASH = {}
for fi, gp in enumerate(GATES):
    for g in gp: GFLASH.setdefault(g, []).append(fi / FPS)

# ---------------- drawing ----------------
def brick(ctx, x, y, col, a=1.0):
    ctx.new_path(); rrect(ctx, x + 3, y + 3, BW - 6, BH - 6, 7); ctx.set_source_rgba(*[c * .55 for c in col], a); ctx.fill()
    ctx.new_path(); rrect(ctx, x + 3, y + 3, BW - 6, BH - 11, 7); ctx.set_source_rgba(*col, a); ctx.fill()
    ctx.new_path(); rrect(ctx, x + 9, y + 7, BW - 22, 5, 2.5); ctx.set_source_rgba(1, 1, 1, .45 * a); ctx.fill()

def gate(ctx, x0, x1, y, mult, ci, gid, t, k=1.0):
    col = BALLCOL[ci]; fl = 0
    for ft in GFLASH.get(gid, []):
        if 0 <= t - ft < .12: fl = max(fl, 1 - (t - ft) / .12)
    ctx.save(); ctx.translate((x0 + x1) / 2, y); ctx.scale(k, 1); ctx.translate(-(x0 + x1) / 2, -y)
    ctx.new_path(); rrect(ctx, x0, y - 40, x1 - x0, 80, 18); ctx.set_source_rgba(*col, .18 + .25 * fl); ctx.fill()
    ctx.new_path(); rrect(ctx, x0, y - 40, x1 - x0, 80, 18); ctx.set_source_rgba(*col, .95); ctx.set_line_width(6); ctx.stroke()
    for xx in (x0, x1): ctx.new_path(); rrect(ctx, xx - 9, y - 58, 18, 116, 9); ctx.set_source_rgb(*col); ctx.fill()
    label(ctx, f"×{mult}", (x0 + x1) / 2, y + 2, 66, col=(1, 1, 1), shadow=.6)
    ctx.restore()

def counter(ctx, t, hpsum):
    done = hpsum == 0
    ctx.new_path(); rrect(ctx, 300, 205, 480, 110, 55); ctx.set_source_rgba(0, 0, 0, .35); ctx.fill()
    for k in range(3): brick(ctx, 330 + k * 20, 232 + k * -4, HPCOL[[5, 3, 2][k]])
    label(ctx, f"{hpsum:,}", 600, 262, 82, col=(.5, 1, .45) if done else (1, 1, 1), shadow=.4)

def draw(ctx, t):
    fi = min(len(F) - 1, int(t * FPS + 1e-6)); bx, by, bc, hp = F[fi]
    bg(ctx, (.06, .04, .16), (.02, .02, .07))
    # rails / floor glow
    glow(ctx, 540, CAN_Y + 60, 520, (.4, .3, 1), .18)
    # bricks
    for r in range(ROWS):
        for c in range(COLS):
            h = hp[r, c]
            if h > 0: brick(ctx, c * BW, BY0 + r * BH, HPCOL[1 if h <= 2 else 2 if h <= 5 else 3 if h <= 7 else 4 if h <= 9 else 5])
    # breaking fragments
    for (bt, r, c, ci) in BREAKS:
        u = t - bt
        if 0 <= u < .7:
            rr = random.Random(r * 97 + c); x0, y0 = c * BW + BW / 2, BY0 + r * BH + BH / 2; col = HPCOL[5 if r < 4 else 4 if r < 8 else 3 if r < 12 else 2]
            for k in range(6):
                vxx, vyy = rr.uniform(-260, 260), rr.uniform(-320, 60); x = x0 + vxx * u; y = y0 + vyy * u + 900 * u * u; s = 12 * (1 - u / .7)
                ctx.save(); ctx.translate(x, y); ctx.rotate(u * rr.uniform(-9, 9)); ctx.rectangle(-s / 2, -s / 2, s, s); ctx.set_source_rgba(*col, 1 - u / .7); ctx.fill(); ctx.restore()
            if u < .15: glow(ctx, x0, y0, 70, (1, 1, 1), .6 * (1 - u / .15))
    # gates
    for (x0, x1, gy, mult, ci, gid) in gates_at(t):
        k = 1.0 if gid != 4 else popk((t - T_MEGA) / .45)
        gate(ctx, x0, x1, gy, mult, ci, gid, t, k)
    if T_MEGA - .25 < t < T_MEGA + .3: ctx.set_source_rgba(1, .85, .3, .35 * (1 - abs(t - T_MEGA) / .3)); ctx.paint()
    # balls
    for ci in range(5):
        m = bc == ci
        if not m.any(): continue
        ctx.set_source_rgb(*BALLCOL[ci])
        for x, y in zip(bx[m], by[m]): ctx.new_sub_path(); ctx.arc(float(x), float(y), 7, 0, 6.29)
        ctx.fill()
    ctx.set_source_rgba(1, 1, 1, .8)
    for x, y in zip(bx, by): ctx.new_sub_path(); ctx.arc(float(x) - 2, float(y) - 2.4, 2.5, 0, 6.29)
    ctx.fill()
    # cannon
    cx = cannon_x(max(t, T_FIRE)) if T_END is None or t < T_END else cannon_x(T_END)
    rec = 0
    for st in SHOTS:
        if 0 <= t - st < .1: rec = max(rec, 1 - (t - st) / .1)
    ctx.new_path(); rrect(ctx, 60, CAN_Y + 50, 960, 16, 8); ctx.set_source_rgba(.5, .45, 1, .5); ctx.fill()
    ctx.new_path(); rrect(ctx, cx - 26, CAN_Y - 90 + rec * 14, 52, 100, 14); ctx.set_source_rgb(.55, .9, 1); ctx.fill()
    ball(ctx, cx, CAN_Y + 20, 62, (.35, .45, 1), spec=.7)
    if rec > .5: glow(ctx, cx, CAN_Y - 95, 60, (.6, .95, 1), .8 * rec)
    counter(ctx, t, int(hp.sum()))
    if T_END and t > T_END:
        u = t - T_END
        if u < .35: ctx.set_source_rgba(1, 1, 1, .3 * (1 - u / .35)); ctx.paint()
        rr = random.Random(5)
        for k in range(80):
            x = rr.uniform(0, W) + 40 * math.sin(u * 3 + k); y = -40 + rr.uniform(0, 300) + 520 * u
            ctx.save(); ctx.translate(x, y); ctx.rotate(u * rr.uniform(-6, 6)); ctx.rectangle(-9, -5, 18, 10); ctx.set_source_rgb(*BALLCOL[k % 5]); ctx.fill(); ctx.restore()
        tagbox(ctx, "CLEARED!", 540, 640, 110, (.5, 1, .45), fg=INK, pointer=False, k=popk(u / .45))

# ---------------- audio ----------------
def tone(f0, f1, d, amp, wave='sin'):
    m = np.arange(int(SR * d)) / SR; f = np.linspace(f0, f1, len(m)); ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) if wave == 'sin' else np.sign(np.sin(ph)) * .5
    return x * np.exp(-m / (d / 4)) * np.minimum(1, m / .004) * amp
def tick(amp):
    g = np.random.default_rng(); n = int(SR * .025); x = g.normal(0, 1, n); x = np.diff(np.r_[0, x]); return x * np.exp(-np.arange(n) / (SR * .004)) * amp
def audio(path):
    tr = Track(DUR); pad(tr, DUR, .03)
    for st in SHOTS: tr.add(tone(180, 70, .08, .07), st)
    for fi, n in enumerate(HITS):
        if n: tr.add(tick(min(.16, .03 * math.sqrt(n))), fi / FPS)
    mf = {0: 3, 1: 5, 2: 4, 3: 2, 4: 8}
    for fi, gp in enumerate(GATES):
        for g, n in gp.items():
            if fi % 2 == 0 or g == 4: f = 300 + 70 * mf[g]; tr.add(tone(f, f * 1.5, .12, min(.06, .025 * math.sqrt(n))), fi / FPS)
    nb = len(BREAKS); scale = [0, 2, 4, 7, 9]
    last = -1
    for k, (bt, r, c, ci) in enumerate(BREAKS):
        if bt - last < .035: continue
        last = bt; step = int(k / nb * 15); f = 392 * 2 ** ((12 * (step // 5) + scale[step % 5]) / 12)
        tr.add(chime(f, .035, .5), bt)
    if T_END:
        m = np.arange(int(SR * 1.2)) / SR; tr.add(np.sin(2 * np.pi * (60 - 20 * m) * m) * np.exp(-m * 3) * .35, T_END)
        for f in (523, 659, 784, 1046): tr.add(chime(f, .05, 2.2), T_END + .1)
    tr.save(path, DUR)

if __name__ == '__main__':
    print('DUR', round(DUR, 1), 'HP0', HP0, 'T_END', T_END, 'maxballs', max(len(f[0]) for f in F))
    if len(sys.argv) > 1: main(draw, DUR, audio, 's1_gates', sys.argv, strength=.9, thr=.6)
