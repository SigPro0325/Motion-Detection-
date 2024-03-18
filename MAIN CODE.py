import cv2
import numpy as np
import speech_recognition as sr
import threading
import datetime
import geocoder

def save_snapshot(frame, snapshot_counter):
    # Getting current time
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Gets the current location of the user's device when the snapshot is taken
    g = geocoder.ip('me')
    location = g.latlng  # returns (lat, long)

    # Adds text overlay for time and location
    cv2.putText(frame, f"Timestamp: {current_time}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"Location: {location}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    # Saves the snapshot within the folder of which the main code is located. 
    filename = f"snapshot_{snapshot_counter}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Snapshot saved as {filename}")

def listen_for_command(shared_dict):
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        while True:
            try:
                print("Listening for the screenshot command...")
                audio_data = recognizer.listen(source)
                text = recognizer.recognize_google(audio_data)
                if "take screenshot" in text.lower():
                    shared_dict["command"] = "take screenshot"
            except sr.UnknownValueError:
                print("Could not understand the command.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")


# Initializes the webcam and then cascades
video_capture = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
smile_cascade = cv2.CascadeClassifier('haarcascade_smile.xml')

snapshot_counter = 0

# A Shared dictionary to communicate between threads
shared_dict = {"command": None}

listener_thread = threading.Thread(target=listen_for_command, args=(shared_dict,))
listener_thread.daemon = True
listener_thread.start()

while True:
    ret, frame = video_capture.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Face Detection
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Eye Detection
    eyes = eye_cascade.detectMultiScale(gray, 1.1, 5)
    for (ex, ey, ew, eh) in eyes:
        cv2.rectangle(frame, (ex, ey), (ex + ew, ey + eh), (255, 0, 0), 2)

    # Smile Detection
    smiles = smile_cascade.detectMultiScale(gray, 1.8, 20)
    for (sx, sy, sw, sh) in smiles:
        cv2.rectangle(frame, (sx, sy), (sx + sw, sy + sh), (255, 255, 0), 2)

    # Text Overlay within the webcam frame
    cv2.putText(frame, f"Faces detected: {len(faces)}", (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)


    # Checks for the given command 
    if shared_dict["command"] == "take screenshot":
        save_snapshot(frame, snapshot_counter)
        snapshot_counter += 1
        shared_dict["command"] = None

    # Displays the main frame 
    cv2.imshow('Face and Eye Tracking', frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
