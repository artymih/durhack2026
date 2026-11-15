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

SCALES = {
    "harmonic_minor":   (0, 2, 3, 5, 7, 8, 11),
    "natural_minor":    (0, 2, 3, 5, 7, 8, 10),
    "dorian":           (0, 2, 3, 5, 7, 9, 10),
    "minor_pentatonic": (0, 3, 5, 7, 10),
    "blues":            (0, 3, 5, 6, 7, 10),
    "major_pentatonic": (0, 2, 4, 7, 9),
}

SCALE_ORDER = (
    "harmonic_minor",
    "natural_minor",
    "dorian",
    "minor_pentatonic",
    "blues",
    "major_pentatonic",
)

def midi_to_hz(m):
    '''takes a midi key note and converts to hz'''
    return 440 * 2 ** ((m - 69) / 12)

def degree_to_midi(scale, degree, root_midi):
    ''' gives nth note from the root within the scale '''
    octave, index = divmod(degree, len(scale))
    return root_midi + 12 * octave + scale[index]

CHORD_COLORS = {
    "power": [0, 4],
    "sus2": [0, 1, 4],
    "triad": [0, 2, 4],
    "add7": [0, 2, 4, 6],
    "add9": [0, 2, 4, 6, 8],
}

# Left-hand finger count -> chord root degree in natural minor (Am F C G Dm in A). 0 fingers = silence.
FINGERS_TO_DEGREE = {1: 0, 2: 5, 3: 2, 4: 6, 5: 3}


def chord_midi(scale, degree, root_midi, color="triad"):
    """MIDI notes of a chord built on `degree`: stack the scale steps listed in CHORD_COLORS.
    Use a 7-note scale (natural_minor), not the pentatonic."""
    return [degree_to_midi(scale, degree + step, root_midi) for step in CHORD_COLORS[color]]

def quantize_cell(v, cells, prev=-1, margin=0.2):
    """Map v (0..1) to a zone 0..cells-1. Once in a zone, stay in it until v is
    `margin` zones past its edge, so the note doesn't flutter on a border."""
    x = min(max(v, 0.0), 0.999999) * cells   # clamp to 0..1, then scale to 0..cells
    cell = int(x)                            # round down = which zone we're in
    if prev >= 0 and cell != prev:
        # how far past the edge of the old zone are we, measured in zones?
        past = x - (prev + 1) if cell > prev else prev - x
        if past < margin:
            return prev                      # not far enough yet, stay put
    return cell


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def midi_to_name(m):
    """MIDI note number -> label for the screen, e.g. 69 -> 'A4'."""
    m = round(m)  # the lead can be a fractional note when quantize is off
    return NOTE_NAMES[m % 12] + str(m // 12 - 1)

def chord_notes(scale, root_midi, colour):
    return [
        degree_to_midi(scale, d, root_midi)
        for d in CHORD_COLORS[colour]
    ]