# Log Classification System Using NLP

A multi-stage log classification system that uses Natural Language Processing techniques to automatically categorize system logs from various sources.

## 📋 Project Overview

This project implements an intelligent log classification pipeline that combines three different approaches:

1. **Regex-based Classification** - Fast pattern matching for well-defined log formats
2. **BERT-based Classification** - ML model using sentence embeddings for complex patterns
3. **LLM-based Classification** - Groq API with Llama 3.1 for edge cases and legacy system logs

## 🎯 Classification Categories

The system classifies logs into 9 categories:

- **User Action** - User login/logout, account creation
- **System Notification** - Backups, updates, file uploads
- **HTTP Status** - API request/response logs
- **Critical Error** - Severe system failures
- **Error** - General errors
- **Security Alert** - Unauthorized access attempts
- **Resource Usage** - Memory, CPU, disk usage logs
- **Workflow Error** - Process/workflow failures
- **Deprecation Warning** - Deprecated feature usage

## 🏗️ Project Structure

```
Log_classification_system_NLP_Personal_project/
├── training/
│   ├── training.ipynb           # Model training and data exploration
│   ├── processor_regex.py       # Regex-based classifier
│   ├── processor_bert.py        # BERT-based classifier
│   ├── processor_llm.py         # LLM-based classifier (Groq API)
│   ├── classify.py              # Multi-stage classification pipeline
│   └── .env                     # Environment variables (API keys)
├── models/
│   └── log_classification_model.pkl  # Trained Logistic Regression model
├── synthetic_logs.csv           # Training dataset (2,410 logs)
├── requirements.txt             # Python dependencies
├── main.py                      # Entry point (to be implemented)
├── README.md                    # Project documentation
└── .gitignore                   # Git ignore file
```

## 🚀 Getting Started

### Prerequisites

```bash
pip install pandas
pip install numpy
pip install scikit-learn
pip install sentence-transformers
pip install joblib
```

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Log_classification_system_NLP_Personal_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up Groq API (for LLM classifier):
   - Get a free API key from [console.groq.com](https://console.groq.com)
   - Create a `.env` file in the `training/` directory:
   ```bash
   cd training
   echo "GROQ_API_KEY=your_api_key_here" > .env
   ```

4. Test the classifiers:
```bash
# Test regex classifier
python training/processor_regex.py

# Test BERT classifier
python training/processor_bert.py

# Test LLM classifier
python training/processor_llm.py

# Test full pipeline
cd training
python classify.py
```

## 📊 Dataset

- **Source**: `synthetic_logs.csv`
- **Total Records**: 2,410 logs
- **Sources**: ModernCRM, AnalyticsEngine, ModernHR, BillingSystem, ThirdPartyAPI, LegacyCRM
- **Features**:
  - `timestamp`: Log timestamp
  - `source`: Source system
  - `log_message`: The actual log text
  - `target_label`: Ground truth classification

### Category Distribution

```
HTTP Status         : 1,017 logs (42%)
Security Alert      : 371 logs (15%)
System Notification : 356 logs (15%)
Error               : 177 logs (7%)
Resource Usage      : 177 logs (7%)
Critical Error      : 161 logs (7%)
User Action         : 144 logs (6%)
Workflow Error      : 4 logs (<1%)
Deprecation Warning : 3 logs (<1%)
```

## 🧠 Model Architecture

### 1. Regex Classifier (`processor_regex.py`)

- **Speed**: Very Fast
- **Accuracy**: 100% for matched patterns
- **Use Case**: Well-defined log patterns
- **Patterns**: 8 regex patterns for User Actions and System Notifications

### 2. BERT Classifier (`processor_bert.py`)

- **Model**: `all-MiniLM-L6-v2` (SentenceTransformer)
- **Embedding Size**: 384 dimensions
- **Classifier**: Logistic Regression
- **Training Size**: 1,687 logs
- **Test Size**: 723 logs
- **Accuracy**: 99% on test set
- **Confidence Threshold**: 50% (returns "Unclassified" if below)

### 3. LLM Classifier (`processor_llm.py`)

- **API**: Groq (groq.com)
- **Model**: `llama-3.1-70b-versatile`
- **Use Case**: Edge cases, Workflow Errors, Deprecation Warnings
- **Categories**: Workflow Error, Deprecation Warning, Unclassified
- **Authentication**: Requires GROQ_API_KEY in `.env` file
- **Advantage**: Semantic understanding of complex log patterns

### 4. Multi-stage Pipeline (`classify.py`)

The classification pipeline follows this logic:

```
Input Log
    ↓
Is source "LegacyCRM"?
    ├── Yes → Use LLM → Return Label
    └── No  → Try Regex
                ↓
        Regex Matched?
            ├── Yes → Return Label
            └── No  → Use BERT → Return Label
```

## 📈 Model Performance

### BERT Classifier Results

```
                     precision    recall  f1-score   support

     Critical Error       0.96      0.98      0.97        48
              Error       1.00      0.94      0.97        53
        HTTP Status       1.00      1.00      1.00       305
     Resource Usage       1.00      1.00      1.00        53
     Security Alert       0.99      1.00      1.00       112
System Notification       0.97      1.00      0.99       107
        User Action       1.00      1.00      1.00        43

           accuracy                           0.99       723
```

## 💡 Usage Examples

### Using Individual Classifiers

```python
from training.processor_regex import classify_with_regex
from training.processor_bert import classify_with_bert

# Regex classification (fast, for known patterns)
log = "User User123 logged in."
label = classify_with_regex(log)
print(label)  # Output: User Action

# BERT classification (ML-based, for complex patterns)
log = "Multiple failed authentication attempts detected"
label = classify_with_bert(log)
print(label)  # Output: Security Alert
```

### Using the Full Pipeline

```python
from training.classify import classify_logs

# Classify a log from ModernCRM
source = "ModernCRM"
log_msg = "Backup completed successfully."
label = classify_logs(source, log_msg)
print(f"{log_msg} --> {label}")
# Output: Backup completed successfully. --> System Notification
```

## 🔧 Model Training

The model was trained using the following approach:

1. **Data Loading**: Load 2,410 logs from `synthetic_logs.csv`
2. **Embedding Generation**: Convert logs to 384-dim vectors using SentenceTransformer
3. **Train/Test Split**: 70/30 split with stratification
4. **Model Training**: Logistic Regression with max_iter=1000
5. **Evaluation**: Achieved 99% accuracy on test set
6. **Model Saving**: Saved to `models/log_classification_model.pkl`

To retrain the model, run the cells in `training/training.ipynb`.

## 📝 TODO / Future Enhancements

- [x] Implement LLM-based classification for LegacyCRM logs (✅ Completed with Groq API)
- [ ] Add real-time log streaming capability
- [ ] Create a web dashboard for log monitoring
- [ ] Add support for custom regex patterns
- [ ] Implement model retraining pipeline
- [ ] Add logging and error handling
- [ ] Create API endpoints for classification service
- [ ] Add unit tests
- [ ] Deploy as a microservice

## 🤝 Contributing

This is a personal project. Contributions, issues, and feature requests are welcome!

## 📄 License

This project is for educational purposes.

## 👤 Author

**Your Name**
- Project: Log Classification System
- Date: February 2026

---

**Last Updated**: February 5, 2026
