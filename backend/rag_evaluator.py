import os
import json
import asyncio
import csv
from dotenv import load_dotenv
load_dotenv()

from core.ingestion import get_vector_store
from core.retrieval import retrieve_evidence
from core.llm_config import get_llm
from pydantic import BaseModel, Field

class RelevanceEvaluation(BaseModel):
    is_relevant: bool = Field(description="True if the chunk contains information that directly helps answer the assessment question, False otherwise.")
    reasoning: str = Field(description="Brief explanation of why the chunk is or is not relevant to the question.")

def list_chunks(strategy: str = "hierarchical", output_file: str = "chunks_export_across_pages.json"):
    """
    Exports all chunks from the specified vector store to a JSON file.
    This allows you to see all chunk IDs, their metadata, and corresponding text slices.
    """
    print(f"Loading vector store for strategy: {strategy}")
    vector_store = get_vector_store(strategy=strategy)
    
    # In ChromaDB, we can get all documents easily
    collection = vector_store._collection
    results = collection.get(include=['metadatas', 'documents'])
    
    if not results or not results['ids']:
        print(f"No chunks found for strategy '{strategy}'. Have you ingested a document yet?")
        return

    ids = results['ids']
    documents = results['documents']
    metadatas = results['metadatas']
    
    data = []
    for i in range(len(ids)):
        chunk_id = metadatas[i].get('chunk_id', ids[i]) if metadatas[i] else ids[i]
        page = metadatas[i].get('page', 'N/A') if metadatas[i] else 'N/A'
        chapter = metadatas[i].get('chapter', 'N/A') if metadatas[i] else 'N/A'
        source = metadatas[i].get('source', 'N/A') if metadatas[i] else 'N/A'
        
        data.append({
            "chunk_id": chunk_id,
            "source": source,
            "page": page,
            "chapter": chapter,
            "text": documents[i]
        })

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully exported {len(data)} chunks to {output_file}")
    print(f"You can now review this file to find the ground-truth chunk IDs for your evaluation.")

async def evaluate_retrieval(gt_file: str = "ground_truth.json", k: int = 5, strategy: str = "hierarchical"):
    """
    Evaluates the retrieval using a ground truth JSON file.
    Computes Precision, Recall, and F1 Score for each query and overall averages.
    """
    if not os.path.exists(gt_file):
        print(f"Ground truth file '{gt_file}' not found.")
        print("Please create one. Example format:")
        print(json.dumps([
            {"query": "Sample question?", "expected_chunk_ids": ["id1", "id2"]}
        ], indent=2))
        return

    with open(gt_file, 'r') as f:
        ground_truth = json.load(f)

    print(f"--- Starting Evaluation using {strategy} strategy (k={k}) ---")
    
    total_precision = 0.0
    total_recall = 0.0
    valid_queries = 0

    results_log = []

    for item in ground_truth:
        query = item.get("query")
        expected_ids = set(item.get("expected_chunk_ids", []))
        
        if not query or not expected_ids:
            continue

        valid_queries += 1
        print(f"\nEvaluating Query: '{query}'")
        
        # Retrieve evidence
        retrieved_docs = await retrieve_evidence(query, k=k, strategy=strategy)
        retrieved_ids = set([doc.chunk_id for doc in retrieved_docs])
        
        # True Positives: Retrieved chunks that are in the expected set
        true_positives = retrieved_ids.intersection(expected_ids)
        
        # Precision: TP / Total Retrieved
        precision = len(true_positives) / len(retrieved_ids) if retrieved_ids else 0.0
        
        # Recall: TP / Total Expected
        recall = len(true_positives) / len(expected_ids) if expected_ids else 0.0
        
        total_precision += precision
        total_recall += recall
        
        print(f"  Retrieved IDs: {list(retrieved_ids)}")
        print(f"  Expected IDs:  {list(expected_ids)}")
        print(f"  True Positives:{list(true_positives)}")
        print(f"  Precision: {precision:.2f} | Recall: {recall:.2f}")

        results_log.append({
            "query": query,
            "precision": precision,
            "recall": recall,
            "retrieved_count": len(retrieved_ids),
            "expected_count": len(expected_ids),
            "tp_count": len(true_positives)
        })

    if valid_queries == 0:
        print("No valid queries found in ground truth file.")
        return

    avg_precision = total_precision / valid_queries
    avg_recall = total_recall / valid_queries
    # F1 Score = 2 * (P * R) / (P + R)
    f1_score = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if (avg_precision + avg_recall) > 0 else 0.0

    print("\n" + "="*50)
    print("OVERALL EVALUATION RESULTS")
    print("="*50)
    print(f"Total Queries Evaluated: {valid_queries}")
    print(f"Average Precision: {avg_precision:.4f}")
    print(f"Average Recall:    {avg_recall:.4f}")
    print(f"Overall F1-Score:  {f1_score:.4f}")

async def evaluate_with_llm(k: int = 5, strategy: str = "hierarchical"):
    """
    Evaluates retrieval quality without a ground truth by using an LLM to judge relevance.
    It reads `criteria_new.json` to extract assessment questions.
    """
    criteria_path = "criteria_new.json"
    if not os.path.exists(criteria_path):
        print(f"Error: {criteria_path} not found.")
        return
        
    with open(criteria_path, "r") as f:
        criteria_data = json.load(f)
        
    queries = []
    # parse criteria_new.json to find assessment_questions
    for expected_commitment in criteria_data.get("commitments", []):
        for criterion in expected_commitment.get("criteria", []):
            q = criterion.get("assessment_question")
            if q:
                queries.append(q)

    if not queries:
        print("No assessment_questions found in criteria_new.json")
        return

    print(f"--- Starting LLM-as-a-Judge Evaluation ({len(queries)} questions) ---")
    print(f"Strategy: {strategy} | Top K: {k}")
    
    # Initialize LLM with structured output
    llm = get_llm(temperature=0).with_structured_output(RelevanceEvaluation)
    
    total_relevant = 0
    total_retrieved = 0
    
    for i, query in enumerate(queries):
        print(f"\n[{i+1}/{len(queries)}] Query: {query}")
        
        retrieved_docs = await retrieve_evidence(query, k=k, strategy=strategy)
        
        if not retrieved_docs:
            print("  -> No chunks retrieved.")
            continue
            
        relevant_for_query = 0
        
        for doc in retrieved_docs:
            total_retrieved += 1
            # Ask LLM if relevant
            prompt = f"Assessment Question: {query}\n\nRetrieved Evidence Chunk:\n{doc.text}\n\nDoes this chunk provide relevant and useful information to answer the assessment question?"
            
            try:
                eval_result = await llm.ainvoke(prompt)
                if eval_result.is_relevant:
                    relevant_for_query += 1
                    total_relevant += 1
                    print(f"  [REQ] ✅ Chunk {doc.chunk_id[:6]}... (Page {doc.page}) - {eval_result.reasoning[:100]}...")
                else:
                    print(f"  [REQ] ❌ Chunk {doc.chunk_id[:6]}... (Page {doc.page}) - {eval_result.reasoning[:100]}...")
            except Exception as e:
                print(f"  [REQ] ⚠️ Error evaluating chunk: {e}")
                
        # Precision for this query
        q_precision = relevant_for_query / len(retrieved_docs) if retrieved_docs else 0.0
        print(f"  -> Query Precision: {q_precision:.2f} ({relevant_for_query}/{len(retrieved_docs)} chunks relevant)")

    if total_retrieved == 0:
        print("No chunks retrieved across all queries.")
        return
        
    overall_precision = total_relevant / total_retrieved
    print("\n" + "="*50)
    print("LLM EVALUATION RESULTS (CONTEXT PRECISION)")
    print("="*50)
    print(f"Queries Evaluated:   {len(queries)}")
    print(f"Total Chunks Judged: {total_retrieved}")
    print(f"Relevant Chunks:     {total_relevant}")
    print(f"Overall Precision Score (Relevance Ratio): {overall_precision:.4f}")
    print("Note: Recall cannot be accurately computed without a manually labelled ground truth.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Tool to visualize chunks and evaluate retrieval precision/recall.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # List chunks command
    parser_list = subparsers.add_parser("list", help="Export vector store chunks to a JSON file")
    parser_list.add_argument("--strategy", type=str, default="hierarchical", help="Retrieval strategy to inspect (flat or hierarchical)")
    parser_list.add_argument("--output", type=str, default="chunks_export.json", help="Output JSON file path")

    # Evaluate command
    parser_eval = subparsers.add_parser("eval", help="Evaluate retrieval precision and recall with a Ground Truth file")
    parser_eval.add_argument("--gt", type=str, default="ground_truth.json", help="Path to ground truth JSON file")
    parser_eval.add_argument("--k", type=int, default=5, help="Number of chunks to retrieve (Top K)")
    parser_eval.add_argument("--strategy", type=str, default="hierarchical", help="Retrieval strategy to evaluate")

    # Auto-eval command
    parser_auto_eval = subparsers.add_parser("auto-eval", help="Evaluate context precision using LLM-as-a-judge (No Ground Truth needed)")
    parser_auto_eval.add_argument("--k", type=int, default=5, help="Number of chunks to retrieve (Top K)")
    parser_auto_eval.add_argument("--strategy", type=str, default="hierarchical", help="Retrieval strategy to evaluate")

    args = parser.parse_args()

    if args.command == "list":
        list_chunks(strategy=args.strategy, output_file=args.output)
    elif args.command == "eval":
        asyncio.run(evaluate_retrieval(gt_file=args.gt, k=args.k, strategy=args.strategy))
    elif args.command == "auto-eval":
        asyncio.run(evaluate_with_llm(k=args.k, strategy=args.strategy))
