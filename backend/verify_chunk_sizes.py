
import os
import sys
import json
import asyncio
from typing import List

# Setup environment
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.getcwd())
from core.ingestion import ingest_document, get_vector_store
from langchain_core.documents import Document

async def verify_chunk_sizes():
    file_path = "uploaded_files/Code_of_Practice_for_GeneralPurpose_AI_Models_Safety_and_Security_Chapter.pdf"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    print(f"--- Ingesting with HIERARCHICAL strategy ---")
    # Ingesting (this will use the existing collection or flush it as per ingestion.py logic)
    ingest_document(file_path, strategy="hierarchical")
    
    vs = get_vector_store(strategy="hierarchical")
    results = vs.get(include=["documents", "metadatas"])
    
    chunks = results["documents"]
    metadatas = results["metadatas"]
    
    if not chunks:
        print("No chunks found.")
        return

    lengths = [len(c) for c in chunks]
    avg_len = sum(lengths) / len(lengths)
    max_len = max(lengths)
    min_len = min(lengths)

    print("\n" + "="*50)
    print("CHUNK SIZE ANALYSIS (HIERARCHICAL)")
    print("="*50)
    print(f"Total Chunks:    {len(chunks)}")
    print(f"Average Length:  {avg_len:.2f}")
    print(f"Max Length:      {max_len}")
    print(f"Min Length:      {min_len}")
    print(f"Target Size:     1500")
    print("="*50)

    # Check for chunks that likely span across pages
    print("\nChunks spanning across pages (based on metadata):")
    span_count = 0
    for i, meta in enumerate(metadatas):
        page = str(meta.get("page", ""))
        if "-" in page:
            span_count += 1
            if span_count <= 5:
                print(f"  - Chunk {i} | Page Range: {page} | Length: {len(chunks[i])} chars")
                # Print a bit of the text to see continuity
                start_snippet = chunks[i][:50].replace('\n', ' ')
                end_snippet = chunks[i][-50:].replace('\n', ' ')
                print(f"    Snippet: {start_snippet}...[FLOW]...{end_snippet}")

    print(f"\nTotal multi-page chunks found: {span_count}")
    
    print("\nConclusion:")
    if avg_len > 1000:
        print("✅ Chunks are robust in size and generally close to the 1500 target.")
    else:
        print("⚠️ Chunks seem smaller than expected on average.")

if __name__ == "__main__":
    asyncio.run(verify_chunk_sizes())
