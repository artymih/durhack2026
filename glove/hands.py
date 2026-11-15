from dataclasses import dataclass, field
import numpy as np
from glove.smoothing import OneEuro, Stable

STABLE_FRAMES = 4      # about 0.13 s at 30 fps; later: config.py
FILTER_SETTINGS = dict(min_cutoff=0.3, beta=5.0)     # later: move to config.py for C
SMOOTHED = ("x", "y", "cam_distance", "roll", "openness", "pinch")


@dataclass
class HandState:
    x: float = 0.5            # palm centre, 0..1, left->right as the USER SEES the mirrored screen
    y: float = 0.5            # 0 = top, 1 = bottom
    palm: tuple[float, float] = (0.5, 0.5)
    depth: float = 0.5        # 0 = far from camera, 1 = near (from hand size, auto-ranged)
    roll: float = 0.0         # radians, hand tilt. 0 = fingers up, + = clockwise
    twist: float = 0.0        # NOT PRESENT IN v1
    openness: float = 1.0     # 0 = fist, 1 = open hand
    thumb: bool = True        # True = up, False = down
    index: bool = True
    middle: bool = True
    ring: bool = True
    pinky: bool = True
    # fingers_up: tuple[bool, bool, bool, bool, bool] = (False,) * 5 NOW REMOVED
    pinch: float = 0.0        # 0..1, thumb to index tip
    vx: float = 0.0           # velocity, frame-heights per second
    vy: float = 0.0           # + = moving down
    strike: bool = False      # True for exactly ONE frame when a downward flick is detected
    strike_vel: float = 0.0   # 0..1 strength of that strike
    held: bool = False        # True if tracking dropped out and we're coasting on the last value
    landmarks: list = field(default_factory=list)  # 21 (x, y) points in 0..1, for drawing




import numpy as np
from dataclasses import replace
from glove.features import extract_features   # or: from glove.features import extract_features

SIZE_FAR = 0.8
SIZE_NEAR = 0.1
HOLD_SEC = 0.05      # how long to keep reporting a hand after tracking drops out


def clamp01(v):
    return float(np.clip(v, 0.0, 1.0))


class HandsModel:
    def __init__(self, cfg=None, aspect=4 / 3):
        self.aspect = aspect
        self.last_pos = {"left": None, "right": None}     # used by assign_roles
        self.last_state = {"left": None, "right": None}   # last HandState per role
        self.last_seen = {"left": 0.0, "right": 0.0}      # time each role was last really seen
        self.filters = {role: self._new_filters() for role in ("left", "right")}
        self.stable = {role: self._new_stable() for role in ("left", "right")}

    def _new_filters(self):
        return {name: OneEuro(**FILTER_SETTINGS) for name in SMOOTHED}

    def _new_stable(self):
        return [Stable(STABLE_FRAMES) for _ in range(5)]    # thumb, index, middle, ring, pinky

    def assign_roles(self, positions, labels, scores):
        roles = {}

        # each hand claims the role named by its label; if two hands claim the same one,
        # the more confident detection keeps it
        for i, label in enumerate(labels):
            role = label.lower()
            if role not in roles or scores[i] > scores[roles[role]]:
                roles[role] = i

        # two hands but both labelled the same: the other hand must be the opposite role
        if len(labels) >= 2 and len(roles) == 1:
            (role, kept), = roles.items()
            other = 1 - kept if len(labels) == 2 else None
            if other is not None:
                roles["left" if role == "right" else "right"] = other

        for role, i in roles.items():
            self.last_pos[role] = positions[i]
        return roles

    # def assign_roles(self, positions, labels):
    #         # positions: list of (x, y), one per hand
    #         # labels: list of "Left"/"Right", one per hand
    #         # return: dict like {"left": 0, "right": 1} (indexes into the lists)
    
    #         if len(positions) == 0:
    #             return {}
    
    #         if len(positions) >= 2:
    #             # two hands: smaller x (further left on screen) is "left"
    #             order = sorted(range(len(positions)), key=lambda i: positions[i][0])
    #             roles = {"left": order[0], "right": order[1]}
    #         else:
    #             x, y = positions[0]
    #             known = {r: p for r, p in self.last_pos.items() if p is not None}
    
    #             if len(known) == 2:
    #                 # both roles remembered: pick the closer one
    #                 role = min(known, key=lambda r: np.hypot(x - known[r][0], y - known[r][1]))
    #             elif len(known) == 1:
    #                 # one role remembered: if the hand is near it, same role; if far, it's the other one
    #                 (r, p), = known.items()
    #                 near = np.hypot(x - p[0], y - p[1]) < 0.25
    #                 role = r if near else ("left" if r == "right" else "right")
    #             else:
    #                 # no memory at all: fall back to the tracker's label
    #                 role = labels[0].lower()
    
    #             roles = {role: 0}
    
    #         # remember where each role is now (after all decisions are made)
    #         for role, i in roles.items():
    #             self.last_pos[role] = positions[i]
    #         return roles

    def update(self, raw_hands, t):
        all_feats = [extract_features(r.landmarks, r.world, r.label, self.aspect)
                     for r in raw_hands]
        positions = [f["palm_centre"] for f in all_feats]
        labels = [r.label for r in raw_hands]
        scores = [r.score for r in raw_hands]
        roles = self.assign_roles(positions, labels, scores)

        out = {}
        for role in ("left", "right"):
            if role in roles:
                i = roles[role]
                state = self._make_state(raw_hands[i], all_feats[i], role, t)
                self.last_state[role] = state     # after _make_state, which reads the old one
                self.last_seen[role] = t
                out[role] = state
            else:
                out[role] = self._held_or_none(role, t)
        return out

    def _make_state(self, raw, feats, role, t):
        # velocity: compare with this role's previous state
        # prev = self.last_state[role]
        # dt = t - self.last_seen[role]
        # x = float(feats["palm_centre"][0])
        # y = float(feats["palm_centre"][1])
        # if prev is not None and 0 < dt < 0.5:
        #     vx = (x - prev.x) / dt
        #     vy = (y - prev.y) / dt
        # else:
        #     vx = vy = 0.0
        f = self.filters[role]
        x = f["x"](float(feats["palm_centre"][0]), t)
        y = f["y"](float(feats["palm_centre"][1]), t)
        depth = f["cam_distance"](feats["cam_distance"], t)
        roll = f["roll"](feats["roll"], t)
        openness = f["openness"](float(feats["openness"]), t)
        pinch = f["pinch"](float(feats["pinch"]), t)
        vx = f["x"].velocity
        vy = f["y"].velocity
        fingers_up = tuple(s(bool(v)) for s, v in zip(self.stable[role], feats["fingers_up"]))

        return HandState(
            x=x,
            y=y,
            palm=feats["palm_centre"],
            depth=clamp01((depth - SIZE_FAR) / (SIZE_NEAR - SIZE_FAR)),
            roll=roll,
            openness=openness,
            thumb=fingers_up[0],
            index=fingers_up[1],
            middle=fingers_up[2],
            ring=fingers_up[3],
            pinky=fingers_up[4],
            pinch=pinch,
            vx=vx,
            vy=vy,
            strike=False,
            strike_vel=0.0,
            held=False,
            landmarks=raw.landmarks[:, :2].tolist()
        )

    def _held_or_none(self, role, t):
        state = self.last_state[role]
        if state is None:
            return None
        if t - self.last_seen[role] > HOLD_SEC:
            self.last_state[role] = None
            self.last_pos[role] = None      # forget it so it can't claim a new hand
            self.filters[role] = self._new_filters()   # fresh smoothing, so a returning hand doesn't glide in
            self.stable[role] = self._new_stable()
            return None
        return replace(state, held=True, strike=False)
