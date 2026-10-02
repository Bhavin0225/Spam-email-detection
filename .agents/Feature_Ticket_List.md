# Feature Ticket List
## Spam Email Detection System

This document breaks the product into buildable engineering tickets. Each ticket can be used directly as a prompt for an AI coding tool.

---

# EPIC 1: Project Foundation

## TICKET-001: FastAPI Project Setup
**Priority:** Must-Have

### Description
Create a production-ready FastAPI backend with modular architecture, environment variable support, logging, and API versioning.

### Acceptance Criteria
- FastAPI starts successfully
- `/health` endpoint returns 200
- Environment variables load from `.env`
- Structured logging enabled

### Dependencies
None

---

## TICKET-002: MongoDB Atlas Connection Layer
**Priority:** Must-Have

### Description
Create a reusable MongoDB Atlas connection module using pymongo with connection pooling and retry logic.

### Acceptance Criteria
- Atlas connection established
- Connection pooling enabled
- Retry logic implemented
- Database health check available

### Dependencies
TICKET-001

---

# EPIC 2: Authentication & Security

## TICKET-003: JWT Authentication System
**Priority:** Must-Have

### Description
Implement signup, login, JWT access tokens, refresh tokens, password hashing, and authentication middleware.

### Acceptance Criteria
- User registration works
- Login returns JWT
- Protected routes require authentication
- Passwords stored using bcrypt

### Dependencies
TICKET-001, TICKET-002

---

## TICKET-004: Role-Based Access Control
**Priority:** Must-Have

### Description
Implement User, Security Analyst, ML Engineer, Admin, and Super Admin roles.

### Acceptance Criteria
- Roles stored in database
- Permissions enforced
- Unauthorized access blocked

### Dependencies
TICKET-003

---

# EPIC 3: Database Design

## TICKET-005: Database Collections & Indexes
**Priority:** Must-Have

### Description
Create collections: emails, predictions, feedback, model_metadata, dataset_metadata, system_logs.

### Acceptance Criteria
- Collections created
- Indexes created
- CRUD operations tested

### Dependencies
TICKET-002

---

# EPIC 4: Dataset Management

## TICKET-006: Dataset Ingestion Pipeline
**Priority:** Must-Have

### Description
Build ingestion scripts for PhishTank, SpamAssassin, and Enron datasets.

### Acceptance Criteria
- Data imported successfully
- Dataset source tracked
- Train/validation/test split stored

### Dependencies
TICKET-005

---

## TICKET-007: Dataset Deduplication Engine
**Priority:** Must-Have

### Description
Prevent duplicate emails using hashing and duplicate detection.

### Acceptance Criteria
- Duplicate emails detected
- Duplicate records skipped

### Dependencies
TICKET-006

---

# EPIC 5: Email Processing

## TICKET-008: Email Parsing Engine
**Priority:** Must-Have

### Description
Extract sender, subject, body, URLs, headers, attachments, SPF, DKIM, and metadata.

### Acceptance Criteria
- Email fields extracted correctly
- HTML emails supported
- Missing fields handled safely

### Dependencies
TICKET-006

---

## TICKET-009: Text Cleaning Pipeline
**Priority:** Must-Have

### Description
Implement HTML removal, normalization, tokenization, stopword removal, and lemmatization.

### Acceptance Criteria
- Clean text output generated
- Works on multilingual input
- Unit tests pass

### Dependencies
TICKET-008

---

# EPIC 6: Feature Engineering

## TICKET-010: TF-IDF Feature Generation
**Priority:** Must-Have

### Description
Create separate TF-IDF vectorizers for subject and body content.

### Acceptance Criteria
- Subject vectorizer created
- Body vectorizer created
- Saved using joblib

### Dependencies
TICKET-009

---

## TICKET-011: URL Feature Extraction
**Priority:** Must-Have

### Description
Generate phishing-related URL features including URL count, URL length, IP domains, shorteners, and suspicious keywords.

### Acceptance Criteria
- Features extracted successfully
- Edge cases handled

### Dependencies
TICKET-008

---

## TICKET-012: Header Feature Extraction
**Priority:** Must-Have

### Description
Extract SPF, DKIM, DMARC, reply-to mismatch, and hop-count features.

### Acceptance Criteria
- Features available in feature vector
- Missing headers handled safely

### Dependencies
TICKET-008

---

# EPIC 7: Machine Learning

## TICKET-013: Baseline Model Training
**Priority:** Must-Have

### Description
Train Multinomial Naive Bayes model as baseline.

### Acceptance Criteria
- Model trained
- Metrics generated
- Artifacts saved

### Dependencies
TICKET-010

---

## TICKET-014: Logistic Regression Model
**Priority:** Must-Have

### Description
Train Logistic Regression using TF-IDF and engineered features.

### Acceptance Criteria
- Metrics recorded
- Compared with baseline

### Dependencies
TICKET-013

---

## TICKET-015: XGBoost Model
**Priority:** Must-Have

### Description
Train XGBoost model and use it as production candidate.

### Acceptance Criteria
- F1 score calculated
- Model serialized
- Feature importance generated

### Dependencies
TICKET-014

---

## TICKET-016: Threshold Optimization
**Priority:** Should-Have

### Description
Evaluate thresholds and select best operating point.

### Acceptance Criteria
- Threshold experiments completed
- Best threshold stored

### Dependencies
TICKET-015

---

# EPIC 8: Inference System

## TICKET-017: Prediction Engine
**Priority:** Must-Have

### Description
Load trained artifacts and generate predictions for new emails.

### Acceptance Criteria
- Prediction returned
- Confidence score returned
- Errors handled gracefully

### Dependencies
TICKET-015

---

# EPIC 9: API Development

## TICKET-018: POST /predict Endpoint
**Priority:** Must-Have

### Description
Accept email content and return prediction.

### Acceptance Criteria
- Valid requests processed
- Prediction stored in database

### Dependencies
TICKET-017

---

## TICKET-019: POST /feedback Endpoint
**Priority:** Must-Have

### Description
Allow users to report incorrect predictions.

### Acceptance Criteria
- Feedback stored
- Linked to prediction

### Dependencies
TICKET-018

---

## TICKET-020: GET /analytics Endpoint
**Priority:** Should-Have

### Description
Return spam statistics, domain analytics, and model metrics.

### Acceptance Criteria
- Aggregated analytics returned

### Dependencies
TICKET-018

---

## TICKET-021: GET /health Endpoint
**Priority:** Must-Have

### Description
Provide API and database health status.

### Acceptance Criteria
- Returns service status
- Checks Atlas connectivity

### Dependencies
TICKET-002

---

# EPIC 10: Dashboard

## TICKET-022: Streamlit Admin Dashboard
**Priority:** Should-Have

### Description
Build dashboard for monitoring spam trends and model performance.

### Acceptance Criteria
- Charts displayed
- Analytics integrated

### Dependencies
TICKET-020

---

# EPIC 11: Feedback & Retraining

## TICKET-023: Feedback Review Workflow
**Priority:** Should-Have

### Description
Allow analysts to review and approve feedback before retraining.

### Acceptance Criteria
- Review process implemented
- Approved samples tracked

### Dependencies
TICKET-019

---

## TICKET-024: Automated Retraining Pipeline
**Priority:** Nice-to-Have

### Description
Automatically retrain models using approved feedback data.

### Acceptance Criteria
- New model generated
- Metrics compared
- Model version tracked

### Dependencies
TICKET-023

---

# EPIC 12: Security

## TICKET-025: API Rate Limiting
**Priority:** Must-Have

### Description
Prevent abuse of prediction endpoints.

### Acceptance Criteria
- Request limits enforced
- Abuse attempts blocked

### Dependencies
TICKET-003

---

## TICKET-026: Audit Logging
**Priority:** Must-Have

### Description
Track authentication events, predictions, feedback, and role changes.

### Acceptance Criteria
- Logs stored securely
- Sensitive data excluded

### Dependencies
TICKET-003

---

# EPIC 13: Testing

## TICKET-027: Unit Testing Suite
**Priority:** Must-Have

### Description
Create tests for preprocessing, feature extraction, prediction logic, and database operations.

### Acceptance Criteria
- Test coverage established
- All critical tests pass

### Dependencies
Multiple

---

## TICKET-028: Integration Testing Suite
**Priority:** Must-Have

### Description
Validate end-to-end API and database workflows.

### Acceptance Criteria
- Core workflows tested
- Failures reported clearly

### Dependencies
TICKET-018

---

# EPIC 14: Deployment

## TICKET-029: Dockerization
**Priority:** Must-Have

### Description
Containerize the backend and ML service.

### Acceptance Criteria
- Docker image builds successfully
- Application runs in container

### Dependencies
Core backend complete

---

## TICKET-030: Cloud Deployment
**Priority:** Must-Have

### Description
Deploy FastAPI service to Render, AWS, or GCP with MongoDB Atlas integration.

### Acceptance Criteria
- Production deployment successful
- HTTPS enabled
- Environment variables configured

### Dependencies
TICKET-029

---

# EPIC 15: Advanced Features

## TICKET-031: SHAP Explainable AI
**Priority:** Nice-to-Have

### Description
Provide explanations for why an email was classified as spam.

### Acceptance Criteria
- Feature contribution displayed

### Dependencies
TICKET-015

---

## TICKET-032: Threat Intelligence Integration
**Priority:** Nice-to-Have

### Description
Integrate OpenPhish, PhishTank, and VirusTotal lookups.

### Acceptance Criteria
- URLs checked against threat feeds
- Threat score returned

### Dependencies
TICKET-018

---

# MVP Scope

Launch MVP includes:

- TICKET-001 through TICKET-021
- TICKET-025
- TICKET-026
- TICKET-027
- TICKET-028
- TICKET-029
- TICKET-030

Everything else can be delivered after launch.
