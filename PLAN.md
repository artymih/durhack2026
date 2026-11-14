# AirGlove: DurHack 2026 plan

**Pitch:** play music in the air with just a webcam. Hand position, distance, tilt, finger shapes and flicks become notes, chords, effects and drums, a bit like Imogen Heap's Mi.Mu gloves, but with no gloves. Every performance also paints an image, which you can save as a "composition".

**Stack (decided):** Python 3.10-3.13 on Windows. MediaPipe Tasks `HandLandmarker` + OpenCV window for tracking and visuals. numpy + scipy synth through `sounddevice`.

## Why this fits the judging

Theme: **Composition** (art, music, tech). We cover all three, and the saved artwork makes the "art" part concrete.

| Criterion | What earns it |
|---|---|
| Creativity & Innovation | A new instrument with no hardware. The performance is also generative art. |
| Technical Competence & Execution | Real-time vision, smoothing filters, a DSP synth in the audio thread. |
| Research & Learning | Write down what we learn (see "Gotchas") and show it in the demo. |
| Polish & Completion | Feature freeze early, offline-safe setup, rehearsed demo, backup video. |

## Gesture to sound (v1)

| Hand | Gesture | Controls |
|---|---|---|
| Right | move left/right | pitch (minor pentatonic, 2 octaves) |
| Right | move up/down | filter brightness |
| Right | toward / away from camera | reverb (far = wetter) |
| Right | pinch thumb + index | echo throw |
| Right | tilt hand | vibrato |
| Right | make a fist | mute |
| Left | hold up 1-5 fingers | chord: i, VI, III, VII, iv (pad) |
| Left | fist | silence |
| Left | tilt | chord colour (sus2 / triad / add7) |
| Left | up/down, near/far | pad brightness, pad volume |
| Strike mode (M) | flick right hand down | pluck (x picks the note) |
| Strike mode (M) | flick left hand down | drum (left third kick, middle snare, right third hat) |

## Data flow

```
webcam -> tracker.py -> features.py -> hands.py -> instrument.py -> synth.py (audio thread) -> speakers
 (A)        (A)            (A)           (A)           (C)              (B)
                                            \-> visuals.py (D) -> OpenCV window
```

`glove/hands.py::HandState` (fields) and the `Synth` method list in `glove/synth.py` are the two contracts. Agree on them in the first 15 minutes, then everyone works in parallel. `python run.py --mouse` fakes a hand so B, C and D don't wait for A.

## Who owns what (4 people)

| Person | Files | First milestone |
|---|---|---|
| A: Vision | `tracker.py`, `features.py`, `smoothing.py`, `hands.py` | Camera window with skeleton, then printed `HandState` values that look sane |
| B: Sound | `synth.py` | A beep through `sounddevice`, then a lead voice with glide + filter |
| C: Music & mapping | `music.py`, `instrument.py`, `config.py` | Mouse x picks a quantized note through B's synth |
| D: Visuals & demo | `visuals.py`, `run.py`, README, slides/video | Dimmed camera + skeleton + HUD in the OpenCV window |

If you're fewer than four, A+C and B+D pair up naturally.

## Schedule (Sat 14 Nov, hacking 12:00 to 12:00 Sunday)

| Time | Goal |
|---|---|
| 14:15-15:00 | Everyone sets up (README). Agree the two contracts. |
| 15:00-17:00 | **M0:** wave a hand, hear the pitch change. (Use `--mouse` if tracking isn't ready.) |
| 17:30 | Dinner (collect in waves by Guild). Check where each of you is. |
| 17:30-21:00 | **M1:** left-hand chords, pad, reverb/echo, trails. Debug HUD to tune thresholds. |
| 21:00-00:00 | **M2:** Strike mode (plucks + drums), gesture to switch modes, "save artwork" (S). |
| 00:00 | Midnight pizza (QRT). Decide what's stretch and what's cut. |
| 00:00-03:00 | Polish + one stretch goal. Then sleep in shifts (TLC123), not all at once. |
| 08:30 | **Feature freeze.** Only bug fixes after this. |
| 09:30 | Sunday breakfast. |
| 09:30-11:00 | Rehearse the demo twice, record a backup video, write the submission. |
| 11:00-12:00 | Final check, submit. Confirm the submission and judging process with the organisers early. |

## Gotchas we already found (use these in the "Research & Learning" story)

- `mediapipe` 1.x **removed `mp.solutions`**. Use the Tasks API and download `hand_landmarker.task` (`python scripts/download_model.py`). Do it on wifi, now.
- **Mirror the frame before detection** (`cv2.flip(frame, 1)`) so MediaPipe's Left/Right labels match the user's real hands. If they're still swapped, add a `swap_handedness` setting.
- MediaPipe's **z is not distance to camera.** Use apparent hand size (wrist to middle knuckle) as the depth signal.
- Raw tracking jitters. Use a **One Euro filter**, a stable finger-count debounce, and hysteresis at note borders, otherwise the lead sounds like a broken theremin.
- Never loop per sample in the audio callback. Use numpy blocks and `scipy.signal.lfilter` with saved state.
- Ramp pitch and volume across each block or you'll hear clicks.
- Don't `pip install opencv-python`: `mediapipe` already installs `opencv-contrib-python`, and the two conflict.
- Feature thresholds in `features.py` are estimates. Tune them on a real hand with the debug HUD.

## Risks

| Risk | Mitigation |
|---|---|
| Venue wifi is bad | Install everything and download the model now. |
| Bad lighting or a busy background | Test at the demo table early. Plain wall behind you, light on your hands. |
| Latency feels laggy | `blocksize=256`, `latency="low"`, keep the vision loop under about 30 ms. |
| Audio device changes on the demo laptop | Test on the demo laptop's own speakers well before the demo. |
| Live demo fails | Record a backup video by 10:00. |

## Stretch goals (in priority order)

1. Gesture to switch modes (both fists for 1 s), so nobody touches the keyboard on stage.
2. **Looper:** record a few bars of the lead, then loop it under live playing. (A very Mi.Mu move.)
3. Optional MIDI out (`mido`) so the same gestures can drive a real synth or DAW.
4. Two-player mode: each person gets one hand.
5. RS challenge tie-in (sense, analyse, decide, act): needs their Arduino UNO Q + camera hardware, so only if you commit to it early.

## 90-second demo

1. (10 s) "Imogen Heap plays with gloves. We use a webcam."
2. (30 s) Right hand melody over left-hand chords. Show the gesture cheat sheet on screen.
3. (20 s) Strike mode: plucks and drums.
4. (15 s) Press S and show the saved artwork: "your performance, as a picture".
5. (15 s) What we learned (the gotchas list) and what's next.

## Prize tracks worth a look

- Main **Composition** prize (art + music + tech): this is our home track.
- **Marshall Wace "New Worlds"**: judged on creativity, technical complexity, presentation. "A new instrument with no hardware" fits.
- Ask the RS and QRT tables if there's a genuinely cheap way in. Don't contort the project for them.
