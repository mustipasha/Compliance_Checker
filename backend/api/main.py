from dotenv import load_dotenv
load_dotenv()

import os
import shutil
import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from core.ingestion import ingest_document
from core.pipeline import run_compliance_check
from criteria_parser import parse_criteria
from api.models import AssessmentReport, CriterionResult, CommitmentResult

app = FastAPI(title="Compliance Checker API (Agentic)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploaded_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- LLM Provider/Model Options ---
LLM_OPTIONS = {
    "providers": [
        {"id": "openai", "name": "OpenAI", "models": ["gpt-4o", "gpt-4o-mini", "gpt-5-nano"]},
        {"id": "anthropic", "name": "Anthropic", "models": ["claude-sonnet-4-6", "claude-sonnet-4-20250514", "claude-haiku-4-5-20251001"]},
        {"id": "google", "name": "Google", "models": ["gemini-3-flash-preview", "gemini-2.5-flash-lite", "gemini-2.0-flash"]},
        {"id": "ollama", "name": "Ollama (Local)", "models": ["llama3"]},
    ]
}

@app.get("/llm-options")
async def get_llm_options():
    """Returns available LLM providers and models."""
    current_provider = os.getenv("LLM_PROVIDER", "openai")
    current_model = os.getenv("LLM_MODEL", "")
    # If no model set, pick the first from the provider's list
    if not current_model:
        for p in LLM_OPTIONS["providers"]:
            if p["id"] == current_provider:
                current_model = p["models"][0]
                break
    return {
        **LLM_OPTIONS,
        "current": {"provider": current_provider, "model": current_model}
    }

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 1. Clear existing files in UPLOAD_DIR so the library only shows the active assessment file
    if os.path.exists(UPLOAD_DIR):
        for filename in os.listdir(UPLOAD_DIR):
            existing_file_path = os.path.join(UPLOAD_DIR, filename)
            try:
                if os.path.isfile(existing_file_path) or os.path.islink(existing_file_path):
                    os.unlink(existing_file_path)
                elif os.path.isdir(existing_file_path):
                    shutil.rmtree(existing_file_path)
            except Exception as e:
                print(f'Failed to delete {existing_file_path}. Reason: {e}')

    # 2. Save the new file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        num_chunks = ingest_document(file_path)
        return {"message": "File uploaded and ingested successfully", "chunks": num_chunks}
    except Exception as e:
        print(f"Upload error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset-db")
async def reset_database():
    """Wipes the ChromaDB collection and clears uploaded files."""
    try:
        from core.ingestion import get_vector_store
        import shutil
        
        # 1. Clear Vector DB
        from core.ingestion import get_vector_store
        for strategy in ["flat", "hierarchical"]:
            try:
                get_vector_store(strategy=strategy).delete_collection()
            except Exception as e:
                print(f"Error resetting {strategy} collection: {e}")
        
        # 2. Clear Uploaded Files
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                file_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
                    
        return {"message": "Database and uploads cleared successfully."}
    except Exception as e:
        print(f"Reset error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test-retrieval")
async def test_retrieval_api(query: str, k: int = 5):
    """
    Endpoint dedicated to testing the retrieval logic and pipeline.
    """
    try:
        from core.retrieval import retrieve_evidence
        results = await retrieve_evidence(query, k=k)
        
        return {
            "query": query,
            "count": len(results),
            "results": [
                {
                    "score": round(r.relevance_score, 4),
                    "chunk_id": r.chunk_id,
                    "source": r.source,
                    "page": r.page,
                    "chapter": r.chapter,
                    "text": r.text
                } for r in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/assess", response_model=AssessmentReport)
async def run_assessment(
    provider: str = Query(None, description="LLM provider (openai, anthropic, google, ollama)"),
    model: str = Query(None, description="Model name"),
    mode: str = Query("single", description="Reasoning mode (single or triple)")
):
    try:
        selected_provider = provider or os.getenv("LLM_PROVIDER", "openai")
        selected_model = model or os.getenv("LLM_MODEL", "")
        print(f"\n🤖 Assessment using: {selected_provider} / {selected_model or '(default)'}")

        # Resolve criteria file
        criteria_file = "criteria_new.json"
        all_measures = parse_criteria(criteria_file)
        
        if not all_measures:
             raise HTTPException(status_code=500, detail="No criteria found in criteria.json.")

        # Run agentic pipeline with SAFE CONCURRENCY
        # Cloud providers (google, openai, anthropic) have RPS/RPM limits.
        # Local providers (ollama) can saturate CPU/GPU if concurrency is too high.
        # Reduced from 20 to much safer defaults.
        if selected_provider == "anthropic":
            MAX_CONCURRENT_CRITERIA = 3
        elif selected_provider in ["google", "openai"]:
            MAX_CONCURRENT_CRITERIA = 15
        else:
            MAX_CONCURRENT_CRITERIA = 4
        semaphore = asyncio.Semaphore(MAX_CONCURRENT_CRITERIA)

        async def run_with_semaphore(measure):
            async with semaphore:
                import random
                await asyncio.sleep(random.uniform(0.1, 0.1))
                return await run_compliance_check(measure, provider=selected_provider, model=selected_model, mode=mode)

        tasks = [run_with_semaphore(m) for m in all_measures]
        flat_results = await asyncio.gather(*tasks)


        
        # Map results by ID for easy lookup during grouping
        results_map = {r.criterion_id: r for r in flat_results}
        
        # Scoring and Grouping Logic
        total_weighted_score = 0
        total_measures = 0
        
        commitments_map = {}
        
        for measure_data in all_measures:
            res = results_map.get(measure_data["id"])
            if not res:
                continue
                
            # Scoring
            if res.status == "COMPLIANT":
                total_weighted_score += 1.0
            elif res.status == "PARTIALLY_COMPLIANT":
                total_weighted_score += 0.5
            total_measures += 1
            
            # Grouping
            comm_id = measure_data.get("commitment_id")
            comm_title = measure_data.get("commitment_title")
            
            # Fallback for flat schema: Use ID prefix (e.g., SS-1 from SS-1.1)
            if not comm_id:
                comm_id = measure_data["id"].split('.')[0] if '.' in measure_data["id"] else measure_data["id"]
                comm_title = f"Commitment {comm_id}"
                
            if comm_id not in commitments_map:
                commitments_map[comm_id] = {
                    "id": comm_id,
                    "title": comm_title,
                    "results": []
                }
            commitments_map[comm_id]["results"].append(res)
            
        score = (total_weighted_score / total_measures) * 100 if total_measures > 0 else 0
        
        # Convert commitments map to list of CommitmentResult and sort numerically
        commitment_results = [
            CommitmentResult(
                commitment_id=c["id"],
                title=c["title"],
                results=c["results"]
            ) for c in commitments_map.values()
        ]
        
        # Natural sort by commitment ID (SS-1, SS-2, ... SS-10)
        commitment_results.sort(key=lambda x: int(x.commitment_id.split('-')[1]) if '-' in x.commitment_id else 0)
        
        # Determine Source Document Name from Vector DB (Primary) or Upload Dir (Secondary)
        source_doc_name = "Unknown Source"
        try:
            from core.ingestion import get_vector_store
            # Access underlying collection to peek metadata
            vs = get_vector_store()
            # method get() helps us peek without full retrieval
            # fetch a small sample to see sources
            db_data = vs._collection.get(include=['metadatas'], limit=100)
            
            found_sources = set()
            for m in db_data.get('metadatas', []):
                if m and 'source' in m:
                    found_sources.add(m['source'])
            
            if len(found_sources) == 1:
                source_doc_name = list(found_sources)[0]
            elif len(found_sources) > 1:
                source_doc_name = f"{len(found_sources)} Documents"
            elif len(found_sources) == 0:
                pass 
                
        except Exception as db_e:
            print(f"Source detection error (DB): {db_e}")

        # Fallback to UPLOAD_DIR
        if source_doc_name == "Unknown Source" and os.path.exists(UPLOAD_DIR):
            files = [f for f in os.listdir(UPLOAD_DIR) if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and not f.startswith('.')]
            if len(files) == 1:
                source_doc_name = files[0]
            elif len(files) > 1:
                source_doc_name = f"{len(files)} Documents"

        report = AssessmentReport(
            compliance_score=score, 
            source_document=source_doc_name,
            provider=selected_provider,
            model=selected_model,
            mode=mode,
            commitments=commitment_results,
            criteria=flat_results
        )
        
        # Archive documents for history persistence
        try:
            import shutil
            os.makedirs(HISTORY_DOCS_DIR, exist_ok=True)
            if source_doc_name != "Unknown Source":
                # If it's a specific file, copy it
                if os.path.isfile(os.path.join(UPLOAD_DIR, source_doc_name)):
                    shutil.copy2(os.path.join(UPLOAD_DIR, source_doc_name), os.path.join(HISTORY_DOCS_DIR, source_doc_name))
                # If it's "X Documents", archive all currently in UPLOAD_DIR
                elif " Documents" in source_doc_name:
                    for f in os.listdir(UPLOAD_DIR):
                        if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and not f.startswith('.'):
                            shutil.copy2(os.path.join(UPLOAD_DIR, f), os.path.join(HISTORY_DOCS_DIR, f))
        except Exception as archive_e:
            print(f"Archiving error: {archive_e}")

        # Save to history
        save_assessment_to_history(report)
        
        return report

    except Exception as e:
        print(f"Assessment error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/criteria")
async def get_criteria():
    """Returns the full criteria JSON structure."""
    try:
        # Resolve criteria file (default to criteria.json for new schema)
        criteria_file = "criteria_new.json"
        if not os.path.exists(criteria_file):
            raise HTTPException(status_code=404, detail="Criteria file not found")
            
        with open(criteria_file, "r") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error serving criteria: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/framework/pdf")
async def get_framework_pdf():
    """Serves the official Code of Practice PDF."""
    pdf_path = os.path.join(os.path.dirname(__file__), "..", "..", "Code_of_Practice_for_GeneralPurpose_AI_Models_Safety_and_Security_Chapter.pdf")
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="Framework PDF not found")
    return FileResponse(pdf_path, media_type="application/pdf", filename="Code_of_Practice.pdf")

# --- Document Management Endpoints ---

@app.get("/documents")
async def list_documents():
    """Returns a list of uploaded documents with metadata."""
    try:
        docs = []
        if os.path.exists(UPLOAD_DIR):
            for filename in os.listdir(UPLOAD_DIR):
                if filename.startswith('.'): continue
                
                file_path = os.path.join(UPLOAD_DIR, filename)
                try:
                    if os.path.isfile(file_path):
                        stats = os.stat(file_path)
                        docs.append({
                            "filename": filename,
                            "size_bytes": stats.st_size,
                            "modified": stats.st_mtime
                        })
                except Exception as ex:
                    print(f"Error reading file {filename}: {ex}")
                    continue
        return docs
    except Exception as e:
        print(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    """Deletes a document from the filesystem and removes its chunks from the vector DB."""
    try:
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 1. Remove from Filesystem
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")
            
        # 2. Remove from Vector DB
        from core.ingestion import get_vector_store
        
        # We need to clear from both collections to be safe
        for strategy in ["flat", "hierarchical"]:
            try:
                collection = get_vector_store(strategy=strategy)._collection
                collection.delete(where={"source": filename})
            except Exception as db_e:
                print(f"Vector DB deletion warning ({strategy}): {db_e}")
            
        return {"message": f"Document {filename} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

from fastapi.responses import FileResponse

@app.get("/documents/{filename}/content")
async def get_document_content(filename: str):
    """Streams the document content for display in the frontend. Falls back to archive if missing."""
    # Check primary UPLOAD_DIR
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    # Fallback to HISTORY_DOCS_DIR
    if not os.path.exists(file_path):
        archive_path = os.path.join(HISTORY_DOCS_DIR, filename)
        if os.path.exists(archive_path):
            file_path = archive_path
        else:
            raise HTTPException(status_code=404, detail="File not found in library or archive")
        
    return FileResponse(file_path, media_type="application/pdf", filename=filename)

# --- Assessment Persistence ---

HISTORY_DIR = "./assessment_history"
HISTORY_DOCS_DIR = os.path.join(HISTORY_DIR, "documents")
os.makedirs(HISTORY_DIR, exist_ok=True)
os.makedirs(HISTORY_DOCS_DIR, exist_ok=True)

import json
from datetime import datetime

def save_assessment_to_history(report: AssessmentReport):
    """Saves the assessment report to a JSON file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean filename for filesystem safety
    safe_source = "".join([c for c in report.source_document if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
    filename = f"{safe_source}_{timestamp}.json"
    file_path = os.path.join(HISTORY_DIR, filename)
    
    with open(file_path, "w") as f:
        # Pydantic v2 use model_dump, v1 use dict()
        f.write(report.json())
    return filename

@app.get("/assessments")
async def list_assessments():
    """Returns a list of past assessments."""
    try:
        assessments = []
        if os.path.exists(HISTORY_DIR):
            for filename in sorted(os.listdir(HISTORY_DIR), reverse=True):
                if filename.endswith(".json"):
                    file_path = os.path.join(HISTORY_DIR, filename)
                    stats = os.stat(file_path)
                    
                    # Try to peek into the file to get metadata
                    try:
                        with open(file_path, "r") as f:
                            data = json.load(f)
                            score = data.get("compliance_score", 0)
                            count = len(data.get("commitments", []))
                            source = data.get("source_document")
                            
                            # Fallback if source is missing or marked as unknown, try to guess from filename
                            # Filename format: {source}_{timestamp}.json
                            if not source or source == "Unknown Source" or source == "Unknown Report":
                                parts = filename.split('_202') # Split at timestamp year start if possible
                                if len(parts) > 1:
                                    source = parts[0].replace('_', ' ').strip()
                                else:
                                    source = "Unknown Report"

                            provider = data.get("provider")
                            model = data.get("model")
                            mode = data.get("mode")

                    except:
                        score = 0
                        count = 0
                        source = "Corrupted Report"
                        provider = None
                        model = None
                        mode = None
                        
                    assessments.append({
                        "filename": filename,
                        "timestamp": stats.st_mtime,
                        "score": score,
                        "commitments_count": count,
                        "source_document": source,
                        "provider": provider,
                        "model": model,
                        "mode": mode
                    })
        
        # Sort assessments by timestamp (most recent first)
        assessments.sort(key=lambda x: x["timestamp"], reverse=True)
        return assessments
    except Exception as e:
        print(f"Error listing assessments: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/assessments/{filename}")
async def delete_assessment(filename: str):
    """Deletes a specific assessment report."""
    file_path = os.path.join(HISTORY_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Assessment not found")
    try:
        os.remove(file_path)
        return {"message": f"Assessment {filename} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def get_expected_evidence_map() -> dict:
    criteria_path = os.path.join(os.path.dirname(__file__), '..', 'criteria_new.json')
    evidence_map = {}
    try:
        with open(criteria_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for commitment in data.get("commitments", []):
                for criterion in commitment.get("criteria", []):
                    evidence_map[criterion["id"]] = criterion.get("expected_evidence", [])
    except Exception as e:
        print(f"Error loading criteria for expected evidence: {e}")
    return evidence_map

@app.get("/assessments/{filename}")
async def get_assessment(filename: str):
    """Retrieves a specific assessment report and dynamically adds expected evidence."""
    file_path = os.path.join(HISTORY_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Assessment not found")
        
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            
        # Stitch expected evidence into the response
        evidence_map = get_expected_evidence_map()
        for commitment in data.get("commitments", []):
            for result in commitment.get("results", []):
                if not result.get("expected_evidence"):
                    result["expected_evidence"] = evidence_map.get(result.get("criterion_id"), [])

        return data
    except Exception as e:
        print(f"Error loading assessment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

