# 🛡️ AI Compliance Checker Tool

An AI-powered compliance assessment tool that evaluates regulatory framework documents against the **EU Code of Practice for General-Purpose AI Models (Safety & Security Chapter)** using Retrieval-Augmented Generation (RAG) and multi-agent reasoning.

> Developed as part of a Master's Thesis at the University of Vienna.

---

## ✨ Key Features

- **Multi-Provider LLM Support** — Switch between OpenAI, Anthropic, Google, and Ollama (local) models at runtime via the UI.
- **Dual Reasoning Modes** — Choose between a fast **Single Agent** mode or a rigorous **Triple Agent** pipeline (Alignment → Gap → Synthesis).
- **RAG-Based Evidence Retrieval** — Documents are chunked (with chapter-aware hierarchical parsing via PyMuPDF), embedded using OpenAI embeddings, and stored in ChromaDB for semantic similarity search.
- **Hierarchical Criteria Assessment** — 10 EU Safety & Security Commitments, each with multiple criteria, assessed individually and scored.
- **Interactive Results Dashboard** — Drill into each criterion's alignment findings, gap analysis, expected evidence coverage, citations, and confidence scores.
- **PDF Export** — Generate detailed PDF compliance reports with per-commitment score breakdowns.
- **Assessment History** — All past assessments are persisted and can be reviewed, compared, or deleted.
- **Framework Guide** — Browse the full EU criteria structure with expected evidence indicators.
- **Methodology Page** — Visual explanation of the RAG pipeline and agent architecture.

---

## 📐 Architecture

```
Compliance Checker Tool/
├── backend/                    # FastAPI Backend (Python 3.9+)
│   ├── agents/                 # LLM Agent Logic
│   │   ├── prompts.py          # Prompt templates (Alignment, Gap, Synthesis)
│   │   ├── reasoners.py        # Alignment & Gap Agents
│   │   └── judge.py            # Synthesis & All-in-One Agents
│   ├── api/
│   │   ├── main.py             # FastAPI endpoints (/upload, /assess, /llm-options, etc.)
│   │   └── models.py           # Pydantic data models
│   ├── core/
│   │   ├── ingestion.py        # PDF parsing, chunking, ChromaDB storage
│   │   ├── retrieval.py        # Semantic similarity search & evidence retrieval
│   │   ├── pipeline.py         # Orchestrates the full assessment pipeline
│   │   ├── llm_config.py       # Centralized LLM provider/model configuration
│   │   ├── parsing.py          # Hierarchical PDF parser (chapter-aware, uses PyMuPDF)
│   │   └── resilience.py       # Retry logic with exponential backoff (tenacity)
│   ├── criteria_new.json       # EU Code of Practice criteria definitions
│   ├── criteria_parser.py      # Criteria JSON parser
│   ├── main.py                 # Uvicorn entry point
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React + TypeScript Frontend (Vite)
│   └── src/
│       ├── components/
│       │   ├── AssessmentFlow.tsx      # Upload → Assess → Results workflow
│       │   ├── Results.tsx             # Detailed results with criterion modals
│       │   ├── AssessmentHistory.tsx   # Past assessment browser
│       │   ├── CommitmentExplorer.tsx  # EU framework criteria browser
│       │   ├── Methodology.tsx         # Pipeline methodology explainer
│       │   ├── DocumentList.tsx        # Uploaded document library
│       │   ├── LandingPage.tsx         # Home page
│       │   ├── Upload.tsx              # File upload component
│       │   └── PdfViewer.tsx           # In-app PDF viewer
│       ├── context/
│       │   └── AssessmentContext.tsx   # Global assessment state (persists across navigation)
│       └── utils/
│           └── pdfExport.ts           # PDF report generation (jsPDF)
├── Architecture/               # UML architecture diagrams (PlantUML + PNG)
├── scripts/                    # Helper scripts (criteria enrichment, extraction)
└── run.sh                      # Start both backend & frontend
```

---

## 🔧 Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| **Python** | 3.9+ | Tested with 3.11. The venv should use 3.9 or higher. |
| **Node.js** | 18+ | Required for the React frontend. |
| **OpenAI API Key** | — | **Always required** — used for embeddings (even if using another LLM provider). |
| **Anthropic API Key** | — | Optional — only needed if using Anthropic models. |
| **Google API Key** | — | Optional — only needed if using Google Gemini models. |
| **Ollama** | — | Optional — only needed for local LLM inference. See [Ollama Setup](#-using-ollama-local-models) below. |

---

## 🚀 Setup

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
```

Create a `backend/.env` file with your API keys:
```env
# Required (always needed for embeddings)
OPENAI_API_KEY=sk-...

# Optional (only if you want to use these providers)
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AI...

# Default provider and model (can be changed at runtime via the UI)
LLM_PROVIDER=openai
LLM_MODEL=gpt-5-nano
```

### 2. Frontend

```bash
cd frontend
npm install
```

---

## ▶️ Running the Application

**Option A: Use PM2 (recommended for background execution)**
```bash
# start both services defined in ecosystem.config.js
pm2 start ecosystem.config.js

# monitor processes
pm2 status
pm2 logs
```

**Option B: Use the startup script**
```bash
chmod +x run.sh   # first time only
./run.sh
```

**Option C: Start services manually**

```bash
# Terminal 1 — Backend
cd backend
source .venv/bin/activate
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

| Service | URL |
|---------|-----|
| Backend API | http://localhost:8000 |
| Frontend UI | http://localhost:5173 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## 📖 Usage

1. Open the frontend at `http://localhost:5173`.
2. Select your preferred **LLM Provider**, **Model**, and **Reasoning Mode** (Single or Triple Agent).
3. **Upload** a regulatory framework document (PDF).
4. Wait for the **assessment** to complete — the assessment persists even if you navigate to other pages.
5. **View** the detailed compliance report with per-criterion breakdowns.
6. **Export** the results as a PDF report.
7. Browse past assessments in the **History** tab.

---

## 🧠 How It Works

### RAG Pipeline

1. **Ingestion** — Uploaded PDFs are parsed using PyMuPDF with chapter-aware hierarchical chunking. Text is split into overlapping chunks (1500 chars for hierarchical, 1000 for flat), embedded using OpenAI embeddings, and stored in ChromaDB.
2. **Retrieval** — For each EU criterion, relevant chunks are retrieved via semantic similarity search (`k=5`, with 4× oversampling and score filtering ≥ 0.3).
3. **Reasoning** — Retrieved evidence is analyzed by LLM agent(s) against the EU criterion and its expected evidence indicators, producing alignment findings, gap analysis, evidence coverage metrics, and a final classification.

### Reasoning Modes

| Mode | Agents | Description |
|------|--------|-------------|
| **Single Agent** | 1 (All-in-One) | Performs alignment, gap analysis, and classification in a single prompt. Faster but less transparent. |
| **Triple Agent** | 3 (Alignment → Gap → Synthesis) | Each step is handled by a specialized agent. More rigorous, auditable, and interpretable. |

### Compliance Classification

| Status | Score | Meaning |
|--------|-------|---------|
| `COMPLIANT` | 100 | All core concepts are explicitly addressed. |
| `PARTIALLY_COMPLIANT` | 50 | Some concepts covered, but gaps or weaknesses exist. |
| `NOT_COMPLIANT` | 0 | Does not meaningfully address the requirement. |
| `NOT_EVIDENCED` | 0 | Insufficient evidence to determine alignment. |
| `NOT_APPLICABLE` | 0 | Criterion does not apply to the evaluated context. |

---

## 🦙 Using Ollama (Local Models)

To use locally hosted LLMs via [Ollama](https://ollama.com/), follow these additional steps:

### 1. Install Ollama

```bash
# macOS (via Homebrew)
brew install ollama

# Or download from https://ollama.com/download
```

### 2. Pull a Model

```bash
ollama pull llama3
```

### 3. Start the Ollama Server

```bash
ollama serve
```
This starts the Ollama API on `http://localhost:11434` by default.

### 4. Select Ollama in the UI

In the frontend, select **"Ollama (Local)"** as the provider and **"llama3"** as the model.

> **Note:** Ollama runs with `format="json"` enforced to ensure structured output for the agent pipeline. Local inference is significantly slower than cloud providers and depends on your hardware. Concurrency is limited to 4 parallel criteria to avoid saturating CPU/GPU resources.

> **Important:** Even when using Ollama for reasoning, you still need an `OPENAI_API_KEY` in your `.env` because embeddings always use OpenAI to maintain vector store consistency.

---

## ☁️ Cloud Deployment (Render)

This application is designed to be deployed on **Render**.

### 1. Backend (Web Service)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `python backend/main.py` (or `uvicorn api.main:app --host 0.0.0.0 --port $PORT` in `backend/` directory)
- **Environment Variables**:
  - `OPENAI_API_KEY`: Required for embeddings.
  - `ANTHROPIC_API_KEY`, `GOOGLE_API_KEY`: Optional.

### 2. Frontend (Static Site)
- **Build Command**: `npm install && npm run build`
- **Publish Directory**: `frontend/dist`
- **Environment Variables**:
  - `VITE_API_URL`: The URL of your deployed backend service.

> [!WARNING]
> **Ephemeral Storage**: In Render's free tier, the disk is not persistent. Any uploaded files, the ChromaDB vector store, and assessment history will be wiped whenever the service restarts or redeploys. For production usage, consider using an external database and persistent storage.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python 3.9+, FastAPI, LangChain, ChromaDB, Pydantic |
| **PDF Parsing** | PyMuPDF (hierarchical), pypdf (flat) |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS |
| **LLM Providers** | OpenAI, Anthropic, Google Gemini, Ollama |
| **Embeddings** | OpenAI (fixed across all providers) |
| **Vector Store** | ChromaDB (persistent, local) |
| **PDF Export** | jsPDF + jspdf-autotable |
| **Resilience** | tenacity (exponential backoff + jitter) |

---

## 🔌 Available Models

| Provider | Models |
|----------|--------|
| **OpenAI** | `gpt-4o`, `gpt-4o-mini`, `gpt-5-nano` |
| **Anthropic** | `claude-sonnet-4-6`, `claude-sonnet-4-20250514`, `claude-haiku-4-5-20251001` |
| **Google** | `gemini-3-flash-preview`, `gemini-2.5-flash-lite`, `gemini-2.0-flash` |
| **Ollama** | `llama3` (or any model you pull locally) |

Models can be selected at runtime via the frontend UI. Default provider and model can also be set in `backend/.env`.

---

## 📁 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/llm-options` | Returns available LLM providers and models |
| `POST` | `/upload` | Upload and ingest a PDF document |
| `POST` | `/assess` | Run compliance assessment (`provider`, `model`, `mode` params) |
| `GET` | `/criteria` | Returns the full EU criteria JSON structure |
| `GET` | `/assessments` | List all past assessments |
| `GET` | `/assessments/{filename}` | Retrieve a specific assessment report |
| `DELETE` | `/assessments/{filename}` | Delete a specific assessment |
| `GET` | `/documents` | List uploaded documents |
| `GET` | `/documents/{filename}/content` | View/download a document |
| `DELETE` | `/documents/{filename}` | Delete a document |
| `POST` | `/reset-db` | Wipe vector database and uploaded files |
| `GET` | `/test-retrieval` | Test retrieval pipeline (debug endpoint) |
| `GET` | `/framework/pdf` | Download the official Code of Practice PDF |

---

## 🗂️ Criteria Schema

The assessment criteria are defined in `backend/criteria_new.json` following this structure:

```json
{
  "commitments": [
    {
      "id": "SS-1",
      "title": "Commitment Title",
      "criteria": [
        {
          "id": "SS-1.1",
          "title": "Criterion Title",
          "requirement": "The EU requirement text...",
          "expected_evidence": ["Evidence indicator 1", "Evidence indicator 2"],
          "compliance_rubric": { ... }
        }
      ]
    }
  ]
}
```

The parser (`criteria_parser.py`) supports both hierarchical (commitment-based) and flat criteria schemas.