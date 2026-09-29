import json
import os
import argparse
import glob
import numpy as np
from typing import Dict, List, Set, Any
from collections import defaultdict

def calculate_precision_recall_f1(actual: Set[str], expected: Set[str]):
    if not actual:
        return 0.0, 0.0, 0.0
    
    tp = len(actual.intersection(expected))
    precision = tp / len(actual) if actual else 0.0
    recall = tp / len(expected) if expected else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    
    return precision, recall, f1

def map_to_binary(status: str) -> str:
    """Maps 4 labels to Binary (COMPLIANT-> POSITIVE, rest -> NEGATIVE)"""
    positive = {"COMPLIANT"}
    return "POSITIVE" if status in positive else "NEGATIVE"

def calculate_classification_metrics(y_true: List[str], y_pred: List[str], classes: List[str]):
    # Accuracy
    correct = sum(1 for t, p in zip(y_true, y_pred) if t == p)
    accuracy = correct / len(y_true) if y_true else 0.0
    
    total_samples = len(y_true)
    per_class = {}
    precisions = []
    recalls = []
    f1s = []
    supports = []
    
    for cls in classes:
        tp = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p == cls)
        fp = sum(1 for t, p in zip(y_true, y_pred) if t != cls and p == cls)
        fn = sum(1 for t, p in zip(y_true, y_pred) if t == cls and p != cls)
        support = sum(1 for t in y_true if t == cls)
        
        p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * (p * r) / (p + r) if (p + r) > 0 else 0.0
        
        per_class[cls] = {"p": p, "r": r, "f1": f1, "support": support}
        precisions.append(p)
        recalls.append(r)
        f1s.append(f1)
        supports.append(support)
    
    # Macro averages (unweighted)
    macro_precision = np.mean(precisions) if precisions else 0.0
    macro_recall = np.mean(recalls) if recalls else 0.0
    macro_f1 = np.mean(f1s) if f1s else 0.0
    
    # Weighted averages (weighted by actual sample count in GT)
    if total_samples > 0:
        weighted_precision = sum(p * s for p, s in zip(precisions, supports)) / total_samples
        weighted_recall = sum(r * s for r, s in zip(recalls, supports)) / total_samples
        weighted_f1 = sum(f * s for f, s in zip(f1s, supports)) / total_samples
    else:
        weighted_precision = weighted_recall = weighted_f1 = 0.0

    return {
        "accuracy": accuracy,
        "macro_precision": macro_precision,
        "macro_recall": macro_recall,
        "macro_f1": macro_f1,
        "weighted_precision": weighted_precision,
        "weighted_recall": weighted_recall,
        "weighted_f1": weighted_f1,
        "per_class": per_class
    }

def calculate_confusion_matrix(y_true: List[str], y_pred: List[str], classes: List[str]):
    matrix = {t: {p: 0 for p in classes} for t in classes}
    for t, p in zip(y_true, y_pred):
        if t in matrix and p in matrix[t]:
            matrix[t][p] += 1
    return matrix

def format_confusion_matrix(matrix, classes):
    header = "Actual\\Pred | " + " | ".join([f"{c:<10}" for c in classes])
    lines = [header, "-" * len(header)]
    for true_cls in classes:
        row = f"{true_cls:<11} | " + " | ".join([f"{matrix[true_cls][pred_cls]:<10}" for pred_cls in classes])
        lines.append(row)
    return "\n".join(lines)

def process_single_run(run_path: str, label_gt: Dict[str, str], ret_gt: Dict[str, Set[str]], binary: bool):
    with open(run_path, 'r') as f:
        run_data = json.load(f)
    
    results = []
    for commitment in run_data.get('commitments', []):
        results.extend(commitment.get('results', []))
    
    y_true = []
    y_pred = []
    retrieval_stats = []
    criterion_predictions = {} # cid -> prediction
    
    classes = ["COMPLIANT", "PARTIALLY_COMPLIANT", "NOT_COMPLIANT", "NOT_EVIDENCED / UNKNOWN"]
    if binary:
        classes = ["POSITIVE", "NEGATIVE"]

    for res in results:
        cid = res['criterion_id']
        pred_status = res['status']
        query = res['assessment_question']
        
        if binary:
            pred_status = map_to_binary(pred_status)
        
        criterion_predictions[cid] = pred_status
        
        if cid in label_gt:
            true_status = label_gt[cid]
            if binary:
                true_status = map_to_binary(true_status)
            y_true.append(true_status)
            y_pred.append(pred_status)
        
        # Retrieval
        actual_ids = set()
        findings = res.get('alignment_findings', {})
        for cit in findings.get('evidence_citations', []):
            if 'chunk_id' in cit:
                ids = [i.strip() for i in str(cit['chunk_id']).split(',')]
                actual_ids.update(ids)
        
        if query in ret_gt:
            expected_ids = ret_gt[query]
            p, r, f1 = calculate_precision_recall_f1(actual_ids, expected_ids)
            retrieval_stats.append({"cid": cid, "p": p, "r": r, "f1": f1})

    return {
        "classification": calculate_classification_metrics(y_true, y_pred, classes),
        "confusion_matrix": calculate_confusion_matrix(y_true, y_pred, classes),
        "retrieval": retrieval_stats,
        "predictions": criterion_predictions,
        "classes": classes
    }

def main():
    parser = argparse.ArgumentParser(description="Calculate assessment and retrieval metrics.")
    parser.add_argument("--run", type=str, nargs='+', required=True, help="Path to assessment run JSON file(s), directory, or glob pattern")
    parser.add_argument("--label_gt", type=str, default="assessment_ground_truth.json", help="Path to status labels ground truth")
    parser.add_argument("--retrieval_gt", type=str, default="../Compliance Checker Tool/backend/ground_truth.json", help="Path to retrieval ground truth")
    parser.add_argument("--output", type=str, default="evaluation_report.txt", help="Path to save the report")
    parser.add_argument("--binary", action="store_true", help="Calculate metrics using Binary labels (Compliant vs Non-Compliant)")
    
    args = parser.parse_args()
    
    # 1. Resolve Files
    input_paths = [p.strip() for p in args.run]
    run_files = []
    
    for path in input_paths:
        if os.path.isdir(path):
            run_files.extend(glob.glob(os.path.join(path, "*.json")))
        elif "*" in path or "?" in path:
            run_files.extend(glob.glob(path))
        else:
            run_files.append(path)
    
    # Filter out duplicates and non-json
    run_files = sorted(list(set([f for f in run_files if f.endswith(".json")])))
    
    if not run_files:
        print(f"Error: No JSON files found for inputs: {args.run}")
        return

    # 2. Load Ground Truths
    with open(args.label_gt.strip(), 'r') as f:
        label_gt = json.load(f)
        
    with open(args.retrieval_gt.strip(), 'r') as f:
        ret_gt_list = json.load(f)
        ret_gt = {item['query']: set(item['expected_chunk_ids']) for item in ret_gt_list}

    # 3. Process all runs
    all_run_results = []
    for fpath in run_files:
        fname = os.path.basename(fpath)
        print(f"Processing run: {fname}")
        res = process_single_run(fpath, label_gt, ret_gt, args.binary)
        res['filename'] = fname
        all_run_results.append(res)

    # 4. Aggregate Metrics
    n_runs = len(all_run_results)
    
    # Classification averages
    accuracies = [r['classification']['accuracy'] for r in all_run_results]
    
    macro_precisions = [r['classification']['macro_precision'] for r in all_run_results]
    macro_recalls = [r['classification']['macro_recall'] for r in all_run_results]
    macro_f1s = [r['classification']['macro_f1'] for r in all_run_results]
    
    weighted_precisions = [r['classification']['weighted_precision'] for r in all_run_results]
    weighted_recalls = [r['classification']['weighted_recall'] for r in all_run_results]
    weighted_f1s = [r['classification']['weighted_f1'] for r in all_run_results]
    
    # Retrieval averages
    ret_precisions = [np.mean([m['p'] for m in r['retrieval']]) for r in all_run_results if r['retrieval']]
    ret_recalls = [np.mean([m['r'] for m in r['retrieval']]) for r in all_run_results if r['retrieval']]
    
    # Stability Analysis: For each criterion, how often did it get the same label?
    stability_data = defaultdict(list) # cid -> [pred1, pred2, ...]
    for r in all_run_results:
        for cid, pred in r['predictions'].items():
            stability_data[cid].append(pred)
            
    criterion_stability = {}
    for cid, preds in stability_data.items():
        if not preds: continue
        most_common_count = preds.count(max(set(preds), key=preds.count))
        criterion_stability[cid] = most_common_count / len(preds)

    # 5. Generate Report
    report = []
    report.append(f"Evaluation Report (Binary Mode: {args.binary})")
    report.append(f"Number of runs evaluated: {n_runs}")
    report.append("="*50)
    
    report.append("\n### Per-Run Classification Metrics (Weighted)")
    report.append(f"{'Run Filename':<80} | {'Acc':<6} | {'W-P':<6} | {'W-R':<6} | {'W-F1':<6}")
    report.append("-" * 115)
    for r in all_run_results:
        m = r['classification']
        report.append(f"{r['filename']:<80} | {m['accuracy']:<6.4f} | {m['weighted_precision']:<6.4f} | {m['weighted_recall']:<6.4f} | {m['weighted_f1']:<6.4f}")

    report.append("\n### Per-Run Confusion Matrices")
    for r in all_run_results:
        report.append(f"\nRun: {r['filename']}")
        report.append(format_confusion_matrix(r['confusion_matrix'], r['classes']))
        report.append("-" * 50)

    report.append("\n### Global Classification Metrics (Mean ± Std)")
    report.append(f"Accuracy:           {np.mean(accuracies):.4f} ± {np.std(accuracies):.4f}")
    report.append("-" * 40)
    report.append("Precision for each class but weights it by the number of actual samples (Support) in the Ground Truth.")
    report.append(f"Weighted-Precision: {np.mean(weighted_precisions):.4f} ± {np.std(weighted_precisions):.4f}")
    report.append(f"Weighted-Recall:    {np.mean(weighted_recalls):.4f} ± {np.std(weighted_recalls):.4f}")
    report.append(f"Weighted-F1 Score:  {np.mean(weighted_f1s):.4f} ± {np.std(weighted_f1s):.4f}")
    report.append("-" * 40)
    report.append("Precision for each class separately")
    report.append(f"Macro-Precision:    {np.mean(macro_precisions):.4f} ± {np.std(macro_precisions):.4f}")
    report.append(f"Macro-Recall:       {np.mean(macro_recalls):.4f} ± {np.std(macro_recalls):.4f}")
    report.append(f"Macro-F1 Score:     {np.mean(macro_f1s):.4f} ± {np.std(macro_f1s):.4f}")
    
    report.append("\n### Global Retrieval Metrics (Mean ± Std)")
    report.append(f"Avg Precision:    {np.mean(ret_precisions):.4f} ± {np.std(ret_precisions):.4f}")
    report.append(f"Avg Recall:       {np.mean(ret_recalls):.4f} ± {np.std(ret_recalls):.4f}")
    
    report.append("\n### Per-Criterion Stability (how consistent the AI is)")
    report.append(f"{'Criterion':<10} | {'Stability':<10} | {'Most Common Prediction'}")
    report.append("-" * 55)
    for cid in sorted(criterion_stability.keys()):
        preds = stability_data[cid]
        most_common = max(set(preds), key=preds.count)
        report.append(f"{cid:<10} | {criterion_stability[cid]:<10.2%} | {most_common}")
        
    report_text = "\n".join(report)
    print(report_text)
    
    output_path = args.output.strip()
    with open(output_path, 'w') as f:
        f.write(report_text)
    
    print(f"\n✅ Report saved to {output_path}")

if __name__ == "__main__":
    main()
