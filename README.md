# The Harmonic Orb

Play music in the air with a webcam. DurHack 2026.

## Setup

Run everything from the project root folder!!

**Windows (PowerShell)**
```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Then, on either**
```pip install -r requirements.txt
python scripts/download_model.py # once, needs internet
python debug_hud.py # camera check: skeleton + hand values (q to quit)
python run.py
```

Python 3.9-3.14 SHOULD all work with the current `mediapipe`. 3.12 is a good choice.

## Layout

```
run.py                  entry point, main loop, key handling 
glove/config.py         every tunable number. ish
glove/tracker.py        camera + MediaPipe
glove/features.py       landmarks -> finger curl, pinch, tilt, etc
glove/smoothing.py      OneEuro filter, debounce helpers 
glove/hands.py          HandState contract, left/right
glove/music.py          scales, chords, note quantizing 
glove/instrument.py     gesture -> sound mappings
glove/synth.py          sounddevice audio engine
glove/visuals.py        OpenCV drawing, orbs, saved artwork
scripts/download_model.py   downloads the MediaPipe model (models/hand_landmarker.task)
debug_hud.py            for debugging the HUD
test_{any}              test scripts, not required for normal execution
