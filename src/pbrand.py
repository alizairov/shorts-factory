"""shared paper-style helpers: softer texture, channel watermark, natural paper sounds"""
import math
import numpy as np, cairo
from common import SR
from paper import paper
from paperkit import *
import paper as _pp, paperkit as _pk
_pp.TEX_A = 0.45; _pk.BG_TEX_A = 0.35
from PIL import Image as _Im
_lg = _Im.open('/home/claude/shorts-factory/branding/channel_logo.png').convert('RGBA').resize((120, 120), _Im.LANCZOS)
_m = _Im.new('L', (120, 120), 0)
from PIL import ImageDraw as _D; _D.Draw(_m).ellipse((0, 0, 119, 119), fill=255); _lg.putalpha(_m)
_a = np.array(_lg); _a = _a[:, :, [2, 1, 0, 3]].copy(); _a[:, :, :3] = (_a[:, :, :3].astype(int) * _a[:, :, 3:4] // 255).astype(np.uint8)
LOGO = cairo.ImageSurface.create_for_data(memoryview(_a), cairo.FORMAT_ARGB32, 120, 120)


def brand(ctx):
    x, y = 70, 120
    ctx.set_source_rgba(0.12, 0.08, 0.05, 0.25); ctx.arc(x + 63, y + 65, 64, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_rgb(*CREAM); ctx.arc(x + 60, y + 60, 66, 0, 2 * math.pi); ctx.fill()
    ctx.set_source_surface(LOGO, x, y); ctx.paint()
    tag(ctx, '@Visual.Brainer', x + 300, y + 76, 40, seed=95)


DUR = 16.0
NF = int(DUR * FPS)
SKY, SKY2 = (0.62, 0.82, 0.93), (0.84, 0.92, 0.95)
GREY, GREY2 = (0.66, 0.68, 0.75), (0.55, 0.57, 0.65)
WOOD, WOOD2 = (0.66, 0.45, 0.28), (0.55, 0.37, 0.22)
CLOUD = (0.99, 0.98, 0.96)
FX, FY, L, HANG = 540, 1020, 290, 190   # fulcrum, half-beam, string length
TH0 = -0.30                              # cloud side down
T_LAND, T_REV, T_ADD0, T_ADD1, T_UP, T_BACK, T_RET = 0.35, 2.2, 3.2, 9.0, 10.2, 13.4, 14.6


def cl(u): return max(0.0, min(1.0, u))


def window(t, t0, t1, d=0.25):
    return cl((t - t0) / d) * cl((t1 - t) / d)


def fade_in(t, t0, d=0.3):
    return cl((t - t0) / d)


# ---------- natural paper sounds ----------
_g = np.random.default_rng(5)


def rustle(d, amp=0.1, rate=260, grain=(60, 260)):
    n = int(SR * d); x = np.zeros(n + 400)
    for p in (_g.random(int(rate * d)) * n).astype(int):
        L_ = _g.integers(*grain); m = np.arange(L_)
        x[p:p + L_] += _g.normal(0, 1, L_) * np.exp(-m / (L_ / 4)) * _g.uniform(0.2, 1)
    x = x[:n]; x = x - 0.85 * np.concatenate([[0], x[:-1]])
    env = np.sin(np.pi * np.arange(n) / n) ** 0.6
    return x / (np.max(np.abs(x)) + 1e-9) * env * amp


def slide(d=0.5, amp=0.08):
    x = soft_noise(d, 6, 1.0) + 0.3 * rustle(d, 1.0, 120)
    m = np.arange(len(x)) / len(x)
    return x * np.sin(np.pi * m) ** 1.5 * amp


def thud(amp=0.3):
    m = np.arange(int(SR * 0.3)) / SR
    return (np.sin(2 * np.pi * 70 * m) * np.exp(-m * 18) + 0.3 * np.sin(2 * np.pi * 140 * m) * np.exp(-m * 30)) * amp


def flick(amp=0.05):
    return rustle(0.05, amp, 900, (30, 90))


