# Enterprise SSD DVT Test Framework

Enterprise SSD Design Verification Testing framework with Node.js web interface and Python test execution.

## 🚀 Quick Access - Live Demo

- **Frontend Dashboard:** https://test-framework-app-bxejmipt.devinapps.com
- **Backend API:** https://app-avocdewb.fly.dev

## How to Run Locally

### Prerequisites
- Node.js 18+
- Python 3.12+
- Poetry (install with: `pip install poetry`)

### Step 1: Clone Repository
```bash
git clone https://github.com/tiger423/enterprise-ssd-dvt-framework.git
cd enterprise-ssd-dvt-framework
```

### Step 2: Start Backend (Terminal 1)
```bash
cd dvt-backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Backend runs at: http://localhost:8000

### Step 3: Start Frontend (Terminal 2)
```bash
cd dvt-frontend
npm install
npm run dev
```
Frontend runs at: http://localhost:5173

### Step 4: Access Application
Open http://localhost:5173 in your browser to use the test dashboard.

## What You Can Do

- **Run Tests:** Boot Drive, Data Drive, System Robustness, Certification
- **Monitor Progress:** Real-time test status updates
- **View Results:** Detailed test results and metrics
- **Configure Tests:** Adjust test parameters and settings

## API Documentation
- Swagger UI: http://localhost:8000/docs
- API Endpoints: http://localhost:8000/redoc

---
**Repository:** https://github.com/tiger423/enterprise-ssd-dvt-framework
