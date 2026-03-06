import fitz
import os

file_path = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Codes_of_Practice/Code_of_Practice_for_GeneralPurpose_AI_Models_Safety_and_Security_Chapter_hchDfNmrzSPiuU5PNh77HCxHu0c_118119 (1).pdf"

if not os.path.exists(file_path):
    print("File not found")
else:
    doc = fitz.open(file_path)
    print(f"Total Pages: {doc.page_count}")
    for i in range(min(5, doc.page_count)):
        page = doc[i]
        text = page.get_text().strip()
        print(f"--- Page Index {i} (Physical Page {i+1}) ---")
        print(f"First 100 chars: {text[:100]}...")
    doc.close()
