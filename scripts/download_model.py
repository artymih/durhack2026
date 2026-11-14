"""Download the MediaPipe hand model to ./models/hand_landmarker.task (run once, while you have wifi).

mediapipe 1.x removed the old mp.solutions API, so the model is no longer bundled in the pip package.
Not yet run against the real URL, so if it fails, download the file in a browser and drop it in ./models/.
"""
import pathlib
import urllib.request

URL = ("https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
       "hand_landmarker/float16/1/hand_landmarker.task")
DEST = pathlib.Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"

if __name__ == "__main__":
    DEST.parent.mkdir(exist_ok=True)
    urllib.request.urlretrieve(URL, DEST)
    print("saved", DEST, DEST.stat().st_size, "bytes")
