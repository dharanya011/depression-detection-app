"""
Text Analysis Module
Performs NLP-based depression detection from text input using trained Logistic Regression model.
"""

import os
import pickle
import re
from datetime import datetime

class TextAnalyzer:
    """Analyze text for depression levels using trained ML model"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.models_loaded = False
        self._load_model()
        
    def _load_model(self):
        """Load the pickled model and vectorizer"""
        try:
            # Adjust path to find the models directory relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            backend_dir = os.path.dirname(current_dir)
            models_dir = os.path.join(backend_dir, 'models')
            
            model_path = os.path.join(models_dir, 'text_model.pkl')
            vectorizer_path = os.path.join(models_dir, 'vectorizer.pkl')
            
            if os.path.exists(model_path) and os.path.exists(vectorizer_path):
                with open(model_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(vectorizer_path, 'rb') as f:
                    self.vectorizer = pickle.load(f)
                self.models_loaded = True
                print("Text analysis models loaded successfully.")
            else:
                print(f"Warning: Model files not found in {models_dir}")
        except Exception as e:
            print(f"Error loading text models: {str(e)}")

    def _preprocess(self, text):
        """Clean and preprocess text"""
        text = text.lower()
        # Remove special characters
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        return text

    def analyze(self, text):
        """
        Analyze text and predict depression level
        
        Args:
            text (str): Input text from user
            
        Returns:
            dict: {depression_level, confidence, explanation}
        """
        if not text or not text.strip():
            return {
                'depression_level': 'Low',
                'confidence': 0.0,
                'explanation': 'No text provided'
            }

        if not self.models_loaded:
            # Fallback if model failed to load
            return self._fallback_analyze(text)

        # Preprocess
        clean_text = self._preprocess(text)
        
        # Vectorize
        vectorized_text = self.vectorizer.transform([clean_text])
        
        # Predict
        prediction = self.model.predict(vectorized_text)[0]
        
        # Get confidence (probability)
        probabilities = self.model.predict_proba(vectorized_text)[0]
        confidence = float(max(probabilities))
        
        # Map labels to match user request (case sensitivity)
        level_map = {
            'Low': 'Low',
            'Moderate': 'Moderate',
            'High': 'High'
        }
        
        depression_level = level_map.get(prediction, prediction)
        
        return {
            'depression_level': depression_level,
            'confidence': round(confidence, 2),
            'explanation': f"Analysis based on linguistic patterns suggests a {depression_level} level of concern."
        }

    def _fallback_analyze(self, text):
        """Simple keyword-based fallback if ML model is unavailable"""
        text_lower = text.lower()
        
        high_risk = ['hopeless', 'suicide', 'kill', 'end it', 'depressed', 'worthless']
        moderate_risk = ['sad', 'stressed', 'anxious', 'tired', 'worried', 'struggling']
        
        if any(word in text_lower for word in high_risk):
            return {'depression_level': 'High', 'confidence': 0.5, 'explanation': 'Fallback: High risk keywords detected'}
        elif any(word in text_lower for word in moderate_risk):
            return {'depression_level': 'Moderate', 'confidence': 0.5, 'explanation': 'Fallback: Moderate risk keywords detected'}
        else:
            return {'depression_level': 'Low', 'confidence': 0.5, 'explanation': 'Fallback: No specific risk indicators found'}

    def transcribe_audio(self, audio_file):
        """Placeholder for audio transcription"""
        return "I am feeling quite overwhelmed and sad lately"

    def analyze_tone(self, audio_file):
        """Placeholder for audio tone analysis"""
        return 65

# Export class
__all__ = ['TextAnalyzer']
