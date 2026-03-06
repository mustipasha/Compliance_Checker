import asyncio
import argparse
from dotenv import load_dotenv

# Load environment variables (API keys, DB paths, etc.)
load_dotenv()

from core.retrieval import retrieve_evidence

async def main():
    parser = argparse.ArgumentParser(description="Test Vector Store Retrieval")
    parser.add_argument("query", type=str, help="The search query to test")
    parser.add_argument("--k", type=int, default=5, help="Number of chunks to retrieve")
    
    args = parser.parse_args()

    print(f"\n🔍 Searching for: '{args.query}' (Top {args.k})\n")

    try:
        # Call the core retrieval function directly
        results = await retrieve_evidence(args.query, k=args.k)
        
        if not results:
            print("❌ No results found. (Is the database populated?)")
            return

        print(f"✅ Found {len(results)} results:\n")
        
        for i, doc in enumerate(results, 1):
            print(f"--- Result {i} (Score: {doc.relevance_score:.4f}) ---")
            print(f"Source: {doc.source} (Page {doc.page}, Chapter: {doc.chapter})")
            print(f"Chunk ID: {doc.chunk_id}")
            print(f"Text Preview: {doc.text[:300]}...\n")
            
    except Exception as e:
        print(f"🚨 Error during retrieval: {e}")

if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
