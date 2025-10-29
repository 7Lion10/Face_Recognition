import cv2
import numpy as np
import face_recognition
import os
import time

# 🔹 Load known faces
path = 'images'
known_encodings = []
known_names = []

print("🧠 Loading known faces...")
for file in os.listdir(path):
    if file.lower().endswith(('jpg', 'jpeg', 'png')):
        img_path = os.path.join(path, file)
        img = face_recognition.load_image_file(img_path)
        encodings = face_recognition.face_encodings(img)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(os.path.splitext(file)[0])
            print(f"✅ Loaded: {file}")
        else:
            print(f"⚠️ No face found in {file}")

print(f"\n📸 Total known faces: {len(known_encodings)}\n")

# 🔹 Start webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open camera.")
    exit()

print("🎥 Press 'q' to quit.\n")

# 🔹 Define smooth color transition for aesthetics
color1 = np.array([0, 255, 255])   # Cyan
color2 = np.array([255, 0, 255])   # Pink
transition_speed = 2.0

while True:
    ret, frame = cap.read()
    if not ret:
        print("⚠️ Frame not captured, skipping...")
        continue

    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    # Detect faces
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    # 🔹 Smooth gradient color animation
    t = (time.time() * transition_speed) % 1
    current_color = (color1 * (1 - t) + color2 * t).astype(int)
    box_color = (int(current_color[0]), int(current_color[1]), int(current_color[2]))

    if len(face_encodings) == 0:
        cv2.putText(frame, "No face detected 😕", (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    else:
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(known_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_names[best_match_index]

            # Scale back to original frame size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # 🔹 Draw stylish face box with gradient color
            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 3)
            overlay = frame.copy()
            cv2.rectangle(overlay, (left, bottom - 35), (right, bottom), box_color, -1)
            frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

            # 🔹 Add text (stylish)
            cv2.putText(frame, name, (left + 10, bottom - 10), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

    # 🔹 Add translucent banner at bottom
    h, w, _ = frame.shape
    cv2.rectangle(frame, (0, h - 50), (w, h), (20, 20, 20), -1)
    cv2.putText(frame, "Press 'q' to quit | Live Face Recognition Active", (10, h - 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # Show output
    cv2.imshow('✨ Smart Face Recognition', frame)

    # Quit with 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("👋 Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
