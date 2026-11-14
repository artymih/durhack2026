"""Entry point.  python run.py          (camera)
                python run.py --mouse   (fake right hand from the mouse, so sound/mapping/visuals work without tracking)
Owner: D, but everyone touches it.

Main loop, once per camera frame:
    frame, raw = tracker.read()                 # glove/tracker.py   (A)
    hands = hands_model.update(raw, now)        # glove/hands.py     (A)
    info = instrument.update(hands, dt)         # glove/instrument.py (C) -> calls synth.* (B)
    out = visuals.draw(frame, hands, info, dt)  # glove/visuals.py   (D)
    cv2.imshow("AirGlove", out)

Keys to wire up: Esc quit | M mode | Q quantize | K transpose up | D debug HUD | S save artwork | Space panic mute

TODO:
- argparse (--mouse, --camera N)
- MouseHands: cv2.setMouseCallback -> a fake HandState (x, y from mouse, wheel = depth, click = gate)
- the loop above
- always release the camera and stop the synth in a finally block
"""

if __name__ == "__main__":
    raise SystemExit("TODO: build the main loop (see the docstring)")
