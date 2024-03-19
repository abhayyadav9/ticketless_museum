import cv2
import numpy as np
import mysql.connector


def load_image(image_path):
    """
    Load an image from the given path.
    """
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Unable to read image from {image_path}")
    return image


def detect_faces(image):
    """
    Detect faces in the given image using a pre-trained face detector.
    """
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray_image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces


def compare_with_database(captured_image_path):
    """
    Compare the captured image with images in the database.
    """
    captured_image = load_image(captured_image_path)
    if captured_image is None:
        return False

    captured_faces = detect_faces(captured_image)

    # Connect to the MySQL database
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="formdata")
    cursor = conn.cursor()

    # Retrieve images from the database
    cursor.execute("SELECT picture FROM ticketinfo")
    database_images = [load_image(result[0]) for result in cursor.fetchall()]

    cursor.close()
    conn.close()

    # Compare the captured faces with faces in the database images
    for database_image in database_images:
        database_faces = detect_faces(database_image)
        if len(captured_faces) == len(database_faces):
            return True

    return False
