*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*

## Prompt p3_json_estricto — cumplimiento de esquema JSON

| provider   |   llamadas |   json_valido |   tasa_json |
|------------|------------|---------------|-------------|
| anthropic  |          5 |             5 |         1   |
| google     |          5 |             5 |         1   |
| groq       |          5 |             5 |         1   |
| ollama     |          5 |             2 |         0.4 |
| openai     |          5 |             3 |         0.6 |

*Coherencia global en p1/p2/p4/p5: `data/llm_quality_notes.json`.*

## Notas cualitativas (archivo)

| provider   |   coherencia_1_5 |   instrucciones_1_5 | nota                                                                                                                                                                                         |
|------------|------------------|---------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| openai     |                5 |                   4 | Respuestas claras en español; p2 razona por combinaciones; p3 JSON con clave agentes; p4 resume las 6 dimensiones; p5 cumple rol Max con calentamiento. Población AMCR varía entre corridas. |
| anthropic  |                5 |                   3 | Contenido sólido pero añade markdown/emojis en p1–p5 cuando se pidió texto plano o JSON exclusivo; p3 sí entrega JSON válido. Excelente estructura en p2.                                    |
| google     |                4 |                   4 | Buen español y resúmenes útiles; p3 JSON 100% válido en corrida 2026-06-08; p4 condensa bien el texto largo.                                                                                 |
| groq       |                4 |                   3 | Rápido y coherente; p4 muy breve (cubre 3 bloques pero poco detalle); p3 a veces devuelve array sin envoltorio agentes; p5 ofrece rutina de calentamiento.                                   |
| ollama     |                3 |                   3 | Llama 3.2 3B local: p1 excede una oración; p3 JSON válido pero con personajes fuera de contexto (Batman/Sonic); p2 y p4 razonables para tamaño del modelo.                                   |
