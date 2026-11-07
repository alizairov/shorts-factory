"""Long-form (16:9) explainer: What your body does in 24 hours. Narration (Higgsfield/ElevenLabs 'Mark') + code animation."""
import sys, math, random, json, wave
sys.path.insert(0, '/home/claude/reels')
import numpy as np, cairo
import common
common.W, common.H = 1920, 1080
from common import FPS, SR, encode, stills, Track, label, mux
from k1_stomach import rrect, ell, tagbox, sparkle, popk, lining, LOGO, chime, pop, pad, cl, ease, lerp
import paperkit as pk

W, H = 1920, 1080
TL = json.load(open('/home/claude/long1/timeline.json'))   # [sec, text, clip_id, dur]
# ---- timing ----
BEATS, t = [], 0.8
prev = None
for sec, txt, cid, d in TL:
    if prev is not None: t += 1.3 if sec != prev else 0.35
    BEATS.append(dict(sec=sec, text=txt, cid=cid, dur=d, t0=t)); t += d; prev = sec
DUR = t + 3.0
NF = int(DUR * FPS)
SECS = []
for i, b in enumerate(BEATS):
    if not SECS or SECS[-1][0] != b['sec']: SECS.append([b['sec'], b['t0'] - (0.6 if i else 0.8)])

INK = (0.12, 0.06, 0.20)
RED, RED2 = (0.95, 0.22, 0.34), (0.72, 0.10, 0.25)
PINK, PINKD = (1.0, 0.45, 0.65), (0.86, 0.22, 0.45)
LIME, CYAN, YEL, ORNG, PURP, BLUE = (0.80, 0.95, 0.30), (0.40, 0.88, 1.0), (1.0, 0.84, 0.25), (1.0, 0.58, 0.25), (0.62, 0.45, 1.0), (0.30, 0.55, 1.0)
BG = {"hook": ((0.30, 0.10, 0.45), (0.55, 0.15, 0.55)), "heart": ((0.40, 0.06, 0.20), (0.70, 0.16, 0.36)), "lungs": ((0.10, 0.22, 0.45), (0.25, 0.45, 0.75)),
      "blood": ((0.35, 0.05, 0.12), (0.62, 0.12, 0.25)), "stomach": ((0.30, 0.10, 0.40), (0.60, 0.22, 0.55)), "gut": ((0.10, 0.30, 0.28), (0.20, 0.55, 0.45)),
      "kidneys": ((0.25, 0.12, 0.40), (0.50, 0.28, 0.65)), "skin": ((0.40, 0.20, 0.12), (0.75, 0.45, 0.30)), "eyes": ((0.08, 0.25, 0.40), (0.20, 0.50, 0.70)),
      "cells": ((0.30, 0.10, 0.45), (0.55, 0.20, 0.60)), "brain": ((0.22, 0.10, 0.42), (0.45, 0.25, 0.70)), "night": ((0.03, 0.04, 0.14), (0.10, 0.12, 0.30)),
      "outro": ((0.30, 0.10, 0.45), (0.55, 0.15, 0.55))}
# organ positions (world) and camera per section (x, y, zoom)
ORG = {"heart": (595, 405), "lungs": (560, 400), "stomach": (610, 520), "gut": (560, 640), "kidneys": (560, 600), "skin": (395, 560),
       "eyes": (560, 185), "brain": (560, 165), "night": (560, 165), "bone": (515, 860)}
CAM = {"hook": (560, 560, 1.0), "heart": (595, 405, 2.6), "lungs": (560, 410, 2.0), "blood": (560, 560, 1.0), "stomach": (610, 520, 2.6), "gut": (560, 640, 2.4),
       "kidneys": (560, 600, 2.4), "skin": (395, 560, 2.6), "eyes": (560, 185, 3.4), "cells": (560, 560, 1.0), "brain": (560, 170, 2.8),
       "night": (560, 170, 2.8), "outro": (560, 560, 1.0)}
ANCHOR = (560, 560)


def sec_at(t):
    s = SECS[0]
    for x in SECS:
        if t >= x[1]: s = x
    return s


def beat_at(t):
    cur = None
    for i, b in enumerate(BEATS):
        if t >= b['t0'] - 0.25: cur = i
    return cur


def cam_at(t):
    idx = max(i for i, s in enumerate(SECS) if t >= s[1]) if t >= SECS[0][1] else 0
    c1 = CAM[SECS[idx][0]]
    if idx == 0: return c1
    c0 = CAM[SECS[idx - 1][0]]
    u = ease((t - SECS[idx][1]) / 1.0)
    # pull out a little mid-transition for punch
    z = lerp(c0[2], c1[2], u) * (1 - 0.18 * math.sin(math.pi * u))
    return (lerp(c0[0], c1[0], u), lerp(c0[1], c1[1], u), z)


def to_screen(p, cam):
    return (ANCHOR[0] + (p[0] - cam[0]) * cam[2], ANCHOR[1] + (p[1] - cam[1]) * cam[2])


# ---------------- body map ----------------
BPM = 72


def beatk(t):
    u = t % (60 / BPM)
    return math.exp(-(u / 0.07) ** 2) + 0.6 * math.exp(-((u - 0.22) / 0.06) ** 2)


def heart_path(ctx, x, y, s):
    ctx.move_to(x, y + 95 * s)
    ctx.curve_to(x - 150 * s, y - 10 * s, x - 110 * s, y - 120 * s, x - 50 * s, y - 115 * s)
    ctx.curve_to(x - 15 * s, y - 112 * s, x, y - 85 * s, x, y - 70 * s)
    ctx.curve_to(x, y - 85 * s, x + 15 * s, y - 112 * s, x + 50 * s, y - 115 * s)
    ctx.curve_to(x + 110 * s, y - 120 * s, x + 150 * s, y - 10 * s, x, y + 95 * s); ctx.close_path()


def glow(ctx, x, y, r, a, col=(1, 1, 0.95)):
    g = cairo.RadialGradient(x, y, 1, x, y, r); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g); ell(ctx, x, y, r, r); ctx.fill()


def body(ctx, t, sec):
    act = lambda k: 1.0 if sec == k else (0.35 if sec in ("hook", "cells", "outro", "blood") else 0.22)
    # silhouette
    ctx.push_group()
    ctx.set_source_rgba(1, 1, 1, 0.16)
    ell(ctx, 560, 170, 95, 105); ctx.fill(); rrect(ctx, 525, 255, 70, 60, 20); ctx.fill()
    rrect(ctx, 440, 300, 240, 400, 90); ctx.fill()
    for sd in (-1, 1):
        rrect(ctx, 560 + sd * 150 - 32, 320, 64, 380, 32); ctx.fill()
        rrect(ctx, 560 + sd * 55 - 42, 660, 84, 400, 40); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint()
    ctx.set_source_rgba(1, 1, 1, 0.45); ctx.set_line_width(3)
    ell(ctx, 560, 170, 95, 105); ctx.stroke(); rrect(ctx, 440, 300, 240, 400, 90); ctx.stroke()
    # skin highlight
    if sec == "skin":
        ctx.set_source_rgba(1, 0.75, 0.6, 0.5); rrect(ctx, 560 - 150 - 32, 320, 64, 380, 32); ctx.fill()
    # vessels (blood section): glowing loop with racing cells
    a = act("blood")
    ctx.set_line_width(7); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    loop = [(595, 405), (640, 330), (700, 380), (710, 650), (620, 980), (560, 1020), (500, 980), (410, 650), (420, 380), (480, 330), (595, 405)]
    ctx.set_source_rgba(*RED, 0.25 + 0.5 * a); ctx.move_to(*loop[0])
    for p in loop[1:]: ctx.line_to(*p)
    ctx.stroke()
    if sec == "blood":
        seg = [(loop[i], loop[i + 1]) for i in range(len(loop) - 1)]
        L = [math.dist(a_, b_) for a_, b_ in seg]; tot = sum(L)
        for k in range(10):
            d = ((t * 420 + k * tot / 10) % tot)
            for (p0, p1), l in zip(seg, L):
                if d <= l:
                    x = lerp(p0[0], p1[0], d / l); y = lerp(p0[1], p1[1], d / l)
                    glow(ctx, x, y, 26, 0.7, (1, 0.4, 0.5)); ctx.set_source_rgb(*RED); ell(ctx, x, y, 9, 6); ctx.fill(); break
                d -= l
    # bones (marrow)
    ctx.set_source_rgba(1, 0.95, 0.85, 0.25 + 0.4 * act("blood")); rrect(ctx, 500, 720, 30, 300, 15); ctx.fill(); rrect(ctx, 590, 720, 30, 300, 15); ctx.fill()
    # lungs
    br = 1 + 0.08 * math.sin(t * 2 * math.pi / 4)
    for sd in (-1, 1):
        ctx.set_source_rgba(1, 0.6, 0.7, 0.35 + 0.55 * act("lungs"))
        ell(ctx, 560 + sd * 62, 410, 52 * br, 95 * br); ctx.fill()
    # heart
    s = 0.36 * (1 + 0.1 * beatk(t))
    if sec == "heart": glow(ctx, 595, 405, 130, 0.5 * beatk(t) + 0.15, (1, 0.5, 0.6))
    heart_path(ctx, 595, 405, s); ctx.set_source_rgba(*RED, 0.45 + 0.55 * act("heart")); ctx.fill()
    # stomach
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for w, c in [(44, (1, 0.9, 0.85)), (30, PINK)]:
        ctx.move_to(615, 470); ctx.curve_to(620, 500, 660, 500, 650, 535); ctx.curve_to(640, 575, 575, 575, 565, 548)
        ctx.set_line_width(w); ctx.set_source_rgba(*c, 0.35 + 0.65 * act("stomach")); ctx.stroke()
    # gut coil
    ctx.set_line_width(16); ctx.set_source_rgba(1, 0.7, 0.55, 0.3 + 0.7 * act("gut"))
    for k in range(4):
        ctx.move_to(500, 600 + k * 22); ctx.curve_to(530, 588 + k * 22, 590, 612 + k * 22, 620, 600 + k * 22); ctx.stroke()
    # kidneys
    for sd in (-1, 1):
        ctx.set_source_rgba(0.75, 0.35, 0.45, 0.3 + 0.7 * act("kidneys")); ell(ctx, 560 + sd * 62, 585, 24, 36); ctx.fill()
    # brain + eyes
    na = max(act("brain"), act("night"))
    ctx.set_source_rgba(1, 0.7, 0.8, 0.25 + 0.6 * na)
    for dx, dy, r in [(-35, -20, 40), (0, -35, 44), (35, -20, 40), (-15, 0, 36), (20, 0, 36)]: ell(ctx, 560 + dx, 145 + dy, r, r * 0.85); ctx.fill()
    if sec == "night":
        for k in range(3):
            ph = (t * 0.35 + k / 3) % 1
            ctx.set_source_rgba(*CYAN, 0.6 * (1 - ph)); ctx.set_line_width(4); ell(ctx, 560, 135, 30 + 60 * ph, 25 + 45 * ph); ctx.stroke()
    blink = 1.0 if sec != "eyes" else min(1, abs(((t * 0.6) % 1) - 0.5) * 12)
    for sd in (-1, 1):
        ctx.set_source_rgba(1, 1, 1, 0.3 + 0.7 * act("eyes")); ell(ctx, 560 + sd * 32, 195, 16, 11 * blink + 0.5); ctx.fill()
        ctx.set_source_rgba(*INK, 0.4 + 0.6 * act("eyes")); ell(ctx, 560 + sd * 32, 196, 6, 6 * blink + 0.3); ctx.fill()
    # sparkles on the active organ
    if sec in ORG:
        ox, oy = ORG[sec]
        for k in range(6):
            ph = (t * 0.8 + k / 6) % 1; ang = k * 2.4 + 1
            sparkle(ctx, ox + math.cos(ang) * (40 + 70 * ph), oy + math.sin(ang) * (40 + 70 * ph), 12 * (1 - ph), 0.8 * (1 - ph))


# ---------------- magnifier contents (local coords, centre cx, cy, radius R) ----------------
def m_valve(ctx, cx, cy, R, t):
    ctx.set_source_rgb(0.30, 0.06, 0.18); ctx.paint()
    ctx.set_source_rgb(*RED2); ctx.rectangle(cx - R, cy - R, R * 0.55, 2 * R); ctx.fill(); ctx.rectangle(cx + R * 0.45, cy - R, R * 0.55, 2 * R); ctx.fill()
    P = 60 / BPM; u = (t % P) / P
    ok = math.sin(math.pi * cl(u / 0.45)) if u < 0.45 else 0.0
    rnd = random.Random(7)
    for k in range(30):
        x = cx + rnd.uniform(-R * 0.38, R * 0.38)
        y = cy + R - ((rnd.uniform(0, 2 * R) + t * 170 + 120 * math.floor(t / P)) % (2 * R))
        if abs(y - cy) < 30 and ok < 0.2: continue
        ctx.set_source_rgb(*RED); ell(ctx, x, y, 22, 14); ctx.fill(); ctx.set_source_rgb(*RED2); ell(ctx, x, y, 10, 5); ctx.fill()
    for sd in (-1, 1):
        hx = cx + sd * R * 0.45; ang = (math.pi / 2 - 0.15) * ok
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(30); ctx.set_source_rgb(1, 0.85, 0.75)
        ctx.move_to(hx, cy); ctx.line_to(hx - sd * R * 0.46 * math.cos(ang), cy - R * 0.46 * math.sin(ang)); ctx.stroke()


def m_alveoli(ctx, cx, cy, R, t):
    ctx.set_source_rgb(0.55, 0.12, 0.25); ctx.paint()
    br = 1 + 0.12 * math.sin(t * 2 * math.pi / 4)
    rnd = random.Random(2)
    for k in range(16):
        x, y = cx + rnd.uniform(-R, R), cy + rnd.uniform(-R, R); r = rnd.uniform(55, 90) * br
        ctx.set_source_rgb(1, 0.72, 0.78); ell(ctx, x, y, r, r); ctx.fill()
        ctx.set_source_rgb(1, 0.85, 0.88); ell(ctx, x - r * 0.2, y - r * 0.2, r * 0.75, r * 0.75); ctx.fill()
    for k in range(40):
        ph = (t * 0.5 + k / 40) % 1; inn = k % 2 == 0
        ang = k * 2.3; d = R * (1 - ph) if inn else R * ph
        x, y = cx + math.cos(ang) * d, cy + math.sin(ang) * d
        ctx.set_source_rgba(*(CYAN if inn else (0.55, 0.55, 0.6)), 0.9); ell(ctx, x, y, 9, 9); ctx.fill()


def m_marrow(ctx, cx, cy, R, t):
    ctx.set_source_rgb(0.85, 0.40, 0.42); ctx.paint()
    rnd = random.Random(5)
    ctx.set_source_rgb(1, 0.92, 0.80); ctx.set_line_width(18); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    pts = [(cx + rnd.uniform(-R, R), cy + rnd.uniform(-R, R)) for _ in range(30)]
    for i, p in enumerate(pts):
        q = pts[(i * 7 + 3) % len(pts)]; ctx.move_to(*p); ctx.line_to(lerp(p[0], q[0], 0.5), lerp(p[1], q[1], 0.5)); ctx.stroke()
    for k in range(45):
        ph = (t * 0.6 + k / 45) % 1; ang = k * 1.7
        x, y = cx + math.cos(ang) * R * ph, cy + math.sin(ang) * R * ph
        s = popk(ph * 3) if ph < 0.33 else 1
        ctx.set_source_rgb(*RED); ell(ctx, x, y, 18 * s, 12 * s); ctx.fill(); ctx.set_source_rgb(*RED2); ell(ctx, x, y, 8 * s, 4 * s); ctx.fill()


def m_bacteria(ctx, cx, cy, R, t):
    ctx.set_source_rgb(0.18, 0.32, 0.22); ctx.paint()
    rnd = random.Random(8)
    cols = [LIME, CYAN, YEL, ORNG, PINK, PURP]
    for k in range(60):
        x = cx + rnd.uniform(-R, R) + 10 * math.sin(t * 1.5 + k); y = cy + rnd.uniform(-R, R) + 10 * math.cos(t * 1.3 + k)
        a = rnd.uniform(0, math.pi) + 0.3 * math.sin(t * 2 + k); L_ = rnd.uniform(18, 36)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(rnd.uniform(14, 22)); ctx.set_source_rgb(*cols[k % 6])
        ctx.move_to(x - L_ * math.cos(a), y - L_ * math.sin(a)); ctx.line_to(x + L_ * math.cos(a), y + L_ * math.sin(a)); ctx.stroke()


def m_skin(ctx, cx, cy, R, t):
    ctx.set_source_rgb(0.95, 0.80, 0.70); ctx.paint()
    top = cy - R * 0.35; ch, cw = 48, 90
    off = (t * 30) % ch
    for row in range(-1, 12):
        y = top + row * ch - off
        depth = cl((y - top) / (R * 1.2))
        for col in range(-6, 7):
            x = cx + col * cw + (row % 2) * cw / 2
            flat = 1 - depth
            c = (lerp(0.98, 1.0, flat), lerp(0.62, 0.90, flat), lerp(0.55, 0.85, flat))
            ctx.set_source_rgb(*c); rrect(ctx, x - cw / 2 + 3, y + 3, cw - 6, ch - 6, 12 * (1 - flat) + 3); ctx.fill()
    for k in range(18):   # flakes falling off the surface (upward/out)
        ph = (t * 0.5 + k / 18) % 1
        x = cx - R + (k * 97) % (2 * R); y = top - ph * R * 0.8
        ctx.set_source_rgba(1, 0.95, 0.9, 1 - ph); ctx.save(); ctx.translate(x, y); ctx.rotate(ph * 3 + k)
        rrect(ctx, -30, -8, 60, 16, 6); ctx.fill(); ctx.restore()
    ctx.set_source_rgba(0.95, 0.80, 0.70, 0.0)


def m_tear(ctx, cx, cy, R, t):
    ctx.set_source_rgb(1, 1, 1); ctx.paint()
    ctx.set_source_rgb(0.30, 0.55, 0.85); ell(ctx, cx, cy, R * 0.55, R * 0.55); ctx.fill()
    ctx.set_source_rgb(*INK); ell(ctx, cx, cy, R * 0.25, R * 0.25); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.8); ell(ctx, cx - R * 0.15, cy - R * 0.15, R * 0.08, R * 0.08); ctx.fill()
    u = (t * 0.45) % 1
    lid = math.sin(math.pi * cl(u / 0.14)) if u < 0.14 else 0
    film = cl((u - 0.15) / 0.6)
    ctx.set_source_rgba(*CYAN, 0.35 * (1 - film) + 0.1); ctx.rectangle(cx - R, cy - R, 2 * R, 2 * R * max(film, lid)); ctx.fill()
    ctx.set_source_rgb(0.95, 0.70, 0.60); ctx.rectangle(cx - R, cy - R, 2 * R, 2 * R * lid); ctx.fill()


def m_brainwave(ctx, cx, cy, R, t, waste=False):
    ctx.set_source_rgb(0.95, 0.65, 0.75); ctx.paint()
    ctx.set_source_rgb(0.85, 0.50, 0.62); ctx.set_line_width(14); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for k in range(7):
        y0 = cy - R + k * R / 3.2
        ctx.move_to(cx - R, y0)
        for i in range(30): ctx.line_to(cx - R + i * 2 * R / 29, y0 + 22 * math.sin(i * 0.9 + k))
        ctx.stroke()
    for k in range(4):
        ph = (t * 0.3 + k / 4) % 1
        x = cx - R + ph * 2 * R
        g = cairo.LinearGradient(x - 120, 0, x + 120, 0)
        g.add_color_stop_rgba(0, *CYAN, 0); g.add_color_stop_rgba(0.5, *CYAN, 0.55); g.add_color_stop_rgba(1, *CYAN, 0)
        ctx.set_source(g); ctx.rectangle(x - 120, cy - R, 240, 2 * R); ctx.fill()
    if waste:
        rnd = random.Random(3)
        for k in range(40):
            x0 = rnd.uniform(-R, R); y = cy + rnd.uniform(-R, R)
            x = cx + x0 + ((t * 80 + k * 13) % (2 * R)) - R * 0.5
            if x > cx + R: continue
            ctx.set_source_rgba(0.40, 0.38, 0.45, 0.9); ell(ctx, x, y, 10, 10); ctx.fill()


MAGS = {"valve": m_valve, "alveoli": m_alveoli, "marrow": m_marrow, "lining": lambda c, x, y, R, t: lining(c, x, y, R, t, 60),
        "lining_fast": lambda c, x, y, R, t: lining(c, x, y, R, t, 260), "bacteria": m_bacteria, "skin": m_skin, "tear": m_tear,
        "brainwave": m_brainwave, "waste": lambda c, x, y, R, t: m_brainwave(c, x, y, R, t, True)}

# panel spec per beat (same order as timeline)
PANELS = [
    ("title", "YOUR BODY IN 24 HOURS", YEL), ("clock",), ("title", "THE NIGHT SECRET?", CYAN),
    ("count", 70, "BEATS / MINUTE", RED), ("count", 103680, "BEATS / DAY", RED), ("mag", "valve", [("Valve", ORNG, (120, -40))]),
    ("count", 7000, "LITERS / DAY", RED, "tubs"),
    ("title", "LUNGS", PINK), ("count", 20000, "BREATHS / DAY", BLUE, "air"), ("mag", "alveoli", [("Air sacs", PINKD, (-90, 150)), ("O₂", BLUE, (150, -120))]),
    ("stopwatch",), ("count", 1440, "LAPS / DAY", RED), ("mag", "marrow", [("Bone marrow", ORNG, (-60, -170))], "2,000,000 / SEC"),
    ("title", "STOMACH", PINK), ("mag", "lining", [("Acid", (0.42, 0.62, 0.10), (-140, -150)), ("Mucus", BLUE, (150, -20)), ("Lining", PINKD, (-40, 150))]),
    ("calendar",),
    ("count", 38, "TRILLION BACTERIA", LIME, "bact"), ("bars", "BACTERIA", "YOUR CELLS", 38, 30, LIME, PINK),
    ("title", "KIDNEYS", PURP), ("count", 180, "LITERS FILTERED / DAY", PURP), ("filter",),
    ("mag", "skin", [("Old cells flake off", ORNG, (0, -170))]), ("title", "NEW SKIN ~ EVERY MONTH", ORNG),
    ("count", 15000, "BLINKS / DAY", CYAN), ("mag", "tear", [("Tear film", BLUE, (0, -170))]),
    ("title", "ADD IT ALL UP", YEL), ("count", 330, "BILLION CELLS / DAY", YEL, "grid"), ("title", "30 TRILLION IN ~3 MONTHS", YEL),
    ("bars", "WEIGHT", "ENERGY", 2, 20, PURP, YEL, "%"),
    ("title", "AT NIGHT…", CYAN), ("mag", "brainwave", [("Brain fluid", BLUE, (0, -170))]), ("mag", "waste", [("Waste washed away", (0.45, 0.42, 0.55), (0, -170))]),
    ("title", "SLEEP MATTERS", CYAN),
    ("montage",), ("follow",)]
assert len(PANELS) == len(BEATS), (len(PANELS), len(BEATS))

PX, PY = 1390, 520          # right-panel centre


def fmt(n):
    return f"{int(n):,}"


def p_count(ctx, u, v, lbl, col, extra=None):
    k = 1 - (1 - cl(u / 1.4)) ** 3
    n = v * k
    label(ctx, fmt(n), PX, PY + 20, 170 if v < 100000 else 150, col=(1, 1, 1), shadow=0.4)
    tagbox(ctx, lbl, PX, PY + 150, 54, col, fg=INK if col in (YEL, LIME, CYAN) else (1, 1, 1), pointer=False, k=popk((u - 0.2) / 0.4), a=cl((u - 0.2) / 0.2))
    if extra == "tubs":
        m = int(40 * cl((u - 1.6) / 2.0))
        for i in range(m):
            x = PX - 320 + (i % 10) * 70; y = PY + 260 + (i // 10) * 50
            ctx.set_source_rgb(1, 1, 1); rrect(ctx, x - 26, y - 14, 52, 28, 10); ctx.fill(); ctx.set_source_rgb(*RED); rrect(ctx, x - 22, y - 10, 44, 12, 6); ctx.fill()
        if m: label(ctx, f"{m} BATHTUBS", PX, PY - 170, 50, col=YEL)
    if extra == "air":
        tagbox(ctx, "10,000+ LITERS OF AIR", PX, PY + 270, 46, (1, 1, 1), fg=BLUE, pointer=False, a=cl((u - 2.4) / 0.3), k=popk((u - 2.4) / 0.4))
    if extra == "bact":
        tagbox(ctx, "38,000,000,000,000", PX, PY - 170, 50, (1, 1, 1), fg=INK, pointer=False, a=cl((u - 1.6) / 0.3), k=popk((u - 1.6) / 0.4))
    if extra == "grid":
        for i in range(100):
            x = PX - 270 + (i % 20) * 28; y = PY + 270 + (i // 20) * 28
            on = i == int((u * 3) % 100) or (u > 2 and i == 57)
            ctx.set_source_rgb(*(YEL if on else (1, 1, 1))); ell(ctx, x, y, 11, 11); ctx.fill()
        tagbox(ctx, "≈ 1% OF YOU", PX, PY - 170, 50, (1, 1, 1), fg=INK, pointer=False, a=cl((u - 2.0) / 0.3), k=popk((u - 2.0) / 0.4))


def p_title(ctx, u, txt, col):
    k = popk(u / 0.45)
    tagbox(ctx, txt, PX, PY + 30, 92 if len(txt) < 14 else 70, col, fg=INK if col in (YEL, LIME, CYAN) else (1, 1, 1), pointer=False, k=k, a=cl(u / 0.15))


def p_clock(ctx, u, t):
    r = 230
    ctx.set_source_rgb(1, 1, 1); ell(ctx, PX, PY, r, r); ctx.fill()
    ctx.set_source_rgb(*PURP); ctx.set_line_width(18); ell(ctx, PX, PY, r, r); ctx.stroke()
    for h in range(24):
        a = h / 24 * 2 * math.pi - math.pi / 2
        ctx.set_source_rgb(*INK); ctx.set_line_width(6 if h % 6 == 0 else 3)
        ctx.move_to(PX + (r - 30) * math.cos(a), PY + (r - 30) * math.sin(a)); ctx.line_to(PX + (r - 10) * math.cos(a), PY + (r - 10) * math.sin(a)); ctx.stroke()
    a = 2 * math.pi * ease(u / 3.5) - math.pi / 2
    ctx.set_source_rgba(*YEL, 0.6); ctx.move_to(PX, PY); ctx.arc(PX, PY, r - 40, -math.pi / 2, a); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(*INK); ctx.set_line_width(12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(PX, PY); ctx.line_to(PX + 170 * math.cos(a), PY + 170 * math.sin(a)); ctx.stroke()
    label(ctx, "24 H", PX, PY + r + 70, 64, col=YEL)


def p_stopwatch(ctx, u, t):
    r = 200
    ctx.set_source_rgb(1, 1, 1); ell(ctx, PX, PY + 20, r, r); ctx.fill(); rrect(ctx, PX - 30, PY - r - 50, 60, 50, 10); ctx.fill()
    ctx.set_source_rgb(*RED); ctx.set_line_width(16); ell(ctx, PX, PY + 20, r, r); ctx.stroke()
    a = 2 * math.pi * cl(u / 3.5) - math.pi / 2
    ctx.set_source_rgba(*RED, 0.35); ctx.move_to(PX, PY + 20); ctx.arc(PX, PY + 20, r - 30, -math.pi / 2, a); ctx.close_path(); ctx.fill()
    ctx.set_source_rgb(*INK); ctx.set_line_width(10); ctx.move_to(PX, PY + 20); ctx.line_to(PX + 150 * math.cos(a), PY + 20 + 150 * math.sin(a)); ctx.stroke()
    secs = int(60 * cl(u / 3.5))
    label(ctx, f"0:{secs:02d}", PX, PY + r + 110, 80, col=(1, 1, 1))


def p_calendar(ctx, u, t):
    d = min(5, 1 + int(u / 0.8))
    rrect(ctx, PX - 190, PY - 200, 380, 400, 40); ctx.set_source_rgb(1, 1, 1); ctx.fill()
    rrect(ctx, PX - 190, PY - 200, 380, 110, 40); ctx.set_source_rgb(*PINKD); ctx.fill(); ctx.rectangle(PX - 190, PY - 140, 380, 50); ctx.fill()
    label(ctx, "DAY", PX, PY - 125, 56, shadow=0)
    label(ctx, str(d), PX, PY + 120, 220, col=INK, shadow=0)
    tagbox(ctx, "NEW LINING EVERY 3–5 DAYS", PX, PY + 320, 44, PINKD, pointer=False, a=cl((u - 3.2) / 0.3), k=popk((u - 3.2) / 0.4))


def p_bars(ctx, u, l1, l2, v1, v2, c1, c2, unit=""):
    mx = max(v1, v2)
    for i, (l, v, c) in enumerate([(l1, v1, c1), (l2, v2, c2)]):
        x = PX - 130 + i * 260; h = 420 * v / mx * ease(cl((u - 0.3 * i) / 1.0))
        rrect(ctx, x - 80, PY + 220 - h, 160, max(h, 1), 24); ctx.set_source_rgb(*c); ctx.fill()
        txt = f"{v}{unit}" if unit else f"~{v}T"
        label(ctx, txt, x, PY + 200 - h - 20, 70, col=(1, 1, 1))
        tagbox(ctx, l, x, PY + 300, 40, (1, 1, 1), fg=INK, pointer=False)


def p_filter(ctx, u, t):
    h1 = 420; k = ease(cl((u - 0.8) / 1.8))
    rrect(ctx, PX - 260, PY + 220 - h1, 180, h1, 24); ctx.set_source_rgb(*PURP); ctx.fill()
    label(ctx, "180 L", PX - 170, PY + 220 - h1 - 30, 64)
    h2 = lerp(h1, 8, k)
    rrect(ctx, PX + 80, PY + 220 - h2, 180, h2, 24 if h2 > 50 else 4); ctx.set_source_rgb(*YEL); ctx.fill()
    label(ctx, "~1.5 L" if k > 0.9 else f"{int(lerp(180, 1.5, k))} L", PX + 170, PY + 220 - h2 - 30, 64)
    ctx.set_source_rgba(1, 1, 1, 0.9 * k); ctx.set_line_width(10); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(PX + 60, PY - 60); ctx.curve_to(PX + 20, PY - 220, PX - 60, PY - 220, PX - 90, PY - 120); ctx.stroke()
    tagbox(ctx, "99% GOES BACK", PX, PY + 310, 44, (1, 1, 1), fg=PURP, pointer=False, a=cl((u - 2.2) / 0.3), k=popk((u - 2.2) / 0.4))


def p_montage(ctx, u, t):
    items = [("103,680", "heartbeats", RED), ("~20,000", "breaths", BLUE), ("~330 billion", "new cells", YEL), ("15,000", "blinks", CYAN)]
    for i, (n, l, c) in enumerate(items):
        k = popk((u - i * 0.6) / 0.4); a = cl((u - i * 0.6) / 0.2)
        y = PY - 270 + i * 165
        tagbox(ctx, f"{n} {l}", PX, y, 60, c, fg=INK if c in (YEL, CYAN) else (1, 1, 1), pointer=False, k=k, a=a)


def p_follow(ctx, u, t):
    k = popk(u / 0.5)
    ctx.save(); ctx.translate(PX, PY - 80); ctx.scale(k * 1.8, k * 1.8)
    ctx.set_source_rgb(1, 1, 1); ell(ctx, 0, 0, 66, 66); ctx.fill(); ctx.set_source_surface(LOGO, -60, -60); ctx.paint(); ctx.restore()
    label(ctx, "VISUAL BRAIN", PX, PY + 120, 90, col=YEL)
    tagbox(ctx, "@Visual.Brainer", PX, PY + 210, 52, (1, 1, 1), fg=INK, pointer=False, a=cl((u - 0.5) / 0.3))


def magnifier(ctx, u, t, name, tags, extra, src):
    R = 330; k = popk(u / 0.45)
    ctx.set_source_rgba(*LIME, cl(u / 0.2)); ctx.set_line_width(10)
    ctx.move_to(*src); ctx.line_to(PX - R * k, PY); ctx.stroke(); ell(ctx, src[0], src[1], 16, 16); ctx.fill()
    ctx.save(); ell(ctx, PX, PY, R * k, R * k); ctx.clip()
    ctx.push_group(); MAGS[name](ctx, PX, PY, R, t); ctx.pop_group_to_source(); ctx.paint(); ctx.restore()
    ctx.set_source_rgb(*LIME); ctx.set_line_width(14); ell(ctx, PX, PY, R * k, R * k); ctx.stroke()
    for i, (txt, col, (dx, dy)) in enumerate(tags):
        tagbox(ctx, txt, PX + dx, PY + dy, 46, col, a=cl((u - 0.6 - i * 0.5) / 0.2), k=popk((u - 0.6 - i * 0.5) / 0.35))
    if extra:
        tagbox(ctx, extra, PX, PY + R + 90, 56, (1, 1, 1), fg=RED2, pointer=False, a=cl((u - 2.0) / 0.3), k=popk((u - 2.0) / 0.4))


def panel(ctx, i, t, cam):
    b = BEATS[i]; u = t - b['t0'] + 0.25
    p = PANELS[i]; kind = p[0]
    sec = b['sec']
    src = to_screen(ORG.get(sec, ORG["heart"] if sec == "hook" else (560, 560)), cam)
    if kind == "count": p_count(ctx, u, p[1], p[2], p[3], p[4] if len(p) > 4 else None)
    elif kind == "title": p_title(ctx, u, p[1], p[2])
    elif kind == "clock": p_clock(ctx, u, t)
    elif kind == "stopwatch": p_stopwatch(ctx, u, t)
    elif kind == "calendar": p_calendar(ctx, u, t)
    elif kind == "bars": p_bars(ctx, u, *p[1:])
    elif kind == "filter": p_filter(ctx, u, t)
    elif kind == "montage": p_montage(ctx, u, t)
    elif kind == "follow": p_follow(ctx, u, t)
    elif kind == "mag":
        if p[1] == "marrow": src = to_screen(ORG["bone"], cam)
        magnifier(ctx, u, t, p[1], p[2], p[3] if len(p) > 3 else None, src)


def captions(ctx, t):
    i = beat_at(t)
    if i is None: return
    b = BEATS[i]; u = (t - b['t0']) / b['dur']
    if u < 0 or u > 1.05: return
    words = b['text'].split()
    n = max(1, math.ceil(len(words) / 7)); chunk = min(n - 1, int(u * n))
    per = math.ceil(len(words) / n)
    txt = " ".join(words[chunk * per:(chunk + 1) * per])
    ctx.select_font_face("Inter Display Black"); ctx.set_font_size(46)
    w = ctx.text_extents(txt).x_advance
    ctx.set_source_rgba(0, 0, 0, 0.45); rrect(ctx, W / 2 - w / 2 - 24, 975, w + 48, 70, 20); ctx.fill()
    label(ctx, txt, W / 2, 1025, 46, col=(1, 1, 1), shadow=0)


def draw(ctx, fi):
    t = fi / FPS
    sec = sec_at(t)[0]
    c0, c1 = BG[sec]
    # crossfade background between sections
    idx = max(i for i, s in enumerate(SECS) if t >= s[1]) if t >= SECS[0][1] else 0
    if idx > 0:
        u = cl((t - SECS[idx][1]) / 0.8); p0, p1 = BG[SECS[idx - 1][0]]
        c0 = tuple(lerp(a, b_, u) for a, b_ in zip(p0, c0)); c1 = tuple(lerp(a, b_, u) for a, b_ in zip(p1, c1))
    g = cairo.LinearGradient(0, 0, W, H); g.add_color_stop_rgb(0, *c0); g.add_color_stop_rgb(1, *c1); ctx.set_source(g); ctx.paint()
    # soft drifting bokeh
    rnd = random.Random(11)
    for k in range(18):
        x = (rnd.uniform(0, W) + t * rnd.uniform(5, 20)) % W; y = rnd.uniform(0, H)
        ctx.set_source_rgba(1, 1, 1, 0.04); ell(ctx, x, y, rnd.uniform(30, 90), rnd.uniform(30, 90)); ctx.fill()
    if sec == "night":
        for k in range(60):
            x, y = rnd.uniform(0, W), rnd.uniform(0, H)
            ctx.set_source_rgba(1, 1, 1, 0.3 + 0.3 * math.sin(t * 2 + k)); ell(ctx, x, y, 2.5, 2.5); ctx.fill()
        ctx.set_source_rgb(1, 0.95, 0.8); ell(ctx, 1750, 140, 60, 60); ctx.fill()
        ctx.set_source_rgb(*BG["night"][0]); ell(ctx, 1775, 125, 55, 55); ctx.fill()
    cam = cam_at(t)
    ctx.save(); ctx.rectangle(0, 0, 1100, H); ctx.clip()
    ctx.translate(ANCHOR[0], ANCHOR[1]); ctx.scale(cam[2], cam[2]); ctx.translate(-cam[0], -cam[1])
    body(ctx, t, sec)
    ctx.restore()
    # right panel: current beat (with quick fade-out of the previous one)
    i = beat_at(t)
    if i is not None:
        b = BEATS[i]
        if i > 0 and t - (b['t0'] - 0.25) < 0.2:
            ctx.push_group(); panel(ctx, i - 1, t, cam); ctx.pop_group_to_source(); ctx.paint_with_alpha(1 - (t - b['t0'] + 0.25) / 0.2)
        panel(ctx, i, t, cam)
    # section chip + mini 24h progress
    chip = {"hook": "INTRO", "heart": "HEART", "lungs": "LUNGS", "blood": "BLOOD", "stomach": "STOMACH", "gut": "GUT", "kidneys": "KIDNEYS",
            "skin": "SKIN", "eyes": "EYES", "cells": "CELLS", "brain": "BRAIN", "night": "SLEEP", "outro": "24 HOURS"}[sec]
    tagbox(ctx, chip, 190, 70, 40, (1, 1, 1), fg=INK, pointer=False)
    hrs = 24 * cl(t / (DUR - 3))
    ctx.set_source_rgba(1, 1, 1, 0.25); rrect(ctx, 80, 110, 220, 12, 6); ctx.fill()
    ctx.set_source_rgb(*YEL); rrect(ctx, 80, 110, max(12, 220 * hrs / 24), 12, 6); ctx.fill()
    label(ctx, f"{int(hrs):02d}:00", 340, 122, 30, col=(1, 1, 1), anchor="l")
    # brand
    ctx.set_source_rgb(1, 1, 1); ell(ctx, 1820, 990, 40, 40); ctx.fill()
    ctx.save(); ctx.translate(1780, 950); ctx.scale(0.667, 0.667); ctx.set_source_surface(LOGO, 0, 0); ctx.paint(); ctx.restore()
    captions(ctx, t)
    # section transition flash
    f = max([0] + [1 - abs(t - s[1]) / 0.18 for s in SECS[1:]])
    if f > 0: ctx.set_source_rgba(1, 1, 1, 0.25 * f); ctx.paint()


# ---------------- audio ----------------
def load(path):
    w = wave.open(path); a = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    return a


def lubdub(amp):
    m = np.arange(int(SR * 0.18)) / SR
    return np.sin(2 * np.pi * 55 * m) * np.exp(-m * 28) * amp


def audio(path):
    tr = Track(DUR)
    pad(tr, DUR, 0.022)
    for b in BEATS:
        tr.add(load(f"/home/claude/long1/vo/b{b['cid']}.wav") * 0.95, b['t0'])
    for s in SECS[1:]:
        tr.add(pk.whoosh(0.9, 0.06), s[1] - 0.35)
    for i, b in enumerate(BEATS):
        tr.add(pop(0.07), b['t0'] - 0.2)
        p = PANELS[i]
        if p[0] == "count":
            for k in range(10): tr.add(pop(0.02), b['t0'] - 0.2 + 1.4 * (1 - (1 - (k + 1) / 10) ** (1 / 3)))
            tr.add(chime(1046, 0.05, 1.5), b['t0'] + 1.2)
        if p[0] == "title": tr.add(chime(784, 0.04, 1.2), b['t0'] - 0.2)
    # section beds
    for j, s in enumerate(SECS):
        end = SECS[j + 1][1] if j + 1 < len(SECS) else DUR
        if s[0] == "heart":
            k = s[1]
            while k < end - 0.3: tr.add(lubdub(0.07), k); tr.add(lubdub(0.045), k + 0.22); k += 60 / BPM
        if s[0] == "lungs":
            k = s[1]
            while k < end - 2: tr.add(pk.soft_noise(2.0, 40, 0.02), k); k += 4
        if s[0] == "gut":
            for q in range(12): tr.add(pk.bubble(0.02), s[1] + q * 0.6)
        if s[0] == "night": tr.add(pk.soft_noise(end - s[1], 25, 0.015), s[1])
    tr.add(chime(1318, 0.05, 3.0), BEATS[-1]['t0'])
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "/home/claude/long1/st")
    elif sys.argv[1] == "info":
        print(DUR, [(s[0], round(s[1], 1)) for s in SECS])
    else:
        audio("/home/claude/long1/a.wav"); encode(draw, NF, "/home/claude/long1/v.mp4"); mux("/home/claude/long1/v.mp4", "/home/claude/long1/a.wav", "/home/claude/long1/body24.mp4")
