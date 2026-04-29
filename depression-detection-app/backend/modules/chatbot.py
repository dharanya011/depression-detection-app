"""
Mental Health Chatbot Module
Empathetic AI chatbot for mental health support conversations
"""

import random

class MentalHealthChatbot:
    """Empathetic chatbot for mental health support"""
    
    EMOTIONAL_RESPONSES = {
        'sad': {
            'keywords': ['sad', 'down', 'unhappy', 'miserable', 'empty', 'broken'],
            'responses': [
                'I hear you. It\'s okay to feel sad sometimes. 💙 What\'s troubling you?',
                'I\'m sorry you\'re feeling down. I\'m here to listen. Tell me more.',
                'Sadness is a natural emotion. You\'re not alone in this feeling.',
                'It takes courage to acknowledge these feelings. I\'m grateful you shared. What can I do to help?'
            ]
        },
        'anxious': {
            'keywords': ['anxious', 'worried', 'nervous', 'afraid', 'panic', 'overwhelmed'],
            'responses': [
                'Anxiety can feel overwhelming. Let\'s take a breath together. 🫁',
                'Your worries matter. Would a grounding exercise help right now?',
                'It\'s normal to feel anxious. Let\'s work through this together.',
                'I\'m here for you. Why don\'t you tell me what\'s making you feel this way?'
            ]
        },
        'stressed': {
            'keywords': ['stressed', 'stress', 'pressure', 'overwhelmed', 'exhausted', 'burnt out'],
            'responses': [
                'You sound stressed. Remember, you\'re stronger than you think. 💪',
                'Stress is a sign you\'re dealing with a lot. Let\'s talk about it.',
                'It\'s okay to feel overwhelmed. Breaking things down helps. What\'s bothering you most?',
                'Burnout is real. You deserve rest and care. How can we help?'
            ]
        },
        'happy': {
            'keywords': ['happy', 'great', 'wonderful', 'amazing', 'excited', 'joyful'],
            'responses': [
                'That\'s wonderful to hear! 🎉 Tell me more about what\'s making you happy!',
                'Your happiness is inspiring! What brought this joy into your life?',
                'I love hearing this! Keep spreading these positive vibes! ✨',
                'Amazing! Hold onto these good feelings and let them fuel you forward!'
            ]
        },
        'lonely': {
            'keywords': ['lonely', 'alone', 'isolated', 'disconnected', 'left out'],
            'responses': [
                'Loneliness is painful, but you\'re not truly alone. I\'m here. 💙',
                'Feeling isolated is tough. Would you like to talk about connecting with others?',
                'You deserve connection. What\'s preventing you from reaching out?',
                'Loneliness can be addressed. Often, the first step is reaching out, just like you did here.'
            ]
        }
    }
    
    DEFAULT_RESPONSES = [
        'I understand. Can you tell me more about how you\'re feeling?',
        'That sounds significant. How has this been affecting you?',
        'I\'m listening. What\'s on your mind?',
        'Thank you for sharing. What do you think would help you feel better?',
        'I appreciate your honesty. How long have you been feeling this way?'
    ]
    
    ENCOURAGING_RESPONSES = {
        'seeking_help': [
            'Reaching out for help is a sign of strength! 💪 I\'m proud of you.',
            'Asking for support is brave. You\'re on the right path.',
            'Seeking help shows self-awareness. That\'s wonderful!',
            'You\'re taking positive steps. I\'m here to support you.'
        ],
        'feeling_better': [
            'I\'m so glad to hear that! 🌟 Keep it up!',
            'That\'s wonderful progress! How are you maintaining this?',
            'Your resilience is inspiring! Keep going!',
            'This is great news! What helped you get here?'
        ],
        'struggling': [
            'It\'s okay to struggle. That\'s part of being human. 💙',
            'Struggles don\'t define you. You have strength within you.',
            'I see your effort. Some days are harder, and that\'s okay.',
            'You\'re not weak for struggling. You\'re strong for trying.'
        ]
    }
    
    def __init__(self):
        """Initialize chatbot"""
        self.conversation_history = []
        self.user_emotional_state = None
    
    def get_response(self, user_message):
        """
        Generate empathetic chatbot response
        
        Args:
            user_message: User's text input
        
        Returns:
            str: Chatbot response
        """
        # Store conversation
        self.conversation_history.append({'user': user_message, 'timestamp': __import__('datetime').datetime.now()})
        
        # Convert to lowercase for processing
        message_lower = user_message.lower()
        
        # Detect emotional keywords
        detected_emotion = self._detect_emotion(message_lower)
        self.user_emotional_state = detected_emotion
        
        # Get contextual response
        if detected_emotion:
            responses = self.EMOTIONAL_RESPONSES[detected_emotion]['responses']
            response = random.choice(responses)
        else:
            response = random.choice(self.DEFAULT_RESPONSES)
        
        # Add follow-up question
        response += '\n\n' + self._get_follow_up(detected_emotion)
        
        return response
    
    def _detect_emotion(self, message):
        """Detect emotion from message"""
        for emotion, details in self.EMOTIONAL_RESPONSES.items():
            for keyword in details['keywords']:
                if keyword in message:
                    return emotion
        return None
    
    def _get_follow_up(self, emotion):
        """Get contextual follow-up question"""
        follow_ups = {
            'sad': '😟 What\'s one person you trust that you could talk to?',
            'anxious': '🫁 Would breathing exercises or grounding techniques help?',
            'stressed': '⏰ What\'s the biggest stressor right now?',
            'happy': '✨ What made this change for you?',
            'lonely': '👥 Would you like to reach out to someone today?',
            None: '💭 What do you think might help right now?'
        }
        
        return follow_ups.get(emotion, follow_ups[None])
    
    def detect_emotional_need(self, message):
        """
        Detect if user has specific emotional needs
        
        Args:
            message: User message
        
        Returns:
            list: Emotional keywords/needs detected
        """
        keywords = []
        message_lower = message.lower()
        
        # Check for specific needs
        crisis_keywords = ['suicide', 'hurt myself', 'death', 'end it', 'harm']
        support_keywords = ['help', 'support', 'talk', 'need assistance']
        
        for keyword in crisis_keywords:
            if keyword in message_lower:
                keywords.append('crisis')
                break
        
        for keyword in support_keywords:
            if keyword in message_lower:
                keywords.append('supports_seeking')
                break
        
        return keywords
    
    def get_encouraging_message(self, context):
        """
        Generate encouraging message based on context
        
        Args:
            context: 'seeking_help', 'feeling_better', 'struggling'
        
        Returns:
            str: Encouraging message
        """
        messages = self.ENCOURAGING_RESPONSES.get(context, [])
        return random.choice(messages) if messages else 'You\'re doing your best, and that\'s enough. 💙'
    
    def get_crisis_response(self):
        """Get immediate crisis support response"""
        return {
            'message': 'Your safety and well-being are my top priority. 🆘',
            'immediate_actions': [
                '📞 Call emergency services if you\'re in immediate danger',
                '☎️ Call 988 (Suicide & Crisis Lifeline) - available 24/7',
                '💬 Text "HELLO" to 741741 (Crisis Text Line)',
                '👥 Tell someone you trust right now'
            ],
            'resources': {
                'National Suicide Prevention Lifeline': '988',
                'Crisis Text Line': 'Text HELLO to 741741',
                'International Association for Suicide Prevention': 'https://www.iasp.info/resources/Crisis_Centres/'
            }
        }
    
    def generate_session_summary(self):
        """
        Generate summary of chat session
        
        Returns:
            dict: Session insights
        """
        if not self.conversation_history:
            return {'summary': 'No conversation yet.', 'emotional_state': 'unknown'}
        
        return {
            'messages_exchanged': len(self.conversation_history),
            'detected_emotion': self.user_emotional_state,
            'session_note': f'User expressed {self.user_emotional_state} emotions during this session.',
            'recommendation': 'Consider exploring deeper with a professional counselor.'
        }
    
    def get_wellness_check_questions(self):
        """Get wellness check-in questions"""
        return [
            '🌅 How are you feeling this morning?',
            '🧠 What\'s taking up most of your mental space today?',
            '💪 What\'s one thing you\'re proud of yourself for?',
            '👥 Who have you connected with recently?',
            '🎯 What\'s one small goal you\'d like to achieve today?'
        ]

# Export class
__all__ = ['MentalHealthChatbot']
