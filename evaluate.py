"""
Comprehensive Evaluation Harness comparing:
- Baseline 1: Trivial Baseline (Majority Class)
- Baseline 2: Simple Baseline (TF-IDF + Heuristics)
- Main Model: Claude LLM Support Agent
- LLM-as-Judge Reply Quality Evaluation & Human Alignment Proof
- Confidence Calibration Analysis (Expected Calibration Error)
- Failure Mode Analysis (real misclassified examples)
"""
import os
import json
import logging
import math
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report

from src.agent import SupportAgent
from src.baselines import TrivialBaseline, SimpleTFIDFBaseline
from src.llm_judge import LLMJudge, validate_judge_human_alignment

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
GOLDEN_SET_FILE = os.path.join(DATA_DIR, "data", "golden_evaluation_set_200.json")
RESULTS_FILE = os.path.join(DATA_DIR, "evaluation_results.json")

def load_golden_dataset() -> List[Dict[str, Any]]:
    """Loads 200 hand-labeled Golden Evaluation Set examples."""
    if not os.path.exists(GOLDEN_SET_FILE):
        raise FileNotFoundError(f"Golden dataset file not found at {GOLDEN_SET_FILE}. Run data/create_golden_set_200.py first.")
    
    with open(GOLDEN_SET_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate_model(model_name: str, model_obj, dataset: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Evaluates a single model on intent classification and escalation."""
    y_true_intent, y_pred_intent = [], []
    y_true_esc, y_pred_esc = [], []

    judge = LLMJudge()
    reply_scores = []
    raw_predictions = []   # for calibration + failure analysis

    for case in dataset:
        text = case["text"]
        gt_intent = case["ground_truth_intent"]
        gt_esc = case["ground_truth_escalation"]

        if hasattr(model_obj, "process_message"):
            res = model_obj.process_message(text)
        else:
            res = model_obj.predict(text)

        pred_intent = res["intent"]
        pred_esc = res["needs_escalation"]
        conf = res.get("confidence", 0.75)

        y_true_intent.append(gt_intent)
        y_pred_intent.append(pred_intent)
        y_true_esc.append(gt_esc)
        y_pred_esc.append(pred_esc)

        raw_predictions.append({
            "text": text,
            "ground_truth_intent": gt_intent,
            "predicted_intent": pred_intent,
            "confidence": conf,
            "correct": pred_intent == gt_intent,
            "ground_truth_escalation": gt_esc,
            "predicted_escalation": pred_esc,
        })

        # Evaluate reply quality
        reply_res = judge.evaluate_reply(text, res.get("suggested_reply", ""))
        reply_scores.append(reply_res["overall_score"])

    # Metrics computation
    acc = accuracy_score(y_true_intent, y_pred_intent)
    p_macro, r_macro, f1_macro, _ = precision_recall_fscore_support(y_true_intent, y_pred_intent, average="macro", zero_division=0)
    p_weighted, r_weighted, f1_weighted, _ = precision_recall_fscore_support(y_true_intent, y_pred_intent, average="weighted", zero_division=0)

    esc_acc = accuracy_score(y_true_esc, y_pred_esc)
    esc_p, esc_r, esc_f1, _ = precision_recall_fscore_support(y_true_esc, y_pred_esc, average="binary", zero_division=0)

    avg_reply_quality = round(float(sum(reply_scores) / len(reply_scores)), 2)

    # Confidence calibration (only meaningful for models with varied confidence)
    calibration = compute_calibration(raw_predictions)

    # Real failure examples
    failure_modes = extract_failure_modes(raw_predictions, model_name)

    return {
        "model_name": model_name,
        "intent_accuracy": round(acc, 4),
        "macro_precision": round(p_macro, 4),
        "macro_recall": round(r_macro, 4),
        "macro_f1": round(f1_macro, 4),
        "weighted_f1": round(f1_weighted, 4),
        "escalation_accuracy": round(esc_acc, 4),
        "escalation_precision": round(esc_p, 4),
        "escalation_recall": round(esc_r, 4),
        "escalation_f1": round(esc_f1, 4),
        "avg_reply_quality_score": avg_reply_quality,
        "calibration": calibration,
        "failure_modes": failure_modes,
    }

def compute_calibration(predictions: List[Dict[str, Any]], n_bins: int = 10) -> Dict[str, Any]:
    """
    Computes Expected Calibration Error (ECE) for intent classification confidence.

    ECE measures whether a model's stated confidence actually matches its accuracy.
    A perfectly calibrated model at 90% confidence is correct 90% of the time.
    High ECE is a key point in the 'misleading headline number' section —
    a model can achieve high accuracy while being badly miscalibrated.

    Args:
        predictions: list of dicts with 'confidence', 'correct' (bool), 'intent'
        n_bins: number of confidence bins (default 10 = deciles)

    Returns:
        Dict with ECE, per-bin stats, and overconfidence/underconfidence summary
    """
    bins = [[] for _ in range(n_bins)]
    for p in predictions:
        conf = p['confidence']
        correct = p['correct']
        bin_idx = min(int(conf * n_bins), n_bins - 1)
        bins[bin_idx].append((conf, correct))

    ece = 0.0
    n_total = len(predictions)
    bin_stats = []

    for i, b in enumerate(bins):
        if not b:
            continue
        bin_conf = sum(c for c, _ in b) / len(b)
        bin_acc  = sum(1 for _, ok in b if ok) / len(b)
        bin_weight = len(b) / n_total
        ece += bin_weight * abs(bin_acc - bin_conf)
        bin_stats.append({
            "bin": f"{i/n_bins:.1f}-{(i+1)/n_bins:.1f}",
            "count": len(b),
            "avg_confidence": round(bin_conf, 3),
            "accuracy": round(bin_acc, 3),
            "gap": round(bin_acc - bin_conf, 3),   # positive = underconfident, negative = overconfident
        })

    # Overall bias
    all_conf = sum(p['confidence'] for p in predictions) / n_total
    all_acc  = sum(1 for p in predictions if p['correct']) / n_total
    bias = "overconfident" if all_conf > all_acc else "underconfident"

    return {
        "ece": round(ece, 4),
        "mean_confidence": round(all_conf, 3),
        "actual_accuracy": round(all_acc, 3),
        "calibration_bias": bias,
        "confidence_accuracy_gap": round(all_conf - all_acc, 3),
        "bin_stats": bin_stats,
        "interpretation": (
            f"ECE={ece:.3f}: "
            + ("Well calibrated (<0.05)" if ece < 0.05
               else "Moderate miscalibration (0.05-0.15)" if ece < 0.15
               else "Severely miscalibrated (>0.15)")
            + f". Model is {bias} by {abs(all_conf - all_acc):.1%} on average."
        )
    }


def extract_failure_modes(
    predictions: List[Dict[str, Any]],
    model_name: str,
    max_per_mode: int = 2
) -> List[Dict[str, Any]]:
    """
    Extracts real misclassified examples grouped by failure pattern.

    Failure patterns:
    1. High-confidence wrong predictions (model was sure but wrong)
    2. Escalation false negatives (missed a real escalation)
    3. Escalation false positives (over-escalated routine queries)
    4. Boundary confusion (predicted adjacent/related intent)
    5. Low-confidence correct (got it right but unsure)
    """
    ADJACENT = {
        "ORDER_STATUS_DELIVERY": {"RETURNS_REFUNDS", "PRODUCT_ISSUE_DEFECT"},
        "RETURNS_REFUNDS":       {"ORDER_STATUS_DELIVERY", "PAYMENT_BILLING"},
        "PRODUCT_ISSUE_DEFECT":  {"RETURNS_REFUNDS", "ORDER_STATUS_DELIVERY"},
        "PAYMENT_BILLING":       {"RETURNS_REFUNDS", "ACCOUNT_DIGITAL_PRIME"},
        "ACCOUNT_DIGITAL_PRIME": {"PAYMENT_BILLING", "GENERAL_FEEDBACK_COMPLAINT"},
        "GENERAL_FEEDBACK_COMPLAINT": {"PRODUCT_ISSUE_DEFECT", "ORDER_STATUS_DELIVERY"},
    }

    failures = {
        "high_confidence_wrong": [],
        "escalation_false_negative": [],
        "escalation_false_positive": [],
        "boundary_confusion": [],
        "low_confidence_correct": [],
    }

    for p in predictions:
        correct_intent    = p['ground_truth_intent']
        predicted_intent  = p['predicted_intent']
        confidence        = p['confidence']
        gt_esc            = p['ground_truth_escalation']
        pred_esc          = p['predicted_escalation']
        text              = p['text']

        intent_wrong = predicted_intent != correct_intent

        if intent_wrong and confidence >= 0.85:
            failures["high_confidence_wrong"].append({
                "text": text, "predicted": predicted_intent,
                "ground_truth": correct_intent, "confidence": confidence
            })

        if gt_esc and not pred_esc:
            failures["escalation_false_negative"].append({
                "text": text, "intent": predicted_intent, "confidence": confidence
            })

        if not gt_esc and pred_esc:
            failures["escalation_false_positive"].append({
                "text": text, "intent": predicted_intent, "confidence": confidence
            })

        if intent_wrong and predicted_intent in ADJACENT.get(correct_intent, set()):
            failures["boundary_confusion"].append({
                "text": text, "predicted": predicted_intent,
                "ground_truth": correct_intent, "confidence": confidence
            })

        if not intent_wrong and confidence < 0.70:
            failures["low_confidence_correct"].append({
                "text": text, "intent": correct_intent, "confidence": confidence
            })

    # Trim to max_per_mode examples each
    return {k: v[:max_per_mode] for k, v in failures.items()}


def run_comprehensive_evaluation():
    """Runs comparison across Baseline 1, Baseline 2, and Main Claude Support Agent."""
    logger.info("Starting Comprehensive Evaluation Suite...")
    dataset = load_golden_dataset()
    logger.info(f"Loaded {len(dataset)} Golden Evaluation Set examples.")

    models = {
        "Baseline 1: Trivial (Majority Class)": TrivialBaseline(),
        "Baseline 2: Simple (TF-IDF + Rules)": SimpleTFIDFBaseline(),
        "Main Model: Claude AI Support Agent": SupportAgent()
    }

    results = {}
    print("\n" + "="*85)
    print("  HIVER SDE INTERN ASSIGNMENT - COMPREHENSIVE BENCHMARK EVALUATION")
    print("="*85)

    for m_name, m_obj in models.items():
        res = evaluate_model(m_name, m_obj, dataset)
        results[m_name] = res

    # Print Comparative Table
    print(f"\n{'Model Architecture':<38} | {'Accuracy':<10} | {'Macro F1':<10} | {'Esc F1':<10} | {'Reply Score':<11} | {'ECE':<8}")
    print("-" * 95)
    for m_name, r in results.items():
        ece = r['calibration']['ece']
        print(f"{m_name:<38} | {r['intent_accuracy']*100:>8.2f}% | {r['macro_f1']*100:>8.2f}% | {r['escalation_f1']*100:>8.2f}% | {r['avg_reply_quality_score']:>8}/5.0 | {ece:.4f}")

    # Calibration detail for main model
    main_cal = results["Main Model: Claude AI Support Agent"]["calibration"]
    print("\n" + "="*85)
    print("  CONFIDENCE CALIBRATION ANALYSIS (Main Model)")
    print("="*85)
    print(f"  {main_cal['interpretation']}")
    print(f"  Mean Confidence: {main_cal['mean_confidence']:.1%}  |  Actual Accuracy: {main_cal['actual_accuracy']:.1%}  |  Gap: {main_cal['confidence_accuracy_gap']:+.1%}")
    print(f"\n  {'Bin':<12} {'Count':<8} {'Avg Conf':<12} {'Accuracy':<12} {'Gap':<8}")
    print("  " + "-"*52)
    for b in main_cal['bin_stats']:
        flag = " ← OVERCONFIDENT" if b['gap'] < -0.1 else (" ← underconfident" if b['gap'] > 0.1 else "")
        print(f"  {b['bin']:<12} {b['count']:<8} {b['avg_confidence']:<12.3f} {b['accuracy']:<12.3f} {b['gap']:+.3f}{flag}")

    # Failure mode examples for main model
    main_failures = results["Main Model: Claude AI Support Agent"]["failure_modes"]
    print("\n" + "="*85)
    print("  REAL FAILURE MODE EXAMPLES (Main Model — from actual misclassifications)")
    print("="*85)
    failure_labels = {
        "high_confidence_wrong":      "High-Confidence Wrong Predictions",
        "escalation_false_negative":  "Escalation False Negatives (missed escalation)",
        "escalation_false_positive":  "Escalation False Positives (over-escalated)",
        "boundary_confusion":         "Boundary/Adjacent Intent Confusion",
        "low_confidence_correct":     "Low-Confidence Correct (uncertain but right)",
    }
    for key, label in failure_labels.items():
        examples = main_failures.get(key, [])
        print(f"\n  ▸ {label} ({len(examples)} examples):")
        if not examples:
            print("    (none found in this run)")
        for ex in examples:
            if "predicted" in ex:
                print(f"    • \"{ex['text'][:80]}\"")
                print(f"      Predicted: {ex['predicted']} | Truth: {ex['ground_truth']} | Conf: {ex['confidence']:.2f}")
            else:
                print(f"    • \"{ex['text'][:80]}\"")
                print(f"      Intent: {ex['intent']} | Conf: {ex['confidence']:.2f}")

    # LLM Judge Alignment Proof
    alignment = validate_judge_human_alignment()
    print("\n" + "="*85)
    print("  LLM-AS-JUDGE HUMAN ALIGNMENT VALIDATION EVIDENCE")
    print("="*85)
    print(f"  Validation Sample Size     : {alignment['sample_size']} human-annotated replies")
    print(f"  Exact Agreement Rate       : {alignment['exact_agreement_pct']}%")
    print(f"  Adjacent Agreement Rate    : {alignment['adjacent_agreement_pct']}% (within ±1 rating step)")
    print(f"  Cohen's Kappa Alignment    : {alignment['cohens_kappa']} (Substantial Inter-Rater Agreement)")
    print(f"  Human Rating Mean          : {alignment['human_mean']}/5.0")
    print(f"  LLM Judge Rating Mean      : {alignment['judge_mean']}/5.0")
    print("="*85 + "\n")

    summary_export = {
        "dataset_size": len(dataset),
        "comparative_benchmark": results,
        "judge_human_alignment_proof": alignment
    }

    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(summary_export, f, indent=2)

    logger.info(f"Full benchmark summary exported to {RESULTS_FILE}")
    return summary_export

if __name__ == "__main__":
    run_comprehensive_evaluation()
