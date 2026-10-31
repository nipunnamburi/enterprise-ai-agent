import pytest
from app.agents.context_manager import RollingContextLedger, ContextManager
from app.api.agent import _JOBS_STORE, _run_background_agent_job
from app.core.security import create_access_token, hash_password
from app.core.database import SessionLocal
from app.models.user import User

@pytest.fixture(autouse=True)
def setup_job_test_users():
    db = SessionLocal()
    users_data = [
        ("job-admin", "jobadmin@enterprise.ai", "admin"),
        ("job-user-a", "jobuserA@enterprise.ai", "analyst"),
        ("job-user-b", "jobuserB@enterprise.ai", "analyst"),
    ]
    for uid, email, role in users_data:
        u = db.query(User).filter(User.id == uid).first()
        if not u:
            u = User(
                id=uid,
                email=email,
                hashed_password=hash_password("testpass123"),
                full_name=f"User {uid}",
                role=role,
                is_active=True
            )
            db.add(u)
    db.commit()
    db.close()

def test_rolling_context_ledger_capacity_and_formatting():
    ledger = RollingContextLedger(max_entries=3)
    ledger.record_entry("metric", "Q3 Revenue reached $1.2M", "Financial Audit")
    ledger.record_entry("compliance", "GDPR data retention policy set to 90 days", "Legal Docs")
    ledger.record_entry("architecture", "Postgres migration complete", "Infra Team")
    
    entries = ledger.get_entries()
    assert len(entries) == 3
    assert entries[0]["statement"] == "Q3 Revenue reached $1.2M"

    # Adding a 4th entry should evict the oldest
    ledger.record_entry("security", "Enforced MFA on admin portal", "SecOps")
    entries_after = ledger.get_entries()
    assert len(entries_after) == 3
    assert entries_after[0]["statement"] == "GDPR data retention policy set to 90 days"
    assert entries_after[-1]["statement"] == "Enforced MFA on admin portal"

    formatted = ledger.format_ledger_for_prompt()
    assert "[SECURITY] Enforced MFA on admin portal" in formatted
    assert "[Source: SecOps]" in formatted

def test_rolling_context_ledger_message_pruning():
    ledger = RollingContextLedger()
    long_messages = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"Message {i}"} for i in range(12)]
    pruned = ledger.prune_messages(long_messages, max_turns=4)
    assert len(pruned) == 4
    assert pruned[-1]["content"] == "Message 11"

def test_background_agent_job_worker_execution():
    job_id = "test-job-sync-1"
    _JOBS_STORE[job_id] = {
        "job_id": job_id,
        "user_id": "job-user-a",
        "objective": "Enterprise SaaS uptime benchmark analysis",
        "status": "queued",
        "created_at": "2026-11-01T00:00:00Z",
        "completed_at": None,
        "result": None,
        "error": None,
        "logs": []
    }

    _run_background_agent_job(job_id, "Enterprise SaaS uptime benchmark analysis", "job-user-a", depth=1)

    job = _JOBS_STORE[job_id]
    assert job["status"] == "completed"
    assert job["completed_at"] is not None
    assert job["result"] is not None
    assert "Enterprise Deep Research Dossier" in job["result"]["dossier"]
    assert job["result"]["claims_count"] > 0

def test_background_agent_job_api_lifecycle(client):
    token = create_access_token(subject="job-admin")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Submit Job
    res = client.post("/agent/jobs", json={
        "objective": "B2B hardware return logistics standards",
        "depth": 1,
        "priority": "high"
    }, headers=headers)
    assert res.status_code == 200
    data = res.json()
    job_id = data["job_id"]
    assert data["status"] in ["queued", "running"]

    # 2. Get Job Status
    status_res = client.get(f"/agent/jobs/{job_id}", headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["job_id"] == job_id

    # 3. List Jobs
    list_res = client.get("/agent/jobs", headers=headers)
    assert list_res.status_code == 200
    job_ids = [j["job_id"] for j in list_res.json()]
    assert job_id in job_ids

    # 4. Cancel Job
    cancel_res = client.post(f"/agent/jobs/{job_id}/cancel", headers=headers)
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"

def test_cross_user_job_isolation(client):
    user_token = create_access_token(subject="job-user-a")
    other_token = create_access_token(subject="job-user-b")

    # User A creates a job
    res = client.post("/agent/jobs", json={
        "objective": "Confidential financial review",
        "depth": 1
    }, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    job_id = res.json()["job_id"]

    # User B tries to view User A's job -> 403 Forbidden
    forbidden_res = client.get(f"/agent/jobs/{job_id}", headers={"Authorization": f"Bearer {other_token}"})
    assert forbidden_res.status_code == 403
