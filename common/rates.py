"""Tarifas USD usadas en benchmarks e informe."""
from __future__ import annotations

# --- LLM (USD por millón de tokens) ---
OPENAI_GPT4O_INPUT_PER_M = 2.50
OPENAI_GPT4O_OUTPUT_PER_M = 10.00

ANTHROPIC_SONNET4_INPUT_PER_M = 3.00
ANTHROPIC_SONNET4_OUTPUT_PER_M = 15.00

GEMINI_FLASH_INPUT_PER_M = 0.30
GEMINI_FLASH_OUTPUT_PER_M = 2.50

GROQ_LLAMA33_INPUT_PER_M = 0.59
GROQ_LLAMA33_OUTPUT_PER_M = 0.79

# --- STT (USD por minuto de audio) ---
DEEPGRAM_NOVA3_USD_PER_MIN = 0.0043
ASSEMBLYAI_USD_PER_MIN = 0.0036
OPENAI_WHISPER_USD_PER_MIN = 0.006
AZURE_STT_USD_PER_MIN = 0.0167

# --- TTS (USD por millón de caracteres) ---
GOOGLE_TTS_USD_PER_M_CHARS = 16.0
AZURE_TTS_USD_PER_M_CHARS = 16.0
ELEVENLABS_USD_PER_M_CHARS = 300.0
OPENAI_TTS_USD_PER_M_CHARS = 600.0

# Tablas para analysis/generate_unit_pricing.py
LLM_PRICING_ROWS = [
    {
        "proveedor": "openai",
        "modelo": "gpt-4o",
        "usd_input_M_tokens": OPENAI_GPT4O_INPUT_PER_M,
        "usd_output_M_tokens": OPENAI_GPT4O_OUTPUT_PER_M,
        "fuente": "common/rates.py",
    },
    {
        "proveedor": "anthropic",
        "modelo": "claude-sonnet-4-6",
        "usd_input_M_tokens": ANTHROPIC_SONNET4_INPUT_PER_M,
        "usd_output_M_tokens": ANTHROPIC_SONNET4_OUTPUT_PER_M,
        "fuente": "common/rates.py",
    },
    {
        "proveedor": "google",
        "modelo": "gemini-2.5-flash",
        "usd_input_M_tokens": GEMINI_FLASH_INPUT_PER_M,
        "usd_output_M_tokens": GEMINI_FLASH_OUTPUT_PER_M,
        "fuente": "common/rates.py",
    },
    {
        "proveedor": "groq",
        "modelo": "llama-3.3-70b-versatile",
        "usd_input_M_tokens": GROQ_LLAMA33_INPUT_PER_M,
        "usd_output_M_tokens": GROQ_LLAMA33_OUTPUT_PER_M,
        "fuente": "common/rates.py",
    },
    {
        "proveedor": "ollama",
        "modelo": "llama3.2:3b",
        "usd_input_M_tokens": 0.0,
        "usd_output_M_tokens": 0.0,
        "fuente": "local (costo marginal API $0)",
    },
]

STT_PRICING_ROWS = [
    {"proveedor": "deepgram", "modelo": "nova-3", "usd_minuto": DEEPGRAM_NOVA3_USD_PER_MIN},
    {"proveedor": "assemblyai", "modelo": "universal-3-pro", "usd_minuto": ASSEMBLYAI_USD_PER_MIN},
    {"proveedor": "openai", "modelo": "whisper-1", "usd_minuto": OPENAI_WHISPER_USD_PER_MIN},
    {"proveedor": "azure", "modelo": "speech-recognition-standard", "usd_minuto": AZURE_STT_USD_PER_MIN},
    {"proveedor": "faster-whisper", "modelo": "large-v3", "usd_minuto": 0.0},
]

TTS_PRICING_ROWS = [
    {"proveedor": "google", "modelo": "es-ES-Neural2-A", "usd_M_caracteres": GOOGLE_TTS_USD_PER_M_CHARS},
    {"proveedor": "azure", "modelo": "es-CR-MariaNeural", "usd_M_caracteres": AZURE_TTS_USD_PER_M_CHARS},
    {
        "proveedor": "elevenlabs",
        "modelo": "eleven_multilingual_v2",
        "usd_M_caracteres": ELEVENLABS_USD_PER_M_CHARS,
    },
    {"proveedor": "openai", "modelo": "gpt-4o-mini-tts", "usd_M_caracteres": OPENAI_TTS_USD_PER_M_CHARS},
    {"proveedor": "piper", "modelo": "es_ES-davefx-medium", "usd_M_caracteres": 0.0},
]
