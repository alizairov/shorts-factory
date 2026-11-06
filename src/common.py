import math, os, subprocess, wave
import numpy as np, cairo

W, H, FPS = 1080, 1920, 30
SR = 44100

# Gen Z palette: digital lavender/purple, hot pink, orange, cyber yellow, acid lime, cyan
HEX = ["#7B61FF", "#FF5CE1", "#FF8A3D", "#FFE14D", "#B8FF3C", "#3CF0FF"]
PAL = [tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)) for h in HEX]


def grad(x):
    """Cyclic gradient through the palette, x in [0,1)."""
    x = (x % 1.0) * len(PAL)
    i = int(x) % len(PAL)
    f = x - int(x)
    a, b = PAL[i], PAL[(i + 1) % len(PAL)]
    return tuple(a[k] + (b[k] - a[k]) * f for k in range(3))


def lighten(c, k):
    return tuple(v + (1 - v) * k for v in c)


def circle(ctx, x, y, r):
    ctx.arc(x, y, max(r, 0.1), 0, 2 * math.pi)


def glossy_ball(ctx, x, y, r, c, glow=True):
    if glow:
        ctx.set_source_rgba(*c, 0.18)
        circle(ctx, x, y, r * 1.55)
        ctx.fill()
    g = cairo.RadialGradient(x - r * 0.35, y - r * 0.4, r * 0.05, x, y, r)
    g.add_color_stop_rgb(0, *lighten(c, 0.75))
    g.add_color_stop_rgb(0.45, *c)
    g.add_color_stop_rgb(1, *(v * 0.7 for v in c))
    ctx.set_source(g)
    circle(ctx, x, y, r)
    ctx.fill()


def encode(draw, n, out):
    tmp = out[:-4] + ".tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgra",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-profile:v", "main",
                          "-crf", "20", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for i in range(n):
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        draw(cairo.Context(s), i)
        p.stdin.write(bytes(s.get_data()))
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out)


def stills(draw, idxs, prefix):
    for i in idxs:
        s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
        draw(cairo.Context(s), i)
        s.write_to_png(f"{prefix}_{i}.png")


class Track:
    def __init__(self, dur):
        self.buf = np.zeros(int(SR * (dur + 1)))

    def add(self, sig, t):
        i = int(t * SR)
        if i >= len(self.buf):
            return
        n = min(len(sig), len(self.buf) - i)
        self.buf[i:i + n] += sig[:n]

    def save(self, path, dur):
        b = self.buf[:int(SR * dur)]
        b = np.tanh(b / (np.max(np.abs(b)) * 0.8 + 1e-9) * 1.2) * 0.9
        pcm = (b * 32767).astype(np.int16)
        with wave.open(path, "wb") as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())


def pluck(f, d=0.5, amp=0.3, decay=8):
    t = np.arange(int(SR * d)) / SR
    env = np.exp(-t * decay) * np.minimum(1, t * 500)
    return amp * env * (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) + 0.1 * np.sin(6 * np.pi * f * t))


PENTA = [0, 2, 4, 7, 9]


def note(step, base=261.63):
    o, d = divmod(step, 5)
    return base * 2 ** ((PENTA[d] + 12 * o) / 12)


def mux(video, audio, out):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-ac", "2", "-shortest",
                    "-movflags", "+faststart", out], check=True)


FONT = "Inter Display Black"


def label(ctx, s, x, y, size, col=(1, 1, 1), alpha=1.0, anchor="c", font=FONT, shadow=0.35):
    ctx.select_font_face(font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
    ctx.set_font_size(size)
    e = ctx.text_extents(s)
    if anchor == "c":
        x0 = x - e.width / 2 - e.x_bearing
    elif anchor == "l":
        x0 = x - e.x_bearing
    else:
        x0 = x - e.width - e.x_bearing
    if shadow:
        ctx.set_source_rgba(0, 0, 0, shadow * alpha)
        ctx.move_to(x0 + size * 0.04, y + size * 0.06)
        ctx.show_text(s)
    ctx.set_source_rgba(*col, alpha)
    ctx.move_to(x0, y)
    ctx.show_text(s)
    return e.width


def music(tr, dur, bpm=112, seed=0, vol=1.0, base=220.0):
    """Original synth bed: kick, hats, bass and a pentatonic arpeggio."""
    rng = np.random.default_rng(seed)
    beat = 60 / bpm
    t = np.arange(int(SR * 0.35)) / SR
    kick = np.sin(2 * np.pi * (50 * t + 60 * (1 - np.exp(-t * 30)) / 30)) * np.exp(-t * 9) * 0.55
    hat = rng.normal(0, 1, int(SR * 0.05)) * np.exp(-np.arange(int(SR * 0.05)) / 300) * 0.06
    prog = [0, 5, 3, 4]  # scale-step roots
    nb = int(dur / beat) + 1
    for b in range(nb):
        tb = b * beat
        if b % 2 == 0:
            tr.add(kick * vol, tb)
        tr.add(hat * vol, tb + beat / 2)
        root = prog[(b // 8) % 4]
        if b % 2 == 0:
            tb2 = np.arange(int(SR * beat * 2)) / SR
            f = note(root, base / 2)
            tr.add(vol * 0.18 * np.sin(2 * np.pi * f * tb2) * np.exp(-tb2 * 2), tb)
        for k in range(2):
            step = root + [0, 2, 4, 5, 7, 4, 2, 5][(b * 2 + k) % 8]
            tr.add(pluck(note(step, base), 0.3, 0.07 * vol, 10), tb + k * beat / 2)
