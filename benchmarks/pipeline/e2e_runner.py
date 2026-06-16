"""Un turno completo: audio → STT → LLM → TTS."""
from __future__ import annotations

import time

from benchmarks.pipeline.scenarios import PIPELINE_SCENARIOS, PipelineScenario
from common.audio_samples import AudioSample
from common.base import BenchmarkResult
from common.benchmark_errors import (
    e2e_exception_stage,
    fail_e2e_stage,
    format_exception,
    stage_error,
)
from common.e2e import E2ETurnResult, e2e_llm_prompt
from common.metrics import elapsed_ms

from benchmarks.pipeline.providers import llm_factory, stt_factory, tts_factory


DEFAULT_SCENARIOS: list[PipelineScenario] = list(PIPELINE_SCENARIOS)


def _response_text(result: BenchmarkResult) -> str:
    return (result.output_text or result.output_preview or "").strip()


def run_e2e_turn(
    scenario: PipelineScenario,
    audio: AudioSample,
    run_id: int,
    *,
    stt_bench=None,
    llm_bench=None,
    tts_bench=None,
) -> E2ETurnResult:
    """Mide latencia de pared del turno STT→LLM→TTS y el desglose por etapa."""
    turn = E2ETurnResult(
        escenario=scenario.nombre,
        stt_provider=scenario.stt,
        llm_provider=scenario.llm,
        tts_provider=scenario.tts,
        test_id=audio.id,
        run_id=run_id,
    )
    if not audio.exists():
        turn.error = stage_error("input", audio.id, f"audio no encontrado · {audio.path}")
        return turn

    stt = stt_bench or stt_factory(scenario.stt)
    llm = llm_bench or llm_factory(scenario.llm)
    tts = tts_bench or tts_factory(scenario.tts)
    missing = [
        f"stt/{scenario.stt}" if stt is None else "",
        f"llm/{scenario.llm}" if llm is None else "",
        f"tts/{scenario.tts}" if tts is None else "",
    ]
    missing = [m for m in missing if m]
    if missing:
        turn.error = stage_error("setup", scenario.nombre, f"proveedor no disponible · {', '.join(missing)}")
        return turn

    wall_start = time.perf_counter()
    try:
        stt_res = stt.run_single(audio, run_id)
        if stt_res.error:
            turn.error = stt_res.error
            turn.notes = stt_res.notes
            turn.total_latency_ms = elapsed_ms(wall_start)
            return turn
        turn.stt_latency_ms = stt_res.latency_ms
        turn.stt_cost_usd = stt_res.cost_usd
        transcript = _response_text(stt_res)
        turn.transcript = transcript
        if not transcript:
            detail = stt_res.notes or stt_res.error or "sin texto en output_preview/output_text"
            return fail_e2e_stage(
                turn,
                stage="stt",
                provider=scenario.stt,
                detail=f"transcripción vacía · {detail}",
                notes=stt_res.notes,
                wall_start=wall_start,
                elapsed_ms_fn=elapsed_ms,
            )

        llm_prompt = e2e_llm_prompt(transcript)
        llm_res = llm.run_single(llm_prompt, run_id)
        if llm_res.error:
            turn.error = llm_res.error
            turn.notes = llm_res.notes
            turn.total_latency_ms = elapsed_ms(wall_start)
            return turn
        turn.llm_latency_ms = llm_res.latency_ms
        turn.llm_ttft_ms = llm_res.ttft_ms
        turn.llm_cost_usd = llm_res.cost_usd
        response = _response_text(llm_res)
        turn.llm_response = response
        if not response:
            detail = llm_res.notes or llm_res.error or "stream sin tokens"
            return fail_e2e_stage(
                turn,
                stage="llm",
                provider=scenario.llm,
                detail=f"respuesta vacía · {detail}",
                notes=llm_res.notes,
                wall_start=wall_start,
                elapsed_ms_fn=elapsed_ms,
            )

        tts_text = response[:500]
        tts_input = {"id": f"e2e_{audio.id}", "text": tts_text}
        tts_res = tts.run_single(tts_input, run_id)
        if tts_res.error:
            turn.error = tts_res.error
            turn.notes = tts_res.notes
            turn.total_latency_ms = elapsed_ms(wall_start)
            return turn
        turn.tts_latency_ms = tts_res.latency_ms
        turn.tts_cost_usd = tts_res.cost_usd
        turn.total_latency_ms = elapsed_ms(wall_start)
        turn.notes = f"tts_chars={len(tts_text)}"
        if tts_res.notes:
            turn.notes = f"{turn.notes}; {tts_res.notes}"
        return turn
    except Exception as exc:
        stage, provider = e2e_exception_stage(turn, scenario)
        turn.error = stage_error(stage, provider, format_exception(exc))
        turn.total_latency_ms = elapsed_ms(wall_start)
        return turn
