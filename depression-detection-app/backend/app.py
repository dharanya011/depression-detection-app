"""
Main Flask Application for Depression Detection Platform
A comprehensive mental health support system using AI
"""


from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv
import os
import json
from datetime import datetime, timedelta
import sqlite3

# Import custom modules
from modules.text_analysis import TextAnalyzer
from modules.face_detection import FaceDetector
from modules.decision_engine import DecisionEngine
from modules.suggestion_engine import SuggestionEngine
from modules.chatbot import MentalHealthChatbot
from modules.mood_tracker import MoodTracker

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend', static_url_path='/')
app.secret_key = os.getenv('SECRET_KEY', 'depression-detection-secret-2024')

# Enable CORS
CORS(app)

# Initialize AI modules
text_analyzer = TextAnalyzer()
face_detector = FaceDetector()
decision_engine = DecisionEngine()
suggestion_engine = SuggestionEngine()
chatbot = MentalHealthChatbot()
mood_tracker = MoodTracker()

# ==================== DATABASE SETUP ====================
def init_db():
    """Initialize SQLite database for mood tracking"""
    conn = sqlite3.connect('mood_data.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS mood_entries
                 (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  text_emotion TEXT,
                  facial_emotion TEXT,
                  combined_result TEXT,
                  depression_level TEXT,
                  confidence REAL)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS streak_data
                 (user_id TEXT PRIMARY KEY,
                  current_streak INTEGER,
                  last_checkin TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY,
                  timestamp TEXT,
                  feedback TEXT,
                  mood_level TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Serve the main application"""
    return app.send_static_file('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# ==================== TEXT ANALYSIS ENDPOINTS ====================

@app.route('/api/analyze/text', methods=['POST'])
def analyze_text():
    """Analyze text for depression level"""
    try:
        data = request.json
        text = data.get('text', '')
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        # Analyze text
        result = text_analyzer.analyze(text)
        
        # Return exactly what was requested: { depression_level, confidence }
        return jsonify({
            'depression_level': result['depression_level'],
            'confidence': result['confidence']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/voice', methods=['POST'])
def analyze_voice():
    """Analyze voice input"""
    try:
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        
        # Transcribe and analyze
        transcribed_text = text_analyzer.transcribe_audio(audio_file)
        result = text_analyzer.analyze(transcribed_text)
        
        # Add tone analysis
        tone_intensity = text_analyzer.analyze_tone(audio_file)
        
        return jsonify({
            'success': True,
            'transcribed_text': transcribed_text,
            'emotion': result['emotion'],
            'confidence': result['confidence'],
            'tone_intensity': tone_intensity,
            'keywords': result['keywords']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== FACIAL ANALYSIS ENDPOINTS ====================

@app.route('/api/analyze/face', methods=['POST'])
def analyze_face():
    """Analyze facial expression from upload"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        image_file = request.files['image']
        result = face_detector.detect_emotion(image_file)
        
        if not result:
            return jsonify({'error': 'No face detected in image'}), 400
        
        return jsonify({
            'emotion': result['emotion'],
            'depression_level': result['depression_level'],
            'confidence': result.get('confidence', 0.5)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analyze/webcam', methods=['POST'])
def analyze_webcam():
    """Analyze facial expression from webcam capture"""
    try:
        data = request.json
        image_data = data.get('image', '')  # Base64 image
        
        if not image_data:
            return jsonify({'error': 'No image data provided'}), 400
        
        result = face_detector.detect_emotion_from_base64(image_data)
        
        if not result:
            return jsonify({'error': 'No face detected'}), 400
        
        # Return exactly what was requested: { emotion, depression_level }
        return jsonify({
            'emotion': result['emotion'],
            'depression_level': result['depression_level']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/face', methods=['POST'])
def analyze_face_v2():
    file = request.files['image']
    result = face_detector.detect_emotion(file)
    return jsonify(result)

# ==================== COMBINED ANALYSIS ====================

@app.route('/api/analyze/combined', methods=['POST'])
def analyze_combined():
    """Combine text and facial analysis"""
    try:
        data = request.json
        text = data.get('text', '')
        image_data = data.get('image', '')
        
        text_res = text_analyzer.analyze(text) if text else None
        face_res = face_detector.detect_emotion_from_base64(image_data) if image_data else None
        
        if not text_res and not face_res:
            return jsonify({'error': 'Need either text or image'}), 400
            
        combined = decision_engine.make_decision(text_analysis=text_res, facial_analysis=face_res)
        
        # Return exactly what was requested: { combined_result: { depression_level, confidence, reasoning } }
        return jsonify({
            'combined_result': {
                'depression_level': combined['depression_level'],
                'confidence': combined['confidence'],
                'reasoning': combined['reasoning']
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== CHATBOT ENDPOINTS ====================

@app.route('/api/chat', methods=['POST'])
def chat():
    """Chat with AI mental health chatbot"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get chatbot response
        bot_response = chatbot.get_response(user_message)
        
        # Detect emotional need
        emotional_keywords = chatbot.detect_emotional_need(user_message)
        
        return jsonify({
            'success': True,
            'message': user_message,
            'response': bot_response,
            'emotional_keywords': emotional_keywords,
            'suggested_activities': suggestion_engine.get_activities()
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== MOOD TRACKING ====================

@app.route('/api/mood/dashboard', methods=['GET'])
def mood_dashboard():
    """Get mood tracking dashboard data"""
    try:
        period = request.args.get('period', 'week')  # week or month
        
        data = mood_tracker.get_dashboard_data(period)
        
        return jsonify({
            'success': True,
            'mood_entries': data['entries'],
            'statistics': data['statistics'],
            'trends': data['trends'],
            'heatmap': data['heatmap'],
            'current_streak': data['streak']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mood/streak', methods=['GET'])
def get_streak():
    """Get current mood tracking streak"""
    try:
        streak_data = mood_tracker.get_streak()
        return jsonify({'success': True, 'streak': streak_data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mood/checkin', methods=['POST'])
def daily_checkin():
    """Daily mood check-in"""
    try:
        data = request.json
        mood_level = data.get('mood_level')
        
        streak = mood_tracker.update_streak()
        result = {
            'success': True,
            'message': f'Great! You\'ve checked in for {streak} days! 🎉',
            'current_streak': streak
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== THERAPY ZONE ====================

@app.route('/api/therapy/breathing', methods=['GET'])
def breathing_guide():
    """Get breathing exercise guide"""
    return jsonify({
        'success': True,
        'exercises': [
            {
                'name': '4-7-8 Breathing',
                'description': 'Inhale for 4, hold for 7, exhale for 8',
                'duration': 5,
                'steps': [
                    'Find a comfortable position',
                    'Inhale through nose for 4 counts',
                    'Hold breath for 7 counts',
                    'Exhale through mouth for 8 counts',
                    'Repeat 4 times'
                ]
            },
            {
                'name': 'Box Breathing',
                'description': 'Equal breathing pattern for calm focus',
                'duration': 5,
                'steps': [
                    'Inhale for 4 counts',
                    'Hold for 4 counts',
                    'Exhale for 4 counts',
                    'Hold for 4 counts',
                    'Repeat 5 times'
                ]
            }
        ],
        'music_suggestions': [
            {'title': 'Calm Piano', 'duration': '45 min'},
            {'title': 'Nature Sounds', 'duration': '60 min'},
            {'title': 'Ambient Meditation', 'duration': '30 min'}
        ]
    })

@app.route('/api/therapy/quotes', methods=['GET'])
def motivational_quotes():
    """Get motivational quotes"""
    quotes = [
        "You are stronger than you think. 💪",
        "Every small step is progress towards healing. 🌱",
        "Your feelings are valid. Let yourself feel. 💙",
        "This too shall pass. You've overcome before, you will again. 🌟",
        "Be gentle with yourself. You're doing the best you can. 🤍",
        "Your struggle is real, but so is your strength. 💫",
        "One day at a time. That's all you need to do. 📅",
        "Asking for help is a sign of strength, not weakness. 🤝"
    ]
    
    import random
    return jsonify({
        'success': True,
        'quote': random.choice(quotes)
    })

# ==================== RISK ALERT ====================

@app.route('/api/alert/risk-assessment', methods=['POST'])
def risk_assessment():
    """Assess risk and provide alert"""
    try:
        data = request.json
        depression_level = data.get('depression_level', 'Low')
        
        if depression_level == 'High':
            return jsonify({
                'success': True,
                'alert_level': 'HIGH',
                'message': 'Your responses suggest you may need additional support.',
                'recommended_actions': [
                    'Contact a trusted friend or family member',
                    'Speak to a school counselor',
                    'Call a mental health helpline',
                    'Consider speaking with a professional'
                ],
                'emergency_contact': 'National Suicide Prevention Lifeline: 988',
                'show_emergency': True
            })
        
        return jsonify({
            'success': True,
            'alert_level': 'LOW',
            'message': 'You are managing well! Keep prioritizing your mental health.'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/alert/trusted-contact', methods=['POST'])
def send_trusted_contact():
    """Send alert to trusted contact"""
    try:
        data = request.json
        contact_type = data.get('contact_type')  # 'friend', 'family', 'teacher'
        
        # In production, this would integrate with messaging services
        return jsonify({
            'success': True,
            'message': f'Support notification sent to your {contact_type}. You\'re not alone. 💙'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== EXPLAINABLE AI ====================

@app.route('/api/explain/<analysis_type>', methods=['POST'])
def explain_result(analysis_type):
    """Explain AI result with XAI"""
    try:
        data = request.json
        
        explanation = decision_engine.explain_decision(
            analysis_type=analysis_type,
            data=data
        )
        
        return jsonify({
            'success': True,
            'explanation': explanation,
            'contributing_factors': explanation.get('factors', []),
            'reasoning': explanation.get('reasoning', '')
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== PREFERENCES ====================

@app.route('/api/preferences', methods=['GET', 'POST'])
def preferences():
    """Get/set user preferences"""
    if request.method == 'POST':
        data = request.json
        # Store preferences in session
        session.update(data)
        return jsonify({'success': True, 'message': 'Preferences updated'})
    
    return jsonify({
        'dark_mode': session.get('dark_mode', False),
        'notifications': session.get('notifications', True),
        'language': session.get('language', 'en')
    })

# ==================== PRIVACY & SAFETY ====================

@app.route('/api/privacy', methods=['GET'])
def privacy_info():
    """Privacy and safety information"""
    return jsonify({
        'success': True,
        'privacy_policy': {
            'data_storage': 'Minimal session data stored locally. No permanent cloud storage.',
            'encryption': 'All communications are encrypted (HTTPS)',
            'data_sharing': 'Your data is never shared with third parties',
            'consent': 'You control what data is collected',
            'deletion': 'You can delete all data anytime'
        },
        'disclaimer': 'This is NOT a medical diagnosis tool. Seek professional help if needed.',
        'emergency': {
            'text': 'Crisis Text Line: Text HOME to 741741',
            'call': 'National Suicide Prevention Lifeline: 988'
        }
    })

# ==================== FEEDBACK ====================

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback"""
    try:
        data = request.json
        feedback_text = data.get('feedback', '')
        mood_level = data.get('mood_level', '')
        
        mood_tracker.log_feedback(feedback_text, mood_level)
        
        return jsonify({
            'success': True,
            'message': 'Thank you for your feedback! It helps us improve. 💙'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== ERROR HANDLING ====================

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({'error': 'Server error'}), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        threaded=True
    )
