import cv2
import numpy as np

from glove.tracker import HandTracker


NOTE_COLOURS = {
    "C":  (0, 0, 255),
    "C#": (0, 85, 255),
    "D":  (0, 165, 255),
    "D#": (0, 215, 255),
    "E":  (0, 255, 255),
    "F":  (0, 255, 128),
    "F#": (0, 255, 0),
    "G":  (255, 255, 0),
    "G#": (255, 150, 0),
    "A":  (255, 0, 0),
    "A#": (255, 0, 140),
    "B":  (255, 0, 255),
}

NOTE_NAMES = list(NOTE_COLOURS.keys())


def draw_glowing_orb(frame, orb_point, current_note):

    colour = NOTE_COLOURS.get(
        current_note,
        (120, 120, 120),
    )

    glow = np.zeros_like(frame)

    cv2.circle(
        glow,
        orb_point,
        45,
        colour,
        -1,
    )

    glow = cv2.GaussianBlur(
        glow,
        (91, 91),
        0,
    )

    cv2.add(
        frame,
        glow,
        dst=frame,
    )

    cv2.circle(
        frame,
        orb_point,
        12,
        colour,
        -1,
    )

    cv2.circle(
        frame,
        orb_point,
        6,
        (255, 255, 255),
        -1,
    )


tracker = HandTracker()

orb_canvas = None

try:

    while True:

        frame, hands = tracker.read()

        if frame is None:
            continue

        h, w = frame.shape[:2]

        if orb_canvas is None:

            orb_canvas = np.zeros_like(frame)

        display = cv2.convertScaleAbs(
            frame,
            alpha=0.4,
            beta=0,
        )

        for hand in hands:

            palm = hand.landmarks[[0, 5, 9, 13, 17]]

            px = int(
                palm[:, 0].mean() * w
            )

            py = int(
                palm[:, 1].mean() * h
            )

            orb_point = (px, py)

            note = NOTE_NAMES[
                min(
                    int(px / w * 12),
                    11,
                )
            ]

            draw_glowing_orb(
                display,
                orb_point,
                note,
            )

            draw_glowing_orb(
                orb_canvas,
                orb_point,
                note,
            )

            cv2.putText(
                display,
                hand.label,
                (px + 20, py),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                1,
            )

        output = cv2.addWeighted(
            display,
            1.0,
            orb_canvas,
            0.3,
            0,
        )

        cv2.imshow(
            "Orb Visual Test",
            output,
        )

        key = cv2.waitKey(1) & 0xFF

        if key == ord("s"):

            cv2.imwrite(
                "orb_artwork.png",
                orb_canvas,
            )

            print(
                "Saved orb_artwork.png"
            )

        elif key == ord("c"):

            orb_canvas[:] = 0

            print(
                "Canvas cleared"
            )

        elif key == ord("q"):

            break

finally:

    if orb_canvas is not None:

        cv2.imwrite(
            "orb_artwork.png",
            orb_canvas,
        )

        print(
            "Final artwork saved"
        )

    tracker.close()
    cv2.destroyAllWindows()