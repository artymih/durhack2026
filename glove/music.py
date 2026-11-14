"""Pure music theory, no audio calls. (Owner: C)

TODO:
- SCALES: dict of semitone offsets, e.g. minor_pentatonic [0,3,5,7,10], natural_minor [0,2,3,5,7,8,10],
  major, dorian, ... (different scales = different "worlds"; good for the Marshall Wace theme)
- midi_to_hz(m) = 440 * 2 ** ((m - 69) / 12)
- midi_to_name(m) for the HUD ("A4")
- degree_to_midi(scale, degree, root_midi): degree may be negative or longer than the scale (wraps by octave)
- chord_midi(scale, degree, root_midi, color): color "triad" = steps [0,2,4], "sus2" = [0,1,4], "add7" = [0,2,4,6]
    (steps inside the scale, so chords stay in key)
- FINGERS_TO_DEGREE = {1: 0, 2: 5, 3: 2, 4: 6, 5: 3}  -> i, VI, III, VII, iv  (Am F C G Dm in A minor)
- quantize_cell(v01, cells, prev, margin=0.2): map 0..1 to one of N zones WITH HYSTERESIS so the note
    doesn't flutter on a boundary. Stay in `prev` until you're `margin` cells past the edge.
"""
