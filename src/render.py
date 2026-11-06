import sys, math, subprocess, colorsys, os
import numpy as np, cairo
import sim
from sim import W, H, FPS, CX, CY, RING

sim.GROW = 5.0
frames, bounces, end_t = sim.simulate(seed=7)
OUTRO = 3.2
N_MAIN = len(frames)
N_TOTAL = N_MAIN + int(OUTRO * FPS)

rng = np.random.default_rng(3)
parts = []
for i in range(420):
    a = rng.uniform(0, 2 * math.pi)
    sp = rng.uniform(250, 1700)
    parts.append((a, sp, rng.uniform(0, 1), rng.uniform(6, 22)))


def rgb(h, s=0.95, l=0.58):
    return colorsys.hls_to_rgb(h % 1, l, s)


def text(ctx, s, y, size, col=(1, 1, 1), alpha=1.0, shadow=True):
    ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    ext = ctx.text_extents(s)
    x = W / 2 - ext.width / 2 - ext.x_bearing
    if shadow:
        ctx.set_source_rgba(0, 0, 0, 0.55 * alpha)
        ctx.move_to(x + 4, y + 5)
        ctx.show_text(s)
    ctx.set_source_rgba(*col, alpha)
    ctx.move_to(x, y)
    ctx.show_text(s)


def background(ctx, t):
    g = cairo.RadialGradient(CX, CY, 50, CX, CY, 1300)
    h = (t * 0.02) % 1
    c1 = colorsys.hls_to_rgb(0.72 + h * 0.1, 0.12, 0.6)
    g.add_color_stop_rgb(0, *c1)
    g.add_color_stop_rgb(1, 0.02, 0.01, 0.05)
    ctx.set_source(g)
    ctx.paint()


def draw_ring(ctx, hue, flash):
    for w, a in [(60, 0.06), (38, 0.12), (24, 0.25)]:
        ctx.set_source_rgba(*rgb(hue), a + flash * 0.25)
        ctx.set_line_width(w + flash * 30)
        ctx.arc(CX, CY, RING + 8, 0, 2 * math.pi)
        ctx.stroke()
    ctx.set_source_rgba(*rgb(hue, 1, 0.65 + 0.3 * flash), 1)
    ctx.set_line_width(14)
    ctx.arc(CX, CY, RING + 8, 0, 2 * math.pi)
    ctx.stroke()


def draw_main(ctx, fi):
    fr = frames[fi]
    t = fr["t"]
    background(ctx, t)
    bx, by = CX + fr["p"][0], CY + fr["p"][1]
    r = fr["r"]
    past = [b for b in bounces if b["t"] <= t]
    last = past[-1] if past else None
    since = t - last["t"] if last else 9
    flash = max(0, 1 - since / 0.18)
    hue = fr["hue"]

    # string-art lines
    ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for b in past:
        x, y = CX + b["pt"][0], CY + b["pt"][1]
        ctx.set_source_rgba(*rgb(b["hue"]), 0.85)
        ctx.set_line_width(5)
        ctx.move_to(x, y)
        ctx.line_to(bx, by)
        ctx.stroke()
    draw_ring(ctx, hue, flash)
    # contact dots on ring
    for b in past:
        x, y = CX + b["pt"][0], CY + b["pt"][1]
        ctx.set_source_rgba(1, 1, 1, 0.9)
        ctx.arc(x, y, 7, 0, 2 * math.pi)
        ctx.fill()
    # ripples
    for b in past[-6:]:
        age = t - b["t"]
        if age < 0.5:
            k = age / 0.5
            x, y = CX + b["pt"][0], CY + b["pt"][1]
            ctx.set_source_rgba(*rgb(b["hue"], 1, 0.75), 1 - k)
            ctx.set_line_width(8 * (1 - k) + 1)
            ctx.arc(x, y, 20 + 140 * k, 0, 2 * math.pi)
            ctx.stroke()
    # motion trail
    for k in range(10, 0, -1):
        j = fi - k
        if j < 0:
            continue
        q = frames[j]
        ctx.set_source_rgba(*rgb(q["hue"]), 0.08 * (11 - k) / 10)
        ctx.arc(CX + q["p"][0], CY + q["p"][1], q["r"], 0, 2 * math.pi)
        ctx.fill()
    # ball with glow + squash on impact
    for gr, a in [(r + min(r * 0.6, 34), 0.10), (r + min(r * 0.3, 17), 0.18)]:
        ctx.set_source_rgba(*rgb(hue), a)
        ctx.arc(bx, by, gr, 0, 2 * math.pi)
        ctx.fill()
    g = cairo.RadialGradient(bx - r * 0.35, by - r * 0.35, r * 0.1, bx, by, r)
    g.add_color_stop_rgb(0, *rgb(hue, 1, 0.85))
    g.add_color_stop_rgb(1, *rgb(hue + 0.08, 1, 0.45))
    ctx.set_source(g)
    ctx.arc(bx, by, r, 0, 2 * math.pi)
    ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.95)
    ctx.set_line_width(5)
    ctx.arc(bx, by, r, 0, 2 * math.pi)
    ctx.stroke()

    # captions
    text(ctx, "IT GROWS", 260, 86)
    text(ctx, "EVERY BOUNCE", 365, 86, col=rgb(hue, 1, 0.68))
    n = fr["nb"]
    pop = 1 + 0.25 * flash
    text(ctx, f"{n}", 1640, int(130 * pop), col=rgb(hue, 1, 0.7))
    text(ctx, "bounces", 1720, 52, col=(1, 1, 1), alpha=0.8)
    pct = min(100, int(100 * (r - sim.R0) / (RING - 6 - sim.R0)))
    # progress bar
    bw = 640
    x0 = W / 2 - bw / 2
    ctx.set_source_rgba(1, 1, 1, 0.15)
    rrect(ctx, x0, 1790, bw, 26, 13)
    ctx.fill()
    ctx.set_source_rgb(*rgb(hue, 1, 0.62))
    rrect(ctx, x0, 1790, max(26, bw * pct / 100), 26, 13)
    ctx.fill()


def rrect(ctx, x, y, w, h, rad):
    ctx.new_sub_path()
    ctx.arc(x + w - rad, y + rad, rad, -math.pi / 2, 0)
    ctx.arc(x + w - rad, y + h - rad, rad, 0, math.pi / 2)
    ctx.arc(x + rad, y + h - rad, rad, math.pi / 2, math.pi)
    ctx.arc(x + rad, y + rad, rad, math.pi, 1.5 * math.pi)
    ctx.close_path()


def draw_outro(ctx, k):
    t = k / FPS
    background(ctx, end_t + t)
    hue0 = frames[-1]["hue"]
    # shockwaves
    for i in range(3):
        tt = t - i * 0.15
        if 0 < tt < 1.2:
            q = tt / 1.2
            ctx.set_source_rgba(*rgb(hue0 + i * 0.2, 1, 0.7), 1 - q)
            ctx.set_line_width(30 * (1 - q) + 2)
            ctx.arc(CX, CY, RING * (1 + q * 1.4), 0, 2 * math.pi)
            ctx.stroke()
    # particles
    for a, sp, hh, sz in parts:
        d = sp * (1 - math.exp(-t * 2.2)) / 2.2 + RING * 0.6
        x = CX + math.cos(a) * d
        y = CY + math.sin(a) * d + 300 * t * t
        al = max(0, 1 - t / 2.6)
        if al <= 0:
            continue
        ctx.set_source_rgba(*rgb(hh), al)
        ctx.arc(x, y, sz * (1 - t / 4), 0, 2 * math.pi)
        ctx.fill()
    # white flash
    fl = max(0, 1 - t / 0.35)
    if fl > 0:
        ctx.set_source_rgba(1, 1, 1, fl * 0.9)
        ctx.paint()
    # end text
    if t > 0.6:
        a = min(1, (t - 0.6) / 0.4)
        s = 1 + 0.15 * max(0, 1 - (t - 0.6) / 0.3)
        text(ctx, "BOOM!", CY + 40, int(200 * s), col=rgb(hue0 + t * 0.2, 1, 0.7), alpha=a)
        text(ctx, f"{len(bounces)} bounces", CY + 170, 70, alpha=a)
    if t > 1.4:
        a = min(1, (t - 1.4) / 0.4)
        text(ctx, "Watch it again?", 1680, 62, alpha=a * 0.9)


def frame(i):
    surf = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    ctx = cairo.Context(surf)
    if i < N_MAIN:
        draw_main(ctx, i)
    else:
        draw_outro(ctx, i - N_MAIN)
    return surf


if __name__ == "__main__":
    if sys.argv[1] == "stills":
        for i in [int(x) for x in sys.argv[2:]]:
            frame(i).write_to_png(f"still_{i}.png")
    else:
        out = sys.argv[2]
        tmp = out.replace(".mp4", ".tmp.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                              "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "18",
                              "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for i in range(N_TOTAL):
            p.stdin.write(bytes(frame(i).get_data()))
        p.stdin.close()
        if p.wait() == 0:
            os.replace(tmp, out)
        print("frames", N_TOTAL, "main", N_MAIN)
