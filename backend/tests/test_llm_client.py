from unittest.mock import MagicMock
import pytest
from app.agents.llm_client import LLMClient
from app.schemas.agent import AgentPlan, ToolDecision


def test_llm_client_initialization_without_key():
    """Verify LLMClient initializes cleanly without an OpenAI API key."""
    client = LLMClient()
    # In offline test mode without key, client should be None
    if not client.api_key:
        assert client.client is None


def test_llm_client_structured_fallback():
    """Verify deterministic structured output fallback generates valid Pydantic models."""
    client = LLMClient()
    client.client = None  # Force fallback path

    plan = client.generate_structured(
        schema=AgentPlan,
        system_prompt="Generate plan",
        user_prompt="Analyze refund policy and calculate restocking deduction for order 1024."
    )
    assert isinstance(plan, AgentPlan)
    assert "search_documents" in plan.required_tools
    assert "customer_order_lookup" in plan.required_tools
    assert "calculator" in plan.required_tools

    tool_decision = client.generate_structured(
        schema=ToolDecision,
        system_prompt="Tool name is 'customer_order_lookup'",
        user_prompt="Look up customer details for order 1024"
    )
    assert isinstance(tool_decision, ToolDecision)
    assert tool_decision.tool_name == "customer_order_lookup"


def test_llm_client_openai_parse_invocation():
    """Verify LLMClient delegates to OpenAI beta parse when client is configured."""
    client = LLMClient()
    mock_openai = MagicMock()
    mock_parsed_response = MagicMock()
    expected_plan = AgentPlan(
        objective="Analyze refund policy",
        steps=["Retrieve policy document", "Calculate total"],
        required_tools=["search_documents", "calculator"],
        reasoning="Policy verification requires document lookup and arithmetic computation."
    )
    mock_parsed_response.choices = [
        MagicMock(message=MagicMock(parsed=expected_plan))
    ]
    mock_openai.beta.chat.completions.parse.return_value = mock_parsed_response
    client.client = mock_openai

    result = client.generate_structured(
        schema=AgentPlan,
        system_prompt="System instructions",
        user_prompt="Audit refund policy",
        model="gpt-4o"
    )

    assert result == expected_plan
    mock_openai.beta.chat.completions.parse.assert_called_once()
