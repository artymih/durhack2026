CONFIG = {
    # arty C
    "music": {
        "root_midi": 33,                  # A3. Change this to change the key of the whole instrument
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
