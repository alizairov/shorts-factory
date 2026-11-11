"""ISOMETRIC BLOCKS, voiced: What if sneezing made you invisible for one second? Group photo + busy street."""
import sys, wave, math, random
sys.path.insert(0, '/home/claude/glow')
from fx import *
from common import pluck, note
LINES = ["What if every time you sneezed, your body turned invisible for one second?", "Sounds harmless. Until the group photo.", "Three, two, one...",
         "Congratulations. You're now a floating shirt with no head. Forever.", "Now picture a busy street.",
         "One driver sneezes, and for one second, a car drives itself.", "And in pollen season, the whole city starts to flicker.", "Would you still go outside in spring?"]
DURS = [wave.open(f'vo/c{i}.wav').getnframes() / 44100 for i in range(8)]
T0 = []; t = .25
for i, d in enumerate(DURS):
    T0.append(t); t += d + (.35 if i not in (2, 3) else (1.5 if i == 2 else .6))
DUR = t + 1.6
WORDS = []
for li, (s, t0, d) in enumerate(zip(LINES, T0, DURS)):
    ws = s.split(); wt = [len(w) + 2 + (4 if w[-1] in '.?,' else 0) for w in ws]; tot = sum(wt); acc = 0
    for w, k in zip(ws, wt): WORDS.append((t0 + d * acc / tot, t0 + d * (acc + k) / tot, w, li)); acc += k
def when(word, line):
    for a, b, w, li in WORDS:
        if li == line and w.strip('.,?').lower() == word: return a
T_DEMO = T0[0] + DURS[0] * .55                     # first sneeze demo (the middle person)
T_SNEEZE = T0[2] + DURS[2] + .25                   # the photo sneeze
T_SHOT = T_SNEEZE + .35
T_STREET = T0[4] - .3
T_CAR = when("sneezes", 5)
T_POLLEN = T0[6]
SKIN, HAIR = (1.0, .78, .62), (.30, .20, .16)
SHIRTS = [(.95, .35, .45), (.30, .65, 1.0), (1.0, .78, .25), (.45, .85, .55), (.65, .45, 1.0)]
PANTS = (.25, .28, .45)

# ---------------- isometric engine ----------------
S = 78
def P(x, y, z): return ((x - y) * .866 * S, (x + y) * .5 * S - z * S)
def shade(c, f): return tuple(min(1, v * f) for v in c)
class Scene:
    def __init__(self): self.b = []
    def box(self, x, y, z, w, d, h, col, a=1.0, dash=False):
        if a > .01 or dash: self.b.append((x + w / 2 + y + d / 2 + z * .02, x, y, z, w, d, h, col, a, dash))
    def draw(self, ctx):
        for _, x, y, z, w, d, h, col, a, dash in sorted(self.b, key=lambda q: q[0]):
            faces = [([(x, y, z + h), (x + w, y, z + h), (x + w, y + d, z + h), (x, y + d, z + h)], 1.0),
                     ([(x, y + d, z), (x + w, y + d, z), (x + w, y + d, z + h), (x, y + d, z + h)], .80),
                     ([(x + w, y, z), (x + w, y + d, z), (x + w, y + d, z + h), (x + w, y, z + h)], .62)]
            for pts, f in faces:
                ctx.new_path(); q = [P(*p) for p in pts]; ctx.move_to(*q[0]); [ctx.line_to(*p) for p in q[1:]]; ctx.close_path()
                if a > .01: ctx.set_source_rgba(*shade(col, f), a); ctx.fill_preserve()
                if dash:
                    ctx.set_source_rgba(1, 1, 1, .55 * (1 - a)); ctx.set_line_width(2.5); ctx.set_dash([7, 6]); ctx.stroke(); ctx.set_dash([])
                else: ctx.new_path()

def person(sc, x, y, shirt, vis=1.0, arm=0.0, z0=0.0, legs=True):
    """vis: 1 = visible, 0 = invisible body (clothes stay, skin/hair vanish, dashed outline)"""
    inv = vis < .99
    if legs:
        for dy in (0, .32):
            sc.box(x + .1, y + dy + .05, z0, .42, .26, .14, (.15, .15, .2))
            sc.box(x + .12, y + dy + .06, z0 + .14, .38, .24, .82, PANTS)
    sc.box(x, y, z0 + .96, .62, .66, .86, shirt)
    for dy, up in ((-.24, arm), (.66, 0)):
        sc.box(x + .14, y + dy, z0 + 1.3 - up * .2, .32, .24, .52, shirt)
        sc.box(x + .16, y + dy + .02, z0 + .96 - up * .2, .28, .2, .34, SKIN, vis, dash=inv)
    sc.box(x + .06, y + .08, z0 + 1.86, .5, .5, .5, SKIN, vis, dash=inv)
    sc.box(x + .02, y + .04, z0 + 2.3, .58, .58, .14, HAIR, vis, dash=inv)

def vis_at(t, ts, dur=1.0):
    """invisible for `dur` seconds starting at ts, with a quick fade"""
    if t < ts or t > ts + dur + .15: return 1.0
    return 1 - cl((t - ts) / .08) * (1 - cl((t - ts - dur) / .15))

def sneeze_fx(ctx, x, y, t, ts, sc_):
    u = (t - ts) / .7
    if 0 < u < 1:
        r = random.Random(int(ts * 100))
        for k in range(26):
            a = r.uniform(-1.1, .5); sp = r.uniform(80, 260) * sc_
            px, py = x + math.cos(a) * sp * u, y + math.sin(a) * sp * u + 120 * u * u * sc_
            ctx.set_source_rgba(.8, .95, 1, (1 - u) * .9); ctx.new_path(); ctx.arc(px, py, (3 + 5 * r.random()) * sc_, 0, 7); ctx.fill()
        ctx.save(); ctx.translate(x + 40 * sc_, y - 90 * sc_); ctx.rotate(-.15); s = popk(u * 1.4) * sc_; ctx.scale(s, s)
        tagbox(ctx, "ACHOO!", 0, 0, 64, (1, 1, 1), fg=(.9, .2, .4), a=1 - cl((u - .7) / .3), pointer=False); ctx.restore()

def floor(sc, x0, y0, nx, ny, c1, c2):
    for i in range(nx):
        for j in range(ny): sc.box(x0 + i, y0 + j, -.2, 1, 1, .2, c1 if (i + j) % 2 else c2)

# ---------------- scene A: the group photo ----------------
GROUP = [(-.2, -2.2), (-.2, -1.1), (-.2, 0.0), (-.2, 1.1), (-.2, 2.2)]
def scene_group(t, photo=False):
    sc = Scene(); floor(sc, -3, -4, 7, 9, (.93, .9, .98), (.86, .84, .96))
    sc.box(-2.8, -4.0, 0, 1.2, 9, 3.2, (.75, .7, .95))                     # back wall
    for k, (x, y) in enumerate(GROUP):
        v = 1.0
        if k == 2: v = vis_at(t, T_DEMO) if not photo else 0.0
        if k == 2 and not photo and T_SNEEZE <= t: v = vis_at(t, T_SNEEZE)
        person(sc, x, y, SHIRTS[k], v, arm=.6 if k in (0, 4) else 0)
    if not photo:                                                            # tripod camera
        cx, cy = 3.2, 0.1
        for dy in (-.3, .4): sc.box(cx + .3, cy + dy, 0, .08, .08, 1.3, (.25, .25, .3))
        sc.box(cx, cy - .3, 1.3, .7, .9, .55, (.2, .2, .26)); sc.box(cx - .15, cy + .05, 1.42, .2, .3, .3, (.35, .6, 1))
    return sc

# ---------------- scene B: the street ----------------
_rr = random.Random(5)
PEDS = [(_rr.uniform(-6, 6), _rr.choice([-2.6, -2.0, 3.0, 3.6]), _rr.choice([-1, 1]) * _rr.uniform(.6, 1.1), k) for k in range(14)]
DX0 = -.4 - 2.6 * (T_CAR - T_STREET)
CARS = [(DX0 - 5.5, .2, 2.6, (1, .35, .35)), (DX0, .2, 2.6, (.3, .6, 1)), (2.0, 1.4, -2.2, (1, .8, .25)), (-4.5, 1.4, -2.2, (.4, .85, .55))]
def scene_street(t):
    sc = Scene(); u = t - T_STREET
    for i in range(-8, 9):
        sc.box(i, -3.2, -.2, 1, 1.6, .25, (.86, .86, .9)); sc.box(i, 2.8, -.2, 1, 1.6, .25, (.86, .86, .9))
        sc.box(i, -1.6, -.3, 1, 4.4, .2, (.32, .33, .40))
        if i % 2 == 0: sc.box(i + .2, .55, -.1, .6, .12, .02, (1, 1, 1))
    for i, (h, col) in enumerate([(4, (.55, .5, .9)), (6, (.95, .6, .7)), (3.5, (.5, .8, .9)), (5, (1, .8, .5)), (4.5, (.6, .85, .6))]):
        sc.box(-8 + i * 3.2, -6.2, 0, 2.6, 2.6, h, col)
        for wy in range(int(h) - 1): sc.box(-8 + i * 3.2 + .4, -3.62, .8 + wy, .5, .02, .5, (1, 1, .85))
    for x0, y0, v, col in CARS:
        x = (x0 + v * u + 8) % 16 - 8; drv = x0 == DX0
        dv = vis_at(t, T_CAR) if drv else 1.0
        if u > T_POLLEN - T_STREET and not drv: dv = 0 if math.sin(t * 11 + x0 * 3) > .55 else 1
        sc.box(x, y0, .2, 2.2, 1.0, .5, col); sc.box(x + .05, y0 + .05, 0, .4, .9, .22, (.15, .15, .2)); sc.box(x + 1.6, y0 + .05, 0, .4, .9, .22, (.15, .15, .2))
        sc.box(x + 1.5, y0 + .1, .7, .1, .8, .35, (.75, .9, 1), .6)
        person(sc, x + .55, y0 + .18, SHIRTS[(int(x0) + 7) % 5], dv, z0=-.2, legs=False)
    for x0, y0, v, k in PEDS:
        x = (x0 + v * u * .7 + 8) % 16 - 8
        pv = 1.0
        if u > T_POLLEN - T_STREET: pv = 0 if math.sin(t * (7 + k) + k * 2.1) > .6 else 1
        person(sc, x, y0, SHIRTS[k % 5], pv)
    return sc

def bgp(ctx, a, b): bg(ctx, a, b)

def captions(ctx, t):
    cur = None
    for i, (a, b, w, li) in enumerate(WORDS):
        if a - .05 <= t < b + .15: cur = i
    if cur is None or WORDS[cur][3] == 2: return
    li = WORDS[cur][3]; idxs = [i for i, x in enumerate(WORDS) if x[3] == li]; pos = idxs.index(cur)
    start = idxs[(pos // 3) * 3]; chunk = [i for i in idxs if start <= i < start + 3]
    ctx.select_font_face("Inter Display Black"); fs = 74; ctx.set_font_size(fs); sp = 30
    widths = [ctx.text_extents(WORDS[i][2].upper()).x_advance * 1.08 for i in chunk]
    tot = sum(widths) + sp * (len(chunk) - 1); s0 = min(1, 960 / tot); widths = [w * s0 for w in widths]; sp *= s0; fs = int(fs * s0); x = 540 - tot * s0 / 2
    ctx.new_path(); rrect(ctx, 540 - tot * s0 / 2 - 30, 1430, tot * s0 + 60, 100, 26); ctx.set_source_rgba(.08, .05, .16, .55); ctx.fill()
    for i, wd in zip(chunk, widths):
        act = i == cur; ctx.save(); ctx.translate(x + wd / 2, 1500); ctx.scale(1.12 if act else 1, 1.12 if act else 1)
        label(ctx, WORDS[i][2].upper(), 0, 0, fs, col=(1, .85, .2) if act else (1, 1, 1), shadow=1.0); ctx.restore(); x += wd + sp

def draw(ctx, t):
    if t < T_STREET:
        bgp(ctx, (.98, .86, .9), (.80, .82, 1.0))
        # camera: close on "you" during the demo, pull back for the photo
        z = lerp(2.3, 1.35, ease((t - T0[1]) / 1.0)); fy = lerp(-160, 0, ease((t - T0[1]) / 1.0))
        ctx.save(); ctx.translate(540, 1000 - fy); ctx.scale(z, z); ctx.translate(-P(-.2, 0, 1.2)[0], -P(-.2, 0, 1.2)[1])
        scene_group(t).draw(ctx)
        hx, hy = P(-.2 + .3, 0 + .3, 2.2)
        for ts in (T_DEMO, T_SNEEZE): sneeze_fx(ctx, hx, hy, t, ts - .05, 1 / z)
        ctx.restore()
        if T_DEMO + .1 < t < T_DEMO + 1.0: tagbox(ctx, "1 SECOND", 540, 640, 64, (1, 1, 1), fg=INK, pointer=False, k=popk((t - T_DEMO - .1) / .35))
        for k, word in enumerate(["3", "2", "1"]):
            ts = T0[2] + DURS[2] * k / 3
            if ts < t < ts + DURS[2] / 3: label(ctx, word, 540, 700, int(240 * popk((t - ts) / .3)), col=(1, 1, 1), shadow=.6)
        # flash + polaroid
        if T_SHOT < t:
            f = 1 - cl((t - T_SHOT) / .35); ctx.set_source_rgba(1, 1, 1, f); ctx.paint()
            k = ease((t - T_SHOT - .1) / .5); ang = lerp(.6, -.06, k)
            ctx.save(); ctx.translate(540, lerp(1900, 1020, k)); ctx.rotate(ang)
            ctx.set_source_rgba(0, 0, 0, .25); rrect(ctx, -380, -420, 780, 900, 18); ctx.fill()
            ctx.set_source_rgb(1, 1, .98); rrect(ctx, -390, -440, 780, 900, 18); ctx.fill()
            ctx.save(); ctx.rectangle(-350, -400, 700, 700); ctx.clip()
            g = cairo.LinearGradient(0, -400, 0, 300); g.add_color_stop_rgb(0, .98, .86, .9); g.add_color_stop_rgb(1, .8, .82, 1); ctx.set_source(g); ctx.paint()
            ctx.translate(0, 40); ctx.scale(1.55, 1.55); ctx.translate(-P(-.2, 0, 1.2)[0], -P(-.2, 0, 1.2)[1]); scene_group(t, photo=True).draw(ctx); ctx.restore()
            label(ctx, "class photo 2026", 0, 395, 46, col=(.3, .3, .4), shadow=0)
            if t > T0[3] + DURS[3] * .8:
                ctx.save(); ctx.translate(230, -330); ctx.rotate(.25); s = popk((t - T0[3] - DURS[3] * .8) / .35); ctx.scale(s, s)
                tagbox(ctx, "FOREVER", 0, 0, 58, (1, .3, .4), pointer=False); ctx.restore()
            ctx.restore()
    else:
        bgp(ctx, (.80, .90, 1.0), (.98, .88, .80))
        z = lerp(1.25, .95, ease((t - T_STREET) / 3)) * (1 + .35 * ease((t - T_CAR + .8) / .6) * (1 - ease((t - T_CAR - 1.6) / .6)))
        fk = ease((t - T_CAR + .8) / .6) * (1 - ease((t - T_CAR - 1.6) / .6)); cxw = lerp(0, (DX0 + 2.6 * (t - T_STREET) + 8) % 16 - 8 + 1, fk)
        ctx.save(); ctx.translate(540, 1000); ctx.scale(z, z); ctx.translate(-P(cxw, .6, 0)[0], -P(cxw, .6, 0)[1])
        scene_street(t).draw(ctx)
        u = t - T_STREET; x = (DX0 + 2.6 * u + 8) % 16 - 8; hx, hy = P(x + .85, .5, 1.9); sneeze_fx(ctx, hx, hy, t, T_CAR - .05, 1 / z)
        if t > T_POLLEN:                                                    # pollen
            r = random.Random(3)
            for k in range(70):
                px, py = r.uniform(-900, 900), r.uniform(-900, 500); py += 40 * math.sin(t * 1.3 + k); px += 30 * t * r.uniform(.5, 1.5)
                ctx.set_source_rgba(1, .9, .3, .75 * cl((t - T_POLLEN) / .5)); ctx.new_path(); ctx.arc((px + 900) % 1800 - 900, py, 5 / z, 0, 7); ctx.fill()
        ctx.restore()
        if T_CAR + .2 < t < T_CAR + 1.4: tagbox(ctx, "NO DRIVER?!", 540, 330, 70, (1, .3, .4), pointer=False, k=popk((t - T_CAR - .2) / .35))
        if t > T0[7] + .2:
            a = cl((t - T0[7] - .2) / .25)
            tagbox(ctx, "WOULD YOU GO OUTSIDE?", 540, 560, 64, (1, 1, 1), fg=INK, a=a, k=popk((t - T0[7] - .2) / .4), pointer=False)
            tagbox(ctx, "YES 🙂   /   NO 🤧", 540, 680, 54, (1, .85, .2), fg=INK, a=cl((t - T0[7] - .6) / .25), pointer=False)
    # whoosh transition between scenes
    w = 1 - abs(t - T_STREET) / .3
    if w > 0: ctx.set_source_rgba(1, 1, 1, w * .9); ctx.paint()
    if t < T_DEMO - .2: tagbox(ctx, "SNEEZE = INVISIBLE?", 540, 330, 70, (1, .3, .4), pointer=False, k=popk(t / .4))
    captions(ctx, t)
    ctx.new_path(); rrect(ctx, 52, 74, 420, 112, 56); ctx.set_source_rgba(.1, .07, .2, .55); ctx.fill()

def load(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
def achoo(amp=.35):
    g = np.random.default_rng(4); n1, n2 = int(SR * .35), int(SR * .35)
    a1 = np.sin(2 * np.pi * np.cumsum(np.linspace(260, 420, n1)) / SR) * np.sin(np.pi * np.arange(n1) / n1) * .4   # "ah"
    noise = g.normal(0, 1, n2); X = np.fft.rfft(noise); f = np.fft.rfftfreq(n2, 1 / SR); X[(f < 1500) | (f > 7000)] = 0; ch = np.fft.irfft(X, n2)
    ch = ch / np.abs(ch).max() * np.exp(-np.arange(n2) / (SR * .09))   # "CHOO"
    return np.concatenate([a1, ch]) * amp
def shutter(amp=.25):
    m = np.arange(int(SR * .12)) / SR; g = np.random.default_rng(2).normal(0, 1, len(m))
    return (g * np.exp(-m * 60) + np.sin(2 * np.pi * 1800 * m) * np.exp(-m * 80)) * amp
def poof(amp=.12):
    m = np.arange(int(SR * .3)) / SR; return np.sin(2 * np.pi * np.cumsum(900 - 700 * m / .3) / SR) * np.exp(-m * 10) * amp
def audio(path):
    tr = Track(DUR)
    k = 0; beat = 60 / 110
    while k * beat < DUR - 1:                                                 # playful pluck groove
        tt = k * beat; tr.add(pluck(note([0, 4, 7, 4, 9, 7, 4, 2][k % 8], 392), .35, .045, 8), tt)
        if k % 2 == 0: tr.add(pluck(note([0, 5, 3, 4][(k // 8) % 4], 98), .5, .05, 4), tt)
        k += 1
    for i in range(8): tr.add(load(f'vo/c{i}.wav'), T0[i])
    for ts in (T_DEMO, T_SNEEZE, T_CAR): tr.add(achoo(.3), ts - .35); tr.add(poof(.12), ts + .05); tr.add(poof(.08), ts + 1.0)
    tr.add(shutter(.3), T_SHOT); tr.add(pk.whoosh(.6, .08), T_SHOT + .1)
    for i in range(3): tr.add(pop(.07), T0[2] + DURS[2] * i / 3)
    tr.add(pop(.1), T0[3] + DURS[3] * .8); tr.add(pk.whoosh(.8, .09), T_STREET - .3)
    m = np.arange(int(SR * .35)) / SR; honk = (np.sign(np.sin(2 * np.pi * 420 * m)) + np.sign(np.sin(2 * np.pi * 530 * m))) * .04 * np.minimum(1, (len(m) - np.arange(len(m))) / 800)
    tr.add(honk, T_CAR + 1.1); tr.add(pop(.1), T_CAR + .2)
    for k in range(10): tr.add(chime(1200 + 120 * k, .02, .6), T_POLLEN + k * .3); tr.add(poof(.04), T_POLLEN + .15 + k * .3)
    tr.add(pop(.1), T0[7] + .2); tr.add(chime(1046, .05, 1.6), T0[7] + .6)
    tr.save(path, DUR)

if __name__ == '__main__': main(draw, DUR, audio, 'iso1_sneeze', sys.argv, strength=.25, thr=.85)
