import cv2
import mediapipe as mp
import time
from Hill_Climb.index_directkeys import up_pressed, down_pressed, PressKey, ReleaseKey  

# Key definitions
open_palm_key = up_pressed
closed_palm_key = down_pressed

time.sleep(2.0)
current_key_pressed = set()

# MediaPipe setup
mp_draw = mp.solutions.drawing_utils
mp_hand = mp.solutions.hands

tipIds = [4, 8, 12, 16, 20]

# Video capture
video = cv2.VideoCapture(0)

with mp_hand.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
    while True:
        keyPressed = False
        ret, image = video.read()
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results = hands.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        lmList = []
        if results.multi_hand_landmarks:
            for hand_landmark in results.multi_hand_landmarks:
                myHands = results.multi_hand_landmarks[0]
                for id, lm in enumerate(myHands.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])
                mp_draw.draw_landmarks(image, hand_landmark, mp_hand.HAND_CONNECTIONS)
        fingers = []
        if len(lmList) != 0:
            if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
                fingers.append(1)
            else:
                fingers.append(0)
            for id in range(1, 5):
                if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            total = fingers.count(1)
            if total == 5:  # Open palm
                cv2.rectangle(image, (20, 300), (270, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(image, "UP", (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
                PressKey(open_palm_key)
                current_key_pressed.add(open_palm_key)
                keyPressed = True
            elif total == 0:  # Closed palm
                cv2.rectangle(image, (20, 300), (270, 425), (0, 255, 0), cv2.FILLED)
                cv2.putText(image, "DOWN", (45, 375), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 0, 0), 5)
                PressKey(closed_palm_key)
                current_key_pressed.add(closed_palm_key)
                keyPressed = True
        if not keyPressed and len(current_key_pressed) != 0:
            for key in current_key_pressed:
                ReleaseKey(key)
            current_key_pressed = set()
        cv2.imshow("Frame", image)
        k = cv2.waitKey(1)
        if k == ord('q'):
            break
video.release()
cv2.destroyAllWindows()
