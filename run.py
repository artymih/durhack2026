import time
import cv2
import numpy as np

from glove.tracker import HandTracker
from glove.hands import HandsModel
from glove.instrument import Instrument
from glove.synth import Synth
from glove.config import CONFIG
from glove.music import midi_to_name
from glove.visuals import (
    draw_orb,
    draw_skeleton,
    draw_dev_info,
    add_border,
    note_colours,
)


def pitch_class(name):
    return name.rstrip("0123456789-")


def main():

    print("Orb running. [S] save  [C] clear  [D] dev info  [Q/Esc] quit")

    tracker = HandTracker()

    hands_model = HandsModel()

    synth = Synth()
    synth.start()

    instrument = Instrument(synth)

    root_note = pitch_class(midi_to_name(CONFIG["music"]["root_midi"]))

    displayed_orbs = None
    permanent_orbs = None

    dev_mode = False

    previous_time = time.monotonic()

    try:

        while True:

            frame, raw_hands = tracker.read()

            if frame is None:
                continue

            now = time.monotonic()

            dt = now - previous_time
            previous_time = now

            h, w = frame.shape[:2]

            hands_model.aspect = w / h

            # tracker -> hands
            hands = hands_model.update(
                raw_hands,
                now,
            )

            # hands -> instrument -> synth
            info = instrument.update(
                hands,
                dt,
            )

            left = hands.get("left")
            right = hands.get("right")

            if displayed_orbs is None:
                displayed_orbs = np.zeros_like(frame)

            if permanent_orbs is None:
                permanent_orbs = np.zeros_like(frame)

            lead_name = info["lead_name"]

            lead_note = pitch_class(lead_name) if lead_name else None

            chord_label = info["chord_name"] or "none"

            if dev_mode:

                display_frame = frame.copy()

                for hand in (left, right):

                    if hand is not None:
                        display_frame = draw_skeleton(
                            display_frame,
                            hand.landmarks,
                        )

                display_frame = draw_dev_info(
                    display_frame,
                    hands,
                )

            else:

                displayed_orbs = cv2.convertScaleAbs(
                    displayed_orbs,
                    alpha=0.90,
                )

                display_frame = cv2.convertScaleAbs(
                    frame,
                    alpha=0.4,
                    beta=0,
                )

                for hand, note in (
                    (right, lead_note),
                    (left, root_note),
                ):

                    if hand is None or note is None:
                        continue

                    orb_center = (
                        int(hand.x * w),
                        int(hand.y * h),
                    )

                    displayed_orbs = draw_orb(
                        displayed_orbs,
                        orb_center,
                        note,
                    )

                    permanent_orbs = draw_orb(
                        permanent_orbs,
                        orb_center,
                        note,
                    )

                display_frame = cv2.add(
                    display_frame,
                    displayed_orbs,
                )

            final_display = add_border(
                display_frame,
                lead_name or "None",
                f"{chord_label} - {info['scale']}",
                note_colours.get(lead_note, (120, 120, 120)),
            )

            cv2.imshow(
                "The Harmonic Orb",
                final_display,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("s"):
                cv2.imwrite("orb_artwork.png", permanent_orbs)
                print("Saved orb_artwork.png")

            elif key == ord("c"):
                displayed_orbs = np.zeros_like(frame)

            elif key in (ord("d"), ord("D")):
                dev_mode = not dev_mode
                print(f"Dev info {'on' if dev_mode else 'off'}")

            elif key == ord("q") or key == 27:
                break

            elif key != 255:
                print(f"Unhandled key: {key}")

    finally:

        if permanent_orbs is not None:
            cv2.imwrite("orb_artwork.png", permanent_orbs)
            print("Final artwork saved to orb_artwork.png")

        tracker.close()

        synth.stop()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
