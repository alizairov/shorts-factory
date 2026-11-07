"""Channel logo (800x800) and banner (2560x1440) in the paper-cutout style."""
import math
import numpy as np, cairo
import paper as P
from paper import paper, pin, rect_pts, ellipse_pts, make_texture
from common import label, FONT

TEAL1, TEAL2 = (0.24, 0.60, 0.66), (0.10, 0.33, 0.42)
CREAM = (0.98, 0.95, 0.87); INK = (0.16, 0.12, 0.14)
OCTO, OCTO2 = (0.93, 0.47, 0.55), (0.83, 0.36, 0.46)


def octo_head(ctx, cx, cy, s, seed=0):
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s)
    # tentacles
    for i in range(6):
        base = -150 + i * 60
        x, y = base, 70
        for k in range(6):
            a = (i - 2.5) * 0.18 + 0.3 * math.sin(k * 0.9 + i)
            L, w = 46 - k * 3, 52 - k * 7
            nx, ny = x + L * math.sin(a), y + L * math.cos(a)
            paper(ctx, [(x - w / 2, y), (x + w / 2, y), (nx + w / 2 - 3, ny), (nx - w / 2 + 3, ny)], OCTO if i % 2 else OCTO2, seed=seed + i * 10 + k, shadow=(4, 6), rough=0.8)
            x, y = nx, ny
    pts = [(190 * math.cos(a), -40 + 230 * math.sin(a)) for a in np.linspace(math.pi, 2 * math.pi, 28)]
    pts += [(190, -40), (165, 95), (-165, 95), (-190, -40)]
    paper(ctx, pts, OCTO, seed=seed + 100, shadow=(9, 12))
    for (dx, dy, r) in [(-80, -170, 20), (70, -195, 15), (110, -110, 16)]:
        paper(ctx, ellipse_pts(dx, dy, r, r, 14), OCTO2, seed=seed + 110 + r, shadow=(2, 3), rough=0.5)
    for ex in (-68, 68):
        paper(ctx, ellipse_pts(ex, 30, 40, 44, 22), CREAM, seed=seed + 120 + ex, shadow=(3, 4), rough=0.7)
        ctx.set_source_rgb(*INK); ctx.arc(ex + 7, 37, 17, 0, 2 * math.pi); ctx.fill()
        ctx.set_source_rgb(1, 1, 1); ctx.arc(ex + 13, 30, 6, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgba(0.98, 0.55, 0.55, 0.6)
    for ex in (-110, 110):
        ctx.arc(ex, 85, 18, 0, 2 * math.pi); ctx.fill()
    ctx.restore()


def bg(ctx, w, h, top, bot):
    g = cairo.LinearGradient(0, 0, 0, h)
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g); ctx.paint()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); ctx.set_source_surface(P.TEX, 0, 0); ctx.paint(); ctx.restore()


def logo(path_out):
    S = 800
    P.TEX, keep = make_texture(S + 256, S + 256, 3)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, S, S); ctx = cairo.Context(surf)
    bg(ctx, S, S, (0.99, 0.86, 0.58), (0.97, 0.66, 0.46))
    # layered paper rings (reads well when YouTube crops to a circle)
    for k, (r, col) in enumerate([(370, (0.97, 0.74, 0.50)), (330, TEAL1), (300, (0.18, 0.47, 0.55))]):
        paper(ctx, ellipse_pts(S / 2, S / 2, r, r, 60), col, seed=10 + k, shadow=(6, 9), rough=1.6)
    # bubbles
    for (x, y, r) in [(205, 260, 18), (590, 230, 14), (620, 330, 9), (180, 360, 10)]:
        ctx.set_source_rgba(1, 1, 1, 0.75); ctx.set_line_width(4); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    octo_head(ctx, S / 2, S / 2 + 30, 1.05, seed=200)
    surf.write_to_png(path_out)


def banner(path_out):
    Wb, Hb = 2560, 1440
    P.TEX, keep = make_texture(Wb + 256, Hb + 256, 5)
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, Wb, Hb); ctx = cairo.Context(surf)
    bg(ctx, Wb, Hb, (0.99, 0.84, 0.60), (0.96, 0.62, 0.45))
    # sea band across the middle (safe area is the central 1546x423 box, y 508–931)
    pts = [(x, 470 + 18 * math.sin(x / 120)) for x in range(-40, Wb + 80, 60)] + [(Wb + 40, 980), (-40, 980)]
    paper(ctx, pts, TEAL1, seed=20, shadow=(0, 8))
    pts = [(x, 940 + 22 * math.sin(x / 150 + 1)) for x in range(-40, Wb + 80, 60)] + [(Wb + 40, Hb + 20), (-40, Hb + 20)]
    paper(ctx, pts, (0.93, 0.83, 0.62), seed=21, shadow=(0, -8))
    # seaweed + bubbles at the sides
    for i, bx in enumerate([430, 490, 2080, 2140]):
        x, y = bx, 980
        for k in range(6):
            a = math.pi + 0.25 * math.sin(k * 0.8 + i)
            nx, ny = x + 60 * math.sin(a), y + 60 * math.cos(a)
            w = 30 - k * 3
            paper(ctx, [(x - w / 2, y), (x + w / 2, y), (nx + w / 2, ny), (nx - w / 2, ny)], [(0.32, 0.62, 0.42), (0.24, 0.52, 0.38)][k % 2], seed=30 + i * 10 + k, shadow=(4, 6), rough=1)
            x, y = nx, ny
    for (x, y, r) in [(620, 560, 16), (660, 600, 10), (1990, 600, 14), (2030, 660, 9), (1960, 545, 12)]:
        ctx.set_source_rgba(1, 1, 1, 0.75); ctx.set_line_width(4); ctx.arc(x, y, r, 0, 2 * math.pi); ctx.stroke()
    # mascot on the left inside the safe area
    octo_head(ctx, 700, 715, 0.5, seed=300)
    # little fact props on the right: Saturn, banana, cube
    sx, sy, r = 1880, 720, 70
    ctx.save(); ctx.translate(sx, sy); ctx.scale(1, 0.3); ctx.set_source_rgb(0.98, 0.88, 0.65); ctx.set_line_width(r * 0.28); ctx.arc(0, 0, r * 1.75, math.pi, 2 * math.pi); ctx.stroke(); ctx.restore()
    paper(ctx, ellipse_pts(sx, sy, r, r, 30), (0.96, 0.84, 0.55), seed=400)
    ctx.save(); ctx.translate(sx, sy); ctx.scale(1, 0.3); ctx.set_source_rgb(0.98, 0.88, 0.65); ctx.set_line_width(r * 0.28); ctx.arc(0, 0, r * 1.75, 0, math.pi); ctx.stroke(); ctx.restore()
    # text on torn paper strips (centre, within safe area)
    def strip(txt, x, y, size, col, bgc, seed):
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(size)
        w = ctx.text_extents(txt).x_advance; pad = size * 0.4
        paper(ctx, rect_pts(x - w / 2 - pad, y - size * 0.95, w + 2 * pad, size * 1.32), bgc, seed=seed, shadow=(6, 9), rough=2.2)
        label(ctx, txt, x, y, size, col=col, shadow=0)
    strip("WEIRD FACTS", 1300, 700, 120, INK, CREAM, 500)
    strip("space · animals · history · science", 1300, 815, 50, (0.83, 0.36, 0.46), CREAM, 501)
    strip("new short every day", 1300, 905, 40, INK, (0.95, 0.88, 0.70), 502)
    surf.write_to_png(path_out)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2: logo("channel_logo.png")
    banner("channel_banner.png")
    print("ok")
