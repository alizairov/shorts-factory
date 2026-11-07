"""Sound: synthesized chalk foley (grainy band-passed scratches sized to each stroke), soft taps, one wipe swish
per wipe, a low thump on the first strike, quiet room tone. No music: ASMR chalk only."""
import json, wave, numpy as np
SR = 44100
d = json.load(open('events.json')); DUR = d['dur']; N = int(SR * DUR)
out = np.zeros(N + SR); g = np.random.default_rng(7)
def add(sig, t):
    i = int(t * SR); out[i:i + len(sig)] += sig[:max(0, len(out) - i)]
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def chalk(dur, amp):
    n = max(64, int(SR * dur)); x = np.zeros(n)
    for p in (g.random(int(900 * dur) + 3) * n).astype(int):        # grains of chalk catching the slate
        L = g.integers(30, 160); m = np.arange(L); x[p:p + L] += g.normal(0, 1, min(L, n - p))[:max(0, min(L, n - p))] * np.exp(-m / (L / 3))[:max(0, min(L, n - p))]
    x = bp(x + .25 * g.normal(0, 1, n), 1800, 9000)
    e = np.minimum(1, np.arange(n) / (SR * .008)) * np.minimum(1, (n - np.arange(n)) / (SR * .02))
    x = x / (np.abs(x).max() + 1e-9) * e * amp
    tap = np.exp(-np.arange(int(SR * .03)) / (SR * .004)) * g.normal(0, 1, int(SR * .03)); tap = bp(tap, 300, 3000) * amp * .9
    x[:len(tap)] += tap[:len(x)]; return x
def thump(amp):
    m = np.arange(int(SR * .9)) / SR
    return (np.sin(2 * np.pi * 48 * m) * np.exp(-m * 5) + bp(g.normal(0, 1, len(m)), 40, 300) * np.exp(-m * 3) * .6) * amp
def swish(dur, amp):
    n = int(SR * dur); x = bp(g.normal(0, 1, n), 400, 5000); m = np.arange(n) / n
    return x / np.abs(x).max() * np.sin(np.pi * m) ** 1.2 * amp
first = True
for e in d['ev']:
    if e['type'] == 'chalk': add(chalk(e['d'], .10 + .05 * g.random()), e['t'])
    elif e['type'] == 'bolt':
        add(chalk(.16, .16), e['t'])
        if first: add(thump(.35), e['t'] + .05); first = False
    elif e['type'] == 'tick': add(chalk(.1, .13), e['t'])
    elif e['type'] == 'wipe': add(swish(e['d'], .09), e['t'])
room = bp(g.normal(0, 1, len(out)), 60, 900); out += room / np.abs(room).max() * .012
out = out[:N]; out = out / max(1, np.abs(out).max() / .9)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close()
print('mix.wav', DUR)
