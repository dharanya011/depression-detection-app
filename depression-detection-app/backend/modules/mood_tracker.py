"""
Mood Tracker Module
Tracks daily mood, generates trends, and manages wellness streaks
"""

import sqlite3
from datetime import datetime, timedelta
import json

class MoodTracker:
    """Track and analyze mood patterns"""
    
    def __init__(self, db_path='mood_data.db'):
        self.db_path = db_path
    
    def log_entry(self, text_emotion=None, facial_emotion=None, combined_result=None, depression_level=None, confidence=0):
        """Log a mood entry to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Use provided combined_result or generate a default one
            result_to_log = combined_result if combined_result else f"{text_emotion}+{facial_emotion}"
            
            c.execute('''INSERT INTO mood_entries 
                        (timestamp, text_emotion, facial_emotion, combined_result, depression_level, confidence)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (datetime.now().isoformat(), text_emotion, facial_emotion, 
                      result_to_log, depression_level, confidence))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging entry: {str(e)}")
            return False
    
    def log_feedback(self, feedback_text, mood_level):
        """Log user feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('''INSERT INTO feedback (timestamp, feedback, mood_level)
                        VALUES (?, ?, ?)''',
                     (datetime.now().isoformat(), feedback_text, mood_level))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging feedback: {str(e)}")
            return False
    
    def get_dashboard_data(self, period='week'):
        """
        Get mood dashboard data
        
        Args:
            period: 'week' or 'month'
        
        Returns:
            dict: Dashboard data with entries, statistics, trends, heatmap
        """
        days = 7 if period == 'week' else 30
        
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get entries for period
            start_date = (datetime.now() - timedelta(days=days)).isoformat()
            c.execute('''SELECT timestamp, depression_level, confidence 
                        FROM mood_entries 
                        WHERE timestamp > ?
                        ORDER BY timestamp DESC''', (start_date,))
            
            entries = c.fetchall()
            conn.close()
            
            # Process entries
            mood_entries = []
            depression_counts = {'Low': 0, 'Medium': 0, 'High': 0}
            
            for timestamp, depression_level, confidence in entries:
                mood_entries.append({
                    'timestamp': timestamp,
                    'depression_level': depression_level,
                    'confidence': confidence,
                    'date': timestamp.split('T')[0]
                })
                
                if depression_level:
                    depression_counts[depression_level] = depression_counts.get(depression_level, 0) + 1
            
            # Calculate statistics
            stats = {
                'total_entries': len(entries),
                'average_confidence': round(sum(e[2] for e in entries) / len(entries), 2) if entries else 0,
                'low_mood_percentage': round(depression_counts.get('Low', 0) / len(entries) * 100, 1) if entries else 0,
                'medium_mood_percentage': round(depression_counts.get('Medium', 0) / len(entries) * 100, 1) if entries else 0,
                'high_mood_percentage': round(depression_counts.get('High', 0) / len(entries) * 100, 1) if entries else 0
            }
            
            # Generate heatmap
            heatmap = self._generate_heatmap(mood_entries, days)
            
            # Calculate trends
            trends = self._calculate_trends(entries)
            
            return {
                'entries': mood_entries,
                'statistics': stats,
                'trends': trends,
                'heatmap': heatmap,
                'streak': self.get_streak()
            }
        
        except Exception as e:
            print(f"Error getting dashboard data: {str(e)}")
            return {
                'entries': [],
                'statistics': {},
                'trends': {},
                'heatmap': [],
                'streak': 0
            }
    
    def _generate_heatmap(self, entries, days):
        """Generate heatmap data for calendar view"""
        heatmap = []
        today = datetime.now()
        
        # Create date range
        for i in range(days, -1, -1):
            date = (today - timedelta(days=i)).date()
            
            # Find entry for this date
            day_entry = next((e for e in entries if e['date'] == str(date)), None)
            
            intensity = 0
            if day_entry:
                intensity = 3 if day_entry['depression_level'] == 'Low' else (
                    2 if day_entry['depression_level'] == 'Medium' else 1)
            
            heatmap.append({
                'date': str(date),
                'intensity': intensity,
                'depression_level': day_entry['depression_level'] if day_entry else None
            })
        
        return heatmap
    
    def _calculate_trends(self, entries):
        """Calculate mood trends"""
        if len(entries) < 2:
            return {'direction': 'stable', 'change': 0}
        
        # Check trend direction
        first_half = entries[:len(entries)//2]
        second_half = entries[len(entries)//2:]
        
        first_avg = len([e for e in first_half if e[1] == 'Low']) / len(first_half)
        second_avg = len([e for e in second_half if e[1] == 'Low']) / len(second_half)
        
        change = (second_avg - first_avg) * 100
        
        if change > 10:
            direction = 'improving'
        elif change < -10:
            direction = 'declining'
        else:
            direction = 'stable'
        
        return {
            'direction': direction,
            'change': round(change, 1),
            'message': self._get_trend_message(direction, change)
        }
    
    def _get_trend_message(self, direction, change):
        """Generate human-readable trend message"""
        if direction == 'improving':
            return f'Great! Your mood is improving 📈 (+{abs(change):.1f}%)'
        elif direction == 'declining':
            return f'Your mood shows a slight decline 📉. Consider self-care activities. ({abs(change):.1f}%)'
        else:
            return 'Your mood is stable. Keep maintaining your wellness routine! ✨'
    
    def update_streak(self):
        """Update daily mood check-in streak"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            # Get user ID (using fixed ID for simplicity)
            user_id = 'default_user'
            
            # Check last check-in
            c.execute('SELECT current_streak, last_checkin FROM streak_data WHERE user_id = ?', (user_id,))
            result = c.fetchone()
            
            today = datetime.now().date().isoformat()
            
            if result:
                current_streak, last_checkin = result
                yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
                
                if last_checkin == today:
                    # Already checked in today
                    new_streak = current_streak
                elif last_checkin == yesterday:
                    # Continue streak
                    new_streak = current_streak + 1
                else:
                    # Streak broken
                    new_streak = 1
                
                c.execute('UPDATE streak_data SET current_streak = ?, last_checkin = ? WHERE user_id = ?',
                         (new_streak, today, user_id))
            else:
                new_streak = 1
                c.execute('INSERT INTO streak_data (user_id, current_streak, last_checkin) VALUES (?, ?, ?)',
                         (user_id, new_streak, today))
            
            conn.commit()
            conn.close()
            
            return new_streak
        
        except Exception as e:
            print(f"Error updating streak: {str(e)}")
            return 0
    
    def get_streak(self):
        """Get current streak count"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            
            c.execute('SELECT current_streak FROM streak_data WHERE user_id = ?', ('default_user',))
            result = c.fetchone()
            conn.close()
            
            return result[0] if result else 0
        
        except Exception as e:
            print(f"Error getting streak: {str(e)}")
            return 0
    
    def get_weekly_summary(self):
        """Get weekly mood summary"""
        try:
            dashboard_data = self.get_dashboard_data(period='week')
            
            return {
                'week_summary': f"This week, you had {dashboard_data['statistics']['low_mood_percentage']}% low mood days and "
                              f"{dashboard_data['statistics']['high_mood_percentage']}% high mood days.",
                'streak': dashboard_data['streak'],
                'trend': dashboard_data['trends']['message']
            }
        
        except Exception as e:
            print(f"Error generating summary: {str(e)}")
            return {}
    
    def generate_mood_report(self, days=30):
        """Generate comprehensive mood report"""
        try:
            dashboard_data = self.get_dashboard_data(period='month')
            
            return {
                'period': f'Last {days} days',
                'entries': dashboard_data['entries'],
                'statistics': dashboard_data['statistics'],
                'trends': dashboard_data['trends'],
                'recommendations': self._get_recommendations(dashboard_data['statistics']),
                'generated_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return {}
    
    def _get_recommendations(self, stats):
        """Get personalized recommendations based on statistics"""
        recommendations = []
        
        if stats.get('high_mood_percentage', 0) > 40:
            recommendations.append('You\'ve had many high-mood days. Please reach out for support.')
        
        if stats.get('low_mood_percentage', 0) > 60:
            recommendations.append('Great! You\'ve maintained a positive mood most days. Keep it up!')
        
        if stats.get('average_confidence', 0) < 0.5:
            recommendations.append('Consider more consistent mood tracking for better insights.')
        
        return recommendations if recommendations else ['Keep maintaining your wellness routine! 💙']

# Export class
__all__ = ['MoodTracker']
