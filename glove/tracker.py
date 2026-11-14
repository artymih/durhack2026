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
