# Spam Email Detection System

A secure, full-stack SaaS web application designed to detect suspicious emails (spam, phishing, credential theft, scams) using modern machine learning (XGBoost), with persistent classification records stored in MongoDB Atlas, and structured JSON logs monitored via Sentry.

## Technology Stack

- **Backend**: FastAPI (Python 3.11) + Uvicorn + Pydantic v2 + pymongo
- **Frontend**: React (Node 20) + TypeScript + Tailwind CSS v4 + shadcn/ui
- **Database**: MongoDB Atlas Cloud Document Store
- **Machine Learning**: XGBoost, Scikit-Learn, spaCy
- **Monitoring**: Sentry Integration

## Project Architecture

```
spam_new/
├── .agent/             # Product and technical specifications
├── backend/            # FastAPI python application
└── frontend/           # React typescript single-page application
```

## Running the Application

There are two ways to execute this system: using local virtual environments or via orchestrated Docker containers.

### Method 1: Local Development Environments

#### Backend Setup
1. Navigate to the `backend/` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # macOS/Linux:
   source .venv/bin/activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `backend/.env.example` to `backend/.env` and configure:
   ```bash
   cp .env.example .env
   ```
5. Start the server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```

#### Frontend Setup
1. Navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Copy/create a `.env` file containing `VITE_API_URL=http://localhost:8000`.
4. Start the dev server:
   ```bash
   npm run dev
   ```

---

### Method 2: Local Containerized Environment (Docker Compose)

Docker Compose configures a MongoDB instance, the FastAPI backend, and the React static server served by Nginx.

1. **Configure environment files**:
   Copy the root unified template `.env.example` to `.env` in the root directory:
   ```bash
   cp .env.example .env
   ```

2. **Build and start the stack**:
   Compile the docker images and start the containers in the background:
   ```bash
   docker compose up --build -d
   ```

3. **Verify running services**:
   - **Frontend Console**: Accessible at [http://localhost:3000/](http://localhost:3000/)
   - **Backend FastAPI Service**: Live at [http://localhost:8000/health](http://localhost:8000/health)
   - **API Documentation**: Live at [http://localhost:8000/docs](http://localhost:8000/docs)
   - **MongoDB Database**: Bound to host port `27017`

4. **Stop the stack**:
   Shut down the running containers:
   ```bash
   docker compose down
   ```

---

## Testing inside Containers

You can run automated backend verification suites directly within the running backend container:

```bash
# Execute Pytest unit and integration test suites
docker compose exec backend pytest

# Check test coverage
docker compose exec backend pytest --cov=app --cov-report=term-missing
```

