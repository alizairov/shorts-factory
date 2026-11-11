"""Glow 3D style: shaded luminous objects on deep backgrounds, bloom post-process, physics-driven motion."""
import sys, math, random, subprocess
sys.path.insert(0, '/home/claude/reels')
import numpy as np, cairo
from PIL import Image
from scipy.ndimage import gaussian_filter
from common import FPS, SR, Track, label, mux
from k1_stomach import rrect, ell, tagbox, popk, chime, pop, pad, cl, ease, lerp, LOGO
import paperkit as pk
W, H = 1080, 1920
INK = (0.07, 0.05, 0.16)
YEL, ORNG, CYAN, PINK, LIME, WHITE = (1.0, 0.84, 0.25), (1.0, 0.55, 0.2), (0.4, 0.9, 1.0), (1.0, 0.42, 0.65), (0.75, 0.95, 0.3), (1, 1, 1)


def bg(ctx, c0, c1):
    g = cairo.LinearGradient(0, 0, 0, H); g.add_color_stop_rgb(0, *c0); g.add_color_stop_rgb(1, *c1); ctx.set_source(g); ctx.paint()


def stars(ctx, t, n=70, seed=1, ymax=H):
    r = random.Random(seed)
    for k in range(n):
        x, y = r.uniform(0, W), r.uniform(0, ymax)
        ctx.set_source_rgba(1, 1, 1, 0.25 + 0.3 * math.sin(t * 2 + k)); ctx.new_path(); ctx.arc(x, y, r.uniform(1.5, 3.2), 0, 7); ctx.fill()


def glow(ctx, x, y, r, col, a):
    g = cairo.RadialGradient(x, y, 0, x, y, r); g.add_color_stop_rgba(0, *col, a); g.add_color_stop_rgba(1, *col, 0)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 7); ctx.fill()


def ball(ctx, x, y, r, col, a=1.0, spec=0.55):
    """soft 3D sphere: lit from the top-left, dark rim, specular dot"""
    g = cairo.RadialGradient(x - r * .35, y - r * .4, r * .05, x, y, r)
    hi = tuple(min(1, c + .35) for c in col); lo = tuple(c * .35 for c in col)
    g.add_color_stop_rgba(0, *hi, a); g.add_color_stop_rgba(.55, *col, a); g.add_color_stop_rgba(1, *lo, a)
    ctx.set_source(g); ctx.arc(x, y, r, 0, 7); ctx.fill()
    g = cairo.RadialGradient(x - r * .38, y - r * .45, 0, x - r * .38, y - r * .45, r * .35)
    g.add_color_stop_rgba(0, 1, 1, 1, spec * a); g.add_color_stop_rgba(1, 1, 1, 1, 0); ctx.set_source(g); ctx.arc(x, y, r, 0, 7); ctx.fill()


def brand(ctx):
    ctx.new_path()
    ctx.set_source_rgba(1, 1, 1, .95); ctx.arc(110, 130, 50, 0, 7); ctx.fill()
    ctx.save(); ctx.translate(65, 85); ctx.scale(.75, .75); ctx.set_source_surface(LOGO, 0, 0); ctx.paint(); ctx.restore()
    label(ctx, "@Visual.Brainer", 180, 142, 34, col=(1, 1, 1), alpha=.9, anchor="l", shadow=.4)


def _post(surf, strength, thr):
    a = np.frombuffer(surf.get_data(), np.uint8).reshape(H, W, 4)
    small = a[::4, ::4, :3].astype(np.float32)
    br = np.clip(small - thr * 255, 0, None)
    br = gaussian_filter(br, sigma=(7, 7, 0))
    up = np.asarray(Image.fromarray(np.clip(br, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32)
    out = a.copy(); out[:, :, :3] = np.clip(a[:, :, :3] + up * strength, 0, 255).astype(np.uint8)
    return out


def frame(draw, fi, strength=1.1, thr=.55):
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); ctx = cairo.Context(s)
    draw(ctx, fi / FPS); brand(ctx); s.flush()
    return _post(s, strength, thr)


def render(draw, dur, audio, out, **kw):
    tmp = out.replace('.mp4', '_v.mp4')
    p = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgra', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-profile:v', 'main', '-crf', '19', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp], stdin=subprocess.PIPE)
    for fi in range(int(dur * FPS)): p.stdin.write(frame(draw, fi, **kw).tobytes())
    p.stdin.close(); p.wait(); mux(tmp, audio, out)


def stills(draw, ts, name, **kw):
    ims = [Image.fromarray(frame(draw, int(t * FPS), **kw)[:, :, [2, 1, 0]]).resize((270, 480)) for t in ts]
    c = Image.new('RGB', (270 * len(ims), 480)); [c.paste(im, (i * 270, 0)) for i, im in enumerate(ims)]; c.save(name)


def main(draw, dur, audio_fn, name, argv, **kw):
    if argv[1] == 'stills': stills(draw, [float(x) for x in argv[2:]], f'{name}_contact.png', **kw)
    else: audio_fn(f'{name}.wav'); render(draw, dur, f'{name}.wav', f'{name}.mp4', **kw)
