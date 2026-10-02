# Spam Email Detection System - Technical Architecture Document

This file was regenerated because the previous download link was unavailable.

## Summary
- FastAPI backend
- MongoDB Atlas database
- XGBoost + Scikit-Learn ML pipeline
- spaCy/NLTK preprocessing
- Docker deployment
- Feedback-driven retraining

## Core Collections
- emails
- predictions
- feedback
- model_metadata
- dataset_metadata
- system_logs

## Core APIs
- POST /predict
- POST /feedback
- GET /analytics
- GET /health

## Environment Variables
MONGODB_URI
MONGODB_DATABASE
MODEL_PATH
ACTIVE_MODEL_VERSION
DECISION_THRESHOLD

Refer to the full architecture document generated in the chat for detailed schema, folder structure, and deployment design.
