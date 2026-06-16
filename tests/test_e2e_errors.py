from unittest.mock import MagicMock

from benchmarks.pipeline.scenarios import PipelineScenario
from benchmarks.pipeline.e2e_runner import run_e2e_turn
from common.audio_samples import AudioSample
from common.base import BenchmarkResult, stt_output_fields


def _audio(tmp_path) -> AudioSample:
    wav = tmp_path / "test.wav"
    wav.write_bytes(b"RIFF")
    return AudioSample(
        id="test_audio",
        path=wav,
        reference_text="hola mundo",
        duration_sec=1.0,
    )


def test_e2e_propagates_stt_error_without_double_prefix(tmp_path):
    audio = _audio(tmp_path)
    scenario = PipelineScenario("stack", "azure", "openai", "azure")
    stt = MagicMock()
    stt.run_single.return_value = BenchmarkResult(
        category="stt",
        provider="azure",
        model="speech",
        test_id=audio.id,
        run_id=1,
        error="stt/azure: transcripción vacía · canceled",
        notes="Azure STT canceled · Error",
    )
    turn = run_e2e_turn(scenario, audio, 1, stt_bench=stt, llm_bench=MagicMock(), tts_bench=MagicMock())
    assert turn.error == "stt/azure: transcripción vacía · canceled"
    assert "stt/azure: stt/azure" not in turn.error


def test_e2e_uses_full_stt_output_text_not_preview(tmp_path):
    long_text = "palabra " * 80  # >200 chars
    audio = _audio(tmp_path)
    scenario = PipelineScenario("stack", "deepgram", "groq", "azure")
    stt = MagicMock()
    stt.run_single.return_value = BenchmarkResult(
        category="stt",
        provider="deepgram",
        model="nova-3",
        test_id=audio.id,
        run_id=1,
        output_text=long_text.strip(),
        output_preview=long_text.strip()[:200],
        latency_ms=50,
    )
    llm = MagicMock()
    llm.run_single.return_value = BenchmarkResult(
        category="llm",
        provider="groq",
        model="llama",
        test_id="e2e_turn",
        run_id=1,
        output_preview="ok",
        latency_ms=80,
    )
    tts = MagicMock()
    tts.run_single.return_value = BenchmarkResult(
        category="tts",
        provider="azure",
        model="voice",
        test_id="e2e_test_audio",
        run_id=1,
        latency_ms=120,
    )
    turn = run_e2e_turn(scenario, audio, 1, stt_bench=stt, llm_bench=llm, tts_bench=tts)
    assert turn.error is None
    assert turn.transcript == long_text.strip()
    llm_prompt = llm.run_single.call_args[0][0]
    assert long_text.strip() in llm_prompt["content"]


def test_stt_output_fields_keeps_full_text():
    text = "x" * 500
    fields = stt_output_fields(text)
    assert fields["output_text"] == text
    assert len(fields["output_preview"]) == 200


def test_e2e_propagates_tts_error_with_notes(tmp_path):
    audio = _audio(tmp_path)
    scenario = PipelineScenario("stack", "deepgram", "groq", "azure")
    stt = MagicMock()
    stt.run_single.return_value = BenchmarkResult(
        category="stt",
        provider="deepgram",
        model="nova-3",
        test_id=audio.id,
        run_id=1,
        output_preview="hola",
        latency_ms=50,
    )
    llm = MagicMock()
    llm.run_single.return_value = BenchmarkResult(
        category="llm",
        provider="groq",
        model="llama",
        test_id="e2e_turn",
        run_id=1,
        output_preview="respuesta del asistente",
        latency_ms=80,
    )
    tts = MagicMock()
    tts.run_single.return_value = BenchmarkResult(
        category="tts",
        provider="azure",
        model="voice",
        test_id="e2e_test_audio",
        run_id=1,
        error="tts/azure: Azure TTS canceled · TooManyRequests",
        notes="Azure TTS canceled · TooManyRequests",
        latency_ms=120,
    )
    turn = run_e2e_turn(scenario, audio, 1, stt_bench=stt, llm_bench=llm, tts_bench=tts)
    assert turn.error == "tts/azure: Azure TTS canceled · TooManyRequests"
    assert turn.notes == "Azure TTS canceled · TooManyRequests"
    assert turn.stt_latency_ms == 50
    assert turn.llm_latency_ms == 80
