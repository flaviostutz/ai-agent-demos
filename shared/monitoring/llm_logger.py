"""LLM interaction logging with LangChain callbacks and MLflow integration."""

import time
from typing import Any

import mlflow
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

from shared.monitoring.logger import get_logger

logger = get_logger(__name__)


class LLMCallbackHandler(BaseCallbackHandler):
    """Custom callback handler to log all LLM interactions with detailed context."""

    def __init__(self, log_prompts: bool = True, log_responses: bool = True) -> None:
        """Initialize LLM callback handler.

        Args:
            log_prompts: Whether to log prompts (may contain sensitive data)
            log_responses: Whether to log LLM responses

        """
        super().__init__()
        self.log_prompts = log_prompts
        self.log_responses = log_responses
        self.call_count = 0
        self.start_time = None

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], **kwargs: Any
    ) -> None:
        """Log when LLM starts generating.

        Args:
            serialized: Serialized LLM configuration
            prompts: List of prompts sent to LLM
            **kwargs: Additional arguments

        """
        self.call_count += 1
        self.start_time = time.time()

        logger.info(f"LLM call #{self.call_count} started")

        if self.log_prompts and prompts:
            for i, prompt in enumerate(prompts):
                logger.debug(f"LLM Prompt #{i + 1}:\n{prompt}")
                # Log to MLflow if in active run
                try:
                    if mlflow.active_run():
                        mlflow.log_text(
                            prompt, f"prompts/llm_call_{self.call_count}_prompt_{i + 1}.txt"
                        )
                except Exception as e:
                    logger.warning(f"Failed to log prompt to MLflow: {e}")

        # Log model configuration
        model_name = serialized.get("name", "unknown")
        logger.info(f"LLM Model: {model_name}")
        try:
            if mlflow.active_run():
                mlflow.log_param(f"llm_call_{self.call_count}_model", model_name)
        except Exception as e:
            logger.warning(f"Failed to log model to MLflow: {e}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Log when LLM finishes generating.

        Args:
            response: LLM generation result
            **kwargs: Additional arguments

        """
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            logger.info(
                f"LLM call #{self.call_count} completed in {elapsed_time:.3f}s"
            )

            # Log timing metric
            try:
                if mlflow.active_run():
                    mlflow.log_metric(
                        f"llm_call_{self.call_count}_latency_sec", elapsed_time
                    )
            except Exception as e:
                logger.warning(f"Failed to log latency to MLflow: {e}")

        # Log token usage if available
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            if token_usage:
                total_tokens = token_usage.get("total_tokens", 0)
                prompt_tokens = token_usage.get("prompt_tokens", 0)
                completion_tokens = token_usage.get("completion_tokens", 0)

                logger.info(
                    f"LLM tokens - Total: {total_tokens}, "
                    f"Prompt: {prompt_tokens}, Completion: {completion_tokens}"
                )

                # Log token metrics
                try:
                    if mlflow.active_run():
                        mlflow.log_metrics({
                            f"llm_call_{self.call_count}_total_tokens": float(total_tokens),
                            f"llm_call_{self.call_count}_prompt_tokens": float(prompt_tokens),
                            f"llm_call_{self.call_count}_completion_tokens": float(completion_tokens),
                        })
                except Exception as e:
                    logger.warning(f"Failed to log tokens to MLflow: {e}")

        # Log responses
        if self.log_responses and response.generations:
            for i, generation_list in enumerate(response.generations):
                for j, generation in enumerate(generation_list):
                    response_text = generation.text
                    logger.debug(f"LLM Response #{i + 1}.{j + 1}:\n{response_text}")

                    # Log to MLflow if in active run
                    try:
                        if mlflow.active_run():
                            mlflow.log_text(
                                response_text,
                                f"responses/llm_call_{self.call_count}_response_{i + 1}_{j + 1}.txt",
                            )
                    except Exception as e:
                        logger.warning(f"Failed to log response to MLflow: {e}")

    def on_llm_error(self, error: Exception | KeyboardInterrupt, **kwargs: Any) -> None:
        """Log when LLM encounters an error.

        Args:
            error: The error that occurred
            **kwargs: Additional arguments

        """
        logger.error(f"LLM call #{self.call_count} failed with error: {error}")

        # Log error to MLflow
        try:
            if mlflow.active_run():
                mlflow.log_param(f"llm_call_{self.call_count}_error", str(error))
        except Exception as e:
            logger.warning(f"Failed to log error to MLflow: {e}")


def setup_mlflow_langchain_autologging(
    log_models: bool = True,
    log_input_examples: bool = True,
    log_model_signatures: bool = True,
    log_inputs_outputs: bool = True,
) -> None:
    """Enable MLflow autologging for LangChain.

    This will automatically log:
    - Model configuration and parameters
    - Input prompts and output responses
    - Token usage and performance metrics
    - Model artifacts

    Args:
        log_models: Whether to log the model
        log_input_examples: Whether to log input examples
        log_model_signatures: Whether to log model signatures
        log_inputs_outputs: Whether to log inputs and outputs (prompts/responses)

    """
    try:
        mlflow.langchain.autolog(
            log_models=log_models,
            log_input_examples=log_input_examples,
            log_model_signatures=log_model_signatures,
            log_inputs_outputs=log_inputs_outputs,
            silent=False,
        )
        logger.info("MLflow LangChain autologging enabled")
    except Exception as e:
        logger.warning(f"Failed to enable MLflow LangChain autologging: {e}")


def get_llm_callback_handler(
    log_prompts: bool = True, log_responses: bool = True
) -> LLMCallbackHandler:
    """Get an LLM callback handler instance.

    Args:
        log_prompts: Whether to log prompts (may contain sensitive data)
        log_responses: Whether to log LLM responses

    Returns:
        LLMCallbackHandler instance

    """
    return LLMCallbackHandler(log_prompts=log_prompts, log_responses=log_responses)
