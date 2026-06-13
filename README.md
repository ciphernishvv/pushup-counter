Project Overview

This project uses your laptop's webcam to detect and count push-ups in real time.
It uses MediaPipe to detect your body pose, tracks your elbow angle, and automatically
counts a push-up every time you complete a full up → down → up cycle.

---

##  Project Structure
```
Pushup_Counter/
│
├── main.py           → Main app. Opens webcam, runs the loop, draws UI
├── pose_detector.py  → Handles MediaPipe pose detection & angle calculation
├── counter.py        → Push-up counting logic and posture checking
├── requirements.txt  → All pip packages needed
└── README.md         → This file
```

---
##  Controls
| Key | Action |
|-----|--------|
| `Q` | Quit the app |
| `R` | Reset counter and timer |

---

##  What Gets Saved
When you press Q to quit, the app saves a **workout_log.txt** file in the same folder with:
- Total push-up count
- Good form reps vs needs-work reps
- Workout duration

---
