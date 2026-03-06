import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from core.ingestion import ingest_document
from core.retrieval import retrieve_evidence

# Sample Document for testing
# (Adjust path if needed to find a real PDF)
TEST_FILE = "/Users/Musta/Documents/Universiy of Vienna/5. Semester/MA/Codes_of_Practice/Code_of_Practice_for_GeneralPurpose_AI_Models_Safety_and_Security_Chapter_hchDfNmrzSPiuU5PNh77HCxHu0c_118119 (1).pdf"


# Queries representing typical compliance questions
TEST_QUERIES = [
    "What are the systemic risks identified for the model?",
    "Describe the safety and security framework implementation.",
    "how is post-market monitoring conducted?",
    "what are the trigger points for systemic risk assessment?"
]

async def run_comparison():
    if not os.path.exists(TEST_FILE):
        print(f"Test file {TEST_FILE} not found. Please ensure it's in the project root.")
        return

    print(f"--- Starting Comparative Ingestion for: {TEST_FILE} ---")
    
    # 1. Ingest both ways
    print("Ingesting Flat...")
    flat_count = ingest_document(TEST_FILE, strategy="flat")
    print(f"Flat Ingestion Complete: {flat_count} chunks.")
    
    print("Ingesting Hierarchical...")
    hier_count = ingest_document(TEST_FILE, strategy="hierarchical")
    print(f"Hierarchical Ingestion Complete: {hier_count} chunks.")

    print("\n" + "="*50)
    print("RETRIEVAL COMPARISON")
    print("="*50)

    for query in TEST_QUERIES:
        print(f"\nQUERY: {query}")
        
        # Retrieval - Flat
        flat_results = await retrieve_evidence(query, k=3, strategy="flat")
        print("\n[FLAT STRATEGY RESULTS]")
        for i, res in enumerate(flat_results):
            print(f"{i+1}. [Page {res.page}] {res.text[:150].replace(chr(10), ' ')}...")
            
        # Retrieval - Hierarchical
        hier_results = await retrieve_evidence(query, k=3, strategy="hierarchical")
        print("\n[HIERARCHICAL STRATEGY RESULTS]")
        for i, res in enumerate(hier_results):
            chapter = getattr(res, 'chapter', 'N/A') # Might need to check if Evidence model has chapter
            print(f"{i+1}. [Page {res.page} | Chapter: {res.metadata.get('chapter', 'Unknown')}] {res.text[:150].replace(chr(10), ' ')}...")

if __name__ == "__main__":
    asyncio.run(run_comparison())
