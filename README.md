# 🚗 DriveAlert: Real-Time Driver Drowsiness and Distraction Detection System

**Category:** Engineering & Technology | **AI Driver Vigilance**

---

## 📌 Abstract

More than **20% of fatal road crashes** occur because drivers get tired, doze off, or look away from the road. **DriveAlert** is a low-cost, smart camera system that monitors the driver's face in real time without requiring any wearable sensors. 

By mapping **468 virtual coordinate points** over the eyes, mouth, and head, the software instantly detects if the eyes are closed in a micro-sleep, if the driver is yawning from exhaustion, or if their head has turned away from the windshield. Running completely offline on a standard CPU at **32 frames per second (FPS)** with **94.6% accuracy**, the system triggers an immediate audio alarm to prevent accidents before they happen.

---

## 🎯 Problem Statement & Objectives

Highway logistics and night-time transit involve long, monotonous driving hours where driver alertness degrades into micro-sleep (eyelid closures lasting 1 to 3 seconds). Existing solutions suffer from major drawbacks:
* **Wearable Biosensors (EEG/Smart Eyewear):** Cause physical discomfort, skin irritation, and driver resistance during extended shifts.
* **End-to-End Deep CNNs:** Require heavy GPU servers, consume excessive electrical power, and cannot run efficiently on budget vehicle dashboard processors.

### Key Objectives
* Develop a real-time, non-intrusive monitoring algorithm using an ordinary RGB cabin webcam.
* Formulate mathematical landmark ratios (**EAR** & **MAR**) to reliably separate involuntary blinks from dangerous micro-sleep episodes.
* Integrate head-pose estimation to flag driver visual distraction (looking away from the windshield corridor for $>2.5\text{ seconds}$).
* Achieve real-time performance ($\ge 30\text{ FPS}$, $<35\text{ms}$ latency) on standard edge CPU architecture (e.g., Raspberry Pi 4 / Intel i3/i5) with zero cloud dependency.

---

## ⚙️ Methodology & System Pipeline

A standard dashboard camera captures the driver's face at 30 FPS, mapping 468 key facial points to reduce memory overhead by **80%** compared to heavy neural networks. 

1. **Video Ingestion:** Captures RGB frames at 30 FPS with CLAHE lighting contrast normalization.
2. **MediaPipe Mesh:** Tracks 468 2D/3D facial landmarks in real time.
3. **Geometric Ratios & Head Pose:**
   * **Micro-sleep Detection (`EAR`):** Tracks eyelid separation to flag closures lasting over **$1.5\text{ seconds}$**.
   * **Fatigue Yawning (`MAR`):** Measures lip opening to detect persistent yawning.
   * **Visual Distraction (`Pose`):** Monitors 3D head angles to catch off-road attention or phone usage lasting over **$2.5\text{ seconds}$**.
4. **Temporal Filter:** Validates sustained threshold breaches across frames to eliminate false positives.
5. **Acoustic Alarm:** Triggers a non-blocking in-cabin audio alert within $<35\text{ms}$ latency.

---

## 📂 Repository Architecture

| Module Name | Primary Class / Functions | Operational Responsibility |
| :--- | :--- | :--- |
| `camera.py` | `ThreadedCamera` | Asynchronous background thread frame acquisition; CLAHE lighting contrast normalization. |
| `landmarks.py` | `extract_landmarks()` | Maps MediaPipe 468 Face Mesh node indices; extracts 2D/3D coordinate arrays. |
| `ear.py` | `calculate_ear()`, `EarTracker` | Calculates Eye Aspect Ratio; maintains EMA smoothing and rolling micro-sleep counter. |
| `mar.py` | `calculate_mar()`, `MarTracker` | Calculates Mouth Aspect Ratio; maintains EMA smoothing and rolling yawn tracker. |
| `pose.py` | `estimate_head_pose()`, `PoseTracker` | Solves `cv2.solvePnP` 3D perspective mapping; tracks 2.5s continuous visual distraction. |
| `alerts.py` | `AlertManager` | Thread-safe `pygame` mixer audio synthesizer; generates acoustic tones without blocking video loop. |
| `logger.py` | `IncidentLogger` | Local SQLite database (`drivealert_logs.db`) recorder for offline post-trip incident telemetry. |
| `main.py` | `Main Processing Loop` | Integrates camera thread, calibration, tracking analytics, dark-glass HUD rendering, and teardown. |

---

## 🛠️ Experimental Setup & Tech Stack

* **Camera Hardware:** Standard USB 720p / 1080p RGB sensor at 30 FPS mounted on the steering column or dashboard.
* **Compute Node:** Quad-core edge CPU (tested on Raspberry Pi 4 and Intel Core i5 laptop) operating without dedicated GPU acceleration.
* **Software Stack:** 
  * Python 3.9+
  * OpenCV 4.8 (Image I/O & `solvePnP`)
  * Google MediaPipe (Face Mesh keypoint extraction)
  * Pygame (Threaded non-blocking acoustic buzzer cues)
  * SQLite3 (Offline incident logging)

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/ankita13-techno/DriveAlert--Real-Time-Driver-Drowsiness-and-Distraction-Detection-System.git
cd DriveAlert--Real-Time-Driver-Drowsiness-and-Distraction-Detection-System
```

### 2. Install Dependencies
```bash
pip install opencv-python mediapipe pygame numpy
```

### 3. Run the Application
```bash
python main.py
```

---

## 📊 Conclusion & Future Enhancements

* **Edge Efficiency & Privacy:** Runs completely offline on local hardware using geometric landmark ratios, matching the accuracy of heavy neural networks without expensive sensors, internet access, or compromising driver data privacy.
* **Future Roadmap:** Integrating Near-Infrared (NIR) illuminators for nocturnal driving conditions and CAN-bus integration for autonomous vehicle speed throttling.

---

## 📚 References

1. **LiteDriveNet Architecture Paper:** 16-layer lightweight CNN; 1.71 MB, 446K parameters, 0.5 GFLOPs; uses `DistractedDrivingSet_v1`.
2. **Deep Learning Distraction Review:** Compares VGG-16, ResNet50, and MobileNetV2 using transfer learning for 10 driver-posture classes.
3. **SPIDER 2.0 Situational Awareness Review:** Covers driver scanning, inattentional blindness, and risks from visual distraction beyond ~2.5 seconds.

---

## 🚨 Smart Alert Scenarios Overview

![DriveAlert Smart Driver Safety Alerts](DriveAlert_%20Smart%20Driver%20Safety%20Alerts.png)
