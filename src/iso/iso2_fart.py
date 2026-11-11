"""ISOMETRIC BLOCKS, voiced: What if farting made you fly? Bus overtake + gas station selling beans."""
import sys, wave, math, random
from iso1_sneeze import Scene, P, person, floor, SKIN, SHIRTS, load, rrect
from fx import *
from common import pluck, note
LINES = ["What if farting could make you fly?", "The average person passes gas about fourteen times a day. Now imagine every single one was a tiny jet engine.",
         "Late for the bus? No problem.", "He didn't just catch it. He overtook it.", "Gas stations would change too. Cars get fuel. People get beans.",
         "So, would you trade your car for a can of beans?"]
DURS = [wave.open(f'vo2/c{i}.wav').getnframes() / 44100 for i in range(6)]
GAP = {0: 1.3, 2: 1.9}
T0 = []; t = .25
for i, d in enumerate(DURS): T0.append(t); t += d + GAP.get(i, .35)
DUR = t + 1.4
WORDS = []
for li, (s, t0, d) in enumerate(zip(LINES, T0, DURS)):
    ws = s.split(); wt = [len(w) + 2 + (4 if w[-1] in '.?,' else 0) for w in ws]; tot = sum(wt); acc = 0
    for w, k in zip(ws, wt): WORDS.append((t0 + d * acc / tot, t0 + d * (acc + k) / tot, w, li)); acc += k
def when(word, line):
    for a, b, w, li in WORDS:
        if li == line and w.strip('.,?').lower() == word: return a
T_F0 = T0[0] + DURS[0] + .15                      # hook fart
T_JET = when("jet", 1)
T_BUS = T0[2] - .3
T_LAUNCH = T0[2] + DURS[2] + .25
T_GAS = T0[4] - .3
GREEN = (.75, .95, .55)
ME = (.95, .35, .45)

def puffs(ctx, pts):
    for (x, y, r, a) in pts:
        ctx.new_path(); ctx.arc(x, y, r, 0, 7); ctx.set_source_rgba(*GREEN, a); ctx.fill()
        ctx.new_path(); ctx.arc(x - r * .3, y - r * .3, r * .45, 0, 7); ctx.set_source_rgba(1, 1, 1, a * .5); ctx.fill()

def fart_cloud(ctx, x, y, t, ts, size=1.0, dur=1.2):
    u = (t - ts) / dur
    if 0 < u < 1:
        r = random.Random(int(ts * 10)); pts = []
        for k in range(12):
            a = r.uniform(2.2, 4.0); d = r.uniform(30, 140) * size * (.3 + u)
            pts.append((x + math.cos(a) * d, y + math.sin(a) * d * .6 + 30 * size, r.uniform(18, 40) * size * (.5 + u), .75 * (1 - u)))
        puffs(ctx, pts)
        ctx.save(); ctx.translate(x - 90 * size, y - 40 * size); ctx.rotate(-.2); s = popk(u * 1.6) * size; ctx.scale(s, s)
        tagbox(ctx, "PFFFT!", 0, 0, 58, GREEN, fg=INK, a=1 - cl((u - .6) / .4), pointer=False); ctx.restore()

def captions(ctx, t):
    cur = None
    for i, (a, b, w, li) in enumerate(WORDS):
        if a - .05 <= t < b + .15: cur = i
    if cur is None: return
    li = WORDS[cur][3]; idxs = [i for i, x in enumerate(WORDS) if x[3] == li]; pos = idxs.index(cur)
    start = idxs[(pos // 3) * 3]; chunk = [i for i in idxs if start <= i < start + 3]
    ctx.select_font_face("Inter Display Black"); fs = 74; ctx.set_font_size(fs); sp = 30
    widths = [ctx.text_extents(WORDS[i][2].upper()).x_advance * 1.08 for i in chunk]
    tot = sum(widths) + sp * (len(chunk) - 1); s0 = min(1, 960 / tot); widths = [w * s0 for w in widths]; sp *= s0; fs = int(fs * s0); x = 540 - tot * s0 / 2
    ctx.new_path(); rrect(ctx, 540 - tot * s0 / 2 - 30, 1430, tot * s0 + 60, 100, 26); ctx.set_source_rgba(.08, .05, .16, .55); ctx.fill()
    for i, wd in zip(chunk, widths):
        act = i == cur; ctx.save(); ctx.translate(x + wd / 2, 1500); ctx.scale(1.12 if act else 1, 1.12 if act else 1)
        label(ctx, WORDS[i][2].upper(), 0, 0, fs, col=(1, .85, .2) if act else (1, 1, 1), shadow=1.0); ctx.restore(); x += wd + sp

# ---------------- scenes ----------------
def hook_z(t):
    if t < T_F0: return 0
    u = t - T_F0; return max(0, 2.2 * u - 2.6 * u * u) * 1.6 if u < 1.2 else 0

def scene_stand(t):
    sc = Scene(); floor(sc, -3, -3, 6, 6, (.93, .9, .98), (.86, .84, .96))
    z = hook_z(t)
    if t > T_JET: z = .35 + .12 * math.sin((t - T_JET) * 6)
    person(sc, 0, 0, ME, z0=z); return sc, z

BUS_V, ME_V = 3.0, 10.0
def bus_x(t): return -1.0 + BUS_V * max(0, t - T_BUS - .4)
def me_pos(t):
    u = t - T_BUS
    if t < T_LAUNCH: return -5.5 + 2.2 * u, 3.0, .12 * abs(math.sin(u * 9))       # running on the sidewalk
    v = t - T_LAUNCH; x0 = -5.5 + 2.2 * (T_LAUNCH - T_BUS)
    return x0 + 5.5 * v + 3 * (1 - math.exp(-2 * v)), 3.0 - min(1.6, v * 3), min(1.8, v * 4)
def scene_bus(t):
    sc = Scene()
    for i in range(-10, 40):
        sc.box(i, -2.6, -.2, 1, 1.2, .25, (.86, .86, .9)); sc.box(i, 2.6, -.2, 1, 1.4, .25, (.86, .86, .9)); sc.box(i, -1.4, -.3, 1, 4.0, .2, (.32, .33, .40))
        if i % 2 == 0: sc.box(i + .2, .55, -.1, .6, .12, .02, (1, 1, 1))
        if i % 4 == 0: sc.box(i, -4.6, 0, 2.6, 1.8, 2.5 + (i * 37 % 5), [(.55, .5, .9), (.95, .6, .7), (.5, .8, .9), (1, .8, .5)][(i // 4) % 4])
    sc.box(-.5, 3.3, 0, .15, .15, 2.2, (.3, .3, .35)); sc.box(-.9, 3.3, 2.2, 1.0, .15, .6, (.2, .5, 1))           # bus stop sign
    bx = bus_x(t)
    sc.box(bx, .9, .25, 4.6, 1.4, 1.7, (1, .75, .2))
    for k in range(4): sc.box(bx + .4 + k * 1.05, 2.29, 1.05, .8, .02, .55, (.65, .85, 1))
    for wx in (.5, 3.5): sc.box(bx + wx, .95, 0, .6, 1.3, .3, (.15, .15, .2))
    x, y, z = me_pos(t); person(sc, x, y, ME, z0=z)
    return sc

def scene_gas(t):
    sc = Scene(); floor(sc, -4, -3, 9, 7, (.88, .88, .92), (.82, .82, .88))
    for px in (-3.6, 3.6):
        for py in (-2.6, 2.6): sc.box(px, py, 0, .3, .3, 3.2, (.95, .95, .98))
    sc.box(-3.9, -2.9, 3.2, 7.9, 6.1, .3, (.95, .3, .35), .45)
    pumps = [(-2.2, -.5, (.3, .6, 1), "FUEL"), (.3, -.5, (.3, .6, 1), "FUEL"), (2.8, -.5, (.55, .35, .2), "BEANS")]
    for x, y, col, _ in pumps: sc.box(x, y, 0, .7, .5, 1.5, col); sc.box(x + .1, y + .5, .9, .5, .02, .35, (.9, 1, .9))
    for k, (x, col) in enumerate([(-2.6, (.4, .85, .55)), (-.1, (1, .45, .4))]):
        sc.box(x, .5, .2, 1.4, 2.4, .5, col); sc.box(x + .05, .7, 0, 1.3, .4, .22, (.15, .15, .2)); sc.box(x + .05, 2.3, 0, 1.3, .4, .22, (.15, .15, .2)); sc.box(x + .1, 1.0, .7, 1.2, 1.1, .4, (.75, .9, 1), .7)
    q = [(2.9, .6), (2.9, 1.5), (2.9, 2.4), (2.9, 3.3)]
    for k, (x, y) in enumerate(q):
        if k < 1 + int((t - T_GAS) * 1.2): person(sc, x, y, SHIRTS[k % 5])
        return sc

def bgp(ctx, a, b): bg(ctx, a, b)

def cam(ctx, cx, cy, cz, z, fy=1000):
    ctx.translate(540, fy); ctx.scale(z, z); px, py = P(cx, cy, cz); ctx.translate(-px, -py)

def draw(ctx, t):
    if t < T_BUS:
        bgp(ctx, (.98, .88, .80), (.82, .86, 1.0))
        sc, z = scene_stand(t)
        zoom = 1.9 if t < T0[1] else lerp(1.9, 1.5, ease((t - T0[1]) / 1.0))
        ctx.save(); cam(ctx, .3, .3, 1.2, zoom); sc.draw(ctx)
        bx, by = P(.3, .7, z + .6)
        fart_cloud(ctx, bx - 20, by, t, T_F0, .9)
        if t > T_JET:                                                    # tiny jet exhaust
            r = random.Random(int(t * 30)); pts = [(bx - 10 + r.uniform(-14, 14), by + 40 + k * 22 + r.uniform(0, 8), 12 + k * 4, .55 - k * .08) for k in range(6)]
            puffs(ctx, pts)
        ctx.restore()
        if T0[1] < t < T_BUS:                                            # fact panel
            a = cl((t - T0[1] - .6) / .3)
            n = min(14, int(max(0, t - T0[1] - .6) / 2.2 * 14))
            ctx.new_path(); rrect(ctx, 120, 360, 840, 330, 40); ctx.set_source_rgba(1, 1, 1, .82 * a); ctx.fill()
            for k in range(14):
                cx, cy = 200 + (k % 7) * 113, 455 + (k // 7) * 100
                if k < n: puffs(ctx, [(cx, cy, 34 * popk(cl((t - T0[1] - .6 - k * 2.2 / 14) / .3)), .9 * a)])
                else: ctx.new_path(); ctx.arc(cx, cy, 30, 0, 7); ctx.set_source_rgba(.8, .8, .85, .5 * a); ctx.set_line_width(4); ctx.stroke()
            label(ctx, f"{n}× A DAY", 540, 660, 64, col=INK, alpha=a, shadow=0)
            if t > T_JET: tagbox(ctx, "≈ 0.5–1.5 L OF GAS / DAY", 540, 780, 46, GREEN, fg=INK, pointer=False, k=popk((t - T_JET) / .4))
        if t < T0[1]: tagbox(ctx, "FART = FLIGHT?", 540, 340, 78, GREEN, fg=INK, pointer=False, k=popk(t / .4))
    elif t < T_GAS:
        bgp(ctx, (.80, .90, 1.0), (.98, .88, .80))
        x, y, z = me_pos(t)
        cx = lerp(bus_x(t) + 1.5, x, ease((t - T_BUS) / 1.0) * .7) if t < T_LAUNCH else lerp(x - 1.5, (x + bus_x(t) + 2.3) / 2, ease((t - T_LAUNCH) / .6))
        zoom = 1.25 if t < T_LAUNCH else lerp(1.25, .95, ease((t - T_LAUNCH) / .8))
        ctx.save(); cam(ctx, cx, 1.8, .6, zoom)
        if t > T_LAUNCH:                                                  # speed lines + trail
            for k in range(8):
                lx, ly = P(x - 1 - k * .9, y + .3, z + .3 + (k % 3) * .4)
                ctx.set_source_rgba(1, 1, 1, .7 - k * .07); ctx.set_line_width(5); ctx.move_to(lx, ly); ctx.line_to(lx - 80, ly + 46); ctx.stroke()
        scene_bus(t).draw(ctx)
        if t > T_LAUNCH:
            r = random.Random(7); pts = []
            for k in range(14):
                tx, ty = P(x - .4 - k * .55, y + .4, z + .5 + r.uniform(-.2, .2)); pts.append((tx, ty, 16 + k * 3, max(0, .7 - k * .05)))
            puffs(ctx, pts)
        bx, by = P(x + .2, y + .5, z + .6); fart_cloud(ctx, bx, by, t, T_LAUNCH, 1.4, 1.0)
        ctx.restore()
        if T_LAUNCH + .1 < t < T_LAUNCH + 1.8:
            mph = int(min(60, (t - T_LAUNCH) * 70))
            tagbox(ctx, f"{mph} MPH", 540, 360, 72, (1, 1, 1), fg=INK, pointer=False)
        if t > when("overtook", 3): tagbox(ctx, "OVERTAKEN!", 540, 360, 76, (1, .75, .2), fg=INK, pointer=False, k=popk((t - when("overtook", 3)) / .4))
        if t < T0[2] + 1.4: tagbox(ctx, "BUS STOP", 540, 360, 60, (.2, .5, 1), pointer=False)
    else:
        bgp(ctx, (.98, .90, .82), (.85, .88, 1.0))
        zoom = lerp(1.55, 1.35, ease((t - T_GAS) / 3))
        ctx.save(); cam(ctx, .6, 1.0, 1.0, zoom); scene_gas(t).draw(ctx)
        for (px, py, txt, col, tw) in [(-1.85, -.25, "FUEL", (.3, .6, 1), when("fuel", 4)), (.65, -.25, "FUEL", (.3, .6, 1), when("fuel", 4)), (3.15, -.25, "BEANS", (.55, .35, .2), when("beans", 4))]:
            lx, ly = P(px, py, 2.4)
            if t > tw: tagbox(ctx, txt, lx, ly, 40, col, pointer=True, k=popk((t - tw) / .35))
        ctx.restore()
        ctx.new_path(); rrect(ctx, 300, 470, 480, 90, 20); ctx.set_source_rgb(.15, .15, .2); ctx.fill()
        label(ctx, "FUEL $3.49   BEANS $0.99", 540, 515, 40, col=(1, .85, .3), shadow=0)
        if t > T0[5] + .3:
            a = cl((t - T0[5] - .3) / .25)
            tagbox(ctx, "CAR OR BEANS?", 540, 360, 66, (1, 1, 1), fg=INK, a=a, k=popk((t - T0[5] - .3) / .4), pointer=False)
    w = max(1 - abs(t - T_BUS) / .25, 1 - abs(t - T_GAS) / .25)
    if w > 0: ctx.set_source_rgba(1, 1, 1, w * .9); ctx.paint()
    captions(ctx, t)
    ctx.new_path(); rrect(ctx, 52, 74, 420, 112, 56); ctx.set_source_rgba(.1, .07, .2, .55); ctx.fill()

# ---------------- audio ----------------
def fart(dur=.7, f0=95, amp=.35, seed=1):
    g = np.random.default_rng(seed); n = int(SR * dur); m = np.arange(n) / SR
    f = f0 * (1 + .25 * np.sin(2 * np.pi * 7 * m)) * (1 + .15 * g.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)) * .02)
    ph = 2 * np.pi * np.cumsum(f) / SR; saw = (ph / np.pi) % 2 - 1
    flap = .6 + .4 * np.sign(np.sin(2 * np.pi * 23 * m))
    env = np.minimum(1, m / .02) * np.minimum(1, (dur - m) / .12)
    return np.tanh(saw * flap * 2.5) * env * amp * .5
def jet(dur, amp):
    g = np.random.default_rng(3); x = g.normal(0, 1, int(SR * dur)); X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < 300) | (f > 3000)] = 0
    x = np.fft.irfft(X, len(x)); m = np.arange(len(x)) / len(x); return x / np.abs(x).max() * np.sin(np.pi * m) * amp
def audio(path):
    tr = Track(DUR)
    k = 0; beat = 60 / 112
    while k * beat < DUR - 1:
        tt = k * beat; tr.add(pluck(note([0, 4, 7, 9, 7, 4, 2, 4][k % 8], 330), .3, .04, 8), tt)
        if k % 2 == 0: tr.add(pluck(note([0, 5, 3, 4][(k // 8) % 4], 82), .5, .05, 4), tt)
        k += 1
    for i in range(6): tr.add(load(f'vo2/c{i}.wav'), T0[i])
    tr.add(fart(.55, 110, .32, 1), T_F0 - .05)
    for k in range(6): tr.add(fart(.12, 160 + k * 8, .12, k + 3), T_JET + k * .5)
    for k in range(14): tr.add(pop(.04), T0[1] + .6 + k * 2.2 / 14)
    m = np.arange(int(SR * (T_GAS - T_BUS))) / SR; tr.add(np.sin(2 * np.pi * 55 * m) * .03 * (1 + .3 * np.sin(2 * np.pi * 3 * m)), T_BUS)
    tr.add(fart(1.1, 75, .42, 9), T_LAUNCH - .05); tr.add(jet(1.6, .12), T_LAUNCH + .1); tr.add(pk.whoosh(1.0, .1), T_LAUNCH + .3)
    m = np.arange(int(SR * .4)) / SR; honk = (np.sign(np.sin(2 * np.pi * 300 * m)) + np.sign(np.sin(2 * np.pi * 380 * m))) * .05 * np.minimum(1, (len(m) - np.arange(len(m))) / 800)
    tr.add(honk, when("overtook", 3) + .2); tr.add(pop(.1), when("overtook", 3))
    tr.add(pk.whoosh(.8, .08), T_GAS - .3); tr.add(chime(880, .05, 1.0), when("fuel", 4)); tr.add(chime(1175, .06, 1.2), when("beans", 4)); tr.add(fart(.25, 140, .12, 4), when("beans", 4) + .5)
    tr.add(pop(.1), T0[5] + .3); tr.add(chime(1046, .05, 1.6), T0[5] + .7)
    tr.save(path, DUR)

if __name__ == '__main__': main(draw, DUR, audio, 'iso2_fart', sys.argv, strength=.25, thr=.85)
