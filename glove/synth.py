import numpy as np
import sounddevice as sd


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

        # pad support
        self.pad_notes = None
        self.pad_level = 0.0
        self.pad_phases = {}

    # --------------------------------------------------

    def start(self):

        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=2,
            dtype="float32",
            callback=self.audio_callback
        )

        self.stream.start()

    # --------------------------------------------------

    def stop(self):

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

    # --------------------------------------------------

    def set_lead(
        self,
        midi,
        gate,
        cutoff_hz,
        vibrato_cents,
        reverb,
        delay,
    ):

        self.lead_midi = midi
        self.lead_gate = gate

        self.cutoff_hz = cutoff_hz
        self.vibrato_cents = vibrato_cents
        self.reverb_amount = reverb
        self.delay_amount = delay

    # --------------------------------------------------

    def set_pad(
        self,
        notes,
        cutoff_hz,
        level
    ):

        self.pad_notes = notes
        self.pad_level = level

    # --------------------------------------------------

    def pluck(self, midi, vel):

        self.set_lead(
            midi=midi,
            gate=True,
            cutoff_hz=1000,
            vibrato_cents=0,
            reverb=0,
            delay=0,
        )

    # --------------------------------------------------

    def drum(self, kind, vel):
        pass

    # --------------------------------------------------

    def level(self):

        return self.current_rms

    # --------------------------------------------------

    @staticmethod
    def midi_to_freq(midi):

        return 440.0 * (
            2 ** ((midi - 69) / 12)
        )

    # --------------------------------------------------

    def audio_callback(
        self,
        outdata,
        frames,
        time,
        status
    ):

        audio = np.zeros(
            frames,
            dtype=np.float32
        )

        # ==================================================
        # LEAD
        # ==================================================

        if (
            self.lead_gate
            and
            self.lead_midi is not None
        ):

            freq = self.midi_to_freq(
                self.lead_midi
            )

            phase_inc = (
                freq / self.samplerate
            )

            phase_block = (
                self.phase
                +
                np.arange(frames)
                * phase_inc
            )

            lead = 0.20 * np.sin(
                2
                * np.pi
                * phase_block
            )

            audio += lead

            self.phase = (
                phase_block[-1]
                % 1.0
            )

        # ==================================================
        # PAD / CHORDS
        # ==================================================

        if self.pad_notes:

            pad = np.zeros(
                frames,
                dtype=np.float32
            )

            for note in self.pad_notes:

                freq = self.midi_to_freq(
                    note
                )

                if note not in self.pad_phases:
                    self.pad_phases[note] = 0.0

                phase_inc = (
                    freq
                    / self.samplerate
                )

                phase_block = (
                    self.pad_phases[note]
                    +
                    np.arange(frames)
                    * phase_inc
                )

                pad += np.sin(
                    2
                    * np.pi
                    * phase_block
                )

                self.pad_phases[note] = (
                    phase_block[-1]
                    % 1.0
                )

            pad /= len(
                self.pad_notes
            )

            audio += (
                pad
                * self.pad_level
                * 0.20
            )

        # ==================================================

        audio = np.clip(
            audio,
            -1.0,
            1.0
        )

        self.current_rms = float(
            np.sqrt(
                np.mean(
                    audio ** 2
                )
            )
        )

        outdata[:] = np.column_stack(
            (audio, audio)
        )