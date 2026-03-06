import sys
try:
    from pypdf import PdfReader
    reader = PdfReader("Criterion_List.pdf")
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    with open("criteria.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Extraction complete. Saved to criteria.txt")
except ImportError:
    print("pypdf not installed")
except Exception as e:
    print(f"Error: {e}")
