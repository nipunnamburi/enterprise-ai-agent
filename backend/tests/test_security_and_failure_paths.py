import pytest
import io
from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token, hash_password
from app.core.database import SessionLocal
from app.models.user import User
from app.models.conversation import Conversation, Message
from app.models.document import Document
from app.agents.graph import agent_graph

client = TestClient(app)


@pytest.fixture(scope="module")
def setup_test_users():
    """Ensure standard test users with different roles exist in test DB."""
    db = SessionLocal()
    # User 1: Analyst
    u1 = db.query(User).filter(User.id == "test-user-analyst").first()
    if not u1:
        u1 = User(
            id="test-user-analyst",
            email="analyst-test@enterprise.ai",
            hashed_password=hash_password("analystpass"),
            full_name="Test Analyst",
            role="analyst",
            is_active=True,
        )
        db.add(u1)

    # User 2: Viewer
    u2 = db.query(User).filter(User.id == "test-user-viewer").first()
    if not u2:
        u2 = User(
            id="test-user-viewer",
            email="viewer-test@enterprise.ai",
            hashed_password=hash_password("viewerpass"),
            full_name="Test Viewer",
            role="viewer",
            is_active=True,
        )
        db.add(u2)

    # User 3: Inactive User
    u3 = db.query(User).filter(User.id == "test-user-inactive").first()
    if not u3:
        u3 = User(
            id="test-user-inactive",
            email="inactive-test@enterprise.ai",
            hashed_password=hash_password("inactivepass"),
            full_name="Test Inactive",
            role="analyst",
            is_active=False,
        )
        db.add(u3)

    db.commit()
    db.close()
    return {"analyst": "test-user-analyst", "viewer": "test-user-viewer", "inactive": "test-user-inactive"}


def auth_header(user_id: str):
    token = create_access_token(subject=user_id)
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# 1. Missing and Invalid Authentication Tests
# ---------------------------------------------------------------------------

def test_missing_authentication_rejected():
    """Endpoints requiring authentication must return 401 when no token is supplied."""
    # /tools
    res = client.get("/tools")
    assert res.status_code == 401
    assert "Authentication credentials were not provided" in res.json()["detail"]

    # /conversations
    res = client.get("/conversations")
    assert res.status_code == 401

    # /documents
    res = client.get("/documents")
    assert res.status_code == 401

    # /agent/chat
    res = client.post("/agent/chat", json={"message": "hello"})
    assert res.status_code == 401


def test_inactive_user_rejected(setup_test_users):
    """Deactivated user accounts must receive 403 Forbidden even with valid token."""
    inactive_header = auth_header(setup_test_users["inactive"])
    res = client.get("/tools", headers=inactive_header)
    assert res.status_code == 403
    assert "User account is deactivated" in res.json()["detail"]


# ---------------------------------------------------------------------------
# 2. Role Permissions Tests
# ---------------------------------------------------------------------------

def test_role_permissions_enforcement(setup_test_users):
    """Verify viewers cannot execute tools or upload documents, but analysts can."""
    viewer_header = auth_header(setup_test_users["viewer"])
    analyst_header = auth_header(setup_test_users["analyst"])

    # 1. Direct tool execution requires admin or analyst
    res_viewer = client.post(
        "/tools/execute",
        headers=viewer_header,
        json={"tool_name": "calculator", "arguments": {"expression": "1+1"}},
    )
    assert res_viewer.status_code == 403
    assert "Operation requires one of the following roles" in res_viewer.json()["detail"]

    # Analyst can execute
    res_analyst = client.post(
        "/tools/execute",
        headers=analyst_header,
        json={"tool_name": "calculator", "arguments": {"expression": "1+1"}},
    )
    assert res_analyst.status_code == 200

    # 2. Document upload requires admin or analyst
    files = {"file": ("test.txt", b"allowed document content", "text/plain")}
    res_upload_viewer = client.post("/documents/upload", files=files, headers=viewer_header)
    assert res_upload_viewer.status_code == 403


# ---------------------------------------------------------------------------
# 3. Document-Upload Size Limits Tests
# ---------------------------------------------------------------------------

def test_document_upload_size_limit(setup_test_users):
    """Uploading a document exceeding MAX_FILE_SIZE (15 MB) should return 413."""
    analyst_header = auth_header(setup_test_users["analyst"])
    
    # 16 MB dummy content
    oversized_content = b"0" * (16 * 1024 * 1024)
    files = {"file": ("oversized_file.txt", io.BytesIO(oversized_content), "text/plain")}
    res = client.post("/documents/upload", files=files, headers=analyst_header)
    assert res.status_code == 413
    assert "exceeds maximum allowed size" in res.json()["detail"]


# ---------------------------------------------------------------------------
# 4. Cross-User Data Access Isolation Tests
# ---------------------------------------------------------------------------

def test_cross_user_conversation_isolation(setup_test_users):
    """Ensure User A cannot view, retrieve, or delete User B's conversations."""
    analyst_header = auth_header(setup_test_users["analyst"])
    viewer_header = auth_header(setup_test_users["viewer"])

    db = SessionLocal()
    # Create conversation belonging to analyst
    conv_analyst = Conversation(
        user_id=setup_test_users["analyst"],
        title="Analyst Secret Conversation",
    )
    db.add(conv_analyst)
    db.commit()
    db.refresh(conv_analyst)
    analyst_conv_id = conv_analyst.id
    db.close()

    # Viewer lists conversations -> should not see analyst's conversation
    res_viewer_list = client.get("/conversations", headers=viewer_header)
    assert res_viewer_list.status_code == 200
    viewer_conv_ids = [c["id"] for c in res_viewer_list.json()]
    assert analyst_conv_id not in viewer_conv_ids

    # Viewer attempts direct GET on analyst conversation -> 404
    res_viewer_get = client.get(f"/conversations/{analyst_conv_id}", headers=viewer_header)
    assert res_viewer_get.status_code == 404

    # Viewer attempts DELETE on analyst conversation -> 404
    res_viewer_delete = client.delete(f"/conversations/{analyst_conv_id}", headers=viewer_header)
    assert res_viewer_delete.status_code == 404

    # Analyst can retrieve and delete their own conversation
    res_analyst_get = client.get(f"/conversations/{analyst_conv_id}", headers=analyst_header)
    assert res_analyst_get.status_code == 200

    res_analyst_delete = client.delete(f"/conversations/{analyst_conv_id}", headers=analyst_header)
    assert res_analyst_delete.status_code == 200


def test_cross_user_memory_isolation(setup_test_users):
    """Ensure User A cannot retrieve or delete User B's agent memory."""
    analyst_header = auth_header(setup_test_users["analyst"])
    viewer_header = auth_header(setup_test_users["viewer"])

    # Analyst creates a private memory
    res_create = client.post(
        "/memory",
        headers=analyst_header,
        json={"category": "preference", "content": "Analyst personal note", "importance": 0.8},
    )
    assert res_create.status_code == 200
    memory_id = res_create.json()["id"]

    # Viewer listing memories must not include analyst's memory
    res_viewer_list = client.get("/memory", headers=viewer_header)
    assert res_viewer_list.status_code == 200
    viewer_mem_ids = [m["id"] for m in res_viewer_list.json()]
    assert memory_id not in viewer_mem_ids

    # Viewer cannot delete analyst's memory
    res_delete = client.delete(f"/memory/{memory_id}", headers=viewer_header)
    assert res_delete.status_code == 404


# ---------------------------------------------------------------------------
# 5. Agent Failure Paths & Graceful Recovery Tests
# ---------------------------------------------------------------------------

def test_agent_handles_unknown_tool_gracefully():
    """Agent tool executor handles unregistered tool calls without crashing."""
    from app.agents.nodes import execute_tools_node

    broken_state = {
        "pending_tool_calls": [
            {"tool_name": "non_existent_tool_xyz", "arguments": {"foo": "bar"}}
        ],
        "tool_results": [],
        "tools_used": [],
        "execution_trace": [],
    }

    result = execute_tools_node(broken_state)
    assert len(result["tool_results"]) == 1
    assert result["tool_results"][0]["result"]["success"] is False
    assert "not registered" in result["tool_results"][0]["result"]["error"]


def test_agent_handles_calculator_division_by_zero():
    """Calculator tool handles invalid expressions like ZeroDivisionError safely."""
    from app.tools.registry import tool_registry

    res = tool_registry.execute_tool("calculator", {"expression": "10 / 0"})
    assert res["success"] is False
    assert "division by zero" in res["error"].lower()


def test_agent_handles_malformed_database_query():
    """Database query tool gracefully rejects unknown entities."""
    from app.tools.registry import tool_registry

    res = tool_registry.execute_tool("query_database", {"entity": "non_existent_table"})
    assert res["success"] is False
    assert "Invalid entity" in res["error"]
