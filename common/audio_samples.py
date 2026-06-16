"""Audios STT en data/test_audio/ y textos TTS. Ver data/test_audio/README.md."""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import soundfile as sf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEST_AUDIO_DIR = PROJECT_ROOT / "data" / "test_audio"
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"

CATALOG_DOC = (
    "Catálogo STT (14 inputs activos). synthetic_piper: scripts/generate_stt_audio_piper.py. "
    "fleurs_human: scripts/download_common_voice_samples.py. "
    "common_voice_noisy: scripts/download_common_voice_noisy.py. "
    "common_voice_central_america: scripts/download_cv_centroamerica_samples.py. "
    "largos (l*): scripts/download_long_stt_samples.py."
)

EXPECTED_STT_IDS: tuple[str, ...] = (
    "a1_saludo_corto",
    "a2_oracion_media",
    "a4_parrafo_tecnico",
    "a5_acentos_cr",
    "g1_fleurs",
    "g2_fleurs",
    "g4_fleurs",
    "c1_cv_noisy",
    "c3_cv_noisy",
    "l1_fleurs_largo",
    "l2_piper_largo",
    "l4_noisy_largo",
    "r1_cv_centroamerica",
    "r2_cv_centroamerica_largo",
)

_REQUIRED_FIELDS = ("id", "file", "reference_text", "source")


@dataclass
class AudioSample:
    id: str
    path: Path
    reference_text: str
    language: str = "es-CR"
    duration_sec: Optional[float] = None

    def exists(self) -> bool:
        return self.path.exists()

    def load_duration(self) -> float:
        if self.duration_sec is None and self.exists():
            with sf.SoundFile(str(self.path)) as snd:
                self.duration_sec = len(snd) / snd.samplerate
        return self.duration_sec or 0.0


def load_catalog_data() -> dict:
    if not REFERENCE_FILE.exists():
        return {"samples": []}
    return json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))


def catalog_fingerprint() -> str:
    data = load_catalog_data()
    payload = json.dumps(data.get("samples", []), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def wav_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_wav_checksums() -> list[str]:
    """Compara sha256 en disco vs. reference_transcriptions.json."""
    warnings: list[str] = []
    for entry in load_catalog_data().get("samples", []):
        entry_id = entry.get("id", "?")
        expected = entry.get("sha256")
        if not expected:
            warnings.append(f"Sin sha256 en catálogo: {entry_id}")
            continue
        wav = TEST_AUDIO_DIR / entry.get("file", "")
        if not wav.exists():
            warnings.append(f"WAV ausente: {wav.name} ({entry_id})")
            continue
        actual = wav_sha256(wav)
        if actual != expected:
            warnings.append(
                f"Checksum distinto en {entry_id}: esperado {expected[:12]}…, "
                f"en disco {actual[:12]}…"
            )
    return warnings


def validate_catalog(*, require_wavs: bool = False) -> list[str]:
    """Valida el catálogo; devuelve lista de advertencias (vacía = OK estructural)."""
    warnings: list[str] = []
    if not REFERENCE_FILE.exists():
        warnings.append(f"Falta {REFERENCE_FILE.relative_to(PROJECT_ROOT)}")
        return warnings

    data = load_catalog_data()
    samples = data.get("samples", [])
    if not samples:
        warnings.append("Catálogo STT vacío")
        return warnings

    seen: set[str] = set()
    for entry in samples:
        entry_id = entry.get("id", "")
        for field in _REQUIRED_FIELDS:
            if not entry.get(field):
                warnings.append(f"Entrada {entry_id or '?'} sin campo '{field}'")
        if entry_id in seen:
            warnings.append(f"ID duplicado: {entry_id}")
        seen.add(entry_id)
        if require_wavs:
            wav = TEST_AUDIO_DIR / entry.get("file", "")
            if not wav.exists():
                warnings.append(f"WAV ausente: {wav.name} ({entry_id})")

    missing_ids = set(EXPECTED_STT_IDS) - seen
    extra_ids = seen - set(EXPECTED_STT_IDS)
    if missing_ids:
        warnings.append(f"IDs esperados ausentes: {', '.join(sorted(missing_ids))}")
    if extra_ids:
        warnings.append(f"IDs no esperados en catálogo: {', '.join(sorted(extra_ids))}")

    return warnings


def load_audio_samples() -> list[AudioSample]:
    """Carga el catálogo desde reference_transcriptions.json."""
    data = load_catalog_data()
    samples: list[AudioSample] = []
    for entry in data.get("samples", []):
        samples.append(
            AudioSample(
                id=entry["id"],
                path=TEST_AUDIO_DIR / entry["file"],
                reference_text=entry["reference_text"],
                language=entry.get("language", "es-CR"),
            )
        )
    return samples


# Textos fijos para benchmarks TTS
TTS_TEXTS = [
    {
        "id": "t1_saludo_corto",
        "text": "Hola, ¿cómo estás? Soy un agente virtual de prueba.",
    },
    {
        "id": "t2_oracion_media",
        "text": (
            "Hola. En esta prueba cada proveedor leerá la misma frase para "
            "comparar claridad y ritmo de la voz sintetizada."
        ),
    },
    {
        "id": "t3_parrafo_largo",
        "text": (
            "El tutor virtual permite elegir voz masculina o femenina, "
            "activar subtítulos en pantalla y descargar un resumen de la sesión. "
            "Si el usuario cambia el idioma, la conversación reinicia desde el "
            "saludo inicial. También puede silenciar la síntesis y leer solo texto."
        ),
    },
    {
        "id": "t4_terminos_tecnicos",
        "text": (
            "El agente virtual procesa audio a dieciséis kilohertz, calcula "
            "latencia al primer token y sintetiza respuestas de voz en streaming."
        ),
    },
    {
        "id": "t5_dialogo_cr",
        "text": (
            "Mae, ¿podés explicarme en pocas palabras cómo elegir entre Groq, "
            "OpenAI y un modelo local para el tutor virtual?"
        ),
    },
]
