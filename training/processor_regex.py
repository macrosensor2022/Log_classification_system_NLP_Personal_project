"""
Regex-based Log Classification Module

This module uses regular expression pattern matching to quickly classify 
common log message patterns. It's faster than ML-based methods for 
well-defined patterns.

Author: Your Name
Date: February 2026
"""

import re


# ==================== CLASSIFICATION FUNCTION ====================
def classify_with_regex(log_message):
    """
    Classify a log message using regex pattern matching.
    
    This is the first step in the classification pipeline. It quickly 
    identifies logs that match known patterns. If no pattern matches,
    returns None to indicate the log should be classified by other methods.
    
    Args:
        log_message (str): The log message to classify
        
    Returns:
        str or None: The classification label if matched, None otherwise
        
    Patterns matched:
        - User login/logout actions
        - System notifications (backups, updates, file uploads, etc.)
        - System maintenance operations
    """
    # Dictionary of regex patterns and their corresponding labels
    # Key: regex pattern, Value: classification label
    regex_patterns = {
        # User Actions
        r"User User\d+ logged (in|out).": "User Action",
        r"Account with ID .* created by .*": "User Action",
        
        # System Notifications
        r"Backup (started|ended) at .*": "System Notification",
        r"Backup completed successfully.": "System Notification",
        r"System updated to version .*": "System Notification",
        r"File .* uploaded successfully by user .*": "System Notification",
        r"Disk cleanup completed successfully.": "System Notification",
        r"System reboot initiated by user .*": "System Notification",
    }
    
    # Check each pattern against the log message
    for pattern, label in regex_patterns.items():
        # Case-insensitive matching
        if re.search(pattern, str(log_message), re.IGNORECASE):
            return label
    
    # No pattern matched - return None for downstream processing
    return None


# ==================== TESTING ====================
if __name__ == "__main__":
    # Test cases for regex classification
    test_logs = [
        "User User123 logged in.",
        "Backup started at 2026-02-05 10:00:00.",
        "Backup completed successfully.",
        "System updated to version 1.0.0.",
        "File data_123.csv uploaded successfully by user 123.",
        "Disk cleanup completed successfully.",
        "System reboot initiated by user 123.",
        "Account with ID 123 created by user 123.",
        "User User123 logged out.",
        "Backup ended at 2026-02-05 10:00:00.",
        "System updated to version 1.0.1.",
        "File data_124.csv uploaded successfully by user 124.",
        "Disk cleanup completed successfully.",
        "Hey bro chill yaa"  # Should return None
    ]
    
    print("=" * 80)
    print("REGEX-BASED LOG CLASSIFICATION RESULTS")
    print("=" * 80)
    
    for log in test_logs:
        result = classify_with_regex(log)
        status = result if result else "No Match (None)"
        print(f"{log:<60} --> {status}")
    
    print("=" * 80)