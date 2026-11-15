import cv2
import numpy as np
from glove.hands import HandState
from glove.music import degree_to_midi, midi_to_name

note_colours = {
    "C":  (250, 59, 59),
    "C#": (250, 148, 59),
    "D":  (250, 240, 59),
    "D#": (160, 250, 51),
    "E":  (61, 250, 51),
    "F":  (68, 241, 149),
    "F#": (68, 241, 241),
    "G":  (68, 149, 241),
    "G#": (61, 51, 250),
    "A":  (160, 51, 250),
    "A#": (250, 59, 240),
    "B":  (250, 59, 151)
}

def draw_orb(frame, orb_center, current_note, intensity=1.0):
    orb_colour = note_colours.get(current_note, (120, 120, 120))

    glow = np.zeros_like(frame)
    cv2.circle(glow, orb_center, 30, orb_colour, -1)
    glow = cv2.GaussianBlur(glow, (51, 51), 0)

    glow = cv2.convertScaleAbs(glow, alpha=intensity, beta=0)
    frame = cv2.add(frame, glow)
    cv2.circle(frame, orb_center, 6, orb_colour, -1)

    return frame

def add_border(frame, current_note, chord_name, note_colour):
    top, bottom, left, right = 60, 50, 20, 20
    border_bg = (25, 25, 25)
    framed = cv2.copyMakeBorder(frame, top, bottom, left, right, cv2.BORDER_CONSTANT, value=border_bg)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(
        framed, current_note, (left, 40), font, 0.9, note_colour, 2, cv2.LINE_AA
    )
    height, width, _ = frame.shape
    cv2.rectangle(framed, (left, top), (left + width, top + height), note_colour, 2)
    cv2.putText(
        framed,
        chord_name.upper(),
        (left + 220, 40),
        font,
        0.9,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )
    controls = "[S] Save Artwork   |   [C] Clear Trails   |   [Q] Quit"
    cv2.putText(
        framed,
        controls,
        (left, top + height + 33),
        font,
        0.55,
        (180, 180, 180),
        1,
        cv2.LINE_AA,
    )

    return framed


if __name__ == "__main__":
    tracker = HandState()
    displayed_orbs = None
    permanent_orbs = None
    current_note = "None"
    chord_name = "None"
    note_colour = (120, 120, 120)

    try:
        while True:
            frame, hands = tracker.read()
            if frame is None:
                continue
            if displayed_orbs is None:
                displayed_orbs = np.zeros_like(frame)
            if permanent_orbs is None:
                permanent_orbs = np.zeros_like(frame)

            displayed_orbs = cv2.convertScaleAbs(displayed_orbs, alpha=0.90)

            display_frame = cv2.convertScaleAbs(frame, alpha=0.4, beta=0)
            height, width, _ = frame.shape
            for hand, degree in hands:
                current_note = midi_to_name(degree_to_midi(degree))
                note_colour = note_colours.get(current_note, (120, 120, 120))

                if hand.label == "Left":
                    if hand.roll < -60:
                        chord_name = "power"
                    elif hand.roll < -20:
                        chord_name = "sus2"
                    elif hand.roll < 20:
                        chord_name = "triad"
                    elif hand.roll < 60:
                        chord_name = "add7"
                    else:
                        chord_name = "add9"
                
                palm_pts = hand.palm
                if len(palm_pts) > 0:
                    avg_x = sum(pt[0] for pt in palm_pts) / len(palm_pts)
                    avg_y = sum(pt[1] for pt in palm_pts) / len(palm_pts)
                    orb_center = (int(avg_x * width), int(avg_y * height))

                    displayed_orbs = draw_orb(displayed_orbs, orb_center, current_note)
                    permanent_orbs = draw_orb(permanent_orbs, orb_center, current_note)
            
            display_frame = cv2.add(display_frame, displayed_orbs)

            final_display = add_border(
                display_frame, current_note, chord_name, (note_colour)
            )
           
            cv2.imshow("Hand Orb Tracker", final_display)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                cv2.imwrite("orb_artwork.png", permanent_orbs)
                print("Saved orb_artwork.png")
            elif key == ord('c'):
                displayed_orbs = np.zeros_like(frame)
            elif key == ord('q'):
                break
    finally:
        if displayed_orbs is not None:
            cv2.imwrite("orb_artwork.png", permanent_orbs)
            print("Final artwork saved to orb_artwork.png")
        tracker.close()
        cv2.destroyAllWindows()