class PushUpCounter:
    def __init__(self):
        self.count = 0
        self.stage = None       # "up" or "down"
        self.correct_reps = 0
        self.incorrect_reps = 0

        # angle thresholds - tuned for push-ups
        self.DOWN_ANGLE = 90    # elbow bent = down position
        self.UP_ANGLE = 160     # elbow straight = up position

        # posture check thresholds
        self.MIN_DOWN_ANGLE = 70   # if angle goes too low, might be bad form
        self.last_min_angle = 180  # track lowest angle in a rep

    def update(self, angle):
        status = ""
        posture_msg = ""
        counted = False

        # detect down position
        if angle < self.DOWN_ANGLE:
            self.stage = "down"
            self.last_min_angle = min(self.last_min_angle, angle)
            status = "DOWN POSITION"

        # detect up position and count rep
        if angle > self.UP_ANGLE and self.stage == "down":
            self.stage = "up"
            self.count += 1
            counted = True

            # simple posture check
            if self.last_min_angle < self.MIN_DOWN_ANGLE:
                posture_msg = "Good Depth!"
                self.correct_reps += 1
            else:
                posture_msg = "Go Lower!"
                self.incorrect_reps += 1

            self.last_min_angle = 180  # reset for next rep

        if self.stage == "up" or self.stage is None:
            status = "UP POSITION"

        return self.count, status, posture_msg, counted

    def get_form_feedback(self, angle):
        # real time feedback while doing the movement
        if angle < 50:
            return "Too Low! Ease up"
        elif angle < self.DOWN_ANGLE:
            return "Hold... push up!"
        elif angle > self.UP_ANGLE:
            return "Arms straight - ready"
        else:
            return "Going down..."

    def reset(self):
        self.count = 0
        self.stage = None
        self.correct_reps = 0
        self.incorrect_reps = 0
        self.last_min_angle = 180