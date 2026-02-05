"""
Multi-stage Log Classification Orchestrator

This module coordinates the classification pipeline using multiple methods:
1. Regex-based classification (fast, pattern-matching)
2. BERT-based classification (ML-based, for complex patterns)
3. LLM-based classification (for legacy systems - TODO)

Author: Your Name
Date: February 2026
"""

from processor_regex import classify_with_regex
from processor_bert import classify_with_bert


# ==================== CLASSIFICATION PIPELINE ====================
def classify_logs(source, log_msg):
    """
    Classify a log message using a multi-stage pipeline.
    
    Classification strategy:
    1. If source is "LegacyCRM": Use LLM-based classification (TODO)
    2. Try regex-based classification first (fast)
    3. If regex fails, fall back to BERT-based classification
    
    Args:
        source (str): The source system of the log (e.g., "ModernCRM", "LegacyCRM")
        log_msg (str): The log message to classify
        
    Returns:
        str: The classification label
    """
    # Special handling for legacy CRM logs
    if source == "LegacyCRM":
        # TODO: Implement LLM-based classification
        # For now, fall through to standard classification
        pass
    
    # Stage 1: Try regex-based classification (fast)
    label = classify_with_regex(log_msg)
    
    # Stage 2: If regex didn't match, use BERT-based classification
    if label is None:
        label = classify_with_bert(log_msg)
    
    return label


def classify_batch(logs):
    """
    Classify multiple logs in batch.
    
    Args:
        logs (list): List of tuples (source, log_msg)
        
    Returns:
        list: List of tuples (source, log_msg, label)
    """
    results = []
    for source, log_msg in logs:
        label = classify_logs(source, log_msg)
        results.append((source, log_msg, label))
    return results


# ==================== TESTING ====================
if __name__ == "__main__":
    # Sample test logs from different sources
    test_logs = [
        ("ModernCRM", "User User123 logged in."),
        ("ModernCRM", "Backup started at 2026-02-05 10:00:00."),
        ("ModernCRM", "Backup completed successfully."),
        ("AnalyticsEngine", "System updated to version 1.0.0."),
        ("AnalyticsEngine", "File data_123.csv uploaded successfully by user 123."),
        ("ModernHR", "Disk cleanup completed successfully."),
        ("ModernHR", "System reboot initiated by user 123."),
        ("BillingSystem", "Account with ID 123 created by user 123."),
        ("BillingSystem", "Hey bro chill yaa"),  # Should use BERT
        ("LegacyCRM", "Critical system failure detected"),  # Should use LLM (TODO)
    ]
    
    print("=" * 100)
    print("MULTI-STAGE LOG CLASSIFICATION PIPELINE")
    print("=" * 100)
    
    for source, log_msg in test_logs:
        label = classify_logs(source, log_msg)
        print(f"[{source:20}] {log_msg:<50} --> {label}")
    
    print("=" * 100)