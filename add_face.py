import os
import pickle
import face_recognition

DB_PATH = os.path.join("database", "known_faces.pkl")

def load_database():
    if not os.path.exists(DB_PATH):
        return {}
    with open(DB_PATH, "rb") as f:
        try:
            return pickle.load(f)
        except Exception:
            return {}

def save_database(db):
    with open(DB_PATH, "wb") as f:
        pickle.dump(db, f)

def add_face(name, image_path):
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return

    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        print("⚠️ No face detected in the image.")
        return

    face_encoding = encodings[0]

    db = load_database()
    db[name] = face_encoding
    save_database(db)
    print(f"✅ Added {name} to database.")

if __name__ == "__main__":
    # Example usage
    # Change these to your image paths and names
    add_face("Sudeep", "images/sudeep.jpg")
    add_face("Aishwarya", "images/aishwarya.jpg")
