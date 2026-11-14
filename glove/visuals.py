"""Everything drawn on the OpenCV window. (Owner: D)

Theme is "Composition" (art + music + tech), so this is not just a debug overlay. It is half the score.
Draw on the mirrored camera frame that tracker.read() returns. Landmarks are 0..1; multiply by frame size.

Layers, in order
 X 1. dim the camera image (frame * 0.4) so the graphics pop
 2. note lanes: vertical bands showing the pitch zones, active one lit (Play mode)
 X 3. skeleton: 21 landmarks + bone lines; colour by hand (left = cyan, right = magenta)
 4. palm orb: radius from depth, hue from the current note (midi % 12), ring fills with pinch
 5. trails: separate persistent canvas that fades each frame (canvas *= 0.94), add with cv2.addWeighted
 6. event bursts: expanding rings where plucks / drum hits happen
 7. HUD: mode, note name, chord name; debug panel (key D) printing raw HandState values
 8. "score" canvas: dots accumulate and NEVER fade; press S to save it as a PNG = the performance as artwork
             
Tips: cv2.GaussianBlur on a copy of the overlay, then add it back = cheap glow. Use cv2.LINE_AA.

TODO: class Visuals: draw(frame, hands, info, dt) -> frame, save_score(path)
"""

import cv2
import numpy as np
from tracker import HandTracker
from music import degree_to_midi, midi_to_name

skeleton_pairs = [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),
             (9,13),(13,14),(14,15),(15,16),(13,17),(0,17),(17,18),(18,19),(19,20)]

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

def get_points(frame, landmarks):
    height, width, _ = frame.shape
    points = []
    for x, y in landmarks:
        points.append((int(x * width), int(y * height)))
    return points

def draw_hand_skeleton(frame, points, current_note):
    if len(points) == 0:
        return frame
    colour = note_colours.get(current_note, (120,120,120))

    for start_idx, end_idx in skeleton_pairs:
        cv2.line(frame, points[start_idx], points[end_idx], colour, 2)
    
    for pt in points:
        cv2.circle(frame, pt, 5, colour, -1)
        cv2.circle(frame, pt, 2, (255, 255, 255), -1)

    return frame

def draw_glowing_orb(frame, orb_point, current_note):

    orb_colour = note_colours[current_note]

    glow_layer = np.zeros_like(frame)
    cv2.circle(glow_layer, orb_point, 45, orb_colour, -1)
    glow_layer = cv2.GaussianBlur(glow_layer, (91, 91), 0)

    frame = cv2.add(frame, glow_layer)
    cv2.circle(frame, orb_point, 12, orb_colour, -1)
    cv2.circle(frame, orb_point, 6, (255, 255, 255), -1)

    return frame

if __name__ == "__main__":
    tracker = HandTracker()
    orb_canvas = None

    try:
        while True:
            frame, hands = tracker.read()
            if frame is None:
                continue

            if orb_canvas is None:
                orb_canvas = np.zeros_like(frame)

            display_frame = cv2.convertScaleAbs(frame, alpha=0.4, beta=0)

            for hand, degree in hands:
                side = hand.label
                points = get_points(display_frame, hand.landmarks)

                current_note = midi_to_name(degree_to_midi(degree))
                # Get orb point ... orb_point = 

                display_frame = draw_glowing_orb(display_frame, points, current_note)
                orb_canvas = draw_glowing_orb(orb_canvas, orb_point, current_note)
                display_frame = draw_hand_skeleton(display_frame, points, current_note)

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