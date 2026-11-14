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
#from tracker import frames etc

#maybe define hands_data depending on input from megan
#This code hinges on getting an input of frame, landmarks, label from megan's code, and getting a current_note from amelkas code

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

def draw_hand_skeleton(frame, landmarks, label, current_note):
    colour = note_colours.get(current_note)
    if not landmarks:
        return frame
    height, width, _ = frame.shape
    colour = hand_colours.get(label, (0,255,0))
    points = []
    for x,y in landmarks:
        if 0.0 <= x <= 1.0 and 0.0 <= y <= 1.0:
            points.append((int(x * width), int(y * height)))
        else:
            points.append((int(x), int(y)))

    for start_idx, end_idx in skeleton_pairs:
        cv2.line(frame, points[start_idx], points[end_idx], colour, 2)
    
    for pt in points:
        cv2.circle(frame, pt, 5, colour, -1)
        cv2.circle(frame, pt, 2, (255, 255, 255), -1)

    return frame
    

for frame, hands_data in '''[function name from megans code]''' :
    display_frame = cv2.convertScaleAbs(frame, alpha=0.4, beta=0)
    
    for hand in hands_data:
        # SOME WAY TO GET CURRENT NOTE FROM AMELKAS CODE
        side = hand["label"]            
        points = hand["landmarks"]
        display_frame = draw_hand_skeleton(display_frame, points, side, current_note)
    cv2.imshow("Hand Skeleton Tracker", display_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()