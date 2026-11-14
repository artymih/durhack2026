"""Camera + MediaPipe hand tracking. (Owner: A)

Job: grab a frame, mirror it, run the hand model, return raw landmarks. Nothing musical in here.

Gotchas (checked against mediapipe 1.2.3):
- mp.solutions is GONE. Use the Tasks API:
      import mediapipe as mp
      from mediapipe.tasks.python import vision, BaseOptions
      opts = vision.HandLandmarkerOptions(
          base_options=BaseOptions(model_asset_path="models/hand_landmarker.task"),
          running_mode=vision.RunningMode.VIDEO, num_hands=2)
      landmarker = vision.HandLandmarker.create_from_options(opts)
      img = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
      result = landmarker.detect_for_video(img, timestamp_ms)   # timestamps must strictly increase
      result.hand_landmarks        # per hand: 21 x (x, y, z) normalised to the image
      result.hand_world_landmarks  # per hand: 21 x metres (best for finger bends / pinch)
      result.handedness            # per hand: [Category(category_name='Left'|'Right', score)]
- The model file is NOT bundled: run `python scripts/download_model.py` first.
- cv2.flip(frame, 1) BEFORE detection, so MediaPipe's Left/Right matches the user's real hands
  and x=0 is the left of what the user sees on screen.
- Windows: cv2.VideoCapture(0, cv2.CAP_DSHOW) opens much faster than the default backend.
- cv2 gives BGR; MediaPipe wants RGB (cv2.cvtColor).

TODO:
- RawHand dataclass: landmarks (21x3 ndarray), world (21x3 ndarray), label ('Left'|'Right'), score
- class HandTracker: __init__(cfg), read() -> (mirrored BGR frame, [RawHand]), close()
"""

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
import time
from dataclasses import dataclass
import numpy as np
from pathlib import Path

@dataclass
class RawHand:
    landmarks: np.ndarray   # (21, 3)
    world: np.ndarray       # (21, 3)
    label: str              # 'Left' or 'Right'
    score: float

class HandTracker:
    def __init__(self):
        options = vision.HandLandmarkerOptions(
          base_options=BaseOptions(model_asset_path="models/hand_landmarker.task"),
          running_mode=vision.RunningMode.VIDEO,
          num_hands=2,
          )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

        # cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)   # 0 = first camera, DSHOW = faster on Windows
        self.cap = cv2.VideoCapture(0)
        self.start = time.monotonic()
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        self.SWAP_HANDEDNESS = True

    def read(self):
      ok, frame = self.cap.read()                 # grab one image
      if not ok or frame is None:
          return None, []
      
      frame = cv2.flip(frame, 1)
      rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
      image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

      timestamp_ms = int((time.monotonic() - self.start) * 1000)
      result = self.landmarker.detect_for_video(image, timestamp_ms)

      hands = []
      for lms, world, handed in zip(result.hand_landmarks,
                                    result.hand_world_landmarks,
                                    result.handedness):
          label = handed[0].category_name
          if self.SWAP_HANDEDNESS:
              label = "Left" if label == "Right" else "Right"
          hands.append(RawHand(
              landmarks=np.array([[p.x, p.y, p.z] for p in lms], dtype=np.float32),   # 21x3 array from lms
              world=np.array([[p.x, p.y, p.z] for p in world], dtype=np.float32),     # 21x3 array from world
              label=label,
              score=handed[0].score,
          ))
      return frame, hands

      # h, w = frame.shape[:2]
      # for i, hand in enumerate(result.hand_landmarks):
      #     label = result.handedness[i][0].category_name
      #     if self.SWAP_HANDEDNESS:
      #       label = "Left" if label == "Right" else "Right"
      #     cv2.putText(frame, label, (int(hand[0].x * w), int(hand[0].y * h)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
      #     for lm in hand:
      #       px = int(lm.x * w)
      #       py = int(lm.y * h)
      #       cv2.circle(frame, (px, py), 4, (0, 255, 0), -1)
      
      # if cv2.waitKey(1) & 0xFF == ord("q"):  # quit when you press q
      #     self.close()

      # cv2.imshow("camera", frame)

    def close(self):
        self.cap.release()
        # cv2.destroyAllWindows()
        self.landmarker.close()

if __name__ == "__main__":
    if not Path("models/hand_landmarker.task").exists():
      raise FileNotFoundError("Mate you gotta run this command: python scripts/download_model.py")

    tracker = HandTracker()
    while True:
        frame, hands = tracker.read()
        if frame is None:
            continue
        h, w = frame.shape[:2]
        for hand in hands:
            for x, y, z in hand.landmarks:
                px = int(x * w)
                py = int(y * h)
                cv2.circle(frame, (px, py), 4, (0, 255, 0), -1)
                wx = int(hand.landmarks[0][0] * w)
                wy = int(hand.landmarks[0][1] * h)
                cv2.putText(frame, hand.label, (wx, wy), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
      #     for lm in hand:
            # draw the dots, using: for x, y, z in hand.landmarks
            # draw the label near the wrist, hand.landmarks[0]
        cv2.imshow("camera", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    tracker.close()
    cv2.destroyAllWindows()
