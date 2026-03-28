<p align="center">
  <img src="assets/asb_logo.jpg" alt="ASB Logo" width="200">
</p>

# 🔮 ASB — Full-Stack AI Numerology System
ASB fuses ancient numerical frameworks with modern AI. 
A comprehensive numerology engine built on deterministic logic and enhanced with LLM interpretation.  
Supports triangle computation, predictive cycles, compatibility models, health analytics, profession mapping, and automated PDF reporting through FastAPI + Streamlit.



---

## 📚 Table of Contents
- Tech Stack
-	System Architecture
-	High-Level Request Flow
-	Numerology Subsystem
-	AI Subsystem
-	Security & Feature Gating
-	Environment & Setup
-	Project Structure
-	API Overview
-	Streamlit Frontend
-	Diagnostics & Troubleshooting
-	License

---

## ⚙️ Tech Stack
- Backend: FastAPI
- Frontend: Streamlit
- AI: OpenAI / Ollama / Mock LLM
- Numerology Engine: Custom deterministic logic
- PDF: AI-driven PDF generator
- Security: API Key + Feature Gating

## 🏗️ System Architecture
```
┌──────────────────────────────────────────────────────────────┐
│                         Frontend (UI)                        │
│   streamlit_app.py                                           │
│   - ASB-branded interface                                    │
│   - Forms: single, relationship, yearly, monthly, daily,     │
│     health, profession, AI-PDF                               │
│   - Communicates with FastAPI                                │
└──────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                       FastAPI Backend (API)                  │
│   app.py                                                     │
│   - CORS, health check                                       │
│   - Mounts main_api router                                   │
│                                                              │
│   main_api.py                                                │
│   - /numerology/* → deterministic engine                     │
│   - /ai/* → AI subsystem                                     │
│   - dev_or_api_key security                                  │
└──────────────────────────────────────────────────────────────┘
         │                               │
         ▼                               ▼
┌────────────────────────────┐   ┌────────────────────────────┐
│        Numerology          │   │            AI               │
│ - Triangle math            │   │ - LLM orchestration         │
│ - Reads, traits, polarity  │   │ - Structured prompts        │
│ - Yearly/monthly/daily     │   │ - JSON-normalized outputs   │
│ - PDF & visualization      │   │ - SWOT & interpretations    │
└────────────────────────────┘   └────────────────────────────┘

```
---

## 🌐 High-Level Request Flow

1. **User interacts via Streamlit UI**  
   Selects a report: single, relationship, yearly, monthly, daily, health, career, or AI-PDF.

2. **Streamlit sends an HTTP request → FastAPI**  
   Example request:
   ```
   GET /ai/yearly-prediction.ai.json?dob=29-10-2001&year=2025
   ```

3. **FastAPI routes the request (`main_api.py`)**
   - Applies API-key or feature gating  
   - Dispatches to the numerology or AI engine  

4. **Numerology subsystem computes deterministic model**
   - A–R mystical triangle  
   - Reads (EF, AB, CD, IJ, …)  
   - Traits and polarity  
   - Special number detection  
   - Combined triangles: yearly, monthly, daily  

5. **AI subsystem interprets the numerology JSON**
   - Provider-agnostic (OpenAI / Ollama / Mock)  
   - Domain-specific structured prompts  
   - Returns normalized, cleaned JSON output  

6. **Streamlit renders results**
   - Interpretation  
   - Quick-Glance summary  
   - SWOT  
   - PDF download  
   - Visuals: triangle + triptych diagrams  

---


## 🔢 Numerology Subsystem
The deterministic mathematical core — predictable, rule-based, and fully explainable.

### **Core Math (`core.py`)**
- Mystical triangle builder (A–R)  
- Full reduction logic  
- Combined triangles (relationship, monthly, daily, yearly)  
- Year/month/day driver triangles  

### **Reads & Traits**
- Excel-style read concatenations (EF, AB, CD, IJ...)  
- Meanings for numbers 1–9  
- Compound number traits  
- Polarity analysis  
- Special numbers engine (18/81 windows, downfall markers, influence windows)  

### **Feature Modules (`numerology/features/`)**
- `single_person_report.py` — complete deterministic report  
- `relationship_report.py` — compatibility model  
- `yearly_report.py` — year energy + special signals  
- `monthly_report.py` — month mappings (E/F/H–K/N/O/Q/R)  
- `daily_report.py` — time-band prediction  
- `health_report.py` — health zones, organ flags, risk markers  
- `profession_report.py` — Mulank–Bhagyank stars & professions  
- `special_numbers.py` — influence windows  

### **Visualization (`viz.py`)**
- Triangle PNGs  
- Triptych diagrams (yearly/monthly/daily)  
- Relationship dual-view  

### **PDF Builder (`pdf.py`)**
- Full AI-powered master report  
- Triangle images  
- Quick-glance summaries  
- Brand-styled formatting  

---

## 🤖 AI Subsystem
A structured, provider-agnostic LLM integration layer.

### **ai.py — Orchestrator**
Supports:
- Summary interpretation  
- Relationship interpretation  
- Yearly, monthly, and daily predictions  
- Health interpretations  
- Career guidance  
- AI PDF generation  

### **AI API Endpoints (`ai_api.py`)**
Under `/ai/*`:
- `/summary`  
- `/relationship`  
- `/yearly-prediction.ai.json`  
- `/monthly-prediction.ai.json`  
- `/daily-prediction.ai.json`  
- `/health-ai`  
- `/career-ai`  
- `/ai-pdf` (master PDF)  

### **Endpoint Requirements**
All AI endpoints enforce:
- API key authentication  
- Feature gating checks  

### **Prompts (`prompts.py`)**
- System prompts  
- JSON schemas  
- Output constraints  
- Domain-specific fields  

### **SWOT Engine (`swot.py`)**
- Extracts SWOT elements from AI interpretation  
- Hybrid heuristic + LLM-based analysis  

---

## 🔐 Security & Feature Gating

### **API Key (`security.py`)**
- Local/dev mode:  
  `SECURITY_BYPASS=1` → No API key required  
- Production mode:  
  Requires `X-API-Key` header  

### **Feature Gating (`feature_gate.py`)**
Controlled via environment variable:

```
ALLOWED_FEATURES=single,yearly,monthly,daily,health,ai
```

### **Usage**
Endpoints call:

```
ensure_allowed("yearly")
```

If the feature is not allowed → **403 Forbidden**

---

## 🧪 Environment & Setup

### 1️⃣ Activate virtual environment
```
ocult\Scripts\activate
```

### 2️⃣ Start backend
```
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### 3️⃣ Open API Docs
👉 http://127.0.0.1:8000/docs

---

### **Environment Variables (`.env`)**
```
LLM_PROVIDER=openai|ollama|mock
OPENAI_API_KEY=...
SECURITY_BYPASS=1
API_KEY=your_prod_key
ALLOWED_FEATURES=single,yearly,monthly,daily,health,ai
API_BASE=http://127.0.0.1:8000
```

---


## 📁 Project Structure

```
Ocult Science/
│
├── app.py                     # FastAPI app entry
├── main_api.py                # Mounts numerology + AI routers
├── streamlit_app.py           # Streamlit UI (ASB branded)
├── .env                       # Keys + feature gating
│
├── security.py                # API-key validation
├── feature_gate.py            # ALLOWED_FEATURES control
│
├── AI/
│   ├── ai.py                  # Provider orchestrator
│   ├── ai_api.py              # /ai/* endpoints
│   ├── prompts.py             # System prompts + schemas
│   ├── settings.py            # Provider/model settings
│   ├── swot.py                # SWOT extraction
│
├── numerology/
│   ├── core.py                # Triangle math
│   ├── reads.py               # Read builder
│   ├── traits.py              # Meanings, polarity, health
│   ├── viz.py                 # PNG generation
│   ├── pdf.py                 # AI-driven PDF
│   ├── num_api.py             # /numerology/* endpoints
│   └── features/
│       ├── single_person_report.py
│       ├── relationship_report.py
│       ├── yearly_report.py
│       ├── monthly_report.py
│       ├── daily_report.py
│       ├── health_report.py
│       ├── profession_report.py
│       ├── special_numbers.py
│
├── requirements.txt
└── tests/
```

---

## 📡 API Overview

### **Numerology Endpoints (`/numerology/*`)**

| Endpoint                     | Output | Description            |
|-----------------------------|--------|------------------------|
| `/mystical-triangle.json`   | JSON   | A–R triangle           |
| `/mystical-triangle.png`    | PNG    | Triangle image         |
| `/single-report.json`       | JSON   | Single-person report   |
| `/relationship-report.json` | JSON   | Compatibility          |
| `/yearly-report.json`       | JSON   | Year energy            |
| `/monthly-report.json`      | JSON   | Month energy           |
| `/daily-report.json`        | JSON   | Daily markers          |
| `/health-report.json`       | JSON   | Health diagnostics     |

---


## **AI Endpoints (`/ai/*`)**

| Endpoint                         | Output | Description                  |
|----------------------------------|--------|------------------------------|
| `/summary`                       | JSON   | AI personality interpretation |
| `/relationship`                  | JSON   | Bond interpretation           |
| `/yearly-prediction.ai.json`    | JSON   | AI yearly prediction          |
| `/monthly-prediction.ai.json`   | JSON   | AI month prediction           |
| `/daily-prediction.ai.json`     | JSON   | AI day insight               |
| `/health-ai`                    | JSON   | AI-based health analysis     |
| `/career-ai`                    | JSON   | Professions + suitability    |
| `/ai-pdf`                       | PDF    | Full master PDF              |

---


## 🎨 Streamlit Frontend

- ASB-branded UI  
- Live backend connectivity  
- Tabs for all modules  
- Debug mode showing exact API calls  
- PDF download buttons  
- Expanders for raw JSON  
- Automatic secure retries on network failures  

---


## 🩺 Diagnostics & Troubleshooting

### **Backend not responding**
- Check `.env`  
- Ensure feature gating allows the endpoint  

---

### **403 Forbidden**
- Missing `X-API-Key`  
- Feature disabled in `ALLOWED_FEATURES`  

---

### **AI returns blank response**
- Incorrect LLM provider key  
- LLM provider mismatch (e.g., OpenAI vs Ollama)  

---

### **Images missing**
- Matplotlib backend not installed  
- PIL (Pillow) missing  

---

### **Streamlit cannot reach backend**
Set the correct API base URL:

```
API_BASE=https://your-backend.onrender.com
```

---
## © License

Proprietary Software — All Rights Reserved © 2025  
**RoboAIAPaths / Ocult Science**

Unauthorized distribution is prohibited.  
For inquiries, contact: **info@roboaiapaths.com**

---


















