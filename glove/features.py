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

ACTUAL DICT:
            {'palm_centre': (x, y),
            'cam_distance': int,
            'roll': int (degrees),
            'curl': arr[4] int (0-1),
            'thumb_open': int (0-1),
            'openness': int (0-1),
            'fingers_up': arr[4] int ,
            'pinch': int (0-1)}


TODO:
- def extract_features(landmarks, world, label, aspect) -> dict with the fields above
- (optional) palm normal from world landmarks, finger spread, thumb-to-each-fingertip pinches
"""

import numpy as np

def dist(a, b):
    return float(np.linalg.norm(a - b))

def clamp01(x):
    return float(np.clip(x, 0.0, 1.0))

def extract_features(landmarks, world, label, aspect):
    palm_points = landmarks[[0, 5, 9, 13, 17]]      # shape (5, 3): five rows, x/y/z each
    palm_centre = palm_points[:, :2].mean(axis=0)         # shape (2,): the mean x and the mean y

    wrist = landmarks[0, :2]       # x, y only
    knuckle = landmarks[9, :2]
    diff = (knuckle - wrist) * np.array([aspect, 1.0])   # scale x only
    cam_dist = float(np.linalg.norm(diff))

    dx, dy = diff
    roll = np.arctan2(dx, -dy)

    wrist = world[0]
    FINGERS = [(8, 5), (12, 9), (16, 13), (20, 17)]
    THUMB_OPEN_THRESHOLD = 0.88
    FINGER_OPEN_THRESHOLD = 0.54
    curl = []

    palm_length = dist(world[9], world[0])
    for finger in FINGERS:
        ratio = dist(world[finger[0]], wrist) / dist(world[finger[1]], wrist)
        curl.append(1 - clamp01((ratio - 0.78) / (1.65 - 0.78)))
    thumb_ratio = (dist(world[4], world[17])) / palm_length
    thumb_open = thumb_ratio > THUMB_OPEN_THRESHOLD
    openness = 1 - np.mean(curl)
    fingers_up = []
    for c in curl:
        fingers_up.append(c < FINGER_OPEN_THRESHOLD)
    fingers_up = tuple([thumb_open] + fingers_up)

    pinch_ratio = dist(world[4], world[8]) / palm_length
    pinch = 1 - clamp01((pinch_ratio - 0.3) / (0.68 - 0.3))

    return {'palm_centre': palm_centre,
            'cam_distance': cam_dist,
            'roll': np.degrees(roll),
            'curl': curl,
            'thumb_open': thumb_open,
            'openness': openness,
            'fingers_up': fingers_up,
            'pinch': pinch}
