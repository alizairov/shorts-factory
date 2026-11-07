"""Shared helpers for paper-cutout fact Shorts."""
import math
import numpy as np, cairo
from common import W, H, FPS, Track, pluck, note, SR, label, FONT
from paper import paper, pin, rect_pts, ellipse_pts, path, TEX

CREAM = (0.98, 0.95, 0.87); INK = (0.16, 0.12, 0.14)
STEP = 12


def stop(t):
    return math.floor(t * STEP) / STEP


def ease(u):
    u = min(max(u, 0), 1); return u * u * (3 - 2 * u)


def popu(u):
    u = min(max(u, 0), 1)
    return u * (1 + 0.35 * math.sin(u * math.pi))


def banner(ctx, txt, y, size, col=INK, bg=CREAM, a=1.0, seed=0):
    """short text on a torn paper strip — keep in the top reading zone (y 230–650)"""
    if a <= 0.01: return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(size)
    w = ctx.text_extents(txt).x_advance
    pad = size * 0.45
    ctx.push_group()
    paper(ctx, rect_pts(W / 2 - w / 2 - pad, y - size * 0.95, w + 2 * pad, size * 1.35), bg, seed=seed, shadow=(5, 7), rough=2.0)
    label(ctx, txt, W / 2, y, size, col=col, shadow=0)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(min(1, a))


def tag(ctx, txt, x, y, size, col=INK, bg=CREAM, seed=0, a=1.0):
    """small paper tag centred at x"""
    if a <= 0.01: return
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL); ctx.set_font_size(size)
    w = ctx.text_extents(txt).x_advance
    pad = size * 0.4
    ctx.push_group()
    paper(ctx, rect_pts(x - w / 2 - pad, y - size * 0.95, w + 2 * pad, size * 1.3), bg, seed=seed, shadow=(3, 5), rough=1.4)
    label(ctx, txt, x, y, size, col=col, shadow=0)
    ctx.pop_group_to_source(); ctx.paint_with_alpha(min(1, a))


def textured_bg(ctx, top, bot):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
    ctx.set_source(g); ctx.paint()
    ctx.save(); ctx.set_operator(cairo.OPERATOR_MULTIPLY); ctx.set_source_surface(TEX, 0, 0); ctx.paint(); ctx.restore()


def vignette(ctx, a=0.32):
    g = cairo.RadialGradient(W / 2, H / 2, 520, W / 2, H / 2, 1250)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0.08, 0.04, 0.02, a)
    ctx.set_source(g); ctx.paint()


def circle_pts(cx, cy, r, n=36):
    return ellipse_pts(cx, cy, r, r, n)


# ---------- ASMR sounds ----------
_r = np.random.default_rng(11)


def soft_noise(d, smooth=30, amp=0.2):
    n = int(SR * d)
    x = np.convolve(_r.normal(0, 1, n), np.ones(smooth) / smooth, mode="same")
    return x / (np.max(np.abs(x)) + 1e-9) * amp


def whoosh(d=0.6, amp=0.15):
    x = soft_noise(d, 20, 1.0)
    m = np.arange(len(x)) / len(x)
    return x * np.sin(np.pi * m) ** 2 * amp


def plop(f0=180, amp=0.35):
    m = np.arange(int(SR * 0.25)) / SR
    f = f0 + 500 * np.exp(-m * 25)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m * 14) * amp


def splash(amp=0.25, d=0.7):
    x = soft_noise(d, 8, 1.0)
    m = np.arange(len(x)) / SR
    return x * np.exp(-m * 6) * np.minimum(1, m * 60) * amp


def bubble(amp=0.06):
    m = np.arange(int(SR * 0.08)) / SR
    f = 500 + 2500 * m / 0.08
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m * 40) * amp


def tap(f=320, amp=0.25):
    m = np.arange(int(SR * 0.12)) / SR
    return (np.sin(2 * np.pi * f * m) + 0.4 * np.sin(2 * np.pi * f * 2.7 * m)) * np.exp(-m * 45) * amp


def musicbox(tr, dur, mel=(0, 4, 2, 4, 5, 4, 2, 0, 2, 4, 7, 5, 4, 2, 4, 0), gap=0.62, vol=0.07, base=261.63, start=0.2):
    i = 0
    while start + i * gap < dur - 0.3:
        tr.add(pluck(note(mel[i % len(mel)] + 5, base), 1.0, vol, 4), start + i * gap)
        i += 1


def ambience(tr, dur, amp=0.05, smooth=500):
    x = soft_noise(dur, smooth, amp)
    tr.add(x, 0)
