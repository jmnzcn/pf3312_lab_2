from benchmarks.pipeline.scenarios import E2E_AUDIO_IDS, PIPELINE_SCENARIOS, scenario_dicts
from common.e2e import E2ETurnResult, e2e_llm_prompt


def test_pipeline_scenarios_shared_with_cost_analysis():
    rows = scenario_dicts()
    assert len(rows) == len(PIPELINE_SCENARIOS) == 4
    assert rows[0]["escenario"] == PIPELINE_SCENARIOS[0].nombre


def test_e2e_audio_subset_covers_five_sources():
    assert len(E2E_AUDIO_IDS) == 5
    assert "c1_cv_noisy" in E2E_AUDIO_IDS
    assert "l1_fleurs_largo" in E2E_AUDIO_IDS


def test_e2e_llm_prompt_includes_transcript():
    p = e2e_llm_prompt("Hola, necesito ayuda")
    assert "Hola, necesito ayuda" in p["content"]
    assert p["id"] == "e2e_turn"


def test_e2e_turn_overhead_and_cost():
    turn = E2ETurnResult(
        escenario="test",
        stt_provider="a",
        llm_provider="b",
        tts_provider="c",
        test_id="x",
        run_id=1,
        stt_latency_ms=100,
        llm_latency_ms=200,
        tts_latency_ms=150,
        total_latency_ms=500,
        stt_cost_usd=0.001,
        llm_cost_usd=0.002,
        tts_cost_usd=0.003,
    )
    turn.finalize()
    assert turn.overhead_ms == 50
    assert turn.total_cost_usd == 0.006
