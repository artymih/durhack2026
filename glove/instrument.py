"""The creative file: hand states in, sound out. Mappings live HERE. (Owner: C)

Each mode is a small class with update(hands, dt) so teammates can add modes without clashing.

v1 mapping, "Play" mode
  RIGHT hand (lead)
    x            -> pitch, quantized to minor pentatonic over 2 octaves (hysteresis at note borders)
    y            -> filter brightness (up = brighter)
    depth        -> reverb (far = wetter)
    pinch        -> echo throw
    roll (tilt)  -> vibrato depth
    openness     -> gate (Schmitt on > 0.45, off < 0.25), so a fist mutes
  LEFT hand (pad)
    fingers 1..5 -> chord (FINGERS_TO_DEGREE in music.py); a fist or no hand = silence
    roll         -> chord colour: tilt left = sus2, level = triad, tilt right = add7
    y            -> pad brightness
    depth        -> pad volume
v1 "Strike" mode (toggle with M)
  right hand downward flick (hand.strike) -> synth.pluck(note from x, velocity from strike_vel)
  left hand downward flick               -> synth.drum(kick / snare / hat by x third)

TODO:
- class Instrument(synth, cfg): update(hands: dict[str, HandState | None], dt) -> info dict for visuals
    info = {"mode": str, "lead_midi": float | None, "lead_name": str, "chord_name": str | None,
            "events": [{"type": "pluck" | "drum", "x": float, "y": float, "vel": float}]}
- next_mode(), toggle_quantize(), transpose(semitones), panic() (silence everything)
- gesture to switch mode so nobody touches the keyboard on stage (e.g. both hands fist for 1 s)
"""
