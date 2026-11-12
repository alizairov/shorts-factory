"""Shared template for one-rule satisfying simulation shorts (Visual Brain).
Layout: question (2 lines) + rule line on top, sim in the middle, two counters under it,
bottom 22% empty for the Shorts UI. Collision notes only, slow motion before the payoff,
0.5 s cross-fade back to frame 0 so the short loops."""
import math, colorsys
import numpy as np, cairo
from fx import W, H, FPS, SR, Track, glow, ball, chime, main as fx_main

CX, CY = 540, 930
YEL = (1, .82, .25)
FONT = "Inter Display"


def txt(ctx, s, x, y, size, col=(1, 1, 1), a=1.0, weight=cairo.FONT_WEIGHT_BOLD, anchor="c", track=0.0, face=FONT):
    ctx.select_font_face(face, cairo.FONT_SLANT_NORMAL, weight); ctx.set_font_size(size)
    if track:
        ws = [ctx.text_extents(ch).x_advance for ch in s]; tw = sum(ws) + track * (len(s) - 1)
    else:
        tw = ctx.text_extents(s).x_advance
    x0 = x - tw / 2 if anchor == "c" else (x if anchor == "l" else x - tw)
    yb = y + size * .35
    ctx.set_source_rgba(0, 0, 0, .35 * a)
    for dx, dy in ((0, 3),):
        ctx.move_to(x0 + dx, yb + dy)
        if track:
            xx = x0 + dx
            for ch, w_ in zip(s, ws): ctx.move_to(xx, yb + dy); ctx.show_text(ch); xx += w_ + track
        else: ctx.show_text(s)
    ctx.set_source_rgba(*col, a)
    if track:
        xx = x0
        for ch, w_ in zip(s, ws): ctx.move_to(xx, yb); ctx.show_text(ch); xx += w_ + track
    else:
        ctx.move_to(x0, yb); ctx.show_text(s)
    return tw


def rich(ctx, parts, y, size):
    """one centred line from [(text, colour), ...]"""
    ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(size)
    tw = sum(ctx.text_extents(p).x_advance for p, _ in parts); x = 540 - tw / 2
    for p, c in parts: x += txt(ctx, p, x, y, size, c, anchor="l")


def background(ctx, t):
    g = cairo.LinearGradient(0, 0, 0, H)
    g.add_color_stop_rgb(0, .13, .10, .30); g.add_color_stop_rgb(.55, .06, .09, .20); g.add_color_stop_rgb(1, .03, .17, .21)
    ctx.set_source(g); ctx.paint()
    ctx.set_line_width(1)
    ctx.set_source_rgba(1, 1, 1, .035)
    for x in range(0, W + 1, 60): ctx.move_to(x, 0); ctx.line_to(x, H)
    for y in range(0, H + 1, 60): ctx.move_to(0, y); ctx.line_to(W, y)
    ctx.stroke()


def header(ctx, q1, q2, rule):
    txt(ctx, "VISUAL BRAIN", 540, 238, 22, (1, 1, 1), .45, track=5)
    for i, line in enumerate((q1, q2)):
        if isinstance(line, list): rich(ctx, line, 300 + i * 74, 62)
        else: txt(ctx, line, 540, 300 + i * 74, 62, (1, 1, 1) if i == 0 else YEL)
    if rule: txt(ctx, rule, 540, 432, 32, (1, 1, 1), .72, weight=cairo.FONT_WEIGHT_NORMAL)


def counters(ctx, left, right):
    """left/right = (label, value, colour)"""
    for x, (lab, val, col) in ((300, left), (780, right)):
        txt(ctx, lab, x, 1428, 24, (1, 1, 1), .55, track=4)
        txt(ctx, val, x, 1498, 86, col)


def tag(ctx, s, y=1384, a=1.0, col=(1, 1, 1)):
    txt(ctx, s, 540, y, 26, col, .8 * a, track=6)


def banner(ctx, big, small, u, col=YEL):
    """payoff text that replaces the question"""
    k = 1 + .25 * math.exp(-u * 9) * math.cos(u * 18)
    ctx.save(); ctx.translate(540, 318); ctx.scale(k, k); txt(ctx, big, 0, 0, 92, col); ctx.restore()
    txt(ctx, small, 540, 412, 40, (1, 1, 1), min(1, u * 3))


def hue(h, s=.72, v=1.0): return colorsys.hsv_to_rgb(h % 1, s, v)


# ---------------- timeline: sim time <-> video time ----------------
class Timeline:
    """Maps every video frame to a sim time. speed(s) gives the playback rate at sim time s;
    the last `slow` sim-seconds before T_END play at 0.33x, then the sim freezes for `hold` s,
    then 0.5 s cross-fade into frame 0."""
    def __init__(self, T_END, speed=lambda s: 1.0, slow=.9, hold=2.0, fade=.5, post=.25):
        S = []; s = 0.0
        while s < T_END + post:
            S.append(s)
            r = .33 if T_END - slow <= s <= T_END + post else speed(s)
            s += r / FPS
        self.t_end_video = next(i for i, x in enumerate(S) if x >= T_END) / FPS
        S += [S[-1]] * int((hold + fade) * FPS)
        self.S = np.array(S); self.T_END = T_END; self.fade = fade
        self.DUR = len(S) / FPS
        self.speedf = speed; self.slow = slow
    def s(self, t): return self.S[min(len(self.S) - 1, int(t * FPS + 1e-6))]
    def v(self, s):
        """video time of sim time s"""
        k = int(np.searchsorted(self.S, s)); return k / FPS
    def rate(self, t):
        s = self.s(t)
        if self.T_END - self.slow <= s <= self.T_END + .25: return 'slow'
        return self.speedf(s)


def looped(draw_core, TL):
    def draw(ctx, t):
        draw_core(ctx, t)
        if t > TL.DUR - TL.fade:
            a = (t - (TL.DUR - TL.fade)) / TL.fade
            ctx.push_group(); draw_core(ctx, 0.0); ctx.pop_group_to_source(); ctx.paint_with_alpha(a)
    return draw


# ---------------- sound ----------------
CHORDS = [[0, 4, 7], [-3, 0, 4], [-7, -3, 0], [-5, -1, 2]]          # C  Am  F  G


def note_freq(k, base=261.63, octaves=(0, 1, 2)):
    ch = CHORDS[(k // 8) % 4]; tones = [c + 12 * o for o in octaves for c in ch]; tones.sort()
    pat = [0, 2, 4, 6, 5, 3, 4, 7]
    return base * 2 ** (tones[pat[k % 8] % len(tones)] / 12)


def marimba(f, amp=.12, d=.9):
    m = np.arange(int(SR * d)) / SR
    x = np.sin(2 * np.pi * f * m) + .35 * np.sin(2 * np.pi * f * 3.98 * m) * np.exp(-m * 18) + .15 * np.sin(2 * np.pi * f * 2 * m)
    return x * np.exp(-m * 5.5) * np.minimum(1, m / .002) * amp


def thud(amp=.3):
    m = np.arange(int(SR * .5)) / SR
    return np.sin(2 * np.pi * (80 - 40 * m) * m) * np.exp(-m * 9) * amp


def shimmer(amp=.05, d=2.5):
    m = np.arange(int(SR * d)) / SR; g = np.random.default_rng(3).normal(0, 1, len(m))
    X = np.fft.rfft(g); f = np.fft.rfftfreq(len(g), 1 / SR); X[(f < 4000)] = 0; x = np.fft.irfft(X, len(g))
    return x / np.abs(x).max() * np.exp(-m * 1.8) * amp


def payoff(tr, t0, base=261.63):
    tr.add(thud(.35), t0)
    for i, st in enumerate((0, 4, 7, 12, 16)): tr.add(marimba(base * 2 ** (st / 12), .1, 2.2), t0 + i * .06)
    tr.add(shimmer(), t0)


def notes(tr, TL, events, amp=.11, min_gap=.045, pitch=None, base=261.63):
    """events: list of sim times (or (sim_t, k) with own note index). Rate-limited so time-lapse
    stays musical; volume grows with time like the references (+~8 dB to the end)."""
    last = -1; k = 0
    for e in events:
        st, kk = (e, None) if not isinstance(e, tuple) else e
        vt = TL.v(st)
        if vt - last < min_gap: k += 1; continue
        last = vt; idx = k if kk is None else kk
        f = note_freq(idx, base) if pitch is None else pitch(st, idx)
        g = .55 + .45 * min(1, vt / max(1, TL.t_end_video))
        tr.add(marimba(f, amp * g), vt); k += 1


def run(draw_core, TL, audio, name, argv):
    fx_main(looped(draw_core, TL), TL.DUR, audio, name, argv, strength=.55, thr=.62)
