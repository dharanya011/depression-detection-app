import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle
import os

# 1. Create Synthetic Dataset
data = {
    'text': [
        # Low
        "I feel happy today", "I'm doing great", "Everything is fine", "I had a wonderful day",
        "Feeling normal and okay", "Life is good", "I am satisfied", "I feel calm",
        "It was a good day", "I am happy with my progress", "I feel energetic",
        "The weather is beautiful", "I enjoy spending time with friends", "I feel motivated",
        "I am looking forward to tomorrow", "I feel peaceful", "Everything is working out",
        "I am grateful for what I have", "I feel healthy", "I'm in a good mood",
        
        # Moderate
        "I feel sad and lonely", "I am very stressed lately", "Feeling anxious about the future",
        "I am worried about my grades", "I feel nervous", "Everything is overwhelming",
        "I am so tired and exhausted", "I feel a bit down", "I'm struggling to focus",
        "I feel restless and uneasy", "I'm not feeling my best today",
        "Work is putting a lot of pressure on me", "I have trouble sleeping because of stress",
        "I feel a bit disconnected", "Everything is just okay, but I feel empty",
        "I'm worried about my health", "I feel a bit insecure today",
        "I'm procrastinating too much", "I feel slightly irritated", "I need a break",
        
        # High
        "I feel hopeless and lost", "I am deeply depressed", "I have suicidal thoughts",
        "I want to give up on everything", "Everything is dark and cold", "No hope for me",
        "I feel worthless and empty", "I can't stop crying", "Life has no meaning",
        "I am in deep despair", "I wish I could just disappear", "I feel completely broken",
        "There is no light at the end of the tunnel", "I hate myself", "I feel like a burden",
        "Nothing matters anymore", "I feel trapped in my own head", "The pain is unbearable",
        "I don't see a point in anything", "I am losing my mind", "I want to end it all"
    ],
    'label': [
        'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low', 'Low',
        'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate', 'Moderate',
        'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High', 'High'
    ]
}

df = pd.DataFrame(data)

# 2. Preprocess (Simple version for training script)
df['text'] = df['text'].str.lower()

# 3. Vectorization
vectorizer = TfidfVectorizer(stop_words='english')
X = vectorizer.fit_transform(df['text'])
y = df['label']

# 4. Train Model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# 5. Print Accuracy
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# 6. Save Model and Vectorizer
models_dir = os.path.join(os.path.dirname(__file__), 'models')
if not os.path.exists(models_dir):
    os.makedirs(models_dir)

with open(os.path.join(models_dir, 'text_model.pkl'), 'wb') as f:
    pickle.dump(model, f)

with open(os.path.join(models_dir, 'vectorizer.pkl'), 'wb') as f:
    pickle.dump(vectorizer, f)

print("Model and vectorizer saved successfully in 'backend/models/'")
