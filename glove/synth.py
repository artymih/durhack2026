"""Audio engine: a small synth running in sounddevice's callback thread. (Owner: B)

THE METHODS BELOW ARE THE CONTRACT with instrument.py (C). Keep the signatures stable.

Design notes
- Import sounddevice lazily inside start(), so the module imports on machines with no audio device.
- Block processing with numpy only. NEVER loop per sample in Python; the callback will underrun.
  Use scipy.signal.lfilter(b, a, x, zi=state) for filters and keep `zi` between blocks.
- sd.OutputStream(samplerate=44100, blocksize=256, channels=2, dtype="float32", latency="low", callback=...)
- The main thread only sets plain float/bool attributes; the callback reads them. No locks needed.
- Avoid clicks: ramp amplitude and pitch across each block (np.linspace(prev, target, frames)) instead of jumping.
- Oscillators: accumulate phase with np.cumsum(freq_per_sample / sr). Saw = 2*(phase % 1) - 1. Detune two of them.
- Delay: ring buffer; read/write whole blocks (works while block <= delay length).
- Reverb: 4 parallel feedback combs (ring buffers of ~1100-1600 samples, feedback ~0.8) + lowpass. Easy to vectorise per block.

Build order: (1) hard-coded sine beeps through the callback, (2) lead voice, (3) filter, (4) delay/reverb,
(5) pad, (6) pluck + drums (kick = sine with falling pitch, snare/hat = filtered noise).

TODO: class Synth
    start() / stop()
    set_lead(midi: float | None, gate: bool, cutoff_hz: float, vibrato_cents: float, reverb: float, delay: float)
    set_pad(notes: list[int] | None, cutoff_hz: float, level: float)    # notes=None -> fade out
    pluck(midi: float, vel: float)          # one-shot, 0..1 velocity
    drum(kind: str, vel: float)             # "kick" | "snare" | "hat"
    level() -> float                        # current output RMS, so visuals can pulse with the sound
"""
