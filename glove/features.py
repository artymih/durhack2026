"""One hand, one frame: raw landmarks -> musically useful numbers. Pure functions, no state. (Owner: A)

Landmark indices: 0 wrist | thumb 1-4 | index 5-8 | middle 9-12 | ring 13-16 | pinky 17-20
(5, 9, 13, 17 are the knuckles / "MCP"; 4, 8, 12, 16, 20 are the fingertips.)

Formulas to start from (estimates, TUNE them on a real hand with the debug HUD):
- palm centre (x, y):  mean of landmarks 0, 5, 9, 13, 17      (steady even when fingers move)
- size / depth proxy:  |wrist -> middle knuckle| in the image, x scaled by width/height.
                       Bigger = closer. MediaPipe's z is NOT distance from the camera, don't use it.
- roll (hand tilt):    atan2(dx, -dy) of wrist -> middle knuckle. 0 = fingers up, + = clockwise on screen.
- curl per finger:     ratio = |tip - wrist| / |knuckle - wrist| using WORLD landmarks (rotation invariant).
                       curl = 1 - clamp((ratio - 1.05) / (1.85 - 1.05)).  0 = straight, 1 = fist.
- thumb open:          |thumb tip - pinky knuckle| / palm_length, roughly 0.6 (tucked) to 1.3 (out).
- openness:            1 - mean(curl of index..pinky)
- fingers:             count of fingers with curl < 0.35, plus the thumb if open.
- pinch:               1 - clamp((|thumb tip - index tip| / palm_length - 0.15) / 0.65).  1 = touching.
- twist (palm vs back): sign of the 2D cross product wrist->index knuckle x wrist->pinky knuckle,
                       flipped for the Left hand. Check the sign on a real hand; it may be backwards.

TODO:
- def extract_features(landmarks, world, label, aspect) -> dict with the fields above
- (optional) palm normal from world landmarks, finger spread, thumb-to-each-fingertip pinches
"""
