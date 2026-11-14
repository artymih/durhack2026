"""Small signal helpers. Hand tracking is jittery, so everything that drives sound goes through these. (Owner: A)

TODO:
- clamp(v, lo=0, hi=1), lerp(a, b, t), remap(v, in_lo, in_hi, out_lo=0, out_hi=1)  (clamped)
- class OneEuro(min_cutoff, beta): .filter(x, t_seconds) -> smoothed x, plus .velocity (units/sec).
    Smooth when slow, snappy when fast. The standard fix for jittery tracking.
- class Schmitt(on, off): noisy 0..1 value -> stable bool (on above `on`, off below `off`)
- class Stable(hold_sec): accept a new discrete value (finger count) only after it has held for hold_sec
- class AutoRange(lo, hi): .expand(v) then .norm(v) -> 0..1, self-calibrating (used for depth)
"""

import math
import numpy as np

def _alpha(cutoff, dt):
    tau = 1 / (2 * np.pi * cutoff)
    return 1 / (1 + tau / dt)

class OneEuro:
    def __init__(self, min_cutoff=1.0, beta=0.0, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.reset()

    def reset(self):
        self.x_hat = None      # last smoothed value
        self.dx_hat = 0.0      # last smoothed speed
        self.t_prev = None
        self.velocity = 0.0    # hands.py reads this for vx / vy

    def __call__(self, x, t):
        if self.x_hat is None:                 # first sample: nothing to smooth against
            self.x_hat, self.t_prev = x, t
            return x

        dt = max(t - self.t_prev, 1e-3)        # never divide by zero

        speed = (x - self.x_hat) / dt

        a_d = _alpha(self.d_cutoff, dt)
        self.dx_hat = a_d * speed + (1 - a_d) * self.dx_hat

        cutoff = self.min_cutoff + self.beta * abs(self.dx_hat)

        a = _alpha(cutoff, dt)
        self.x_hat = a * x + (1 - a) * self.x_hat

        self.velocity = self.dx_hat
        self.t_prev = t
        return self.x_hat

class Stable:
    """Debounce a boolean: only change the output after the new value has held for `frames` calls."""

    def __init__(self, frames=4):
        self.frames = frames
        self.reset()

    def reset(self):
        self.value = None        # the accepted value (None until the first sample)
        self.candidate = None    # what we're thinking of switching to
        self.count = 0           # how many calls in a row the candidate has been seen

    def __call__(self, new):
        if self.value is None:                 # first sample: accept straight away
            self.value = new
            return self.value

        if new == self.value:
            self.count = 0
        elif new == self.candidate:
            self.count += 1                    # same new value again, so one step closer
            if self.count >= self.frames:
                self.value = new               # seen enough times in a row: accept it
                self.count = 0
        else:
            self.candidate = new               # a different new value: start counting from 1
            self.count = 1

        return self.value


if __name__ == "__main__":
    import random
    f = OneEuro(min_cutoff=1.0, beta=0.0)
    for i in range(90):
        t = i / 30
        raw = (0.5 if i < 45 else 0.8) + random.gauss(0, 0.01)   # a step at frame 45, plus noise
        print(f"{raw:.3f} -> {f(raw, t):.3f}")