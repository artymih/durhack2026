"""Everything drawn on the OpenCV window. (Owner: D)

Theme is "Composition" (art + music + tech), so this is not just a debug overlay. It is half the score.
Draw on the mirrored camera frame that tracker.read() returns. Landmarks are 0..1; multiply by frame size.

Layers, in order
 1. dim the camera image (frame * 0.4) so the graphics pop
 2. note lanes: vertical bands showing the pitch zones, active one lit (Play mode)
 3. skeleton: 21 landmarks + bone lines; colour by hand (left = cyan, right = magenta)
 4. palm orb: radius from depth, hue from the current note (midi % 12), ring fills with pinch
 5. trails: separate persistent canvas that fades each frame (canvas *= 0.94), add with cv2.addWeighted
 6. event bursts: expanding rings where plucks / drum hits happen
 7. HUD: mode, note name, chord name; debug panel (key D) printing raw HandState values
 8. "score" canvas: dots accumulate and NEVER fade; press S to save it as a PNG = the performance as artwork

Bone pairs: [(0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),(5,9),(9,10),(10,11),(11,12),
             (9,13),(13,14),(14,15),(15,16),(13,17),(0,17),(17,18),(18,19),(19,20)]

Tips: cv2.GaussianBlur on a copy of the overlay, then add it back = cheap glow. Use cv2.LINE_AA.

TODO: class Visuals: draw(frame, hands, info, dt) -> frame, save_score(path)
"""

import cv2

Webcam = cv2.VideoCapture(0)

if not Webcam.isOpened():
    print("Could not access webcam.")

ret, frame = Webcam.read()

if ret:
    cv2.imshow("Captured Frame", frame)
    cv2.waitKey(0)
    cv2.destoryAllWindows()
else:
    print("Could not capture frame.")

Webcam.release()