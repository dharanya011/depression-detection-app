/**
 * MindCare - Mental Health Support Platform
 * Main Application JavaScript
 */

const API_BASE = 'http://localhost:5000/api';
let mediaRecorder;
let audioChunks = [];
let recordingStartTime;
let recordingInterval;

// Application State
const app = {
    currentPage: 'home',
    darkMode: false,
    selectedImage: null,
    webcamStream: null,
    conversationHistory: [],

    // Initialize App
    init() {
        console.log('🚀 MindCare initializing...');
        this.loadPreferences();
        this.initializeEventListeners();
        this.loadDashboard('week');
        this.getNewQuote();
        this.loadActivities();
        console.log('✅ MindCare ready!');
    },

    // Navigation
    navigateTo(page) {
        // Hide all pages
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        
        // Show selected page
        const selectedPage = document.getElementById(page);
        if (selectedPage) {
            selectedPage.classList.add('active');
            this.currentPage = page;
            
            // Refresh page-specific content
            if (page === 'dashboard') {
                this.loadDashboard('week');
            }
        }
    },

    switchAnalysisTab(tab) {
        // Hide all analysis sections
        document.querySelectorAll('.analysis-section').forEach(s => s.classList.remove('active'));
        
        // Show selected tab
        const selectedTab = document.getElementById(`${tab}-analysis`);
        if (selectedTab) selectedTab.classList.add('active');
        
        // Update active tab button
        document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
        event.target.classList.add('active');
    },

    // ===== TEXT ANALYSIS =====
    async analyzeText() {
        const text = document.getElementById('textInput').value.trim();
        
        if (!text) {
            alert('Please enter your feelings to analyze');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/analyze/text`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.displayTextResult(result);
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Text analysis error:', error);
            alert('Failed to analyze text');
        }
    },

    displayTextResult(result) {
        const resultCard = document.getElementById('textResult');
        const levelMap = {
            'Low': {'emoji': '😊', 'color': '#4CAF50'},
            'Moderate': {'emoji': '😐', 'color': '#FFC107'},
            'High': {'emoji': '😢', 'color': '#F44336'}
        };

        const level = result.depression_level;
        const levelData = levelMap[level] || {'emoji': '😐', 'color': '#9E9E9E'};

        const html = `
            <div class="result-header">
                <div class="emotion-display" style="background: ${levelData.color}22; color: ${levelData.color}">
                    ${levelData.emoji}
                </div>
                <div class="emotion-info">
                    <h2>${level} Depression Level</h2>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${result.confidence * 100}%; background: ${levelData.color}"></div>
                    </div>
                    <small>${(result.confidence * 100).toFixed(1)}% confidence</small>
                </div>
            </div>

            <div class="result-details">
                <div class="explanation-box">
                    <strong>📊 Assessment:</strong>
                    <p>Based on your text input, the system has classified your current depression indicators as ${level}.</p>
                </div>

                <div style="margin-top: 1rem;">
                    <strong>🔍 Insight:</strong>
                    <p>Our AI analyzes the linguistic patterns, sentiment, and emotional weight of your words to provide this assessment.</p>
                </div>
            </div>
        `;

        document.getElementById('textResultContent').innerHTML = html;
        resultCard.classList.remove('hidden');
    },

    async checkHiddenEmotions(text) {
        // Detect hidden emotions (simple rule-based)
        const indicators = {
            'i am fine': '😟 You said "I am fine" but your words might hide deeper feelings',
            'i am okay': '😟 You said "I am okay" - sometimes we minimize our feelings. It\'s okay to not be okay',
            'nothing is wrong': '😟 Denial detected. Remember, it\'s okay to acknowledge struggles',
            'it is what it is': '😟 Resignation detected. You deserve support and happiness'
        };

        const textLower = text.toLowerCase();
        for (const [phrase, message] of Object.entries(indicators)) {
            if (textLower.includes(phrase)) {
                const alertDiv = document.getElementById('hiddenEmotionAlert');
                alertDiv.textContent = message;
                alertDiv.style.display = 'block';
                document.getElementById('noHiddenEmotion').style.display = 'none';
                break;
            }
        }
    },

    // ===== FACIAL ANALYSIS =====
    async startWebcam() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ 
                video: { width: 640, height: 480 } 
            });
            
            const video = document.getElementById('webcam');
            video.srcObject = stream;
            this.webcamStream = stream;
            
            console.log('Webcam started');
            // Show capture button if in combined mode
            const capBtn = document.getElementById('captureCombinedBtn');
            if (capBtn) capBtn.classList.remove('hidden');
        } catch (error) {
            console.error('Webcam error:', error);
            alert('Could not access webcam. Please check permissions.');
        }
    },

    async startCombinedWebcam() {
        // Switch to analysis tab to see the webcam if needed, 
        // but actually we'll just start it. The user just needs to see the capture button.
        await this.startWebcam();
        document.getElementById('captureCombinedBtn').classList.remove('hidden');
        // Scroll to webcam view so they can see themselves
        document.getElementById('webcam').scrollIntoView({ behavior: 'smooth' });
    },

    stopWebcam() {
        if (this.webcamStream) {
            this.webcamStream.getTracks().forEach(track => track.stop());
            this.webcamStream = null;
            document.getElementById('webcam').srcObject = null;
        }
    },

    captureWebcam() {
        const video = document.getElementById('webcam');
        if (!video.srcObject) {
            alert('Please start the webcam first');
            return;
        }
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        this.selectedImage = canvas.toDataURL('image/jpeg');
        console.log('Webcam image captured');
        
        // Show in preview
        const preview = document.getElementById('facePreview');
        const combinedPreview = document.getElementById('combinedPreview');
        if (preview) {
            preview.src = this.selectedImage;
            document.getElementById('facePreviewContainer').classList.remove('hidden');
        }
        if (combinedPreview) {
            combinedPreview.src = this.selectedImage;
            document.getElementById('combinedPreviewContainer').classList.remove('hidden');
        }

        // If in facial tab, analyze immediately. In combined, let user click Run.
        if (this.currentPage === 'analysis' && document.getElementById('face-analysis').classList.contains('active')) {
            this.analyzeFace();
        } else {
            alert('Image captured successfully! Scroll down to Step 3.');
        }
    },

    handleImageUpload(input) {
        const file = input.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            this.selectedImage = e.target.result;
            // Show preview
            const preview = document.getElementById('facePreview');
            if (preview) {
                preview.src = this.selectedImage;
                document.getElementById('facePreviewContainer').classList.remove('hidden');
            }
        };
        reader.readAsDataURL(file);
    },

    async analyzeFace() {
        if (!this.selectedImage) {
            alert('Please upload or capture an image first');
            return;
        }

        try {
            console.log(this.selectedImage);
            const response = await fetch(`${API_BASE}/analyze/webcam`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ image: this.selectedImage })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.displayFaceResult(result);
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Face analysis error:', error);
            alert('Failed to analyze facial expression');
        }
    },

    displayFaceResult(result) {
        const resultCard = document.getElementById('faceResult');
        const levelMap = {
            'Low': {'emoji': '😊', 'color': '#4CAF50'},
            'Moderate': {'emoji': '😐', 'color': '#FFC107'},
            'High': {'emoji': '😢', 'color': '#F44336'}
        };

        const level = result.depression_level;
        const levelData = levelMap[level] || {'emoji': '😐', 'color': '#9E9E9E'};

        const html = `
            <div class="result-header">
                <div class="emotion-display" style="background: ${levelData.color}22; color: ${levelData.color}">
                    ${levelData.emoji}
                </div>
                <div class="emotion-info">
                    <h2>${level} Depression Level</h2>
                    <p>Detected Emotion: <strong>${this.capitalizeFirst(result.emotion)}</strong></p>
                </div>
            </div>

            <div class="result-details">
                <div class="explanation-box">
                    <strong>📊 Visual Assessment:</strong>
                    <p>Your facial expression suggests a ${level} level of depressive indicators. The primary emotion detected is ${result.emotion}.</p>
                </div>

                <div style="margin-top: 1.5rem; background: rgba(155, 89, 182, 0.05); padding: 1rem; border-radius: 0.5rem;">
                    <strong>💡 How it works:</strong>
                    <p>Our deep learning model analyzes micro-expressions and muscle positioning to identify core emotions, which are then mapped to clinically recognized depression markers.</p>
                </div>
            </div>
        `;

        document.getElementById('faceResultContent').innerHTML = html;
        resultCard.classList.remove('hidden');
    },

    // ===== COMBINED ANALYSIS =====
    handleCombinedImageUpload(input) {
        const file = input.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            this.selectedImage = e.target.result;
            // Show preview
            const preview = document.getElementById('combinedPreview');
            if (preview) {
                preview.src = this.selectedImage;
                document.getElementById('combinedPreviewContainer').classList.remove('hidden');
            }
        };
        reader.readAsDataURL(file);
    },

    async analyzeCombined() {
        const text = document.getElementById('combinedTextInput').value.trim();
        
        if (!text && !this.selectedImage) {
            alert('Please enter text or upload an image');
            return;
        }

        try {
            const response = await fetch(`${API_BASE}/analyze/combined`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    text: text,
                    image: this.selectedImage 
                })
            });

            const result = await response.json();
            
            if (response.ok) {
                this.displayCombinedResult(result);
                this.checkRiskLevel(result.combined_result?.depression_level);
            } else {
                alert('Error: ' + result.error);
            }
        } catch (error) {
            console.error('Combined analysis error:', error);
            alert('Failed to perform combined analysis');
        }
    },

    displayCombinedResult(data) {
        const combined = data.combined_result;
        const resultCard = document.getElementById('combinedResult');
        
        const levelMap = {
            'Low': {'emoji': '😊', 'color': '#4CAF50'},
            'Moderate': {'emoji': '😐', 'color': '#FFC107'},
            'High': {'emoji': '😢', 'color': '#F44336'}
        };

        const level = combined.depression_level;
        const levelData = levelMap[level] || {'emoji': '😐', 'color': '#9E9E9E'};

        const html = `
            <div class="result-header">
                <div class="emotion-display" style="background: ${levelData.color}22; color: ${levelData.color}">
                    ${levelData.emoji}
                </div>
                <div class="emotion-info">
                    <h2>${level} Depression Level</h2>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${combined.confidence * 100}%; background: ${levelData.color}"></div>
                    </div>
                    <small>${(combined.confidence * 100).toFixed(1)}% confidence</small>
                </div>
            </div>

            <div class="result-details">
                <div class="explanation-box">
                    <strong>📊 Final Assessment:</strong>
                    <p>${combined.reasoning}</p>
                </div>

                <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(155, 89, 182, 0.05); border-radius: 0.5rem;">
                    <strong>💡 Analysis Logic:</strong>
                    <p>This result is calculated by averaging the scores from both text-based AI and facial recognition modules (Low=1, Moderate=2, High=3) to provide a more reliable overall assessment.</p>
                </div>
            </div>
        `;

        document.getElementById('combinedResultContent').innerHTML = html;
        document.getElementById('combinedResult').classList.remove('hidden');
    },

    async checkRiskLevel(depressionLevel) {
        if (depressionLevel === 'High') {
            // Show emergency resources
            const response = await fetch(`${API_BASE}/alert/risk-assessment`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ depression_level: depressionLevel })
            });

            if (response.ok) {
                this.showEmergencyAlert();
            }
        }
    },

    // ===== VOICE ANALYSIS =====
    async startVoiceRecording() {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];
            recordingStartTime = Date.now();

            mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
            mediaRecorder.onstart = () => {
                console.log('🎙️ Recording started');
                document.getElementById('stopRecordBtn').classList.remove('hidden');
                this.updateRecordingTime();
                recordingInterval = setInterval(() => this.updateRecordingTime(), 100);
            };

            mediaRecorder.onstop = () => this.processVoiceRecording();
            mediaRecorder.start();
        } catch (error) {
            console.error('Recording error:', error);
            alert('Could not access microphone');
        }
    },

    stopVoiceRecording() {
        if (mediaRecorder) {
            mediaRecorder.stop();
            document.getElementById('stopRecordBtn').classList.add('hidden');
            clearInterval(recordingInterval);
        }
    },

    updateRecordingTime() {
        const elapsed = Math.round((Date.now() - recordingStartTime) / 1000);
        document.getElementById('recordingTime').textContent = `Recording: ${elapsed}s`;
    },

    async processVoiceRecording() {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const formData = new FormData();
        formData.append('audio', audioBlob);

        try {
            const response = await fetch(`${API_BASE}/analyze/voice`, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            if (response.ok) {
                this.displayVoiceResult(result);
            }
        } catch (error) {
            console.error('Voice analysis error:', error);
            alert('Failed to analyze voice');
        }
    },

    displayVoiceResult(result) {
        const emotionMap = {
            'happy': {'emoji': '😊', 'color': '#4CAF50'},
            'sad': {'emoji': '😢', 'color': '#F44336'},
            'neutral': {'emoji': '😐', 'color': '#FFC107'}
        };

        const emotion = result.emotion;
        const emotionData = emotionMap[emotion] || {'emoji': '😐', 'color': '#9E9E9E'};

        const html = `
            <div class="result-header">
                <div class="emotion-display" style="background: ${emotionData.color}22; color: ${emotionData.color}">
                    ${emotionData.emoji}
                </div>
                <div class="emotion-info">
                    <h2>${this.capitalizeFirst(emotion)}</h2>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: ${result.confidence * 100}%; background: ${emotionData.color}"></div>
                    </div>
                    <small>${(result.confidence * 100).toFixed(1)}% confidence</small>
                </div>
            </div>

            <div class="result-details">
                <div style="margin-bottom: 1rem;">
                    <strong>📝 Transcribed Text:</strong>
                    <p style="margin-top: 0.5rem; font-style: italic;">"${result.transcribed_text}"</p>
                </div>

                <div style="margin-bottom: 1rem; padding: 1rem; background: rgba(155, 89, 182, 0.1); border-radius: 0.5rem;">
                    <strong>🔊 Voice Tone Intensity:</strong>
                    <p>${result.tone_intensity}%</p>
                </div>

                <h3>Keywords Detected:</h3>
                <div class="keywords-list">
                    ${result.keywords.map(kw => `<span class="keyword-tag">#${kw}</span>`).join('')}
                </div>
            </div>
        `;

        document.getElementById('voiceResultContent').innerHTML = html;
        document.getElementById('voiceResult').classList.remove('hidden');
    },

    // ===== CHATBOT =====
    async sendChatMessage() {
        const message = document.getElementById('userMessage').value.trim();
        if (!message) return;

        // Add user message to chat
        this.addChatMessage(message, 'user');
        document.getElementById('userMessage').value = '';

        try {
            const response = await fetch(`${API_BASE}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            const result = await response.json();
            if (response.ok) {
                this.addChatMessage(result.response, 'bot');
            }
        } catch (error) {
            console.error('Chat error:', error);
            this.addChatMessage('Sorry, I couldn\'t process that. Please try again.', 'bot');
        }
    },

    sendQuickMessage(message) {
        this.addChatMessage(message, 'user');
        // Auto-send to bot
        this.sendChatMessage();
    },

    addChatMessage(message, sender) {
        const chatMessages = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}-message`;
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${message}</p>
            </div>
        `;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    },

    // ===== MOOD DASHBOARD =====
    async loadDashboard(period) {
        try {
            const response = await fetch(`${API_BASE}/mood/dashboard?period=${period}`);
            const data = await response.json();

            if (response.ok) {
                this.displayDashboardData(data);
            }
        } catch (error) {
            console.error('Dashboard error:', error);
        }
    },

    displayDashboardData(data) {
        // Update statistics
        const stats = data.statistics;
        document.getElementById('lowMoodPercent').textContent = stats.low_mood_percentage + '%';
        document.getElementById('mediumMoodPercent').textContent = stats.medium_mood_percentage + '%';
        document.getElementById('highMoodPercent').textContent = stats.high_mood_percentage + '%';
        document.getElementById('totalEntries').textContent = stats.total_entries;
        document.getElementById('streakNumber').textContent = data.streak + '🔥';

        // Display heatmap
        this.displayHeatmap(data.heatmap);

        // Display trend
        const trendDiv = document.getElementById('moodTrend');
        trendDiv.innerHTML = `
            <div class="trend-message">
                ${data.trends.message}
            </div>
        `;
    },

    displayHeatmap(heatmapData) {
        const heatmapContainer = document.querySelector('.heatmap-container');
        const heatmapGrid = document.createElement('div');
        heatmapGrid.className = 'heatmap-grid';

        heatmapData.forEach(day => {
            const dayDiv = document.createElement('div');
            dayDiv.className = `heatmap-day ${day.depression_level ? day.depression_level.toLowerCase() : 'empty'}`;
            dayDiv.title = `${day.date}: ${day.depression_level || 'No data'}`;
            heatmapGrid.appendChild(dayDiv);
        });

        heatmapContainer.innerHTML = '';
        heatmapContainer.appendChild(heatmapGrid);
    },

    async dailyCheckin() {
        try {
            const response = await fetch(`${API_BASE}/mood/checkin`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ mood_level: 'checked' })
            });

            const result = await response.json();
            alert(result.message);
            this.loadDashboard('week');
        } catch (error) {
            console.error('Check-in error:', error);
        }
    },

    // ===== THERAPY ZONE =====
    startBreathingExercise(type) {
        const visualizer = document.getElementById('breathingVisualizer');
        const instruction = document.getElementById('breathingInstruction');
        
        let cycle = 0;
        let step = 0;
        
        const exercises = {
            '4-7-8': [
                { duration: 4, text: 'Breathe In...' },
                { duration: 7, text: 'Hold...' },
                { duration: 8, text: 'Breathe Out...' }
            ],
            'box': [
                { duration: 4, text: 'Breathe In...' },
                { duration: 4, text: 'Hold...' },
                { duration: 4, text: 'Breathe Out...' },
                { duration: 4, text: 'Hold...' }
            ]
        };

        const exercise = exercises[type];
        if (!exercise) return;

        const runExercise = () => {
            if (cycle >= 4) {
                instruction.textContent = 'Exercise Complete! 🎉';
                return;
            }

            const currentStep = exercise[step % exercise.length];
            instruction.textContent = currentStep.text;

            setTimeout(() => {
                step++;
                if (step % exercise.length === 0) cycle++;
                runExercise();
            }, currentStep.duration * 1000);
        };

        runExercise();
    },

    async getNewQuote() {
        try {
            const response = await fetch(`${API_BASE}/therapy/quotes`);
            const data = await response.json();
            
            if (data.success) {
                document.getElementById('quoteText').textContent = data.quote;
            }
        } catch (error) {
            console.error('Quote fetch error:', error);
        }
    },

    async loadActivities() {
        const list = document.getElementById('activitiesList');
        list.innerHTML = `
            <div class="activity-item">
                <div class="activity-emoji">🚶</div>
                <div class="activity-info">
                    <h4>Take a Walk</h4>
                    <p>Get fresh air and movement</p>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-emoji">🎵</div>
                <div class="activity-info">
                    <h4>Listen to Music</h4>
                    <p>Your mood-boosting playlist</p>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-emoji">📚</div>
                <div class="activity-info">
                    <h4>Read or Journal</h4>
                    <p>Express your thoughts</p>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-emoji">👥</div>
                <div class="activity-info">
                    <h4>Call a Friend</h4>
                    <p>Connect with someone you trust</p>
                </div>
            </div>
            <div class="activity-item">
                <div class="activity-emoji">🧘</div>
                <div class="activity-info">
                    <h4>Meditate</h4>
                    <p>Find your inner peace</p>
                </div>
            </div>
        `;
    },

    playMusic(type) {
        const musicNames = {
            'piano': '🎹 Calm Piano',
            'nature': '🌊 Nature Sounds',
            'ambient': '🌙 Ambient Meditation'
        };
        alert(`Now playing: ${musicNames[type]}\n\n(In production, this would stream actual music)`);
    },

    // ===== MODALS & ALERTS =====
    showEmergencyAlert() {
        document.getElementById('emergencyAlert').classList.remove('hidden');
    },

    closeEmergencyAlert() {
        document.getElementById('emergencyAlert').classList.add('hidden');
    },

    async showPrivacy() {
        try {
            const response = await fetch(`${API_BASE}/privacy`);
            const data = await response.json();

            let html = '<div class="privacy-content">';
            
            if (data.privacy_policy) {
                html += '<div class="privacy-section">';
                html += '<h3>🔒 Your Data is Safe</h3>';
                Object.entries(data.privacy_policy).forEach(([key, value]) => {
                    html += `<p><strong>${key}:</strong> ${value}</p>`;
                });
                html += '</div>';
            }

            if (data.disclaimer) {
                html += '<div class="privacy-section">';
                html += '<h3>⚠️ Important Disclaimer</h3>';
                html += `<p>${data.disclaimer}</p>`;
                html += '</div>';
            }

            if (data.emergency) {
                html += '<div class="privacy-section">';
                html += '<h3>🆘 Emergency Resources</h3>';
                html += `<p><strong>Call:</strong> ${data.emergency.call}</p>`;
                html += `<p><strong>Text:</strong> ${data.emergency.text}</p>`;
                html += '</div>';
            }

            html += '</div>';

            document.getElementById('privacyContent').innerHTML = html;
            document.getElementById('privacyModal').classList.remove('hidden');
        } catch (error) {
            console.error('Privacy fetch error:', error);
        }
    },

    closePrivacyModal() {
        document.getElementById('privacyModal').classList.add('hidden');
    },

    closeModal() {
        document.getElementById('resultModal').classList.add('hidden');
    },

    // ===== THEME & PREFERENCES =====
    toggleTheme() {
        this.darkMode = !this.darkMode;
        document.body.classList.toggle('dark-mode');
        this.savePreferences();
        
        const icon = document.querySelector('.theme-toggle i');
        icon.classList.toggle('fa-moon');
        icon.classList.toggle('fa-sun');
    },

    loadPreferences() {
        const prefs = JSON.parse(localStorage.getItem('mindcarePrefs')) || {};
        
        if (prefs.darkMode) {
            this.darkMode = true;
            document.body.classList.add('dark-mode');
            document.querySelector('.theme-toggle i').classList.remove('fa-moon');
            document.querySelector('.theme-toggle i').classList.add('fa-sun');
        }
    },

    savePreferences() {
        const prefs = {
            darkMode: this.darkMode
        };
        localStorage.setItem('mindcarePrefs', JSON.stringify(prefs));
    },

    // ===== UTILITIES =====
    capitalizeFirst(str) {
        return str.charAt(0).toUpperCase() + str.slice(1);
    },

    initializeEventListeners() {
        // Enter key in text inputs
        document.getElementById('textInput')?.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.analyzeText();
            }
        });

        document.getElementById('userMessage')?.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                this.sendChatMessage();
            }
        });

        // Initialize app
        document.addEventListener('DOMContentLoaded', () => this.init());
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => app.init());
