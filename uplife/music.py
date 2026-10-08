"""Uplife Kadıköy filmi için (seslendirme altı, sakin) kodla üretilen telifsiz müzik (build/music.wav).

Sahne geçişleri film.html'deki SC dizisiyle aynı saniyelere denk gelir.
"""
import os
import wave

import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
DUR = 62.5
BPM = 96
BEAT = 60 / BPM
N = int(SR * DUR)
t = np.arange(N) / SR
out = np.zeros((N, 2))

TRANSITIONS = [5.3, 16.6, 29.85, 41.15, 52.7]


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def env(n, a, r):
    e = np.ones(n)
    na, nr = int(a * SR), int(r * SR)
    e[:na] = np.linspace(0, 1, na)
    e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(sig, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    out[i:i + len(sig), 0] += sig * gain * (1 - pan) / 2 ** .5 * 1.4
    out[i:i + len(sig), 1] += sig * gain * (1 + pan) / 2 ** .5 * 1.4


def lp(x, f):
    return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)


def hp(x, f):
    return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)


def saw(f, n, detune=0.0):
    ph = np.arange(n) / SR * f * (1 + detune)
    return 2 * (ph % 1) - 1


# I–V–vi–IV (C – G – Am – F), her akor 2 ölçü
CHORDS = [[48, 55, 60, 64, 67], [43, 55, 59, 62, 67], [45, 57, 60, 64, 69], [41, 57, 60, 65, 69]]
BAR = 4 * BEAT
chord_len = 2 * BAR
n_chords = int(np.ceil(DUR / chord_len))

for c in range(n_chords):
    notes = CHORDS[c % 4]
    st = c * chord_len
    n = int(chord_len * SR) + int(.4 * SR)
    # Pad
    pad = sum(saw(hz(m), n, d) for m in notes[1:] for d in (-.004, .004))
    pad = lp(pad, 1400) * env(n, .6, .8) * .035
    add(pad, st, pan=0)
    # Bas (8'lik) — 5. saniyeden sonra
    for k in range(16):
        bt = st + k * BEAT / 2
        if bt < 4.9 or bt > DUR - 1.5:
            continue
        bn = int(BEAT / 2 * SR)
        b = lp(saw(hz(notes[0] - 12), bn), 500) * env(bn, .005, .08) * .16
        add(b, bt)
    # Arpej (16'lık pluck)
    arp = [notes[2] + 12, notes[3] + 12, notes[4] + 12, notes[3] + 12]
    for k in range(32):
        at = st + k * BEAT / 4
        if at > DUR - 2:
            continue
        an = int(.35 * SR)
        f = hz(arp[k % 4])
        x = np.sin(2 * np.pi * f * np.arange(an) / SR) + .3 * np.sin(4 * np.pi * f * np.arange(an) / SR)
        x *= np.exp(-np.arange(an) / SR * 14) * .05
        add(x, at, pan=.35 if k % 2 else -.35)

# Davul
kn = int(.35 * SR)
kt = np.arange(kn) / SR
kick = np.sin(2 * np.pi * (45 * kt + 90 / 30 * (1 - np.exp(-kt * 30)))) * np.exp(-kt * 9) * .32
cn = int(.25 * SR)
clap = hp(np.random.default_rng(1).standard_normal(cn), 1200) * np.exp(-np.arange(cn) / SR * 22) * .05
hn = int(.06 * SR)
hat = hp(np.random.default_rng(2).standard_normal(hn), 7000) * np.exp(-np.arange(hn) / SR * 70) * .06
beat_i = 0
while beat_i * BEAT < DUR - 1.2:
    bt = beat_i * BEAT
    if bt >= 5.0:
        add(kick, bt)
        if beat_i % 2 == 1:
            add(clap, bt)
        add(hat, bt + BEAT / 2, pan=.3)
    elif bt >= 2.6:
        add(hat, bt + BEAT / 2, gain=.6, pan=.3)
    beat_i += 1

# Geçişlerde whoosh (filtreli gürültü süpürmesi) + darbe
rng = np.random.default_rng(3)
for tr in TRANSITIONS:
    wn = int(.9 * SR)
    noise = rng.standard_normal(wn)
    lo = hp(noise, 300)
    sweep = np.linspace(0, 1, wn) ** 2
    w = lp(lo, 6000) * sweep * np.concatenate([np.ones(wn - int(.05 * SR)), np.linspace(1, 0, int(.05 * SR))]) * .07
    add(w, tr - .8)
    imp = np.sin(2 * np.pi * 55 * kt) * np.exp(-kt * 6) * .35
    add(imp, tr)

# Final akor
fn = int(4 * SR)
fin = sum(saw(hz(m), fn, d) for m in [48, 60, 64, 67, 72] for d in (-.005, .005))
add(lp(fin, 2200) * env(fn, .02, 3.5) * .05, 52.7)

# Genel zarf + normalizasyon
fade = np.ones(N)
fade[:int(.3 * SR)] = np.linspace(0, 1, int(.3 * SR))
fade[-int(2.5 * SR):] = np.linspace(1, 0, int(2.5 * SR))
out *= fade[:, None]
out = np.tanh(out * 1.2)
out /= np.abs(out).max() / .89

os.makedirs('build', exist_ok=True)
with wave.open('build/music.wav', 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes((out * 32767).astype('<i2').tobytes())
print('yazıldı: build/music.wav')
