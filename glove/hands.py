"""Turns raw per-frame detections into smooth, stable left/right hand states. (Owner: A)

THIS FILE'S HandState IS THE CONTRACT between vision (A) and everyone else. Don't rename fields
without telling the team. Until A's tracking works, run.py --mouse fakes a right hand.
"""
from dataclasses import dataclass, field


@dataclass
class HandState:
    x: float = 0.5            # palm centre, 0..1, left->right as the USER SEES the mirrored screen
    y: float = 0.5            # 0 = top, 1 = bottom
    depth: float = 0.5        # 0 = far from camera, 1 = near (from hand size, auto-ranged)
    roll: float = 0.0         # radians, hand tilt. 0 = fingers up, + = clockwise
    twist: float = 0.0        # -1..1, + = palm toward camera, - = back of hand
    openness: float = 1.0     # 0 = fist, 1 = open hand
    fingers: int = 5          # stable finger count 0..5
    pinch: float = 0.0        # 0..1, thumb to index tip
    vx: float = 0.0           # velocity, frame-heights per second
    vy: float = 0.0           # + = moving down
    strike: bool = False      # True for exactly ONE frame when a downward flick is detected
    strike_vel: float = 0.0   # 0..1 strength of that strike
    held: bool = False        # True if tracking dropped out and we're coasting on the last value
    landmarks: list = field(default_factory=list)  # 21 (x, y) points in 0..1, for drawing


# TODO: class HandsModel:
#   __init__(cfg, aspect)
#   update(raw_hands, t_seconds) -> {"left": HandState | None, "right": HandState | None}
#
# Steps inside update():
#   1. features.extract_features() for each raw hand
#   2. roles: with 2 hands the leftmost on screen is "left"; with 1 hand keep the role whose last
#      position is closest (fall back to MediaPipe's label). Don't trust the label alone, it flickers.
#   3. smooth with OneEuro (x, y, size, roll, twist, curl, pinch); finger count through Stable
#   4. depth = AutoRange over smoothed hand size
#   5. velocity = OneEuro .velocity of x and y
#   6. strike: when vy crosses min_down_speed, wait for the velocity peak (or ~60 ms), emit ONE event,
#      then re-arm only after vy falls below ~40% of the threshold. Add a 150 ms refractory period.
#   7. if a hand vanishes, keep its last state with held=True for hold_sec, then return None
