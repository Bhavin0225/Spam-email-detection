# Security and Access Document
## Spam Email Detection System
### Version 1.0

## Purpose

This document explains how security, authentication, permissions, database access, error handling, and edge cases should work for the Spam Email Detection System. It is written in plain English so both technical and non-technical stakeholders can understand it.

---

# 1. Authentication Strategy

## Recommended Authentication

Use:

- Email + Password Login
- JWT Access Tokens
- Refresh Tokens
- Optional Google Login (future)

### Why?

This system contains:

- User email submissions
- Prediction history
- Feedback data
- Administrative controls
- Model management

JWT authentication provides:

- Good security
- Easy FastAPI integration
- Scalability
- Industry-standard implementation

---

# 2. User Roles

The system should use Role-Based Access Control (RBAC).

## Role 1: End User

### Can Do

- Create account
- Login
- Submit emails for analysis
- View own prediction history
- Submit feedback
- Update profile

### Cannot Do

- View other users' emails
- Access system analytics
- View model details
- Retrain models
- Access database records directly
- Modify system settings

---

## Role 2: Security Analyst

### Can Do

- View submitted emails
- Review predictions
- Mark predictions as correct/incorrect
- Investigate suspicious emails
- View analytics dashboard
- Export reports

### Cannot Do

- Change application settings
- Create admin accounts
- Delete model versions
- Access infrastructure secrets

---

## Role 3: ML Engineer

### Can Do

- View training datasets
- Launch retraining jobs
- Deploy new model versions
- Review model metrics
- Manage model metadata

### Cannot Do

- Manage user accounts
- Change billing settings
- Access infrastructure credentials

---

## Role 4: Administrator

### Can Do

- Manage users
- Assign roles
- Manage system settings
- View all analytics
- Access audit logs
- Enable/disable accounts

### Cannot Do

- View passwords
- Decrypt password hashes

---

## Role 5: Super Admin (Owner)

### Can Do

- Everything administrators can do
- Manage infrastructure
- Manage deployment configuration
- Manage database permissions
- Manage secrets

### Cannot Do

- Directly view password values

---

# 3. Database Access Rules

MongoDB Atlas is the source of truth.

Principle:

"Users should only access their own data."

---

## Emails Collection

### End User

Can:

- Read own emails
- Create new email submissions

Cannot:

- Read another user's emails

---

## Predictions Collection

### End User

Can:

- Read predictions linked to their account

Cannot:

- Read predictions belonging to others

---

## Feedback Collection

### End User

Can:

- Create feedback on their own predictions

Cannot:

- Modify feedback submitted by other users

---

## Model Metadata

Only:

- ML Engineers
- Administrators

can access.

Regular users cannot access model internals.

---

# 4. Database Security Rules

## Encryption

Enable:

- Encryption in transit (TLS)
- Encryption at rest

---

## Password Storage

Never store:

- Plain text passwords

Always store:

- Salted password hashes

Recommended:

- bcrypt
- Argon2

---

## API Security

Implement:

- HTTPS only
- JWT validation
- Request validation
- Rate limiting

---

# 5. Error Handling Guide

## Authentication Errors

### Invalid Password

User sees:

```json
{
  "message": "Invalid email or password"
}
```

Never reveal whether the email exists.

---

### Expired Token

```json
{
  "message": "Session expired. Please login again."
}
```

---

### Unauthorized Access

```json
{
  "message": "You do not have permission to perform this action."
}
```

---

# Database Errors

## Atlas Connection Failure

System Action:

- Log error
- Retry connection
- Alert administrators

User Message:

```json
{
  "message": "Service temporarily unavailable."
}
```

---

## Query Timeout

System Action:

- Retry request
- Log slow query

User Message:

```json
{
  "message": "Request timed out. Please try again."
}
```

---

# Model Errors

## Model Not Loaded

System Action:

- Log critical error
- Return safe response

User Message:

```json
{
  "message": "Prediction service unavailable."
}
```

---

## Prediction Failure

System Action:

- Store failed request
- Generate error log

User Message:

```json
{
  "message": "Unable to analyze email at this time."
}
```

---

# Input Validation Errors

## Empty Email

```json
{
  "message": "Email content cannot be empty."
}
```

---

## File Too Large

```json
{
  "message": "File exceeds maximum allowed size."
}
```

---

## Unsupported Format

```json
{
  "message": "Unsupported email format."
}
```

---

# 6. Logging and Audit Requirements

Log:

- Login attempts
- Failed logins
- Password resets
- Role changes
- Model deployments
- Prediction requests
- Feedback submissions

Do Not Log:

- Passwords
- Tokens
- Sensitive secrets

---

# 7. Security Monitoring

Track:

- Failed login spikes
- API abuse
- Excessive prediction requests
- Unusual account activity
- Atlas connection failures

Generate alerts when thresholds are exceeded.

---

# 8. Edge Cases Before Launch

## Duplicate Email Submission

Handle:

- Same email submitted multiple times

Action:

- Generate new prediction
- Link records appropriately

---

## Extremely Large Email

Handle:

- Large email bodies
- Massive attachments

Action:

- Reject or truncate safely

---

## HTML-Only Emails

Handle:

- Emails containing only HTML

Action:

- Convert HTML to text before analysis

---

## Emails With No Subject

Handle:

- Empty subject field

Action:

- Continue analysis

---

## Multiple URLs

Handle:

- Hundreds of URLs in one email

Action:

- Process safely
- Limit resource usage

---

## Malformed Headers

Handle:

- Missing SPF
- Missing DKIM
- Corrupted metadata

Action:

- Continue with available features

---

## Unicode Characters

Handle:

- Multi-language emails
- Emojis
- Special characters

Action:

- Normalize text safely

---

## Database Outage

Handle:

- Atlas unavailable

Action:

- Graceful degradation
- Retry strategy
- Alert administrators

---

## Model Version Rollback

Handle:

- New model performs worse

Action:

- Roll back to previous model version

---

## Concurrent Requests

Handle:

- Multiple users predicting simultaneously

Action:

- Queue safely
- Scale API horizontally

---

# 9. Launch Security Checklist

Before production launch:

- HTTPS enabled
- JWT authentication implemented
- Password hashing enabled
- MongoDB Atlas IP restrictions configured
- Environment variables secured
- Rate limiting enabled
- Input validation complete
- Audit logging enabled
- Backup strategy tested
- Recovery plan documented
- Role permissions verified
- Penetration testing completed
- Error messages reviewed
- Secrets removed from source code

---

# Final Recommendation

For Version 1, focus on:

1. JWT Authentication
2. Role-Based Access Control
3. MongoDB Atlas Security
4. Input Validation
5. Audit Logging
6. Rate Limiting
7. Secure Error Handling

These controls provide strong security while keeping implementation complexity reasonable for an early-stage product.
