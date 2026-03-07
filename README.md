# 🛡️ AI Compliance Checker Tool

An AI-powered compliance assessment tool that evaluates regulatory framework documents against the **EU Code of Practice for General-Purpose AI Models (Safety & Security Chapter)** using Retrieval-Augmented Generation (RAG) and multi-agent reasoning.

> Developed as part of a Master's Thesis at the University of Vienna.

---

## ✨ Key Features

- **Multi-Provider LLM Support** — Switch between OpenAI, Anthropic, Google, and Ollama (local) models at runtime.
- **Dual Reasoning Modes** — Choose between a fast **Single Agent** mode or a rigorous **Triple Agent** pipeline (Alignment → Gap → Synthesis).
- **RAG-Based Evidence Retrieval** — Documents are chunked, embedded (OpenAI), and stored in ChromaDB for semantic similarity search.
- **Hierarchical Criteria Assessment** — 10 EU Safety & Security Commitments, each with multiple criteria, assessed individually and scored.
- **Interactive Results Dashboard** — Drill into each criterion's alignment findings, gap analysis, evidence citations, and confidence scores.
- **PDF Export** — Generate detailed PDF compliance reports with per-commitment score breakdowns.
- **Assessment History** — All past assessments are persisted and can be reviewed, compared, or deleted.
- **Framework Guide** — Browse the full EU criteria structure with expected evidence indicators.
- **Methodology Page** — Visual explanation of the RAG pipeline process and agent architecture.

---

## 📐 Architecture

```
Compliance Checker Tool/
├── backend/                    # FastAPI Backend
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
│   │   ├── parsing.py          # Hierarchical PDF parser (chapter-aware)
│   │   └── resilience.py       # Retry logic with exponential backoff
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

- **Python** 3.10+
- **Node.js** 18+
- At least one LLM API key (set in `backend/.env`):
  - `OPENAI_API_KEY` (also required for embeddings)
  - `ANTHROPIC_API_KEY` (optional)
  - `GOOGLE_API_KEY` (optional)

---

## 🚀 Setup

### 1. Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `backend/.env` file:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...     # Optional
GOOGLE_API_KEY=AI...              # Optional
LLM_PROVIDER=openai               # Default provider
LLM_MODEL=gpt-5-nano              # Default model
```

### 2. Frontend

```bash
cd frontend
npm install
```

---

## ▶️ Running the Application

**Option A: Use the startup script (recommended)**
```bash
./run.sh
```
This starts both the backend (port `8000`) and frontend (port `5173`) simultaneously.

**Option B: Start services manually**

```bash
# Terminal 1 — Backend
cd backend
source .venv/bin/activate
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

# Terminal 2 — Frontend
cd frontend
npm run dev
```

- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:5173

---

## 📖 Usage

1. Open the frontend at `http://localhost:5173`.
2. Select your preferred **LLM Provider**, **Model**, and **Reasoning Mode** (Single or Triple Agent).
3. **Upload** a regulatory framework document (PDF).
4. Wait for the **assessment** to complete (the assessment persists even if you navigate away).
5. **View** the detailed compliance report with per-criterion breakdowns.
6. **Export** the results as a PDF report.
7. Browse past assessments in the **History** tab.

---

## 🧠 How It Works

### RAG Pipeline
1. **Ingestion** — Uploaded PDFs are parsed (with chapter-aware hierarchical chunking), split into overlapping text chunks, embedded using OpenAI embeddings, and stored in ChromaDB.
2. **Retrieval** — For each EU criterion, relevant chunks are retrieved via semantic similarity search with score filtering and deduplication.
3. **Reasoning** — Retrieved evidence is analyzed by LLM agents against the EU criterion.

### Reasoning Modes

| Mode | Agents | Description |
|------|--------|-------------|
| **Single Agent** | 1 (All-in-One) | Performs alignment, gap analysis, and classification in a single prompt. Faster. |
| **Triple Agent** | 3 (Alignment → Gap → Synthesis) | Each step is handled by a specialized agent. More rigorous and auditable. |

### Compliance Classification

| Status | Meaning |
|--------|---------|
| `COMPLIANT` | All core concepts are explicitly addressed |
| `PARTIALLY_COMPLIANT` | Some concepts covered, but gaps or weaknesses exist |
| `NOT_COMPLIANT` | Does not meaningfully address the requirement |
| `NOT_EVIDENCED` | Insufficient evidence to determine alignment |
| `NOT_APPLICABLE` | Criterion does not apply to the evaluated context |

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Backend** | Python, FastAPI, LangChain, ChromaDB, Pydantic |
| **Frontend** | React 19, TypeScript, Vite, Tailwind CSS |
| **LLM Providers** | OpenAI, Anthropic, Google Gemini, Ollama |
| **Embeddings** | OpenAI (fixed across providers) |
| **Vector Store** | ChromaDB (persistent, local) |
| **PDF Generation** | jsPDF + jspdf-autotable |

---

## 📁 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/llm-options` | Returns available LLM providers and models |
| `POST` | `/upload` | Upload and ingest a PDF document |
| `POST` | `/assess` | Run compliance assessment (params: `provider`, `model`, `mode`) |
| `GET` | `/criteria` | Returns the full EU criteria JSON structure |
| `GET` | `/assessments` | List all past assessments |
| `GET` | `/assessments/{filename}` | Retrieve a specific assessment report |
| `DELETE` | `/assessments/{filename}` | Delete a specific assessment |
| `GET` | `/documents` | List uploaded documents |
| `DELETE` | `/documents/{filename}` | Delete a document |
| `POST` | `/reset-db` | Wipe vector database and uploaded files |