import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
OFF = 3.0  # açılış (ARANIYOR) süresi; ana zaman çizelgesi bu kadar kayar
DUR = 30.0 + OFF
N = int(SR * DUR)
rng = np.random.default_rng(3)

mus = np.zeros((N, 2))   # müzik
fx = np.zeros((N, 2))    # efektler (reverb'e de gider)


def add(buf, t0, x, amp=1.0, pan=0.0):
    i = int((t0 + OFF) * SR)
    if i >= N:
        return
    x = x[: N - i]
    if isinstance(pan, tuple):  # (başlangıç, bitiş): ses soldan sağa vb. akar
        pan = np.linspace(pan[0], pan[1], len(x))
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


# ---------- sesler ----------
def kick(d=.45, f0=160, f1=45, k=28):
    t = tt(d)
    f = f1 + (f0 - f1) * np.exp(-t * k)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) + lp(noise(d), 3000) * np.exp(-t * 90) * .3


def boom(d=2.2):
    t = tt(d)
    f = 28 + 90 * np.exp(-t * 9)
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t * 1.6)
    crack = lp(noise(d), 2500) * np.exp(-t * 6) * .55
    return np.tanh(1.6 * (sub + crack))


def hit(d=1.0):  # yazı çarpması
    t = tt(d)
    body = kick(d, 220, 50, 22) * 1.0
    snap = bp(noise(d), 800, 6000) * np.exp(-t * 22) * .6
    return np.tanh(1.4 * (body + snap))


def clap(d=.3):
    t = tt(d)
    e = np.zeros_like(t)
    for o in (0, .011, .022):
        e += np.where(t >= o, np.exp(-(t - o) * 60), 0)
    return bp(noise(d), 900, 5000) * e * .8


def hat(d=.05, a=1.0):
    t = tt(d)
    return hp(noise(d), 7000) * np.exp(-t * 90) * a


def whoosh(d=.7, rev=False, down=False):
    """Geçiş sesi: tok gövdeli 'vuuş' (tonal süpürme + rezonanslı hava + yumuşak kuyruk)."""
    t = tt(d)
    p = t / d
    if rev:
        env = p ** 3
    else:
        pk = .62
        env = np.where(p < pk, (p / pk) ** 2, ((1 - p) / (1 - pk)) ** 1.6)
    shape = np.sin(np.pi * np.clip(p / (.62 * 2), 0, 1))  # tepe noktasında en parlak
    # rezonanslı hava (ince 'fıss' yerine dar bantlı, yumuşak)
    n = noise(d)
    air = np.zeros_like(n)
    blk = 512
    for i in range(0, len(n), blk):
        fc = 260 + 1500 * shape[i]
        air[i:i + blk] = bp(n[i:i + blk], fc / 1.35, fc * 1.35)
    air = lp(air, 4200)
    # tonal gövde: doppler gibi yükselip inen perde
    f = (95 + 190 * (1 - shape)) if down else (80 + 200 * shape)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = lp(np.sin(ph) + .35 * signal.sawtooth(ph), 700)
    x = (air / (np.std(air) + 1e-9) * .5 + body * .55) * env
    if not rev:  # tepe noktasında hafif 'tum'
        i0 = int(.62 * d * SR)
        tk = np.arange(len(x) - i0) / SR
        x[i0:] += np.sin(2 * np.pi * (48 + 40 * np.exp(-tk * 20)) * tk) * np.exp(-tk * 9) * .45
    return x / (np.max(np.abs(x)) + 1e-9)


def riser(d=1.7):
    t = tt(d)
    f = 180 * (7 ** (t / d))
    ph = 2 * np.pi * np.cumsum(f) / SR
    saw = signal.sawtooth(ph) * .35 + signal.sawtooth(ph * 1.01) * .35
    nz = hp(noise(d), 2000) * .5
    return lp(saw, 4000) * (t / d) ** 2 + nz * (t / d) ** 3


def ping():
    t = tt(.6)
    return (np.sin(2 * np.pi * 1318.5 * t) * np.exp(-t * 9) +
            np.where(t > .09, np.sin(2 * np.pi * 1760 * t) * np.exp(-(t - .09) * 8), 0)) * .5


def buzz(d=.38):
    t = tt(d)
    x = np.sign(np.sin(2 * np.pi * 150 * t)) * (0.5 + .5 * np.sign(np.sin(2 * np.pi * 26 * t)))
    return lp(x, 900) * np.minimum(1, (d - t) * 20) * .5


def tick():
    t = tt(.06)
    return np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 110)


def clink():
    t = tt(1.0)
    return sum(np.sin(2 * np.pi * f * t) * np.exp(-t * k) * a
               for f, k, a in ((2380, 5, .5), (3710, 7, .35), (5230, 9, .25), (6900, 12, .15)))


def stamp():
    t = tt(.5)
    return np.tanh(2 * (kick(.5, 140, 55, 35) + lp(noise(.5), 1800) * np.exp(-t * 30) * .7))


def pop():
    t = tt(.25)
    f = 400 + 900 * t / .25
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)


# ---------- müzik ----------
def note(n):  # A4=69
    return 440 * 2 ** ((n - 69) / 12)


def saw_pad(freqs, d, att=.3):
    t = tt(d)
    x = sum(signal.sawtooth(2 * np.pi * f * dt * t) for f in freqs for dt in (.996, 1.004))
    env = np.minimum(1, t / att) * np.minimum(1, (d - t) / .15)
    return x * env / (len(freqs) * 2)


def bass(f, d):
    t = tt(d)
    x = np.sin(2 * np.pi * f * t) + .3 * signal.sawtooth(2 * np.pi * f * t)
    return lp(x, 400) * np.exp(-t * 1.2) * np.minimum(1, (d - t) / .03)


CH = {'Am': [57, 60, 64], 'F': [53, 57, 60], 'C': [55, 60, 64], 'G': [55, 59, 62]}
ROOT = {'Am': 33, 'F': 29, 'C': 36, 'G': 31}
PROG = ['Am', 'F', 'C', 'G']
B = .5
G0 = .2  # vuruş ızgarası (sahne geçişleriyle hizalı)

pad = np.zeros((N, 2))
# giriş: alçak drone
add(pad, 0, lp(saw_pad([note(45), note(52)], 3.4, 1.0), 500), .9)
# 3.2 - 6.3 ve 8.7 - 25.2 arası akor yürüyüşü (2 sn'lik ölçüler)
def chords(t0, t1, prog, cutoff=1800, amp=1.0):
    t = t0
    i = 0
    while t < t1 - .05:
        d = min(2.0, t1 - t)
        c = prog[i % len(prog)]
        add(pad, t, lp(saw_pad([note(n) for n in CH[c]] + [note(CH[c][0] + 12)], d + .1), cutoff), .55 * amp)
        add(mus, t, bass(note(ROOT[c]), d), .8 * amp)
        t += 2.0
        i += 1

chords(3.2, 6.3, PROG, 1500)
add(pad, 6.3, lp(saw_pad([note(57), note(64), note(69)], 2.5, .6), 700), .5)  # kırılma: kapalı pad
chords(8.7, 24.7, PROG, 2200)
# final: F - G - C (majör çözülüş)
for t0, c, d in ((25.2, 'F', 1.5), (26.7, 'G', 1.6), (28.3, 'C', 1.7)):
    add(pad, t0, lp(saw_pad([note(n) for n in CH[c]] + [note(CH[c][0] + 12), note(CH[c][1] + 12)], d, .08), 3500), .7)
    add(mus, t0, bass(note(ROOT[c]), d), .9)

# davul
def beat_times(a, b, step=B):
    k = np.ceil((a - G0) / step - 1e-9)
    t = G0 + k * step
    while t < b - 1e-6:
        yield round(t, 4)
        t += step

for t in beat_times(3.2, 6.3):
    add(mus, t, kick(), .9)
for t in beat_times(3.2, 6.3, B / 2):
    add(mus, t, hat(a=.25 if (t - G0) % B else .12), 1, .3)
# kırılma: kalp atışı
for t in (6.9, 7.15, 7.9, 8.15):
    add(mus, t, kick(.4, 90, 40, 30), .55)
for t in beat_times(8.7, 23.7):
    add(mus, t, kick(), 1.0)
    if round((t - G0) / B) % 2 == 1:
        add(mus, t, clap(), .6, -.1)
for t in beat_times(8.7, 20.2, B / 2):
    add(mus, t, hat(a=.28 if (t - G0) % B else .14), 1, .3)
for t in beat_times(20.2, 23.7, B / 4):  # enerji artışı
    add(mus, t, hat(a=.22), 1, .35)
# trampet rulosu 23.7 -> 24.9
t = 23.7
step = .25
while t < 24.9:
    add(mus, t, clap(.2), .35 + .5 * (t - 23.7) / 1.2, 0)
    step = max(.0625, step * .8)
    t += step
# final davul (yarım tempo)
for t in (25.2, 26.2, 26.7, 27.7, 28.3):
    add(mus, t, kick(.6, 150, 40, 22), 1.0)
for t in (25.7, 26.7, 27.2):
    add(mus, t, clap(), .5)

# ---------- efektler (animasyonla birebir) ----------
add(fx, 0.0, lp(noise(3.3), 180) * np.linspace(.2, .6, int(3.3 * SR)), .5)  # inşaat gürültüsü
for t, p in ((.2, 0), (.7, -.2), (1.1, .2), (1.45, 0)):
    add(fx, t, hit(), .9, p)
for i in range(6):  # vinç zinciri / metal tıkırtı
    add(fx, .35 + i * .45, clink()[:int(.15 * SR)], .08, .6)
add(fx, 3.1, whoosh(.6), .75, (-.9, .9))
add(fx, 3.3, lp(noise(1.4), 120) * np.sin(np.linspace(0, np.pi, int(1.4 * SR))), 1.2)  # binalar yükseliyor
wl = np.sort(rng.uniform(3.9, 6.2, 18))
for i, t in enumerate(wl):  # pencere ışıkları
    add(fx, t, tick(), .06, rng.uniform(-.8, .8))
add(fx, 5.1, hit(1.2), 1.0)
add(fx, 6.2, whoosh(.8), .75, (.9, -.9))
add(fx, 6.9, whoosh(1.1, rev=True), .4, (-.5, .5))
add(fx, 8.0, clink(), .45, .1)
add(fx, 8.0, riser(.7), .35)
add(fx, 8.7, boom(1.8), 1.0)
add(fx, 10.05, whoosh(.6), .75, (-.9, .9))
add(fx, 10.75, stamp(), .6)      # pin iniyor
add(fx, 10.9, whoosh(.6), .5, (.3, -.3))
for i in range(4):
    add(fx, 11.6 + i * .55, tick(), .35, -.3 + i * .2)
add(fx, 14.0, stamp(), 1.0)
add(fx, 15.2, whoosh(.6), .75, (.9, -.9))
for t in (15.6, 16.25, 16.9, 17.55, 18.2):
    add(fx, t, buzz(), .7)
    add(fx, t + .02, ping(), .45, .2)
add(fx, 19.0, hit(.8), .7)
add(fx, 20.1, whoosh(.5), .7, (-.9, .1))
add(fx, 20.2, whoosh(.5), .7, (.9, -.1))
add(fx, 20.35, hit(), .8, -.3)
add(fx, 20.6, hit(), .8, .3)
add(fx, 22.2, pop(), .35)
add(fx, 22.2, whoosh(.5), .4)
add(fx, 23.5, riser(1.7), .7)
add(fx, 25.2, boom(2.6), 1.1)
add(fx, 25.2, whoosh(2.3), .45)  # balon yükseliyor
add(fx, 25.5, hit(), .7)
add(fx, 26.1, hit(), .8)
add(fx, 27.3, clink(), .25, -.2)
add(fx, 27.8, pop(), .4)
add(fx, 28.3, boom(1.7), .9)

# ---------- açılış: ARANIYOR (zamanlar ana çizelgeye göre negatif) ----------
H = -OFF
add(fx, H + .05, boom(1.6), 1.0)
add(fx, H + .05, hit(), .9)
add(fx, H + .33, whoosh(.45, down=True), .75, (-.3, .3))
add(fx, H + .8, stamp(), 1.0)
add(fx, H + 1.3, pop(), .5)
add(fx, H + 1.35, hit(.5), .45)
add(fx, H + 1.75, tick(), .4)
add(fx, H + 1.95, pop(), .35, .2)
add(fx, H + 2.1, riser(.9), .45)
add(fx, H + 2.75, whoosh(.5), .75, (-.9, .9))
for t in beat_times(H + .1, -.1):
    add(mus, t, kick(), .9)
    add(mus, t, bass(note(33), .45), .7)
for t in beat_times(H + .1, H + 2.2, B / 2):
    add(mus, t, hat(a=.2), 1, .3)
t = H + 2.2
step = .2
while t < H + 2.95:
    add(mus, t, clap(.2), .3 + .4 * (t - H - 2.2) / .75)
    step = max(.06, step * .8)
    t += step

# ---------- miks ----------
def reverb(x, d=1.6, mix=.25):
    t = tt(d)
    irl = rng.standard_normal(len(t)) * np.exp(-t * 4)
    irr = rng.standard_normal(len(t)) * np.exp(-t * 4)
    irl, irr = lp(irl, 5000) / 30, lp(irr, 5000) / 30
    wet = np.stack([signal.fftconvolve(x[:, 0], irl)[:N], signal.fftconvolve(x[:, 1], irr)[:N]], 1)
    return x + wet * mix

padw = reverb(pad, 2.2, .5)
mix = mus * .75 + padw * .5 + reverb(fx, 1.4, .3) * .9
mix = hp(mix.T, 25).T
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.8) / np.tanh(1.8)
fade = np.ones(N)
fade[-int(.8 * SR):] = np.linspace(1, 0, int(.8 * SR))
fade[:int(.01 * SR)] = np.linspace(0, 1, int(.01 * SR))
mix *= fade[:, None] * .89
wavfile.write(__import__('sys').argv[1], SR, (mix * 32767).astype(np.int16))
print('ok', np.max(np.abs(mix)))
