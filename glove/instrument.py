from glove.config import CONFIG
from glove.music import (
    SCALES,
    degree_to_midi,
    midi_to_name,
    quantize_cell,
)


class Instrument:

    def __init__(self, synth):

        self.synth = synth

        self.cell = -1
        self.gate = False

    def update(self, hands, dt):

        m = CONFIG["music"]

        scale = SCALES[m["lead_scale"]]

        info = {
            "mode": "Play",
            "lead_midi": None,
            "lead_name": "",
            "chord_name": None,
            "events": [],
        }

        right = hands.get("right")
        left = hands.get("left")

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
            # X -> pitch
            # ------------------------------------------

            u = (right.x - 0.1) / 0.8

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
            # Y -> brightness
            # ------------------------------------------

            bright = 1.0 - min(
                max(
                    (right.y - 0.15) / 0.7,
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

            vibrato = min(
                abs(
                    getattr(
                        right,
                        "roll",
                        0.0,
                    )
                ) * 80.0,
                80.0,
            )

            # ------------------------------------------
            # Depth -> reverb
            # ------------------------------------------

            reverb = min(
                max(
                    getattr(
                        right,
                        "depth",
                        0.0,
                    ),
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

            if roll < -0.3:

                chord_name = "sus2"

                degrees = [
                    0,  # root
                    1,  # 2nd
                    4,  # 5th
                    6,  # 7th
                    8,  # 9th
                ]

            elif roll > 0.3:

                chord_name = "major"

                degrees = [
                    0,  # root
                    2,  # 3rd
                    4,  # 5th
                    6,  # 7th
                    8,  # 9th
                ]

            else:

                chord_name = "minor"

                degrees = [
                    0,  # root
                    2,  # scale 3rd
                    4,  # 5th
                    6,  # 7th
                    8,  # 9th
                ]

            notes = []

            if getattr(left, "thumb", False):
                notes.append(
                    degree_to_midi(
                        scale,
                        degrees[0],
                        root,
                    )
                )

            if getattr(left, "index", False):
                notes.append(
                    degree_to_midi(
                        scale,
                        degrees[1],
                        root,
                    )
                )

            if getattr(left, "middle", False):
                notes.append(
                    degree_to_midi(
                        scale,
                        degrees[2],
                        root,
                    )
                )

            if getattr(left, "ring", False):
                notes.append(
                    degree_to_midi(
                        scale,
                        degrees[3],
                        root,
                    )
                )

            if getattr(left, "pinky", False):
                notes.append(
                    degree_to_midi(
                        scale,
                        degrees[4],
                        root,
                    )
                )

            # ------------------------------------------
            # Y -> volume
            # top = loud
            # bottom = quiet
            # ------------------------------------------

            volume = min(
                max(
                    1.0 - left.y,
                    0.0,
                ),
                1.0,
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