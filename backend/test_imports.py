from dotenv import load_dotenv
load_dotenv()

import sys
import os

print("Testing imports...")
try:
    from api.models import AssessmentReport
    print("✓ api.models")
    from core.ingestion import ingest_document
    print("✓ core.ingestion")
    from core.retrieval import retrieve_evidence
    print("✓ core.retrieval")
    from agents.reasoners import SemanticAgent, StrictAgent
    print("✓ agents.reasoners")
    from agents.judge import JudgeAgent
    print("✓ agents.judge")
    from core.pipeline import run_compliance_check
    print("✓ core.pipeline")
    from api.main import app
    print("✓ api.main")
    print("All imports successful!")
except Exception as e:
    print(f"Import failed: {e}")
    sys.exit(1)
