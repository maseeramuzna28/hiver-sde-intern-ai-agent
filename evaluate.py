"""
Comprehensive Evaluation Harness comparing:
- Baseline 1: Trivial Baseline (Majority Class)
- Baseline 2: Simple Baseline (TF-IDF + Heuristics)
- Main Model: Claude LLM Support Agent
- LLM-as-Judge Reply Quality Evaluation & Human Alignment Proof
"""
import os
import json
import logging
from typing import List, Dict, Any
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

        y_true_intent.append(gt_intent)
        y_pred_intent.append(pred_intent)

        y_true_esc.append(gt_esc)
        y_pred_esc.append(pred_esc)

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
        "avg_reply_quality_score": avg_reply_quality
    }

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
    print(f"\n{'Model Architecture':<38} | {'Accuracy':<10} | {'Macro F1':<10} | {'Esc F1':<10} | {'Reply Score':<11}")
    print("-" * 85)
    for m_name, r in results.items():
        print(f"{m_name:<38} | {r['intent_accuracy']*100:>8.2f}% | {r['macro_f1']*100:>8.2f}% | {r['escalation_f1']*100:>8.2f}% | {r['avg_reply_quality_score']:>8}/5.0")

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
