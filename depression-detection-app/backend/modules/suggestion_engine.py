"""
Suggestion Engine Module
Provides personalized suggestions and activities based on mood
"""

import random

class SuggestionEngine:
    """Generate personalized wellness suggestions"""
    
    SUGGESTIONS_BY_LEVEL = {
        'Low': {
            'activities': [
                {'name': 'Practice gratitude', 'emoji': '🙏', 'icon': 'heart'},
                {'name': 'Share positivity with others', 'emoji': '🤝', 'icon': 'share'},
                {'name': 'Continue meditation', 'emoji': '🧘', 'icon': 'calm'},
                {'name': 'Celebrate small wins', 'emoji': '🎉', 'icon': 'celebrate'}
            ],
            'music': [
                'Uplifting Pop Mix',
                'Feel Good Indie',
                'Motivational Hits',
                'Happy Vibes Playlist'
            ],
            'message': 'You\'re doing great! Keep spreading positive energy! 💫'
        },
        'Medium': {
            'activities': [
                {'name': 'Take a 15-min walk', 'emoji': '🚶', 'icon': 'walk'},
                {'name': 'Journal your thoughts', 'emoji': '📝', 'icon': 'journal'},
                {'name': 'Talk to a friend', 'emoji': '👥', 'icon': 'friend'},
                {'name': 'Try breathing exercise', 'emoji': '🫁', 'icon': 'breath'},
                {'name': 'Listen to calming music', 'emoji': '🎵', 'icon': 'music'},
                {'name': 'Practice yoga', 'emoji': '🧘‍♀️', 'icon': 'yoga'}
            ],
            'music': [
                'Lo-Fi Beats',
                'Ambient Meditation',
                'Calm Piano',
                'Nature Sounds'
            ],
            'message': 'Take care of yourself. These activities can help! 💙'
        },
        'High': {
            'activities': [
                {'name': 'Contact a trusted person', 'emoji': '📞', 'icon': 'call'},
                {'name': 'Talk to a counselor', 'emoji': '👨‍⚕️', 'icon': 'help'},
                {'name': 'Emergency breathing exercise', 'emoji': '🫁', 'icon': 'emergency'},
                {'name': 'Visit a safe space', 'emoji': '🏠', 'icon': 'home'},
                {'name': 'Call crisis helpline', 'emoji': '🆘', 'icon': 'crisis'}
            ],
            'music': [
                'Healing Frequencies',
                'Deep Meditation',
                'Soothing Nature'
            ],
            'message': 'You\'re important. Please reach out to someone you trust. 💙',
            'emergency_resources': [
                '☎️ National Suicide Prevention Lifeline: 988',
                '💬 Crisis Text Line: Text HOME to 741741',
                '🌐 International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/'
            ]
        }
    }
    
    def get_suggestions(self, depression_level):
        """
        Get personalized suggestions based on depression level
        
        Args:
            depression_level: 'Low', 'Medium', or 'High'
        
        Returns:
            dict: suggestions, activities, music, and messages
        """
        suggestions = self.SUGGESTIONS_BY_LEVEL.get(depression_level, {})
        
        if not suggestions:
            return {}
        
        return {
            'depression_level': depression_level,
            'message': suggestions.get('message', ''),
            'suggested_activities': suggestions.get('activities', []),
            'music_suggestions': suggestions.get('music', []),
            'emergency_resources': suggestions.get('emergency_resources', []),
            'personalized_tip': self._get_personalized_tip(depression_level)
        }
    
    def get_activities(self):
        """
        Get a mix of suggested activities
        
        Returns:
            list: curated activities
        """
        all_activities = []
        for level in self.SUGGESTIONS_BY_LEVEL.values():
            all_activities.extend(level.get('activities', []))
        
        # Return 5 random activities
        return random.sample(all_activities, min(5, len(all_activities)))
    
    def _get_personalized_tip(self, depression_level):
        """Generate personalized wellness tip"""
        tips = {
            'Low': random.choice([
                'Your positive energy is contagious! Share it with others. 🌟',
                'Maintain this momentum by keeping up healthy habits.',
                'Remember why you\'re feeling good and protect these feelings.',
                'Use this time to help someone else feel better too!'
            ]),
            'Medium': random.choice([
                'Small changes can have big impacts. Start with one activity.',
                'It\'s okay to feel stressed sometimes. You\'re not alone.',
                'Reaching out for support is a sign of strength, not weakness.',
                'Your feelings are temporary. This too shall pass.'
            ]),
            'High': random.choice([
                'Your safety and well-being are the top priority right now.',
                'Please talk to someone today. You don\'t have to carry this alone.',
                'Professional help can make a real difference. Reach out now.',
                'Every moment you reach out is a step towards feeling better.'
            ])
        }
        
        return tips.get(depression_level, 'Take care of yourself!')
    
    def get_daily_prompt(self):
        """
        Get daily reflection prompt
        
        Returns:
            str: reflection prompt
        """
        prompts = [
            '🤔 What\'s one thing that made you smile today?',
            '💭 Who is someone that makes you feel supported?',
            '🌙 What helps you relax before bed?',
            '🌅 What are you looking forward to tomorrow?',
            '💪 What\'s a challenge you overcame today?',
            '❤️ How can you be kind to yourself today?',
            '🎯 What\'s one goal you made progress on?'
        ]
        
        return random.choice(prompts)
    
    def get_breathing_guide(self):
        """Get detailed breathing exercise guide"""
        return {
            'exercises': [
                {
                    'name': '4-7-8 Breathing',
                    'description': 'Calming breath pattern for anxiety relief',
                    'duration_seconds': 240,
                    'cycles': 4,
                    'steps': [
                        {'instruction': 'Exhale completely through mouth', 'duration': 4},
                        {'instruction': 'Inhale through nose for 4 counts', 'duration': 4},
                        {'instruction': 'Hold breath for 7 counts', 'duration': 7},
                        {'instruction': 'Exhale through mouth for 8 counts', 'duration': 8}
                    ],
                    'benefits': ['Reduces anxiety', 'Promotes sleep', 'Calms mind']
                },
                {
                    'name': 'Box Breathing',
                    'description': 'Equal breathing for focus and calm',
                    'duration_seconds': 300,
                    'cycles': 5,
                    'steps': [
                        {'instruction': 'Inhale for 4 counts', 'duration': 4},
                        {'instruction': 'Hold for 4 counts', 'duration': 4},
                        {'instruction': 'Exhale for 4 counts', 'duration': 4},
                        {'instruction': 'Hold for 4 counts', 'duration': 4}
                    ],
                    'benefits': ['Improves focus', 'Reduces stress', 'Improves mood']
                }
            ]
        }
    
    def get_coping_strategies(self, emotion):
        """
        Get coping strategies for specific emotion
        
        Args:
            emotion: emotion type (sad, anxious, angry, etc.)
        
        Returns:
            list: coping strategies
        """
        strategies = {
            'sad': [
                '📞 Reach out to someone',
                '🎬 Watch your favorite movie or show',
                '🎵 Listen to uplifting music',
                '🚶‍♂️ Go for a walk outside',
                '🎨 Creative expression through art'
            ],
            'anxious': [
                '🫁 Deep breathing exercise',
                '🧘 Progressive muscle relaxation',
                '📝 Write down your worries',
                '🎮 Distract yourself with activities',
                '☕ Take a warm bath or shower'
            ],
            'angry': [
                '💪 Physical exercise',
                '🥊 Punch a pillow',
                '🚶 Take a walk to cool off',
                '📖 Read something calming',
                '🎵 Listen to calming music'
            ],
            'stressed': [
                '🧘‍♀️ Meditation',
                '🏃‍♂️ Exercise',
                '👥 Talk to friends',
                '📝 Organize your thoughts',
                '🎯 Break tasks into smaller steps'
            ]
        }
        
        return strategies.get(emotion, strategies['stressed'])

# Export class
__all__ = ['SuggestionEngine']
