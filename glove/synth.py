import numpy as np
import sounddevice as sd

#import math
#import pygame
#import time

#pygame.init()

#bits=16
#sample_rate= 44100

#pygame.mixer.pre_init(sample_rate, bits)

#def sine_x(amp, freq, time):
#    return int(round(amp * math.sin(2 * math.pi * freq * time)))

#class Tone:
#    def sine(freq, duration=1, speaker=None): 
#        num_samples = int(round(duration * sample_rate))
#
#        sound_buffer = numpy.zeros((num_samples, 2), dtype = numpy.int16)
#        amplitude = 2 ** (bits - 1) - 1

#        for sample_num in range(num_samples):
#            t = float(sample_num) / sample_rate

#            sine = sine_x(amplitude, freq, t)

#            if speaker == 'r':
#                sound_buffer[sample_num][1] = sine
#            if speaker == 'l':
#                sound_buffer[sample_num][0] = sine

#            else:
#                sound_buffer[sample_num][1] = sine
#                sound_buffer[sample_num][0] = sine

#        sound = pygame.sndarray.make_sound(sound_buffer)
#        sound.play(loops=1, maxtime=int(duration * 1000))
#        time.sleep(duration)

#
# Tone.sine(400, duration=2)*/


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

class Synth:
    def __init__(self):

        self.lead_midi = None
        self.lead_gate = False
        self.cutoff_hz = 1000.0
        self.vibrato_cents = 0.0
        self.reverb_amount = 0.0
        self.delay_amount = 0.0

        self.samplerate = 44100
        self.blocksize = 256

        self.phase = 0.0
        self.current_rms = 0.0

        self.stream = None

    def start(self):
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=2,
            dtype="float32",
            callback=self.audio_callback
        )

        self.stream.start()

    def stop(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()

    def set_lead(self, midi, gate, cutoff_hz, vibrato_cents, reverb, delay):
        self.lead_midi = midi
        self.lead_gate = gate
        self.cutoff_hz = cutoff_hz
        self.vibrato_cents = vibrato_cents
        self.reverb_amount = reverb
        self.delay_amount = delay


    def audio_callback(self, outdata, frames, time, status):

        audio = np.zeros(frames, dtype=np.float32)

        if self.lead_gate and self.lead_midi is not None:

            # MIDI -> frequency
            freq = 440.0 * (2 ** ((self.lead_midi - 69) / 12))

            # phase increment per sample
            phase_inc = freq / self.samplerate

            phase_block = (
                self.phase
                + np.arange(frames) * phase_inc
            )

            # basic sine wave
            audio = 0.2 * np.sin(
                2 * np.pi * phase_block
            )

            self.phase = phase_block[-1] % 1.0

        self.current_rms = np.sqrt(
            np.mean(audio ** 2)
        )

        # stereo output
        outdata[:] = np.column_stack(
            (audio, audio)
        )

#below this is testing section
if __name__ == "__main__":

    synth = Synth()

    synth.start()

    synth.set_lead(midi=69, gate=True, cutoff_hz=1000, vibrato_cents=0, reverb=0, delay=0),

    input("Press Enter to quit...")

    synth.stop()
        
    
