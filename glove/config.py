"""Every tunable number lives here. (Owner: C, but anyone may add a setting.)

TODO:
- camera: index, width, height, fps
- model_path: models/hand_landmarker.task
- swap_handedness: bool (flip if left/right hands come out swapped)
- smoothing: One Euro params (min_cutoff, beta) for position / size / angle / 0-1 values
- hold_sec: keep a hand alive this long after tracking drops out (~0.15)
- finger_hold_sec: finger count must be stable this long before changing (~0.12)
- depth range: hand size near/far (fraction of frame height, auto-expands)
- strike: min_down_speed, max_speed, refractory_sec
- music: root_midi (57 = A3), lead scale/octaves, pad scale, quantize on/off
- audio: samplerate 44100, blocksize 256
"""

CONFIG = {
    # arty C
    "music": {
        "root_midi": 57,                  # A3. Change this to change the key of the whole instrument
        "lead_scale": "minor_pentatonic", # name of a scale in music.SCALES
        "lead_octaves": 2,                # how many octaves the right hand's left-to-right sweep covers
        "lead_root_offset": 12,           # lead plays this many semitones above the root (12 = one octave up)
        "pad_scale": "natural_minor",     # must be a 7-note scale, used for chords
        "quantize": True
    },
    # megan A
    "camera": {},
    "model_path": "models/hand_landmarker.task",
    "swap_hand": False,
    # amelka B
    "audio": {"samplerate": 44100, "blocksize": 256}
}  
