"""Pipeline E2E: STT → LLM → TTS por escenario."""
from __future__ import annotations

import sys

from dotenv import load_dotenv

from benchmarks.pipeline.e2e_runner import DEFAULT_SCENARIOS, run_e2e_turn
from benchmarks.pipeline.providers import llm_factory, stt_factory, tts_factory
from benchmarks.pipeline.scenarios import E2E_AUDIO_IDS
from common.audio_samples import load_audio_samples
from common.e2e import append_e2e_results
from common.run_context import ensure_run_batch, start_run_batch


load_dotenv()


def main(runs: int = 5, *, new_batch: bool = True) -> None:
    catalog = {s.id: s for s in load_audio_samples() if s.exists()}
    missing = [aid for aid in E2E_AUDIO_IDS if aid not in catalog]
    if missing:
        print(
            "[ERROR] Faltan audios E2E en data/test_audio/: "
            + ", ".join(missing)
            + ". Ver scripts de descarga en README."
        )
        return

    samples = [catalog[aid] for aid in E2E_AUDIO_IDS]
    if new_batch:
        start_run_batch(runs_per_input=runs, note="e2e pipeline", force=True)
    else:
        ensure_run_batch(runs_per_input=runs, note="full pipeline + e2e")
    all_results = []

    for scenario in DEFAULT_SCENARIOS:
        stt = stt_factory(scenario.stt)
        llm = llm_factory(scenario.llm)
        tts = tts_factory(scenario.tts)
        if stt is None or llm is None or tts is None:
            print(f"[SKIP] {scenario.nombre}: proveedor no disponible")
            continue
        print(f"\n>> E2E · {scenario.nombre} ({scenario.stt} → {scenario.llm} → {scenario.tts})")
        for audio in samples:
            for run_id in range(1, runs + 1):
                turn = run_e2e_turn(
                    scenario,
                    audio,
                    run_id,
                    stt_bench=stt,
                    llm_bench=llm,
                    tts_bench=tts,
                )
                all_results.append(turn)
                status = "OK" if not turn.error else f"ERR {turn.error}"
                print(
                    f"  {audio.id} run{run_id}: {turn.total_latency_ms:.0f} ms total "
                    f"(stt={turn.stt_latency_ms:.0f} llm={turn.llm_latency_ms:.0f} "
                    f"tts={turn.tts_latency_ms:.0f}) · {status}"
                )

    if not all_results:
        print("[WARN] Ningún escenario E2E ejecutado.")
        return

    append_e2e_results(all_results)
    ok = sum(1 for r in all_results if not r.error)
    print(f"\nOK E2E · {ok}/{len(all_results)} turnos · results/e2e_results.csv")


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    main(runs=n)
