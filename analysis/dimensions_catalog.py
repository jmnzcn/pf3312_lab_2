"""Catálogo cualitativo para dimensiones 4–6 (privacidad, customización, integración).

Escala 1–5: 1 = bajo / difícil, 5 = alto / excelente.
Fuentes: términos públicos de cada proveedor (mayo 2026) y naturaleza local vs cloud.
Revisar antes del PDF final si cambian políticas.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QualitativeScores:
    privacidad: int
    privacidad_nota: str
    customizacion: int
    customizacion_nota: str
    integracion: int
    integracion_nota: str


# Clave: "categoria/proveedor"
QUALITATIVE: dict[str, QualitativeScores] = {
    # --- LLM ---
    "llm/openai": QualitativeScores(
        3,
        "API: datos no usados para entrenar por defecto; retención limitada. Cloud.",
        5,
        "System prompt, temperatura, tools, múltiples modelos.",
        5,
        "SDK oficial Python; streaming SSE; amplia documentación.",
    ),
    "llm/anthropic": QualitativeScores(
        4,
        "Política API: no entrena con prompts por defecto.",
        5,
        "System, tools, ventanas largas, Claude family.",
        5,
        "SDK Python maduro; streaming de mensajes.",
    ),
    "llm/google": QualitativeScores(
        3,
        "Gemini API pay-tier distinto del free; revisar retención en consola.",
        4,
        "Instrucciones, safety, multimodal; menos open-weight en API.",
        4,
        "SDK google-genai; integración GCP opcional.",
    ),
    "llm/groq": QualitativeScores(
        4,
        "Inferencia acelerada; política de no entrenamiento en API.",
        3,
        "Menos knobs que OpenAI; modelos open-weight servidos.",
        4,
        "API compatible OpenAI-style; muy simple para prototipos.",
    ),
    "llm/ollama": QualitativeScores(
        5,
        "100 % local; datos no salen del equipo.",
        4,
        "Modelos intercambiables, Modelfile, parámetros locales.",
        3,
        "HTTP local; sin SLA cloud; ideal dev/offline.",
    ),
    # --- STT ---
    "stt/openai": QualitativeScores(
        3,
        "Audio enviado a cloud OpenAI; política API estándar.",
        3,
        "Idioma, prompt opcional; sin fine-tune trivial.",
        5,
        "Whisper API simple; mismo ecosistema que GPT.",
    ),
    "stt/deepgram": QualitativeScores(
        3,
        "Cloud; opciones enterprise para retención cero.",
        4,
        "Modelos Nova, idiomas, puntuación, diarización en planes altos.",
        4,
        "SDK v6, streaming WebSocket fuerte.",
    ),
    "stt/assemblyai": QualitativeScores(
        3,
        "Cloud; políticas según plan.",
        4,
        "Vocabulario custom, speaker labels, summarization add-ons.",
        4,
        "SDK Python; API REST clara.",
    ),
    "stt/azure": QualitativeScores(
        3,
        "Azure Cognitive Services; datos en región elegida.",
        4,
        "Custom speech models, frases, pronunciación.",
        4,
        "SDK Azure; buen fit .NET/Unity vía REST.",
    ),
    "stt/faster-whisper": QualitativeScores(
        5,
        "Offline local; sin envío a terceros.",
        3,
        "Modelo/tamaño/compute_type; sin custom cloud.",
        3,
        "Librería Python; requiere GPU/CPU tuning.",
    ),
    # --- TTS ---
    "tts/openai": QualitativeScores(
        3,
        "Cloud OpenAI; mismas consideraciones que LLM API.",
        4,
        "Varias voces, instrucciones en modelos nuevos.",
        5,
        "API unificada OpenAI; fácil desde Python.",
    ),
    "tts/elevenlabs": QualitativeScores(
        3,
        "Cloud; clonación de voz implica datos biométricos de voz.",
        5,
        "Clonación, estilos, multilingüe, ajuste expresivo.",
        4,
        "API REST; SDK; orientado a producto de voz.",
    ),
    "tts/azure": QualitativeScores(
        3,
        "Región Azure; cumplimiento enterprise.",
        4,
        "Neural voices, SSML, custom neural voice (planes altos).",
        4,
        "SDK + SSML; integración Unity vía plugin o REST.",
    ),
    "tts/google": QualitativeScores(
        3,
        "GCP; cuenta de servicio; datos en proyecto Google.",
        4,
        "Muchas voces Neural2/Wavenet, SSML, idiomas.",
        4,
        "Cliente google-cloud-texttospeech; GCP setup.",
    ),
    "tts/piper": QualitativeScores(
        5,
        "Offline; sin telemetría de contenido.",
        2,
        "Voces ONNX preentrenadas; cambiar modelo, pocos parámetros.",
        2,
        "CLI/subprocess; sin SDK cloud; manual en Unity.",
    ),
}
