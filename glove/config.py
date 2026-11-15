import cv2
import sys

CONFIG = {
    # arty C
    "music": {
        "root_midi": 33,                  
        "lead_scale": "minor_pentatonic", 
        "lead_octaves": 2,                
        "lead_root_offset": 12,           
        "pad_scale": "natural_minor",     
        "quantize": True
    },
    # megan A
    "camera": {},
    "model_path": "models/hand_landmarker.task",
    "swap_hand": False,
    "camera_index": 0,
    "camera_backend":cv2.CAP_DSHOW if sys.platform.startswith("win") else cv2.CAP_ANY,  # you can change this to just cv2.CAP_DSHOW if using windows, try cv2.CAP_MSMF if that's not working
    "stable_frames": 4, # how many frames should hand/fingers be stable for before it actually updates the note, 4 = about 0.13 s at 30 fps;
    "filter_settings": dict(min_cutoff=0.3, beta=5.0),
    # min_cutoff = how smooth when still (lower = less jitter, more lag)
    # beta = how quickly filter opens as you speed up (higher = less lag during fast moves but less smooth)
    "hold_sec":0.05, # keep hand alive this long after dropping out
    "size_far":0.8,  # value of cam_distance/depth at hand at far distance
    "size_near":0.1,   # value of cam_distance/depth at hand right next to camera
    "thumb_open_threshold": 0.88,
    "finger_open_threshold": 0.54,
    "pinch_apart": 0.68,
    "pinch_touch": 0.3,
    "curl_straight": 1.65,
    "curl_fist": 0.78,

    # amelka B
    "audio": {"samplerate": 44100, "blocksize": 256}
}  
