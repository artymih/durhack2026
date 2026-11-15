import numpy as np
from glove.config import CONFIG

THUMB_OPEN_THRESHOLD = CONFIG["thumb_open_threshold"]
FINGER_OPEN_THRESHOLD = CONFIG["finger_open_threshold"]
PINCH_APART = CONFIG["pinch_apart"]
PINCH_TOUCH = CONFIG["pinch_touch"]
CURL_STRAIGHT = CONFIG["curl_straight"]
CURL_FIST = CONFIG["curl_fist"]



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
    curl = []

    palm_length = dist(world[9], world[0])
    for finger in FINGERS:
        ratio = dist(world[finger[0]], wrist) / dist(world[finger[1]], wrist)
        curl.append(1 - clamp01((ratio - CURL_FIST) / (CURL_STRAIGHT - CURL_FIST)))
    thumb_ratio = (dist(world[4], world[17])) / palm_length
    thumb_open = thumb_ratio > THUMB_OPEN_THRESHOLD
    openness = 1 - np.mean(curl)
    fingers_up = []
    for c in curl:
        fingers_up.append(c < FINGER_OPEN_THRESHOLD)
    fingers_up = tuple([thumb_open] + fingers_up)

    pinch_ratio = dist(world[4], world[8]) / palm_length
    pinch = 1 - clamp01((pinch_ratio - PINCH_TOUCH) / (PINCH_APART - PINCH_TOUCH))

    return {'palm_centre': palm_centre,
            'cam_distance': cam_dist,
            'roll': np.degrees(roll),
            'curl': curl,
            'thumb_open': thumb_open,
            'openness': openness,
            'fingers_up': fingers_up,
            'pinch': pinch}
