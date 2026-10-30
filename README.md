# 🔬 HealthLens — AI-Powered Health Report Analyzer

> **Final Year Engineering Project**
>
> An intelligent web application that transforms medical laboratory reports into actionable health insights using OCR, deterministic classification, and AI-powered explanations.

---

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Core Workflow](#core-workflow)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
- [Usage Guide](#usage-guide)
- [API Documentation](#api-documentation)
- [Disclaimer](#disclaimer)

---

## 🎯 Overview

**HealthLens** is an informational health report analysis system. It is **NOT** a medical diagnosis system.

Users upload their medical/laboratory reports (JPG, PNG, PDF), and the system:

1. **Reads** the report using OCR (PaddleOCR)
2. **Extracts** test names, values, and units using pattern matching
3. **Compares** values against stored medical reference ranges
4. **Classifies** each result as NORMAL, LOW, or HIGH
5. **Generates** simple AI explanations using the Qwen language model
6. **Displays** results in an interactive dashboard with charts

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                     │
│  Login → Upload → Dashboard → Charts → AI Summary       │
│  React 19 + TypeScript + Tailwind CSS + Recharts         │
│  Port: 5173                                              │
└───────────────────────┬──────────────────────────────────┘
                        │ HTTP REST API (JSON)
                        │ JWT Authentication
┌───────────────────────┴──────────────────────────────────┐
│                    BACKEND (FastAPI)                      │
│                                                          │
│  ┌──────────┐  ┌────────────┐  ┌──────────────────────┐  │
│  │ Auth API │  │ Report API │  │ Results/Trends API   │  │
│  └────┬─────┘  └─────┬──────┘  └──────────┬───────────┘  │
│       │              │                     │              │
│  ┌────┴──────────────┴─────────────────────┴───────────┐  │
│  │              SERVICE LAYER                          │  │
│  │  OCR Service → Extraction → Classification → AI    │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌─────────────┐  ┌───────────────────────────────────┐  │
│  │  SQLite DB  │  │  NVIDIA NIM API (Qwen 2.5 7B)    │  │
│  └─────────────┘  └───────────────────────────────────┘  │
│  Port: 8000                                              │
└──────────────────────────────────────────────────────────┘
```

---

## 💻 Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Frontend** | React 19 + TypeScript | UI Framework |
| **Styling** | Tailwind CSS 3 | Utility-first CSS |
| **Charts** | Recharts | Data visualization |
| **Routing** | React Router 7 | Client-side navigation |
| **HTTP Client** | Axios | API communication |
| **Backend** | Python FastAPI | REST API server |
| **Database** | SQLite + SQLAlchemy | Data persistence |
| **OCR** | PaddleOCR | Text extraction from images |
| **AI Model** | Qwen 2.5 7B (NVIDIA NIM) | Report explanations |
| **Auth** | JWT + bcrypt | User authentication |

---

## 🔄 Core Workflow

```
UPLOAD → OCR → EXTRACT → COMPARE → AI EXPLAIN → DASHBOARD
```

### Step-by-Step:

1. **UPLOAD**: User uploads a lab report (JPG/PNG/PDF)
2. **OCR**: PaddleOCR reads text from the image with preprocessing (CLAHE, adaptive threshold)
3. **EXTRACT**: Regex patterns find test names, values, and units
4. **COMPARE**: Values are compared against 26+ stored reference ranges from MedlinePlus/Mayo Clinic
5. **AI EXPLAIN**: Qwen 2.5 generates informational explanations for each result
6. **DASHBOARD**: Results displayed with charts, color-coded status badges, and AI summary

---

## 📁 Project Structure

```
healthlens/
├── README.md
├── backend/
│   ├── .env                          # Environment variables (API keys)
│   ├── requirements.txt              # Python dependencies
│   └── app/
│       ├── main.py                   # FastAPI app entry point
│       ├── config.py                 # Settings loader
│       ├── database.py               # SQLAlchemy setup
│       ├── models/                   # Database models
│       │   ├── user.py               #   User model
│       │   ├── report.py             #   Report model
│       │   ├── test_result.py        #   Test result model
│       │   └── reference_range.py    #   Reference range model
│       ├── schemas/                  # Pydantic request/response schemas
│       │   ├── user.py
│       │   ├── report.py
│       │   └── test_result.py
│       ├── api/                      # API route handlers
│       │   ├── auth.py               #   Register, login, get profile
│       │   ├── reports.py            #   Upload, list, get, compare, delete
│       │   ├── results.py            #   Get result, trends
│       │   └── demo.py              #   Load/clear demo data
│       ├── services/                 # Business logic layer
│       │   ├── ocr_service.py        #   PaddleOCR wrapper
│       │   ├── extraction_service.py #   Regex-based data extraction
│       │   ├── classification_service.py  # Deterministic LOW/NORMAL/HIGH
│       │   ├── ai_service.py         #   NVIDIA NIM API (Qwen)
│       │   └── report_service.py     #   Full pipeline orchestrator
│       ├── utils/
│       │   ├── security.py           #   JWT + bcrypt auth
│       │   └── test_name_normalizer.py  # Alias resolution
│       └── seed/
│           ├── reference_ranges.json #   26 medical reference ranges
│           └── demo_data.json        #   6 sample demo reports
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   └── src/
│       ├── App.tsx                   # Root component
│       ├── router.tsx                # Route definitions
│       ├── index.css                 # Global styles + design system
│       ├── lib/
│       │   ├── api.ts                # Axios API client
│       │   └── types.ts              # TypeScript interfaces
│       ├── context/
│       │   ├── AuthContext.tsx        # Auth state management
│       │   └── ThemeContext.tsx       # Dark/light theme
│       ├── components/
│       │   ├── layout/               # Sidebar, Header, Layout
│       │   ├── auth/                 # LoginForm, RegisterForm, ProtectedRoute
│       │   ├── upload/               # FileDropZone, FilePreview, UploadProgress
│       │   ├── dashboard/            # SummaryCards, TestResultsTable, TestDetailPanel
│       │   ├── charts/               # NormalVsAbnormalChart, TestValuesChart, TrendChart
│       │   ├── reports/              # ReportList, ReportComparison
│       │   ├── ai/                   # AISummary
│       │   └── common/               # Disclaimer, LoadingSpinner, ErrorMessage, ThemeToggle
│       └── pages/
│           ├── LoginPage.tsx
│           ├── RegisterPage.tsx
│           ├── DashboardPage.tsx
│           ├── UploadPage.tsx
│           ├── ReportsPage.tsx
│           ├── TestResultsPage.tsx
│           ├── TrendsPage.tsx
│           ├── AISummaryPage.tsx
│           └── SettingsPage.tsx
```

---

## 🚀 Setup Instructions

### Prerequisites

- **Node.js** ≥ 18
- **Python** ≥ 3.10
- **pip** (Python package manager)

### 1. Clone / Navigate to Project

```bash
cd healthlens
```

### 2. Backend Setup

```bash
cd backend

# Install Python dependencies (core)
pip install fastapi[standard] sqlalchemy bcrypt pyjwt openai python-dotenv python-multipart aiofiles httpx pillow

# Optional: Install OCR dependencies (for real report scanning)
pip install paddleocr opencv-python

# The .env file is already configured with the NVIDIA API key

# Start the backend server
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Start the development server
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs

### 5. Quick Start (Demo)

1. Open http://localhost:5173
2. Click **Register** → Create an account
3. Go to **Settings** → Click **Load Demo Data**
4. Navigate to **Dashboard** to see analyzed reports

---

## 📖 Usage Guide

### Uploading a Real Report
1. Navigate to **Upload** page
2. Drag-and-drop or click to select your lab report image (JPG/PNG/PDF)
3. Click **Analyze Report**
4. Wait for the pipeline: Upload → OCR → Extract → Compare → AI Explain
5. View results on the Dashboard

### Understanding the Dashboard
- **Summary Cards**: Total tests, Normal/Low/High counts
- **Test Results Table**: Click any row for detailed AI explanation
- **Charts**: Visual representation of your results vs reference ranges
- **AI Summary**: Auto-generated overview of your entire report

### Comparing Reports
- Go to **Reports** page
- Select two reports to compare side by side
- View which values improved or worsened

### Tracking Trends
- Go to **Trends** page
- Select a test name to see historical values across all reports
- Track how your health metrics change over time

---

## 📡 API Documentation

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create new user |
| POST | `/api/auth/login` | Login (returns JWT) |
| GET | `/api/auth/me` | Get current user |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/reports/upload` | Upload & analyze report |
| GET | `/api/reports/` | List all reports |
| GET | `/api/reports/{id}` | Get report with results |
| GET | `/api/reports/compare` | Compare two reports |
| DELETE | `/api/reports/{id}` | Delete a report |

### Results
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/results/{id}` | Get single result |
| GET | `/api/results/trends/{test_name}` | Get historical trend |

### Demo
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/demo/load` | Load 6 demo reports |
| DELETE | `/api/demo/clear` | Clear demo data |

> Full interactive docs available at **http://localhost:8000/docs** (Swagger UI)

---

## ⚠️ Disclaimer

> **This application provides informational interpretation of laboratory results and is not a substitute for professional medical advice, diagnosis, or treatment.**
>
> - Reference ranges may vary between laboratories
> - AI-generated explanations are for educational purposes only
> - Always consult a qualified healthcare professional for proper diagnosis
> - Do not make medical decisions based solely on this application's output
> - Reference ranges sourced from MedlinePlus and Mayo Clinic (general adult values)

---

## 👤 Author

Final Year Engineering Project — HealthLens

---

## 📄 License

This project is for educational purposes only.
