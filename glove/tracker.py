import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision, BaseOptions
import time
from dataclasses import dataclass, asdict
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
        from glove.config import CONFIG
        options = vision.HandLandmarkerOptions(
          base_options=BaseOptions(model_asset_path=str(Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task")),
          running_mode=vision.RunningMode.VIDEO,
          num_hands=2,
          )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

        self.cap = cv2.VideoCapture(CONFIG["camera_index"], CONFIG["camera_backend"])
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

    def close(self):
        self.cap.release()
        # cv2.destroyAllWindows()
        self.landmarker.close()

# def draw_hud(frame, feats, x, y):
#     for key, value in feats.items():
#         if isinstance(value, (list, tuple, np.ndarray)):
#             parts = []
#             for v in value:
#                 if isinstance(v, (bool, np.bool_)):
#                     parts.append("T" if v else "F")
#                 elif isinstance(v, (float, np.floating)):
#                     parts.append(f"{v:.2f}")
#                 else:
#                     parts.append(str(v))
#             text = f"{key}: " + " ".join(parts)
#         elif isinstance(value, (float, np.floating)):
#             text = f"{key}: {value:.2f}"
#         else:
#             text = f"{key}: {value}"
#         cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
#         y += 20

def draw_states(frame, states, w):
    for role, state in states.items():
        x = 10 if role == "left" else w - 220
        y = 30
        cv2.putText(frame, role.upper(), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
        y += 22
        if state is None:
            cv2.putText(frame, "none", (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)
            continue
        for key, value in asdict(state).items():
            if key == "landmarks":
                continue
            if isinstance(value, bool):
                text = f"{key}: {value}"
            elif isinstance(value, float):
                text = f"{key}: {value:.2f}"
            elif isinstance(value, tuple):
                text = f"{key}: " + " ".join("T" if v else "F" for v in value)
            else:
                text = f"{key}: {value}"
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)
            y += 18
