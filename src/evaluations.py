import json
import logging
from typing import Any, Optional, Dict
from langsmith.evaluation import EvaluationResult, run_evaluator
from langsmith.schemas import Run, Example
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import PromptTemplate

logger = logging.getLogger(__name__)

# LLM to be used for LLM-as-a-judge evaluations
llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0, max_retries=10)

# =====================================================================
# 1. Task Success Rate
# - Definition & measurement techniques
# - Absolute vs relative success
# =====================================================================
@run_evaluator
def evaluate_task_success(run: Run, example: Optional[Example] = None) -> EvaluationResult:
    """
    Evaluates the Task Success Rate.
    Absolute success checks if the main goal was completely achieved (1 or 0).
    Relative success measures partial completion on a scale.
    """
    prediction = run.outputs.get("output", "") if run.outputs else ""
    reference = example.outputs.get("expected", "") if example and example.outputs else ""
    input_query = run.inputs.get("input", "") if run.inputs else ""

    if not prediction or not input_query:
        return EvaluationResult(key="task_success_rate", score=0, comment="Missing prediction or input.")

    # Using LLM to score success relative and absolute
    prompt = f"""
    Evaluate the success of the system based on the user's input.
    Input: {input_query}
    System Output: {prediction}
    Expected (if any): {reference}

    Score 1.0 if the task was completely successful, 0.5 for partial success (relative), and 0.0 for failure.
    Return ONLY a numerical score.
    """
    
    try:
        score_str = llm.invoke(prompt).content.strip()
        score = float(score_str)
    except Exception as e:
        logger.error(f"Error evaluating task success: {e}")
        score = 0.0

    return EvaluationResult(
        key="task_success_rate",
        score=score,
        comment="Score evaluated based on input task fulfillment."
    )


# =====================================================================
# 2. Coherence
# - Logical flow, context continuity
# - Detecting contradictions
# =====================================================================
@run_evaluator
def evaluate_coherence(run: Run, example: Optional[Example] = None) -> EvaluationResult:
    """
    Evaluates Coherence (Logical flow, context continuity, contradiction detection).
    """
    prediction = run.outputs.get("output", "") if run.outputs else ""
    
    if not prediction:
        return EvaluationResult(key="coherence", score=0, comment="Empty output.")

    prompt = f"""
    Analyze the following text for coherence, logical flow, and contradictions.
    Text: {prediction}

    Provide a coherence score from 0.0 to 1.0, where 1.0 means perfectly logical, fluent, and devoid of contradictions.
    Return ONLY a numerical score.
    """
    
    try:
        score_str = llm.invoke(prompt).content.strip()
        score = float(score_str)
    except Exception as e:
        logger.error(f"Error evaluating coherence: {e}")
        score = 0.0

    return EvaluationResult(
        key="coherence",
        score=score,
        comment="Evaluated logical flow and context continuity."
    )


# =====================================================================
# 3. Correctness
# - Ground truth comparison
# - Hallucination detection
# =====================================================================
@run_evaluator
def evaluate_correctness(run: Run, example: Optional[Example] = None) -> EvaluationResult:
    """
    Evaluates Correctness including Ground truth comparison and Hallucination detection.
    """
    prediction = run.outputs.get("output", "") if run.outputs else ""
    context = run.outputs.get("context", "") if run.outputs else "" # Or wherever context is stored
    reference = example.outputs.get("expected", "") if example and example.outputs else ""

    if not prediction:
        return EvaluationResult(key="correctness", score=0, comment="Empty output.")

    # Combining ground truth check with hallucination detection (faithfulness to context)
    prompt = f"""
    Evaluate the correctness of the answer.
    Answer: {prediction}
    Context provided to agent: {context}
    Ground Truth: {reference}

    Check for factual correctness against Ground Truth and ensure no hallucinations outside the Context.
    Return a correctness score from 0.0 to 1.0. 
    Return ONLY a numerical score.
    """
    
    try:
        score_str = llm.invoke(prompt).content.strip()
        score = float(score_str)
    except Exception as e:
        logger.error(f"Error evaluating correctness: {e}")
        score = 0.0

    return EvaluationResult(
        key="correctness",
        score=score,
        comment="Checked against ground truth and verified hallucination absence."
    )


# =====================================================================
# 4. Coverage
# - Completeness of response
# - Edge-case handling
# =====================================================================
@run_evaluator
def evaluate_coverage(run: Run, example: Optional[Example] = None) -> EvaluationResult:
    """
    Evaluates Coverage (Completeness of response, Edge-case handling).
    """
    prediction = run.outputs.get("output", "") if run.outputs else ""
    input_query = run.inputs.get("input", "") if run.inputs else ""

    if not prediction:
        return EvaluationResult(key="coverage", score=0, comment="Empty output.")

    prompt = f"""
    Evaluate how completely the system addressed the prompt, including any implicit edge cases.
    Prompt: {input_query}
    System Output: {prediction}

    Score from 0.0 to 1.0 where 1.0 means full coverage of all parts of the user question and proper edge-case handling.
    Return ONLY a numerical score.
    """
    
    try:
        score_str = llm.invoke(prompt).content.strip()
        score = float(score_str)
    except Exception as e:
        logger.error(f"Error evaluating coverage: {e}")
        score = 0.0

    return EvaluationResult(
        key="coverage",
        score=score,
        comment="Assessed response completeness and edge-case coverage."
    )


# =====================================================================
# 5. Latency
# - End-to-end time vs step-by-step latency
# - Trade-offs between speed and accuracy
# =====================================================================
@run_evaluator
def evaluate_latency(run: Run, example: Optional[Example] = None) -> EvaluationResult:
    """
    Evaluates Latency.
    Analyzes end-to-end time and step-by-step latency based on run execution times.
    """
    if not run.start_time or not run.end_time:
        return EvaluationResult(key="latency", score=0, comment="Execution times not found.")

    # Calculate end-to-end latency in seconds
    end_to_end_latency_ms = (run.end_time - run.start_time).total_seconds() * 1000
    
    # Ideally, we'd also check child runs for step-by-step latency
    step_latencies = []
    if run.child_runs:
        for child in run.child_runs:
            if child.start_time and child.end_time:
                step_latencies.append((child.name, (child.end_time - child.start_time).total_seconds() * 1000))

    # Example threshold: 5000ms is a 1.0, 15000ms is a 0.0
    # Custom formula can balance the trade-off with accuracy (calculated alongside other metrics)
    max_threshold_ms = 15000
    ideal_threshold_ms = 5000

    if end_to_end_latency_ms <= ideal_threshold_ms:
        score = 1.0
    elif end_to_end_latency_ms >= max_threshold_ms:
        score = 0.0
    else:
        score = 1.0 - ((end_to_end_latency_ms - ideal_threshold_ms) / (max_threshold_ms - ideal_threshold_ms))

    comment = f"End-to-end Latency: {end_to_end_latency_ms:.2f}ms. "
    if step_latencies:
        comment += "Step-by-step latency found."

    return EvaluationResult(
        key="latency",
        score=score,
        comment=comment
    )

# =====================================================================
# Running the evaluators
# =====================================================================
def get_all_evaluators():
    """
    Returns a list of all evaluators to be passed to evaluate() routine.
    """
    return [
        evaluate_task_success,
        evaluate_coherence,
        evaluate_correctness,
        evaluate_coverage,
        evaluate_latency
    ]

# Example usage for reference:
# from langsmith.evaluation import evaluate
# evaluate(
#     "<your-target-function-or-chain>",
#     data="<dataset-name>",
#     evaluators=get_all_evaluators(),
#     experiment_prefix="full-agent-eval"
# )
