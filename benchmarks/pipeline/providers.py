"""Registro de proveedores para el benchmark end-to-end."""
from __future__ import annotations

from common.base import Benchmark
from common.benchmark_registry import factory_by_provider
from common.runner import safe_factory


def stt_factory(provider: str) -> Benchmark | None:
    factories = factory_by_provider("stt")
    if provider not in factories:
        return None
    return safe_factory(f"stt/{provider}", factories[provider])


def llm_factory(provider: str) -> Benchmark | None:
    factories = factory_by_provider("llm")
    if provider not in factories:
        return None
    return safe_factory(f"llm/{provider}", factories[provider])


def tts_factory(provider: str) -> Benchmark | None:
    factories = factory_by_provider("tts")
    if provider not in factories:
        return None
    return safe_factory(f"tts/{provider}", factories[provider])
