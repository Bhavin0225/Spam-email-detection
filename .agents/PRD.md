# Product Requirements Document (PRD)
## Spam Email Detection System

**Document version:** 1.0  
**Date:** 2026-06-07  
**Prepared for:** Early-stage product and engineering planning

---

## 1. Product Summary

The Spam Email Detection System is an AI-powered application that classifies incoming emails as **spam/phishing** or **legitimate**. It is designed to help users and organizations reduce inbox clutter, prevent phishing attacks, and improve email safety through a combination of NLP, URL analysis, and email header analysis.

The product stores email records and prediction results in **MongoDB Atlas**, exposes a **FastAPI** backend for inference, and supports future model improvements through user feedback and retraining.

---

## 2. Problem Statement

Email remains one of the most common entry points for spam, phishing, and social engineering attacks. Traditional mailbox filters are often either too weak, allowing harmful messages through, or too aggressive, sending important messages to spam.

Users need a system that can:

- detect suspicious emails quickly,
- avoid false positives on legitimate messages,
- explain why an email was flagged,
- and improve over time using feedback.

---

## 3. Goals

### Primary goals
- Detect spam/phishing emails with high precision and strong overall classification quality.
- Store email data, predictions, and feedback in MongoDB Atlas.
- Provide a usable API for real-time email classification.
- Support future retraining from feedback and updated datasets.

### Business goals
- Demonstrate a complete end-to-end AI product suitable for academic, portfolio, or startup use.
- Build a production-style system with clear architecture, logging, and extensibility.
- Make the project strong enough to show both ML capability and software engineering quality.

---

## 4. Non-Goals

Version 1 will **not** include:
- full email client replacement,
- user account management and authentication UI,
- browser extensions,
- enterprise SIEM integrations,
- deep threat intelligence platform features,
- human analyst workbench,
- multi-tenant admin console,
- real-time email inbox syncing with Gmail/Outlook APIs,
- full explainability suite beyond basic model confidence and selected feature reasons.

---

## 5. Target Users

### Primary users
1. **Students and individual users** who want safer email screening.
2. **Small teams or startups** that need a lightweight email risk classifier.
3. **Developers and data scientists** building or demoing an ML-powered security system.

### Secondary users
1. **Instructors and reviewers** evaluating an ML + backend project.
2. **Security-aware organizations** that want a prototype for email risk classification.

---

## 6. User Needs

Users need the system to:
- classify emails quickly,
- keep a record of predictions,
- reduce spam and phishing exposure,
- avoid incorrectly blocking legitimate messages,
- and allow correction when the model makes a mistake.

---

## 7. Product Scope

The product will include:
- email text cleaning and preprocessing,
- feature extraction from subject/body/URLs/headers,
- model inference,
- prediction storage,
- feedback capture,
- analytics,
- model version tracking,
- and retraining support.

The product will be built around:
- **MongoDB Atlas** for storage,
- **FastAPI** for inference services,
- **XGBoost + baseline models** for classification,
- and a **hybrid feature pipeline** combining text, URL, and header signals.

---

## 8. Core Features

### 8.1 Must-Have Features

#### A. Email classification
- Accept email subject and body as input.
- Predict whether an email is spam/phishing or legitimate.
- Return a confidence score with the prediction.

#### B. NLP preprocessing
- Remove HTML tags and HTML entities.
- Normalize text to lowercase.
- Remove extra whitespace and symbols.
- Tokenize and lemmatize text.
- Remove stopwords while preserving important negation terms like “not” and “never.”

#### C. Feature engineering
- Extract subject TF-IDF features.
- Extract body TF-IDF features.
- Generate statistical text features such as word count, uppercase ratio, and exclamation count.
- Extract URL-based features such as URL count, URL length, shortener usage, and suspicious keywords.
- Extract header-based features such as SPF fail, DKIM fail, reply-to mismatch, and hop count.

#### D. MongoDB Atlas storage
- Store raw email data in MongoDB Atlas.
- Store prediction results in MongoDB Atlas.
- Store feedback entries in MongoDB Atlas.
- Store model metadata and dataset metadata in MongoDB Atlas.

#### E. API layer
- Provide a `POST /classify` endpoint for prediction.
- Provide a `POST /feedback` endpoint for user corrections.
- Provide a `GET /analytics` endpoint for summary metrics.
- Provide a `GET /health` endpoint for health checks.

#### F. Model versioning
- Track the deployed model version.
- Save evaluation metrics for each model version.
- Allow future replacement of the model without changing the API contract.

#### G. Basic analytics
- Show total predictions.
- Show spam/phishing rate.
- Show false positive and false negative counts.
- Show top suspicious sender domains.

#### H. Logging and audit trail
- Record each prediction with timestamp, model version, and confidence.
- Maintain a retraining-ready history of feedback and corrections.

---

### 8.2 Nice-to-Have Features

#### A. Explanation layer
- Show top contributing words or features behind a prediction.
- Display a short explanation such as “suspicious URL” or “urgent language detected.”

#### B. Dashboard
- Visual analytics dashboard for trends over time.
- Charts for spam rate, confidence distribution, and top domains.

#### C. Threat intelligence enrichment
- Check suspicious URLs against external threat feeds such as PhishTank or VirusTotal.

#### D. Advanced retraining pipeline
- Automated scheduled retraining when enough new feedback is collected.
- Model comparison dashboard between versions.

#### E. Alerting
- Notify an admin when spam volume spikes sharply.
- Flag repeated malicious sender domains.

---

## 9. User Flow

### End-to-end user journey

1. **User submits an email**
   - The user enters or sends the subject and body text to the system.

2. **System validates the input**
   - The API checks that the payload is not empty and is properly formatted.

3. **Preprocessing runs**
   - The system cleans the text and extracts structured signals.

4. **Feature generation runs**
   - The system creates text, URL, and header features.

5. **Model inference runs**
   - The trained classifier predicts spam/phishing or legitimate.

6. **Results are stored**
   - Prediction, confidence, timestamp, and model version are saved in MongoDB Atlas.

7. **User sees the result**
   - The API returns the label and confidence to the client.

8. **Feedback is collected**
   - If the user disagrees with the result, they can submit correction feedback.

9. **Analytics and retraining**
   - Feedback is reviewed, aggregated, and used later for model improvement.

---

## 10. MVP Definition

The MVP should be the smallest version that demonstrates the core value of the product.

### MVP includes
- One prediction endpoint (`POST /classify`)
- One feedback endpoint (`POST /feedback`)
- MongoDB Atlas storage for emails and predictions
- Text preprocessing pipeline
- Basic feature engineering
- One strong final classifier, preferably XGBoost
- Model confidence score in the response
- Basic logging and health endpoint
- Minimal analytics endpoint

### MVP excludes
- Full dashboard UI
- Browser integration
- User authentication
- Email inbox syncing
- Complex explainability tools
- Automated retraining pipeline
- Threat intelligence integration

---

## 11. Success Metrics

### Model metrics
- **Precision**: Primary metric for reducing false positives.
- **Recall**: Important to catch harmful emails.
- **F1 Score**: Balanced measure of classification quality.
- **AUC-ROC**: Measure of ranking quality across thresholds.
- **False Positive Rate**: Must remain low to preserve trust.

### Product metrics
- Percentage of emails successfully classified.
- Average API response time.
- Percentage of predictions stored successfully in MongoDB Atlas.
- Feedback submission rate.
- Reduction in repeated misclassifications over time.

### MVP success criteria
The MVP is successful if it:
- correctly classifies most obvious spam/phishing emails,
- avoids excessive false positives,
- stores predictions reliably,
- and supports a usable feedback loop.

---

## 12. Functional Requirements

### FR1 — Email input
The system must accept email subject and body as structured input.

### FR2 — Prediction
The system must return a spam/phishing or legitimate label with confidence.

### FR3 — Storage
The system must store raw email data, predictions, and feedback in MongoDB Atlas.

### FR4 — Feature processing
The system must apply the same preprocessing and feature pipeline in training and inference.

### FR5 — Model versioning
The system must record the model version used for every prediction.

### FR6 — Feedback capture
The system must allow users to mark predictions as correct or incorrect.

### FR7 — Analytics
The system must support summary statistics on predictions and feedback.

---

## 13. Non-Functional Requirements

### Performance
- The API should respond quickly enough for practical real-time use.
- Inference should remain stable under moderate request load.

### Reliability
- The system should not fail when MongoDB Atlas experiences temporary latency.
- Prediction failures should be logged clearly.

### Security
- MongoDB credentials must be stored in environment variables.
- Atlas access must be protected by network and role-based access controls.
- Sensitive data should not be exposed unnecessarily.

### Maintainability
- The codebase must be modular.
- Training, inference, and storage logic should be separated.
- Models and vectorizers must be serialized cleanly.

### Scalability
- The design should support future expansion to larger datasets and more features.

---

## 14. Data Model Overview

### Email record
- email_id
- subject
- sender
- sender_domain
- body_text
- links
- headers
- dataset_source
- label
- split
- created_at

### Prediction record
- prediction_id
- email_id
- prediction_label
- confidence
- model_version
- timestamp

### Feedback record
- feedback_id
- prediction_id
- correct_or_incorrect
- user_comment
- timestamp

### Model metadata record
- model_version
- algorithm
- training_date
- dataset_version
- precision
- recall
- F1
- AUC

---

## 15. Risks and Mitigations

### Risk: False positives
Legitimate emails may be flagged as spam.

**Mitigation:** Use threshold tuning, emphasize precision, and test carefully on legitimate samples.

### Risk: Data leakage
Training on information from the full dataset can inflate metrics.

**Mitigation:** Split data early and fit vectorizers only on training data.

### Risk: Model drift
Spam patterns change over time.

**Mitigation:** Preserve feedback data and support retraining.

### Risk: Overengineering the MVP
Too many features can slow delivery.

**Mitigation:** Keep version one focused on classification, storage, and feedback.

---

## 16. Deliberately Not Building in Version 1

The following are intentionally out of scope:
- inbox sync with Gmail/Outlook,
- email sending functionality,
- user authentication and role management,
- enterprise compliance tooling,
- advanced SOC-style threat hunting,
- external SIEM integration,
- complete admin console,
- mobile app,
- browser extension,
- full explainability reports,
- automatic production retraining without review.

---

## 17. Release Plan

### Version 1
- Classification API
- MongoDB Atlas storage
- Basic analytics
- Feedback capture
- One production-grade ML model

### Version 2
- Better explainability
- Dashboard
- Retraining workflow
- More features from headers and URLs

### Version 3
- Threat intelligence integration
- Admin tools
- Automated model comparison
- Broader security workflow support

---

## 18. Open Questions

- Should the product focus on spam only, phishing only, or both?
- Will users enter text manually, or will emails be imported from a mailbox later?
- Should the final model prioritize precision, recall, or a balanced threshold?
- Do we want a simple API-only product, or a web UI as well?

---

## 19. Final Recommendation

For version one, the best approach is to keep the product focused on:

- accurate classification,
- MongoDB Atlas-backed persistence,
- strong feature engineering,
- a clean API,
- and a feedback loop.

That gives the project the best balance of technical depth, usability, and implementation speed.
