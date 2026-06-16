from common.benchmark_registry import BENCHMARK_REGISTRY, category_specs, factory_by_provider, providers_for_category


def test_registry_has_fifteen_benchmarks():
    assert len(BENCHMARK_REGISTRY) == 15
    assert len(category_specs("llm")) == 5
    assert len(category_specs("stt")) == 5
    assert len(category_specs("tts")) == 5


def test_registry_provider_ids_unique_per_category():
    for category in ("llm", "stt", "tts"):
        providers = providers_for_category(category)
        assert len(providers) == len(set(providers))


def test_factory_map_covers_pipeline_providers():
    stt = factory_by_provider("stt")
    assert set(stt) == {"deepgram", "openai", "assemblyai", "azure", "faster-whisper"}
    llm = factory_by_provider("llm")
    assert "google" in llm
    tts = factory_by_provider("tts")
    assert set(tts) == {"google", "elevenlabs", "azure", "piper", "openai"}
