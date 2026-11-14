"""Small signal helpers. Hand tracking is jittery, so everything that drives sound goes through these. (Owner: A)

TODO:
- clamp(v, lo=0, hi=1), lerp(a, b, t), remap(v, in_lo, in_hi, out_lo=0, out_hi=1)  (clamped)
- class OneEuro(min_cutoff, beta): .filter(x, t_seconds) -> smoothed x, plus .velocity (units/sec).
    Smooth when slow, snappy when fast. The standard fix for jittery tracking.
- class Schmitt(on, off): noisy 0..1 value -> stable bool (on above `on`, off below `off`)
- class Stable(hold_sec): accept a new discrete value (finger count) only after it has held for hold_sec
- class AutoRange(lo, hi): .expand(v) then .norm(v) -> 0..1, self-calibrating (used for depth)
"""
