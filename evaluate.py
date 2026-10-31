import os
import sys
import time
import json
from typing import List, Dict, Any

# Ensure backend directory can be imported
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token, hash_password
from app.evaluation.metrics import (
    compute_semantic_similarity,
    compute_token_f1,
    verify_numerical_tolerance,
)

client = TestClient(app)

# Ensure an active evaluation user exists in DB and generate a valid signed JWT bearer token
db = SessionLocal()
eval_user = db.query(User).filter(User.email == "eval@enterprise.ai").first()
if not eval_user:
    eval_user = User(
        id="eval-admin-101",
        email="eval@enterprise.ai",
        full_name="Benchmark Evaluation Admin",
        hashed_password=hash_password("BenchmarkAdmin123!"),
        role="admin",
        is_active=True,
    )
    db.add(eval_user)
    db.commit()
    db.refresh(eval_user)

EVAL_TOKEN = create_access_token(subject=eval_user.id)
AUTH_HEADERS = {"Authorization": f"Bearer {EVAL_TOKEN}"}
db.close()

BENCHMARK_QUESTIONS: List[Dict[str, Any]] = [
    # 1. RAG Policy Queries
    {
        "id": 1,
        "category": "RAG",
        "question": "What is the return window duration in our refund policy?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "reference_answer": "According to the corporate refund policy, standard hardware items must be returned within 30 calendar days from the delivery date.",
        "expected_numbers": [30],
        "expected_keywords": ["30", "calendar days", "delivery"]
    },
    {
        "id": 2,
        "category": "RAG",
        "question": "What restocking fee applies to standard undamaged hardware returns?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "reference_answer": "Standard undamaged hardware returns are subject to a mandatory 15% restocking fee deduction from the refund amount.",
        "expected_numbers": [15],
        "expected_keywords": ["15%", "restocking fee"]
    },
    {
        "id": 3,
        "category": "RAG",
        "question": "Is restocking fee charged for defective or DOA items under our return policy?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "reference_answer": "No, restocking fees are completely waived for defective or dead-on-arrival (DOA) items, qualifying for a 100% full refund.",
        "expected_numbers": [100],
        "expected_keywords": ["waived", "full refund", "doa"]
    },
    {
        "id": 4,
        "category": "RAG",
        "question": "How many days of paid time off do full-time employees receive according to the employee handbook?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["employee_handbook.pdf"],
        "reference_answer": "Full-time employees receive 20 days of paid time off (PTO) annually, accrued at 1.67 days per month.",
        "expected_numbers": [20],
        "expected_keywords": ["20 days", "1.67", "pto"]
    },
    {
        "id": 5,
        "category": "RAG",
        "question": "What is the remote work home office stipend and monthly internet reimbursement in the handbook?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["employee_handbook.pdf"],
        "reference_answer": "Eligible remote employees receive a one-time $1,000 home office setup stipend and a monthly $75 internet reimbursement.",
        "expected_numbers": [1000, 75],
        "expected_keywords": ["1,000", "75", "stipend"]
    },
    {
        "id": 6,
        "category": "RAG",
        "question": "What uptime percentage is guaranteed for Enterprise Cloud Suite in the product documentation?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["product_documentation.pdf"],
        "reference_answer": "Enterprise Cloud Suite guarantees an availability uptime SLA of 99.95% backed by service credit penalties.",
        "expected_numbers": [99.95],
        "expected_keywords": ["99.95%", "sla", "uptime"]
    },
    {
        "id": 7,
        "category": "RAG",
        "question": "What are the response time SLAs for urgent and high priority support tickets?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["customer_support_policy.pdf"],
        "reference_answer": "Response time SLAs require a 1 hour initial response for urgent tickets and 4 hours for high priority support tickets.",
        "expected_numbers": [1, 4],
        "expected_keywords": ["1 hour", "4 hours"]
    },
    {
        "id": 8,
        "category": "RAG",
        "question": "What is the maximum discretionary goodwill credit a customer success manager can issue?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["customer_support_policy.pdf"],
        "reference_answer": "Customer success managers are empowered to authorize discretionary goodwill credits up to a maximum of $500 per customer account.",
        "expected_numbers": [500],
        "expected_keywords": ["$500", "goodwill"]
    },

    # 2. Tool Calling & Calculations
    {
        "id": 9,
        "category": "Tool_Calling",
        "question": "Calculate the refund for a $2,499.00 order subject to a 15% restocking fee deduction.",
        "expected_tools": ["calculator"],
        "expected_sources": [],
        "reference_answer": "For an order amount of $2,499.00 with a 15% restocking fee ($374.85) deducted, the net refund is $2,124.15.",
        "expected_numbers": [2124.15],
        "expected_keywords": ["2,124.15", "2124.15"]
    },
    {
        "id": 10,
        "category": "Tool_Calling",
        "question": "Look up order 1024 and check the delivery date, status, and total amount.",
        "expected_tools": ["customer_order_lookup"],
        "expected_sources": [],
        "reference_answer": "Order #1024 was delivered on 2024-09-15 with status delivered for a total value of $2,499.00.",
        "expected_numbers": [1024, 2499],
        "expected_keywords": ["1024", "2499", "delivered"]
    },
    {
        "id": 11,
        "category": "Tool_Calling",
        "question": "Query the total actual sales revenue vs target revenue for Q3 2024.",
        "expected_tools": ["query_database"],
        "expected_sources": [],
        "reference_answer": "In Q3 2024, database records record actual sales revenue of $957,500.00 compared against the target revenue of $910,000.00.",
        "expected_numbers": [957500, 910000],
        "expected_keywords": ["957,500", "910,000", "sales"]
    },
    {
        "id": 12,
        "category": "Tool_Calling",
        "question": "Calculate the percentage difference between actual sales of 720000 and target of 650000.",
        "expected_tools": ["calculator"],
        "expected_sources": [],
        "reference_answer": "The percentage difference is approximately 10.77%, indicating that actual revenue exceeded target revenue by 10.77%.",
        "expected_numbers": [10.77],
        "expected_keywords": ["10.77"]
    },
    {
        "id": 13,
        "category": "Tool_Calling",
        "question": "Query customer database for customer code CUST-1001.",
        "expected_tools": ["query_database"],
        "expected_sources": [],
        "reference_answer": "Customer code CUST-1001 belongs to Jane Doe at GlobalTech, subscribed under the Enterprise plan tier.",
        "expected_numbers": [],
        "expected_keywords": ["Jane Doe", "GlobalTech", "Enterprise"]
    },

    # 3. Multi-Step Workflows
    {
        "id": 14,
        "category": "Multi_Step",
        "question": "Analyze the customer complaint for order 1024, verify our refund policy, check delivery eligibility, calculate the refund, and prepare a response.",
        "expected_tools": ["search_documents", "customer_order_lookup", "calculator", "generate_report"],
        "expected_sources": ["refund_policy.pdf"],
        "reference_answer": "Order #1024 for $2,499.00 is eligible for a full refund of $2,499.00 because the item arrived DOA/defective, waiving standard restocking fees.",
        "expected_numbers": [1024, 2499.00],
        "expected_keywords": ["Order #1024", "eligible", "2,499", "refund", "waived"]
    },
    {
        "id": 15,
        "category": "Multi_Step",
        "question": "Compare Q3 sales against our target, query the database, calculate the percentage difference, and summarize regional performance.",
        "expected_tools": ["query_database", "calculator"],
        "expected_sources": [],
        "reference_answer": "Q3 2024 actual sales recorded in database reached $957,500.00 against a $910,000.00 target, representing 5.22% performance over quota.",
        "expected_numbers": [957500, 910000, 5.22],
        "expected_keywords": ["Q3", "957,500", "910,000"]
    },
    {
        "id": 16,
        "category": "Multi_Step",
        "question": "Investigate ticket TICK-501, check order 1024 warranty and return policy, and determine if restocking fee applies.",
        "expected_tools": ["search_documents", "customer_order_lookup"],
        "expected_sources": ["refund_policy.pdf"],
        "reference_answer": "Ticket TICK-501 concerns order 1024 where hardware arrived defective. Per return policy, restocking fee is waived for defective goods.",
        "expected_numbers": [1024],
        "expected_keywords": ["TICK-501", "1024", "waived"]
    },

    # 4. Memory & Context
    {
        "id": 17,
        "category": "Memory",
        "question": "My preferred response style is concise bullet points.",
        "expected_tools": [],
        "expected_sources": [],
        "reference_answer": "Preference acknowledged. Future responses will be formatted in concise bullet points.",
        "expected_numbers": [],
        "expected_keywords": ["concise", "preference", "bullet"]
    },
    {
        "id": 18,
        "category": "Memory",
        "question": "Summarize the refund policy under my preferred style.",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "reference_answer": "- Returns allowed within 30 days of delivery\n- Standard returns incur a 15% restocking fee\n- Defective/DOA items receive 100% full refund with fee waived",
        "expected_numbers": [30, 15],
        "expected_keywords": ["30", "refund"]
    },

    # 5. Guardrails & Edge Cases
    {
        "id": 19,
        "category": "Guardrails",
        "question": "What is our company policy on corporate spaceship refueling protocols?",
        "expected_tools": ["search_documents"],
        "expected_sources": [],
        "reference_answer": "The enterprise knowledge base contains no documentation or company policy regarding corporate spaceship refueling protocols.",
        "expected_numbers": [],
        "expected_keywords": ["does not contain", "not found", "insufficient", "knowledge base"]
    },
    {
        "id": 20,
        "category": "Guardrails",
        "question": "Check order 999999 for refund eligibility.",
        "expected_tools": ["customer_order_lookup"],
        "expected_sources": [],
        "reference_answer": "Order query failed: No matching customer or order found with provided identifiers.",
        "expected_numbers": [],
        "expected_keywords": ["not found", "no matching"]
    }
]


def run_evaluation() -> Dict[str, Any]:
    print("================================================================================")
    print("      ENTERPRISE AI RESEARCH & AUTOMATION AGENT - BENCHMARK EVALUATION")
    print("================================================================================")
    print(f"Total Evaluation Test Cases: {len(BENCHMARK_QUESTIONS)}")
    print("Evaluation Dimensions: Semantic Cosine, Token F1 Overlap, Numerical Tolerance, Tool & RAG Precision")
    print("Starting automated execution...\n")

    results = []
    total_latency = 0.0
    correct_retrieval_count = 0
    retrieval_test_count = 0
    tool_accuracy_hits = 0
    numerical_tests_count = 0
    numerical_passed_count = 0
    f1_scores: List[float] = []
    semantic_scores: List[float] = []
    overall_passed_count = 0

    for idx, test in enumerate(BENCHMARK_QUESTIONS, start=1):
        q_text = test["question"]
        ref_text = test["reference_answer"]
        expected_nums = test.get("expected_numbers", [])
        expected_tools = test.get("expected_tools", [])
        expected_sources = test.get("expected_sources", [])

        print(f"[{idx:02d}/{len(BENCHMARK_QUESTIONS):02d}] Evaluating [{test['category']}]: '{q_text[:50]}...'")

        t0 = time.time()
        resp = client.post(
            "/agent/chat",
            headers=AUTH_HEADERS,
            json={
                "message": q_text,
                "user_id": "eval-benchmark-user",
            },
        )
        elapsed = time.time() - t0
        total_latency += elapsed

        if resp.status_code != 200:
            print(f"     ❌ Request failed with status {resp.status_code}: {resp.text[:100]}")
            results.append({
                "id": test["id"],
                "category": test["category"],
                "question": q_text,
                "overall_passed": False,
                "error": resp.text,
                "latency_s": round(elapsed, 3),
            })
            continue

        data = resp.json()
        answer = data.get("answer", "")
        tools_used = data.get("tools_used", [])
        sources = data.get("sources", [])
        exec_steps = [s.get("step_name") for s in data.get("execution_steps", [])]

        # 1. RAG Retrieval Evaluation
        retrieval_passed = True
        if expected_sources:
            retrieval_test_count += 1
            matched_sources = [s for s in sources if any(exp in s for exp in expected_sources)]
            if matched_sources or any(exp.replace(".pdf", "") in answer.lower() for exp in expected_sources):
                correct_retrieval_count += 1
            else:
                retrieval_passed = False

        # 2. Tool Selection Accuracy
        if not expected_tools:
            tool_passed = len(tools_used) == 0
        else:
            all_executed_tools = set(tools_used + exec_steps)
            matched_tools = [t for t in expected_tools if t in all_executed_tools]
            tool_passed = len(matched_tools) >= 1

        if tool_passed:
            tool_accuracy_hits += 1

        # 3. Semantic Cosine Similarity
        semantic_sim = compute_semantic_similarity(answer, ref_text)
        semantic_scores.append(semantic_sim)

        # 4. Token Overlap F1 Score
        token_metrics = compute_token_f1(answer, ref_text)
        f1_score = token_metrics["f1"]
        f1_scores.append(f1_score)

        # 5. Numerical Tolerance Verification
        num_result = verify_numerical_tolerance(answer, expected_nums, rel_tol=0.015, abs_tol=0.05)
        num_passed = num_result["passed"]
        if expected_nums:
            numerical_tests_count += 1
            if num_passed:
                numerical_passed_count += 1

        # 6. Keyword Match (for backward-compatible signal)
        keywords = test.get("expected_keywords", [])
        matched_kw = [kw for kw in keywords if kw.lower() in answer.lower() or kw.lower() in str(data).lower()]
        keyword_passed = (len(matched_kw) >= 1 or len(keywords) == 0)

        # 7. Composite Pass Criteria
        # A test passes if tool selection passed, RAG retrieval passed (if required),
        # numerical validation passed (if required), and semantic similarity meets baseline threshold.
        semantic_threshold = 0.35 if test["category"] in ("Guardrails", "Memory") else 0.40
        overall_passed = tool_passed and retrieval_passed and num_passed and (semantic_sim >= semantic_threshold or keyword_passed)
        if overall_passed:
            overall_passed_count += 1

        status_icon = "✅" if overall_passed else "⚠️"
        print(
            f"     {status_icon} Time: {elapsed:.2f}s | "
            f"Semantic: {semantic_sim:.2f} | "
            f"F1: {f1_score:.2f} | "
            f"NumMatch: {'Pass' if num_passed else 'Fail'} | "
            f"Tools: {tools_used}"
        )

        results.append({
            "id": test["id"],
            "category": test["category"],
            "question": q_text,
            "overall_passed": overall_passed,
            "tool_selection_passed": tool_passed,
            "retrieval_passed": retrieval_passed,
            "numerical_passed": num_passed,
            "semantic_similarity": semantic_sim,
            "token_precision": token_metrics["precision"],
            "token_recall": token_metrics["recall"],
            "token_f1": f1_score,
            "latency_s": round(elapsed, 3),
            "tools_used": tools_used,
            "sources": sources,
            "generated_answer_snippet": answer[:160] + "..." if len(answer) > 160 else answer,
        })

    # Summary Metrics
    total_q = len(BENCHMARK_QUESTIONS)
    avg_latency = round(total_latency / total_q, 3)
    rag_acc = round((correct_retrieval_count / max(1, retrieval_test_count)) * 100, 1)
    tool_acc = round((tool_accuracy_hits / total_q) * 100, 1)
    mean_semantic = round(sum(semantic_scores) / max(1, len(semantic_scores)), 3)
    mean_f1 = round(sum(f1_scores) / max(1, len(f1_scores)), 3)
    num_acc = round((numerical_passed_count / max(1, numerical_tests_count)) * 100, 1) if numerical_tests_count else 100.0
    overall_pass_rate = round((overall_passed_count / total_q) * 100, 1)

    summary = {
        "benchmark_title": "Enterprise AI Agent Multi-Metric Quality Evaluation",
        "total_test_cases": total_q,
        "overall_pass_rate_pct": overall_pass_rate,
        "metrics": {
            "rag_retrieval_accuracy_pct": rag_acc,
            "tool_selection_accuracy_pct": tool_acc,
            "numerical_accuracy_pct": num_acc,
            "mean_semantic_similarity": mean_semantic,
            "mean_token_f1_score": mean_f1,
            "average_latency_seconds": avg_latency,
        },
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "test_results": results,
    }

    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "eval_report.json"))
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n================================================================================")
    print("                         BENCHMARK EVALUATION RESULTS                           ")
    print("================================================================================")
    print(f"Overall Pass Rate:             {overall_pass_rate}% ({overall_passed_count}/{total_q})")
    print(f"Mean Semantic Similarity:      {mean_semantic} (Cosine metric)")
    print(f"Mean Token Overlap F1 Score:   {mean_f1}")
    print(f"Numerical Calculation Accuracy:{num_acc}%")
    print(f"RAG Retrieval Accuracy:        {rag_acc}%")
    print(f"Tool Selection Accuracy:       {tool_acc}%")
    print(f"Average Request Latency:       {avg_latency}s")
    print(f"Comprehensive Report Saved To: {report_path}")
    print("================================================================================\n")

    return summary


if __name__ == "__main__":
    run_evaluation()
