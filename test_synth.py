import time

from glove.synth import Synth

BPM = 100
BEAT = 60.0 / BPM

s = Synth()
s.start()

sections = [

    # G major (2 bars)
    (
        [55, 59, 62],
        [
            (67, 1),   # G
            (69, 1),   # A
            (71, 2),   # B
            (74, 2),   # D
            (71, 1),
            (69, 1),
        ]
    ),

    # B minor (2 bars)
    (
        [59, 62, 66],
        [
            (71, 1),
            (74, 1),
            (78, 2),   # F#
            (74, 2),
            (71, 1),
            (69, 1),
        ]
    ),

    # C major (2 bars)
    (
        [60, 64, 67],
        [
            (72, 1),
            (76, 1),
            (79, 2),
            (76, 2),
            (74, 1),
            (72, 1),
        ]
    ),

    # C minor (2 bars)
    (
        [60, 63, 67],
        [
            (72, 1),
            (75, 1),
            (79, 2),
            (75, 2),
            (72, 1),
            (70, 1),
        ]
    ),
]

for _ in range(4):

    for chord, melody in sections:

        s.set_pad(
            notes=chord,
            cutoff_hz=2500,
            level=1.0
        )

        for note, beats in melody:

            s.set_lead(
                midi=note,
                gate=True,
                cutoff_hz=2500,
                vibrato_cents=0,
                reverb=0,
                delay=0
            )

            time.sleep(beats * BEAT)

s.set_lead(
    midi=None,
    gate=False,
    cutoff_hz=1000,
    vibrato_cents=0,
    reverb=0,
    delay=0
)

s.set_pad(
    notes=None,
    cutoff_hz=1000,
    level=0
)

time.sleep(1)

s.stop()