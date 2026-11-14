import cv2
import numpy as np
from glove.hands import HandState
from glove.music import degree_to_midi, midi_to_name

note_colours = {
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
    "B":  (255, 0, 255)
}

def draw_glowing_orb(frame, orb_point, current_note, intensity=1.0):
    orb_colour = note_colours.get(current_note, (120, 120, 120))

    glow_layer = np.zeros_like(frame)
    cv2.circle(glow_layer, orb_point, 30, orb_colour, -1)
    glow_layer = cv2.GaussianBlur(glow_layer, (51, 51), 0)

    glow_layer = cv2.convertScaleAbs(glow_layer, alpha=intensity, beta=0)
    frame = cv2.add(frame, glow_layer)
    cv2.circle(frame, orb_point, 6, orb_colour, -1)

    return frame

if __name__ == "__main__":
    tracker = HandState()
    orb_canvas = None
    artwork_canvas = None

    try:
        while True:
            frame, hands = tracker.read()
            if frame is None:
                continue

            if orb_canvas is None:
                orb_canvas = np.zeros_like(frame)
            if artwork_canvas is None:
                artwork_canvas = np.zeros_like(frame)

            orb_canvas = cv2.multiply(orb_canvas, 0.90)

            display_frame = cv2.convertScaleAbs(frame, alpha=0.4, beta=0)
            height, width, _ = frame.shape
            for hand, degree in hands:
                current_note = midi_to_name(degree_to_midi(degree))
                
                palm_pts = hand.palm
                if len(palm_pts) > 0:
                    avg_x = sum(pt[0] for pt in palm_pts) / len(palm_pts)
                    avg_y = sum(pt[1] for pt in palm_pts) / len(palm_pts)
                    orb_point = (int(avg_x * width), int(avg_y * height))

                orb_canvas = draw_glowing_orb(orb_canvas, orb_point, current_note)
                artwork_canvas = draw_glowing_orb(artwork_canvas, orb_point, current_note)
            display_frame = cv2.add(display_frame, orb_canvas)
           
            cv2.imshow("Hand Orb Tracker", display_frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                cv2.imwrite("orb_artwork.png", orb_canvas)
                print("Saved orb_artwork.png!")
            elif key == ord('c'):
                orb_canvas = np.zeros_like(frame)
            elif key == ord('q'):
                break
    finally:
        if orb_canvas is not None:
            cv2.imwrite("orb_artwork.png", orb_canvas)
            print("Final artwork saved to orb_artwork.png")
        tracker.close()
        cv2.destroyAllWindows()