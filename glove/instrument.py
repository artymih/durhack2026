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

from glove.config import CONFIG
from glove.music import SCALES, degree_to_midi, midi_to_name, quantize_cell


class Instrument:
    def __init__(self, synth):
        self.synth = synth
        self.cell = -1        # last lead zone, remembered so quantize_cell can be sticky
        self.gate = False     # is the lead sounding?

    def update(self, hands, dt):
        m = CONFIG["music"]
        scale = SCALES[m["lead_scale"]]
        info = {"mode": "Play", "lead_midi": None, "lead_name": "", "chord_name": None, "events": []}

        right = hands.get("right")
        if right is None:
            self.gate = False
            self.synth.set_lead(midi=None, gate=False, cutoff_hz=1000.0,
                                vibrato_cents=0.0, reverb=0.0, delay=0.0)
            return info

        # --- pitch: hand x -> note ---
        u = (right.x - 0.1) / 0.8   # use the middle 80% of the screen so you don't reach for the edges
        base = m["root_midi"] + m["lead_root_offset"]
        if m["quantize"]:
            cells = len(scale) * m["lead_octaves"] + 1
            self.cell = quantize_cell(u, cells, self.cell)
            midi = degree_to_midi(scale, self.cell, base)
        else:
            midi = base + min(max(u, 0.0), 1.0) * 12 * m["lead_octaves"]

        # --- brightness: hand y -> filter cutoff (up = brighter), 250 Hz .. 8000 Hz ---
        bright = 1.0 - min(max((right.y - 0.15) / 0.7, 0.0), 1.0)
        cutoff = 250.0 * 32.0 ** bright

        # --- gate: open hand = sound, fist = mute (two thresholds so it doesn't flicker) ---
        if right.openness > 0.45:
            self.gate = True
        elif right.openness < 0.25:
            self.gate = False

        self.synth.set_lead(midi=midi, gate=self.gate, cutoff_hz=cutoff,
                            vibrato_cents=0.0, reverb=0.2, delay=0.0)

        info["lead_midi"] = midi
        info["lead_name"] = midi_to_name(midi)
        return info
