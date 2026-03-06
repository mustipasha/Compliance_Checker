import json

JSON_PATH = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Compliance Checker Tool/backend/criteria_new.json"

ARTIFACT_MAPPING = {
    "SS-1.1": ["Safety & Security Framework", "Risk Acceptance Criteria", "Responsibility Allocation Map"],
    "SS-1.2": ["Lighter-touch Eval Results", "Post-market Monitoring Data", "Serious Incident Reports"],
    "SS-1.3": ["Framework Changelog", "Framework Assessment Report", "Remediation Plans"],
    "SS-1.4": ["Unredacted Framework", "Framework Updates"],
    
    "SS-2.1": ["List of Systemic Risks", "Risk Characteristics Analysis", "Risk Source Analysis"],
    "SS-2.2": ["Systemic Risk Scenarios"],
    
    "SS-3.1": ["Model-independent Info", "Literature Reviews", "Training Data Reviews", "Incident Data Analysis"],
    "SS-3.2": ["Model Evaluation Results", "Red-teaming Reports", "Benchmark Scores"],
    "SS-3.3": ["Systemic Risk Modelling Results"],
    "SS-3.4": ["Systemic Risk Estimates", "Risk Matrix", "Probability Distributions"],
    "SS-3.5": ["Post-market Monitoring Results", "End-user Feedback Logs", "Incident Reporting Forms"],
    
    "SS-4.1": ["Risk Acceptance Criteria", "Systemic Risk Tiers", "Forecast Timelines", "External Input Process"],
    "SS-4.2": ["Proceeding Decision Record", "Re-assessment Results"],
    
    "SS-5.1": ["Safety Mitigation Docs", "Data Filtering Logs", "Access Control Records", "Model Behavior Tests"],
    
    "SS-6.1": ["Security Goal Definition", "Threat Actor Analysis"],
    "SS-6.2": ["Security Mitigation Docs", "Cybersecurity Audit Reports", "Access Logs"],
    
    "SS-7.1": ["Model Description", "Model Specification", "System Prompt", "Training Data Documentation"],
    "SS-7.2": ["Justification for Proceeding", "Safety Margin Analysis", "Decision Record"],
    "SS-7.3": ["Risk ID & Analysis Results", "Model Evaluation Results", "Elicitation Records", "Input/Output Samples"],
    "SS-7.4": ["External Evaluation Reports", "Security Review Reports", "Evaluator Selection Justification"],
    "SS-7.5": ["Scaling Laws Analysis", "Novel Architecture Summary", "Mitigation Effectiveness Review"],
    "SS-7.6": ["Updated Model Report", "Model Report Changelog"],
    "SS-7.7": ["Model Report Access Link"],
    
    "SS-8.1": ["Responsibility Allocation Map", "Governance Structure Doc"],
    "SS-8.2": ["Resource Allocation Plan", "Budget/Personnel Records"],
    "SS-8.3": ["Risk Culture Promotion Plan", "Anonymous Survey Results", "Whistleblower Policy"],
    
    "SS-9.1": ["Incident Tracking Log", "External Report Reviews"],
    "SS-9.2": ["Serious Incident Report", "Root Cause Analysis", "Harm Assessment", "Chain of Events Analysis"],
    "SS-9.3": ["Initial Incident Report", "Intermediate Incident Report", "Final Incident Report"],
    "SS-9.4": ["Document Retention Policy", "Archived Incident Records"],
    
    "SS-10.1": ["Detailed Architecture Doc", "Integration Description", "Detailed Evaluation Results", "Mitigation Details"],
    "SS-10.2": ["Public Framework Summary", "Public Model Report Summary"]
}

def update_artifacts():
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    
    count = 0
    for commit in data["commitments"]:
        for criterion in commit["criteria"]:
            measure_id = criterion["id"]
            if measure_id in ARTIFACT_MAPPING:
                criterion["extracted_artifacts"] = ARTIFACT_MAPPING[measure_id]
                count += 1
            else:
                # Fallback if I missed one (though I covered all 32 SS measures)
                pass
                
    with open(JSON_PATH, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Updated artifacts for {count} measures.")

if __name__ == "__main__":
    update_artifacts()
