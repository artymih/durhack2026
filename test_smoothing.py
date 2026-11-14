"""Fake-data test for the One Euro filter. No camera needed.

Run from the project root:   python test_smoothing.py

The fake signal is a hand that sits still at 0.5, jumps to 0.8 at frame 45, and sits still again,
with a bit of tracking noise on top (like a real, slightly shaky hand).

For each filter setting it prints:
  noise  = how shaky the output is while the hand is still (lower is better)
  lag    = frames after the jump before the output has covered 90% of it (lower is better)
"""
import random
import statistics

from glove.smoothing import OneEuro

FPS = 30
FRAMES = 90
JUMP_AT = 45
LOW, HIGH = 0.5, 0.8
NOISE = 0.01          # standard deviation of the fake tracking jitter


def make_signal():
    random.seed(1)    # same fake data every run, so settings can be compared fairly
    return [(LOW if i < JUMP_AT else HIGH) + random.gauss(0, NOISE) for i in range(FRAMES)]


def run(raw, **settings):
    f = OneEuro(**settings)
    return [f(x, i / FPS) for i, x in enumerate(raw)]


def noise_of(values):
    still = values[10:JUMP_AT]                    # the still stretch before the jump
    return statistics.pstdev(still)


def lag_of(values):
    target = LOW + 0.9 * (HIGH - LOW)
    for i in range(JUMP_AT, FRAMES):
        if values[i] >= target:
            return i - JUMP_AT
    return None                                   # never caught up


if __name__ == "__main__":
    raw = make_signal()
    print(f"{'setting':<28}{'noise':>8}{'lag (frames)':>15}")
    print(f"{'raw input (no filter)':<28}{noise_of(raw):>8.4f}{lag_of(raw):>15}")

    for min_cutoff, beta in [(1.0, 0.0), (0.3, 0.0), (0.3, 5.0), (1.0, 5.0)]:
        out = run(raw, min_cutoff=min_cutoff, beta=beta)
        lag = lag_of(out)
        label = f"min_cutoff={min_cutoff}, beta={beta}"
        print(f"{label:<28}{noise_of(out):>8.4f}{str(lag) if lag is not None else 'never':>15}")

    # Uncomment to see the first frames after the jump, raw vs filtered:
    # out = run(raw, min_cutoff=1.0, beta=5.0)
    # for i in range(JUMP_AT - 2, JUMP_AT + 12):
    #     print(f"frame {i}: raw {raw[i]:.3f} -> filtered {out[i]:.3f}")