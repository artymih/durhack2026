from glove.config import CONFIG
from glove.music import (
    SCALES,
    SCALE_ORDER,
    degree_to_midi,
    midi_to_name,
    quantize_cell,
    CHORD_COLORS,
)


class Instrument:

    def __init__(self, synth):

        self.synth = synth

        self.cell = -1
        self.gate = False

        self.scale_idx = SCALE_ORDER.index("minor_pentatonic")

    def update(self, hands, dt):

        m = CONFIG["music"]

        info = {
            "mode": "Play",
            "lead_midi": None,
            "lead_name": "",
            "chord_name": None,
            "events": [],
        }

        right = hands.get("right")
        left = hands.get("left")

        # ------------------------------------------
        # Left X -> scale
        # ------------------------------------------

        LEFT_X_MIN = 0.10
        LEFT_X_MAX = 0.90

        if left is not None:
            u_scale = min(
                max(
                    (left.x - LEFT_X_MIN) / (LEFT_X_MAX - LEFT_X_MIN),
                    0.0,
                ),
                1.0,
            )

            self.scale_idx = quantize_cell(
                u_scale,
                len(SCALE_ORDER),
                self.scale_idx,
            )

        scale_name = SCALE_ORDER[self.scale_idx]
        scale = SCALES[scale_name]
        info["scale"] = scale_name

        # ==================================================
        # RIGHT HAND - LEAD
        # ==================================================

        if right is None:

            self.gate = False

            self.synth.set_lead(
                midi=None,
                gate=False,
                cutoff_hz=1000.0,
                vibrato_cents=0.0,
                reverb=0.0,
                delay=0.0,
            )

        else:

            # ------------------------------------------
            # Y -> pitch
            # ------------------------------------------

            u = 1.0 - (right.y - 0.1) / 0.8

            base = (
                m["root_midi"]
                + m["lead_root_offset"]
            )

            if m["quantize"]:

                cells = (
                    len(scale)
                    * m["lead_octaves"]
                    + 1
                )

                self.cell = min(self.cell, cells - 1)

                self.cell = quantize_cell(
                    u,
                    cells,
                    self.cell,
                )

                midi = degree_to_midi(
                    scale,
                    self.cell,
                    base,
                )

            else:

                midi = (
                    base
                    + min(max(u, 0.0), 1.0)
                    * 12
                    * m["lead_octaves"]
                )

            # ------------------------------------------
            # X -> brightness
            # ------------------------------------------

            bright = 1.0 - min(
                max(
                    (right.x - 0.15) / 0.7,
                    0.0,
                ),
                1.0,
            )

            cutoff = 250.0 * (32.0 ** bright)

            # ------------------------------------------
            # Gate
            # ------------------------------------------

            if right.openness > 0.45:
                self.gate = True

            elif right.openness < 0.25:
                self.gate = False

            # ------------------------------------------
            # Roll -> vibrato
            # ------------------------------------------

            roll = -1 * getattr(
                right,
                "roll",
                0.0,
            )

            DEAD_ZONE = 10.0
            MAX_ROLL = 70.0
            MAX_VIBRATO = 40.0

            t = (roll - DEAD_ZONE) / (MAX_ROLL - DEAD_ZONE)
            t = min(max(t, 0.0), 1.0)

            vibrato = t * MAX_VIBRATO

            # ------------------------------------------
            # Depth -> reverb
            # ------------------------------------------

            depth = getattr(
                right,
                "depth",
                0.0,
            )

            DEPTH_NEAR = 0.70
            DEPTH_FAR = 0.30

            reverb = min(
                max(
                    (depth - DEPTH_FAR) / (DEPTH_NEAR - DEPTH_FAR),
                    0.0,
                ),
                1.0,
            )

            # ------------------------------------------
            # Pinch -> delay
            # ------------------------------------------

            delay = min(
                max(
                    getattr(
                        right,
                        "pinch",
                        0.0,
                    ),
                    0.0,
                ),
                1.0,
            )

            self.synth.set_lead(
                midi=midi,
                gate=self.gate,
                cutoff_hz=cutoff,
                vibrato_cents=vibrato,
                reverb=reverb,
                delay=delay,
            )

            info["lead_midi"] = midi
            info["lead_name"] = midi_to_name(midi)

        # ==================================================
        # LEFT HAND - CHORDS
        # ==================================================

        if left is None:

            self.synth.set_pad(
                notes=None,
                cutoff_hz=2500,
                level=0.0,
            )

        else:

            root = m["root_midi"]

            roll = getattr(
                left,
                "roll",
                0.0,
            )

            # ------------------------------------------
            # Chord colour
            # ------------------------------------------

            if roll < -60:
                chord_name = "power"

            elif roll < -20:
                chord_name = "sus2"

            elif roll < 20:
                chord_name = "triad"

            elif roll < 60:
                chord_name = "add7"

            else:
                chord_name = "add9"

            degrees = CHORD_COLORS[chord_name]

            notes = []

            finger_states = [
                getattr(left, "thumb", False),
                getattr(left, "index", False),
                getattr(left, "middle", False),
                getattr(left, "ring", False),
                getattr(left, "pinky", False),
            ]

            for finger_on, degree in zip(
                finger_states,
                degrees,
            ):

                if finger_on:

                    notes.append(
                        degree_to_midi(
                            scale,
                            degree,
                            root+36,
                        )
                    )

            # ------------------------------------------
            # Y -> volume
            # range 0.5 -> 1.0
            # ------------------------------------------

            volume = (
                0.5
                + 0.5
                * min(
                    max(
                        1.0 - left.y,
                        0.0,
                    ),
                    1.0,
                )
            )

            if notes:

                self.synth.set_pad(
                    notes=notes,
                    cutoff_hz=2500,
                    level=volume,
                )

                info["chord_name"] = chord_name

            else:

                self.synth.set_pad(
                    notes=None,
                    cutoff_hz=2500,
                    level=0.0,
                )

        return info
