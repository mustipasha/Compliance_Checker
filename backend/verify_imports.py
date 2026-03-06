import sys
import os
from dotenv import load_dotenv

# Load env vars first
load_dotenv()

try:
    print("Importing models...")
    from api.models import AuditorOutput, ChallengerOutput, JudgeOutput
    print("Models OK.")
    
    print("Importing retrieval...")
    from core.retrieval import retrieve_evidence
    print("Retrieval OK.")
    
    print("Importing agents...")
    from agents.reasoners import AuditorAgent, ChallengerAgent
    print("Agents OK.")
    
    print("Importing pipeline...")
    from core.pipeline import run_compliance_check
    print("Pipeline OK.")
    
    print("Importing main...")
    from api.main import app
    print("Main App OK.")
    
    print("Testing Criteria Parser...")
    from criteria_parser import parse_criteria
    # Check criteria.json explicitly
    criteria = parse_criteria("criteria.json")
    
    if criteria:
        print(f"Parsed {len(criteria)} criteria (Flat list).")
        first_item = criteria[0]
        print(f" First item ID: {first_item.get('id')}")
        
        # Check keyword extraction
        keywords = first_item.get("extracted_keywords", [])
        print(f" Extracted Keywords: {keywords}")
        
    else:
        print("Criteria parsing returned empty list/None.")
    
    print("ALL MODULES VERIFIED.")
except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
