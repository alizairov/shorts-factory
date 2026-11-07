"""Flat-vector explainer demo: your stomach lining renews every 3–5 days.
Character with blinks/expressions, camera zoom in/out, magnifier callout, pop labels, glow."""
import sys, math, random
import numpy as np, cairo
from common import W, H, FPS, SR, encode, stills, Track, pluck, note, mux, label
from pbrand import LOGO
import paperkit as pk

DUR = 15.0
NF = int(DUR * FPS)
SKIN, SKIN2 = (1.0, 0.70, 0.52), (0.93, 0.56, 0.42)
HAIR, HAIR2 = (0.18, 0.42, 0.52), (0.13, 0.32, 0.42)
SHIRT, PANTS = (0.36, 0.80, 0.62), (0.28, 0.24, 0.52)
INK = (0.17, 0.08, 0.22)
PINKS, PINKD = (1.0, 0.42, 0.62), (0.86, 0.22, 0.45)
LIME, CYAN, YEL = (0.80, 0.95, 0.30), (0.45, 0.90, 1.0), (1.0, 0.85, 0.25)
STOM = (575, 1185)   # stomach position in world space


def cl(u): return max(0.0, min(1.0, u))
def ease(u): u = cl(u); return u * u * (3 - 2 * u)
def lerp(a, b, u): return a + (b - a) * u
def popk(u):
    u = cl(u)
    return 1 + 0.25 * math.sin(u * math.pi) * (1 - u) * 2.2 if u < 1 else 1.0


def rrect(ctx, x, y, w, h, r):
    ctx.new_sub_path(); ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi); ctx.close_path()


def ell(ctx, x, y, rx, ry):
    ctx.save(); ctx.translate(x, y); ctx.scale(max(rx, 0.01), max(ry, 0.01)); ctx.arc(0, 0, 1, 0, 2 * math.pi); ctx.restore()


def tagbox(ctx, txt, x, y, size, bg, fg=(1, 1, 1), a=1.0, k=1.0, pointer=True):
    """flat label with a little pointer under it; (x, y) = pointer tip"""
    if a <= 0.01: return
    ctx.save(); ctx.translate(x, y); ctx.scale(k, k)
    ctx.select_font_face("Inter Display Black"); ctx.set_font_size(size)
    w = ctx.text_extents(txt).x_advance; pad = size * 0.4; h = size * 1.3
    by = -h - (size * 0.35 if pointer else -h / 2)
    ctx.push_group()
    rrect(ctx, -w / 2 - pad, by, w + 2 * pad, h, size * 0.18); ctx.set_source_rgb(*bg); ctx.fill()
    if pointer:
        ctx.move_to(-size * 0.3, by + h - 1); ctx.line_to(size * 0.3, by + h - 1); ctx.line_to(0, 0); ctx.close_path(); ctx.fill()
    label(ctx, txt, 0, by + h * 0.72, size, col=fg, shadow=0)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(a); ctx.restore()


def sparkle(ctx, x, y, r, a):
    ctx.set_source_rgba(1, 1, 1, a)
    ctx.move_to(x, y - r)
    for ang in range(1, 9):
        rr = r if ang % 2 == 0 else r * 0.22
        th = -math.pi / 2 + ang * math.pi / 4
        ctx.line_to(x + rr * math.cos(th), y + rr * math.sin(th))
    ctx.close_path(); ctx.fill()


# ---------------- character ----------------
BLINKS = [1.3, 3.9, 8.0, 13.9]


def blink(t):
    return min([1.0] + [cl(abs(t - b) / 0.09) for b in BLINKS])     # 1 = open, 0 = closed


def stomach_shape(ctx, x, y, s):
    ctx.move_to(x + 10 * s, y - 120 * s)
    ctx.curve_to(x + 15 * s, y - 60 * s, x + 95 * s, y - 70 * s, x + 80 * s, y + 10 * s)
    ctx.curve_to(x + 65 * s, y + 85 * s, x - 70 * s, y + 90 * s, x - 85 * s, y + 35 * s)


def character(ctx, t, xray):
    bob = 6 * math.sin(t * 2.2)
    cx, hy = 540, 640 + bob
    surprised = cl(t / 0.3) * (1 - ease((t - 13.2) / 0.6))
    # legs + body
    ctx.set_source_rgb(*PANTS)
    for dx in (-85, 85):
        rrect(ctx, cx + dx - 70, 1380, 140, 520, 60); ctx.fill()
    ctx.push_group()
    rrect(ctx, cx - 210, 860 + bob * 0.5, 420, 600, 150); ctx.set_source_rgb(*SHIRT); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.12); rrect(ctx, cx - 180, 880 + bob * 0.5, 120, 520, 60); ctx.fill()
    ell(ctx, cx, 870 + bob * 0.5, 95, 40); ctx.set_source_rgb(*SKIN2); ctx.fill()
    ctx.pop_group_to_source(); ctx.paint_with_alpha(1 - 0.72 * xray)
    # glowing stomach (always under the shirt, revealed by x-ray)
    gx, gy = STOM
    g = cairo.RadialGradient(gx, gy, 10, gx, gy, 330)
    glow = 0.55 * cl(t / 0.4) + 0.2 * math.sin(t * 4)
    g.add_color_stop_rgba(0, 1, 1, 0.95, cl(glow + 0.2 * xray)); g.add_color_stop_rgba(1, 1, 1, 0.9, 0)
    ctx.set_source(g); ell(ctx, gx, gy, 330, 330); ctx.fill()
    if xray > 0.01:
        ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        for w, c, a in [(96, (1, 0.95, 0.85), 0.9), (70, PINKS, 1.0), (30, PINKD, 0.6)]:
            stomach_shape(ctx, gx, gy, 1.0); ctx.set_line_width(w); ctx.set_source_rgba(*c, a * xray); ctx.stroke()
    for k in range(9):
        ph = (t * 0.7 + k / 9) % 1
        ang = k * 2.4
        sparkle(ctx, gx + math.cos(ang) * (90 + 150 * ph), gy + math.sin(ang) * (90 + 150 * ph), 22 * (1 - ph), 0.9 * (1 - ph) * cl(t / 0.5))
    # arms (hands raised in surprise)
    ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(78)
    for sd in (-1, 1):
        sx, sy = cx + sd * 185, 930 + bob * 0.5
        wav = 10 * math.sin(t * 3 + sd)
        ex, ey = cx + sd * 250, 1150 + wav
        hx, hy2 = cx + sd * 150, 1040 - 40 * surprised + wav
        ctx.set_source_rgb(*SHIRT); ctx.move_to(sx, sy); ctx.line_to(ex, ey); ctx.stroke()
        ctx.set_source_rgb(*SKIN); ctx.move_to(ex, ey); ctx.line_to(hx, hy2); ctx.stroke()
        ell(ctx, hx, hy2 - 10, 46, 46); ctx.fill()
    # head
    ctx.set_source_rgb(*HAIR2); ell(ctx, cx, hy + 10, 225, 245); ctx.fill()
    ctx.set_source_rgb(*SKIN2); ell(ctx, cx - 180, hy + 30, 40, 52); ctx.fill(); ell(ctx, cx + 180, hy + 30, 40, 52); ctx.fill()
    ctx.set_source_rgb(*SKIN); ell(ctx, cx, hy + 20, 180, 200); ctx.fill()
    ctx.set_source_rgb(*HAIR)   # bangs
    ctx.move_to(cx - 200, hy - 20); ctx.curve_to(cx - 190, hy - 230, cx + 190, hy - 250, cx + 205, hy - 30)
    ctx.curve_to(cx + 120, hy - 120, cx + 30, hy - 60, cx - 40, hy - 150); ctx.curve_to(cx - 90, hy - 80, cx - 160, hy - 60, cx - 200, hy - 20); ctx.fill()
    ctx.set_source_rgb(*HAIR); ell(ctx, cx, hy - 250, 70, 62); ctx.fill()     # bun
    # eyes with blinks + look direction
    look = 18 * ease(cl((t - 3.0) / 0.6)) * (1 - ease(cl((t - 12.8) / 0.6)))
    op = blink(t)
    brow = 22 * surprised + 6
    for sd in (-1, 1):
        ex_, ey_ = cx + sd * 72, hy + 30
        ctx.set_source_rgb(1, 1, 1); ell(ctx, ex_, ey_, 42, 50 * op + 2); ctx.fill()
        if op > 0.15:
            ctx.set_source_rgb(*INK); ell(ctx, ex_ + 4, ey_ + look * 0.6 + 6, 26, 30 * op); ctx.fill()
            ctx.set_source_rgb(1, 1, 1); ell(ctx, ex_ + 13, ey_ - 6, 8, 8 * op); ctx.fill()
        ctx.set_source_rgb(*HAIR2); ctx.set_line_width(16); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(ex_ - 38, ey_ - 72 - brow + sd * 4); ctx.curve_to(ex_ - 10, ey_ - 92 - brow, ex_ + 15, ey_ - 92 - brow, ex_ + 40, ey_ - 76 - brow - sd * 4); ctx.stroke()
    # cheeks
    ctx.set_source_rgba(1, 0.45, 0.45, 0.35); ell(ctx, cx - 120, hy + 100, 34, 20); ctx.fill(); ell(ctx, cx + 120, hy + 100, 34, 20); ctx.fill()
    # mouth: "o" when surprised, smile at the end
    smile = ease(cl((t - 13.3) / 0.5))
    ctx.set_source_rgb(0.62, 0.12, 0.22)
    if smile < 0.5:
        ell(ctx, cx, hy + 120, 30 * (0.6 + 0.4 * surprised), 38 * (0.5 + 0.5 * surprised)); ctx.fill()
    else:
        ctx.set_line_width(14); ctx.arc(cx, hy + 90, 55, 0.2 * math.pi, 0.8 * math.pi); ctx.stroke()


# ---------------- magnifier: lining cells conveyor ----------------
def lining(ctx, cx, cy, R, t, speed):
    # acid (top), mucus band, cell layer moving up, deeper stem cells (bottom)
    ctx.set_source_rgb(0.22, 0.10, 0.30); ctx.paint()
    rnd = random.Random(3)
    for k in range(26):
        bx = cx - R + rnd.uniform(0, 2 * R); by = cy - R + ((rnd.uniform(0, R * 0.8) - t * 60) % (R * 0.8))
        ctx.set_source_rgba(*LIME, 0.55); ell(ctx, bx, by, rnd.uniform(6, 16), rnd.uniform(6, 16)); ctx.fill()
    my = cy - R * 0.12
    ctx.move_to(cx - R, my)
    for i in range(0, 41):
        x = cx - R + i * 2 * R / 40
        ctx.line_to(x, my + 12 * math.sin(i * 0.7 + t * 2))
    ctx.line_to(cx + R, my + 70); ctx.line_to(cx - R, my + 70); ctx.close_path()
    ctx.set_source_rgba(0.65, 0.88, 1.0, 0.8); ctx.fill()
    top = my + 70
    cw, ch = 62, 92
    off = (t * speed) % ch
    for col in range(-7, 8):
        x = cx + col * cw - cw / 2
        for row in range(-1, 7):
            y = top + row * ch - off + (col % 2) * ch * 0.5
            depth = cl((y - top) / (ch * 5))
            shed = cl((top + 10 - y) / ch)          # cells pushed past the surface fade and drift off
            if y + ch < top - ch: continue
            c = tuple(lerp(PINKS[i], (1.0, 0.75, 0.82)[i], depth) for i in range(3))
            ctx.save(); ctx.translate(0, -shed * 30)
            rrect(ctx, x + 4, y + 4, cw - 8, ch - 8, 18); ctx.set_source_rgba(*c, 1 - shed); ctx.fill()
            ctx.set_source_rgba(*PINKD, 0.9 * (1 - shed)); ell(ctx, x + cw / 2, y + ch / 2, 11, 11); ctx.fill()
            ctx.restore()


def magnifier(ctx, t, a, k, speed):
    mx, my, R = 540, 780, 270
    sx, sy = 540, 1500
    ctx.set_source_rgba(*LIME, a); ctx.set_line_width(14)
    ctx.move_to(sx, sy); ctx.line_to(mx, my + R * k); ctx.stroke()
    ell(ctx, sx, sy, 24 * k, 24 * k); ctx.fill()
    ctx.save(); ell(ctx, mx, my, R * k, R * k); ctx.clip()
    ctx.push_group(); lining(ctx, mx, my, R, t, speed); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    ctx.restore()
    ctx.set_source_rgba(*LIME, a); ctx.set_line_width(16); ell(ctx, mx, my, R * k, R * k); ctx.stroke()
    return mx, my, R


def draw(ctx, fi):
    t = fi / FPS
    z = ease(cl((t - 2.9) / 1.4)) * (1 - ease(cl((t - 12.5) / 1.3)))
    # background: warm outside, deep purple when we "go inside"
    g = cairo.LinearGradient(0, 0, 0, H)
    top = tuple(lerp(a, b, z) for a, b in zip((1.0, 0.58, 0.42), (0.36, 0.12, 0.48)))
    bot = tuple(lerp(a, b, z) for a, b in zip((1.0, 0.84, 0.48), (0.55, 0.18, 0.62)))
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot); ctx.set_source(g); ctx.paint()
    # rays behind the character
    ctx.save(); ctx.translate(540, 1000)
    for k in range(14):
        ctx.rotate(math.pi / 7)
        ctx.move_to(0, 0); ctx.line_to(1400, -110); ctx.line_to(1400, 110); ctx.close_path()
        ctx.set_source_rgba(1, 1, 1, 0.07 * (1 - z)); ctx.fill()
    ctx.restore()
    # camera
    zoom = 1 + 3.2 * z
    fx, fy = lerp(540, STOM[0], z), lerp(1000, STOM[1], z)
    ctx.save(); ctx.translate(540, lerp(1000, 1500, z)); ctx.scale(zoom, zoom); ctx.translate(-fx, -fy)
    character(ctx, t, z)
    ctx.restore()
    # magnifier with the lining
    ma = cl((t - 5.0) / 0.25) * (1 - cl((t - 12.2) / 0.3))
    if ma > 0.01:
        speed = 40 + 260 * ease(cl((t - 9.6) / 0.8))
        mx, my, R = magnifier(ctx, t, ma, popk((t - 5.0) / 0.45), speed)
        tagbox(ctx, "Acid", mx - 150, my - 150, 48, (0.42, 0.62, 0.10), a=ma * cl((t - 5.8) / 0.2), k=popk((t - 5.8) / 0.35))
        tagbox(ctx, "Mucus", mx + 160, my - 20, 48, (0.20, 0.55, 0.85), a=ma * cl((t - 6.4) / 0.2), k=popk((t - 6.4) / 0.35))
        tagbox(ctx, "Lining cells", mx - 40, my + 150, 50, PINKD, a=ma * cl((t - 7.0) / 0.2), k=popk((t - 7.0) / 0.35))
    # stomach label while zooming in
    tagbox(ctx, "Stomach", 540, 960, 64, PINKD, a=cl((t - 4.2) / 0.2) * (1 - cl((t - 5.0) / 0.2)), k=popk((t - 4.2) / 0.35))
    # day counter
    if 9.6 < t < 12.3:
        d = min(5, 1 + int((t - 9.8) / 0.45))
        a = cl((t - 9.6) / 0.2) * (1 - cl((t - 12.0) / 0.3))
        ctx.push_group()
        rrect(ctx, 830, 560, 190, 210, 30); ctx.set_source_rgb(1, 1, 1); ctx.fill()
        rrect(ctx, 830, 560, 190, 66, 30); ctx.set_source_rgb(*PINKD); ctx.fill(); ctx.rectangle(830, 593, 190, 33); ctx.fill()
        label(ctx, "DAY", 925, 610, 38, shadow=0)
        label(ctx, str(d), 925, 735, 110, col=INK, shadow=0)
        ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    # headline text (top band)
    tagbox(ctx, "YOUR STOMACH", 540, 290, 84, (1, 1, 1), fg=PINKD, a=1 - cl((t - 4.6) / 0.3) + cl((t - 13.4) / 0.3), pointer=False)
    tagbox(ctx, "REBUILDS ITSELF", 540, 400, 84, PINKD, a=1 - cl((t - 4.6) / 0.3) + cl((t - 13.4) / 0.3), pointer=False)
    tagbox(ctx, "EVERY 3–5 DAYS", 540, 380, 88, (1, 1, 1), fg=PINKD, a=cl((t - 9.7) / 0.25) * (1 - cl((t - 13.0) / 0.3)), k=popk((t - 9.7) / 0.4), pointer=False)
    # brand
    ctx.set_source_rgb(1, 1, 1); ell(ctx, 130, 150, 66, 66); ctx.fill()
    ctx.set_source_surface(LOGO, 70, 90); ctx.paint()
    tagbox(ctx, "@Visual.Brainer", 360, 150, 38, (1, 1, 1), fg=INK, pointer=False)


# ---------------- audio ----------------
def pad(tr, dur, vol=0.045):
    chords = [[0, 4, 7, 11], [5, 9, 12, 16], [2, 5, 9, 12], [7, 11, 14, 17]]
    seg = 4.0
    for i in range(int(dur / seg) + 1):
        L = seg + 1.5; tt = np.arange(int(SR * L)) / SR
        env = np.sin(np.pi * tt / L) ** 2
        sig = sum(np.sin(2 * np.pi * 261.63 * 2 ** (s / 12) * tt) + 0.5 * np.sin(2 * np.pi * 261.63 * 2 ** (s / 12) * 1.004 * tt) for s in chords[i % 4])
        tr.add(vol * env * sig / 6, max(0, i * seg - 0.75))


def chime(f, amp=0.06, d=1.5):
    tt = np.arange(int(SR * d)) / SR
    return amp * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(2 * np.pi * f * 2.01 * tt)) * np.exp(-tt * 3) * (1 - np.exp(-tt * 300))


def pop(amp=0.12):
    m = np.arange(int(SR * 0.12)) / SR
    f = 300 + 900 * np.exp(-m * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m * 30) * amp


def audio(path):
    tr = Track(DUR)
    pad(tr, DUR)
    for k in range(6): tr.add(chime(1046 * 2 ** ([0, 4, 7, 12, 7, 4][k] / 12), 0.03, 1.0), 0.1 + k * 0.35)
    for b in BLINKS: tr.add(pop(0.04), b)
    tr.add(pk.whoosh(1.2, 0.09), 2.9); tr.add(pk.whoosh(1.2, 0.08), 12.5)
    for tt in (4.2, 5.0, 5.8, 6.4, 7.0, 9.7): tr.add(pop(0.11), tt)
    for k in range(10): tr.add(pk.bubble(0.03), 5.4 + k * 0.4)
    for k in range(5): tr.add(chime(784 * 2 ** (k * 2 / 12), 0.05, 0.8), 9.8 + k * 0.45)
    tr.add(chime(1318, 0.06, 2.0), 13.4)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(float(x) * FPS) for x in sys.argv[2:]], "k1")
    else:
        audio("k1.wav"); encode(draw, NF, "k1_v.mp4"); mux("k1_v.mp4", "k1.wav", "k1_stomach.mp4")
