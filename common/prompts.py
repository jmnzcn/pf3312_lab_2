"""Cinco prompts en español para benchmarks LLM (también usados en TTS/STT sintético)."""
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
            "Un sistema de agentes virtuales ofrece tres avatares 3D: Alfa (28 mil "
            "triángulos), Beta (31 mil triángulos) y Gamma (17 mil triángulos). Si la "
            "GPU del cliente soporta como máximo 50 mil triángulos simultáneos en "
            "pantalla, indique paso a paso qué combinaciones se pueden mostrar a la "
            "vez sin exceder el límite, y cuál combinación ofrece la mayor variedad "
            "visual sin pasarse del presupuesto."
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
            "Texto: En el diseño del tutor de voz del laboratorio se plantearon tres "
            "metas: que la respuesta en nube llegue en menos de dos segundos, que no se "
            "guarde audio sin un consentimiento explícito del usuario, y que se pueda "
            "cambiar la voz del avatar sin recompilar la aplicación Unity. También se "
            "propuso estimar el costo por clase de quince minutos y revisar el error de "
            "transcripción con grabaciones de sala, no solo con audios sintéticos de Piper."
        ),
        "expected_tokens": 200,
    },
    {
        "id": "p5_creativo",
        "title": "Generación creativa / role-play",
        "content": (
            "Usted es un coach virtual de bienestar físico. Salude al usuario en "
            "máximo cuatro oraciones, ofrezca una rutina corta de calentamiento de "
            "tres ejercicios, y termine con una frase motivadora. Use un tono cercano "
            "pero profesional."
        ),
        "expected_tokens": 180,
    },
]


def get_prompt(prompt_id: str) -> PromptSpec:
    for p in LLM_PROMPTS:
        if p["id"] == prompt_id:
            return p
    raise KeyError(f"Prompt no encontrado: {prompt_id}")
