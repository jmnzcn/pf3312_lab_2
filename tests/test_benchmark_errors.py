from types import SimpleNamespace

from common.base import BenchmarkResult
from common.benchmark_errors import (
    e2e_exception_stage,
    format_exception,
    mark_empty_llm,
    mark_empty_stt,
    mark_tts_output,
    provider_error,
    stage_error,
)
from common.e2e import E2ETurnResult


class _ApiError(Exception):
    def __init__(self, message: str, status_code: int = 429):
        super().__init__(message)
        self.status_code = status_code
        self.body = '{"error":"rate_limit"}'


def test_format_exception_includes_status_and_body():
    exc = _ApiError("Too many requests", status_code=429)
    msg = format_exception(exc)
    assert "ApiError" in msg
    assert "status_code=429" in msg
    assert "body=" in msg


def test_stage_error_format():
    assert stage_error("stt", "azure", "timeout") == "stt/azure: timeout"


def test_provider_error_with_stage():
    assert provider_error("deepgram", "quota", stage="stt") == "stt/deepgram: quota"


def test_mark_empty_stt_sets_error_and_notes():
    result = BenchmarkResult(category="stt", provider="deepgram", model="nova-3", test_id="x", run_id=1)
    out = mark_empty_stt(result, "", detail="sin alternativas")
    assert out.error == "stt/deepgram: transcripción vacía · sin alternativas"
    assert out.notes == "sin alternativas"


def test_mark_empty_llm_skips_when_output_present():
    result = BenchmarkResult(category="llm", provider="openai", model="gpt-4o", test_id="p1", run_id=1)
    out = mark_empty_llm(result, "hola")
    assert out.error is None


def test_mark_tts_output_flags_zero_byte_file(tmp_path):
    wav = tmp_path / "empty.wav"
    wav.write_bytes(b"")
    result = BenchmarkResult(category="tts", provider="piper", model="es", test_id="t1", run_id=1)
    out = mark_tts_output(result, wav)
    assert out.error is not None
    assert "tts/piper" in out.error
    assert "bytes=0" in out.error


def test_e2e_exception_stage_infers_tts_after_llm():
    scenario = SimpleNamespace(stt="a", llm="b", tts="c")
    turn = E2ETurnResult(
        escenario="x",
        stt_provider="a",
        llm_provider="b",
        tts_provider="c",
        test_id="audio",
        run_id=1,
        stt_latency_ms=100,
        llm_latency_ms=200,
        llm_response="respuesta",
    )
    stage, provider = e2e_exception_stage(turn, scenario)
    assert stage == "tts"
    assert provider == "c"
