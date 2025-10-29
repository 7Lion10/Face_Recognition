import face_recognition
import numpy as np
import pickle
import os

DB_PATH = "database/known_faces.pkl"


def load_database():
    db_path = os.path.join("database", "known_faces.pkl")
    if not os.path.exists(db_path):
        # Return an empty dictionary if file doesn't exist yet
        return {}
    with open(db_path, "rb") as f:
        try:
            return pickle.load(f)
        except Exception:
            # If file is empty or corrupted, return empty
            return {}


def save_database(data):
    """Save known faces to pickle file."""
    with open(DB_PATH, "wb") as f:
        pickle.dump(data, f)


def add_face(name, image_path):
    """Add a new person's face to the database."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return False  # No face found

    db = load_database()
    db[name] = encodings[0]
    save_database(db)
    return True


def recognize_face(image_path):
    """Recognize the face from uploaded image."""
    db = load_database()
    if not db:
        return "No faces in database yet", 0.0

    unknown_img = face_recognition.load_image_file(image_path)
    unknown_encodings = face_recognition.face_encodings(unknown_img)

    if len(unknown_encodings) == 0:
        return "No face detected", 0.0

    unknown_enc = unknown_encodings[0]
    names = list(db.keys())
    known_encs = list(db.values())

    distances = face_recognition.face_distance(known_encs, unknown_enc)
    min_distance = np.min(distances)
    best_match = names[np.argmin(distances)]

    if min_distance < 0.5:
        return best_match, 1 - min_distance
    else:
        return "Unknown", 0.0
def rename_face(old_name, new_name, image_path):
    import pickle, os
    db_path = "database/known_faces.pkl"

    if not os.path.exists(db_path):
        return False

    with open(db_path, "rb") as f:
        db = pickle.load(f)

    # Update the name if found
    if old_name in db:
        db[new_name] = db.pop(old_name)
        with open(db_path, "wb") as f:
            pickle.dump(db, f)
        return True
    return False
