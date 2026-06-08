# Resumen comparativo - LLM

*Corrida: `2026-06-08T05:47:46Z` · runs/input: 5 · Python 3.13.13*

| provider   | model                   | deployment   |   llamadas |   latencia_ms_prom |   latencia_ms_std |   latencia_ms_p95 |   ttft_ms_prom |   costo_usd_prom | categoria   |
|------------|-------------------------|--------------|------------|--------------------|-------------------|-------------------|----------------|------------------|-------------|
| anthropic  | claude-sonnet-4-6       | cloud        |         25 |            6979.31 |           4672.96 |          14756.4  |        1497.13 |         0.005716 | llm         |
| google     | gemini-2.5-flash        | cloud        |         25 |            5966.03 |           4251.84 |          12148.9  |        4834.07 |         0.000748 | llm         |
| groq       | llama-3.3-70b-versatile | cloud        |         25 |             675.16 |            380.8  |           1399.7  |         230.73 |         0.000218 | llm         |
| ollama     | llama3.2:3b             | local        |         25 |           15400.6  |          12408.9  |          37157    |        1087.1  |         0        | llm         |
| openai     | gpt-4o                  | cloud        |         25 |            1918.41 |           1440.69 |           4816.11 |         601.13 |         0.002081 | llm         |
