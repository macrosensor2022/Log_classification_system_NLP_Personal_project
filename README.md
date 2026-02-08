# Log Classification System Using NLP

A multi-stage log classification system using NLP techniques to automatically categorize system logs.

## Overview

This project implements an intelligent log classification pipeline that combines three approaches:

1. **Regex-based Classification** - Fast pattern matching for well-defined formats
2. **BERT-based Classification** - ML model using sentence embeddings for complex patterns
3. **LLM-based Classification** - (TODO) For legacy systems with unpredictable formats

## Categories

The system classifies logs into 9 categories:
- User Action
- System Notification
- HTTP Status
- Critical Error
- Error
- Security Alert
- Resource Usage
- Workflow Error
- Deprecation Warning

## Project Structure

```
Log_classification_system_NLP_Personal_project/
├── training/
│   ├── training.ipynb           # Model training
│   ├── processor_regex.py       # Regex classifier
│   ├── processor_bert.py        # BERT classifier
│   ├── processor_llm.py         # LLM classifier (TODO)
│   └── classify.py              # Classification pipeline
├── models/
│   └── log_classification_model.pkl
├── synthetic_logs.csv
└── README.md
```

## Installation

```bash
git clone <repository-url>
cd Log_classification_system_NLP_Personal_project
pip install pandas numpy scikit-learn sentence-transformers joblib
```

## Usage

```python
from training.classify import classify_logs

source = "ModernCRM"
log_msg = "Backup completed successfully."
label = classify_logs(source, log_msg)
print(f"{log_msg} --> {label}")
# Output: Backup completed successfully. --> System Notification
```

## Dataset

- **Total**: 2,410 logs from various sources
- **Split**: 70/30 train/test
- **Distribution**: HTTP Status (42%), Security Alert (15%), System Notification (15%), others (28%)

## Model Performance

BERT classifier achieves 99% accuracy on test set.

### Results by Category:

```
                     precision    recall  f1-score   support
     Critical Error       0.96      0.98      0.97        48
              Error       1.00      0.94      0.97        53
        HTTP Status       1.00      1.00      1.00       305
     Resource Usage       1.00      1.00      1.00        53
     Security Alert       0.99      1.00      1.00       112
System Notification       0.97      1.00      0.99       107
        User Action       1.00      1.00      1.00        43
```

## Pipeline

```
Input Log
    ↓
Is source "LegacyCRM"?
    ├── Yes → Use LLM (TODO)
    └── No  → Try Regex
                ↓
        Regex Matched?
            ├── Yes → Return Label
            └── No  → Use BERT → Return Label
```

## Technical Details

- **BERT Model**: `all-MiniLM-L6-v2` (384-dim embeddings)
- **Classifier**: Logistic Regression
- **Confidence Threshold**: 50%

## Future Work

- Implement LLM classification for legacy systems
- Real-time log streaming
- Web dashboard
- API endpoints
- Model retraining pipeline
