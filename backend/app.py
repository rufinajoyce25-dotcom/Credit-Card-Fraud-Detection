from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import cv2
import os
import numpy as np

app = Flask(__name__)
CORS(app)

# -----------------------------
# LOAD DATASET
# -----------------------------
try:
    data = pd.read_csv("../dataset/transactions.csv")
    print("Dataset loaded successfully")
except Exception as e:
    print("Dataset error:", e)
    data = pd.DataFrame(columns=["name", "password", "amount", "is_fraud"])

# -----------------------------
# FACES DIRECTORY
# -----------------------------
FACES_DIR = "faces"
os.makedirs(FACES_DIR, exist_ok=True)

# -----------------------------
# FACE CASCADE
# -----------------------------
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
)

# -----------------------------
# FACE REGISTRATION (CROPPED)
# -----------------------------
def register_face(name):
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not accessible")
        return False

    print("Capturing face for registration...")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        print("No face detected")
        return False

    (x, y, w, h) = faces[0]
    face = gray[y:y+h, x:x+w]
    face = cv2.resize(face, (200, 200))

    file_path = os.path.join(FACES_DIR, f"{name.replace(' ', '_')}.jpg")
    cv2.imwrite(file_path, face)

    print("Face saved at:", file_path)
    return True

# -----------------------------
# FACE VERIFICATION (LBPH)
# -----------------------------
def verify_face(name):
    file_path = os.path.join(FACES_DIR, f"{name.replace(' ', '_')}.jpg")

    print("Looking for file:", file_path)

    if not os.path.exists(file_path):
        print("No registered face found")
        return False

    stored_face = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Camera not accessible")
        return False

    print("Verifying face...")

    ret, frame = cap.read()
    cap.release()

    if not ret:
        return False

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    if len(faces) == 0:
        print("No face detected in live image")
        return False

    (x, y, w, h) = faces[0]
    live_face = gray[y:y+h, x:x+w]
    live_face = cv2.resize(live_face, (200, 200))

    # -----------------------------
    # LBPH RECOGNIZER
    # -----------------------------
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    recognizer.train([stored_face], np.array([1]))

    label, confidence = recognizer.predict(live_face)

    print("Confidence:", confidence)

    # Lower confidence = better match
    if confidence < 60:
        return True

    return False

# -----------------------------
# STRICT FRAUD CHECK
# -----------------------------
def check_fraud_strict(name, password, amount):
    user_data = data[
        (data['name'].str.lower() == name.lower()) &
        (data['password'] == password) &
        (data['amount'] == amount)
    ]

    if user_data.empty:
        return True  # Fraud

    return False  # Safe

# -----------------------------
# REGISTER API
# -----------------------------
@app.route('/register', methods=['POST'])
def register():
    req = request.get_json()

    name = req.get('name')
    password = req.get('password')

    if not name or not password:
        return jsonify({
            "status": "error",
            "message": "Name and password required"
        })

    # Check user exists in dataset
    user = data[
        (data['name'].str.lower() == name.lower()) &
        (data['password'] == password)
    ]

    if user.empty:
        return jsonify({
            "status": "failed",
            "message": "Invalid credentials"
        })

    success = register_face(name)

    if success:
        return jsonify({
            "status": "success",
            "message": "Face registered successfully"
        })

    return jsonify({
        "status": "failed",
        "message": "Face registration failed"
    })

# -----------------------------
# TRANSACTION API
# -----------------------------
@app.route('/transaction', methods=['POST'])
def transaction():

    req = request.get_json()

    name = req.get('name')
    password = req.get('password')
    amount = req.get('amount')

    # -----------------------------
    # VALIDATION
    # -----------------------------
    if not name or not password or not amount:
        return jsonify({
            "status": "error",
            "message": "Missing input fields"
        })

    try:
        amount = float(amount)
    except:
        return jsonify({
            "status": "error",
            "message": "Invalid amount"
        })

    # -----------------------------
    # STEP 1: FACE VERIFICATION
    # -----------------------------
    face_verified = verify_face(name)

    if not face_verified:
        return jsonify({
            "status": "fraud",
            "message": "🚨 Face mismatch detected"
        })

    # -----------------------------
    # STEP 2: STRICT DATA CHECK
    # -----------------------------
    fraud = check_fraud_strict(name, password, amount)

    if fraud:
        return jsonify({
            "status": "fraud",
            "message": "🚨 Data mismatch - suspicious transaction"
        })

    # -----------------------------
    # SAFE TRANSACTION
    # -----------------------------
    return jsonify({
        "status": "safe",
        "message": "✅ Transaction verified successfully"
    })

# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)