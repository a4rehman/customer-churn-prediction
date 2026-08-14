---
title: Customer Churn Prediction
emoji: 📊
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.31.0
app_file: app.py
pinned: false
---

# ChurnIQ — Enterprise Customer Churn Prediction System

An enterprise-grade, end-to-end customer churn prediction platform with a production-ready ML pipeline,
a secured FastAPI backend, and a modern React dashboard.

![Stack](https://img.shields.io/badge/ML-scikit--learn%20%7C%20XGBoost-blue)
![Stack](https://img.shields.io/badge/API-FastAPI-teal)
![Stack](https://img.shields.io/badge/UI-React%20%2B%20Vite%20%2B%20Tailwind-indigo)
![Stack](https://img.shields.io/badge/Deploy-Docker%20%2B%20CI%2FCD-green)

---

## Features

### Machine Learning Pipeline (`backend/ml/`)
- **Data Generation** — realistic synthetic Telco dataset (10k customers, ~27% churn)
- **Data Cleaning** — missing values, duplicates, type coercion, sensible imputation
- **EDA** — automated report with charts + JSON summary (`backend/ml/reports/`)
- **Feature Engineering** — tenure buckets, service counts, loyalty score, charge ratios, flags
- **Feature Selection** — `SelectKBest` with mutual information (embedded in every pipeline)
- **Multiple ML Algorithms** — Logistic Regression, Random Forest, Gradient Boosting, XGBoost
- **Hyperparameter Tuning** — `RandomizedSearchCV` per model, scored on ROC-AUC
- **ROC & Precision-Recall Curves** — comparison plots across models
- **Confusion Matrix** — saved + surfaced in the UI
- **SHAP Explainability** — global summary plot + per-customer feature contributions

### Backend (`backend/app/`) — FastAPI
- **Authentication** — JWT (access tokens), bcrypt-hashed passwords, role-based access
- **Prediction API** — real-time churn scoring with per-customer SHAP explanations
- **Customer Search** — search + live risk scoring of existing customers
- **Admin Dashboard API** — model metrics, EDA, reports, prediction analytics, user management
- **Audit logging** — every prediction is persisted with features, contributions, recommendations
- Swagger docs at `/docs`

### Frontend (`frontend/`) — React + Vite + Tailwind
- Modern dark-themed dashboard with sidebar navigation
- Customer search with inline risk badges
- **Probability gauge** (animated SVG radial gauge)
- Risk categories (Low / Medium / High / Very High)
- SHAP-driven feature contribution bars
- Retention **recommendations** with priority & impact
- Admin console: model comparison, confusion matrix, ROC/PR, SHAP summary, EDA, user admin

### Deployment
- Dockerfiles (backend + frontend/nginx), `docker-compose.yml`
- GitHub Actions CI/CD — backend tests, frontend build, image publishing to GHCR
- Deployment-ready: healthchecks, production nginx config, env-driven configuration

---

## Project Structure

```
customer_chrun_prediction/
├── backend/
│   ├── app/                    # FastAPI application
│   │   ├── routers/            # health, auth, predictions, customers, admin
│   │   ├── services/           # model_service, recommendation, seed
│   │   ├── auth.py             # JWT auth + RBAC deps
│   │   ├── config.py           # env-driven settings
│   │   ├── database.py         # SQLAlchemy engine/session
│   │   ├── models.py           # User, Customer, PredictionLog
│   │   ├── schemas.py          # Pydantic models
│   │   ├── main.py             # app factory, CORS, SPA serving
│   │   └── test_api.py         # end-to-end API tests
│   ├── ml/
│   │   ├── generate_data.py    # synthetic Telco data
│   │   ├── preprocess.py       # data cleaning
│   │   ├── eda.py              # EDA report generation
│   │   ├── features.py         # feature engineering
│   │   ├── train.py            # multi-model training + tuning + eval + SHAP
│   │   ├── run_all.py          # run the full pipeline in one go
│   │   ├── artifacts/          # trained model, preprocessor, selector, metadata
│   │   └── reports/            # plots + JSON reports
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/         # gauge, risk badge, SHAP bars, charts, KPI cards
│   │   ├── pages/              # Login, Dashboard, Search, CustomerDetail, Admin
│   │   ├── api/client.js       # authenticated API client
│   │   └── auth/AuthContext.jsx
│   ├── Dockerfile
│   └── package.json
├── data/                       # generated datasets
├── deploy/nginx/nginx.conf     # production nginx config
├── scripts/                    # dev / deploy helper scripts
├── docker-compose.yml
└── .github/workflows/ci.yml    # CI/CD
```

---

## Quick Start (local development)

Prerequisites: **Python 3.12**, **Node 20+**.

### 1. Train the model

```powershell
cd backend/ml
python run_all.py            # generate data -> clean -> EDA -> train -> SHAP
```

This produces `backend/ml/artifacts/` (model, preprocessor, selector, metadata) and
`backend/ml/reports/` (plots + JSON). The best model is selected by ROC-AUC.

### 2. Start the backend

```powershell
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

On startup the app creates tables, seeds the `admin` user and imports customers.
Swagger UI: http://localhost:8000/docs

### 3. Start the frontend

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 and sign in with **`admin` / `admin123`**.

> The Vite dev server proxies `/api` to `http://localhost:8000`.

### Run backend tests

```powershell
cd backend
python test_api.py
```

---

## Deployment with Docker Compose

```powershell
docker compose up --build -d
```

| Service   | URL                            |
|-----------|--------------------------------|
| Frontend  | http://localhost:8080          |
| Backend   | http://localhost:8000/docs     |

The backend image builds the model during the build (self-contained). Config comes from
environment variables — copy `.env.example` to `.env` and adjust secrets.

### Production checklist
- Change `SECRET_KEY`, `ADMIN_PASSWORD` in your environment.
- Use a managed Postgres instance via `DATABASE_URL`.
- Point `CORS_ORIGINS` at your real frontend origin.
- Terminate TLS at your ingress/load balancer.

---

## Deploy to Fly.io

Prerequisites: install the Fly CLI and authenticate once (browser login):

```powershell
powershell -ExecutionPolicy Bypass -Command "Invoke-WebRequest https://fly.io/install.ps1 -UseBasicParsing | Invoke-Expression"
~/.fly/bin/flyctl.exe auth login
```

Then, from the repo root, either run the helper or the manual steps:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/fly_deploy.ps1
```

Manual steps (equivalent):

```powershell
flyctl apps create churniq-backend
flyctl apps create churniq-frontend
flyctl volumes create churniq_data --app churniq-backend --size 1 --region iad

flyctl secrets set --config fly.backend.toml SECRET_KEY=<random> ADMIN_PASSWORD=<strong-password>

flyctl deploy --config fly.backend.toml --remote-only   # remote build trains the model
flyctl deploy --config fly.frontend.toml --remote-only
```

| Service   | URL                            |
|-----------|--------------------------------|
| Frontend  | https://churniq-frontend.fly.dev |
| API docs  | https://churniq-backend.fly.dev/docs |

How it works:

- `fly.backend.toml` runs the FastAPI service with **1 GB RAM** (sklearn/xgboost/SHAP need headroom)
  and a persistent **SQLite volume** (`churniq_data` → `/data`) so users and prediction history survive
  redeploys. Set `DATABASE_URL` to Fly Postgres instead for multi-instance scale.
- `fly.frontend.toml` runs nginx serving the React build; it proxies `/api/*` to the backend over Fly's
  **private network** (`churniq-backend.internal:8000`) — no CORS in production.
- `--remote-only` builds on Fly's infrastructure, so **Docker is not needed locally**.
- The backend image trains the model during the image build, so the first deploy takes a few minutes.
- Sign in with `admin` / your `ADMIN_PASSWORD`.

> If the app names are taken on Fly, rename them in the `fly.*.toml` files and update the
> `BACKEND_UPSTREAM` value in `fly.frontend.toml` to match.

---

## CI/CD

`.github/workflows/ci.yml`:

1. **Backend tests** — trains the model and runs the API test suite.
2. **Frontend build** — installs deps, builds the production bundle.
3. **Docker** — on push to `main`, builds and pushes `churn-backend` and `churn-frontend`
   images to GitHub Container Registry (tagged `latest` + commit SHA).

---

## API Overview

| Method | Path                              | Auth  | Description                          |
|--------|-----------------------------------|-------|--------------------------------------|
| POST   | `/api/auth/login`                 | —     | Exchange credentials for JWT         |
| GET    | `/api/auth/me`                    | ✓     | Current user profile                 |
| GET    | `/api/health`                     | —     | Service + model health               |
| GET    | `/api/model/info`                 | —     | Model metadata, features, metrics    |
| POST   | `/api/predict`                    | ✓     | Churn score + SHAP + recommendations |
| GET    | `/api/predictions`                | ✓     | Prediction log                       |
| GET    | `/api/predictions/{id}`           | ✓     | Single prediction detail             |
| GET    | `/api/customers/search`           | ✓     | Search customers with live risk      |
| GET    | `/api/customers/{id}`             | ✓     | Customer profile                     |
| GET    | `/api/admin/stats`                | admin | Dashboard KPIs                       |
| GET    | `/api/admin/model`                | admin | Model metrics + confusion matrix     |
| GET    | `/api/admin/eda`                  | admin | EDA report JSON                      |
| GET    | `/api/admin/reports/{file}`       | admin | Report images (PNG)                  |
| GET    | `/api/admin/prediction-summary`   | admin | Time-series prediction volume        |
| GET/POST | `/api/admin/users`              | admin | User management                      |

### Example prediction request

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "CUST-001",
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 2,
    "PhoneService": "Yes",
    "InternetService": "Fiber optic",
    "OnlineSecurity": "No",
    "TechSupport": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 89.9,
    "TotalCharges": 179.8
  }'
```

---

## Notes

- This repository ships with a **synthetic dataset** so the pipeline runs out of the box.
  To use real data, replace `data/telco_customers.csv` (keep the same schema) and re-run
  `python backend/ml/train.py`.
- A pre-trained model and its artifacts are committed so the app and API tests work immediately
  after cloning. Re-run `python backend/ml/train.py` any time to retrain, and the API picks up
  the new artifacts on restart.
- Docker images retrain the model during the build for fully self-contained deployments.
