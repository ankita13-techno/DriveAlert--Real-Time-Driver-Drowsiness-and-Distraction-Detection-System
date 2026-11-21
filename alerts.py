"""
DriveAlert — Threaded Pygame Alerting Module
Generates synthetic acoustic alarm tones using Pygame Mixer and NumPy.
Executes non-blocking sound playback on background threads to ensure zero drop in video FPS.
"""

import threading
import time
import numpy as np
import pygame


def generate_tone(frequency: float, duration: float, sample_rate: int = 44100) -> pygame.mixer.Sound:
    """
    Generates a 16-bit PCM Sound object for a given frequency and duration.
    
    Args:
        frequency (float): Tone frequency in Hz.
        duration (float): Tone duration in seconds.
        sample_rate (int): Audio sample rate in Hz.
        
    Returns:
        pygame.mixer.Sound: Pygame sound object.
    """
    n_samples = int(sample_rate * duration)
    t = np.linspace(0, duration, n_samples, False)
    # Generate sine wave with soft envelope attack/decay to prevent audio clicks
    sine_wave = np.sin(2 * np.pi * frequency * t)
    
    # Apply fade-in and fade-out envelope
    envelope = np.ones(n_samples)
    fade = int(sample_rate * 0.01)  # 10ms fade
    if fade > 0 and n_samples > 2 * fade:
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        
    audio_data = (sine_wave * envelope * 32767).astype(np.int16)
    
    # Duplicate for stereo audio output
    stereo_data = np.column_stack((audio_data, audio_data))
    return pygame.mixer.Sound(stereo_data)


class AlertManager:
    """
    Non-blocking acoustic alert sound manager for Drowsiness, Yawn, and Distraction triggers.
    """
    def __init__(self):
        self.enabled = False
        try:
            # Initialize Pygame Mixer with standard stereo config
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
        except Exception as e:
            print(f"Warning: Could not initialize Pygame Mixer: {e}")
            return

        # Pre-synthesize alert sounds
        self.drowsy_sound = generate_tone(frequency=1000.0, duration=0.4)
        self.yawn_sound = generate_tone(frequency=600.0, duration=0.5)
        self.distraction_sound = generate_tone(frequency=850.0, duration=0.3)

        self.last_play_time = {
            'drowsy': 0.0,
            'yawn': 0.0,
            'distraction': 0.0
        }
        
        self.cooldown_seconds = 0.5  # Prevents overlapping audio overlap chaos

    def trigger_drowsy_alert(self):
        """Triggers acoustic alert for micro-sleep / drowsiness."""
        self._play_async('drowsy', self.drowsy_sound)

    def trigger_yawn_alert(self):
        """Triggers acoustic alert for yawning."""
        self._play_async('yawn', self.yawn_sound)

    def trigger_distraction_alert(self):
        """Triggers acoustic alert for head distraction."""
        self._play_async('distraction', self.distraction_sound)

    def _play_async(self, alert_key: str, sound: pygame.mixer.Sound):
        if not self.enabled:
            return

        curr_time = time.time()
        if curr_time - self.last_play_time[alert_key] >= self.cooldown_seconds:
            self.last_play_time[alert_key] = curr_time
            # Run audio playback in separate background daemon thread
            threading.Thread(target=self._play_sound_thread, args=(sound,), daemon=True).start()

    def _play_sound_thread(self, sound: pygame.mixer.Sound):
        try:
            channel = sound.play()
            if channel is not None:
                # Wait for sound to finish without blocking main CV loop
                while channel.get_busy():
                    time.sleep(0.01)
        except Exception as e:
            pass

    def cleanup(self):
        """Cleanly releases Pygame Mixer resources."""
        if self.enabled:
            try:
                pygame.mixer.quit()
            except Exception:
                pass
