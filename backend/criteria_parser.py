import json
from typing import List, Dict, Tuple

def parse_criteria(file_path: str) -> List[Dict]:
    """
    Parses the criteria.json schema.
    Supports both flat criteria list (v2.0) and hierarchical commitments (v2.1).
    Returns a list of criteria objects, enriched with commitment context if available.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        processed_criteria = []
        
        # Check for hierarchical structure (v2.1)
        if "commitments" in data:
            for commitment in data["commitments"]:
                comm_id = commitment.get("id")
                comm_title = commitment.get("title")
                for item in commitment.get("criteria", []):
                    # Enrich with commitment info
                    item["commitment_id"] = comm_id
                    item["commitment_title"] = comm_title
                    _process_criterion(item)
                    processed_criteria.append(item)
        
        # Fallback to flat structure (v2.0)
        elif "criteria" in data:
            for item in data["criteria"]:
                _process_criterion(item)
                processed_criteria.append(item)
                
        return processed_criteria
        
    except Exception as e:
        print(f"Error parsing criteria JSON: {e}")
        return []

def _process_criterion(item: Dict):
    """Internal helper to process keywords and evidence."""
    evidence_list = item.get("expected_evidence", [])
    keywords = []
    cleaned_evidence = []
    
    for evid in evidence_list:
        # Extract Keywords
        if "Indicative keywords" in evid or "Indicative concepts" in evid:
            try:
                prefix, content = evid.split(":", 1)
                keywords = [k.strip() for k in content.split(",") if k.strip()]
            except:
                pass
        else:
            cleaned_evidence.append(evid)

    # Heuristic Artifact Extraction
    # Look for capitalized terms ending in "Report", "Log", "Assessment", "Plan", "Policy", "Framework"
    artifacts = set()
    combined_text = item.get("requirement", "") + " " + " ".join(cleaned_evidence)
    
    # Common artifacts in this domain
    target_artifacts = [
        "Risk Assessment", "Model Report", "Safety and Security Framework", 
        "Incident Log", "Test Plan", "Evaluation Results", "Technical Documentation",
        "Change Log", "Versioning System", "External Audit"
    ]
    
    for art in target_artifacts:
        if art.lower() in combined_text.lower():
            artifacts.add(art)

    item["extracted_keywords"] = keywords
    item["extracted_artifacts"] = list(artifacts)
    item["cleaned_evidence"] = cleaned_evidence
