"""
DriveAlert — Threaded Camera & CLAHE Low-Light Illumination Preprocessing
"""

import threading
import time
import cv2
import numpy as np


class ThreadedCamera:
    """
    Asynchronous OpenCV VideoCapture wrapper.
    Acquires frames on a background thread to eliminate camera I/O latency,
    and applies CLAHE (Contrast Limited Adaptive Histogram Equalization) on LAB L-channel
    to normalize contrast under low-light/night cabin conditions.
    """
    def __init__(self, src: int = 0, width: int = 640, height: int = 480, apply_clahe: bool = True):
        self.src = src
        self.width = width
        self.height = height
        self.apply_clahe_enabled = apply_clahe

        # Try DirectShow backend on Windows first to prevent MSMF driver error
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.src)

        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera device index {self.src}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))

        self.grabbed = False
        self.frame = None
        self.stopped = False
        self.lock = threading.Lock()

        # Grab initial frame
        grabbed, frame = self.cap.read()
        if grabbed and frame is not None:
            self.grabbed = grabbed
            self.frame = frame

        # Start background capture thread
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                break
            grabbed, frame = self.cap.read()
            if not grabbed or frame is None:
                time.sleep(0.005)
                continue

            with self.lock:
                self.grabbed = grabbed
                self.frame = frame

    def read(self) -> tuple[bool, np.ndarray]:
        with self.lock:
            if not self.grabbed or self.frame is None:
                return False, None
            frame_copy = self.frame.copy()

        if self.apply_clahe_enabled:
            frame_copy = self.preprocess_clahe(frame_copy)

        return True, frame_copy

    def preprocess_clahe(self, frame: np.ndarray) -> np.ndarray:
        """
        Converts BGR -> LAB, applies CLAHE to L-channel, converts back to BGR.
        Normalizes cabin illumination under low-light/night driving conditions.
        """
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        cl = self.clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def stop(self):
        self.stopped = True
        if self.thread.is_alive():
            self.thread.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()
