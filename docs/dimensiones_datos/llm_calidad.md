*Dimensión 2 (precisión LLM): revisión manual de coherencia en p1/p2/p4/p5 y tasa de JSON válido en p3_json_estricto (escala 1-5 en las notas).*

## Prompt p3_json_estricto: cumplimiento de esquema JSON

| provider   |   llamadas |   json_valido |   tasa_json |
|------------|------------|---------------|-------------|
| anthropic  |          5 |             5 |         1   |
| google     |          5 |             3 |         0.6 |
| groq       |          5 |             5 |         1   |
| ollama     |          5 |             4 |         0.8 |
| openai     |          5 |             5 |         1   |

*Coherencia global en p1/p2/p4/p5: `data/llm_quality_notes.json`.*

*Evaluador: Ney Fred Jiménez Campos (B03230) · Revisión manual de las respuestas de la corrida LLM: coherencia en p1/p2/p4/p5 y cumplimiento de formato en p3_json_estricto.*

## Puntuación cualitativa (escala 1–5)

| provider   |   coherencia_1_5 |   instrucciones_1_5 |
|------------|------------------|---------------------|
| openai     |                5 |                   4 |
| anthropic  |                5 |                   3 |
| google     |                4 |                   4 |
| groq       |                4 |                   3 |
| ollama     |                3 |                   3 |
