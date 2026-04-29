"""
Face Detection Module
Performs facial expression analysis for depression level detection using FER library.
"""

import cv2
import numpy as np
import base64
from io import BytesIO
from PIL import Image
import os
import sys

class FaceDetector:
    """Detect depression levels from facial expressions using FER"""
    
    # Emotion to Depression Level mapping
    EMOTION_MAP = {
        'happy': 'Low',
        'neutral': 'Moderate',
        'surprise': 'Moderate',
        'sad': 'High',
        'angry': 'High',
        'fear': 'High',
        'disgust': 'High'
    }
    
    def __init__(self):
        """Initialize face detector"""
        self.detector = None
        self.face_cascade = None
        self._initialize_detector()
        
    def _initialize_detector(self):
        """Lazy load FER detector"""
        print("Initializing FaceDetector...")
        try:
            from fer import FER
            # mtcnn=False is more reliable in many environments
            self.detector = FER(mtcnn=False)
            print("✅ FER detector initialized successfully.")
        except Exception as e:
            print(f"❌ Error initializing FER: {e}")
            self.detector = None
            
        # Always load Haar Cascade as a secondary fallback
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            if self.face_cascade.empty():
                print("❌ Failed to load Haar Cascade.")
            else:
                print("✅ Haar Cascade loaded as fallback.")
        except Exception as e:
            print(f"❌ Error loading Haar Cascade: {e}")

    def predict_face(self, frame):
        """
        Analyze frame and predict depression level
        """
        if frame is None:
            print("Received empty frame for prediction.")
            return None
            
        if self.detector:
            try:
                results = self.detector.detect_emotions(frame)
                if results:
                    # Get the most dominant emotion from the first detected face
                    emotions = results[0]['emotions']
                    dominant_emotion = max(emotions, key=emotions.get)
                    confidence = emotions[dominant_emotion]
                    
                    depression_level = self.EMOTION_MAP.get(dominant_emotion, 'Moderate')
                    print(f"Face detected: {dominant_emotion} ({depression_level}) with {confidence:.2f} confidence.")
                    
                    return {
                        'emotion': dominant_emotion,
                        'depression_level': depression_level,
                        'confidence': round(float(confidence), 2)
                    }
                else:
                    print("No face detected by FER.")
            except Exception as e:
                print(f"FER detection runtime error: {e}")
                
        # Fallback if FER is not available, fails, or finds no face
        return self._fallback_detect(frame)

    def _fallback_detect(self, frame):
        """Fallback rule-based detection using Haar Cascades"""
        if self.face_cascade is None or self.face_cascade.empty():
            return None

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        if len(faces) == 0:
            print("No face detected by Fallback Haar Cascade.")
            return None
            
        print("Face detected by Fallback Haar Cascade. Mapping to Moderate.")
        return {
            'emotion': 'neutral',
            'depression_level': 'Moderate',
            'confidence': 0.5
        }

    def detect_emotion(self, image_file):
        """Process uploaded image file"""
        try:
            img_stream = image_file.read()
            nparr = np.frombuffer(img_stream, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return self.predict_face(frame)
        except Exception as e:
            print(f"Error processing image file: {e}")
            return None

    def detect_emotion_from_base64(self, image_base64):
        """Process Base64 encoded image"""
        try:
            if ';' in image_base64 and ',' in image_base64:
                image_base64 = image_base64.split(',')[1]
            
            img_data = base64.b64decode(image_base64)
            nparr = np.frombuffer(img_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return self.predict_face(frame)
        except Exception as e:
            print(f"Error processing base64 image: {e}")
            return None

# Export class
__all__ = ['FaceDetector']
