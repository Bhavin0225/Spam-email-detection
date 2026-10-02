# Technical Architecture Document
## Spam Email Detection System
### Version 1.0

**Date:** 2026-06-07  
**Status:** Approved — implementation may begin  
**Priority:** Blocker — must be complete before development starts

---

## 1. System Overview

### 1.1 Product Summary

The Spam Email Detection System is a SaaS web application that classifies incoming emails as **suspicious** (spam, phishing, scam, malicious URLs, credential theft) or **legitimate** using machine learning. It provides a secure web UI and API for users, security analysts, and administrators.

### 1.2 Business Goal

- Demonstrate a complete end-to-end AI product suitable for academic, portfolio, or startup use.
- Build a production-style system with clear architecture, logging, and extensibility.
- Deliver accurate email classification with a feedback-driven improvement loop.

### 1.3 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENTS                                    │
│          Browser (React SPA)  │  API Consumers (curl, SDKs)            │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │ HTTPS
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RENDER (Cloud Host)                             │
│                                                                         │
│  ┌──────────────────────────────────────────────┐                       │
│  │           FASTAPI BACKEND (Python 3.11)      │                       │
│  │                                              │                       │
│  │  API Layer ──→ Middleware ──→ Services ──→ DB │                       │
│  │       │              │            │           │                       │
│  │       │         JWT + RBAC   ML Engine        │                       │
│  │       │         Rate Limit   Preprocessing    │                       │
│  │       │         Audit Log    Feature Eng.     │                       │
│  └──────────────────────┬───────────────────────┘                       │
│                         │                                                │
│  ┌──────────────────────┴───────────────────────┐                       │
│  │          REACT FRONTEND (Node 20)            │                       │
│  │          TypeScript + Tailwind v4             │                       │
│  │          shadcn/ui + Recharts                 │                       │
│  └──────────────────────────────────────────────┘                       │
│                                                                         │
└──────────────────────┬──────────────────────────────────────────────────┘
                       │ pymongo (TLS)
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       MONGODB ATLAS                                     │
│                   phishing_detection_db                                  │
│                                                                         │
│  users │ emails │ predictions │ feedback │ model_metadata │             │
│  dataset_metadata │ system_logs                                         │
└─────────────────────────────────────────────────────────────────────────┘

                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         SENTRY                                          │
│                   Error Monitoring + Performance                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.4 Core Components

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| **Frontend** | React + TypeScript + Tailwind v4 + shadcn/ui | User interface for all roles |
| **Backend API** | FastAPI (Python 3.11) | REST API, auth, business logic, ML inference |
| **Database** | MongoDB Atlas | Persistent storage for all application data |
| **ML Engine** | XGBoost + Scikit-Learn + spaCy | Email classification pipeline |
| **Monitoring** | Sentry | Error tracking and performance monitoring |

### 1.5 Service Interactions

```
Frontend ──HTTP──→ Backend API ──pymongo──→ MongoDB Atlas
                       │
                       ├──→ Authentication Service
                       ├──→ Prediction Service (ML Engine)
                       ├──→ Feedback Service
                       ├──→ Analytics Service
                       └──→ Model Management Service
                       │
                       └──Sentry SDK──→ Sentry (monitoring)
```

---

## 2. Technology Stack

### 2.1 Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | FastAPI | Latest stable |
| **Language** | Python | 3.11 |
| **ASGI Server** | Uvicorn | Latest stable |
| **Database Driver** | pymongo / motor | Latest stable |
| **ML Framework** | Scikit-Learn, XGBoost | Latest stable |
| **NLP** | spaCy, NLTK | Latest stable |
| **Data Processing** | pandas, numpy | Latest stable |
| **Auth** | python-jose (JWT), passlib + bcrypt | Latest stable |
| **Validation** | Pydantic v2 | Latest stable |
| **Rate Limiting** | slowapi | Latest stable |
| **Monitoring** | sentry-sdk[fastapi] | Latest stable |
| **Environment** | python-dotenv | Latest stable |
| **Serialization** | joblib | Latest stable |

### 2.2 Frontend

| Component | Technology | Version |
|-----------|-----------|---------|
| **Framework** | React | 18+ |
| **Language** | TypeScript | 5+ |
| **Styling** | Tailwind CSS | v4 |
| **UI Components** | shadcn/ui | Latest |
| **Charts** | Recharts | Latest |
| **Data Fetching** | React Query (TanStack Query) or SWR | Latest |
| **HTTP Client** | Axios | Latest |
| **Routing** | React Router | v6+ |
| **Build Tool** | Vite | Latest |
| **Runtime** | Node.js | 20 |
| **Monitoring** | @sentry/react | Latest |

### 2.3 Database

| Component | Technology |
|-----------|-----------|
| **Provider** | MongoDB Atlas |
| **Database Name** | `phishing_detection_db` |
| **Driver** | pymongo (sync) / motor (async) |
| **Connection** | TLS encrypted, connection pooling |

### 2.4 ML Stack

| Library | Purpose |
|---------|---------|
| **Scikit-Learn** | TF-IDF vectorization, Naive Bayes, Logistic Regression, preprocessing utilities |
| **XGBoost** | Production classification model |
| **spaCy** | Tokenization, lemmatization, NLP preprocessing |
| **pandas** | Data manipulation and feature engineering |
| **numpy** | Numerical operations |
| **joblib** | Model and vectorizer serialization |

### 2.5 Infrastructure

| Component | Technology |
|-----------|-----------|
| **Deployment** | Render |
| **Containerization** | Docker + Docker Compose |
| **Monitoring** | Sentry |
| **Version Control** | Git (feature branches) |
| **CI/CD** | GitHub Actions or Render auto-deploy |

---

## 3. Repository Structure

### 3.1 Root Directory

```
spam_new/
├── .agent/                          # Project specification documents
│   ├── PRD.md
│   ├── technical_architecture.md    # This document
│   ├── Frontend_Specification_Document.md
│   ├── Feature_Ticket_List.md
│   └── Security_and_Access_Document.md
│
├── backend/                         # FastAPI backend application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   ├── config.py                # Settings and environment loading
│   │   │
│   │   ├── api/                     # Route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # POST /auth/signup, /auth/login, /auth/refresh
│   │   │   ├── predict.py           # POST /predict
│   │   │   ├── feedback.py          # POST /feedback
│   │   │   ├── analytics.py         # GET /analytics
│   │   │   ├── history.py           # GET /history
│   │   │   ├── health.py            # GET /health
│   │   │   └── admin.py             # GET /admin/users, /admin/audit-logs
│   │   │
│   │   ├── core/                    # Application core
│   │   │   ├── __init__.py
│   │   │   ├── security.py          # JWT creation, password hashing, token validation
│   │   │   ├── permissions.py       # RBAC role checks and decorators
│   │   │   └── exceptions.py        # Custom exception classes
│   │   │
│   │   ├── database/                # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── connection.py        # MongoDB Atlas connection, pooling, retry
│   │   │   ├── collections.py       # Collection references and index creation
│   │   │   └── crud.py              # Generic CRUD operations
│   │   │
│   │   ├── services/                # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py      # Registration, login, token management
│   │   │   ├── prediction_service.py # Preprocessing → features → inference
│   │   │   ├── feedback_service.py  # Feedback collection and validation
│   │   │   ├── analytics_service.py # Aggregation queries and stats
│   │   │   └── model_service.py     # Model loading, versioning, management
│   │   │
│   │   ├── ml/                      # Machine learning pipeline
│   │   │   ├── __init__.py
│   │   │   ├── preprocessor.py      # Text cleaning pipeline
│   │   │   ├── feature_engine.py    # TF-IDF, URL, header, statistical features
│   │   │   ├── inference.py         # Model loading and prediction
│   │   │   └── training.py          # Training pipeline (offline)
│   │   │
│   │   ├── schemas/                 # Pydantic models
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # SignupRequest, LoginRequest, TokenResponse
│   │   │   ├── email.py             # EmailInput, EmailRecord
│   │   │   ├── prediction.py        # PredictionResponse, PredictionRecord
│   │   │   ├── feedback.py          # FeedbackRequest, FeedbackResponse
│   │   │   ├── analytics.py         # AnalyticsResponse
│   │   │   └── common.py            # Shared schemas (pagination, errors)
│   │   │
│   │   ├── middleware/              # Request middleware
│   │   │   ├── __init__.py
│   │   │   ├── auth_middleware.py   # JWT validation middleware
│   │   │   ├── rate_limiter.py      # Rate limiting middleware
│   │   │   └── audit_logger.py      # Audit logging middleware
│   │   │
│   │   └── utils/                   # Shared utilities
│   │       ├── __init__.py
│   │       ├── hashing.py           # Content hashing for deduplication
│   │       ├── validators.py        # Input validation helpers
│   │       └── logger.py            # Structured logging setup
│   │
│   ├── scripts/                     # Dataset and utility scripts
│   │   ├── fetch_spamassassin.py    # Download SpamAssassin corpus
│   │   ├── fetch_enron.py           # Download Enron email dataset
│   │   ├── fetch_phishtank.py       # Download PhishTank phishing data
│   │   ├── ingest_data.py           # Parse, deduplicate, load into MongoDB
│   │   └── train_models.py          # Train baseline → LR → XGBoost pipeline
│   │
│   ├── tests/                       # Test suites
│   │   ├── __init__.py
│   │   ├── conftest.py              # Shared fixtures
│   │   ├── unit/                    # Unit tests
│   │   │   ├── test_preprocessor.py
│   │   │   ├── test_feature_engine.py
│   │   │   ├── test_inference.py
│   │   │   ├── test_auth_service.py
│   │   │   └── test_schemas.py
│   │   └── integration/             # Integration tests
│   │       ├── test_predict_api.py
│   │       ├── test_feedback_api.py
│   │       ├── test_analytics_api.py
│   │       └── test_auth_api.py
│   │
│   ├── models/                      # Serialized ML artifacts
│   │   ├── v1.0.0/
│   │   │   ├── subject_vectorizer.pkl
│   │   │   ├── body_vectorizer.pkl
│   │   │   └── xgboost_model.pkl
│   │   └── .gitkeep
│   │
│   ├── docs/                        # Backend documentation
│   │   └── api_reference.md
│   │
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Backend Docker image
│   └── .env.example                 # Environment variable template
│
├── frontend/                        # React frontend application
│   ├── src/
│   │   ├── components/              # Reusable UI components
│   │   │   ├── ui/                  # shadcn/ui primitives
│   │   │   ├── layout/              # Shell, sidebar, navbar
│   │   │   ├── forms/               # Email input, feedback forms
│   │   │   ├── cards/               # Prediction card, stats card
│   │   │   ├── modals/              # Confirmation, feedback detail
│   │   │   └── charts/              # Recharts wrappers
│   │   │
│   │   ├── pages/                   # Route-level page components
│   │   │   ├── Dashboard/
│   │   │   ├── AnalyzeEmail/
│   │   │   ├── History/
│   │   │   ├── Analytics/
│   │   │   ├── Feedback/
│   │   │   ├── Admin/
│   │   │   ├── Auth/                # Login, Signup
│   │   │   └── Settings/
│   │   │
│   │   ├── services/                # API client layer
│   │   │   ├── apiClient.ts         # Axios instance with interceptors
│   │   │   ├── authService.ts       # Login, signup, token refresh
│   │   │   ├── predictionService.ts # POST /predict, GET /history
│   │   │   └── analyticsService.ts  # GET /analytics
│   │   │
│   │   ├── hooks/                   # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   ├── usePrediction.ts
│   │   │   └── useAnalytics.ts
│   │   │
│   │   ├── contexts/                # React Context providers
│   │   │   ├── AuthContext.tsx
│   │   │   └── ThemeContext.tsx
│   │   │
│   │   ├── styles/                  # Global styles
│   │   │   └── globals.css
│   │   │
│   │   ├── utils/                   # Frontend utilities
│   │   │   ├── constants.ts
│   │   │   ├── formatters.ts
│   │   │   └── validators.ts
│   │   │
│   │   ├── App.tsx                  # Root component with routing
│   │   └── main.tsx                 # Entry point
│   │
│   ├── public/                      # Static assets
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   └── Dockerfile                   # Frontend Docker image
│
├── docker-compose.yml               # Local development orchestration
├── .gitignore
├── .env.example                     # Root-level env template
├── understanding.md                 # Codebase understanding document
└── README.md                        # Project documentation
```

---

## 4. Deployment Architecture

### 4.1 Infrastructure Map

| Component | Host | Notes |
|-----------|------|-------|
| **Frontend** | Render (Static Site or Web Service) | Serves built React SPA |
| **Backend** | Render (Web Service) | Runs FastAPI via Docker |
| **Database** | MongoDB Atlas | Cloud-managed, TLS encrypted |
| **Monitoring** | Sentry | SaaS error tracking |

### 4.2 Deployment Flow

```
Developer pushes code to feature branch
        │
        ▼
GitHub repository updated
        │
        ▼
Pull request created → Code review
        │
        ▼
Merge to main branch
        │
        ▼
CI pipeline runs (GitHub Actions)
  ├── Lint (ruff / eslint)
  ├── Unit tests (pytest / vitest)
  └── Integration tests
        │
        ▼
Tests pass → Docker image built
        │
        ▼
Deployment triggered on Render
  ├── Backend service updated
  └── Frontend service updated
        │
        ▼
Post-deployment health checks execute
  └── GET /health returns 200
```

### 4.3 Local Development (Docker Compose)

```yaml
# docker-compose.yml defines:
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: ./backend/.env
    volumes: ["./backend:/app"]

  frontend:
    build: ./frontend
    ports: ["3000:3000"]
    volumes: ["./frontend:/app"]
```

Both services start with a single `docker compose up` command. Backend runs with hot reload via Uvicorn. Frontend runs with Vite dev server.

---

## 5. Database Architecture

### 5.1 Database Details

| Setting | Value |
|---------|-------|
| **Provider** | MongoDB Atlas |
| **Database Name** | `phishing_detection_db` |
| **Connection** | TLS encrypted, connection pooling, retry logic |
| **Driver** | pymongo (sync) or motor (async) |

### 5.2 Collections Overview

The database contains **7 collections**:

| Collection | Purpose | Write Frequency |
|------------|---------|-----------------|
| `users` | Registered application users | Low (signup, profile updates) |
| `emails` | Raw email submissions and training data | Medium (user submissions, batch ingestion) |
| `predictions` | ML classification results | Medium (every prediction request) |
| `feedback` | User corrections on predictions | Low (user-driven) |
| `model_metadata` | Trained model versions and metrics | Very low (training events) |
| `dataset_metadata` | Dataset import provenance | Very low (ingestion events) |
| `system_logs` | Audit trail and system events | High (every request, auth event) |

---

### 5.3 Collection Schemas

#### 5.3.1 `users`

```json
{
  "user_id":        "string, required, unique",
  "email":          "string, required, unique",
  "password_hash":  "string, required",
  "full_name":      "string, optional",
  "role":           "string, required, enum: [user, analyst, ml_engineer, admin, super_admin]",
  "status":         "string, required, enum: [active, disabled, pending]",
  "auth_provider":  "string, required, default: local",
  "email_verified": "boolean, required, default: false",
  "mfa_enabled":    "boolean, optional, default: false",
  "last_login_at":  "datetime, optional",
  "created_at":     "datetime, required",
  "updated_at":     "datetime, required"
}
```

**Validation Rules:**
- `email` must be a valid email format and unique across the collection.
- `password_hash` must never be empty; plain text passwords must never be stored.
- `role` must be one of the defined enum values.
- `status` must be one of the defined enum values.

**Relationships:**
- One user → many emails (via `user_id` in emails)
- One user → many predictions (via `user_id`)
- One user → many feedback records (via `user_id`)
- One user → many system_logs entries (via `user_id`)

---

#### 5.3.2 `emails`

```json
{
  "email_id":       "string, required, unique",
  "user_id":        "string, optional (null for training data)",
  "subject":        "string, required",
  "sender":         "string, optional",
  "sender_domain":  "string, optional",
  "body_text":      "string, required",
  "links":          "[string], optional",
  "headers":        "object, optional",
  "dataset_source": "string, required, enum: [user_submitted, SpamAssassin, Enron, PhishTank]",
  "label":          "integer, optional, enum: [0 (legitimate), 1 (suspicious)]",
  "split":          "string, optional, enum: [train, validation, test]",
  "content_hash":   "string, required (for deduplication)",
  "created_at":     "datetime, required"
}
```

**Validation Rules:**
- `body_text` must not be empty for user submissions.
- `content_hash` is computed from subject + body for deduplication.
- `label` is only present for training data; null for user-submitted emails pending prediction.
- `split` is only present for training data.

**Relationships:**
- One email → one or more predictions
- Many emails ← one dataset import (via `dataset_source`)
- Many emails ← one user (via `user_id`)

---

#### 5.3.3 `predictions`

```json
{
  "prediction_id":    "string, required, unique",
  "email_id":         "string, required",
  "user_id":          "string, optional",
  "prediction_label": "string, required, enum: [suspicious, legitimate]",
  "confidence":       "float, required, range: [0.0, 1.0]",
  "risk_level":       "string, required, enum: [high, medium, low, safe]",
  "model_version":    "string, required",
  "features_used":    "object, optional (feature importance snapshot)",
  "created_at":       "datetime, required"
}
```

**Validation Rules:**
- `confidence` must be between 0.0 and 1.0.
- `risk_level` is derived: `high` (≥ 0.85), `medium` (0.60–0.84), `low` (< 0.60 and suspicious), `safe` (legitimate).
- `prediction_label` is `suspicious` if confidence ≥ `DECISION_THRESHOLD` (0.65), otherwise `legitimate`.

**Relationships:**
- One prediction → one email (via `email_id`)
- One prediction → zero or more feedback records (via `prediction_id`)
- Many predictions ← one model version (via `model_version`)

---

#### 5.3.4 `feedback`

```json
{
  "feedback_id":    "string, required, unique",
  "prediction_id":  "string, required",
  "user_id":        "string, required",
  "was_correct":    "boolean, required",
  "correct_label":  "string, optional, enum: [ham, spam, phishing, suspicious]",
  "comment":        "string, optional",
  "status":         "string, required, enum: [pending, approved, rejected]",
  "reviewed_by":    "string, optional",
  "created_at":     "datetime, required"
}
```

**Validation Rules:**
- `correct_label` is required when `was_correct` is false.
- `status` defaults to `pending` on creation.
- Only analysts and admins can update `status` and `reviewed_by`.

**Relationships:**
- One feedback → one prediction (via `prediction_id`)
- One feedback → one user (via `user_id`)
- Approved feedback → retraining candidate pool

---

#### 5.3.5 `model_metadata`

```json
{
  "model_version":    "string, required, unique",
  "algorithm":        "string, required",
  "training_date":    "datetime, required",
  "dataset_version":  "string, required",
  "precision":        "float, required",
  "recall":           "float, required",
  "f1_score":         "float, required",
  "auc_roc":          "float, required",
  "threshold":        "float, required",
  "deployed":         "boolean, required, default: false",
  "artifact_path":    "string, required",
  "notes":            "string, optional",
  "created_by":       "string, optional",
  "created_at":       "datetime, required"
}
```

**Validation Rules:**
- Only one record should have `deployed: true` at any time (the active model).
- `model_version` follows semantic versioning: `v1.0.0`, `v1.1.0`, `v2.0.0`.
- All metric values must be between 0.0 and 1.0.

**Relationships:**
- One model version → many predictions (via `model_version`)
- One model version → one dataset version (via `dataset_version`)

---

#### 5.3.6 `dataset_metadata`

```json
{
  "dataset_id":     "string, required, unique",
  "name":           "string, required",
  "source":         "string, required",
  "version":        "string, required",
  "record_count":   "integer, required",
  "spam_count":     "integer, required",
  "ham_count":      "integer, required",
  "ingestion_date": "datetime, required",
  "split_ratios":   "object, required, e.g. {train: 0.70, validation: 0.15, test: 0.15}",
  "checksum":       "string, required",
  "notes":          "string, optional",
  "created_by":     "string, optional"
}
```

**Validation Rules:**
- `split_ratios` values must sum to 1.0.
- `record_count` must equal `spam_count` + `ham_count`.
- `checksum` should be SHA-256 of the source file.

**Relationships:**
- One dataset import → many email records
- One dataset version → many model training runs

---

#### 5.3.7 `system_logs`

```json
{
  "log_id":       "string, required, unique",
  "event_type":   "string, required, enum: [login, login_failed, logout, prediction, feedback, role_change, model_deploy, error, system]",
  "user_id":      "string, optional",
  "details":      "object, required",
  "ip_address":   "string, optional",
  "timestamp":    "datetime, required",
  "severity":     "string, required, enum: [info, warning, error, critical]",
  "request_id":   "string, optional"
}
```

**Validation Rules:**
- Must never contain passwords, tokens, or secrets in `details`.
- `timestamp` must be server-generated UTC.
- High-volume: consider TTL index for automatic cleanup of old logs.

**Relationships:**
- A log entry may or may not reference a user.
- Independent from business data; logging failures must not block API responses.

---

### 5.4 MongoDB Index Strategy

Indexes are critical for query performance. The following indexes must be created during application startup or via a migration script.

#### `users`

| Index | Fields | Type | Purpose |
|-------|--------|------|---------|
| `idx_users_email` | `email` | Unique | Login lookup, prevent duplicates |
| `idx_users_user_id` | `user_id` | Unique | Primary key lookup |
| `idx_users_role` | `role` | Standard | Role-based queries and admin filtering |

#### `emails`

| Index | Fields | Type | Purpose |
|-------|--------|------|---------|
| `idx_emails_email_id` | `email_id` | Unique | Primary key lookup |
| `idx_emails_created_at` | `created_at` | Descending | History sorting and pagination |
| `idx_emails_sender_domain` | `sender_domain` | Standard | Domain analytics |
| `idx_emails_dataset_source` | `dataset_source` | Standard | Dataset filtering |
| `idx_emails_split` | `split` | Standard | Train/val/test split queries |
| `idx_emails_label` | `label` | Standard | Label distribution queries |
| `idx_emails_content_hash` | `content_hash` | Unique | Deduplication enforcement |

#### `predictions`

| Index | Fields | Type | Purpose |
|-------|--------|------|---------|
| `idx_predictions_prediction_id` | `prediction_id` | Unique | Primary key lookup |
| `idx_predictions_email_id` | `email_id` | Standard | Join with emails |
| `idx_predictions_model_version` | `model_version` | Standard | Model performance tracking |
| `idx_predictions_created_at` | `created_at` | Descending | History sorting and pagination |
| `idx_predictions_user_id` | `user_id` | Standard | User-specific history |

#### `feedback`

| Index | Fields | Type | Purpose |
|-------|--------|------|---------|
| `idx_feedback_feedback_id` | `feedback_id` | Unique | Primary key lookup |
| `idx_feedback_prediction_id` | `prediction_id` | Standard | Join with predictions |
| `idx_feedback_user_id` | `user_id` | Standard | User-specific feedback |
| `idx_feedback_status` | `status` | Standard | Pending review queue |

#### `model_metadata`

| Index | Fields | Type | Purpose |
|-------|--------|------|---------|
| `idx_model_version` | `model_version` | Unique | Primary key lookup |
| `idx_model_deployed` | `deployed` | Standard | Find active model quickly |

#### `dataset_metadata`

| Index | Fields | Type | Purpose |
|-------|--------|------|---------|
| `idx_dataset_id` | `dataset_id` | Unique | Primary key lookup |
| `idx_dataset_name` | `name` | Standard | Dataset name lookup |
| `idx_dataset_source` | `source` | Standard | Source filtering |
| `idx_dataset_ingestion_date` | `ingestion_date` | Descending | Chronological ordering |

#### `system_logs`

| Index | Fields | Type | Purpose |
|-------|--------|------|---------|
| `idx_logs_log_id` | `log_id` | Unique | Primary key lookup |
| `idx_logs_event_type` | `event_type` | Standard | Event filtering |
| `idx_logs_timestamp` | `timestamp` | Descending | Chronological queries |
| `idx_logs_severity` | `severity` | Standard | Error/critical filtering |
| `idx_logs_ttl` | `timestamp` | TTL (90 days) | Automatic cleanup of old logs |

---

## 6. Service Boundaries

The backend is organized into logical service modules. Each service encapsulates a specific domain of responsibility. Services communicate through direct function calls within the same process — no inter-service network calls in V1.

### 6.1 Authentication Service

**Module:** `app/services/auth_service.py`

| Responsibility | Description |
|----------------|-------------|
| Registration | Create new user accounts with hashed passwords |
| Login | Validate credentials and issue JWT tokens |
| JWT Generation | Create access tokens (30m TTL) and refresh tokens (7d TTL) |
| Token Refresh | Validate refresh token and issue new access token |
| Password Reset | Generate and validate password reset tokens (future) |

**Dependencies:** `database/`, `core/security.py`

---

### 6.2 Prediction Service

**Module:** `app/services/prediction_service.py`

| Responsibility | Description |
|----------------|-------------|
| Preprocessing | Clean text (HTML removal, normalization, tokenization, lemmatization) |
| Feature Generation | TF-IDF (subject + body), URL features, header features, statistical features |
| Model Inference | Load active model, generate prediction label and confidence |
| Result Storage | Save email and prediction records to MongoDB |

**Dependencies:** `ml/`, `database/`

---

### 6.3 Feedback Service

**Module:** `app/services/feedback_service.py`

| Responsibility | Description |
|----------------|-------------|
| Feedback Collection | Accept user corrections linked to prediction IDs |
| Validation | Ensure prediction exists and user owns it |
| Retraining Candidates | Surface approved feedback for future retraining |

**Dependencies:** `database/`

---

### 6.4 Analytics Service

**Module:** `app/services/analytics_service.py`

| Responsibility | Description |
|----------------|-------------|
| Aggregation Queries | Total scans, spam rate, false positives, false negatives |
| Dashboard Data | Time-series data for charts, top domains, confidence distribution |
| Reporting | Summary statistics for admin and analyst views |

**Dependencies:** `database/`

---

### 6.5 Model Management Service

**Module:** `app/services/model_service.py`

| Responsibility | Description |
|----------------|-------------|
| Version Tracking | List all model versions and their metrics |
| Deployment Tracking | Track which model version is currently active |
| Model Loading | Load serialized model and vectorizers from `models/` directory |
| Retraining (Future) | Orchestrate retraining pipeline with approved feedback data |

**Dependencies:** `ml/`, `database/`, filesystem (`models/`)

---

## 7. Model Artifact Management

### 7.1 Artifacts

Each trained model version produces the following serialized artifacts:

| Artifact | Format | Purpose |
|----------|--------|---------|
| `subject_vectorizer.pkl` | joblib/pickle | TF-IDF vectorizer fitted on email subjects |
| `body_vectorizer.pkl` | joblib/pickle | TF-IDF vectorizer fitted on email bodies |
| `xgboost_model.pkl` | joblib/pickle | Trained XGBoost classifier |

### 7.2 Storage Location

```
backend/models/
├── v1.0.0/
│   ├── subject_vectorizer.pkl
│   ├── body_vectorizer.pkl
│   └── xgboost_model.pkl
├── v1.1.0/
│   ├── subject_vectorizer.pkl
│   ├── body_vectorizer.pkl
│   └── xgboost_model.pkl
└── .gitkeep
```

- **Local development:** Artifacts stored in `backend/models/` directory.
- **Production:** Artifacts bundled into the Docker image or mounted as a volume.
- **Metadata:** Stored in `model_metadata` collection in MongoDB Atlas.

### 7.3 Versioning

Model versions follow **semantic versioning**:

| Version | Meaning |
|---------|---------|
| `v1.0.0` | Initial production model |
| `v1.1.0` | Minor improvement (same features, retrained data) |
| `v2.0.0` | Major change (new features, new algorithm, architecture change) |

### 7.4 Active Model Selection

- The active model version is set via the `ACTIVE_MODEL_VERSION` environment variable.
- The `model_metadata` collection has a `deployed` boolean flag.
- The prediction service loads the model matching `ACTIVE_MODEL_VERSION` at startup.
- Rollback is performed by changing the environment variable and restarting.

---

## 8. Environment Configuration

### 8.1 Environment Variables

All secrets and configuration are loaded from `.env` files. **Never commit `.env` files to version control.**

| Variable | Required | Default | Description |
|----------|:--------:|---------|-------------|
| `MONGODB_URI` | Yes | — | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | Yes | `phishing_detection_db` | Target database name |
| `JWT_SECRET_KEY` | Yes | — | Access token signing key (≥256 bits) |
| `JWT_REFRESH_SECRET_KEY` | Yes | — | Refresh token signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Yes | `30` | Access token TTL in minutes |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Yes | `7` | Refresh token TTL in days |
| `DECISION_THRESHOLD` | Yes | `0.65` | Minimum probability for "suspicious" label |
| `ACTIVE_MODEL_VERSION` | Yes | `v1.0.0` | Currently deployed model version |
| `SENTRY_DSN` | No | — | Sentry project DSN for error monitoring |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Allowed CORS origins |
| `LOG_LEVEL` | No | `INFO` | Application log level |

### 8.2 `.env.example` Template

```env
# MongoDB Atlas
MONGODB_URI=mongodb+srv://user:password@cluster.mongodb.net/phishing_detection_db
MONGODB_DATABASE=phishing_detection_db

# JWT Authentication
JWT_SECRET_KEY=your-secret-key-here-minimum-256-bits
JWT_REFRESH_SECRET_KEY=your-refresh-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# ML Configuration
DECISION_THRESHOLD=0.65
ACTIVE_MODEL_VERSION=v1.0.0

# Monitoring
SENTRY_DSN=

# Server
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

---

## 9. CI/CD Pipeline

### 9.1 Pipeline Stages

The CI/CD pipeline runs on every push to `main` and on pull requests to `main`.

```
┌─────────┐    ┌────────────┐    ┌──────────────────┐    ┌─────────┐
│  Lint   │───→│ Unit Tests │───→│ Integration Tests│───→│  Build  │
└─────────┘    └────────────┘    └──────────────────┘    └────┬────┘
                                                              │
┌──────────────────────┐    ┌─────────────┐    ┌──────────────┴────────┐
│ Docker Image Created │───→│  Deployment │───→│ Post-Deploy Health    │
│                      │    │  (Render)   │    │ Check (GET /health)   │
└──────────────────────┘    └─────────────┘    └───────────────────────┘
```

### 9.2 Stage Details

| Stage | Tool | Trigger | Pass Criteria |
|-------|------|---------|---------------|
| **Lint** | ruff (Python), eslint (TypeScript) | PR + push to main | Zero lint errors |
| **Unit Tests** | pytest (backend), vitest (frontend) | PR + push to main | All tests pass |
| **Integration Tests** | pytest with test MongoDB | PR + push to main | All tests pass |
| **Build** | Docker build | Push to main only | Image builds successfully |
| **Docker Image Creation** | Docker + Render | Push to main only | Image pushes to registry |
| **Deployment** | Render auto-deploy | Push to main only | Service starts successfully |
| **Post-Deploy Health Check** | HTTP request to `/health` | After deployment | Returns 200 OK |

### 9.3 Branch Strategy

| Branch | Purpose | Deploys To |
|--------|---------|------------|
| `main` | Production-ready code | Render (production) |
| `feature/*` | Feature development | None (PR only) |
| `fix/*` | Bug fixes | None (PR only) |

---

## 10. Security Architecture

### 10.1 Authentication

| Mechanism | Details |
|-----------|---------|
| **Password Hashing** | bcrypt with salt rounds |
| **JWT Access Token** | Signed with `JWT_SECRET_KEY`, expires in 30 minutes |
| **JWT Refresh Token** | Signed with `JWT_REFRESH_SECRET_KEY`, expires in 7 days |
| **Token Validation** | Middleware checks every protected request |

### 10.2 Authorization (RBAC)

| Role | Access Level |
|------|-------------|
| `user` | Submit emails, view own predictions, submit feedback |
| `analyst` | All user permissions + view all predictions, analytics, review feedback |
| `ml_engineer` | All analyst permissions + model management, retraining, dataset management |
| `admin` | All ml_engineer permissions + user management, audit logs, system settings |
| `super_admin` | All admin permissions + infrastructure management, deployment config |

### 10.3 Additional Security Controls

| Control | Implementation |
|---------|---------------|
| **Rate Limiting** | slowapi — per-IP and per-user limits on prediction endpoints |
| **Audit Logging** | Every auth event, prediction, feedback, and role change logged to `system_logs` |
| **Secret Management** | All secrets in `.env`, never in source code |
| **MongoDB TLS** | Connection to Atlas uses TLS encryption in transit |
| **Atlas Encryption** | MongoDB Atlas encrypts data at rest by default |
| **Input Validation** | Pydantic schemas validate all incoming requests |
| **CORS** | Restricted to allowed origins only |
| **Generic Error Messages** | Never reveal system internals or account existence to end users |

---

## 11. Backup and Recovery

### 11.1 Database Backup

| Setting | Value |
|---------|-------|
| **Provider** | MongoDB Atlas |
| **Backup Strategy** | Atlas automated snapshots + point-in-time recovery |
| **Snapshot Frequency** | Daily (Atlas default) |
| **Retention** | Per Atlas tier (typically 2–5 snapshots for free/shared tier) |

### 11.2 Recovery Requirements

| Metric | Target |
|--------|--------|
| **RPO (Recovery Point Objective)** | 24 hours — maximum acceptable data loss |
| **RTO (Recovery Time Objective)** | 4 hours — maximum acceptable downtime |

### 11.3 Recovery Procedures

1. **Database Recovery:** Restore from Atlas snapshot or point-in-time recovery.
2. **Model Recovery:** Redeploy previous model version by changing `ACTIVE_MODEL_VERSION` and restarting.
3. **Application Recovery:** Redeploy from last known good commit on `main` branch.

---

## 12. Observability

### 12.1 Logging

| Component | Destination | Format |
|-----------|-------------|--------|
| **Application Logs** | stdout (captured by Render) | Structured JSON |
| **Audit Logs** | `system_logs` collection in MongoDB | Structured documents |
| **Error Logs** | Sentry + stdout | Exception with stack trace |

### 12.2 Monitoring

| Component | Platform | What It Tracks |
|-----------|----------|----------------|
| **Error Tracking** | Sentry | Unhandled exceptions, runtime errors |
| **Performance** | Sentry | API response times, slow queries |
| **Uptime** | Render health checks | Service availability |

### 12.3 Health Checks

| Endpoint | Method | Response |
|----------|--------|----------|
| `GET /health` | GET | `{"status": "ok", "database": "connected", "model": "loaded", "version": "v1.0.0"}` |

The health check verifies:
- API server is running
- MongoDB Atlas connection is active
- ML model is loaded and ready for inference

---

## 13. Implementation Rules

> **⚠️ Do not start development until:**
> - This architecture document is complete ✅
> - All collection schemas are approved ✅
> - All environment variables are defined ✅
> - All collection indexes are defined ✅

### Must Do

- Build FastAPI backend + React/TypeScript frontend
- Connect backend to MongoDB Atlas only
- Implement JWT auth with refresh tokens + RBAC
- Implement `POST /predict`, `POST /feedback`, `GET /analytics`, `GET /health`
- Write dataset fetch scripts (do not assume datasets exist)
- Implement text cleaning, URL features, header features
- Train baseline (NB) + Logistic Regression + XGBoost
- Save model artifacts with versioning
- Add Docker, Docker Compose, tests, Sentry
- Create all indexes at application startup

### Must Not Do

- Do not connect frontend directly to MongoDB Atlas
- Do not assume datasets already exist locally
- Do not use `/classify` as the main endpoint
- Do not skip authentication in V1
- Do not hardcode secrets in code
- Do not commit `.env` files
- Do not store passwords, tokens, or secrets in `system_logs`
