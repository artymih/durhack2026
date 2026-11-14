import time
import cv2
import numpy as np

from glove.tracker import HandTracker
from glove.hands import HandsModel
from glove.visuals import (
    draw_hand_skeleton,
    #draw_glowing_orb,
)


NOTE_NAMES = [
    "C", "C#", "D", "D#",
    "E", "F", "F#",
    "G", "G#", "A",
    "A#", "B"
]


tracker = HandTracker()
hands_model = HandsModel()

trail = None

try:

    while True:

        frame, raw_hands = tracker.read()

        if frame is None:
            continue

        h, w = frame.shape[:2]

        hands_model.aspect = w / h

        states = hands_model.update(
            raw_hands,
            time.monotonic()
        )

        if trail is None:
            trail = frame.copy()
            trail[:] = 0

        trail = cv2.addWeighted(
            trail,
            0.95,
            np.zeros_like(trail),
            0.05,
            0,
        )

        display = cv2.convertScaleAbs(
            frame,
            alpha=0.4,
            beta=0,
        )

        for hand in raw_hands:

            role = hand.label.lower()

            state = states.get(role)

            if state is None:
                continue

            points = [
                (
                    int(x * w),
                    int(y * h),
                )
                for x, y, z in hand.landmarks
            ]

            note = NOTE_NAMES[
                int(state.x * 12) % 12
            ]

            orb_point = points[9]

            draw_hand_skeleton(
                display,
                points,
                note,
            )

            # draw_glowing_orb(
            #     display,
            #     orb_point,
            #     note,
            # )

            # draw_glowing_orb(
            #     trail,
            #     orb_point,
            #     note,
            # )

            cv2.putText(
                display,
                role,
                (
                    orb_point[0],
                    orb_point[1] - 20,
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )

        output = cv2.addWeighted(
            display,
            1.0,
            trail,
            0.5,
            0,
        )

        cv2.imshow(
            "Visual Test",
            output,
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):

            cv2.imwrite(
                "visual_artwork.png",
                trail,
            )

            print(
                "Saved visual_artwork.png"
            )

        elif key == ord("c"):

            trail[:] = 0

            print(
                "Trail cleared"
            )

        elif key == ord("q"):

            break

finally:

    tracker.close()
    cv2.destroyAllWindows()