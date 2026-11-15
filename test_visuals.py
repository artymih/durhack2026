import argparse
import importlib.util
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from glove.config import CONFIG
from glove.hands import HandsModel
from glove.instrument import Instrument
from glove.music import midi_to_name
from glove.tracker import HandTracker

GREY = (120, 120, 120)


class NullSynth:

    def set_lead(self, **kwargs):
        pass

    def set_pad(self, **kwargs):
        pass


def find_target():
    here = Path(__file__).resolve().parent
    candidates = list(here.glob("*.py")) + list(here.glob("*/*.py"))

    for path in sorted(candidates):
        if path.resolve() == Path(__file__).resolve():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if "def draw_orb" in text:
            return path

    return None


def load_module(path):
    spec = importlib.util.spec_from_file_location("orb_module", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pitch_class(name):
    return name.rstrip("0123456789-")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?")
    parser.add_argument("--audio", action="store_true")
    args = parser.parse_args()

    target = Path(args.target) if args.target else find_target()

    if target is None or not target.is_file():
        print("Could not find the orb tracker file. Pass its path as an argument.")
        sys.exit(1)

    orb = load_module(target)

    if args.audio:
        from glove.synth import Synth
        synth = Synth()
        synth.start()
    else:
        synth = NullSynth()

    tracker = HandTracker()
    hands_model = HandsModel()
    instrument = Instrument(synth)

    root_note = pitch_class(midi_to_name(CONFIG["music"]["root_midi"]))

    displayed_orbs = None
    permanent_orbs = None
    previous_time = time.monotonic()

    try:
        while True:
            frame, raw_hands = tracker.read()
            if frame is None:
                continue

            now = time.monotonic()
            dt = now - previous_time
            previous_time = now

            height, width, _ = frame.shape
            hands_model.aspect = width / height

            hands = hands_model.update(raw_hands, now)
            info = instrument.update(hands, dt)

            if displayed_orbs is None:
                displayed_orbs = np.zeros_like(frame)
            if permanent_orbs is None:
                permanent_orbs = np.zeros_like(frame)

            displayed_orbs = cv2.convertScaleAbs(displayed_orbs, alpha=0.90)
            display_frame = cv2.convertScaleAbs(frame, alpha=0.4, beta=0)

            lead_name = info["lead_name"]
            lead_note = pitch_class(lead_name) if lead_name else None
            chord_label = info["chord_name"] or "none"

            orbs = (
                (hands.get("right"), lead_note),
                (hands.get("left"), root_note),
            )

            for hand, note in orbs:
                if hand is None or note is None:
                    continue
                orb_center = (int(hand.x * width), int(hand.y * height))
                displayed_orbs = orb.draw_orb(displayed_orbs, orb_center, note)
                permanent_orbs = orb.draw_orb(permanent_orbs, orb_center, note)

            display_frame = cv2.add(display_frame, displayed_orbs)

            note_colour = orb.note_colours.get(lead_note, GREY)
            final_display = orb.add_border(
                display_frame,
                lead_name or "None",
                f"{chord_label} - {info['scale']}",
                note_colour,
            )

            cv2.imshow("Hand Orb Demo", final_display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord("s"):
                cv2.imwrite("orb_artwork.png", permanent_orbs)
                print("Saved orb_artwork.png")
            elif key == ord("c"):
                displayed_orbs = np.zeros_like(frame)
            elif key == ord("q") or key == 27:
                break
    finally:
        if permanent_orbs is not None:
            cv2.imwrite("orb_artwork.png", permanent_orbs)
            print("Final artwork saved to orb_artwork.png")
        tracker.close()
        if args.audio:
            synth.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
