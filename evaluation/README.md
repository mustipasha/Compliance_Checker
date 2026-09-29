# Evaluation Data

This folder contains the data and the script behind the functionality tests reported in Chapter 5 of the master's thesis.

## Contents

| Path | Content |
|---|---|
| `runs/sanity_check/` | The five runs of the sanity check against the Safety and Security chapter of the Code of Practice |
| `runs/nist_baseline/` | The five baseline runs against the NIST AI RMF |
| `../backend/ablation_runs/` | The five ablation runs against the NIST AI RMF (`suppress_overreach=true`) |
| `assessment_ground_truth.json` | Reference labels for the NIST AI RMF test (26 `PARTIALLY_COMPLIANT`, 6 `NOT_COMPLIANT`) |
| `reference_annotation_nist.docx` | Annotation instruction, labels and justifications behind the NIST AI RMF reference labels |
| `sanity_ground_truth.json` | Reference labels for the sanity check. Every criterion is `COMPLIANT`, as described in the thesis. |
| `calculate_metrics.py` | Computes accuracy, per-class and weighted metrics, confusion matrices and stability |
| `reports/` | The original metric reports for the sanity check and the NIST baseline |
| `../backend/evaluation_report_without_alignment_overreach.txt` | The original metric report for the ablation |
| `retrieval_quality_sanity_check.xlsx` | Manual retrieval annotation for the sanity check (Table 5.1) |

All runs were made in triple-agent mode with OpenAI `gpt-5-nano`. The ablation files record an empty model field because `run_ablation.py` does not pass a model, so the backend used its default (`gpt-5-nano`).

## Reproducing the metrics

Run from this folder with Python 3 and `numpy` installed:

```bash
python calculate_metrics.py --run runs/sanity_check --label_gt sanity_ground_truth.json --retrieval_gt ../backend/ground_truth.json
python calculate_metrics.py --run runs/nist_baseline --label_gt assessment_ground_truth.json --retrieval_gt ../backend/ground_truth.json
python calculate_metrics.py --run ../backend/ablation_runs --label_gt assessment_ground_truth.json --retrieval_gt ../backend/ground_truth.json
```

Each command writes `evaluation_report.txt` unless `--output` is given. The global metrics match the reports in `reports/` and the ablation report in `backend/`.

The pilot user study data is not included here because it contains personal data.
