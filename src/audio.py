import numpy as np, wave
import sim
sim.GROW = 5.0
frames, bounces, end_t = sim.simulate(seed=7)
SR = 44100
dur = len(frames) / 30 + 3.2
out = np.zeros(int(SR * (dur + 0.5)))
penta = [0, 2, 4, 7, 9]


def add(sig, t):
    i = int(t * SR)
    n = min(len(sig), len(out) - i)
    out[i:i + n] += sig[:n]


def pluck(f, d=0.6, amp=0.32):
    t = np.arange(int(SR * d)) / SR
    env = np.exp(-t * 7) * np.minimum(1, t * 400)
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.12 * np.sin(6 * np.pi * f * t)
    return amp * env * s


for b in bounces:
    k = b["idx"]
    step = (k * 2) % 25  # wanders up the scale and wraps
    octv, deg = divmod(step, 5)
    f = 261.63 * 2 ** ((penta[deg] + 12 * octv) / 12)
    add(pluck(f), b["t"])

T0 = len(frames) / 30
t = np.arange(int(SR * 2.5)) / SR
boom = np.sin(2 * np.pi * (90 * t - 30 * t * t)) * np.exp(-t * 2.5) * 0.9
noise = np.random.default_rng(1).normal(0, 1, len(t)) * np.exp(-t * 6) * 0.25
add(boom + noise, T0)
for j, semi in enumerate([0, 4, 7, 12, 16, 19, 24]):
    add(pluck(523.25 * 2 ** (semi / 12), 1.4, 0.18), T0 + 0.5 + j * 0.07)

out /= np.max(np.abs(out)) * 1.05
pcm = (out * 32767).astype(np.int16)
with wave.open("audio.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("ok", dur)
