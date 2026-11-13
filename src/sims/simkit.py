"""Visual Brain sim kit: shared layout (title / container / 2 counters), notes, speed tag."""
from fx import *
BG0, BG1 = (.05, .04, .13), (.02, .09, .11)
GOLD, CYAN, ORNG, PINK, GRN = (1, .8, .3), (.35, .85, 1), (1, .55, .25), (1, .4, .7), (.45, 1, .55)

def backdrop(ctx):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *BG0); g.add_color_stop_rgb(.55, .04, .04, .12); g.add_color_stop_rgb(1, *BG1)
    ctx.set_source(g); ctx.paint()
    v = cairo.RadialGradient(540, 980, 300, 540, 980, 1200); v.add_color_stop_rgba(0, 0, 0, 0, 0); v.add_color_stop_rgba(1, 0, 0, 0, .55)
    ctx.set_source(v); ctx.paint()

def header(ctx, t, acts, y=330):
    """acts: list of (t_start, line1, line2, col2). crossfades between acts."""
    cur = 0
    for i, a in enumerate(acts):
        if t >= a[0]: cur = i
    t0, l1, l2, c2 = acts[cur][:4]
    u = cl((t - t0) / .35) if cur else 1
    ctx.save(); ctx.translate(0, 18 * (1 - ease(u)))
    label(ctx, l1, 540, y, 60, col=(1, 1, 1), alpha=u, shadow=.5)
    label(ctx, l2, 540, y + 76, 64, col=c2, alpha=u, shadow=.5)
    ctx.restore()

def stats(ctx, items, y=1560):
    """items: list of (caption, value_str, colour)"""
    n = len(items)
    for i, (cap, val, col) in enumerate(items):
        x = 540 + (i - (n - 1) / 2) * 400
        label(ctx, cap, x, y, 30, col=(.62, .66, .8), shadow=0)
        label(ctx, val, x, y + 70, 84, col=col, shadow=.4)

def speed_tag(ctx, sp, y=1430, a=1.0):
    if a <= 0: return
    s = "SLOW MOTION" if sp < 1 else f"SPEED ×{sp:g}"
    ctx.new_path(); rrect(ctx, 400, y - 30, 280, 60, 30); ctx.set_source_rgba(1, 1, 1, .08 * a); ctx.fill()
    label(ctx, s, 540, y, 32, col=(1, .85, .4) if sp < 1 else (.8, .85, 1), alpha=a, shadow=0)

def mtof(m): return 440 * 2 ** ((m - 69) / 12)
def piano(f, d=1.6, amp=.12):
    tt = np.arange(int(SR * d)) / SR
    x = sum(a * np.sin(2 * np.pi * f * k * tt) * np.exp(-tt * (2.2 + 1.6 * k)) for k, a in ((1, 1), (2, .45), (3, .22), (4, .12), (5, .06)))
    return amp * x * (1 - np.exp(-tt * 900))
def marimba(f, d=.9, amp=.1):
    tt = np.arange(int(SR * d)) / SR
    x = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 6) + .35 * np.sin(2 * np.pi * f * 3.93 * tt) * np.exp(-tt * 18) + .12 * np.sin(2 * np.pi * f * 9.8 * tt) * np.exp(-tt * 40)
    return amp * x * (1 - np.exp(-tt * 1500))
def soft_bed(tr, dur, root=45, vol=.018):
    tt = np.arange(int(SR * dur)) / SR
    x = sum(np.sin(2 * np.pi * mtof(root + iv) * tt + k) for k, iv in enumerate((0, 7, 12)))
    tr.add(x * vol * np.minimum(1, tt / 2) * np.minimum(1, (dur - tt) / 2), 0)
