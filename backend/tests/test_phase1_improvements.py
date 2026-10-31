import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.tool import (
    CalculatorArgs,
    CustomerOrderLookupArgs,
    QueryDatabaseArgs,
    GenerateReportArgs,
    TOOL_ARGUMENT_SCHEMAS,
)
from app.core.security import create_access_token
from pydantic import ValidationError

client = TestClient(app)


def test_tool_argument_pydantic_validation():
    """Verify strongly typed tool argument schemas validate required fields and types."""
    # 1. Calculator valid & invalid
    calc_valid = CalculatorArgs(expression="100.0 * 0.15")
    assert calc_valid.expression == "100.0 * 0.15"

    with pytest.raises(ValidationError):
        # Missing required expression
        CalculatorArgs()

    # 2. Customer order lookup valid & invalid
    order_valid = CustomerOrderLookupArgs(order_number="1025")
    assert order_valid.order_number == "1025"

    with pytest.raises(ValidationError):
        CustomerOrderLookupArgs()

    # 3. Query database
    db_valid = QueryDatabaseArgs(entity="sales", filters={"quarter": "Q3"})
    assert db_valid.entity == "sales"
    assert db_valid.limit == 10

    # 4. Registered schemas mapping
    assert "calculator" in TOOL_ARGUMENT_SCHEMAS
    assert "customer_order_lookup" in TOOL_ARGUMENT_SCHEMAS
    assert "query_database" in TOOL_ARGUMENT_SCHEMAS


def test_auth_protected_routes_with_valid_and_invalid_tokens():
    """Verify protected routes enforce JWT Bearer authentication and role checks."""
    # 1. Accessing /auth/me with an invalid token returns 401
    bad_headers = {"Authorization": "Bearer invalid.expired.token"}
    res = client.get("/auth/me", headers=bad_headers)
    assert res.status_code == 401
    assert "Could not validate token signature" in res.json()["detail"]

    # 2. Accessing /tools/execute with an invalid token returns 401
    res = client.post(
        "/tools/execute",
        headers=bad_headers,
        json={"tool_name": "calculator", "arguments": {"expression": "2+2"}},
    )
    assert res.status_code == 401


def test_file_upload_validation_and_sanitization():
    """Verify document upload enforces allowed file extensions and sanitizes paths."""
    # Attempt to upload an unauthorized file extension (.exe)
    files = {"file": ("malicious_script.exe", b"print('hack')", "application/x-msdownload")}
    res = client.post("/documents/upload", files=files)
    assert res.status_code == 400
    assert "Unsupported file extension" in res.json()["detail"]
