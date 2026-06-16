# Recursos locales: escalabilidad (dimensión 3)

- **Plataforma:** Windows-11-10.0.26200-SP0
- **CPU lógicos:** 12
- **RAM total:** 31.73 GB (disponible al capturar: 6.8 GB)

| GPU | VRAM total (MB) | VRAM usada (MB) | Driver |
|-----|-----------------|-----------------|--------|
| Quadro P2000 | 4096 | 495 | 573.96 |

**Energía (estimada):** TDP referencia GPU ~75 W (Quadro P2000). En inferencia local sostenida (faster-whisper/Ollama) el consumo del sistema se acerca a carga GPU+CPU; no se midió wattímetro en esta corrida; valor indicativo para comparar nube ($/llamada) vs. estación de trabajo.

## Modelos locales evaluados

| componente     | modelo                |
|----------------|-----------------------|
| ollama         | llama3.2:3b           |
| faster_whisper | large-v3 int8_float16 |
| piper          | es_ES-davefx-medium   |

*Costo API de modelos locales: $0. A cambio: latencia mayor y consumo de VRAM/RAM en esta estación de trabajo.*
