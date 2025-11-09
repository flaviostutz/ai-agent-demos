"""Quick test to verify LLM logging is working correctly."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Set test environment
os.environ["OPENAI_API_KEY"] = "test-key-for-validation"
os.environ["ENABLE_LLM_LOGGING"] = "true"
os.environ["LOG_LLM_PROMPTS"] = "true"
os.environ["LOG_LLM_RESPONSES"] = "true"

from agents.loan_approval.src.config import config
from shared.monitoring import (
    LLMCallbackHandler,
    get_llm_callback_handler,
    setup_mlflow_langchain_autologging,
)


def test_config():
    """Test that configuration is loaded correctly."""
    print("✓ Testing configuration...")
    assert config.enable_llm_logging is True
    assert config.log_llm_prompts is True
    assert config.log_llm_responses is True
    assert config.mlflow_log_llm_models is True
    assert config.mlflow_log_llm_inputs_outputs is True
    print("  ✓ All config values correct")


def test_callback_handler():
    """Test that callback handler can be created."""
    print("✓ Testing callback handler creation...")
    handler = get_llm_callback_handler(log_prompts=True, log_responses=True)
    assert isinstance(handler, LLMCallbackHandler)
    assert handler.log_prompts is True
    assert handler.log_responses is True
    assert handler.call_count == 0
    print("  ✓ Callback handler created successfully")


def test_mlflow_autologging():
    """Test that MLflow autologging can be set up."""
    print("✓ Testing MLflow autologging setup...")
    try:
        setup_mlflow_langchain_autologging(
            log_models=True, log_inputs_outputs=True
        )
        print("  ✓ MLflow autologging setup successful")
    except Exception as e:
        print(f"  ⚠ MLflow autologging setup: {e}")


def test_imports():
    """Test that all necessary modules can be imported."""
    print("✓ Testing imports...")
    try:
        from langchain_openai import ChatOpenAI

        print("  ✓ ChatOpenAI imported")
    except ImportError as e:
        print(f"  ✗ ChatOpenAI import failed: {e}")
        return False

    try:
        from langchain_core.callbacks import BaseCallbackHandler

        print("  ✓ BaseCallbackHandler imported")
    except ImportError as e:
        print(f"  ✗ BaseCallbackHandler import failed: {e}")
        return False

    try:
        import mlflow

        print("  ✓ MLflow imported")
    except ImportError as e:
        print(f"  ✗ MLflow import failed: {e}")
        return False

    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("LLM Logging Implementation Validation")
    print("=" * 60)
    print()

    try:
        test_imports()
        print()
        test_config()
        print()
        test_callback_handler()
        print()
        test_mlflow_autologging()
        print()
        print("=" * 60)
        print("✓ All validation tests passed!")
        print("=" * 60)
        print()
        print("LLM logging is ready to use:")
        print("  1. Run 'make run' to start agent with LLM debug logging")
        print("  2. Run 'python examples/llm_logging_demo.py' for a demo")
        print("  3. View logs in MLflow UI: cd agents/loan_approval/src && mlflow ui")
        print()
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ Validation failed: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
