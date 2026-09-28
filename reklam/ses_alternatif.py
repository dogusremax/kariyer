"""Alternatif ses: sinematik fragman tarzı (saat tik-takı, taiko, braam, yaylılar).
Zaman çizelgesi ses.py ile aynıdır; efektler animasyonla senkron.
Kullanım: python3 ses_alternatif.py cikti.wav
"""
import sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
OFF = 3.0
DUR = 30.0 + OFF
N = int(SR * DUR)
rng = np.random.default_rng(11)

mus = np.zeros((N, 2))
pad = np.zeros((N, 2))
fx = np.zeros((N, 2))


def add(buf, t0, x, amp=1.0, pan=0.0):
    i = int((t0 + OFF) * SR)
    if i >= N or i + len(x) <= 0:
        return
    if i < 0:
        x, i = x[-i:], 0
    x = x[: N - i]
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    buf[i:i + len(x), 0] += x * amp * l * 1.414
    buf[i:i + len(x), 1] += x * amp * r * 1.414


def tt(d):
    return np.arange(int(d * SR)) / SR


def lp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)


def hp(x, f, o=2):
    return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)


def bp(x, f1, f2):
    return signal.sosfilt(signal.butter(2, [f1, f2], 'band', fs=SR, output='sos'), x)


def noise(d):
    return rng.standard_normal(int(d * SR))


def note(n):
    return 440 * 2 ** ((n - 69) / 12)


def sweep_lp(x, f0, f1, curve=1.0):
    out = np.zeros_like(x)
    blk = 1024
    for i in range(0, len(x), blk):
        p = (i / len(x)) ** curve
        out[i:i + blk] = lp(x[i:i + blk], f0 + (f1 - f0) * p)
    return out


# ---------- sesler ----------
def clock(tock=False):
    t = tt(.07)
    f = 2600 if tock else 3400
    return bp(noise(.07), f * .7, f * 1.3) * np.exp(-t * 120) + np.sin(2 * np.pi * f * t) * np.exp(-t * 160) * .4


def taiko(d=.9, f0=110, f1=55, amp_n=.5):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    skin = lp(noise(d), 1200) * np.exp(-t * 25) * amp_n
    return np.tanh(1.5 * (body + skin))


def small_drum(d=.25):
    t = tt(d)
    return (np.sin(2 * np.pi * 220 * t) * np.exp(-t * 20) + bp(noise(d), 400, 3000) * np.exp(-t * 35) * .6)


def braam(d=2.2, root=38, major=False):
    t = tt(d)
    notes = [root, root + 12, root + 19, root + (16 if major else 15) + 12]
    x = sum(signal.sawtooth(2 * np.pi * note(n) * dt * t) for n in notes for dt in (.995, 1.0, 1.006))
    x = sweep_lp(x / 12, 180, 2600, .35)
    env = np.minimum(1, t / .04) * np.exp(-t * 1.1)
    return np.tanh(2.2 * x * env) * .9


def subdrop(d=1.8):
    t = tt(d)
    f = 30 + 70 * np.exp(-t * 3)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.4)


def whoosh(d=.7, rev=False):
    t = tt(d)
    n = noise(d)
    out = np.zeros_like(n)
    blk = 1024
    for i in range(0, len(n), blk):
        p = i / len(n)
        fc = 300 + 4500 * (np.sin(np.pi * p) ** 2)
        out[i:i + blk] = bp(n[i:i + blk], fc * .6, min(fc * 1.6, 20000))
    env = (t / d) ** 3 if rev else np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2
    return out * env


def riser(d=1.7):
    t = tt(d)
    f = 110 * (8 ** (t / d))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = (signal.sawtooth(ph) + signal.sawtooth(ph * 1.5)) * .3
    return lp(tone, 5000) * (t / d) ** 2 + hp(noise(d), 3000) * (t / d) ** 3 * .6


def pluck(f, d=.6):
    # Karplus-Strong
    n = int(SR / f)
    buf = rng.uniform(-1, 1, n)
    out = np.zeros(int(d * SR))
    for i in range(len(out)):
        out[i] = buf[i % n]
        buf[i % n] = .5 * (buf[i % n] + buf[(i + 1) % n]) * .996
    return out


def shing():
    t = tt(1.4)
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) * a
               for f, k, a in ((1870, 3, .4), (2810, 4, .3), (4230, 6, .25), (6100, 8, .15))) + \
        hp(noise(1.4), 6000) * np.exp(-t * 10) * .3


def stamp():
    t = tt(.5)
    return np.tanh(2 * (taiko(.5, 150, 60) + lp(noise(.5), 1800) * np.exp(-t * 30) * .7))


def pop():
    t = tt(.25)
    f = 500 + 1000 * t / .25
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)


def buzz(d=.38):
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * 150 * t)) * (0.5 + .5 * np.sign(np.sin(2 * np.pi * 26 * t)))
    return lp(x, 900) * np.minimum(1, (d - t) * 20) * .5


def strings(notes, d, att=.5, cutoff=2600):
    t = tt(d)
    vib = 1 + .004 * np.sin(2 * np.pi * 5.2 * t)
    x = sum(signal.sawtooth(2 * np.pi * np.cumsum(note(n) * dt * vib) / SR) for n in notes for dt in (.997, 1.003))
    env = np.minimum(1, t / att) * np.minimum(1, (d - t) / .3)
    return lp(x / (2 * len(notes)), cutoff) * env


def ostinato(root, d, step=.25):
    out = np.zeros(int(d * SR))
    pat = [0, 12, 0, 7]
    for k in range(int(d / step)):
        f = note(root + pat[k % 4])
        t = tt(step)
        s = lp(signal.sawtooth(2 * np.pi * f * t), 900) * np.exp(-t * 9)
        i = int(k * step * SR)
        out[i:i + len(s)] += s[:len(out) - i]
    return out


B = .5
G0 = .2


def grid(a, b, step=B):
    k = np.ceil((a - G0) / step - 1e-9)
    t = G0 + k * step
    while t < b - 1e-6:
        yield round(t, 4)
        t += step


# Re minör: Dm - Bb - F - C ; final Bb - C - F (majör)
CH = {'Dm': [50, 53, 57, 62], 'Bb': [46, 50, 53, 58], 'F': [45, 48, 53, 57], 'C': [48, 52, 55, 60]}
ROOT = {'Dm': 38, 'Bb': 34, 'F': 41, 'C': 36}
PROG = ['Dm', 'Bb', 'F', 'C']


def prog(t0, t1, cutoff=2600, amp=1.0, osti=True):
    t, i = t0, 0
    while t < t1 - .05:
        d = min(2.0, t1 - t)
        c = PROG[i % 4]
        add(pad, t, strings(CH[c], d + .2, .4, cutoff), .7 * amp)
        if osti:
            add(mus, t, ostinato(ROOT[c], d), .45 * amp, -.2)
        t += 2.0
        i += 1


H = -OFF

# ---------- açılış (ARANIYOR) ----------
add(fx, H + .05, braam(2.4, 38), 1.0)
add(fx, H + .05, subdrop(), .8)
for k, t in enumerate(grid(H + .1, 0)):
    add(mus, t, clock(k % 2 == 1), .35, .4 if k % 2 else -.4)
add(fx, H + .33, whoosh(.45), .6, -.3)
add(fx, H + .8, stamp(), 1.0)
add(fx, H + 1.3, pop(), .45)
add(fx, H + 1.3, pluck(note(74)), .5, .3)
add(fx, H + 1.75, pluck(note(77)), .4, -.3)
add(fx, H + 1.95, pluck(note(81)), .4)
t = H + 2.2
step = .18
while t < H + 2.95:
    add(mus, t, small_drum(), .35 + .5 * (t - H - 2.2) / .75)
    step = max(.05, step * .82)
    t += step
add(fx, H + 2.75, whoosh(.5), .6, .5)

# ---------- sahne 1: saat işliyor ----------
add(pad, 0, strings([38, 45, 50], 3.5, 1.0, 900), .8)
for k, t in enumerate(grid(0, 3.3)):
    add(mus, t, clock(k % 2 == 1), .4, .4 if k % 2 else -.4)
for t, p in ((.2, 0), (.7, -.2), (1.1, .2), (1.45, 0)):
    add(fx, t, taiko(), 1.0, p)
add(fx, 1.45, braam(1.6, 38), .45)

# ---------- sahne 2: binalar ----------
add(fx, 3.1, whoosh(.6), .55, -.5)
add(fx, 3.3, lp(noise(1.4), 120) * np.sin(np.linspace(0, np.pi, int(1.4 * SR))), 1.1)
prog(3.2, 6.3, 1600, .9, osti=False)
for t in grid(3.2, 6.3):
    add(mus, t, taiko(.6, 100, 55, .3) if round((t - G0) / B) % 2 == 0 else small_drum(), .7)
for t in np.sort(rng.uniform(3.9, 6.2, 16)):
    add(fx, t, pluck(note(rng.choice([74, 77, 81, 86])), .4), .12, rng.uniform(-.8, .8))
add(fx, 5.1, taiko(1.2, 130, 50), 1.0)
add(fx, 5.1, braam(1.4, 34), .5)

# ---------- sahne 3: karanlık, sadece saat + kalp ----------
add(fx, 6.2, whoosh(.8), .55, .5)
for k, t in enumerate(grid(6.4, 8.6)):
    add(mus, t, clock(k % 2 == 1), .5, .4 if k % 2 else -.4)
for t in (6.9, 7.15, 7.9, 8.15):
    add(mus, t, taiko(.5, 80, 40, .1), .6)
add(pad, 6.3, strings([50, 57, 62], 2.5, .8, 700), .5)
add(fx, 8.0, shing(), .45, .1)
add(fx, 7.6, whoosh(1.1, rev=True), .5)
add(fx, 8.7, braam(2.4, 38), 1.1)
add(fx, 8.7, subdrop(), 1.0)
add(fx, 8.7, taiko(1.4, 140, 45), .9)

# ---------- 8.7 - 23.7: tam tempo ----------
prog(8.7, 24.7, 2800, 1.0)
for t in grid(8.7, 23.7):
    b = round((t - G0) / B)
    add(mus, t, taiko(.7, 105, 52, .35) if b % 2 == 0 else small_drum(), .85 if b % 2 == 0 else .5)
for k, t in enumerate(grid(8.7, 20.2, B / 2)):
    add(mus, t, clock(k % 2 == 1), .18, .5 if k % 2 else -.5)
for k, t in enumerate(grid(20.2, 23.7, B / 4)):
    add(mus, t, clock(k % 2 == 1), .15, .5 if k % 2 else -.5)

# efektler
add(fx, 10.05, whoosh(.6), .55, -.4)
add(fx, 10.75, stamp(), .6)
add(fx, 10.9, whoosh(.6), .4, .3)
for i in range(4):
    add(fx, 11.6 + i * .55, pluck(note([62, 65, 69, 74][i]), .5), .45, -.3 + i * .2)
add(fx, 14.0, stamp(), 1.0)
add(fx, 14.0, braam(1.2, 41), .35)
add(fx, 15.2, whoosh(.6), .55, .4)
for i, t in enumerate((15.6, 16.25, 16.9, 17.55, 18.2)):
    add(fx, t, buzz(), .6)
    add(fx, t + .02, pluck(note([81, 84, 86, 89, 93][i]), .5), .45, .2)
add(fx, 19.0, taiko(.9, 130, 55), .8)
add(fx, 20.1, whoosh(.5), .65, -.8)
add(fx, 20.2, whoosh(.5), .65, .8)
add(fx, 20.35, taiko(1.0, 140, 50), .9, -.3)
add(fx, 20.6, taiko(1.0, 140, 50), .9, .3)
add(fx, 22.2, pop(), .3)
add(fx, 22.2, whoosh(.5), .3)

# ---------- 23.7 - 25.2: taiko rulosu + yükseliş, sonra sessizlik ----------
t = 23.7
step = .25
while t < 24.95:
    add(mus, t, taiko(.4, 120, 60, .5), .35 + .6 * (t - 23.7) / 1.25, rng.uniform(-.4, .4))
    step = max(.055, step * .82)
    t += step
add(fx, 23.4, riser(1.7), .6)

# ---------- final: majör çözülüş ----------
add(fx, 25.2, braam(3.0, 41, major=True), 1.1)
add(fx, 25.2, subdrop(2.2), 1.0)
add(fx, 25.2, whoosh(2.3), .3)
for t0, c, d in ((25.2, 'Bb', 1.5), (26.7, 'C', 1.6), (28.3, 'F', 1.7)):
    notes = CH[c] + [CH[c][1] + 12, CH[c][2] + 12]
    add(pad, t0, strings(notes, d + .2, .08, 4000), .9)
    add(mus, t0, ostinato(ROOT[c], d, .125), .4)
for t in (25.2, 25.95, 26.2, 26.7, 27.45, 27.7, 28.3):
    add(mus, t, taiko(.8, 115, 50, .4), .9)
add(fx, 25.5, taiko(), .6)
add(fx, 26.1, taiko(), .7)
add(fx, 27.3, shing(), .25, -.2)
add(fx, 27.8, pop(), .35)
add(fx, 28.3, braam(1.8, 41, major=True), .8)
add(fx, 28.3, subdrop(1.6), .8)


# ---------- miks ----------
def reverb(x, d=1.6, mix=.25):
    t = tt(d)
    irl = lp(rng.standard_normal(len(t)) * np.exp(-t * 3.2), 5000) / 30
    irr = lp(rng.standard_normal(len(t)) * np.exp(-t * 3.2), 5000) / 30
    wet = np.stack([signal.fftconvolve(x[:, 0], irl)[:N], signal.fftconvolve(x[:, 1], irr)[:N]], 1)
    return x + wet * mix


mix = reverb(mus, 1.2, .25) * .7 + reverb(pad, 2.6, .6) * .45 + reverb(fx, 1.8, .35) * .9
mix = hp(mix.T, 25).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.8) / np.tanh(1.8)
fade = np.ones(N)
fade[-int(.8 * SR):] = np.linspace(1, 0, int(.8 * SR))
fade[:int(.01 * SR)] = np.linspace(0, 1, int(.01 * SR))
mix *= fade[:, None] * .89
wavfile.write(sys.argv[1], SR, (mix * 32767).astype(np.int16))
print('ok', np.max(np.abs(mix)))
