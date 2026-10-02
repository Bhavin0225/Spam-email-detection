# Understanding Document
## Spam Email Detection System — Codebase Analysis

**Generated:** 2026-06-07  
**Last Updated:** 2026-06-07 (all gaps resolved — ready for implementation)  
**Source:** Full repository analysis of `f:\spam_new`  
**Status:** Pre-implementation (planning phase only — no source code exists yet)

---

## 1. Project Summary

The Spam Email Detection System is a **SaaS web application** powered by machine learning that classifies incoming emails as **suspicious** (spam, phishing, scam, malicious URLs, credential theft) or **legitimate**. It targets students, small teams, developers, and security-conscious organizations who need a lightweight, intelligent email risk screening tool.

### Core Value Proposition

- Detect spam and phishing emails with high precision
- Explain why an email was flagged (at a basic level)
- Allow users to correct mistakes via feedback
- Improve the model over time through feedback-driven retraining

### Technology Stack (Confirmed)

| Layer             | Technology                                    | Version/Notes     |
|-------------------|-----------------------------------------------|-------------------|
| **Backend API**   | FastAPI (Python)                              | Python 3.11       |
| **Database**      | MongoDB Atlas                                 | `phishing_detection_db` |
| **ML Models**     | XGBoost (production), Logistic Regression, Naive Bayes (baseline) | Binary classification |
| **NLP**           | spaCy, NLTK, Scikit-Learn (TF-IDF)           |                   |
| **Feature Eng.**  | Text stats, URL analysis, email header analysis |                 |
| **Frontend**      | React + TypeScript + Tailwind CSS + shadcn/ui | Node 20, Tailwind v4 |
| **Charts**        | Recharts                                      |                   |
| **Data Fetching** | React Query or SWR + Axios                    |                   |
| **Deployment**    | Docker + Docker Compose → **Render**          | Feature branches  |
| **Auth**          | JWT (access + refresh tokens), bcrypt hashing | 30m access / 7d refresh |
| **Monitoring**    | **Sentry** + structured logging               | Confirmed for V1  |

### Current Repository State

The repository contains **only planning and specification documents** inside the `.agent/` directory. No source code, configuration files, or ML artifacts have been created yet. The project is in the **pre-build / design-complete** stage.

---

## 2. Knowledge Graph — Major Entities and Relationships

The following graph describes the key domain entities and how they relate to each other.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         KNOWLEDGE GRAPH                                     │
│                   Entities & Relationships                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────┐    submits     ┌──────────┐   stored in    ┌──────────────┐
  │   User   │──────────────→│  Email   │──────────────→│   emails     │
  │ (5 roles)│               │ (raw     │               │  collection  │
  └────┬─────┘               │  input)  │               └──────────────┘
       │                     └────┬─────┘
       │                          │ triggers
       │                          ▼
       │                     ┌──────────────┐  stored in  ┌──────────────┐
       │                     │  Prediction  │────────────→│ predictions  │
       │                     │  (label +    │             │  collection  │
       │                     │   confidence)│             └──────────────┘
       │                     └──────┬───────┘
       │                            │
       │ provides feedback          │ generates
       │ on prediction              ▼
       │                     ┌──────────────┐  stored in  ┌──────────────┐
       └────────────────────→│  Feedback   │────────────→│  feedback    │
                             │  (correct/  │             │  collection  │
                             │   incorrect)│             └──────────────┘
                             └─────────────┘
                                    │
                                    │ feeds into
                                    ▼
                             ┌──────────────┐  tracked in ┌──────────────┐
                             │  Retraining  │────────────→│model_metadata│
                             │  Pipeline    │             │  collection  │
                             └──────────────┘             └──────────────┘

  ┌──────────────┐ ingested via  ┌──────────────┐  tracked in  ┌────────────────┐
  │  Datasets    │──────────────→│  Ingestion   │─────────────→│dataset_metadata│
  │ (PhishTank,  │               │  Pipeline    │              │  collection    │
  │  SpamAssassin│               └──────────────┘              └────────────────┘
  │  Enron)      │
  └──────────────┘

  ┌──────────────┐  writes to    ┌──────────────┐
  │  System      │──────────────→│ system_logs  │
  │  Events      │               │  collection  │
  └──────────────┘               └──────────────┘
```

### Entity Descriptions

| Entity               | Description |
|----------------------|-------------|
| **User**             | A person interacting with the system. Has one of 5 roles: End User, Security Analyst, ML Engineer, Administrator, Super Admin. |
| **Email**            | Raw email input containing subject, body, sender, URLs, and headers. |
| **Prediction**       | The ML model's classification of an email: **suspicious** or **legitimate**, with confidence score and risk level. |
| **Feedback**         | User-submitted correction on a prediction (correct/incorrect + correct label + comment). |
| **Model**            | A trained ML classifier (XGBoost, Logistic Regression, or Naive Bayes) serialized as an artifact. |
| **Model Metadata**   | Version, algorithm, training date, dataset version, and evaluation metrics for a trained model. |
| **Dataset**          | Source email corpus (PhishTank, SpamAssassin, Enron) used for training. |
| **Dataset Metadata** | Provenance, version, and split information for ingested datasets. |
| **System Log**       | Audit trail of login attempts, predictions, feedback, role changes, and model deployments. |

### Key Relationships

| From → To                        | Relationship                                    |
|----------------------------------|-------------------------------------------------|
| User → Email                     | User submits email for analysis                 |
| Email → Prediction               | Email is processed through ML pipeline to produce prediction |
| User → Feedback                  | User provides feedback on a prediction          |
| Feedback → Prediction            | Feedback is linked to a specific prediction     |
| Feedback → Retraining Pipeline   | Approved feedback feeds model retraining        |
| Model → Prediction               | Active model version generates predictions      |
| Dataset → Model                  | Dataset is used to train models                 |
| Prediction → System Log          | Each prediction is audit-logged                 |
| User → System Log                | Auth events and role changes are logged         |

---

## 3. Structure Graph — Modules/Components and Interconnections

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        SYSTEM ARCHITECTURE                                  │
│                  Components & Data Flow                                     │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │                     FRONTEND (React + TS)                │
  │                                                         │
  │  ┌────────┐ ┌────────────┐ ┌─────────┐ ┌────────────┐  │
  │  │ Auth   │ │  Analyze   │ │ History │ │ Analytics  │  │
  │  │ Pages  │ │  Email     │ │ Page    │ │ Page       │  │
  │  └────────┘ └────────────┘ └─────────┘ └────────────┘  │
  │  ┌────────┐ ┌────────────┐ ┌─────────┐                 │
  │  │Feedback│ │ Dashboard  │ │ Admin   │                 │
  │  │ Page   │ │            │ │ Pages   │                 │
  │  └────────┘ └────────────┘ └─────────┘                 │
  │                                                         │
  │  Services: apiClient, authService, predictionService,   │
  │            analyticsService                              │
  └───────────────────────┬─────────────────────────────────┘
                          │ HTTP (REST API)
                          ▼
  ┌─────────────────────────────────────────────────────────┐
  │                  FASTAPI BACKEND                         │
  │                                                         │
  │  ┌──────────────────────────────────────────────────┐   │
  │  │              API Layer                            │   │
  │  │  POST /predict   POST /feedback                  │   │
  │  │  GET /analytics  GET /health   GET /history      │   │
  │  │  GET /admin/users  GET /admin/audit-logs         │   │
  │  └────────────────────┬─────────────────────────────┘   │
  │                       │                                  │
  │  ┌────────────────────┼─────────────────────────────┐   │
  │  │         MIDDLEWARE & SECURITY                     │   │
  │  │  JWT Auth │ RBAC │ Rate Limiting │ Audit Logging │   │
  │  └────────────────────┼─────────────────────────────┘   │
  │                       │                                  │
  │  ┌────────────────────┼─────────────────────────────┐   │
  │  │              CORE SERVICES                        │   │
  │  │                    │                              │   │
  │  │  ┌─────────────┐  │  ┌─────────────────────┐    │   │
  │  │  │ Email Parser│  │  │ Prediction Engine   │    │   │
  │  │  │ (extract    │  │  │ (load model, infer) │    │   │
  │  │  │  fields)    │  │  └──────────┬──────────┘    │   │
  │  │  └──────┬──────┘  │             │               │   │
  │  │         │         │             │               │   │
  │  │         ▼         │             ▼               │   │
  │  │  ┌─────────────┐  │  ┌─────────────────────┐    │   │
  │  │  │ Text        │  │  │ Feature Combiner    │    │   │
  │  │  │ Cleaning    │──┼─→│ (TF-IDF + URL +     │    │   │
  │  │  │ Pipeline    │  │  │  Header + Stats)    │    │   │
  │  │  └─────────────┘  │  └─────────────────────┘    │   │
  │  │                    │                              │   │
  │  │  ┌─────────────┐  │  ┌─────────────────────┐    │   │
  │  │  │ URL Feature │  │  │ Header Feature      │    │   │
  │  │  │ Extractor   │  │  │ Extractor           │    │   │
  │  │  └─────────────┘  │  └─────────────────────┘    │   │
  │  │                    │                              │   │
  │  └────────────────────┼─────────────────────────────┘   │
  │                       │                                  │
  │  ┌────────────────────┼─────────────────────────────┐   │
  │  │         ML PIPELINE (Training)                    │   │
  │  │  Dataset Ingestion → Deduplication →              │   │
  │  │  Preprocessing → Feature Engineering →            │   │
  │  │  Baseline (NB) → Logistic Reg → XGBoost →        │   │
  │  │  Threshold Optimization → Model Serialization    │   │
  │  └──────────────────────────────────────────────────┘   │
  │                       │                                  │
  └───────────────────────┼──────────────────────────────────┘
                          │ pymongo
                          ▼
  ┌─────────────────────────────────────────────────────────┐
  │                  MONGODB ATLAS                           │
  │                                                         │
  │  Collections:                                           │
  │  ┌──────────┐ ┌────────────┐ ┌──────────┐              │
  │  │  emails  │ │predictions │ │ feedback │              │
  │  └──────────┘ └────────────┘ └──────────┘              │
  │  ┌──────────────┐ ┌────────────────┐ ┌─────────────┐   │
  │  │model_metadata│ │dataset_metadata│ │ system_logs │   │
  │  └──────────────┘ └────────────────┘ └─────────────┘   │
  └─────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────┐
  │        OPTIONAL INTEGRATIONS (Future)                    │
  │  OpenPhish │ PhishTank │ VirusTotal │ Google OAuth       │
  │  Sentry    │ Streamlit Dashboard                        │
  └─────────────────────────────────────────────────────────┘
```

---

## 4. Core Structures and Data Models

### 4.1 Email Record

Represents a raw email submitted for analysis or ingested from a training dataset.

| Field            | Type     | Description                                       |
|------------------|----------|---------------------------------------------------|
| `email_id`       | String   | Unique identifier for the email                   |
| `subject`        | String   | Email subject line                                |
| `sender`         | String   | Sender email address                              |
| `sender_domain`  | String   | Domain extracted from sender address               |
| `body_text`      | String   | Plain-text body content (HTML stripped)            |
| `links`          | [String] | URLs extracted from the email                     |
| `headers`        | Object   | Raw email headers (SPF, DKIM, DMARC, etc.)        |
| `dataset_source` | String   | Origin dataset (PhishTank, SpamAssassin, Enron, or user-submitted) |
| `label`          | Integer  | Ground-truth label: `0` = legitimate, `1` = suspicious — if from training data |
| `split`          | String   | Dataset split (train/validation/test)             |
| `created_at`     | DateTime | Timestamp of record creation                      |

### 4.2 Prediction Record

Stores the model's classification result for a specific email.

| Field              | Type     | Description                                      |
|--------------------|----------|--------------------------------------------------|
| `prediction_id`    | String   | Unique identifier for this prediction            |
| `email_id`         | String   | FK reference to the email record                 |
| `prediction_label` | String   | Model output: `"suspicious"` or `"legitimate"`   |
| `confidence`       | Float    | Model confidence score (0.0 – 1.0). Threshold: **0.65** |
| `risk_level`       | String   | Derived: `"high"` (≥0.85), `"medium"` (0.60–0.84), `"low"` (<0.60), `"safe"` (legitimate) |
| `model_version`    | String   | Version of the model that made this prediction   |
| `timestamp`        | DateTime | When the prediction was generated                |

### 4.3 Feedback Record (Confirmed — v2 Richer Schema)

Captures user corrections on predictions. Uses the richer schema that supports retraining.

| Field              | Type     | Description                                      |
|--------------------|----------|--------------------------------------------------|
| `feedback_id`      | String   | Unique identifier for this feedback              |
| `prediction_id`    | String   | FK reference to the prediction                   |
| `was_correct`      | Boolean  | Whether the user agrees with the prediction      |
| `correct_label`    | String   | User-provided correct label: `"ham"` \| `"spam"` \| `"phishing"` \| `"suspicious"` |
| `comment`          | String   | Optional explanation from the user               |
| `timestamp`        | DateTime | When the feedback was submitted                  |

### 4.4 Model Metadata Record

Tracks each trained model version and its performance.

| Field             | Type     | Description                                     |
|-------------------|----------|-------------------------------------------------|
| `model_version`   | String   | Version identifier (e.g., `"v1.0"`)            |
| `algorithm`       | String   | Algorithm name (XGBoost, LogisticRegression, etc.) |
| `training_date`   | DateTime | When the model was trained                      |
| `dataset_version` | String   | Which dataset version was used                  |
| `precision`       | Float    | Precision metric on evaluation set              |
| `recall`          | Float    | Recall metric on evaluation set                 |
| `F1`              | Float    | F1 score on evaluation set                      |
| `AUC`             | Float    | AUC-ROC score on evaluation set                 |

### 4.5 User Record (Formalized)

Collection: `users`. Stores registered application users, their login identity, and authorization role. Must be implemented before JWT authentication (TICKET-003).

| Field              | Type     | Required | Description                                      |
|--------------------|----------|:--------:|--------------------------------------------------|
| `user_id`          | String   | Yes      | Unique application-level user identifier         |
| `email`            | String   | Yes      | Unique login email address                       |
| `password_hash`    | String   | Yes      | bcrypt hashed password — never plain text         |
| `full_name`        | String   | No       | Display name of the user                         |
| `role`             | String   | Yes      | One of: `user`, `analyst`, `ml_engineer`, `admin`, `super_admin` |
| `status`           | String   | Yes      | Account state: `active`, `disabled`, or `pending` |
| `auth_provider`    | String   | Yes      | Auth source, e.g. `local` for V1                 |
| `email_verified`   | Boolean  | Yes      | Whether the email has been verified              |
| `mfa_enabled`      | Boolean  | No       | Whether multi-factor authentication is enabled   |
| `last_login_at`    | DateTime | No       | Last successful login timestamp                  |
| `created_at`       | DateTime | Yes      | Account creation time                            |
| `updated_at`       | DateTime | Yes      | Last profile or permission update time           |

**Relationships:**
- One user → many email submissions
- One user → many feedback records
- One user → many prediction history entries
- Admins → manage many user accounts

---

### 4.6 Dataset Metadata Record (Formalized)

Collection: `dataset_metadata`. Tracks the datasets used for training and retraining so the team always knows what data produced a given model. Every dataset import job should automatically write a record here.

| Field              | Type     | Required | Description                                      |
|--------------------|----------|:--------:|--------------------------------------------------|
| `dataset_id`       | String   | Yes      | Unique identifier for the dataset import batch   |
| `name`             | String   | Yes      | Dataset name: `SpamAssassin`, `Enron`, or `PhishTank` |
| `source`           | String   | Yes      | Source label for the dataset                     |
| `version`          | String   | Yes      | Internal version or release label                |
| `record_count`     | Integer  | Yes      | Total number of imported records                 |
| `spam_count`       | Integer  | Yes      | Number of spam/suspicious records                |
| `ham_count`        | Integer  | Yes      | Number of legitimate records                     |
| `ingestion_date`   | DateTime | Yes      | When the dataset was imported                    |
| `split_ratios`     | Object   | Yes      | Train/validation/test split definition           |
| `checksum`         | String   | Yes      | Integrity check value for the imported file set  |
| `notes`            | String   | No       | Optional comments about cleaning or filtering    |
| `created_by`       | String   | No       | Pipeline or user that imported the dataset       |

**Example `split_ratios`:**
```json
{
  "train": 0.70,
  "validation": 0.15,
  "test": 0.15
}
```

**Relationships:**
- One dataset import → many email records
- One dataset version → many model training runs

---

### 4.7 System Log Record (Formalized)

Collection: `system_logs`. Stores important system events for auditing, debugging, and security monitoring. Should never store passwords, tokens, or other secrets. Written by middleware or service layer.

| Field              | Type     | Required | Description                                      |
|--------------------|----------|:--------:|--------------------------------------------------|
| `log_id`           | String   | Yes      | Unique identifier for the log event              |
| `event_type`       | String   | Yes      | Event type: `login`, `prediction`, `feedback`, `role_change`, `model_deploy` |
| `user_id`          | String   | No       | ID of the user who triggered the event           |
| `details`          | Object   | Yes      | Structured metadata about the event              |
| `ip_address`       | String   | No       | Source IP address                                |
| `timestamp`        | DateTime | Yes      | Time the event occurred                          |
| `severity`         | String   | Yes      | Log severity: `info`, `warning`, `error`, `critical` |
| `request_id`       | String   | No       | Correlation ID for cross-service tracing         |

**Example events:** login success/failure, prediction request, feedback submission, role update, model deployment, database connection failure.

**Relationships:**
- A log entry may or may not be linked to a user
- A single user → many log events
- Logs are independent from business data and should not affect app functionality

---

## 5. Workflows and Processes

### 5.1 Email Classification Workflow (Primary User Journey)

```
User submits email (subject + body + optional sender)
        │
        ▼
  Input Validation
  (non-empty, well-formed)
        │
        ▼
  Text Cleaning Pipeline
  ├── Remove HTML tags/entities
  ├── Normalize to lowercase
  ├── Remove extra whitespace/symbols
  ├── Tokenize
  ├── Lemmatize (spaCy/NLTK)
  └── Remove stopwords (preserve negation: "not", "never")
        │
        ▼
  Feature Engineering
  ├── Subject TF-IDF features
  ├── Body TF-IDF features
  ├── Statistical text features (word count, uppercase ratio, exclamation count)
  ├── URL features (count, length, shortener usage, suspicious keywords, IP domains)
  └── Header features (SPF fail, DKIM fail, reply-to mismatch, hop count)
        │
        ▼
  Feature Combination
  (concatenate all feature vectors)
        │
        ▼
  Model Inference (XGBoost)
  ├── Apply decision threshold (0.65)
  └── Generate prediction label (suspicious/legitimate) + confidence score
        │
        ▼
  Store Results in MongoDB Atlas
  ├── Email → emails collection
  └── Prediction → predictions collection
        │
        ▼
  Return Response to User
  { prediction, confidence, risk_level, prediction_id, model_version }
```

### 5.2 Feedback Workflow

```
User views prediction result
        │
        ▼
User disagrees with classification
        │
        ▼
Submits feedback via POST /feedback
  { prediction_id, was_correct, correct_label, comment }
        │
        ▼
Feedback stored in feedback collection
  (linked to prediction_id)
        │
        ▼
(Future) Analyst reviews feedback
        │
        ▼
(Future) Approved feedback → Retraining Pipeline
        │
        ▼
(Future) New model version trained and evaluated
```

### 5.3 ML Training Pipeline (Offline)

```
Dataset Ingestion
  ├── PhishTank (phishing URLs/emails)
  ├── SpamAssassin (spam corpus)
  └── Enron (legitimate email corpus)
        │
        ▼
Deduplication Engine
  (hash-based duplicate detection)
        │
        ▼
Train/Validation/Test Split
  (split early to prevent data leakage)
        │
        ▼
Preprocessing (same pipeline as inference)
        │
        ▼
Feature Engineering
  (fit TF-IDF vectorizers on training data ONLY)
        │
        ▼
Baseline Training: Multinomial Naive Bayes
        │
        ▼
Intermediate: Logistic Regression
        │
        ▼
Production Candidate: XGBoost
        │
        ▼
Threshold Optimization
  (precision-recall trade-off analysis)
        │
        ▼
Evaluation & Comparison
  (precision, recall, F1, AUC-ROC)
        │
        ▼
Serialization
  ├── Model → joblib/pickle
  └── Vectorizers → joblib
        │
        ▼
Metadata Storage → model_metadata collection
```

### 5.4 Authentication and Authorization Flow

```
User signs up
  (email + password → bcrypt hash stored)
        │
        ▼
User logs in
  (credentials validated → JWT access + refresh tokens issued)
        │
        ▼
Each API request
  ├── JWT validated by middleware
  ├── Role extracted from token
  └── RBAC middleware checks permissions
        │
        ▼
Unauthorized → 401/403 response
Authorized → Request proceeds
```

---

## 6. Patterns, Conventions, and Design Decisions

### 6.1 Architectural Patterns

| Pattern | Description |
|---------|-------------|
| **Separation of Concerns** | Training, inference, storage, and API logic are designed to be modular and independent. |
| **Feature-Pipeline Parity** | The same preprocessing and feature engineering pipeline must be used in both training and inference to prevent train-serve skew. |
| **Model Versioning** | Every prediction is tagged with the model version that produced it, enabling rollback and A/B comparison. |
| **Feedback Loop** | The system is designed for continuous improvement: feedback → review → retrain → deploy. |
| **Defense in Depth** | Multiple security layers: JWT auth, RBAC, rate limiting, input validation, audit logging, HTTPS. |

### 6.2 Design Decisions (Confirmed)

| Decision | Rationale | Status |
|----------|-----------|--------|
| **Binary classification: suspicious vs legitimate** | Simpler, more practical, stronger for launch. "Suspicious" encompasses spam, phishing, scam, malicious URLs, and credential theft. | ✅ Confirmed |
| **Decision threshold: 0.65** | Minimum probability to mark email as suspicious. Balances precision with recall. | ✅ Confirmed |
| **Precision-first evaluation** | False positives (legitimate → suspicious) are more damaging to user trust than false negatives. | ✅ Confirmed |
| **MongoDB Atlas over SQL** | Document-oriented storage fits the semi-structured nature of email data. Cloud-managed for operational simplicity. | ✅ Confirmed |
| **XGBoost as production model** | Strong performance on tabular/structured feature vectors. Naive Bayes and Logistic Regression serve as progressive baselines. | ✅ Confirmed |
| **Separate TF-IDF for subject vs body** | Subjects carry different spam signals than body text; separate vectorizers capture this distinction. | From spec |
| **Negation-aware stopword removal** | Words like "not" and "never" invert meaning and are critical for accurate classification. | From spec |
| **JWT + Refresh Tokens (30m / 7d)** | Stateless auth scales well with FastAPI; refresh tokens allow long sessions without compromising security. | ✅ Confirmed |
| **React + TypeScript + Tailwind v4 frontend** | Type safety, component reuse, and industry-standard SPA framework. Tailwind v4 + shadcn/ui for rapid, consistent styling. | ✅ Confirmed |
| **Docker + Docker Compose** | Containerization ensures environment consistency. Compose simplifies local dev with backend + frontend together. | ✅ Confirmed |
| **Deploy to Render** | Simple, cost-effective PaaS for early-stage deployment with Docker support. | ✅ Confirmed |
| **RBAC with 5 roles** | `user`, `analyst`, `ml_engineer`, `admin`, `super_admin` — fine-grained access control with clear boundaries. | ✅ Confirmed |
| **Sentry for monitoring** | Frontend error capture and runtime error tracking from V1. | ✅ Confirmed |
| **Feature branch git strategy** | Clean separation of work, supports code review and CI. | ✅ Confirmed |

### 6.3 Conventions Observed

- **Document-driven development:** The project starts with comprehensive specifications before writing any code. All five `.agent/` documents form a complete spec: product requirements, technical architecture, frontend specification, security design, and feature tickets.
- **Ticket-based decomposition:** Work is broken into 32 tickets across 15 epics, each independently buildable. Dependencies are explicitly declared.
- **MVP-first philosophy:** The PRD and tickets explicitly define what's in and out of scope for V1, preventing feature creep.
- **Generic error messages:** Security-conscious error handling — never reveal system internals or account existence to end users.
- **8px spacing system:** The frontend spec enforces a consistent spatial rhythm for visual polish.
- **Semantic color system:** Colors are mapped to meanings (green = safe, red = danger, amber = uncertain), not arbitrary.

---

## 7. Document Inventory

The repository consists entirely of specification documents. No source code exists.

| File | Purpose | Size | Key Content |
|------|---------|------|-------------|
| [PRD.md](file:///f:/spam_new/.agent/PRD.md) | Product Requirements Document | 12.8 KB | Problem statement, goals, features, user flows, data model, risks, release plan |
| [technical_architecture.md](file:///f:/spam_new/.agent/technical_architecture.md) | **Complete Technical Architecture** | ~30 KB | System overview, tech stack, repo structure, deployment, DB schemas, indexes, service boundaries, model artifacts, env config, CI/CD, security, backup/recovery, observability |
| [Technical_Architecture_Document.md](file:///f:/spam_new/.agent/Technical_Architecture_Document.md) | Architecture stub (superseded) | 0.7 KB | Abbreviated summary — **replaced by `technical_architecture.md`** |
| [Frontend_Specification_Document.md](file:///f:/spam_new/.agent/Frontend_Specification_Document.md) | Frontend design system & spec | 18.4 KB | Design system, component specs, page-level UI, API contracts, accessibility, responsive rules |
| [Feature_Ticket_List.md](file:///f:/spam_new/.agent/Feature_Ticket_List.md) | Engineering ticket backlog | 9.7 KB | 32 tickets across 15 epics with priorities, acceptance criteria, and dependencies |
| [Security_and_Access_Document.md](file:///f:/spam_new/.agent/Security_and_Access_Document.md) | Security & access control spec | 7.2 KB | Auth strategy, 5 RBAC roles, DB access rules, error handling, edge cases, launch checklist |

---

## 8. Open Questions and Gaps

### ✅ All Questions Resolved

All 11 open questions identified during the initial codebase analysis have been resolved.

| # | Question | Resolution | Source |
|---|----------|------------|--------|
| 8.1 | Feedback schema inconsistency | ✅ **Use v2 richer schema**: `was_correct` + `correct_label` + `comment` | Project config |
| 8.2 | Technical Architecture Document incomplete | ✅ **Full document generated** at [technical_architecture.md](file:///f:/spam_new/.agent/technical_architecture.md) with 13 sections covering system overview, repo structure, deployment, DB schemas + indexes, service boundaries, model artifacts, env config, CI/CD, security, backup/recovery, observability | Architecture document |
| 8.3 | User data model not formally defined | ✅ **Formal 12-field schema** added to §4.5 with roles, status, auth_provider, MFA support | Architecture addendum |
| 8.4 | API endpoint naming (`/classify` vs `/predict`) | ✅ **`POST /predict`** is canonical | Project config |
| 8.5 | Spam vs. phishing scope | ✅ **Binary: suspicious vs legitimate**. Suspicious includes spam, phishing, scam, malicious URLs, credential theft | Project config |
| 8.6 | Risk level derivation | ✅ **Confirmed thresholds**: High ≥ 0.85, Medium 0.60–0.84, Low < 0.60. Decision threshold: 0.65 | Project config |
| 8.7 | Dataset storage strategy | ✅ **Script-first**: Write fetch scripts, don't assume datasets exist locally. Raw files on local filesystem, processed records in Atlas | Project config |
| 8.8 | Auth in V1? | ✅ **Yes**: JWT auth with refresh tokens, RBAC, full Login/Signup UI in V1 | Project config |
| 8.9 | Retraining trigger | ✅ **Manual for V1**. Automated retraining is post-MVP | Project config |
| 8.10 | `dataset_metadata` schema missing | ✅ **Formal 12-field schema** added to §4.6 with split_ratios, checksum, provenance tracking | Architecture addendum |
| 8.11 | `system_logs` schema missing | ✅ **Formal 8-field schema** added to §4.7 with severity, request_id, structured details | Architecture addendum |

---

## 9. Next Steps

Based on the analysis and confirmed project configuration, the following actions are recommended:

### Pre-Implementation Checklist — ✅ ALL COMPLETE
1. ~~Resolve schema inconsistencies~~ — ✅ Done (v2 richer feedback schema confirmed)
2. ~~Define missing schemas~~ — ✅ Done (formal schemas for `users` §4.5, `dataset_metadata` §4.6, `system_logs` §4.7)
3. ~~Standardize endpoint naming~~ — ✅ Done (`POST /predict` confirmed)
4. ~~Regenerate Technical Architecture Document~~ — ✅ Done ([technical_architecture.md](file:///f:/spam_new/.agent/technical_architecture.md) created with 13 sections)
5. ~~Decide spam vs. phishing scope~~ — ✅ Done (binary: suspicious vs legitimate)
6. ~~Define risk level mapping~~ — ✅ Done (High ≥ 0.85, Medium 0.60–0.84, Low < 0.60)

> **🚀 All blockers are resolved. Implementation can begin.**

### Implementation Dependencies (from Architecture Addendum)
- **User schema (§4.5) must be implemented before** TICKET-003 (JWT Authentication)
- **Dataset metadata (§4.6) must be written during** dataset ingestion (TICKET-006)
- **System logs (§4.7) should be written by** middleware/service layer (TICKET-026)

### Implementation Order (Recommended)
Following ticket dependencies and MVP scope:

```
Phase 1 — Foundation
  TICKET-001 (FastAPI Setup — Python 3.11)
  TICKET-002 (MongoDB Atlas Connection — phishing_detection_db)
  TICKET-005 (DB Collections & Indexes)
  TICKET-021 (Health Endpoint)

Phase 2 — Auth & Security
  TICKET-003 (JWT Authentication — 30m access / 7d refresh)
  TICKET-004 (RBAC — user, analyst, ml_engineer, admin, super_admin)
  TICKET-025 (Rate Limiting)
  TICKET-026 (Audit Logging)

Phase 3 — Data Pipeline
  Dataset Fetch Scripts:
    scripts/fetch_spamassassin.py
    scripts/fetch_enron.py
    scripts/fetch_phishtank.py
    scripts/ingest_data.py
  TICKET-006 (Dataset Ingestion)
  TICKET-007 (Deduplication — content hash)
  TICKET-008 (Email Parsing)
  TICKET-009 (Text Cleaning)

Phase 4 — Feature Engineering
  TICKET-010 (TF-IDF Features)
  TICKET-011 (URL Features)
  TICKET-012 (Header Features)

Phase 5 — ML Training
  TICKET-013 (Naive Bayes Baseline)
  TICKET-014 (Logistic Regression)
  TICKET-015 (XGBoost — production candidate)
  TICKET-016 (Threshold Optimization — 0.65 default) [Should-Have]

Phase 6 — Inference & API
  TICKET-017 (Prediction Engine — suspicious/legitimate labels)
  TICKET-018 (POST /predict)
  TICKET-019 (POST /feedback — v2 richer schema)
  TICKET-020 (GET /analytics) [Should-Have]

Phase 7 — Frontend (React + TS + Tailwind v4)
  Login / Signup pages
  Dashboard
  Analyze Email page
  History page
  Feedback page
  Analytics page
  Admin pages (role-dependent)

Phase 8 — Testing & Deployment
  TICKET-027 (Unit Tests)
  TICKET-028 (Integration Tests)
  TICKET-029 (Dockerization + Docker Compose)
  TICKET-030 (Cloud Deployment → Render)
  Sentry integration

Phase 9 — Post-MVP
  TICKET-022 (Streamlit Dashboard)
  TICKET-023 (Feedback Review Workflow)
  TICKET-024 (Automated Retraining)
  TICKET-031 (SHAP Explainability)
  TICKET-032 (Threat Intelligence — V3)
```

---

## 10. Conflict Resolution Notes

| Conflict | Resolution | Evidence | Status |
|----------|------------|----------|--------|
| `POST /classify` vs `POST /predict` | Standardize on **`POST /predict`** | Used in Tech Architecture, Frontend Spec, and Feature Tickets (3 docs). PRD is the sole outlier. | ✅ Confirmed by owner |
| Auth in V1 or not | **Auth is in V1** | Feature Tickets (TICKET-003, TICKET-004 are Must-Have), Security Document (full auth spec), and Frontend Spec (Login/Signup pages) all assume auth in V1. | ✅ Confirmed by owner |
| Feedback schema (`correct_or_incorrect` vs `was_correct` + `correct_label`) | **Use the richer v2 schema** | `correct_label` is essential for retraining — knowing an email was mislabeled is useless without knowing the correct label. | ✅ Confirmed by owner |
| Technical Architecture Document completeness | **Treat other documents as primary source** | The Tech Architecture Doc is an acknowledged stub. The PRD, Frontend Spec, Security Doc, and Feature Tickets together provide comprehensive coverage. | Unchanged |
| Spam/phishing scope | **Binary: suspicious vs legitimate** | "Suspicious" encompasses spam, phishing, scam, malicious URLs, credential theft. Labels: 0 = legitimate, 1 = suspicious. | ✅ Confirmed by owner |

---

## 11. Confirmed Project Configuration

The following configuration was confirmed by the project owner and governs all implementation decisions.

### Environment Variables (`.env`)

| Variable | Value / Format | Description |
|----------|---------------|-------------|
| `MONGODB_URI` | `mongodb+srv://user:pass@cluster.mongodb.net/dbname` | MongoDB Atlas connection string |
| `MONGODB_DATABASE` | `phishing_detection_db` | Target database name |
| `JWT_SECRET_KEY` | Long random string (≥256 bits) | Access token signing key |
| `JWT_REFRESH_SECRET_KEY` | Long random string | Refresh token signing key |
| `ACCESS_TOKEN_TTL` | `30m` | Access token time-to-live |
| `REFRESH_TOKEN_TTL` | `7d` | Refresh token time-to-live |
| `DECISION_THRESHOLD` | `0.65` | Minimum probability for "suspicious" label |
| `SENTRY_DSN` | Sentry project DSN | Error monitoring (optional but recommended) |

> ⚠️ **Rule:** Never commit `.env` files. Provide `.env.example` with placeholder values.

### Classification Configuration

| Setting | Value |
|---------|-------|
| **ML task** | Binary classification |
| **Label 0** | `legitimate` |
| **Label 1** | `suspicious` |
| **Suspicious includes** | spam, phishing, scam, malicious URLs, credential theft |
| **Decision threshold** | 0.65 |
| **Primary metric** | Precision (minimize false positives) |
| **Risk bands** | High (≥ 0.85), Medium (0.60–0.84), Low (< 0.60) |

### Dataset Fetch Scripts (Required)

| Script | Purpose | Source |
|--------|---------|--------|
| `scripts/fetch_spamassassin.py` | Download SpamAssassin public corpus | spamassassin.apache.org |
| `scripts/fetch_enron.py` | Download Enron email dataset | cs.cmu.edu/~enron |
| `scripts/fetch_phishtank.py` | Download PhishTank phishing data | phishtank.org |
| `scripts/ingest_data.py` | Parse, deduplicate, and load into MongoDB | Local → Atlas |

**Ingestion rules:**
- Store source name for every record
- Store split: train / validation / test
- Deduplicate by content hash
- Keep raw record plus processed features

### Infrastructure

| Setting | Value |
|---------|-------|
| **Python** | 3.11 |
| **Node.js** | 20 |
| **Tailwind CSS** | v4 |
| **Deployment target** | Render |
| **Local dev** | Docker Compose |
| **Git strategy** | Feature branches |
| **Monitoring** | Sentry |
| **Threat intelligence (V1)** | Not included (V3) |

### Implementation Must-Do / Must-Not-Do

**Must Do:**
- Build FastAPI backend + React/TypeScript frontend
- Connect backend to MongoDB Atlas only
- Implement JWT auth with refresh tokens + RBAC
- Implement `POST /predict`, `POST /feedback`, `GET /analytics`, `GET /health`
- Write dataset fetch scripts (do not assume datasets exist)
- Implement text cleaning, URL features, header features
- Train baseline (NB) + Logistic Regression + XGBoost
- Save model artifacts with versioning
- Add Docker, Docker Compose, tests, Sentry

**Must Not Do:**
- Do not connect frontend directly to MongoDB Atlas
- Do not assume datasets already exist locally
- Do not use `/classify` as the main endpoint
- Do not skip authentication in V1
- Do not hardcode secrets in code
- Do not commit `.env` files

### Expected Output Artifacts

- Full source code (backend + frontend)
- Folder structure
- `.env.example`
- `Dockerfile`
- `docker-compose.yml`
- Dataset fetch scripts
- Training scripts
- Inference API
- Frontend UI
- Tests
- `README.md`
