import re
import math
from typing import List, Dict, Any, Optional
from app.rag.vector_store import EmbeddingService

_STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "it", "its", "that", "this", "these", "those",
    "from", "as", "our", "we", "you", "your", "they", "their", "will", "would"
}


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two numeric vectors."""
    if not vec_a or not vec_b or len(vec_a) != len(vec_b):
        return 0.0

    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    cos = dot / (norm_a * norm_b)
    # Clip numerical precision artifacts to [-1.0, 1.0]
    return max(-1.0, min(1.0, round(cos, 4)))


def compute_semantic_similarity(
    candidate_text: str,
    reference_text: str,
    embedding_service: Optional[EmbeddingService] = None,
) -> float:
    """
    Calculate semantic vector similarity between candidate output and reference text.
    Uses OpenAI embeddings when available or the deterministic fallback projection.
    Returns normalized similarity in range [0.0, 1.0].
    """
    if not candidate_text or not reference_text:
        return 0.0

    service = embedding_service or EmbeddingService()
    embeddings = service.get_embeddings([candidate_text, reference_text])
    if len(embeddings) != 2:
        return 0.0

    raw_cos = cosine_similarity(embeddings[0], embeddings[1])
    # Rescale negative similarity to 0.0 for benchmark metric reporting
    return max(0.0, round(raw_cos, 4))


def tokenize_text(text: str, remove_stopwords: bool = True) -> List[str]:
    """Tokenize text into lowercase alphanumeric tokens, optionally stripping stopwords."""
    if not text:
        return []
    raw_tokens = re.findall(r"\b[a-zA-Z0-9_\-\.]+\b", text.lower())
    clean_tokens = [t.strip(".") for t in raw_tokens if t.strip(".")]
    if remove_stopwords:
        clean_tokens = [t for t in clean_tokens if t not in _STOPWORDS]
    return clean_tokens


def compute_token_f1(candidate_text: str, reference_text: str) -> Dict[str, float]:
    """
    Compute Token Precision, Recall, and harmonic F1 score between candidate and reference.
    Standard QA metric for answer overlap.
    """
    cand_tokens = tokenize_text(candidate_text)
    ref_tokens = tokenize_text(reference_text)

    if not cand_tokens or not ref_tokens:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}

    cand_counts: Dict[str, int] = {}
    for t in cand_tokens:
        cand_counts[t] = cand_counts.get(t, 0) + 1

    ref_counts: Dict[str, int] = {}
    for t in ref_tokens:
        ref_counts[t] = ref_counts.get(t, 0) + 1

    # Overlap count
    overlap = sum(min(cand_counts[t], ref_counts.get(t, 0)) for t in cand_counts)

    precision = overlap / len(cand_tokens) if cand_tokens else 0.0
    recall = overlap / len(ref_tokens) if ref_tokens else 0.0

    if precision + recall > 0:
        f1 = (2.0 * precision * recall) / (precision + recall)
    else:
        f1 = 0.0

    return {
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def extract_numbers(text: str) -> List[float]:
    """
    Extract all numeric values (integers, decimals, percentages, currency) from text.
    Handles thousand separators (e.g., 2,499.00 -> 2499.00).
    """
    if not text:
        return []
    # Pattern to match numbers with optional commas and decimal points
    matches = re.findall(r"[-+]?\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b|[-+]?\b\d+(?:\.\d+)?\b", text)
    numbers = []
    for m in matches:
        clean_m = m.replace(",", "")
        try:
            numbers.append(float(clean_m))
        except ValueError:
            continue
    return numbers


def verify_numerical_tolerance(
    candidate_text: str,
    expected_numbers: List[float],
    rel_tol: float = 0.01,
    abs_tol: float = 0.05,
) -> Dict[str, Any]:
    """
    Verify that candidate text contains the expected numbers within acceptable tolerance.
    Supports both relative (e.g. 1% difference) and absolute (e.g. $0.05 cent rounding) tolerances.
    """
    if not expected_numbers:
        return {
            "passed": True,
            "matched_numbers": [],
            "missing_numbers": [],
            "extracted_numbers": extract_numbers(candidate_text),
        }

    extracted = extract_numbers(candidate_text)
    matched: List[float] = []
    missing: List[float] = []

    for target in expected_numbers:
        target_matched = False
        for cand in extracted:
            # Check absolute tolerance
            if abs(cand - target) <= abs_tol:
                target_matched = True
                break
            # Check relative tolerance
            if target != 0 and abs(cand - target) / abs(target) <= rel_tol:
                target_matched = True
                break
        if target_matched:
            matched.append(target)
        else:
            missing.append(target)

    return {
        "passed": len(missing) == 0,
        "matched_numbers": matched,
        "missing_numbers": missing,
        "extracted_numbers": extracted,
    }
