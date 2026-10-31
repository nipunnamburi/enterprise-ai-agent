import os
import json
import pytest
from app.evaluation.metrics import (
    cosine_similarity,
    compute_semantic_similarity,
    tokenize_text,
    compute_token_f1,
    extract_numbers,
    verify_numerical_tolerance,
)


def test_cosine_similarity_edge_cases_and_accuracy():
    """Verify vector cosine similarity handles identical, orthogonal, and edge case vectors."""
    # 1. Identical vectors -> 1.0
    v1 = [1.0, 2.0, 3.0]
    assert cosine_similarity(v1, v1) == 1.0

    # 2. Orthogonal vectors -> 0.0
    v_ortho_a = [1.0, 0.0]
    v_ortho_b = [0.0, 1.0]
    assert cosine_similarity(v_ortho_a, v_ortho_b) == 0.0

    # 3. Opposing vectors -> -1.0
    v_opp_a = [1.0, -1.0]
    v_opp_b = [-1.0, 1.0]
    assert cosine_similarity(v_opp_a, v_opp_b) == -1.0

    # 4. Zero / Empty / Mismatched dimension vectors
    assert cosine_similarity([], [1.0, 2.0]) == 0.0
    assert cosine_similarity([0.0, 0.0], [1.0, 1.0]) == 0.0
    assert cosine_similarity([1.0], [1.0, 2.0]) == 0.0


def test_token_f1_score_calculation():
    """Verify Token Precision, Recall, and harmonic F1 score computation."""
    cand = "The refund window is 30 calendar days from delivery."
    ref = "Standard hardware returns are accepted within 30 calendar days."

    metrics = compute_token_f1(cand, ref)
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1" in metrics

    # Common non-stopword tokens: ['refund', 'window', '30', 'calendar', 'days', 'delivery'] vs ['standard', 'hardware', 'returns', 'accepted', '30', 'calendar', 'days']
    # Overlap: '30', 'calendar', 'days' -> 3 tokens
    assert metrics["precision"] > 0.0
    assert metrics["recall"] > 0.0
    assert metrics["f1"] > 0.0

    # Identical text produces F1 of 1.0
    perfect = compute_token_f1("exact matching response", "exact matching response")
    assert perfect["f1"] == 1.0

    # Disjoint text produces F1 of 0.0
    disjoint = compute_token_f1("apple banana cherry", "dog elephant giraffe")
    assert disjoint["f1"] == 0.0


def test_numerical_tolerance_verification():
    """Verify extraction and tolerance verification for integer, decimal, and currency figures."""
    text = "The calculated order refund for order #1024 is $2,124.15 USD after a 15% fee."

    # 1. Extraction
    extracted = extract_numbers(text)
    assert 1024.0 in extracted
    assert 2124.15 in extracted
    assert 15.0 in extracted

    # 2. Strict exact match
    res = verify_numerical_tolerance(text, [2124.15, 1024.0])
    assert res["passed"] is True
    assert len(res["matched_numbers"]) == 2
    assert len(res["missing_numbers"]) == 0

    # 3. Approximate tolerance (e.g. 2124.18 within ±0.05 absolute tolerance)
    approx_text = "Net amount: 2124.18"
    approx_res = verify_numerical_tolerance(approx_text, [2124.15], abs_tol=0.05)
    assert approx_res["passed"] is True

    # 4. Missing required number fails
    missing_res = verify_numerical_tolerance(text, [9999.00])
    assert missing_res["passed"] is False
    assert 9999.0 in missing_res["missing_numbers"]


def test_benchmark_report_structure_and_schema():
    """Verify eval_report.json file exists and adheres to benchmark summary schema."""
    report_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../eval_report.json")
    )
    assert os.path.exists(report_path), f"eval_report.json not found at {report_path}"

    with open(report_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "benchmark_title" in data
    assert "total_test_cases" in data
    assert data["total_test_cases"] == 20
    assert "overall_pass_rate_pct" in data
    assert "metrics" in data
    metrics = data["metrics"]
    assert "rag_retrieval_accuracy_pct" in metrics
    assert "tool_selection_accuracy_pct" in metrics
    assert "mean_semantic_similarity" in metrics
    assert "mean_token_f1_score" in metrics
    assert "average_latency_seconds" in metrics

    assert "test_results" in data
    assert len(data["test_results"]) == 20
    first_test = data["test_results"][0]
    assert "id" in first_test
    assert "category" in first_test
    assert "overall_passed" in first_test
    assert "semantic_similarity" in first_test
    assert "token_f1" in first_test
