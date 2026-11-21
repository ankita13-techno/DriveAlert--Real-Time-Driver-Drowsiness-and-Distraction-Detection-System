"""
DriveAlert — Eye Aspect Ratio (EAR) & EMA Micro-Sleep Detection
"""

import numpy as np
from landmarks import LEFT_EYE_INDICES, RIGHT_EYE_INDICES

EAR_THRESHOLD = 0.22
EAR_CONSEC_FRAMES = 45  # ~1.5s at 30 FPS


def calculate_single_eye_ear(eye_points: np.ndarray) -> float:
    p1, p2, p3, p4, p5, p6 = eye_points[0], eye_points[1], eye_points[2], eye_points[3], eye_points[4], eye_points[5]
    dist_v1 = np.linalg.norm(p2 - p6)
    dist_v2 = np.linalg.norm(p3 - p5)
    dist_h = np.linalg.norm(p1 - p4)

    if dist_h < 1e-6:
        return 0.0

    return float((dist_v1 + dist_v2) / (2.0 * dist_h))


def calculate_ear(landmarks: np.ndarray) -> float:
    left_ear = calculate_single_eye_ear(landmarks[LEFT_EYE_INDICES])
    right_ear = calculate_single_eye_ear(landmarks[RIGHT_EYE_INDICES])
    return (left_ear + right_ear) / 2.0


class EarTracker:
    """
    Tracks Eye Aspect Ratio using Exponential Moving Average (EMA, alpha=0.3).
    Maintains a rolling counter for smoothed EAR < threshold to trigger Micro-Sleep Alert.
    Supports dynamic personalized threshold calculation (e.g. 0.75 * baseline EAR).
    """
    def __init__(self, threshold: float = EAR_THRESHOLD, consec_frames: int = EAR_CONSEC_FRAMES, alpha: float = 0.3):
        self.threshold = threshold
        self.consec_frames = consec_frames
        self.alpha = alpha
        self.smoothed_ear = None
        self.counter = 0
        self.is_drowsy = False

    def set_personalized_threshold(self, baseline_ear: float):
        """Dynamically adjusts threshold based on user's baseline resting geometry."""
        self.threshold = max(0.16, min(0.25, 0.75 * baseline_ear))
        print(f"[EarTracker] Personalized EAR threshold set to {self.threshold:.3f} (Baseline: {baseline_ear:.3f})")

    def update(self, raw_ear: float) -> tuple[bool, float]:
        if self.smoothed_ear is None:
            self.smoothed_ear = raw_ear
        else:
            self.smoothed_ear = self.alpha * raw_ear + (1.0 - self.alpha) * self.smoothed_ear

        if self.smoothed_ear < self.threshold:
            self.counter += 1
            if self.counter >= self.consec_frames:
                self.is_drowsy = True
        else:
            self.counter = 0
            self.is_drowsy = False

        return self.is_drowsy, float(self.smoothed_ear)
