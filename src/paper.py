"""Paper-cutout style demo: jointed paper puppet walking through a paper room (stop-motion feel)."""
import sys, math
import numpy as np, cairo
from common import W, H, FPS, encode, stills, Track, pluck, note, SR, mux

DUR = 10.0
NF = int(DUR * FPS)
STEP_FPS = 12                       # stop-motion: puppet poses update 12x per second
rng = np.random.default_rng(1)


# ---------- paper texture ----------
def make_texture(w, h, seed):
    r = np.random.default_rng(seed)
    n = r.normal(0, 1, (h // 4 + 2, w // 4 + 2))
    big = np.kron(n, np.ones((4, 4)))[:h, :w]
    fine = r.normal(0, 1, (h, w))
    fib = np.zeros((h, w))
    for _ in range(260):  # paper fibres
        x, y = r.integers(0, w), r.integers(0, h)
        L = r.integers(10, 40); a = r.uniform(0, math.pi)
        for k in range(L):
            xx, yy = int(x + k * math.cos(a)), int(y + k * math.sin(a))
            if 0 <= xx < w and 0 <= yy < h:
                fib[yy, xx] += 1
    v = 0.93 + 0.03 * big + 0.025 * fine - 0.05 * fib
    v = np.clip(v, 0.75, 1.0)
    g = (v * 255).astype(np.uint8)
    a = np.dstack([g, g, g, np.full_like(g, 255)])
    surf = cairo.ImageSurface.create_for_data(memoryview(np.ascontiguousarray(a)), cairo.FORMAT_ARGB32, w, h)
    return surf, a


TEX, _keep = make_texture(W, H, 7)


def rough_poly(pts, amp=2.2, seed=0, step=18):
    """resample polygon edges and jitter them for a torn-paper edge (deterministic)."""
    r = np.random.default_rng(seed)
    out = []
    n = len(pts)
    for i in range(n):
        (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % n]
        L = math.hypot(x1 - x0, y1 - y0)
        k = max(1, int(L / step))
        for j in range(k):
            u = j / k
            out.append((x0 + (x1 - x0) * u + r.normal(0, amp), y0 + (y1 - y0) * u + r.normal(0, amp)))
    return out


def rect_pts(x, y, w, h):
    return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]


def ellipse_pts(cx, cy, rx, ry, n=40):
    return [(cx + rx * math.cos(2 * math.pi * k / n), cy + ry * math.sin(2 * math.pi * k / n)) for k in range(n)]


def path(ctx, pts):
    ctx.move_to(*pts[0])
    for p in pts[1:]:
        ctx.line_to(*p)
    ctx.close_path()


def paper(ctx, pts, col, seed=0, shadow=(7, 9), sh_a=0.28, rough=2.0):
    p = rough_poly(pts, rough, seed) if rough else pts
    # layered soft-ish drop shadow
    for k, a in ((1.6, sh_a * 0.35), (1.0, sh_a * 0.6), (0.5, sh_a * 0.5)):
        ctx.save(); ctx.translate(shadow[0] * k, shadow[1] * k)
        path(ctx, p); ctx.set_source_rgba(0.12, 0.08, 0.05, a); ctx.fill(); ctx.restore()
    path(ctx, p); ctx.set_source_rgb(*col); ctx.fill_preserve()
    ctx.save(); ctx.clip()
    ctx.set_operator(cairo.OPERATOR_MULTIPLY)
    ctx.set_source_surface(TEX, (seed * 37) % 200 - 200, (seed * 53) % 200 - 200)
    ctx.paint()
    ctx.restore()
    ctx.new_path()


def pin(ctx, x, y, r=7):
    ctx.set_source_rgba(0, 0, 0, 0.3); ctx.arc(x + 2, y + 2, r, 0, 2 * math.pi); ctx.fill()
    g = cairo.RadialGradient(x - r * 0.3, y - r * 0.3, 1, x, y, r)
    g.add_color_stop_rgb(0, 1, 0.92, 0.6); g.add_color_stop_rgb(1, 0.62, 0.45, 0.15)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.fill()


def limb(ctx, x, y, ang, length, width, col, seed):
    """paper strip hanging from joint (x,y) at angle ang (0 = straight down). returns end point."""
    ex, ey = x + length * math.sin(ang), y + length * math.cos(ang)
    nx, ny = math.cos(ang) * width / 2, -math.sin(ang) * width / 2
    pts = [(x - nx, y - ny), (x + nx, y + ny), (ex + nx, ey + ny), (ex - nx, ey - ny)]
    paper(ctx, pts + [], col, seed=seed, shadow=(5, 7), sh_a=0.3, rough=1.2)
    return ex, ey


# ---------- palette (warm paper) ----------
WALL = (0.90, 0.84, 0.72); WALL2 = (0.86, 0.79, 0.66)
FLOOR = (0.72, 0.52, 0.34); FLOOR2 = (0.66, 0.47, 0.30)
GREEN = (0.40, 0.62, 0.36); GREEN2 = (0.30, 0.52, 0.30)
TERRA = (0.80, 0.42, 0.28); RED = (0.86, 0.30, 0.22); MUST = (0.92, 0.72, 0.30)
NAVY = (0.20, 0.27, 0.50); CREAM = (0.97, 0.94, 0.86); SKIN = (0.96, 0.78, 0.62); HAIR = (0.38, 0.24, 0.16)
TEAL = (0.30, 0.58, 0.60); SHOE = (0.25, 0.17, 0.12)

FLOOR_Y = 1380
SCROLL = 150          # px per second background scroll (parallax far layer slower)


def wall_layer(ctx, off):
    paper(ctx, rect_pts(-20, -20, W + 40, FLOOR_Y + 40), WALL, seed=1, shadow=(0, 0), rough=0)
    for k in range(-1, 10):
        x = k * 160 - (off * 0.5) % 160
        paper(ctx, rect_pts(x, 0, 80, FLOOR_Y), WALL2, seed=10 + k % 3, shadow=(0, 0), sh_a=0, rough=1.0)
    # skirting
    paper(ctx, rect_pts(-20, FLOOR_Y - 40, W + 40, 44), CREAM, seed=2, shadow=(0, 6), rough=1.5)


def floor_layer(ctx, off):
    paper(ctx, rect_pts(-20, FLOOR_Y, W + 40, H - FLOOR_Y + 20), FLOOR, seed=3, shadow=(0, 0), rough=0)
    for row in range(6):
        y = FLOOR_Y + 20 + row * 90
        shift = (row % 2) * 120
        for k in range(-1, 6):
            x = k * 240 + shift - off % 240
            paper(ctx, rect_pts(x, y, 230, 80), FLOOR2 if (k + row) % 2 else FLOOR, seed=40 + (k + row) % 5, shadow=(0, 3), sh_a=0.15, rough=1.0)


def props(ctx, off, t):
    span = 1400
    base = -(off % span)
    for rep in (0, 1):
        o = base + rep * span
        # framed chart poster
        paper(ctx, rect_pts(o + 260, 560, 420, 330), CREAM, seed=5, shadow=(8, 10))
        for i, (h, c) in enumerate([(120, MUST), (170, MUST), (230, RED)]):
            paper(ctx, rect_pts(o + 320 + i * 110, 840 - h, 60, h), c, seed=60 + i, shadow=(4, 5))
        paper(ctx, rect_pts(o + 300, 846, 340, 8), (0.3, 0.25, 0.2), seed=8, shadow=(2, 3))
        # desk + monitor
        paper(ctx, rect_pts(o + 820, 1080, 380, 26), (0.62, 0.42, 0.26), seed=9, shadow=(6, 9))
        paper(ctx, rect_pts(o + 850, 1106, 20, 270), (0.55, 0.37, 0.22), seed=11)
        paper(ctx, rect_pts(o + 1150, 1106, 20, 270), (0.55, 0.37, 0.22), seed=12)
        paper(ctx, rect_pts(o + 930, 900, 240, 160), (0.25, 0.28, 0.32), seed=13, shadow=(6, 8))
        paper(ctx, rect_pts(o + 945, 915, 210, 130), (0.62, 0.86, 0.92), seed=14, shadow=(0, 0))
        for i, h in enumerate([40, 70, 55, 95]):
            paper(ctx, rect_pts(o + 975 + i * 40, 1030 - h, 22, h), [MUST, RED, MUST, RED][i], seed=70 + i, shadow=(2, 2), rough=0.6)
        paper(ctx, rect_pts(o + 1030, 1060, 40, 22), (0.25, 0.28, 0.32), seed=15)
        # potted plant
        paper(ctx, [(o + 80, 1250), (o + 200, 1250), (o + 185, 1380), (o + 95, 1380)], TERRA, seed=16)
        for i in range(7):
            a = -1.2 + i * 0.4 + 0.04 * math.sin(t * 1.5 + i)
            bx, by = o + 140, 1255
            tip = (bx + 230 * math.sin(a), by - 260 * math.cos(a) * 0.9)
            paper(ctx, [(bx - 10, by), tip, (bx + 10, by)], GREEN if i % 2 else GREEN2, seed=80 + i, shadow=(5, 7), rough=1.2)
    # hanging lamp (gentle sway, not scrolling-repeated to keep it simple)
    sw = 0.05 * math.sin(t * 1.3)
    lx = W * 0.47 - (off * 1.0) % span + 0
    for lxx in (lx, lx + span):
        ctx.set_source_rgba(0.15, 0.12, 0.1, 0.9); ctx.set_line_width(3)
        ex, ey = lxx + 380 * math.sin(sw), 380 * math.cos(sw)
        ctx.move_to(lxx, 0); ctx.line_to(ex, ey); ctx.stroke()
        paper(ctx, [(ex - 70, ey + 70), (ex - 30, ey), (ex + 30, ey), (ex + 70, ey + 70)], RED, seed=90, shadow=(6, 8))
        g = cairo.RadialGradient(ex, ey + 80, 10, ex, ey + 220, 320)
        g.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.30); g.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
        ctx.set_source(g); ctx.move_to(ex - 70, ey + 70); ctx.line_to(ex - 330, ey + 620); ctx.line_to(ex + 330, ey + 620); ctx.line_to(ex + 70, ey + 70); ctx.fill()


def puppet(ctx, cx, ground, ph):
    """jointed paper man, walk phase ph (radians)."""
    s = math.sin(ph); c = math.cos(ph)
    bob = -abs(math.sin(ph)) * 10
    hip = (cx, ground - 330 + bob)
    thigh, shin, foot = 160, 150, 70
    # legs (back leg first)
    for side, sgn, col in ((1, -1, (0.17, 0.23, 0.44)), (0, 1, NAVY)):
        a = sgn * 0.36 * s
        knee_bend = max(0, -sgn * s) * 0.8 + 0.05
        kx, ky = limb(ctx, hip[0], hip[1], a, thigh, 56, col, seed=200 + side)
        fx, fy = limb(ctx, kx, ky, a - knee_bend, shin, 48, col, seed=210 + side)
        paper(ctx, [(fx - 18, fy - 14), (fx + foot, fy - 10), (fx + foot + 6, fy + 14), (fx - 22, fy + 14)], SHOE, seed=220 + side, shadow=(4, 6), rough=1)
        pin(ctx, kx, ky, 6)
    # back arm
    sh = (cx + 6, hip[1] - 175)
    ex, ey = limb(ctx, sh[0], sh[1], -0.45 * s, 120, 40, (0.88, 0.85, 0.76), seed=230)
    hx, hy = limb(ctx, ex, ey, -0.45 * s - 0.35, 110, 36, (0.88, 0.85, 0.76), seed=231)
    paper(ctx, ellipse_pts(hx, hy + 6, 18, 18, 16), SKIN, seed=232, shadow=(3, 4), rough=0.8)
    # torso (shirt) + belt + tie
    paper(ctx, [(cx - 62, hip[1] - 200), (cx + 62, hip[1] - 200), (cx + 58, hip[1] + 10), (cx - 58, hip[1] + 10)], CREAM, seed=240)
    paper(ctx, rect_pts(cx - 60, hip[1] - 10, 120, 24), (0.15, 0.12, 0.1), seed=241, shadow=(2, 3), rough=0.8)
    paper(ctx, [(cx + 8, hip[1] - 190), (cx + 24, hip[1] - 190), (cx + 30, hip[1] - 60), (cx + 16, hip[1] - 40), (cx + 4, hip[1] - 60)], RED, seed=242, shadow=(3, 4), rough=0.8)
    for k in range(3):
        pin(ctx, cx - 18, hip[1] - 160 + k * 50, 5)
    pin(ctx, hip[0], hip[1], 8)
    # head
    hx0, hy0 = cx + 6, hip[1] - 270
    paper(ctx, rect_pts(cx - 12, hip[1] - 225, 28, 30), SKIN, seed=250, shadow=(3, 4), rough=0.6)
    paper(ctx, ellipse_pts(hx0, hy0, 50, 56, 30), SKIN, seed=251)
    hair = [(hx0 - 4 + 56 * math.cos(a), hy0 - 6 + 60 * math.sin(a)) for a in np.linspace(math.pi * 0.95, math.pi * 1.95, 16)]
    hair += [(hx0 + 30, hy0 - 30), (hx0 - 20, hy0 - 22), (hx0 - 40, hy0 + 14)]
    paper(ctx, hair, HAIR, seed=252, shadow=(3, 4), rough=1)
    ctx.set_source_rgb(0.15, 0.1, 0.08); ctx.arc(hx0 + 26, hy0 - 4, 5, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(0.95, 0.5, 0.45, 0.55); ctx.arc(hx0 + 22, hy0 + 18, 9, 0, 2 * math.pi); ctx.fill()
    # front arm
    ex, ey = limb(ctx, sh[0], sh[1], 0.45 * s, 120, 42, CREAM, seed=260)
    hx, hy = limb(ctx, ex, ey, 0.45 * s - 0.35, 110, 38, CREAM, seed=261)
    paper(ctx, ellipse_pts(hx, hy + 6, 19, 19, 16), SKIN, seed=262, shadow=(3, 4), rough=0.8)
    pin(ctx, sh[0], sh[1], 7); pin(ctx, ex, ey, 6)


def draw(ctx, fi):
    t = fi / FPS
    ts = math.floor(t * STEP_FPS) / STEP_FPS        # stop-motion time
    off = ts * SCROLL
    wall_layer(ctx, off)
    props(ctx, off, ts)
    floor_layer(ctx, off)
    # contact shadow
    ctx.save(); ctx.translate(W * 0.5, FLOOR_Y + 30); ctx.scale(1, 0.18)
    ctx.set_source_rgba(0.1, 0.06, 0.03, 0.25); ctx.arc(0, 0, 190, 0, 2 * math.pi); ctx.fill(); ctx.restore()
    ctx.save(); ctx.translate(W * 0.5, FLOOR_Y + 30); ctx.scale(1.3, 1.3); ctx.translate(-W * 0.5, -(FLOOR_Y + 30))
    puppet(ctx, W * 0.5, FLOOR_Y + 30, ts * 2 * math.pi * 0.9)
    ctx.restore()
    # soft vignette
    g = cairo.RadialGradient(W / 2, H / 2, 500, W / 2, H / 2, 1250)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.1, 0.05, 0, 0.35)
    ctx.set_source(g); ctx.paint()


def audio(path):
    tr = Track(DUR)
    r = np.random.default_rng(3)
    # soft paper footsteps on each foot plant
    for k in range(int(DUR * 0.9 * 2)):
        tt = (k + 0.5) / (0.9 * 2)
        n = int(SR * 0.12)
        x = r.normal(0, 1, n)
        x = np.convolve(x, np.ones(25) / 25, mode="same")
        tr.add(x * np.exp(-np.arange(n) / 900) * 0.5, tt)
    # gentle music box melody
    mel = [0, 2, 4, 2, 5, 4, 2, 0, 1, 2, 4, 7, 5, 4, 2, 0]
    for i, st in enumerate(mel * 2):
        tr.add(pluck(note(st + 5, 261.63), 0.9, 0.12, 4), i * 0.6)
    tr.save(path, DUR)


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        stills(draw, [int(x) for x in sys.argv[2:]], "pp")
    else:
        audio("pp.wav"); encode(draw, NF, "pp_v.mp4"); mux("pp_v.mp4", "pp.wav", "paper_cutout_demo.mp4")
