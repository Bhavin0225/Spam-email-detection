# Frontend Specification Document
## Spam Email Detection System
### Version 1.0

## 1. Purpose

This document defines the frontend design system, UI behavior, component standards, layout rules, and integration expectations for the Spam Email Detection System.

The frontend should feel:

- clean
- trustworthy
- security-focused
- fast
- easy for non-technical users
- suitable for both individual users and admin/analyst workflows

The interface should make spam detection feel simple while still supporting advanced review, analytics, and feedback workflows.

---

## 2. Product Experience Goals

The frontend should help users:

- submit an email for analysis quickly
- understand whether the email is safe or suspicious
- see the reason behind the prediction at a high level
- review past predictions
- give feedback on incorrect predictions
- view analytics if they are analysts or admins
- navigate the product without needing technical knowledge

The experience should avoid clutter and should prioritize confidence, clarity, and speed.

---

## 3. Design Principles

### 3.1 Security-First Visual Language
Use colors, spacing, and typography that communicate trust, caution, and clarity.

### 3.2 Minimal Cognitive Load
Every screen should answer one main question at a time.

### 3.3 Accessible by Default
All screens should support keyboard navigation, readable contrast, and clear error messaging.

### 3.4 Data Should Be Easy to Scan
Tables, cards, badges, and charts should make spam trends and risk signals easy to understand at a glance.

### 3.5 Mobile-Responsive
Core user actions such as submitting an email and viewing a prediction must work on mobile and desktop.

---

## 4. Information Architecture

### Main Areas of the App
1. **Dashboard**
2. **Submit Email**
3. **Prediction History**
4. **Feedback**
5. **Analytics**
6. **Admin / Analyst Views**
7. **Settings**
8. **Login / Signup**

### Primary Navigation
- Dashboard
- Analyze Email
- History
- Analytics
- Feedback
- Settings

### Role-Based Navigation
The UI must hide or show navigation items depending on the logged-in role.

- Regular users should see only user-facing sections.
- Analysts should see analytics and review tools.
- Administrators should see user management and audit tools.

---

## 5. Design System

## 5.1 Color Palette

The product should use a security-oriented palette with a modern SaaS look.

### Primary Colors
- **Primary Blue:** `#2563EB`
- **Primary Dark:** `#1E40AF`
- **Primary Light:** `#DBEAFE`

### Secondary Colors
- **Teal Accent:** `#0F766E`
- **Cyan Accent:** `#06B6D4`
- **Purple Accent:** `#7C3AED`

### Semantic Colors
- **Success Green:** `#16A34A`
- **Warning Amber:** `#F59E0B`
- **Danger Red:** `#DC2626`
- **Info Blue:** `#0284C7`

### Neutral Colors
- **Background:** `#F8FAFC`
- **Surface:** `#FFFFFF`
- **Muted Surface:** `#F1F5F9`
- **Border:** `#E2E8F0`
- **Text Primary:** `#0F172A`
- **Text Secondary:** `#475569`
- **Text Muted:** `#94A3B8`

### Dark Mode Optional Palette
If dark mode is enabled later, use:
- **Background:** `#0F172A`
- **Surface:** `#111827`
- **Border:** `#334155`
- **Text Primary:** `#F8FAFC`
- **Text Secondary:** `#CBD5E1`

### Color Usage Rules
- Blue is the primary action color.
- Green is for safe/benign results.
- Red is for phishing/spam warnings and destructive actions.
- Amber is for uncertain or medium-risk results.
- Neutral grays are for all supporting content.

---

## 5.2 Typography

### Font Family
Use a modern sans-serif stack:

- **Primary Font:** Inter
- **Fallbacks:** system-ui, Segoe UI, Roboto, Helvetica, Arial, sans-serif

### Type Scale
- **Display / Hero:** 32px / 40px, 700 weight
- **H1:** 28px / 36px, 700 weight
- **H2:** 24px / 32px, 600 weight
- **H3:** 20px / 28px, 600 weight
- **Body Large:** 18px / 28px, 400 weight
- **Body:** 16px / 24px, 400 weight
- **Body Small:** 14px / 20px, 400 weight
- **Caption / Meta:** 12px / 16px, 500 weight

### Typography Rules
- Use sentence case in UI labels.
- Avoid all-caps except in badges or technical labels.
- Use bold text only for important numbers, statuses, and headings.
- Long paragraphs should be broken into short blocks.

---

## 5.3 Spacing System

Use an 8px spacing system.

### Base Units
- `4px`
- `8px`
- `12px`
- `16px`
- `24px`
- `32px`
- `40px`
- `48px`
- `64px`

### Layout Rules
- Page padding: `24px` desktop, `16px` mobile
- Card padding: `20px` to `24px`
- Section spacing: `32px` to `48px`
- Small gaps between related items: `8px` to `12px`

### Spacing Principles
- Related elements should be visually grouped.
- Independent blocks should have clear breathing space.
- Avoid tight clustering of controls.

---

## 5.4 Border Radius and Elevation

### Border Radius
- **Small controls:** `8px`
- **Cards:** `16px`
- **Modals / sheets:** `20px`
- **Pills / badges:** `9999px`

### Shadow System
Use subtle shadows only.

- **Card shadow:** light soft shadow
- **Modal shadow:** deeper than cards
- **Hover shadow:** slightly stronger than default

Avoid heavy shadows that make the interface feel noisy.

---

## 5.5 Icon Style

Use a consistent outline icon set.

Recommended style:
- simple
- geometric
- modern
- minimal

Icons should be used to support meaning, not replace labels.

---

## 6. Core UI Components

## 6.1 Buttons

### Button Variants
1. **Primary Button**
   - Used for main actions such as “Analyze Email”
   - Background: Primary Blue
   - Text: White

2. **Secondary Button**
   - Used for lower-priority actions
   - Background: White or muted surface
   - Border: Border color
   - Text: Text primary

3. **Danger Button**
   - Used for destructive actions such as delete or revoke
   - Background: Red

4. **Ghost Button**
   - Used for subtle actions
   - Transparent background

### Button States
- Default
- Hover
- Focus
- Disabled
- Loading

### Button Rules
- Primary pages should have only one clear primary button.
- Use loading spinner on submit actions.
- Disabled buttons must clearly appear inactive.

---

## 6.2 Inputs

### Input Types
- Text input
- Email input
- Password input
- Textarea
- Search input
- Select dropdown
- Checkbox
- Toggle switch

### Input Design Rules
- Labels must always be visible.
- Placeholder text should never replace labels.
- Invalid inputs must show a short, human-readable error.
- Required fields must be marked clearly.

### Input Behavior
- Autofocus should be used carefully.
- Inputs should preserve typed content on validation errors.
- Long email bodies should support textarea or file paste areas.

---

## 6.3 Cards

Cards are the main building block for dashboards and history views.

### Card Types
- Prediction summary card
- Analytics card
- Stats card
- Review card
- Alert card

### Card Rules
- Use title, supporting metadata, and action area.
- Cards should visually separate different pieces of information.
- High-risk results should have a stronger border or semantic accent color.

---

## 6.4 Modals

### Modal Use Cases
- Confirm deletion
- Submit feedback details
- Review prediction explanation
- Show login or signup forms if needed
- Display advanced analytics filters

### Modal Rules
- Must support keyboard close
- Must trap focus
- Must close with Escape
- Must not hide critical information behind layers if a full page is better

---

## 6.5 Badges and Tags

### Badge Types
- Spam
- Safe
- High Risk
- Medium Risk
- Low Risk
- Verified
- Pending Review

### Badge Rules
- Color should reflect status instantly
- Badge text must remain short
- Use badges consistently across tables, cards, and prediction detail pages

---

## 6.6 Tables

Tables are needed for:
- prediction history
- analytics
- user management
- audit logs

### Table Rules
- Keep columns minimal
- Allow sorting where useful
- Use pagination for large datasets
- Support row click for details
- Sticky headers are recommended

---

## 6.7 Charts

Use charts for:
- daily spam volume
- phishing trends over time
- false positive and false negative counts
- source/domain analysis
- confidence distribution

### Chart Rules
- Prefer simple line, bar, and donut charts
- Avoid clutter
- Keep labels readable
- Do not over-animate

---

## 7. Page-Level UI Specification

## 7.1 Login Page
### Goal
Allow users to sign in securely.

### Must Include
- Email field
- Password field
- Login button
- Forgot password link
- Signup link if registration is enabled

### Behavior
- Show generic error messages on failed login
- Prevent account enumeration

---

## 7.2 Dashboard
### Goal
Give users a clear overview of activity and risk.

### Must Include
- Total scans
- Spam detected count
- Safe emails count
- Recent activity
- Quick action to analyze email

### Role Variants
- End users see their own stats
- Analysts see team or system stats
- Admins see system-wide metrics

---

## 7.3 Analyze Email Page
### Goal
Let users submit content for detection.

### Must Include
- Subject field
- Body field
- Optional sender email field
- Analyze button
- Clear button
- Result panel

### Result Panel Should Show
- Prediction label
- Confidence score
- Risk color
- Short explanation
- Time of scan

---

## 7.4 History Page
### Goal
Let users review previously analyzed emails.

### Must Include
- Search
- Filter by date, status, and risk
- Table or list view
- Detail drawer or detail page

---

## 7.5 Feedback Page
### Goal
Let users report incorrect predictions.

### Must Include
- Was this prediction correct?
- Correct label selector
- Optional notes field
- Submit feedback button

---

## 7.6 Analytics Page
### Goal
Help analysts and admins track trends.

### Must Include
- Spam trend chart
- Top suspicious sender domains
- Prediction confidence metrics
- False positive / false negative metrics

---

## 7.7 Admin Pages
### Goal
Allow secure management of users and system behavior.

### Must Include
- User management
- Role assignment
- Audit logs
- Model version display
- System settings

---

## 8. Responsive Layout Rules

### Desktop
- Use a 2-column or 3-column grid where needed
- Keep content width readable
- Keep action areas visible without excessive scrolling

### Tablet
- Collapse dense grids into stacked sections
- Keep charts readable

### Mobile
- Single-column layout
- Bottom-friendly actions
- Larger tap targets
- Simplified navigation

### Breakpoints
- Mobile: up to 640px
- Tablet: 641px to 1024px
- Desktop: 1025px and above

---

## 9. Accessibility Rules

The frontend must support:

- keyboard navigation
- visible focus states
- readable contrast ratios
- screen-reader-friendly labels
- error messages that are easy to understand
- proper form association between labels and fields

### Accessibility Minimums
- No icon-only buttons without labels
- No color-only status communication
- No hidden error states
- No text smaller than 12px for essential UI

---

## 10. Frontend State Rules

### Loading States
Show skeletons or spinners while waiting for:
- login
- prediction generation
- analytics data
- history loading

### Empty States
Provide friendly, clear messages when:
- no predictions exist
- no feedback has been submitted
- analytics data is unavailable

### Error States
Errors should be:
- clear
- non-technical
- actionable where possible

---

## 11. API Integration Specification

The frontend should consume the backend API as the primary application service. The backend is responsible for all database access and ML inference. The frontend should never connect directly to MongoDB Atlas.

Below is the integration specification for every third-party service and external dependency involved in the app.

---

## 12. Third-Party Service Integration

# 12.1 MongoDB Atlas

### What it does
Stores:
- raw emails
- predictions
- feedback
- model metadata
- dataset metadata
- system logs

### How the frontend uses it
The frontend does **not** call Atlas directly. The frontend talks to the FastAPI backend, and the backend writes to Atlas.

### Backend-endpoints involved
- `POST /predict`
- `POST /feedback`
- `GET /analytics`
- `GET /history`
- `GET /admin/users`
- `GET /admin/audit-logs`

### Data sent
The frontend sends user input to the backend, which then stores it in Atlas.

### Expected response
- saved record IDs
- prediction results
- analytics summaries
- history lists
- permission-based data

---

# 12.2 OpenPhish (Optional Threat Intelligence)

### What it does
Provides phishing URL intelligence and threat categorization.

### How it is used
The backend may query it during analysis to compare URLs found in an email against known phishing data.

### API style
This may be a paid or partner-based feed depending on access method.

### Data sent
- URL/domain extracted from email
- optional confidence or context metadata

### Expected response
- known threat flag
- threat category
- reference or source information
- risk confidence if available

### Frontend impact
Show a warning badge or additional explanation if the backend marks a URL as known malicious.

---

# 12.3 PhishTank (Optional Threat Intelligence)

### What it does
Maintains phishing URLs and known malicious sites.

### How it is used
The backend may query it when a URL is found in a submitted email.

### Data sent
- URL or domain

### Expected response
- phishing match or no match
- details if available

### Frontend impact
Use the result to enrich the explanation panel and risk indicators.

---

# 12.4 VirusTotal (Optional Threat Intelligence)

### What it does
Checks URLs or domains against multiple threat engines.

### How it is used
The backend may call it for URL scanning enrichment.

### Data sent
- URL or domain

### Expected response
- malicious / suspicious / clean status
- scan metadata
- detection counts

### Frontend impact
Show this information only in advanced or analyst views.

---

# 12.5 Google OAuth (Optional Future Login)

### What it does
Allows login using Google accounts.

### How it is used
If enabled later, the frontend redirects users to Google login and receives a token on success.

### Data sent
- user identity token
- profile email
- name if allowed by consent

### Expected response
- authenticated user session
- user profile data

### Frontend impact
Display a “Continue with Google” button if this integration is enabled.

---

# 12.6 Sentry (Optional Monitoring)

### What it does
Captures frontend crashes and runtime errors.

### How it is used
The frontend sends JavaScript error events and performance traces.

### Data sent
- error message
- stack trace
- browser info
- page route
- user session context if allowed

### Expected response
- event acceptance confirmation from Sentry

### Frontend impact
No visible UI change unless an error occurs.

---

## 13. Internal API Contract Summary

Although the user asked for third-party integration, the frontend also needs a clear understanding of backend contract endpoints.

### POST /predict
**Purpose:** Analyze an email

**Request**
```json
{
  "subject": "Verify your account",
  "body": "Click here to login",
  "sender": "support@example.com"
}
```

**Response**
```json
{
  "prediction": "spam",
  "confidence": 0.97,
  "risk_level": "high",
  "prediction_id": "pred_123",
  "model_version": "v1.0"
}
```

---

### POST /feedback
**Purpose:** Submit correction data

**Request**
```json
{
  "prediction_id": "pred_123",
  "was_correct": false,
  "correct_label": "ham",
  "comment": "This was a newsletter"
}
```

**Response**
```json
{
  "status": "success",
  "message": "Feedback saved"
}
```

---

### GET /analytics
**Purpose:** Get system summary

**Response**
```json
{
  "total_scans": 1200,
  "spam_count": 340,
  "safe_count": 860,
  "top_domains": []
}
```

---

### GET /history
**Purpose:** Get user scan history

**Response**
```json
{
  "items": []
}
```

---

## 14. Frontend Error Handling Rules

### Network Failure
Show:
- “Service unavailable. Please try again.”

### Prediction Failure
Show:
- “We could not analyze this email right now.”

### Validation Failure
Show:
- “Please fill in the required fields.”

### Unauthorized Access
Show:
- “Your session has expired. Please log in again.”

### Access Denied
Show:
- “You do not have permission to view this page.”

---

## 15. UI Copy Guidelines

All text should be:

- short
- clear
- human
- non-alarming unless risk is high
- non-technical for general users

### Good Example
“High-risk email detected”

### Bad Example
“Classifier confidence threshold exceeded for malicious corpus classification”

---

## 16. Recommended Frontend File Structure

```text
frontend/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── ui/
│   │   ├── layout/
│   │   ├── forms/
│   │   ├── cards/
│   │   ├── modals/
│   │   └── charts/
│   ├── pages/
│   │   ├── Dashboard/
│   │   ├── AnalyzeEmail/
│   │   ├── History/
│   │   ├── Analytics/
│   │   ├── Feedback/
│   │   ├── Admin/
│   │   └── Auth/
│   ├── services/
│   │   ├── apiClient.ts
│   │   ├── authService.ts
│   │   ├── analyticsService.ts
│   │   └── predictionService.ts
│   ├── hooks/
│   ├── context/
│   ├── styles/
│   ├── utils/
│   └── App.tsx
├── public/
├── package.json
└── README.md
```

---

## 17. Launch-Ready Frontend Checklist

Before launch, verify that the frontend has:

- consistent design tokens
- responsive layouts
- accessible forms
- error handling
- loading states
- role-based navigation
- secure authentication flow
- clear prediction results
- feedback submission flow
- analytics views for privileged users
- safe copy that avoids exposing sensitive internals

---

## 18. Final Recommendation

For this product, the frontend should be:

- minimal
- trustworthy
- highly readable
- analytics-friendly
- role-aware
- mobile responsive
- easy to use in one or two clicks

The best frontend stack for this app is:

- **React**
- **TypeScript**
- **Tailwind CSS**
- **shadcn/ui**
- **Recharts**
- **React Query or SWR**
- **Axios or Fetch**
- **FastAPI backend integration**

This combination gives the app a modern SaaS feel while keeping the implementation practical and scalable.
