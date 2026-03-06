import json
import re
from pypdf import PdfReader

PDF_PATH = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Codes_of_Practice/Code_of_Practice_for_GeneralPurpose_AI_Models_Safety_and_Security_Chapter_hchDfNmrzSPiuU5PNh77HCxHu0c_118119 (1).pdf"
JSON_PATH = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Compliance Checker Tool/backend/criteria_new.json"
OUTPUT_PATH = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Compliance Checker Tool/backend/criteria_new.json"

def extract_pages():
    reader = PdfReader(PDF_PATH)
    measure_pages = {}
    
    print(f"Scanning {len(reader.pages)} pages...")
    
    # Load JSON to get Titles (optional, but good for verification if needed)
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
    
    # Create a look-up for existing IDs
    existing_ids = set()
    if "commitments" in data:
        for commit in data["commitments"]:
            for criterion in commit.get("criteria", []):
                existing_ids.add(criterion["id"])

    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Strict Check: Line must START with "Measure X.Y" 
            # This allows "Measure 1.1" or "Measure 1.1:" or "Measure 1.1 -"
            match = re.search(r"^Measure\s+(\d+\.\d+)", line, re.IGNORECASE)
            
            if match:
                measure_num = match.group(1)
                measure_id = f"SS-{measure_num}"
                
                # Check if this ID actually exists in our JSON (filters out phantom measures)
                if measure_id in existing_ids:
                    # Filter TOC: usually ends with a number or has dots
                    # BUT be careful, "Measure 1.1 ... 14" is TOC.
                    # "Measure 1.1 Risk ID" is definition.
                    if re.search(r"\.+\s*\d+$", line) or re.search(r"\s+\d+$", line):
                         # Likely TOC
                         continue
                         
                    if measure_id not in measure_pages:
                        measure_pages[measure_id] = i + 1
                        print(f"Found {measure_id} on page {i+1}")
    
    updated_count = 0
    if "commitments" in data:
        for commit in data["commitments"]:
            for criterion in commit.get("criteria", []):
                m_id = criterion["id"]
                if m_id in measure_pages:
                    criterion["page"] = measure_pages[m_id]
                    updated_count += 1
    
    with open(OUTPUT_PATH, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Updated {updated_count} criteria with page numbers.")

if __name__ == "__main__":
    extract_pages()
