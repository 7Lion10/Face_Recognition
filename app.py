from flask import Flask, render_template, request, redirect, url_for, Response, send_from_directory
import os
import cv2
import time
import face_recognition
import numpy as np
from models.face_model import recognize_face, add_face, rename_face  # Custom functions

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# 📁 Folder paths
UPLOAD_FOLDER = "static/uploads"
KNOWN_FOLDER = "images"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWN_FOLDER, exist_ok=True)

# ==============================
# 🧠 Load known faces
# ==============================
known_encodings = []
known_names = []
print("🧠 Loading known faces...")

for file in os.listdir(KNOWN_FOLDER):
    if file.lower().endswith(('jpg', 'jpeg', 'png')):
        img_path = os.path.join(KNOWN_FOLDER, file)
        img = face_recognition.load_image_file(img_path)
        encs = face_recognition.face_encodings(img)
        if len(encs) > 0:
            known_encodings.append(encs[0])
            known_names.append(os.path.splitext(file)[0])
            print(f"✅ Loaded: {file}")
        else:
            print(f"⚠️ No face found in {file}")

print(f"📸 Total known faces: {len(known_encodings)}")

# ==============================
# 🔹 Routes
# ==============================

@app.route("/")
def index():
    """Home page — shows live camera + upload form"""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    """Handle image upload for recognition"""
    file = request.files.get("image") or request.files.get("file")
    if not file or file.filename == "":
        return redirect(url_for("index"))

    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    name, confidence = recognize_face(filepath)
    return render_template(
        "result.html",
        name=name,
        confidence=round(confidence, 2),
        image=file.filename
    )


@app.route("/add", methods=["POST"])
def add_new_face():
    """Add a new face to the database"""
    name = request.form["name"]
    image = request.form["image"]
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image)

    if add_face(name, image_path):
        message = f"✅ {name} has been added to the database!"
    else:
        message = "❌ No face detected in the image."

    return render_template("message.html", message=message)


@app.route("/rename", methods=["POST"])
def rename_existing_face():
    """Rename an existing face"""
    old_name = request.form["old_name"]
    new_name = request.form["new_name"]
    image = request.form["image"]
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], image)

    if rename_face(old_name, new_name, image_path):
        message = f"✅ Renamed {old_name} to {new_name}!"
    else:
        message = "❌ Could not rename — face not found."

    return render_template("message.html", message=message)


# ==============================
# 🔹 Live Face Recognition Stream
# ==============================
def get_camera():
    """Try to access webcam safely (for local use only)"""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("⚠️ Webcam not accessible (this is normal on Railway).")
        return None
    return cam


camera = get_camera()


def gen_frames():
    """Generate video frames with recognition overlay"""
    if camera is None:
        while True:
            # Send a blank frame or a static image if webcam unavailable
            blank = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(blank, "Webcam not available on Railway 🚫",
                        (40, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            _, buffer = cv2.imencode('.jpg', blank)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        return

    process_every = 3
    frame_count = 0
    last_detected_time = time.time()

    color1 = np.array([0, 255, 255])  # Cyan
    color2 = np.array([255, 0, 255])  # Pink
    transition_speed = 2.0

    while True:
        success, frame = camera.read()
        if not success:
            break

        frame_count += 1
        t = (time.time() * transition_speed) % 1
        current_color = (color1 * (1 - t) + color2 * t).astype(int)
        box_color = tuple(map(int, current_color))

        if frame_count % process_every == 0:
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(known_encodings, face_encoding)
                name = "Unknown"
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)

                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = known_names[best_match_index]
                face_names.append(name)

        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4; right *= 4; bottom *= 4; left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), box_color, 3)
            overlay = frame.copy()
            cv2.rectangle(overlay, (left, bottom - 35), (right, bottom), box_color, -1)
            frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)
            cv2.putText(frame, name, (left + 10, bottom - 10),
                        cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 2)

        if not face_encodings and time.time() - last_detected_time > 10:
            cv2.putText(frame, "No face detected 😕", (40, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, h - 50), (w, h), (20, 20, 20), -1)
        cv2.putText(frame, "Press 'q' to quit | Live Face Recognition Active",
                    (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video feed route"""
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ==============================
# 🔹 Serve Static Files
# ==============================
@app.route('/static/<path:filename>')
def serve_static(filename):
    """Ensure static files load correctly in Docker/Railway"""
    return send_from_directory(app.static_folder, filename)


# ==============================
# 🔹 Run App
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))  # Railway uses dynamic ports
    app.run(host="0.0.0.0", port=port, debug=False)
