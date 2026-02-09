"""
BERT-based Log Classification Module

This module uses a pre-trained sentence transformer model (all-MiniLM-L6-v2) 
to convert log messages into embeddings, which are then classified using 
a Logistic Regression model.

Author: Your Name
Date: February 2026
"""

from sentence_transformers import SentenceTransformer
import numpy as np
import joblib
from pathlib import Path

# ==================== MODEL INITIALIZATION ====================
# Load models once at module level for efficiency
# This prevents reloading the model on every function call

# SentenceTransformer: Converts text to 384-dimensional embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Logistic Regression classifier: Trained on log embeddings
# Use dynamic path to work from any directory
model_path = Path(__file__).parent.parent / 'models' / 'log_classification_model.pkl'
clf = joblib.load(model_path)


# ==================== CLASSIFICATION FUNCTION ====================
def classify_with_bert(log_msg):
    """
    Classify a log message using BERT embeddings and ML model.
    
    Args:
        log_msg (str): The log message to classify
        
    Returns:
        str: The predicted category or "Unclassified" if confidence is low
        
    Categories:
        - User Action
        - System Notification
        - HTTP Status
        - Critical Error
        - Error
        - Security Alert
        - Resource Usage
        - Workflow Error
        - Deprecation Warning
    """
    # Convert log message to embedding (384-dim vector)
    log_embedding = model.encode(log_msg)
    
    # Get prediction probabilities for all classes
    probabilities = clf.predict_proba([log_embedding])[0]
    
    # If confidence is too low (< 50%), return "Unclassified"
    if max(probabilities) < 0.5:
        return "Unclassified"
    
    # Predict the most likely class
    label = clf.predict([log_embedding])[0]
    return label


# ==================== TESTING ====================
if __name__ == "__main__":
    # Sample log messages for testing
    logs = [
        "User User123 logged in.",
        "Backup started at 2026-02-05 10:00:00.",
        "Backup completed successfully.",
        "System updated to version 1.0.0.",
        "File data_123.csv uploaded successfully by user 123.",
        "Disk cleanup completed successfully.",
        "System reboot initiated by user 123.",
        "Account with ID 123 created by user 123.",
        "hey bro chill yaa",
        "Multiple bad login attempts detected on user 8538 account"
    ]
    
    print("=" * 70)
    print("BERT-BASED LOG CLASSIFICATION RESULTS")
    print("=" * 70)
    
    for log in logs:
        label = classify_with_bert(log)
        print(f"{log:<60} --> {label}")
    
    print("=" * 70)




