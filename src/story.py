"""Shared helpers for fact/story Shorts."""
import math, re
import numpy as np, cairo
from common import *

BG1, BG2 = (0.10, 0.05, 0.22), (0.02, 0.01, 0.07)
YEL, PINK, LIME, CYAN, PURP, ORNG = PAL[3], PAL[1], PAL[4], PAL[5], PAL[0], PAL[2]


def ease(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def eout(u):
    u = min(max(u, 0), 1); return 1 - (1 - u) ** 3


def pop(u):
    """overshoot pop 0->1"""
    u = min(max(u, 0), 1)
    return 1 + 0.18 * math.sin(u * math.pi) * (1 - u) * 3 if u < 1 else 1


def bg(ctx, t=0, hue_shift=0.0):
    g = cairo.RadialGradient(W / 2, H * 0.45, 50, W / 2, H * 0.45, 1300)
    g.add_color_stop_rgb(0, *BG1)
    g.add_color_stop_rgb(1, *BG2)
    ctx.set_source(g); ctx.paint()


def progress(ctx, t, dur):
    ctx.set_source_rgba(1, 1, 1, 0.12); ctx.rectangle(0, 0, W, 10); ctx.fill()
    ctx.set_source_rgb(*YEL); ctx.rectangle(0, 0, W * min(1, t / dur), 10); ctx.fill()


def rich(ctx, text, x, y, size, alpha=1.0, base=(1, 1, 1), hl=YEL, anchor="c"):
    """Draw a line where *words* are highlighted."""
    parts = re.split(r"(\*[^*]+\*)", text)
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    segs = [(p[1:-1], hl) if p.startswith("*") else (p, base) for p in parts if p]
    total = sum(ctx.text_extents(s).x_advance for s, _ in segs)
    cx = x - total / 2 if anchor == "c" else x
    for s, col in segs:
        ctx.set_source_rgba(0, 0, 0, 0.4 * alpha); ctx.move_to(cx + size * 0.04, y + size * 0.06); ctx.show_text(s)
        ctx.set_source_rgba(*col, alpha); ctx.move_to(cx, y); ctx.show_text(s)
        cx += ctx.text_extents(s).x_advance


def lines(ctx, txts, y, size, alpha=1.0, gap=1.18, **kw):
    for i, s in enumerate(txts):
        rich(ctx, s, W / 2, y + i * size * gap, size, alpha=alpha, **kw)


def card(ctx, x, y, w, h, r=28, rgba=(1, 1, 1, 0.07)):
    ctx.new_sub_path()
    ctx.arc(x + w - r, y + r, r, -math.pi / 2, 0); ctx.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    ctx.arc(x + r, y + h - r, r, math.pi / 2, math.pi); ctx.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    ctx.close_path(); ctx.set_source_rgba(*rgba); ctx.fill()


def fade_in(t, t0, d=0.35):
    return ease((t - t0) / d)


def window(t, t0, t1, d=0.3):
    """alpha that fades in at t0 and out at t1"""
    return ease((t - t0) / d) * (1 - ease((t - t1) / d))


# ---------- sound ----------
def whoosh(d=0.45, amp=0.12, seed=0):
    n = int(SR * d)
    x = np.random.default_rng(seed).normal(0, 1, n)
    # crude band-pass sweep via moving average of different widths
    env = np.sin(np.linspace(0, np.pi, n)) ** 2
    y = np.convolve(x, np.ones(12) / 12, mode="same") - np.convolve(x, np.ones(80) / 80, mode="same")
    return y * env * amp * 3


def boom(d=1.6, amp=0.6):
    t = np.arange(int(SR * d)) / SR
    return np.sin(2 * np.pi * (60 * t - 15 * t * t)) * np.exp(-t * 2.2) * amp


def ding(step=7, amp=0.22):
    return pluck(note(step, 523.25), 1.2, amp, 3.5)


def riser(d=1.5, amp=0.08):
    t = np.arange(int(SR * d)) / SR
    f = 200 + 900 * (t / d) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) * amp


def pill(ctx, txt, y, size, col=(1, 1, 1), alpha=1.0, bgc=(0.06, 0.03, 0.14), bga=0.78):
    """short neon text on a dark rounded card (top reading zone)"""
    if alpha <= 0.01: return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(size)
    w = ctx.text_extents(txt).x_advance
    pad = size * 0.45
    card(ctx, W / 2 - w / 2 - pad, y - size * 0.98, w + 2 * pad, size * 1.38, r=size * 0.3, rgba=(*bgc, bga * alpha))
    label(ctx, txt, W / 2, y, size, col=col, alpha=alpha, shadow=0)


def stop12(t):
    return math.floor(t * 12) / 12
