import abc
import json
import os
from typing import Type, TypeVar, Optional, Dict, Any, List
from pydantic import BaseModel
from app.core.config import settings

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(abc.ABC):
    """Abstract interface for model-neutral LLM providers (Devo-inspired)."""

    @abc.abstractmethod
    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Generate plain textual response."""
        pass

    @abc.abstractmethod
    def generate_structured(
        self,
        schema: Type[T],
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
    ) -> Optional[T]:
        """Generate structured response matching Pydantic schema."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider implementation."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = base_url
        self.client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except Exception as e:
                print(f"[OpenAIProvider] Initialization error: {e}")
                self.client = None

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        if not self.client:
            raise RuntimeError("OpenAI client not initialized or missing OPENAI_API_KEY.")
        model_name = model or settings.FAST_LLM_MODEL
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        resp = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""

    def generate_structured(
        self,
        schema: Type[T],
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
    ) -> Optional[T]:
        if not self.client:
            return None
        model_name = model or settings.FAST_LLM_MODEL
        try:
            response = self.client.beta.chat.completions.parse(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=schema,
                temperature=0.1,
            )
            return response.choices[0].message.parsed
        except Exception as e:
            print(f"[OpenAIProvider] Structured call failed: {e}")
            return None


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider implementation."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.client = None
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.Anthropic(api_key=self.api_key)
            except Exception as e:
                print(f"[AnthropicProvider] Initialization error: {e}")
                self.client = None

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        if not self.client:
            raise RuntimeError("Anthropic client not initialized or missing ANTHROPIC_API_KEY.")
        model_name = model or "claude-3-5-sonnet-20241022"
        resp = self.client.messages.create(
            model=model_name,
            max_tokens=2048,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
        )
        return resp.content[0].text if resp.content else ""

    def generate_structured(
        self,
        schema: Type[T],
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
    ) -> Optional[T]:
        if not self.client:
            return None
        try:
            # Instruct Claude to produce JSON strictly conforming to schema
            json_system = f"{system_prompt}\nReturn JSON strictly adhering to schema: {json.dumps(schema.model_json_schema())}"
            raw_text = self.generate_text(user_prompt, system_prompt=json_system, model=model)
            # Extract JSON block
            if "```json" in raw_text:
                raw_text = raw_text.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_text:
                raw_text = raw_text.split("```")[1].split("```")[0].strip()
            data = json.loads(raw_text)
            return schema.model_validate(data)
        except Exception as e:
            print(f"[AnthropicProvider] Structured generation failed: {e}")
            return None


class OllamaLocalProvider(BaseLLMProvider):
    """Local Ollama / vLLM OpenAI-compatible endpoint provider."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.openai_provider = OpenAIProvider(api_key="ollama", base_url=f"{self.base_url}/v1")

    def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        return self.openai_provider.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            model=model or "llama3.2:latest",
            temperature=temperature,
        )

    def generate_structured(
        self,
        schema: Type[T],
        system_prompt: str,
        user_prompt: str,
        model: Optional[str] = None,
    ) -> Optional[T]:
        return self.openai_provider.generate_structured(
            schema=schema,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            model=model or "llama3.2:latest",
        )
