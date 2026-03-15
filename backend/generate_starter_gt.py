import json
import asyncio
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def generate_ground_truth(criteria_path="criteria_new.json", chunks_path="chunks_export.json", output_path="ground_truth.json", top_n=3):
    """
    Reads assessment questions and chunks, computes basic string similarity (TF-IDF),
    and creates a starter ground truth file.
    """
    if not os.path.exists(criteria_path) or not os.path.exists(chunks_path):
        print("Missing required files.")
        return

    # 1. Load criteria
    with open(criteria_path, "r") as f:
        criteria_data = json.load(f)

    queries = []
    for expected_commitment in criteria_data.get("commitments", []):
        for criterion in expected_commitment.get("criteria", []):
            q = criterion.get("assessment_question")
            if q:
                queries.append(q)

    # 2. Load chunks
    with open(chunks_path, "r") as f:
        chunks_data = json.load(f)

    chunk_texts = [c.get("text", "") for c in chunks_data]
    chunk_ids = [c.get("chunk_id", "") for c in chunks_data]

    # 3. Compute Similarity Setup
    vectorizer = TfidfVectorizer(stop_words='english')
    # Fit on both queries and chunks to build vocabulary
    all_text = queries + chunk_texts
    tfidf_matrix = vectorizer.fit_transform(all_text)
    
    query_vectors = tfidf_matrix[:len(queries)]
    chunk_vectors = tfidf_matrix[len(queries):]

    # Calculate similarities
    similarities = cosine_similarity(query_vectors, chunk_vectors)

    # 4. Generate Ground Truth
    ground_truth = []
    
    for i, query in enumerate(queries):
        # Get indices of top N chunks for this query
        top_indices = np.argsort(similarities[i])[-top_n:][::-1]
        
        expected_ids = []
        for idx in top_indices:
            # Only add if there is SOME similarity
            if similarities[i][idx] > 0.05:
                expected_ids.append(chunk_ids[idx])
                
        # Fallback to at least taking the absolute highest if all are below threshold
        if not expected_ids and len(top_indices) > 0:
             expected_ids.append(chunk_ids[top_indices[0]])

        ground_truth.append({
            "query": query,
            "expected_chunk_ids": expected_ids
        })

    # 5. Save output
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2, ensure_ascii=False)
        
    print(f"✅ Generated starter ground truth with {len(ground_truth)} queries to {output_path}!")
    print(f"Review the file to make sure the matched chunks make sense before running your evaluation.")

if __name__ == "__main__":
    generate_ground_truth()
