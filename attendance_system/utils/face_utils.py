import cv2
import face_recognition
import numpy as np
from PIL import Image
import io

class FaceDetector:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_faces(self, frame):
        """Detect faces in a frame and return the face locations"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def draw_faces(self, frame, faces):
        """Draw rectangles around detected faces"""
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return frame
    
    def get_face_encodings(self, frame):
        """Get face encodings from a frame"""
        # Convert BGR to RGB (face_recognition uses RGB)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find all face locations and encodings
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        return face_locations, face_encodings
    
    def compare_faces(self, known_encodings, face_encoding, tolerance=0.6):
        """Compare a face encoding with a list of known encodings"""
        if not known_encodings or not face_encoding:
            return False, -1
        
        # Convert list to numpy array if needed
        if isinstance(known_encodings, list):
            known_encodings = np.array(known_encodings)
        
        # Compare faces and return the closest match
        matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=tolerance)
        face_distances = face_recognition.face_distance(known_encodings, face_encoding)
        
        if not any(matches):
            return False, -1
        
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            return True, best_match_index
        
        return False, -1
    
    def resize_frame(self, frame, width=None, height=None):
        """Resize a frame while keeping aspect ratio"""
        if width is None and height is None:
            return frame
        
        h, w = frame.shape[:2]
        if width is None:
            ratio = height / float(h)
            dim = (int(w * ratio), height)
        else:
            ratio = width / float(w)
            dim = (width, int(h * ratio))
        
        resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
        return resized
    
    def image_to_bytes(self, image):
        """Convert an OpenCV image to bytes"""
        is_success, buffer = cv2.imencode(".jpg", image)
        if is_success:
            return buffer.tobytes()
        return None
    
    def bytes_to_image(self, bytes_data):
        """Convert bytes to an OpenCV image"""
        if not bytes_data:
            return None
        
        npimg = np.frombuffer(bytes_data, np.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        return image 