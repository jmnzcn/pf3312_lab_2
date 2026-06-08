# TTS — MOS (plantilla)

| provider   |   mos_inteligibilidad |   mos_naturalidad |   wer_promedio | nota                                                                      |
|------------|-----------------------|-------------------|----------------|---------------------------------------------------------------------------|
| azure      |                     4 |                 4 |         0.08   | Voz es-CR clara; t1 con WER alto por saludo informal transcrito distinto. |
| elevenlabs |                     4 |                 5 |         0.0741 | Mejor naturalidad esperada; WER casi cero en t2/t3.                       |
| google     |                     3 |                 4 |         0.1211 | Ligera pérdida en t2; neural estable en párrafo largo.                    |
| openai     |                     4 |                 4 |         0.0921 | Buena inteligibilidad en textos medios/largos.                            |
| piper      |                     4 |                 3 |         0.0902 | Local gratuito; timbre más sintético que nube.                            |
