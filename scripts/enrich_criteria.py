import json
import re

JSON_PATH = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Compliance Checker Tool/backend/criteria_new.json"

# Common artifacts in compliance
ARTIFACT_TYPES = [
    "Policy", "Procedure", "Framework", "Report", "Log", "Register", 
    "Assessment", "audit", "documentation", "record", "plan", "inventory",
    "notification", "Evaluation", "Testing results"
]

def enrich_criteria():
    with open(JSON_PATH, "r") as f:
        data = json.load(f)

    updated_count = 0
    
    for commit in data.get("commitments", []):
        for criterion in commit.get("criteria", []):
            # 1. Extract Keywords from "Indicative concepts"
            keywords = []
            if "expected_evidence" in criterion:
                last_evidence = criterion["expected_evidence"][-1]
                if last_evidence.startswith("Indicative concepts and phrases:"):
                    # Remove prefix and split by comma
                    raw_keywords = last_evidence.replace("Indicative concepts and phrases:", "").strip()
                    keywords = [k.strip() for k in raw_keywords.split(',') if k.strip()]
            
            criterion["extracted_keywords"] = keywords[:6] # Limit to top 6
            
            # 2. Extract Artifacts (Naive approach: look for keywords in title/evidence)
            artifacts = set()
            text_corpus = criterion["title"] + " " + criterion["requirement"] + " " + " ".join(criterion["expected_evidence"])
            
            # Specific mappings based on common sense compliance
            text_lower = text_corpus.lower()
            if "risk assessment" in text_lower: artifacts.add("Risk Assessment")
            if "framework" in text_lower: artifacts.add("Framework Document")
            if "log" in text_lower or "register" in text_lower: artifacts.add("Register/Log")
            if "report" in text_lower: artifacts.add("Report")
            if "notification" in text_lower: artifacts.add("Notification Record")
            if "audit" in text_lower: artifacts.add("Audit Report")
            if "policy" in text_lower: artifacts.add("Policy Document")
            if "training" in text_lower: artifacts.add("Training Records")
            if "testing" in text_lower or "test" in text_lower: artifacts.add("Test Results")
            if "technical file" in text_lower or "documentation" in text_lower: artifacts.add("Technical Documentation")

            criterion["extracted_artifacts"] = list(artifacts)[:4] # Limit to top 4
            
            updated_count += 1

    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Enriched {updated_count} criteria.")

if __name__ == "__main__":
    enrich_criteria()
