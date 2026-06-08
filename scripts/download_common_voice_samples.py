"""Descarga 5 clips de voz humana en español para el benchmark STT.

Mozilla Common Voice ya no publica archivos en Hugging Face (solo en Mozilla Data
Collective con registro). Este script usa **Google FLEURS** (`es_419`): voz humana
leída, transcripción verificada, licencia CC BY 4.0.

Guarda WAV 16 kHz mono en data/test_audio/ y actualiza las entradas g* en
reference_transcriptions.json.

Uso:
    pip install datasets
    python scripts/download_common_voice_samples.py
    python scripts/download_common_voice_samples.py --force
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import soundfile as sf
from datasets import Audio, load_dataset


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "test_audio"
TARGET_SR = 16_000

DURATION_BUCKETS: list[tuple[str, float, float]] = [
    ("corto_1", 2.5, 6.0),
    ("corto_2", 6.0, 10.0),
    ("medio_1", 10.0, 15.0),
    ("medio_2", 15.0, 22.0),
    ("corto_3", 3.0, 8.0),
]

MAX_SCAN = 6_000
HUMAN_SOURCES = {"human_recorded", "common_voice_human", "fleurs_human"}


@dataclass
class PickedClip:
    bucket: str
    file_name: str
    entry_id: str
    sentence: str
    duration_sec: float
    fleurs_id: int
    language: str


def _resample_to_16k(data: np.ndarray, sr: int) -> np.ndarray:
    if sr == TARGET_SR:
        return data.astype(np.float32)
    n = int(len(data) * TARGET_SR / sr)
    x_old = np.linspace(0, 1, len(data), endpoint=False)
    x_new = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x_new, x_old, data).astype(np.float32)


def _decode_audio_bytes(audio_bytes: bytes) -> tuple[np.ndarray, int]:
    data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
    return data, int(sr)


def _save_wav(path: Path, array: np.ndarray, sr: int) -> None:
    if array.ndim > 1:
        array = array.mean(axis=1)
    array = _resample_to_16k(array, sr)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), array, TARGET_SR, subtype="PCM_16")


def _load_dataset_stream():
    try:
        import datasets  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "Falta el paquete 'datasets'. Instalá con:\n"
            "  pip install datasets\n"
            f"Detalle: {exc}"
        ) from exc

    print("Conectando a Google FLEURS (es_419, train, streaming)...")
    stream = load_dataset("google/fleurs", "es_419", split="train", streaming=True)
    return stream.cast_column("audio", Audio(decode=False))


def _download_clips(force: bool) -> list[PickedClip]:
    existing = sorted(OUTPUT_DIR.glob("g*_fleurs.wav"))
    if existing and not force:
        print(
            f"Ya existen {len(existing)} archivos g*_fleurs.wav. "
            "Usá --force para reemplazar."
        )
        return []

    stream = _load_dataset_stream()
    picked: list[PickedClip] = []
    filled = {name: False for name, _, _ in DURATION_BUCKETS}

    for idx, row in enumerate(stream):
        if idx >= MAX_SCAN or all(filled.values()):
            break

        sentence = (row.get("transcription") or "").strip()
        if len(sentence) < 12:
            continue

        audio = row.get("audio") or {}
        audio_bytes = audio.get("bytes")
        if not audio_bytes:
            continue

        array, sr = _decode_audio_bytes(audio_bytes)
        duration = len(array) / sr

        for bucket_name, lo, hi in DURATION_BUCKETS:
            if filled[bucket_name] or not (lo <= duration < hi):
                continue

            slot = len(picked) + 1
            file_name = f"g{slot}_fleurs.wav"
            out = OUTPUT_DIR / file_name
            _save_wav(out, array, sr)

            clip = PickedClip(
                bucket=bucket_name,
                file_name=file_name,
                entry_id=f"g{slot}_fleurs",
                sentence=sentence,
                duration_sec=round(duration, 2),
                fleurs_id=int(row.get("id", -1)),
                language=str(row.get("lang_id", "es_419")),
            )
            picked.append(clip)
            filled[bucket_name] = True
            print(f"  [{slot}/5] {bucket_name} ({duration:.1f}s) -> {file_name}")
            print(f"       {sentence[:90]}{'...' if len(sentence) > 90 else ''}")
            break

    missing = [name for name, ok in filled.items() if not ok]
    if missing:
        raise RuntimeError(
            f"Solo se encontraron {len(picked)} clips tras revisar {MAX_SCAN} filas. "
            f"Faltan buckets: {', '.join(missing)}."
        )

    return picked


def _update_catalog(clips: list[PickedClip]) -> None:
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    samples = data.get("samples", [])

    samples = [
        s
        for s in samples
        if s.get("source") not in HUMAN_SOURCES
        and not str(s.get("id", "")).startswith("g")
    ]

    for clip in clips:
        samples.append(
            {
                "id": clip.entry_id,
                "file": clip.file_name,
                "language": clip.language,
                "source": "fleurs_human",
                "reference_text": clip.sentence,
                "duration_sec": clip.duration_sec,
                "fleurs_id": clip.fleurs_id,
                "notes": (
                    "Clip de Google FLEURS (es_419, train). Voz humana leída con "
                    "transcripción verificada (CC BY 4.0). No es grabación del investigador."
                ),
            }
        )

    data["samples"] = samples
    data["_doc"] = (
        "Catálogo STT. synthetic_piper: scripts/generate_stt_audio_piper.py. "
        "fleurs_human: scripts/download_common_voice_samples.py (FLEURS es_419)."
    )
    REFERENCE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK catálogo: {REFERENCE_FILE.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descargar 5 clips de voz humana en español (FLEURS es_419)."
    )
    parser.add_argument("--force", action="store_true", help="Reemplazar g*_fleurs.wav existentes.")
    args = parser.parse_args()

    clips = _download_clips(force=args.force)
    if not clips:
        return

    _update_catalog(clips)
    print("\nListo. Corré el benchmark STT con:")
    print("  python -m benchmarks.stt.run_all 5")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelado.")
