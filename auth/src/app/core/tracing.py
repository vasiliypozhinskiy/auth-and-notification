from app.core.config import TracingConfig

from flask import Blueprint, request         
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider   
from opentelemetry.sdk.resources import SERVICE_NAME, Resource     
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased

tracing_blueprint = Blueprint("tracing", __name__)
trace_settings = TracingConfig()


def configure_tracer() -> None:
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "auth"}),
            sampler=TraceIdRatioBased(trace_settings.sampling_rate)
        )
    )
    trace.get_tracer_provider().add_span_processor(
        BatchSpanProcessor(
            JaegerExporter(
                agent_host_name=trace_settings.host,
                agent_port=trace_settings.agent_port,
            )
        )
    )
    # Чтобы видеть трейсы в консоли
    if trace_settings.log:
        trace.get_tracer_provider()\
            .add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))


@tracing_blueprint.before_request
def before_request():
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        raise RuntimeError('request id is required') 
