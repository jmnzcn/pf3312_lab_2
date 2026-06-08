"""Prompts estandarizados de prueba para benchmarking de LLMs.

Cinco prompts en español que cubren niveles distintos de complejidad:
    1. Pregunta factual corta (latencia base, costo mínimo).
    2. Razonamiento multi-paso (capacidad de cadena lógica).
    3. Seguimiento de instrucciones con formato estricto (JSON).
    4. Comprensión de contexto largo (resumen de un texto extenso).
    5. Generación creativa / role-play (calidad subjetiva).

Estos prompts también se usan como entrada para los benchmarks de TTS,
y sus respuestas de referencia para STT cuando se sintetiza audio.
"""
from __future__ import annotations

from typing import TypedDict


class PromptSpec(TypedDict):
    id: str
    title: str
    content: str
    expected_tokens: int  # estimación cruda para planear costo


LLM_PROMPTS: list[PromptSpec] = [
    {
        "id": "p1_factual_corto",
        "title": "Pregunta factual corta",
        "content": (
            "Responda en una sola oración: ¿cuál es la capital de Costa Rica "
            "y aproximadamente cuántos habitantes tiene su área metropolitana?"
        ),
        "expected_tokens": 60,
    },
    {
        "id": "p2_razonamiento",
        "title": "Razonamiento multi-paso",
        "content": (
            "Un agente virtual tiene tres modelos: Max (gimnasio, 28 mil triángulos), "
            "Winston (entretenimiento, 31 mil triángulos) y Liam (educativo, 17 mil "
            "triángulos). Si la GPU del usuario soporta como máximo 50 mil triángulos "
            "simultáneos en pantalla, indique paso a paso qué combinaciones de modelos "
            "se pueden mostrar a la vez sin pasarse del límite, y cuál combinación "
            "ofrece la mayor variedad estética sin exceder dicho presupuesto."
        ),
        "expected_tokens": 250,
    },
    {
        "id": "p3_json_estricto",
        "title": "Instrucciones con formato JSON estricto",
        "content": (
            "Devuelva EXCLUSIVAMENTE un objeto JSON válido, sin texto adicional, "
            "que liste tres agentes virtuales con los campos: nombre (string), "
            "estilo (uno de: realista, caricaturesco, cartoon), rol (string), "
            "expresiones (array de strings). No incluya comentarios ni markdown."
        ),
        "expected_tokens": 200,
    },
    {
        "id": "p4_contexto_largo",
        "title": "Resumen de contexto largo",
        "content": (
            "A continuación encontrará un fragmento técnico. Resúmalo en máximo "
            "60 palabras, conservando los tres puntos principales:\n\n"
            "Texto: El benchmarking sistemático de servicios cognitivos para agentes "
            "virtuales contempla al menos seis dimensiones interdependientes: la "
            "latencia empírica, donde se distingue el tiempo al primer token de la "
            "latencia total de respuesta; la precisión, medida con métricas como "
            "Word Error Rate para reconocimiento de voz o coherencia subjetiva para "
            "modelos generativos; el costo a escala, expresado en dólares por millón "
            "de tokens, por minuto de audio transcrito o por caracteres sintetizados; "
            "la privacidad y gobernanza de los datos, que considera si los proveedores "
            "utilizan las entradas para reentrenar sus modelos comerciales; la "
            "customización, que incluye la inyección de system prompts y la "
            "clonación de voz; y finalmente la facilidad de integración con "
            "ecosistemas como Unity o aplicaciones C# y Python."
        ),
        "expected_tokens": 200,
    },
    {
        "id": "p5_creativo",
        "title": "Generación creativa / role-play",
        "content": (
            "Usted es Max, un acompañante virtual de bienestar físico atlético. "
            "Salude al usuario en máximo cuatro oraciones, ofrezca una rutina corta "
            "de calentamiento de tres ejercicios, y termine con una frase "
            "motivadora. Use un tono cercano pero profesional."
        ),
        "expected_tokens": 180,
    },
]


def get_prompt(prompt_id: str) -> PromptSpec:
    for p in LLM_PROMPTS:
        if p["id"] == prompt_id:
            return p
    raise KeyError(f"Prompt no encontrado: {prompt_id}")
