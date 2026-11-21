"""
DriveAlert — Facial Landmark Definitions & MediaPipe 468 Mesh Mappings
"""

import numpy as np

# Eye Aspect Ratio (EAR) Landmark Indices (Soukupová & Čech 6-point layout)
# [p1 (corner 1), p2 (top 1), p3 (top 2), p4 (corner 2), p5 (bottom 2), p6 (bottom 1)]
LEFT_EYE_INDICES = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_INDICES = [362, 385, 387, 263, 373, 380]

# Mouth Aspect Ratio (MAR) Landmark Indices
MOUTH_OUTER_INDICES = [61, 291, 0, 17]  # left corner, right corner, top outer, bottom outer
MOUTH_INNER_INDICES = [13, 14, 78, 308]  # top inner, bottom inner, left inner, right inner

MOUTH_INDICES = {
    'top': 13,
    'bottom': 14,
    'left': 78,
    'right': 308
}

# Key structural boundary contour indices for selective rendering
FACE_OVAL_INDICES = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]

# Realistic 3D Reference Model Points for Head Pose solvePnP (mm units, +X Right, +Y Down, +Z Away)
MODEL_3D_POINTS = np.array([
    (0.0, 0.0, 0.0),             # Nose tip (index 1)
    (0.0, 65.0, -50.0),          # Chin (index 152)
    (-45.0, -28.0, -30.0),       # Right eye outer corner (index 33)
    (45.0, -28.0, -30.0),        # Left eye outer corner (index 263)
    (-30.0, 32.0, -30.0),        # Right mouth corner (index 61)
    (30.0, 32.0, -30.0)          # Left mouth corner (index 291)
], dtype=np.float64)

HEAD_POSE_2D_INDICES = [1, 152, 33, 263, 61, 291]


def extract_landmarks(face_landmarks, frame_width: int, frame_height: int) -> np.ndarray:
    """Extracts landmark points as pixel (x, y) coordinates array of shape (N, 2)."""
    landmarks = np.zeros((len(face_landmarks), 2), dtype=np.float64)
    for idx, lm in enumerate(face_landmarks):
        landmarks[idx] = (lm.x * frame_width, lm.y * frame_height)
    return landmarks
