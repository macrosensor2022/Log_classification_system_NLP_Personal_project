"""
LLM-based Log Classification Module

This module uses Groq's LLM API to classify complex log messages that don't 
match regex patterns or are from legacy systems. It leverages large language 
models for semantic understanding of log content.

Author: Your Name
Date: February 2026
"""

from groq import Groq
from dotenv import load_dotenv
import os 
from pathlib import Path 

# ==================== ENVIRONMENT SETUP ====================
# Get the directory where this script is located
current_dir = Path(__file__).parent
env_path = current_dir / '.env'

# Load environment variables from .env file (contains GROQ_API_KEY)
load_dotenv(dotenv_path=env_path)

# Initialize Groq client with API key from environment
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))


# ==================== CLASSIFICATION FUNCTION ====================
def classify_with_llm(log_message):
    """
    Classify a log message using Groq's LLM API.
    
    This function is specifically designed for edge cases that regex and BERT
    cannot handle well, such as:
    - Workflow Error: Complex workflow-related failures
    - Deprecation Warning: API or feature deprecation notices
    
    Args:
        log_message (str): The log message to classify
        
    Returns:
        str: The predicted category or "Unclassified" if uncertain
        
    Categories:
        - Workflow Error
        - Deprecation Warning
        - Unclassified (if uncertain)
    """
    # Create a detailed prompt for the LLM
    prompt = f'''Classify the following log message into one of these categories: 
    (1) Workflow Error, (2) Deprecation Warning. 
    
    If you are not sure, return "Unclassified".
    Only return the category name, no other text or explanation.
    
    Log message: {log_message}
    '''
    
    # Call Groq API; model name may change — see https://console.groq.com/docs/models
    response = groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    
    return response.choices[0].message.content


# ==================== TESTING ====================
if __name__ == "__main__":
    # Test cases for LLM classification
    print("=" * 80)
    print("LLM-BASED LOG CLASSIFICATION RESULTS")
    print("=" * 80)
    
    test_logs = [
        "Workflow error: Backup process failed",
        "Deprecation warning: API v1 is deprecated",
        "Unknown log message"
    ]
    
    for log in test_logs:
        result = classify_with_llm(log)
        print(f"{log:<50} --> {result}")
    
    print("=" * 80)