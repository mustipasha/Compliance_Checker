from typing import List
from core.ingestion import get_vector_store
from api.models import Evidence

MIN_RELEVANCE_SCORE = 0.5 # Threshold (cosine similarity is usually 0-1 or -1 to 1 depending on metric)
# Chroma default is L2 distance usually, or cosine. LangChain `similarity_search_with_relevance_scores` converts to 0-1 range.

async def retrieve_evidence(query: str, k: int = 5, strategy: str = "hierarchical") -> List[Evidence]:
    """
    Retrieves top-k relevant chunks for a given query using vector similarity.
    Includes a basic quality filter and deduplication.
    """
    vector_store = get_vector_store(strategy=strategy)
    
    # 1. Broad Search (Fetch more candidates)
    # Lowered threshold to avoid missing relevant but jargon-heavy text
    # Increased fetch count for better post-filtering
    results = await vector_store.asimilarity_search_with_relevance_scores(query, k=k*4)
    
    # 2. Filter by Score (Lenient)
    # Threshold 0.3 allows for "related" concepts which agent can then verify
    MIN_RELEVANCE_SCORE = 0.3
    filtered_results = [r for r in results if r[1] >= MIN_RELEVANCE_SCORE]
    
    # Fallback: if nothing meets 0.3, take top 3 anyway (Agent decides relevance)
    if not filtered_results and results:
        filtered_results = results[:3]

    # 3. Deduplicate (by Chunk ID or Content)
    seen_ids = set()
    evidence_list = []
    
    for doc, score in filtered_results:
        # Use stable chunk_id if available, else content hash
        chunk_id = doc.metadata.get("chunk_id")
        if not chunk_id:
            # Fallback for old docs
            chunk_id = str(hash(doc.page_content))
            
        if chunk_id in seen_ids:
            continue
        seen_ids.add(chunk_id)
        
        evidence_list.append(Evidence(
            text=doc.page_content,
            source=doc.metadata.get('source', 'unknown'),
            page=doc.metadata.get('page', 0),
            chapter=doc.metadata.get('chapter'),
            metadata=doc.metadata,
            chunk_id=chunk_id,
            relevance_score=score
        ))
        
        if len(evidence_list) >= k:
            break
        
    return evidence_list
