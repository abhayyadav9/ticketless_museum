import cv2
import numpy as np
import mysql.connector
from skimage.feature import local_binary_pattern

# Load pre-trained face detection model
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Function to connect to the database and retrieve face images
def retrieve_faces_from_database():
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='formdata'
    )
    c = conn.cursor()
    c.execute("SELECT full_name, picture FROM ticketinfo")
    records = c.fetchall()
    conn.close()
    return records


# Function to extract facial features from an image using Local Binary Patterns (LBP)
def extract_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) == 0:
        return None

    # Assuming there's only one face in the image, find the largest face
    (x, y, w, h) = max(faces, key=lambda f: f[2] * f[3])
    face_roi = gray[y:y + h, x:x + w]

    # Apply Local Binary Patterns (LBP)
    radius = 3
    n_points = 8 * radius
    lbp = local_binary_pattern(face_roi, n_points, radius, method='uniform')
    lbp = np.uint8((lbp / np.max(lbp)) * 255)
    hist, _ = np.histogram(lbp.ravel(), bins=np.arange(0, 256), range=(0, 256))
    hist = hist.astype("float")
    hist /= (hist.sum() + 1e-7)

    # Convert histogram to CV_32F type
    hist = hist.astype(np.float32)

    return hist, (x, y, w, h)


# Function to compare faces based on extracted features
def compare_faces(face1, face2):
    # Convert histogram to CV_32F type
    face1 = face1.astype(np.float32)

    # Compute histogram intersection similarity
    similarity = cv2.compareHist(face1, face2, cv2.HISTCMP_INTERSECT)
    return similarity


# Main function to capture video from camera and perform face recognition
def main():
    faces_from_db = retrieve_faces_from_database()
    THRESHOLD = 0.5  # Define your threshold value here

    if not faces_from_db:
        # Display a message on the OpenCV window
        message = "Database is empty."
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.9
        font_color = (36, 255, 12)
        thickness = 2
        text_size = cv2.getTextSize(message, font, font_scale, thickness)[0]
        text_x = (frame.shape[1] - text_size[0]) // 2
        text_y = (frame.shape[0] + text_size[1]) // 2
        cv2.putText(frame, message, (text_x, text_y), font, font_scale, font_color, thickness)
        cv2.imshow('Face Recognition', frame)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        return

    cap = cv2.VideoCapture(0)  # 0 is the default camera

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Extract features from the captured frame
        features = extract_features(frame)
        if features is not None:
            hist1, (x, y, w, h) = features
        else:
            # If no face is detected, skip processing this frame
            continue

        matched_name = None
        for (full_name, db_picture_path) in faces_from_db:
            db_image = cv2.imread(db_picture_path)
            features_db = extract_features(db_image)
            if features_db is not None:
                hist2, _ = features_db
                # Compare faces
                similarity = compare_faces(hist1, hist2)
                # You need to define a threshold for similarity to consider it a match
                if similarity > THRESHOLD:
                    matched_name = full_name
                    break

        if matched_name:
            # If a match is found, display the name on the frame
            cv2.putText(frame, matched_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36, 255, 12), 2)

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
