import numpy as np
import pygame


class Sound:
    FREQUENCY = 441.0  # Hz
    DURATION = 1.0  # 1s
    VOLUME = 0.5  # 50%
    SAMPLE_RATE = 44100  # Cannot be changed
    CHANNELS = 2
    BITS = -16
    BUFFER = 1024

    def __init__(self):
        pygame.mixer.pre_init(self.SAMPLE_RATE, self.BITS, self.CHANNELS, self.BUFFER)
        pygame.mixer.init()
        self.sound = self.generate_square_wave()
        self.is_playing = False

    def generate_square_wave(self) -> pygame.mixer.Sound:
        """Generate_square_wave and return a pygame.mixer.Sound object."""

        # Generate single cycle of square wave
        n_samples = int(self.SAMPLE_RATE * self.DURATION)
        samples_per_cycle = int(self.SAMPLE_RATE / self.FREQUENCY)
        wave_cycle = [1] * (samples_per_cycle // 2) + [-1] * (samples_per_cycle // 2)

        # Repeat the cycle to generate the full waveform
        waveform = np.tile(wave_cycle, (n_samples // samples_per_cycle) + 1)[:n_samples]

        # Scale the waveform to the desired volume and convert to 16-bit integers
        waveform_scaled = np.int16(waveform * self.VOLUME * 32767)

        # Convert mono waveform to stereo by duplicating the waveform
        waveform_stereo = np.column_stack((waveform_scaled, waveform_scaled))

        return pygame.sndarray.make_sound(waveform_stereo)

    def play_beep(self):
        if not self.is_playing:
            self.sound.play(-1)  # -1 is for looping indefinitely
            self.is_playing = True

    def stop_beep(self):
        if self.is_playing:
            self.sound.stop()
            self.is_playing = False
