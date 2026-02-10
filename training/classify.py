"""
Multi-stage Log Classification Orchestrator

This module coordinates the classification pipeline using multiple methods:
1. Regex-based classification (fast, pattern-matching)
2. BERT-based classification (ML-based, for complex patterns)
3. LLM-based classification (for legacy systems - TODO)

Author: Your Name
Date: February 2026
"""
import pandas as pd
from processor_regex import classify_with_regex
from processor_bert import classify_with_bert

from processor_llm import classify_with_llm

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
    # LegacyCRM logs use the LLM for semantic understanding (workflow/deprecation edge cases)
    if source == "LegacyCRM":
        label = classify_with_llm(log_msg)
    else:
        # Fast path: try regex first; if no match, use BERT embeddings + Logistic Regression
        label = classify_with_regex(log_msg)
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


def classify_csv(input_file):
    """
    Classify logs from a CSV file and save results.
    
    Args:
        input_file (str): Path to input CSV file with columns 'source' and 'log_message'
    """
    df = pd.read_csv(input_file)
    logs = list(zip(df["source"], df["log_message"]))
    results = classify_batch(logs)
    df["target_label"] = [label for _, _, label in results]
    # Write from project root; path is relative when run from training/
    output_file = "resources/output.csv"
    df.to_csv(output_file, index=False)
    print(f"Classification complete. Results saved to {output_file}")
# ==================== TESTING ====================
if __name__ == "__main__":
    print("=" * 100)
    print("MULTI-STAGE LOG CLASSIFICATION PIPELINE")
    print("=" * 100)
    
    # Classify logs from CSV file
    classify_csv("resources/test.csv")
    
    print("=" * 100)