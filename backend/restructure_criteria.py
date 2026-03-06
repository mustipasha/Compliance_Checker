#!/usr/bin/env python3
"""
Script to restructure criteria.json from flat to hierarchical (commitment-based) structure.
"""
import json

# Load current flat structure
with open('criteria.json', 'r') as f:
    data = json.load(f)

# Define commitment metadata based on criteria IDs
commitments_metadata = {
    "SS-1": {
        "title": "Safety & Security Framework",
        "description": "Establish, implement, and maintain a comprehensive Safety & Security Framework"
    },
    "SS-2": {
        "title": "Systemic Risk Identification",
        "description": "Identify and develop scenarios for systemic risks"
    },
    "SS-3": {
        "title": "Systemic Risk Analysis",
        "description": "Analyze systemic risks through model-independent information, evaluations, modelling, estimation, and monitoring"
    },
    "SS-4": {
        "title": "Risk Acceptance & Decisions",
        "description": "Define acceptance criteria and make proceeding decisions based on risk acceptability"
    },
    "SS-5": {
        "title": "Safety Mitigations",
        "description": "Implement safety mitigations robust under adversarial pressure"
    },
    "SS-6": {
        "title": "Security Protections",
        "description": "Define security goals and implement appropriate security mitigations"
    },
    "SS-7": {
        "title": "Model Reporting",
        "description": "Create and maintain comprehensive Model Reports with required documentation"
    },
    "SS-8": {
        "title": "Governance & Resources",
        "description": "Establish governance, allocate resources, and promote healthy risk culture"
    },
    "SS-9": {
        "title": "Serious Incident Management",
        "description": "Identify, document, report, and retain serious incident information"
    },
    "SS-10": {
        "title": "Documentation & Transparency",
        "description": "Maintain detailed documentation and provide appropriate public transparency"
    }
}

# Group criteria by commitment
commitments_dict = {}
for criterion in data['criteria']:
    # Extract commitment ID (e.g., "SS-1" from "SS-1.1")
    commitment_id = '-'.join(criterion['id'].split('-')[:-1]) + '-' + criterion['id'].split('-')[-1].split('.')[0]
    
    if commitment_id not in commitments_dict:
        commitments_dict[commitment_id] = {
            "id": commitment_id,
            "title": commitments_metadata[commitment_id]["title"],
            "description": commitments_metadata[commitment_id]["description"],
            "criteria": []
        }
    
    commitments_dict[commitment_id]["criteria"].append(criterion)

# Convert to list and sort
commitments_list = sorted(commitments_dict.values(), key=lambda x: x['id'])

# Create new structure
new_data = {
    "schema_version": "2.1",
    "domain": data["domain"],
    "source": data["source"],
    "commitments": commitments_list
}

# Write to new file
with open('criteria_hierarchical.json', 'w') as f:
    json.dump(new_data, f, indent=2)

print(f"✅ Restructured {len(data['criteria'])} criteria into {len(commitments_list)} commitments")
for comm in commitments_list:
    print(f"  {comm['id']}: {comm['title']} ({len(comm['criteria'])} criteria)")
