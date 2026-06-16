# Apéndice B: Inputs controlados de prueba

Reproducción de los insumos definidos en `common/prompts.py`, `common/audio_samples.py` y `data/reference_transcriptions.json`.

## B.1 Prompts LLM (5)

### `p1_factual_corto`: Pregunta factual corta

> Responda en una sola oración: ¿cuál es la capital de Costa Rica y aproximadamente cuántos habitantes tiene su área metropolitana?

### `p2_razonamiento`: Razonamiento multi-paso

> Un sistema de agentes virtuales ofrece tres avatares 3D: Alfa (28 mil triángulos), Beta (31 mil triángulos) y Gamma (17 mil triángulos). Si la GPU del cliente soporta como máximo 50 mil triángulos simultáneos en pantalla, indique paso a paso qué combinaciones se pueden mostrar a la vez sin exceder el límite, y cuál combinación ofrece la mayor variedad visual sin pasarse del presupuesto.

### `p3_json_estricto`: Instrucciones con formato JSON estricto

> Devuelva EXCLUSIVAMENTE un objeto JSON válido, sin texto adicional, que liste tres agentes virtuales con los campos: nombre (string), estilo (uno de: realista, caricaturesco, cartoon), rol (string), expresiones (array de strings). No incluya comentarios ni markdown.

### `p4_contexto_largo`: Resumen de contexto largo

> A continuación encontrará un fragmento técnico. Resúmalo en máximo 60 palabras, conservando los tres puntos principales:
>
> Texto: En el diseño del tutor de voz del laboratorio se plantearon tres metas: que la respuesta en nube llegue en menos de dos segundos, que no se guarde audio sin un consentimiento explícito del usuario, y que se pueda cambiar la voz del avatar sin recompilar la aplicación Unity. También se propuso estimar el costo por clase de quince minutos y revisar el error de transcripción con grabaciones de sala, no solo con audios sintéticos de Piper.

### `p5_creativo`: Generación creativa / role-play

> Usted es un coach virtual de bienestar físico. Salude al usuario en máximo cuatro oraciones, ofrezca una rutina corta de calentamiento de tres ejercicios, y termine con una frase motivadora. Use un tono cercano pero profesional.

## B.2 Textos TTS (5)

- **`t1_saludo_corto`:** Hola, ¿cómo estás? Soy un agente virtual de prueba.
- **`t2_oracion_media`:** Hola. En esta prueba cada proveedor leerá la misma frase para comparar claridad y ritmo de la voz sintetizada.
- **`t3_parrafo_largo`:** El tutor virtual permite elegir voz masculina o femenina, activar subtítulos en pantalla y descargar un resumen de la sesión. Si el usuario cambia el idioma, la conversación reinicia desde el saludo inicial. También puede silenciar la síntesis y leer solo texto.
- **`t4_terminos_tecnicos`:** El agente virtual procesa audio a dieciséis kilohertz, calcula latencia al primer token y sintetiza respuestas de voz en streaming.
- **`t5_dialogo_cr`:** Mae, ¿podés explicarme en pocas palabras cómo elegir entre Groq, OpenAI y un modelo local para el tutor virtual?

## B.3 Audios STT (14)

- **`a1_saludo_corto`** (`a1_saludo_corto.wav`, synthetic_piper): «Hola, buenos días. Soy el asistente de voz del tutor del curso.»
- **`a2_oracion_media`** (`a2_oracion_media.wav`, synthetic_piper): «Hoy probamos cómo cada motor de voz entiende una frase media con el micrófono a un metro de distancia.»
- **`a4_parrafo_tecnico`** (`a4_parrafo_tecnico.wav`, synthetic_piper): «El sistema graba a dieciséis kilohertz, manda el audio al servicio de transcripción y muestra el texto en pantalla antes de pasarlo al modelo de lenguaje.»
- **`a5_acentos_cr`** (`a5_acentos_cr.wav`, synthetic_piper): «Mae, qué tuanis lo que hizo el agente virtual hoy. La verdad sí jaló pura vida con la transcripción en tiempo real.»
- **`g1_fleurs`** (`g1_fleurs.wav`, fleurs_human): «los murales o garabatos indeseados reciben el nombre de grafiti»
- **`g2_fleurs`** (`g2_fleurs.wav`, fleurs_human): «por el momento no se sabe qué cargos se imputarán o qué condujo a las autoridades hasta el niño pero se ha dado inicio a procedimientos penales de menores en el tribunal federal»
- **`g4_fleurs`** (`g4_fleurs.wav`, fleurs_human): «a veces un mismo vuelo puede costar precios muy diferentes en varios recopiladores de contenidos por lo que vale la pena comparar los resultados de búsqueda y navegar en el sitio web de la empresa antes de realizar la reserva»
- **`c1_cv_noisy`** (`c1_cv_noisy.wav`, common_voice_noisy): «Por un lado, en el sector culto encontramos un movimiento progresivamente creciente.»
- **`c3_cv_noisy`** (`c3_cv_noisy.wav`, common_voice_noisy): «Generalmente se celebra el tercer sábado del mes de septiembre.»
- **`r1_cv_centroamerica`** (`r1_cv_centroamerica.wav`, common_voice_central_america): «Situado en la provincia de Guadalajara, en la comarca del Señorío de Molina-Alto Tajo.»
- **`r2_cv_centroamerica_largo`** (`r2_cv_centroamerica_largo.wav`, common_voice_central_america): «Situado en la provincia de Guadalajara, en la comarca del Señorío de Molina-Alto Tajo. Sin embargo, la investigación paleontológica para buscar conexiones evolutivas tiene ciertas limitaciones. La Real Academia Española define orientador como "que orienta".»
- **`l1_fleurs_largo`** (`l1_fleurs_largo.wav`, fleurs_human_concat): «por el momento no se sabe qué cargos se imputarán o qué condujo a las autoridades hasta el niño pero se ha dado inicio a procedimientos penales de menores en el tribunal federal a veces un mismo vuelo puede costar precios muy diferentes en varios recopiladores de contenidos por lo que vale la pena comparar los resultados de búsqueda y navegar en el sitio web de la empresa antes de realizar la reserva»
- **`l2_piper_largo`** (`l2_piper_largo.wav`, synthetic_piper_long): «El tutor de voz del laboratorio escucha al estudiante por el micrófono del laptop, muestra en pantalla lo que entendió y responde con audio generado. Si la red falla, la aplicación puede cambiar a un modo local que tarda más pero no envía datos afuera. En las pruebas del curso se midió el tiempo de cada paso por separado y también el turno completo, porque sumar latencias aisladas no siempre coincide con lo que siente el usuario en la sala. Por eso en el protocolo de benchmark también se registró el costo por clase de quince minutos y se comparó el error de transcripción entre grabaciones de sala y archivos sintéticos.»
- **`l4_noisy_largo`** (`l4_noisy_largo.wav`, synthetic_noisy_long): «por el momento no se sabe qué cargos se imputarán o qué condujo a las autoridades hasta el niño pero se ha dado inicio a procedimientos penales de menores en el tribunal federal a veces un mismo vuelo puede costar precios muy diferentes en varios recopiladores de contenidos por lo que vale la pena comparar los resultados de búsqueda y navegar en el sitio web de la empresa antes de realizar la reserva»
