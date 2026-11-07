"""Knife scrapes on each paint sweep, soft after-rain drips, a harp arpeggio climbing while the ring closes,
one glockenspiel when it completes, a quiet airy bed above the clouds."""
import wave, numpy as np, sys
sys.path.insert(0, '/home/claude/reels')
from common import pluck, note
SR = 44100; DUR = 17; N = SR * DUR
out = np.zeros(N + SR * 3); g = np.random.default_rng(3)
def add(sig, t): i = int(t * SR); out[i:i + len(sig)] += sig[:len(out) - i]
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def scrape(d, amp):                                   # palette knife dragged through thick paint
    n = int(SR * d); x = bp(g.normal(0, 1, n), 700, 6000); m = np.arange(n) / n
    rid = 1 + .6 * np.sin(2 * np.pi * np.cumsum(9 + 6 * g.random(n)) / SR)
    return x / np.abs(x).max() * np.sin(np.pi * m) ** .8 * rid * amp
def drip(amp):
    m = np.arange(int(SR * .25)) / SR; f = 900 + 1400 * np.exp(-m * 40)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-m * 22) * amp
def glock(f, amp):
    m = np.arange(int(SR * 2.5)) / SR
    return (np.sin(2 * np.pi * f * m) + .4 * np.sin(2 * np.pi * f * 2.76 * m)) * np.exp(-m * 2.2) * amp
for t, d in [(0, 1.2), (6.6, 1.0), (15.1, 1.2)]: add(scrape(d, .16), t)
for k in range(3): add(scrape(.5, .08), 1.6 + k * .3)
for k in range(3): add(scrape(.5, .08), 11.0 + k * .3)
for k in range(16): add(drip(.05 * g.random() + .02), .3 + g.random() * 6)
air = bp(g.normal(0, 1, int(SR * 8.6)), 200, 1800); m = np.arange(len(air)) / len(air); add(air / np.abs(air).max() * np.sin(np.pi * m) * .04, 6.6)
for k in range(12): add(pluck(note(k, 261.63), 1.6, .07, 3), 8.0 + k * 2.6 / 12)       # harp climbing round the ring
add(glock(1568, .12), 10.65); add(glock(2093, .06), 10.7)
for k in range(5): add(pluck(note(k * 2, 196), 2.2, .05, 2), k * 3.4)                   # a sparse bass line
out = out[:N]; out /= max(1, np.abs(out).max() / .9)
w = wave.open('mix.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes()); w.close(); print('ok')
