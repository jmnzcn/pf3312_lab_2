"""Lista ordenada de pasos que ejecuta scripts/run_analysis.py."""
from __future__ import annotations

OPTIONAL_STEPS: frozenset[str] = frozenset(
    {
        "scripts.score_tts_inteligibilidad",
    }
)

FULL_ANALYSIS_STEPS: tuple[str, ...] = (
    "scripts.render_pipeline",
    "analysis.generate_charts",
    "analysis.generate_six_dimensions",
    "analysis.generate_local_resources",
    "scripts.score_tts_inteligibilidad",
    "analysis.evaluate_llm_quality",
    "analysis.generate_appendix_inputs",
)

# Sin diagrama UML ni scoring TTS opcional (más rápido para CI)
SMOKE_ANALYSIS_STEPS: tuple[str, ...] = tuple(
    step
    for step in FULL_ANALYSIS_STEPS
    if step not in OPTIONAL_STEPS and step != "scripts.render_pipeline"
)
