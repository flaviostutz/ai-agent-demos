#!/usr/bin/env python3
"""Automated agent evaluation script with MLFlow tracking."""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.loan_approval.agent import LoanApprovalAgent
from shared.datasets import DatasetManager
from shared.logging_utils import get_logger
from shared.model_evaluation import ModelEvaluator

logger = get_logger(__name__)


def create_agent_wrapper(agent: LoanApprovalAgent):
    """
    Create a wrapper function for the agent that matches evaluation interface.

    Args:
        agent: LoanApprovalAgent instance

    Returns:
        Callable that takes dict and returns dict
    """

    def agent_func(request_data: dict) -> dict:
        """Wrapper function for agent evaluation."""
        try:
            # Create LoanRequest from dict
            from agents.loan_approval.agent import LoanRequest

            loan_request = LoanRequest(**request_data)

            # Process request
            decision = agent.process_request(loan_request)

            # Return as dict
            return {
                "outcome": decision.outcome,
                "risk_score": decision.risk_score,
                "reason": decision.reason,
                "approved_amount": decision.approved_amount,
                "interest_rate": decision.interest_rate,
            }
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            return {"outcome": "error", "risk_score": 100, "reason": str(e)}

    return agent_func


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate agent performance on datasets")
    parser.add_argument(
        "--agent",
        type=str,
        default="loan_approval",
        choices=["loan_approval"],
        help="Agent to evaluate",
    )
    parser.add_argument(
        "--dataset",
        type=str,
        default="loan_approval_test_set",
        help="Dataset name to evaluate on",
    )
    parser.add_argument(
        "--target-field",
        type=str,
        default="expected_outcome",
        help="Field name containing expected outcomes",
    )
    parser.add_argument(
        "--prediction-field",
        type=str,
        default="outcome",
        help="Field name in agent response containing predictions",
    )
    parser.add_argument(
        "--no-mlflow",
        action="store_true",
        help="Disable MLFlow logging",
    )
    parser.add_argument(
        "--drift-detection",
        action="store_true",
        help="Run drift detection against baseline",
    )
    parser.add_argument(
        "--baseline-dataset",
        type=str,
        help="Baseline dataset for drift detection",
    )

    args = parser.parse_args()

    logger.info(f"Starting evaluation of {args.agent} on dataset '{args.dataset}'")

    # Initialize agent
    if args.agent == "loan_approval":
        agent = LoanApprovalAgent()
        agent_func = create_agent_wrapper(agent)
    else:
        logger.error(f"Unknown agent: {args.agent}")
        sys.exit(1)

    # Initialize dataset manager
    dataset_manager = DatasetManager()

    # Validate dataset exists
    try:
        dataset_manager.get_dataset_info(args.dataset)
    except FileNotFoundError:
        logger.error(f"Dataset '{args.dataset}' not found")
        logger.info(f"Available datasets: {dataset_manager.list_datasets()}")
        sys.exit(1)

    # Initialize evaluator
    evaluator = ModelEvaluator(
        agent_name=args.agent, agent_func=agent_func, dataset_manager=dataset_manager
    )

    # Run evaluation
    logger.info("Running evaluation...")
    metrics = evaluator.evaluate_dataset(
        dataset_name=args.dataset,
        target_field=args.target_field,
        prediction_field=args.prediction_field,
        log_to_mlflow=not args.no_mlflow,
    )

    # Print results
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    print(f"Dataset: {args.dataset}")
    print(f"Agent: {args.agent}")
    print("-" * 60)
    print(f"Accuracy:          {metrics.accuracy:.3f}")
    print(f"Precision:         {metrics.precision:.3f}")
    print(f"Recall:            {metrics.recall:.3f}")
    print(f"F1 Score:          {metrics.f1_score:.3f}")
    print("-" * 60)
    print(f"Avg Latency:       {metrics.avg_latency_ms:.2f} ms")
    print(f"P95 Latency:       {metrics.p95_latency_ms:.2f} ms")
    print(f"P99 Latency:       {metrics.p99_latency_ms:.2f} ms")
    print("-" * 60)
    print(f"Error Rate:        {metrics.error_rate:.3f}")
    if metrics.total_cost > 0:
        print(f"Total Cost:        ${metrics.total_cost:.4f}")
        print(f"Avg Cost/Request:  ${metrics.avg_cost_per_request:.4f}")
    print("=" * 60 + "\n")

    # Run drift detection if requested
    if args.drift_detection:
        if not args.baseline_dataset:
            logger.error("--baseline-dataset required for drift detection")
            sys.exit(1)

        logger.info(f"Running drift detection against baseline '{args.baseline_dataset}'")
        drift_results = evaluator.detect_drift(
            baseline_dataset=args.baseline_dataset, current_dataset=args.dataset
        )

        print("\n" + "=" * 60)
        print("DRIFT DETECTION RESULTS")
        print("=" * 60)
        print(f"Baseline: {args.baseline_dataset}")
        print(f"Current:  {args.dataset}")
        print(f"Has Drift: {'YES' if drift_results['has_drift'] else 'NO'}")
        print("-" * 60)

        for metric_name, metric_data in drift_results["metrics"].items():
            print(f"{metric_name}:")
            print(f"  Baseline: {metric_data['baseline']:.3f}")
            print(f"  Current:  {metric_data['current']:.3f}")
            print(f"  Drift:    {metric_data['drift']:+.3f} ({metric_data['drift_pct']:+.1f}%)")
            if metric_data["has_drift"]:
                print("  ⚠️  DRIFT DETECTED")
            print()
        print("=" * 60 + "\n")

    logger.info("Evaluation complete!")

    if not args.no_mlflow:
        logger.info("Results logged to MLFlow. Check your Databricks workspace.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
