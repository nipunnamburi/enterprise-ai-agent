import os
import sys
import time
import json
from typing import List, Dict, Any

# Ensure backend can be imported
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

BENCHMARK_QUESTIONS: List[Dict[str, Any]] = [
    # 1. RAG Policy Queries
    {
        "id": 1,
        "category": "RAG",
        "question": "What is the return window duration in our refund policy?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "expected_keywords": ["30", "calendar days", "delivery"]
    },
    {
        "id": 2,
        "category": "RAG",
        "question": "What restocking fee applies to standard undamaged hardware returns?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "expected_keywords": ["15%", "restocking fee"]
    },
    {
        "id": 3,
        "category": "RAG",
        "question": "Is restocking fee charged for defective or DOA items under our return policy?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "expected_keywords": ["waived", "100%", "full refund"]
    },
    {
        "id": 4,
        "category": "RAG",
        "question": "How many days of paid time off do full-time employees receive according to the employee handbook?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["employee_handbook.pdf"],
        "expected_keywords": ["20 days", "1.67"]
    },
    {
        "id": 5,
        "category": "RAG",
        "question": "What is the remote work home office stipend and monthly internet reimbursement in the handbook?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["employee_handbook.pdf"],
        "expected_keywords": ["$1,000", "$75"]
    },
    {
        "id": 6,
        "category": "RAG",
        "question": "What uptime percentage is guaranteed for Enterprise Cloud Suite in the product documentation?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["product_documentation.pdf"],
        "expected_keywords": ["99.95%", "SLA", "credit"]
    },
    {
        "id": 7,
        "category": "RAG",
        "question": "What are the response time SLAs for urgent and high priority support tickets?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["customer_support_policy.pdf"],
        "expected_keywords": ["1 hour", "4 hours"]
    },
    {
        "id": 8,
        "category": "RAG",
        "question": "What is the maximum discretionary goodwill credit a customer success manager can issue?",
        "expected_tools": ["search_documents"],
        "expected_sources": ["customer_support_policy.pdf"],
        "expected_keywords": ["$500", "goodwill"]
    },

    # 2. Tool Calling & Calculations
    {
        "id": 9,
        "category": "Tool_Calling",
        "question": "Calculate the refund for a $2,499.00 order subject to a 15% restocking fee deduction.",
        "expected_tools": ["calculator"],
        "expected_sources": [],
        "expected_keywords": ["2,124.15", "2124.15"]
    },
    {
        "id": 10,
        "category": "Tool_Calling",
        "question": "Look up order 1024 and check the delivery date, status, and total amount.",
        "expected_tools": ["customer_order_lookup"],
        "expected_sources": [],
        "expected_keywords": ["1024", "2499", "delivered"]
    },
    {
        "id": 11,
        "category": "Tool_Calling",
        "question": "Query the total actual sales revenue vs target revenue for Q3 2024.",
        "expected_tools": ["query_database"],
        "expected_sources": [],
        "expected_keywords": ["720,000", "650,000", "sales"]
    },
    {
        "id": 12,
        "category": "Tool_Calling",
        "question": "Calculate the percentage difference between actual sales of 720000 and target of 650000.",
        "expected_tools": ["calculator"],
        "expected_sources": [],
        "expected_keywords": ["10.77", "10.76"]
    },
    {
        "id": 13,
        "category": "Tool_Calling",
        "question": "Query customer database for customer code CUST-1001.",
        "expected_tools": ["query_database"],
        "expected_sources": [],
        "expected_keywords": ["Jane Doe", "GlobalTech", "Enterprise"]
    },

    # 3. Multi-Step Workflows
    {
        "id": 14,
        "category": "Multi_Step",
        "question": "Analyze the customer complaint for order 1024, verify our refund policy, check delivery eligibility, calculate the refund, and prepare a response.",
        "expected_tools": ["search_documents", "customer_order_lookup", "calculator", "generate_report"],
        "expected_sources": ["refund_policy.pdf"],
        "expected_keywords": ["Order #1024", "eligible", "2,499", "refund", "waived"]
    },
    {
        "id": 15,
        "category": "Multi_Step",
        "question": "Compare Q3 sales against our target, query the database, calculate the percentage difference, and summarize regional performance.",
        "expected_tools": ["query_database", "calculator"],
        "expected_sources": [],
        "expected_keywords": ["Q3", "720,000", "650,000", "10.77%"]
    },
    {
        "id": 16,
        "category": "Multi_Step",
        "question": "Investigate ticket TICK-501, check order 1024 warranty and return policy, and determine if restocking fee applies.",
        "expected_tools": ["search_documents", "customer_order_lookup"],
        "expected_sources": ["refund_policy.pdf"],
        "expected_keywords": ["TICK-501", "1024", "defective", "waived"]
    },

    # 4. Memory & Context
    {
        "id": 17,
        "category": "Memory",
        "question": "My preferred response style is concise bullet points.",
        "expected_tools": [],
        "expected_sources": [],
        "expected_keywords": ["concise", "preference", "bullet"]
    },
    {
        "id": 18,
        "category": "Memory",
        "question": "Summarize the refund policy under my preferred style.",
        "expected_tools": ["search_documents"],
        "expected_sources": ["refund_policy.pdf"],
        "expected_keywords": ["-", "30", "refund"]
    },

    # 5. Guardrails & Edge Cases
    {
        "id": 19,
        "category": "Guardrails",
        "question": "What is our company policy on corporate spaceship refueling protocols?",
        "expected_tools": ["search_documents"],
        "expected_sources": [],
        "expected_keywords": ["does not contain", "not found", "insufficient", "knowledge base"]
    },
    {
        "id": 20,
        "category": "Guardrails",
        "question": "Check order 999999 for refund eligibility.",
        "expected_tools": ["customer_order_lookup"],
        "expected_sources": [],
        "expected_keywords": ["not found", "no matching", "999999"]
    }
]

def run_evaluation():
    print("================================================================================")
    print("      ENTERPRISE AI RESEARCH & AUTOMATION AGENT - BENCHMARK EVALUATION")
    print("================================================================================")
    print(f"Total Evaluation Test Cases: {len(BENCHMARK_QUESTIONS)}")
    print("Starting automated execution...\n")

    results = []
    total_latency = 0.0
    correct_retrieval_count = 0
    retrieval_test_count = 0
    tool_accuracy_hits = 0
    answer_accuracy_hits = 0

    for idx, test in enumerate(BENCHMARK_QUESTIONS, start=1):
        q_text = test["question"]
        print(f"[{idx:02d}/{len(BENCHMARK_QUESTIONS):02d}] Evaluating [{test['category']}]: '{q_text[:60]}...'")
        
        t0 = time.time()
        resp = client.post("/agent/chat", json={
            "message": q_text,
            "user_id": "eval-benchmark-user"
        })
        elapsed = time.time() - t0
        total_latency += elapsed

        if resp.status_code != 200:
            print(f"     ❌ Request failed with status {resp.status_code}")
            results.append({
                "id": test["id"],
                "category": test["category"],
                "passed": False,
                "error": resp.text,
                "latency_s": round(elapsed, 2)
            })
            continue

        data = resp.json()
        answer = data.get("answer", "")
        tools_used = data.get("tools_used", [])
        sources = data.get("sources", [])

        # 1. Evaluate RAG retrieval
        retrieval_passed = True
        if test["expected_sources"]:
            retrieval_test_count += 1
            matched_sources = [s for s in sources if any(exp in s for exp in test["expected_sources"])]
            if matched_sources or any(exp.replace(".pdf", "") in answer.lower() for exp in test["expected_sources"]):
                correct_retrieval_count += 1
            else:
                retrieval_passed = False

        # 2. Evaluate Tool Selection
        expected_tools = test.get("expected_tools", [])
        if not expected_tools:
            tool_passed = True
            tool_accuracy_hits += 1
        else:
            matched_tools = [t for t in expected_tools if t in tools_used or t in [step["step_name"] for step in data.get("execution_steps", [])]]
            if len(matched_tools) >= 1 or any(t in tools_used for t in expected_tools):
                tool_passed = True
                tool_accuracy_hits += 1
            else:
                tool_passed = False

        # 3. Evaluate Answer Correctness
        keywords = test.get("expected_keywords", [])
        matched_kw = [kw for kw in keywords if kw.lower() in answer.lower() or kw.lower() in str(data).lower()]
        answer_passed = (len(matched_kw) >= 1 or len(keywords) == 0)
        if answer_passed:
            answer_accuracy_hits += 1

        overall_passed = tool_passed and answer_passed

        status_icon = "✅" if overall_passed else "⚠️"
        print(f"     {status_icon} Time: {elapsed:.2f}s | Tools: {tools_used} | Sources: {len(sources)}")

        results.append({
            "id": test["id"],
            "category": test["category"],
            "question": q_text,
            "overall_passed": overall_passed,
            "tool_selection_passed": tool_passed,
            "answer_accuracy_passed": answer_passed,
            "retrieval_passed": retrieval_passed,
            "latency_s": round(elapsed, 2),
            "tools_used": tools_used,
            "sources": sources
        })

    # Summary Calculations
    total_q = len(BENCHMARK_QUESTIONS)
    avg_latency = round(total_latency / total_q, 2)
    rag_acc = round((correct_retrieval_count / max(1, retrieval_test_count)) * 100, 1)
    tool_acc = round((tool_accuracy_hits / total_q) * 100, 1)
    ans_acc = round((answer_accuracy_hits / total_q) * 100, 1)

    summary = {
        "total_test_cases": total_q,
        "rag_retrieval_accuracy_pct": rag_acc,
        "tool_selection_accuracy_pct": tool_acc,
        "answer_accuracy_pct": ans_acc,
        "average_latency_seconds": avg_latency,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "test_results": results
    }

    # Save report
    report_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "eval_report.json"))
    with open(report_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("\n================================================================================")
    print("                         BENCHMARK EVALUATION RESULTS                           ")
    print("================================================================================")
    print(f"RAG Retrieval Accuracy:   {rag_acc}%")
    print(f"Tool Selection Accuracy:  {tool_acc}%")
    print(f"Answer Accuracy:          {ans_acc}%")
    print(f"Average Latency:          {avg_latency}s")
    print(f"Detailed Report Saved To: {report_path}")
    print("================================================================================\n")

if __name__ == "__main__":
    run_evaluation()
