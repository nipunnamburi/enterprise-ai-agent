import pytest
from app.agents.providers import OpenAIProvider, AnthropicProvider, OllamaLocalProvider
from app.agents.llm_client import LLMClient
from app.schemas.agent import AgentPlan


def test_provider_initialization():
    """Verify providers initialize gracefully even without active API keys."""
    openai_prov = OpenAIProvider(api_key=None)
    assert openai_prov.client is None

    anthropic_prov = AnthropicProvider(api_key=None)
    assert anthropic_prov.client is None

    ollama_prov = OllamaLocalProvider(base_url="http://localhost:11434")
    assert ollama_prov.base_url == "http://localhost:11434"


def test_model_neutral_runtime_switching():
    """Verify LLMClient can dynamically change providers at runtime (Devo pattern)."""
    client = LLMClient(provider="mock")
    assert client.provider_name == "mock"

    client.set_provider("anthropic", api_key="dummy_anthropic_key")
    assert client.provider_name == "anthropic"

    client.set_provider("ollama", base_url="http://127.0.0.1:11434")
    assert client.provider_name == "ollama"

    client.set_provider("openai", api_key="dummy_openai_key")
    assert client.provider_name == "openai"


def test_structured_fallback_with_mock_provider():
    """Verify structured schema generation succeeds even when no remote LLM keys are configured."""
    client = LLMClient(provider="mock")
    plan = client.generate_structured(
        schema=AgentPlan,
        system_prompt="Create execution plan",
        user_prompt="Analyze refund policy for order 1024 and calculate refund amount.",
    )
    assert isinstance(plan, AgentPlan)
    assert "search_documents" in plan.required_tools
    assert "calculator" in plan.required_tools
