import json
import re
from pypdf import PdfReader

PDF_PATH = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Codes_of_Practice/Code_of_Practice_for_GeneralPurpose_AI_Models_Safety_and_Security_Chapter_hchDfNmrzSPiuU5PNh77HCxHu0c_118119 (1).pdf"
JSON_PATH = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Compliance Checker Tool/backend/criteria_new.json"

def extract_text_for_analysis():
    with open(JSON_PATH, "r") as f:
        data = json.load(f)
        
    reader = PdfReader(PDF_PATH)
    
    output_text = ""
    
    # Sort criteria by ID to help reading flow
    all_criteria = []
    for commit in data["commitments"]:
        all_criteria.extend(commit["criteria"])
    
    # Sort by ID
    all_criteria.sort(key=lambda x: [int(p) for p in re.findall(r'\d+', x['id'])])

    print(f"Extracting text for {len(all_criteria)} measures...")

    for crit in all_criteria:
        page_idx = crit.get("page", 1) - 1
        if page_idx < 0: page_idx = 0
        
        # Extract text from that page and the next one (to catch overflow)
        text = ""
        try:
            text += reader.pages[page_idx].extract_text()
            if page_idx + 1 < len(reader.pages):
                text += "\n--- NEXT PAGE ---\n"
                text += reader.pages[page_idx + 1].extract_text()
        except:
            pass
            
        # Naive extraction: Find start of this measure and end of this measure
        # This is just for MY analysis, doesn't need to be perfect code, just needs to show me context.
        match = re.search(rf"Measure\s+{crit['id'].replace('SS-', '')}", text, re.IGNORECASE)
        
        start_pos = match.start() if match else 0
        snippet = text[start_pos:start_pos+3000] # Get reasonable chunk
        
        output_text += f"\n\n================ {crit['id']} : {crit['title']} ================\n"
        output_text += snippet
        
    with open("measure_dump.txt", "w") as f:
        f.write(output_text)

if __name__ == "__main__":
    extract_text_for_analysis()
