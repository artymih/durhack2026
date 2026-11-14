# AirGlove

Play music in the air with a webcam. DurHack 2026. See **PLAN.md** for the plan, owners and schedule.

## Setup (Windows, PowerShell)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/download_model.py     # once, needs internet
python run.py                        # or: python run.py --mouse
```

Python 3.10-3.13 all work with the current `mediapipe`. If PowerShell blocks the activate script, run
`Set-ExecutionPolicy -Scope Process Bypass` first.

## Layout

```
run.py                  entry point, main loop, key handling         (D)
glove/config.py         every tunable number                         (C)
glove/tracker.py        camera + MediaPipe                           (A)
glove/features.py       landmarks -> finger curl, pinch, tilt, ...   (A)
glove/smoothing.py      One Euro filter, debounce helpers            (A)
glove/hands.py          HandState contract, left/right, strikes      (A)
glove/music.py          scales, chords, note quantizing              (C)
glove/instrument.py     gesture -> sound mappings (the creative file) (C)
glove/synth.py          sounddevice audio engine                     (B)
glove/visuals.py        OpenCV drawing, trails, saved artwork        (D)
scripts/download_model.py   fetch hand_landmarker.task
```

Every file's top docstring says what goes in it. Start there.
