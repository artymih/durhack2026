"""Quick visual test for glove/visuals.py. Sits in the project root. Run:  python try_visuals.py

Move your hands in front of the camera. Each hand gets a glowing orb drawn by glove.visuals.draw_glowing_orb,
coloured by the note the instrument WOULD play at that spot (hand x -> quantize -> note -> colour).
No audio is used, so it works without B's synth.

Keys:  s = save orb_artwork.png   c = clear   q = quit

If your function has a different name, change the import below.
"""
import cv2
import numpy as np

from glove.hands import HandState
from glove.instrument import Instrument
from glove.tracker import HandTracker
from glove.visuals import draw_glowing_orb   # <-- the code under test


class FakeSynth:
    """Instrument wants a synth. This one ignores every call, so no audio is needed."""

    def __getattr__(self, name):
        return lambda *args, **kwargs: None


def pitch_class(note_name):
    """midi_to_name() gives 'A4' but the colour table is keyed 'A'. Strip the octave: 'C#5' -> 'C#'."""
    return note_name.rstrip("0123456789-")


tracker = HandTracker()
instruments = {}    # one Instrument per hand slot, so each hand keeps its own sticky note zones
orb_canvas = None   # trail: fades out
artwork = None      # never fades: this is what S saves

try:
    while True:
        frame, hands = tracker.read()
        if frame is None:
            continue

        h, w = frame.shape[:2]
        if orb_canvas is None:
            orb_canvas = np.zeros_like(frame)
            artwork = np.zeros_like(frame)

        orb_canvas = cv2.convertScaleAbs(orb_canvas, alpha=0.90)   # fade the trail a little each frame
        display = cv2.convertScaleAbs(frame, alpha=0.4)            # dim the camera so the orbs pop

        labels = []
        for i, hand in enumerate(hands):
            palm = hand.landmarks[[0, 5, 9, 13, 17]]
            x = float(palm[:, 0].mean())
            y = float(palm[:, 1].mean())
            orb_point = (int(x * w), int(y * h))

            # Ask the real instrument which note this hand position plays.
            if i not in instruments:
                instruments[i] = Instrument(FakeSynth())
            fake_hand = HandState(x=x, y=y, openness=1.0)
            info = instruments[i].update({"left": None, "right": fake_hand}, 0.016)
            note = info["lead_name"]           # e.g. "A4"
            colour_key = pitch_class(note)     # e.g. "A"

            orb_canvas = draw_glowing_orb(orb_canvas, orb_point, colour_key)
            artwork = draw_glowing_orb(artwork, orb_point, colour_key, intensity=0.15)
            labels.append((orb_point, f"{hand.label} {note}"))

        output = cv2.add(display, orb_canvas)
        for (px, py), text in labels:
            cv2.putText(output, text, (px + 20, py), cv2.FONT_HERSHEY_SIMPLEX,
                        0.6, (255, 255, 255), 1, cv2.LINE_AA)

        cv2.imshow("Visuals Test", output)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            cv2.imwrite("orb_artwork.png", artwork)
            print("Saved orb_artwork.png")
        elif key == ord("c"):
            orb_canvas[:] = 0
            artwork[:] = 0
            print("Cleared")
        elif key == ord("q"):
            break

finally:
    tracker.close()
    cv2.destroyAllWindows()
