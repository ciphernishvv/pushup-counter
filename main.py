import cv2
import time
import os
from posedetector import PoseDetector
from counter import PushUpCounter
 
# mediapipe landmark IDs we need
# full list: https://developers.google.com/mediapipe/solutions/vision/pose_landmarker
LEFT_SHOULDER  = 11
LEFT_ELBOW     = 13
LEFT_WRIST     = 15
RIGHT_SHOULDER = 12
RIGHT_ELBOW    = 14
RIGHT_WRIST    = 16
 
 
def draw_angle_arc(frame, point, angle, color=(255, 255, 0)):
    # draw a small circle at joint to show angle
    cv2.circle(frame, point, 20, color, 2)
    cv2.putText(frame, f"{int(angle)}", (point[0] - 20, point[1] - 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
 
 
def draw_ui(frame, count, status, posture_msg, elapsed_time, angle):
    h, w = frame.shape[:2]
 
    # dark semi transparent bar at top
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 80), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
 
    # push-up count - big text top left
    cv2.putText(frame, f"Push-ups: {count}", (15, 55),
                cv2.FONT_HERSHEY_DUPLEX, 1.6, (0, 255, 100), 2)
 
    # timer top right
    mins = int(elapsed_time // 60)
    secs = int(elapsed_time % 60)
    timer_str = f"Time: {mins:02d}:{secs:02d}"
    cv2.putText(frame, timer_str, (w - 220, 45),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
 
    # status bar at bottom
    overlay2 = frame.copy()
    cv2.rectangle(overlay2, (0, h - 70), (w, h), (0, 0, 0), -1)
    cv2.addWeighted(overlay2, 0.5, frame, 0.5, 0, frame)
 
    # up / down status
    status_color = (0, 255, 0) if status == "UP POSITION" else (0, 140, 255)
    cv2.putText(frame, status, (15, h - 35),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, status_color, 2)
 
    # posture message on the right side of bottom bar
    if posture_msg:
        msg_color = (0, 255, 0) if "Good" in posture_msg else (0, 0, 255)
        cv2.putText(frame, posture_msg, (w - 280, h - 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, msg_color, 2)
 
    # angle value small indicator
    cv2.putText(frame, f"Elbow Angle: {int(angle)}", (15, h - 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
 
    return frame
 
 
def save_session(count, correct, incorrect, workout_time):
    filename = "workout_log.txt"
    mins = int(workout_time // 60)
    secs = int(workout_time % 60)
 
    with open(filename, "a") as f:
        from datetime import datetime
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write("=" * 40 + "\n")
        f.write(f"Date & Time   : {now}\n")
        f.write(f"Total Push-ups: {count}\n")
        f.write(f"Good Form Reps: {correct}\n")
        f.write(f"Needs Work    : {incorrect}\n")
        f.write(f"Workout Time  : {mins:02d}:{secs:02d}\n")
        f.write("=" * 40 + "\n\n")
 
    print(f"\n[INFO] Session saved to {os.path.abspath(filename)}")
 
 
def main():
    print("Starting AI Push-Up Counter...")
    print("Press 'q' to quit | Press 'r' to reset counter\n")
 
    cap = cv2.VideoCapture(0)
 
    # try to set resolution - wont crash if webcam doesnt support it
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
 
    if not cap.isOpened():
        print("[ERROR] Cannot open webcam. Check if it's connected.")
        return
 
    detector = PoseDetector()
    counter  = PushUpCounter()
 
    start_time    = time.time()
    posture_msg   = ""
    posture_timer = 0     # how long to show posture message
    current_angle = 0
 
    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Frame not received. Exiting...")
            break
 
        # flip frame so it acts like a mirror - more intuitive
        frame = cv2.flip(frame, 1)
 
        # run pose detection
        frame = detector.find_pose(frame)
        landmarks = detector.get_landmarks(frame)
 
        if landmarks:
            # pick whichever side has better visibility (higher confidence)
            l_vis = landmarks[LEFT_ELBOW][3]
            r_vis = landmarks[RIGHT_ELBOW][3]
 
            if l_vis > r_vis:
                # use left arm
                shoulder = [landmarks[LEFT_SHOULDER][1], landmarks[LEFT_SHOULDER][2]]
                elbow    = [landmarks[LEFT_ELBOW][1],    landmarks[LEFT_ELBOW][2]]
                wrist    = [landmarks[LEFT_WRIST][1],    landmarks[LEFT_WRIST][2]]
            else:
                # use right arm
                shoulder = [landmarks[RIGHT_SHOULDER][1], landmarks[RIGHT_SHOULDER][2]]
                elbow    = [landmarks[RIGHT_ELBOW][1],    landmarks[RIGHT_ELBOW][2]]
                wrist    = [landmarks[RIGHT_WRIST][1],    landmarks[RIGHT_WRIST][2]]
 
            current_angle = detector.calculate_angle(shoulder, elbow, wrist)
 
            # draw angle at elbow
            draw_angle_arc(frame, tuple(elbow), current_angle)
 
            # update counter with new angle
            count, status, new_msg, counted = counter.update(current_angle)
 
            if counted:
                posture_msg   = new_msg
                posture_timer = 60  # show message for ~2 seconds at 30fps
        else:
            status = "No pose detected"
            count  = counter.count
 
        # countdown posture message display
        if posture_timer > 0:
            posture_timer -= 1
        else:
            posture_msg = ""
 
        elapsed = time.time() - start_time
 
        # draw all UI elements
        frame = draw_ui(frame, count, status, posture_msg, elapsed, current_angle)
 
        cv2.imshow("AI Push-Up Counter | press Q to quit", frame)
 
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            counter.reset()
            start_time = time.time()
            print("[INFO] Counter reset!")
 
    # save session before closing
    elapsed_total = time.time() - start_time
    save_session(counter.count, counter.correct_reps, counter.incorrect_reps, elapsed_total)
 
    print(f"\n--- Workout Summary ---")
    print(f"Total Push-ups : {counter.count}")
    print(f"Good Form Reps : {counter.correct_reps}")
    print(f"Needs Work     : {counter.incorrect_reps}")
    mins = int(elapsed_total // 60)
    secs = int(elapsed_total % 60)
    print(f"Workout Time   : {mins:02d}:{secs:02d}")
 
    cap.release()
    cv2.destroyAllWindows()
 
 
if __name__ == "__main__":
    main()