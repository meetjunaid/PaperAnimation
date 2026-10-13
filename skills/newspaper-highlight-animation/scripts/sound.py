"""Synthesised projector rattle: a fast, bright, continuous run of tiny mechanical
clicks under the whole video, like film running through a projector gate.
Pure numpy, so there is no sample to license.

Tweak the knobs below, then preview without rendering any video:

    ~/.cache/newspaper-highlight-animation/venv-*/bin/python sound.py preview.wav && afplay preview.wav
"""
import math
import sys
import wave
import numpy as np

# ---- knobs -------------------------------------------------------------------
SPEED = 1.0                # >1 = faster rattle (shorter gaps), <1 = slower
LEVEL_DB = -36.0           # overall loudness, RMS dBFS. Raise towards -24 for louder
TONE_HZ = (9000, 13500)    # the two click voices. Lower = darker, chunkier clicks
CLICK_MS = 5.0             # how long each click rings
HISS_DB = -47.0            # faint mechanical hiss between clicks (None = off)

# One 300 ms loop of the mechanism: the gap before each click, its accent and
# which TONE_HZ voice it uses. The irregular 13/30 ms pairs are what make it
# sound like a gear train rather than a metronome.
GAPS_MS = [24, 23, 13, 30, 24, 29, 24, 24, 23, 13, 30, 24, 19]
ACCENT_DB = [-5.3, -2.9, -0.1, -5.9, -4.2, -2.7, -4.9, -3.8, -2.9, 0.0, -5.5, -4.2, -2.1]
VOICE = [0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1]
# ------------------------------------------------------------------------------

SR = 48000


def bandpass(x, f, q):
    """RBJ biquad band-pass (constant 0 dB peak gain)."""
    w0 = 2 * math.pi * f / SR
    al = math.sin(w0) / (2 * q)
    a0 = 1 + al
    b0, b2, a1, a2 = al / a0, -al / a0, -2 * math.cos(w0) / a0, (1 - al) / a0
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        y[i] = b0 * v + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, y[i]
    return y


def click(rng, hz):
    n = int(CLICK_MS * 3 / 1000 * SR)
    t = np.arange(n) / SR
    env = np.minimum(t / 0.0025, 1) * np.exp(-t / (CLICK_MS / 3000))
    return bandpass(rng.standard_normal(n) * env, hz * rng.uniform(0.95, 1.05), 1.2)


def rattle(duration, seed):
    rng = np.random.default_rng(seed)
    out = np.zeros(int(round(duration * SR)))
    t, k = 0.0, 0
    while t < duration:
        j = k % len(GAPS_MS)
        c = click(rng, TONE_HZ[VOICE[j]]) * 10 ** ((ACCENT_DB[j] + rng.uniform(-0.8, 0.8)) / 20)
        i = int(t * SR)
        n = min(len(c), len(out) - i)
        out[i:i + n] += c[:n]
        k += 1
        t += GAPS_MS[k % len(GAPS_MS)] / 1000 / SPEED
    out *= 10 ** (LEVEL_DB / 20) / np.sqrt((out ** 2).mean())
    if HISS_DB is not None:
        hiss = bandpass(rng.standard_normal(len(out)), 9000, 0.7)
        out += hiss * 10 ** (HISS_DB / 20) / np.sqrt((hiss ** 2).mean())
    out *= min(1.0, 10 ** (-1 / 20) / np.abs(out).max())  # never clip
    f = int(0.005 * SR)
    out[-f:] *= np.linspace(1, 0, f)  # no pop at the cut
    return out


def write_rattle(path, duration, seed):
    pcm = (np.repeat(rattle(duration, seed)[:, None], 2, 1) * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    write_rattle(sys.argv[1] if len(sys.argv) > 1 else "preview.wav", 3.0, 0)
