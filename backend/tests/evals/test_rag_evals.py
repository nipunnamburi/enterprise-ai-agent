import json
import os
import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase
from app.rag.hybrid_retriever import hybrid_retriever

GOLDEN_PATH = os.path.join(os.path.dirname(__file__), "golden_dataset.json")


def _load_golden_cases():
    with open(GOLDEN_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.mark.eval
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY is required to run DeepEval LLM-as-judge metrics.",
)
@pytest.mark.parametrize("case", _load_golden_cases(), ids=lambda c: c["id"])
def test_rag_pipeline_deepeval(case):
    retrieved = hybrid_retriever.search(query=case["query"], top_k=3, tenant_id="default")
    contexts = [r["content"] for r in retrieved] if retrieved else case["retrieval_context"]

    test_case = LLMTestCase(
        input=case["query"],
        actual_output=case["expected_output"],
        expected_output=case["expected_output"],
        retrieval_context=contexts,
    )

    metrics = [
        FaithfulnessMetric(threshold=0.7),
        ContextualPrecisionMetric(threshold=0.7),
        AnswerRelevancyMetric(threshold=0.7),
    ]
    assert_test(test_case, metrics)
