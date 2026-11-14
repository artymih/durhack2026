import numpy as np
import sounddevice as sd


class Synth:

    def __init__(self):

        # lead voice
        self.lead_midi = None
        self.lead_gate = False

        self.cutoff_hz = 1000.0
        self.vibrato_cents = 0.0
        self.reverb_amount = 0.0
        self.delay_amount = 0.0

        self.samplerate = 44100
        self.blocksize = 256

        self.stream = None

        self.current_rms = 0.0

        # lead oscillator state
        self.phase1 = 0.0
        self.phase2 = 0.0

        self.current_freq = 440.0

        self.vibrato_phase = 0.0

        # filter state
        self.filter_z = 0.0

        # pad
        self.pad_notes = None
        self.pad_level = 0.0
        self.pad_phases = {}

        # delay (500ms)

        self.delay_len = self.samplerate // 2

        self.delay_buffer = np.zeros(
            self.delay_len,
            dtype=np.float32
        )

        self.delay_pos = 0

        # reverb

        self.reverb_lengths = [
            1103,
            1277,
            1499,
            1613,
        ]

        self.reverb_buffers = [
            np.zeros(
                n,
                dtype=np.float32
            )
            for n in self.reverb_lengths
        ]

        self.reverb_positions = [
            0,
            0,
            0,
            0,
        ]

        # pluck
        self.pluck_midi = None
        self.pluck_level = 0.0
        self.pluck_phase = 0.0

        # drums
        self.kick_level = 0.0
        self.kick_phase = 0.0

        self.snare_level = 0.0
        self.hat_level = 0.0

    # ==================================================
    # ENGINE CONTROL
    # ==================================================

    def start(self):

        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            channels=2,
            dtype="float32",
            latency="low",
            callback=self.audio_callback,
        )

        self.stream.start()

    def stop(self):

        if self.stream is not None:

            self.stream.stop()
            self.stream.close()

            self.stream = None

    # ==================================================
    # API CONTRACT
    # ==================================================

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

    def set_pad(
        self,
        notes,
        cutoff_hz,
        level,
    ):

        self.pad_notes = notes
        self.pad_level = level

    def pluck(self, midi, vel):

        self.pluck_midi = midi
        self.pluck_level = vel


    def drum(self, kind, vel):

        if kind == "kick":
            self.kick_level = vel

        elif kind == "snare":
            self.snare_level = vel

        elif kind == "hat":
            self.hat_level = vel

    def level(self):

        return self.current_rms

    # ==================================================
    # HELPERS
    # ==================================================

    @staticmethod
    def midi_to_freq(midi):

        return 440.0 * (
            2 ** (
                (midi - 69)
                / 12.0
            )
        )

    @staticmethod
    def make_saw(phase):

        return (
            2.0
            * (phase % 1.0)
            - 1.0
        )

    # ==================================================
    # CALLBACK
    # ==================================================

    def audio_callback(
        self,
        outdata,
        frames,
        time,
        status,
    ):

        audio = np.zeros(
            frames,
            dtype=np.float32
        )

        # ==========================================
        # LEAD VOICE
        # ==========================================

        if (
            self.lead_gate
            and
            self.lead_midi is not None
        ):

            target_freq = self.midi_to_freq(
                self.lead_midi
            )

            freqs = np.linspace(
                self.current_freq,
                target_freq,
                frames,
            )

            self.current_freq = target_freq

            # vibrato

            if self.vibrato_cents > 0:

                vib_phase = (
                    self.vibrato_phase
                    +
                    np.arange(frames)
                    * 5.0
                    / self.samplerate
                )

                vib = np.sin(
                    2
                    * np.pi
                    * vib_phase
                )

                ratio = 2 ** (
                    (
                        vib
                        * self.vibrato_cents
                    )
                    / 1200.0
                )

                freqs *= ratio

                self.vibrato_phase = (
                    vib_phase[-1]
                    % 1.0
                )

            phase1 = (
                self.phase1
                +
                np.cumsum(
                    freqs
                    / self.samplerate
                )
            )

            phase2 = (
                self.phase2
                +
                np.cumsum(
                    freqs
                    * 1.0005
                    / self.samplerate
                )
            )

            osc1 = self.make_saw(
                phase1
            )

            osc2 = self.make_saw(
                phase2
            )

            lead = (
                osc1 + osc2
            ) * 0.08

            self.phase1 = (
                phase1[-1]
                % 1.0
            )

            self.phase2 = (
                phase2[-1]
                % 1.0
            )

            audio += lead

        # ==========================================
        # PAD
        # ==========================================

        if self.pad_notes:

            pad = np.zeros(
                frames,
                dtype=np.float32
            )

            for note in self.pad_notes:

                freq = self.midi_to_freq(
                    note
                )

                if (
                    note
                    not in self.pad_phases
                ):

                    self.pad_phases[
                        note
                    ] = 0.0

                phase = (
                    self.pad_phases[note]
                    +
                    np.cumsum(
                        np.full(
                            frames,
                            freq
                            /
                            self.samplerate
                        )
                    )
                )

                pad += (
                    np.sin(
                        2
                        * np.pi
                        * phase
                    )
                )

                self.pad_phases[
                    note
                ] = (
                    phase[-1]
                    % 1.0
                )

            pad /= len(
                self.pad_notes
            )

            audio += (
                pad
                * self.pad_level
                * 0.15
            )

        # ==========================================
        # FILTER
        # ==========================================

        alpha = min(
            (
                self.cutoff_hz
                / self.samplerate
            )
            * 8.0,
            0.99
        )

        filtered = np.empty_like(
            audio
        )

        z = self.filter_z

        for i in range(frames):

            z += alpha * (
                audio[i] - z
            )

            filtered[i] = z

        self.filter_z = z

        audio = filtered

        # ==========================================
        # DELAY
        # ==========================================

        if self.delay_amount > 0:

            delayed = np.zeros_like(
                audio
            )

            for i in range(frames):

                delayed[i] = (
                    self.delay_buffer[
                        self.delay_pos
                    ]
                )

                self.delay_buffer[
                    self.delay_pos
                ] = (
                    audio[i]
                    +
                    delayed[i]
                    * 0.4
                )

                self.delay_pos = (
                    self.delay_pos + 1
                ) % self.delay_len

            audio += (
                delayed
                * self.delay_amount
            )

        # ==========================================
        # REVERB
        # ==========================================

        if self.reverb_amount > 0:

            wet = np.zeros_like(
                audio
            )

            for n, buf in enumerate(
                self.reverb_buffers
            ):

                pos = self.reverb_positions[
                    n
                ]

                for i in range(frames):

                    y = buf[pos]

                    buf[pos] = (
                        audio[i]
                        + y * 0.8
                    )

                    wet[i] += y

                    pos += 1

                    if pos >= len(buf):
                        pos = 0

                self.reverb_positions[
                    n
                ] = pos

            wet /= len(
                self.reverb_buffers
            )

            audio += (
                wet
                * self.reverb_amount
                * 0.5
            )

        # ==========================================
        # OUTPUT
        # ==========================================

        audio = np.clip(
            audio,
            -1.0,
            1.0
        )

        self.current_rms = float(
            np.sqrt(
                np.mean(
                    audio * audio
                )
            )
        )

        outdata[:] = np.column_stack(
            (
                audio,
                audio,
            )
        )