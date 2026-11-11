"""PUNCH style: voiced myth-buster. Kinetic word captions, punch-zoom, stamp, counter, tiles. 'You have 5 senses? Wrong.'"""
import sys, wave, math
sys.path.insert(0, '/home/claude/glow')
from fx import *
LINES = ["You have five senses. That's what school taught you.", "It's wrong.",
         "Close your eyes and touch your nose. You just used a sixth sense.",
         "Feeling hot or cold? Another one. Pain? Another. Balance? Another.",
         "Hunger. Thirst. Even knowing you need the bathroom.",
         "Many scientists count more than twenty. So, how many did you know?"]
DURS = [wave.open(f'vo/c{i}.wav').getnframes() / 44100 for i in range(6)]
T0 = []; t = .15
for d in DURS: T0.append(t); t += d + .25
DUR = t + 1.3
WORDS = []                                     # (t_start, t_end, word, line)
for li, (s, t0, d) in enumerate(zip(LINES, T0, DURS)):
    ws = s.split(); wt = [len(w) + 2 + (4 if w[-1] in '.?,' else 0) for w in ws]; tot = sum(wt); acc = 0
    for w, k in zip(ws, wt): WORDS.append((t0 + d * acc / tot, t0 + d * (acc + k) / tot, w, li)); acc += k
def when(word, line):
    for a, b, w, li in WORDS:
        if li == line and w.strip('.,?').lower() == word: return a
    raise KeyError(word)
RED = (1.0, .23, .25)
TILES = [("SIGHT", "eye", when("five", 0)), ("HEARING", "ear", when("five", 0) + .12), ("SMELL", "nose", when("five", 0) + .24),
         ("TASTE", "tongue", when("five", 0) + .36), ("TOUCH", "hand", when("five", 0) + .48),
         ("BODY POSITION", "pos", when("sixth", 2)), ("TEMPERATURE", "thermo", when("hot", 3)), ("PAIN", "bolt", when("pain", 3)),
         ("BALANCE", "level", when("balance", 3)), ("HUNGER", "fork", when("hunger", 4)), ("THIRST", "drop", when("thirst", 4)),
         ("BLADDER", "wc", when("bathroom", 4))]
T_WRONG = T0[1]; T_MORE = when("twenty", 5)
for k in range(9): TILES.append(("?", "q", T_MORE + .05 + k * .07))
COLS = [CYAN, YEL, PINK, ORNG, LIME, (.6, .5, 1), RED, YEL, CYAN, ORNG, (.35, .7, 1), LIME]


def icon(ctx, kind, x, y, s, col):
    ctx.set_source_rgb(*col); ctx.set_line_width(s * .09); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_join(cairo.LINE_JOIN_ROUND); ctx.new_path()
    if kind == "eye":
        ctx.move_to(x - s * .45, y); ctx.curve_to(x - s * .2, y - s * .32, x + s * .2, y - s * .32, x + s * .45, y); ctx.curve_to(x + s * .2, y + s * .32, x - s * .2, y + s * .32, x - s * .45, y); ctx.stroke(); ctx.arc(x, y, s * .13, 0, 7); ctx.fill()
    elif kind == "ear":
        ctx.arc(x, y - s * .05, s * .25, math.pi, 2.2 * math.pi); ctx.curve_to(x + s * .2, y + s * .25, x, y + s * .2, x - s * .05, y + s * .38); ctx.stroke()
    elif kind == "nose":
        ctx.move_to(x, y - s * .38); ctx.line_to(x - s * .2, y + s * .2); ctx.curve_to(x - s * .1, y + s * .34, x + s * .15, y + s * .3, x + s * .2, y + s * .18); ctx.stroke()
    elif kind == "tongue":
        ctx.move_to(x - s * .4, y - s * .1); ctx.curve_to(x - s * .2, y + s * .1, x + s * .2, y + s * .1, x + s * .4, y - s * .1); ctx.stroke()
        ctx.move_to(x - s * .18, y + s * .02); ctx.curve_to(x - s * .2, y + s * .42, x + s * .2, y + s * .42, x + s * .18, y + s * .02); ctx.fill()
    elif kind == "hand":
        for k, dx in enumerate((-.24, -.08, .08, .24)): ctx.move_to(x + dx * s, y + s * .05); ctx.line_to(x + dx * s, y - s * (.32 + .06 * (k in (1, 2)))); ctx.stroke()
        ctx.move_to(x - s * .3, y + s * .05); ctx.curve_to(x - s * .3, y + s * .42, x + s * .3, y + s * .42, x + s * .3, y + s * .05); ctx.stroke()
    elif kind == "pos":
        ctx.arc(x - s * .05, y - s * .05, s * .3, 0, 7); ctx.stroke(); ctx.move_to(x + s * .45, y + s * .4); ctx.line_to(x + s * .18, y + s * .02); ctx.stroke(); ctx.arc(x + s * .18, y + s * .02, s * .06, 0, 7); ctx.fill()
    elif kind == "thermo":
        ctx.move_to(x, y - s * .38); ctx.line_to(x, y + s * .15); ctx.stroke(); ctx.arc(x, y + s * .25, s * .14, 0, 7); ctx.fill()
    elif kind == "bolt":
        ctx.move_to(x + s * .1, y - s * .42); ctx.line_to(x - s * .2, y + s * .05); ctx.line_to(x + s * .02, y + s * .05); ctx.line_to(x - s * .1, y + s * .42); ctx.line_to(x + s * .22, y - s * .08); ctx.line_to(x, y - s * .08); ctx.close_path(); ctx.fill()
    elif kind == "level":
        ctx.move_to(x - s * .15, y + s * .35); ctx.line_to(x, y + s * .1); ctx.line_to(x + s * .15, y + s * .35); ctx.close_path(); ctx.fill()
        ctx.move_to(x - s * .42, y + s * .02); ctx.line_to(x + s * .42, y - s * .1); ctx.stroke(); ctx.arc(x, y - s * .3, s * .1, 0, 7); ctx.fill()
    elif kind == "fork":
        for dx in (-.12, 0, .12): ctx.move_to(x + dx * s, y - s * .4); ctx.line_to(x + dx * s, y - s * .12); ctx.stroke()
        ctx.move_to(x - s * .14, y - s * .12); ctx.curve_to(x - s * .14, y, x + s * .14, y, x + s * .14, y - s * .12); ctx.stroke(); ctx.move_to(x, y - s * .05); ctx.line_to(x, y + s * .42); ctx.stroke()
    elif kind == "drop":
        ctx.move_to(x, y - s * .42); ctx.curve_to(x + s * .1, y - s * .2, x + s * .3, y, x + s * .28, y + s * .15); ctx.arc(x, y + s * .15, s * .28, 0, math.pi); ctx.curve_to(x - s * .3, y, x - s * .1, y - s * .2, x, y - s * .42); ctx.fill()
    elif kind == "wc": label(ctx, "WC", x, y + s * .16, int(s * .48), col=col, shadow=0)
    elif kind == "q": label(ctx, "?", x, y + s * .2, int(s * .62), col=(1, 1, 1), alpha=.85, shadow=0)


def grid(n_cols, size, gap, y0, i):
    r, c = divmod(i, n_cols); w = n_cols * size + (n_cols - 1) * gap
    return 540 - w / 2 + c * (size + gap) + size / 2, y0 + r * (size + gap) + size / 2


def draw(ctx, t):
    bg(ctx, (.05, .03, .09), (.14, .03, .10))
    # punch-zoom on stamp / reveals
    shake = 0
    if T_WRONG < t < T_WRONG + .45: shake = 22 * math.exp(-(t - T_WRONG) * 9) * math.sin((t - T_WRONG) * 70)
    big = t > T_MORE
    k = ease((t - T_MORE) / .5)
    size, gap, cols, y0 = lerp(190, 130, k), lerp(22, 14, k), int(5), lerp(640, 610, k)
    ctx.save(); ctx.translate(shake, shake * .4)
    n = sum(1 for tl in TILES if t >= tl[2])
    for i, (lab, kind, ta) in enumerate(TILES):
        if t < ta: continue
        x, y = grid(cols, size, gap, y0, i); p = popk((t - ta) / .3)
        dead = i < 5 and T_WRONG < t < T0[2] - .1
        ctx.save(); ctx.translate(x, y); ctx.scale(p, p)
        col = COLS[i] if i < len(COLS) else (1, 1, 1)
        if kind == "q": col = (.8, .8, .9)
        glow(ctx, 0, 0, size * .8, col, .22 if not dead else .06)
        rrect(ctx, -size / 2, -size / 2, size, size, size * .2); ctx.set_source_rgba(.12, .09, .18, .95); ctx.fill_preserve()
        ctx.set_source_rgba(*col, .9 if not dead else .35); ctx.set_line_width(4); ctx.stroke()
        icon(ctx, kind, 0, -size * .1, size * .55, col if not dead else (.55, .5, .6))
        if lab != "?": label(ctx, lab, 0, size * .38, int(size * (.13 if len(lab) < 9 else .095)), col=(1, 1, 1), alpha=.9 if not dead else .45, shadow=0)
        ctx.restore()
    # WRONG stamp over the first five
    if t > T_WRONG:
        sk = 1 + 1.6 * (1 - ease((t - T_WRONG) / .18)); a = cl((t - T_WRONG) / .08) * (1 - cl((t - T0[2] + .3) / .4))
        if a > 0:
            ctx.save(); ctx.translate(540, y0 + size * .9); ctx.rotate(-.18); ctx.scale(sk, sk)
            ctx.push_group()
            rrect(ctx, -330, -95, 660, 190, 26); ctx.set_source_rgb(*RED); ctx.set_line_width(16); ctx.stroke()
            label(ctx, "WRONG", 0, 52, 150, col=RED, shadow=0)
            ctx.pop_group_to_source(); ctx.paint_with_alpha(a); ctx.restore()
    ctx.restore()
    # counter
    shown = n if t < T_MORE else 12 + int(9 * cl((t - T_MORE) / .7))
    plus = "+" if t > T_MORE + .7 else ""
    last = max([tl[2] for tl in TILES if t >= tl[2]] + [0])
    cp = popk((t - last) / .3)
    if t > TILES[0][2]:
        col = RED if T_WRONG < t < T0[2] else (YEL if t > T_MORE else (1, 1, 1))
        label(ctx, f"{shown}{plus}", 540, 470, int(170 * cp), col=col, shadow=.5)
        label(ctx, "SENSES", 540, 545, 52, col=(1, 1, 1), alpha=.75, shadow=.3)
    if t < TILES[0][2]:
        label(ctx, "SENSES", 540, 545, 52, col=(1, 1, 1), alpha=.75, shadow=.3)
    # final question
    if t > T0[5] + DURS[5] * .55:
        a = cl((t - T0[5] - DURS[5] * .55) / .2)
        tagbox(ctx, "HOW MANY DID YOU KNOW?", 540, 1560, 62, YEL, fg=INK, a=a, k=popk((t - T0[5] - DURS[5] * .55) / .4), pointer=False)
    # word-by-word captions (TikTok style): 3-word window, active word highlighted
    cur = None
    for i, (a, b, w, li) in enumerate(WORDS):
        if a - .05 <= t < b + .15: cur = i
    if cur is not None and t < T0[5] + DURS[5] * .55:
        li = WORDS[cur][3]; idxs = [i for i, x in enumerate(WORDS) if x[3] == li]; pos = idxs.index(cur)
        start = idxs[(pos // 3) * 3]; chunk = [i for i in idxs if start <= i < start + 3]
        ctx.select_font_face("Inter Display Black"); fs = 76
        ctx.set_font_size(fs); sp = 34
        widths = [ctx.text_extents(WORDS[i][2].upper()).x_advance * 1.08 for i in chunk]
        tot = sum(widths) + sp * (len(chunk) - 1); sc = min(1, 960 / tot); widths = [w_ * sc for w_ in widths]; sp *= sc; fs = int(fs * sc); tot *= sc; x = 540 - tot / 2; y = 1420 if t < T0[5] + DURS[5] * .55 else 1420
        for i, wdt in zip(chunk, widths):
            act = i == cur; s = 1.12 if act else 1.0
            ctx.save(); ctx.translate(x + wdt / 2, y); ctx.scale(s, s)
            label(ctx, WORDS[i][2].upper(), 0, 0, fs, col=YEL if act else (1, 1, 1), shadow=.9)
            ctx.restore(); x += wdt + sp


def load(p):
    w = wave.open(p); return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768


def audio(path):
    tr = Track(DUR)
    m = np.arange(int(SR * .25)) / SR
    kick = np.sin(2 * np.pi * (50 + 90 * np.exp(-m * 30)) * m) * np.exp(-m * 14)
    b = 0.15
    while b < DUR - 1.2: tr.add(kick * (.10 if b < T_WRONG else .14), b); b += .5
    for i, (s, t0, d) in enumerate(zip(LINES, T0, DURS)): tr.add(load(f'vo/c{i}.wav') * 1.0, t0)
    for _, _, ta in TILES: tr.add(pop(.06), ta)
    m = np.arange(int(SR * .7)) / SR
    tr.add((np.sin(2 * np.pi * 42 * m) * np.exp(-m * 6) + .3 * np.random.default_rng(1).normal(0, 1, len(m)) * np.exp(-m * 18)) * .45, T_WRONG)
    tr.add(pk.whoosh(.6, .1), T_WRONG - .3); tr.add(pk.whoosh(1.0, .08), T_MORE - .5)
    for i, f in enumerate([523, 659, 784, 1046]): tr.add(chime(f, .05, 2), T_MORE + .7 + i * .06)
    tr.save(path, DUR)


if __name__ == '__main__': main(draw, DUR, audio, 'p1_senses', sys.argv, strength=.7, thr=.6)
