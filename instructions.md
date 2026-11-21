# DriveAlert — Project Blueprint & State Document

## 1. Project Identity

- **Name:** DriveAlert — Real-Time Driver Drowsiness and Distraction Detection System Using Facial Landmark Geometry
- **Category:** Engineering & Technology, Avishkar Research Convention (UG, 3rd Year IT/AI)
- **One-line pitch:** A lightweight, non-intrusive, edge-only computer vision system that watches a driver's face through an ordinary RGB webcam and raises an alarm before micro-sleep or distraction becomes dangerous.
- **Core constraint:** Everything must run **locally, on CPU, with zero cloud dependency**. This is being developed and tested purely on a local laptop using the built-in webcam.

## 2. Problem Statement

Driver fatigue and cognitive distraction contribute to over 20% of fatal road crashes worldwide. Existing solutions are inadequate:

| Approach | Why it fails |
|---|---|
| Wearable biosensors (EEG / smart eyewear) | Physical discomfort, skin irritation, driver resistance on long shifts |
| End-to-end deep CNNs | Need heavy GPU servers, excessive power draw, can't run on budget dashboard CPUs |
| Cloud-based telematics | Connection dropouts and round-trip latency in rural areas / tunnels |

DriveAlert's answer: compute **dimensionless geometric ratios** from facial landmarks instead of running raw pixel tensors through a deep network. This cuts memory overhead by over 80% versus a CNN pipeline and runs comfortably on a quad-core CPU.

## 3. Objectives

1. Real-time, non-intrusive monitoring using an ordinary RGB cabin webcam (no special sensors).
2. Mathematical landmark ratios (EAR & MAR) to reliably separate involuntary blinks from dangerous micro-sleep.
3. Head-pose estimation to flag visual distraction (looking away from the road for >2.5 seconds).
4. Real-time performance target: **≥30 FPS, <35 ms latency**, on standard edge CPU hardware (Raspberry Pi 4 / Intel i3-class or better), with **zero cloud dependency**.

## 4. Mathematical Formulation (must be implemented exactly)

### 4.1 Eye Aspect Ratio (EAR) — micro-sleep detection

```
EAR = ( ||p2 - p6|| + ||p3 - p5|| ) / ( 2 * ||p1 - p4|| )
```

- `p1..p6` are the six eye-corner/eyelid landmark points (from MediaPipe Face Mesh's 468-point model), following the standard Soukupová & Čech eye-landmark convention.
- Compute EAR per eye and typically average both eyes for a single frame value.
- **Baseline:** a normal, healthy eye blink produces an EAR between **0.28 and 0.35**.
- **Micro-sleep rule:** if EAR **< 0.22** continuously for **45 consecutive frames** (≈1.5 seconds at 30 FPS), fire a **critical acoustic alarm**.
- Use a rolling frame counter, not a single-frame threshold crossing — a single low-EAR frame is a blink, not a micro-sleep event.

### 4.2 Mouth Aspect Ratio (MAR) — yawn detection

```
MAR = ||p_top - p_bottom|| / ||p_left - p_right||
```

- `p_top`/`p_bottom` are vertical mouth-opening landmarks; `p_left`/`p_right` are mouth-corner landmarks.
- **Baseline:** normal talking keeps MAR **< 0.35**.
- **Yawn alert rule:** a sustained mouth opening with MAR **> 0.60** across consecutive frames signals excessive fatigue.

### 4.3 Head Pose Estimation — distraction detection

- Solve **Perspective-n-Point (`cv2.solvePnP`)**, mapping 2D camera landmark points to a generic 3D facial model to compute **Pitch** (head nod) and **Yaw** (looking away).
- **Distraction rule:** if the driver's head is turned away from the windshield corridor for **> 2.5 seconds**, raise a distraction flag/alert.

## 5. Core User Flow

1. **Startup:** Open the default laptop webcam (`cv2.VideoCapture(0)`), initialize MediaPipe Face Mesh, initialize the Pygame audio mixer for non-blocking alerts.
2. **Per-frame loop:**
   - Capture frame → convert BGR→RGB → run Face Mesh → extract the 468 3D landmarks.
   - If no face is detected, handle gracefully (no crash; show "face not detected" state, do not evaluate ratios on stale/missing landmarks).
   - Compute EAR (both eyes), MAR, and head pose (pitch/yaw) from the landmarks.
   - Update rolling counters/timers for each rule (micro-sleep frame counter, yawn frame counter, distraction duration timer).
   - Evaluate the three rules in §4 against the current counters/timers.
3. **Alerting:**
   - On a fired rule, trigger a threaded/non-blocking Pygame acoustic alarm so audio playback never blocks the capture/inference loop.
   - Reset the relevant counter after the alert fires (or after eyes/mouth/head return to normal) to avoid a continuous alarm lock-up.
4. **On-screen feedback (dev/test mode):** draw landmark overlays, live EAR/MAR values, FPS counter, and current alert state on the video window — this is essential for local testing/tuning since there is no vehicle dashboard yet.
5. **Shutdown:** clean release of the camera and destroy OpenCV windows on exit (`q` key or window close).

## 6. Local Laptop Testing Constraints

Since this is being developed and tested **purely on a local laptop with the built-in webcam** (not the target Raspberry Pi / dashboard hardware yet), the following constraints apply:

- **Camera source:** always the laptop's built-in webcam via OpenCV's default device index (`0`). No IP cameras, no video file simulation unless explicitly requested for regression testing.
- **No GPU assumption:** code must not assume CUDA/GPU availability. MediaPipe's CPU-based Face Mesh is the target; do not add GPU-only code paths.
- **Performance target while testing:** aim for the same ≥30 FPS / <35 ms/frame target on a standard laptop CPU (Intel i5-class or better) as a proxy for the Raspberry Pi 4 target — this validates the "runs on modest edge CPU" claim before real hardware is available.
- **Lighting/webcam variability:** built-in laptop webcams are lower quality and more light-sensitive than a dedicated dashboard camera — thresholds may need runtime calibration/logging during testing rather than being treated as immutably fixed.
- **No internet dependency during a test run:** the app must run with Wi-Fi off to validate the "zero cloud dependency" claim.
- **Audio alerts:** must work through the laptop's built-in speakers via Pygame; no external buzzer hardware yet.
- **Calibration mode (recommended addition):** a short per-user calibration step (measure resting EAR/MAR for ~5 seconds) is useful on a laptop where lighting/face geometry varies more than in a fixed vehicle mount — flag this as a future/optional enhancement, not a change to the fixed thresholds in §4 unless the user explicitly asks for adaptive thresholds.

## 7. Target Performance (from research results — for reference, not laptop-guaranteed)

| Metric | Result | Baseline | Outcome |
|---|---|---|---|
| Micro-sleep detection accuracy | 94.6% | >90.0% | Exceeds |
| Yawn detection accuracy | 92.8% | >88.0% | Exceeds |
| Distraction detection accuracy | 91.4% | >85.0% | Exceeds |
| Inference latency/frame | 29.4 ms | <40.0 ms | Real-time edge capable |
| Frame throughput (CPU only) | 32–35 FPS | ≥24 FPS | Fluid real-time |
| False alarm rate | 3.2% | <5.0% | High reliability |

## 8. Tech Stack (fixed — see `.cursorrules` for enforcement)

- Python 3.9+
- OpenCV 4.8 (image I/O, drawing, camera capture)
- Google MediaPipe Face Mesh (468-point landmark extraction)
- Pygame (threaded, non-blocking acoustic alerts)
- No cloud APIs, no heavy deep-learning frameworks (no PyTorch/TensorFlow CNN pipelines) — the entire value proposition is lightweight geometric-ratio computation, not learned inference.

## 9. Future Scope (not in current build)

- Near-infrared (NIR) illuminators for nocturnal driving.
- CAN-bus integration for autonomous speed throttling.
- Deployment target: Raspberry Pi 4 / Intel i3-class dashboard hardware (post laptop-validation).
