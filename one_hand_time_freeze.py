import cv2
import mediapipe as mp
import math

import pyautogui
import time
import webbrowser

# Initialize Mediapipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Define a function to calculate the distance between two points
def calculate_distance(point1, point2):
    return math.hypot(point2[0]-point1[0], point2[1]-point1[1])

# Define a simple gesture recognition function
def recognize_palm(hand_landmarks):
    # Example: Recognize if the hand is showing a fist or open palm
    # We'll check the distance between the tip of the thumb and the base
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_MCP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    thumb_cmc = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_CMC]

    index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
    index_pip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_PIP]
    index_open = index_tip.y < index_pip.y

    middle_tip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
    middle_pip = hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_PIP]
    middle_open = middle_tip.y < middle_pip.y


    ring_tip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_TIP]
    ring_pip = hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_PIP]
    ring_open = ring_tip.y < ring_pip.y


    pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]
    pinky_mcp = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP]
    pinky_pip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP]
    pinky_open = pinky_tip.y < pinky_pip.y

    distance = calculate_distance(
        (thumb_tip.x, thumb_tip.y), 
        (index_tip.x, index_tip.y)
    )

    thumb_distance = calculate_distance((thumb_tip.x, thumb_tip.y), (thumb_mcp.x, thumb_mcp.y))

    side = ""
    if (calculate_distance((pinky_mcp.x, pinky_mcp.y), (thumb_ip.x, thumb_ip.y)) > 0.1):
        if ((thumb_ip.x - thumb_tip.x) > 0.015 and thumb_ip.x < thumb_mcp.x and thumb_mcp.x < thumb_cmc.x):
            side = "Left"
        elif ((thumb_tip.x-thumb_ip.x) > 0.015 and thumb_ip.x > thumb_mcp.x and thumb_mcp.x > thumb_cmc.x):
            side = "Right"

    if (side != "" and thumb_distance > 0.05):
        if (index_open):
            if (middle_open and ring_open and pinky_open):
                    return "Open Palm"
            elif (middle_open and not ring_open and not pinky_open):
                return "Peace"
            elif (not middle_open and not ring_open):
                if (not pinky_open):
                    return side + " Pointer"
                elif (pinky_open):
                    return "Rock On"
        elif (not middle_open and not ring_open and not pinky_open):
            return side + " Thumb"
        elif (distance < 0.05 and middle_open and ring_open and pinky_open):
            return "OK"
    elif (middle_open and index_open and not ring_open and not pinky_open):
        return "Peace"
    elif (index_open and middle_open and ring_open and not pinky_open):
        return "Three"
    elif (distance < 0.05 and middle_open and ring_open and pinky_open):
        return "OK"
    return "unknown"

def main():
    is_first_ok = True
    # Initialize video capture
    cap = cv2.VideoCapture(0)  # 0 is the default webcam

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:

        while cap.isOpened():



            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            # Flip the image horizontally and convert the BGR image to RGB.
            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # To improve performance, optionally mark the image as not writeable to pass by reference.
            image_rgb.flags.writeable = False
            results = hands.process(image_rgb)

            # Draw the hand annotations on the image.
            image_rgb.flags.writeable = True
            image = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # Draw landmarks
                    mp_drawing.draw_landmarks(
                        image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    
                    # Recognize gesture
                    gesture = recognize_palm(hand_landmarks)

                    if is_first_ok and gesture == "OK":
                        webbrowser.open('https://armorgames.com/time-freeze-game/19384', new=2)
                        time.sleep(1)
                        pyautogui.scroll(-10)
                        screenWidth, screenHeight = pyautogui.size()
                        pyautogui.click(screenWidth / 2, screenHeight / 2)
                        is_first_ok = False

                    if gesture == "unknown":
                        pyautogui.keyUp("a")
                        pyautogui.keyUp("w")
                        pyautogui.keyUp("d")
                    elif gesture == "Left Pointer":
                        pyautogui.keyUp("d")
                        pyautogui.keyDown("a")
                        pyautogui.keyDown("w")
                    elif gesture == "Left Thumb":
                        pyautogui.keyUp("w")
                        pyautogui.keyUp("d")
                        pyautogui.keyDown("a")
                    elif gesture == "Right Pointer":
                        pyautogui.keyUp("a")
                        pyautogui.keyDown("d")
                        pyautogui.keyDown("w")
                    elif gesture == "Right Thumb":
                        pyautogui.keyUp("w")
                        pyautogui.keyUp("a")
                        pyautogui.keyDown("d")
                    else:
                        pyautogui.keyUp("d")
                        pyautogui.keyUp("w")
                        pyautogui.keyUp("a")
                        if gesture == "OK":
                            pyautogui.click()
                        elif gesture == "Open Palm":
                            pyautogui.press("e", interval = 0.5)
                        elif gesture == "Rock On":
                            pyautogui.press("r", interval = 1.0)
                        elif gesture == "Three":
                            pyautogui.press("esc", interval = 1.0)

                    
                    #gesture = recognize_ok(hand_landmarks)
                    
                    # Display gesture near hand location
                    """
                    cv2.putText(image, gesture, 
                                (int(hand_landmarks.landmark[0].x * image.shape[1]), 
                                 int(hand_landmarks.landmark[0].y * image.shape[0]) - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                    """
                    
            # Display the resulting image
         

            #cv2.imshow('Gesture Recognition', image)

            if cv2.waitKey(5) & 0xFF == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()