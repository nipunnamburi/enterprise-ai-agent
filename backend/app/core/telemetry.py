from typing import Dict, Optional
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from openinference.instrumentation.langchain import LangChainInstrumentor
from app.core.config import settings


def _parse_otlp_headers(raw_headers: Optional[str]) -> Dict[str, str]:
    if not raw_headers:
        return {}
    headers: Dict[str, str] = {}
    for pair in raw_headers.split(","):
        if "=" in pair:
            k, v = pair.split("=", 1)
            headers[k.strip()] = v.strip()
    return headers


def configure_telemetry(app) -> None:
    """Configure OpenTelemetry TracerProvider, OTLP/Langfuse exporter, and instrumentors."""
    resource = Resource.create({"service.name": settings.OTEL_SERVICE_NAME})
    provider = TracerProvider(resource=resource)

    if settings.OTEL_EXPORTER_OTLP_ENDPOINT:
        exporter = OTLPSpanExporter(
            endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT,
            headers=_parse_otlp_headers(settings.OTEL_EXPORTER_OTLP_HEADERS),
        )
        provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)
    FastAPIInstrumentor.instrument_app(app, tracer_provider=provider)
    LangChainInstrumentor().instrument(tracer_provider=provider)


def set_span_context_attributes(
    tenant_id: str,
    user_id: str,
    thread_id: str,
) -> None:
    """Propagate multi-tenant and thread context onto the current active OpenTelemetry span."""
    span = trace.get_current_span()
    if span and span.is_recording():
        span.set_attribute("tenant.id", tenant_id)
        span.set_attribute("user.id", user_id)
        span.set_attribute("langgraph.thread_id", thread_id)
