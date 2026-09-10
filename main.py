"""
Main CLI Interface for AI Customer Support Agent.
Supports dataset download, single message classification, and performance evaluation.
"""
import argparse
import sys
import os
import json

from src.agent import SupportAgent
from evaluate import run_evaluation
from data.download_data import main as run_download

def format_output(result: dict):
    """Formats classification result for clean terminal printing."""
    print("\n" + "="*70)
    print("  AI SUPPORT AGENT CLASSIFICATION RESULT")
    print("="*70)
    print(f"  Customer Tweet  : \"{result['text']}\"")
    print(f"  Classified Intent: {result['intent']}")
    print(f"  Confidence Score: {result['confidence']:.2f}")
    print(f"  Escalation Needed: {'YES' if result['needs_escalation'] else 'NO'}")
    print(f"  Routing Priority : {result['priority']}")
    if result['needs_escalation']:
        print(f"  Escalation Reason: {result['escalation_reason']}")
    print("\n  Suggested Response:")
    print(f"  -> \"{result['suggested_reply']}\"")
    print("="*70 + "\n")

def main():
    parser = argparse.ArgumentParser(description="AI Customer Support Agent for Intent Classification & Escalation.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Command 1: classify
    classify_parser = subparsers.add_parser("classify", help="Classify a customer message")
    classify_parser.add_argument("--text", "-t", type=str, required=True, help="Customer message text to classify")
    classify_parser.add_argument("--json", action="store_true", help="Output raw JSON format")

    # Command 2: evaluate
    subparsers.add_parser("evaluate", help="Run evaluation benchmark on 150 hand-labeled examples")

    # Command 3: download
    subparsers.add_parser("download", help="Download Kaggle Twitter dataset and filter Amazon tweets")

    args = parser.parse_args()

    if args.command == "classify":
        agent = SupportAgent()
        result = agent.process_message(args.text)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            format_output(result)

    elif args.command == "evaluate":
        run_evaluation()

    elif args.command == "download":
        run_download()

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
