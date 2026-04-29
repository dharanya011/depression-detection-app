"""
Decision Engine Module
Combines text and facial analysis results into a final depression classification.
"""

class DecisionEngine:
    """Combines multiple analysis inputs to determine depression level"""
    
    LEVEL_SCORES = {
        'Low': 1,
        'Moderate': 2,
        'High': 3
    }
    
    SCORE_TO_LEVEL = {
        1: 'Low',
        2: 'Moderate',
        3: 'High'
    }

    def __init__(self):
        pass

    def make_decision(self, text_analysis=None, facial_analysis=None):
        """
        Combine text and face scores
        
        Algorithm:
        1. Convert levels to score: Low=1, Moderate=2, High=3
        2. Average score = (text_score + face_score) / 2
        3. Final classification:
           score >= 2.5 -> High
           score >= 1.5 -> Moderate
           else -> Low
        """
        text_score = 1
        face_score = 1
        
        if text_analysis:
            text_score = self.LEVEL_SCORES.get(text_analysis.get('depression_level', 'Low'), 1)
        
        if facial_analysis:
            face_score = self.LEVEL_SCORES.get(facial_analysis.get('depression_level', 'Low'), 1)
            
        # If only one is provided, we use it as the score (or we could default the other to 1)
        # The user's formula implies both are present, but we should be robust.
        if text_analysis and facial_analysis:
            combined_score = (text_score + face_score) / 2
        elif text_analysis:
            combined_score = float(text_score)
        elif facial_analysis:
            combined_score = float(face_score)
        else:
            combined_score = 1.0

        # Determine level based on combined score
        if combined_score >= 2.5:
            final_level = 'High'
        elif combined_score >= 1.5:
            final_level = 'Moderate'
        else:
            final_level = 'Low'

        # Calculate confidence
        # Simple confidence: if both agree, higher confidence. 
        # If they disagree, lower confidence.
        base_confidence = 0.8
        if text_analysis and facial_analysis:
            if text_score == face_score:
                base_confidence = 0.95
            elif abs(text_score - face_score) == 1:
                base_confidence = 0.85
            else:
                base_confidence = 0.7
        
        # Reasoning
        reasoning = self._generate_reasoning(text_analysis, facial_analysis, final_level)

        return {
            'depression_level': final_level,
            'confidence': base_confidence,
            'reasoning': reasoning,
            'text_score': text_score,
            'face_score': face_score,
            'combined_score': combined_score
        }

    def _generate_reasoning(self, text, face, final_level):
        if not text and not face:
            return "No data provided for analysis."
        
        reasons = []
        if text:
            reasons.append(f"Text analysis indicates {text['depression_level']} concern")
        if face:
            reasons.append(f"Facial expression shows {face.get('emotion', 'unknown')} ({face['depression_level']})")
            
        if text and face:
            if text['depression_level'] == face['depression_level']:
                return f"Both text and face indicate {final_level} distress. " + " ".join(reasons)
            else:
                return f"Combined analysis suggests {final_level} concern. " + " - ".join(reasons)
        
        return " - ".join(reasons)

    def explain_decision(self, analysis_type, data):
        """Simple explanation generator for XAI compatibility"""
        return {
            'reasoning': data.get('reasoning', 'No reasoning provided.'),
            'factors': [
                {'factor': 'Text Score', 'impact': data.get('text_score', 0)},
                {'factor': 'Face Score', 'impact': data.get('face_score', 0)}
            ]
        }

# Export class
__all__ = ['DecisionEngine']
