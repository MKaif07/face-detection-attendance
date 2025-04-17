import cv2
import numpy as np
from PIL import Image
import io
import os
import pickle

class FaceDetector:
    def __init__(self):
        # Load the pre-trained Haar cascade classifier for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        # Use LBPH recognizer for face recognition - simpler than dlib/face_recognition
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.trained = False
        
        # Try to load a pre-trained model if it exists
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models', 'lbph_model.yml')
        if os.path.exists(model_path):
            try:
                self.recognizer.read(model_path)
                self.trained = True
            except:
                self.trained = False
    
    def detect_faces(self, frame):
        """Detect faces in a frame and return the face locations"""
        if frame is None:
            return []
            
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces
    
    def draw_faces(self, frame, faces):
        """Draw rectangles around detected faces"""
        if frame is None:
            return frame
            
        frame_copy = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(frame_copy, (x, y), (x+w, y+h), (255, 0, 0), 2)
        return frame_copy
    
    def extract_face(self, frame, face_location):
        """Extract a face from a frame and preprocess it for recognition"""
        if frame is None or len(face_location) != 4:
            return None
            
        x, y, w, h = face_location
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        face_roi = gray[y:y+h, x:x+w]
        
        # Resize to standard size
        face_roi = cv2.resize(face_roi, (100, 100))
        
        # Apply histogram equalization for better recognition in different lighting
        face_roi = cv2.equalizeHist(face_roi)
        
        return face_roi
    
    def get_face_encodings(self, frame):
        """Get face locations and return preprocessed faces for recognition"""
        faces = self.detect_faces(frame)
        
        # Preprocess each detected face
        face_samples = []
        for face_location in faces:
            face = self.extract_face(frame, face_location)
            if face is not None:
                face_samples.append(face)
        
        return faces, face_samples
    
    def train_recognizer(self, faces, labels):
        """Train the face recognizer with labeled face samples"""
        if not faces or not labels or len(faces) != len(labels):
            return False
            
        # Train LBPH recognizer
        self.recognizer.train(faces, np.array(labels))
        self.trained = True
        
        # Save the model
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'models')
        os.makedirs(model_path, exist_ok=True)
        self.recognizer.write(os.path.join(model_path, 'lbph_model.yml'))
        
        return True
    
    def compare_faces(self, known_encodings, face_encoding, tolerance=70):
        """Compare a face with known faces and return the closest match"""
        if not self.trained or face_encoding is None:
            return False, -1
        
        try:
            # Predict the face using LBPH
            label, confidence = self.recognizer.predict(face_encoding)
            
            # Lower confidence is better in LBPH (unlike face_recognition)
            if confidence < tolerance:
                return True, label
            
        except Exception as e:
            print(f"Error in face comparison: {e}")
            pass
            
        return False, -1
    
    def prepare_faces_for_training(self, face_data):
        """Prepare face data for training the recognizer"""
        faces = []
        labels = []
        
        for student_id, face_pkl in face_data:
            if face_pkl:
                try:
                    # Unpack the face data stored in the database
                    face_img = pickle.loads(face_pkl)
                    
                    # For LBPH, we need grayscale images
                    if isinstance(face_img, np.ndarray):
                        if len(face_img.shape) == 3 and face_img.shape[2] == 3:
                            # Convert color image to grayscale
                            face_gray = cv2.cvtColor(face_img, cv2.COLOR_BGR2GRAY)
                            # Resize to standard size
                            face_gray = cv2.resize(face_gray, (100, 100))
                            faces.append(face_gray)
                            labels.append(student_id)
                except Exception as e:
                    print(f"Error preparing face: {e}")
                    continue
        
        return faces, labels
    
    def resize_frame(self, frame, width=None, height=None):
        """Resize a frame while keeping aspect ratio"""
        if frame is None or (width is None and height is None):
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
        if image is None:
            return None
            
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
    
    def save_face(self, face):
        """Save a face for later use with training"""
        if face is None:
            return None
            
        # Simply return the face image as numpy array
        # In a real system, you might want to apply feature extraction
        return face 