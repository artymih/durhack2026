import time
import cv2

from glove.tracker import HandTracker
from glove.hands import HandsModel
from glove.instrument import Instrument
from glove.synth import Synth


def main():

    tracker = HandTracker()

    hands_model = HandsModel()

    synth = Synth()
    synth.start()

    instrument = Instrument(synth)

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

            # ----------------------------------
            # HUD
            # ----------------------------------

            left = hands.get("left")
            right = hands.get("right")

            y = 25

            cv2.putText(
                frame,
                f"Lead: {info['lead_name']}",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

            y += 25

            cv2.putText(
                frame,
                f"Chord: {info['chord_name']}",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

            y += 25

            cv2.putText(
                frame,
                f"Audio: {synth.level():.2f}",
                (10, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )

            # ----------------------------------
            # Left hand info
            # ----------------------------------

            if left is not None:

                y += 35

                cv2.putText(
                    frame,
                    f"L vol={1.0-left.y:.2f}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                y += 20

                cv2.putText(
                    frame,
                    f"L roll={left.roll:.1f}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

            # ----------------------------------
            # Right hand info
            # ----------------------------------

            if right is not None:

                y += 35

                cv2.putText(
                    frame,
                    f"R reverb={right.depth:.2f}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                y += 20

                cv2.putText(
                    frame,
                    f"R pinch={right.pinch:.2f}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

                y += 20
                
                cv2.putText(
                    frame,
                    f"R vibrato={right.roll:.2f}",
                    (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )

            # ----------------------------------
            # Draw hand landmarks
            # ----------------------------------

            for hand in raw_hands:

                for x, ylm, z in hand.landmarks:

                    px = int(x * w)
                    py = int(ylm * h)

                    cv2.circle(
                        frame,
                        (px, py),
                        4,
                        (0, 255, 0),
                        -1,
                    )

                tx = int(
                    hand.landmarks[0][0] * w
                )

                ty = int(
                    hand.landmarks[0][1] * h
                )

                cv2.putText(
                    frame,
                    hand.label,
                    (tx, ty),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 0, 0),
                    2,
                )

            cv2.imshow(
                "AirGlove",
                frame,
            )

            key = cv2.waitKey(1) & 0xFF

            if key == 27:  # ESC
                break

    finally:

        tracker.close()

        synth.stop()

        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()