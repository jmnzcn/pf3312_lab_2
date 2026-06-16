"""Descarga clips Common Voice 23.0 con ruido audible (c1, c3) para STT."""
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
DATASET_ID = "bookbot/common_voice_23_0_es"
CV_SOURCE = "common_voice_noisy"
CV_FILE_PREFIX = "c"
MIN_SENTENCE_LEN = 12
MAX_SCAN = 25_000

# (nombre, duración mín, duración máx, SNR máximo por bucket)
# A mayor duración permitimos un poco más de SNR: hay pocos clips largos y muy ruidosos.
DURATION_BUCKETS: list[tuple[str, float, float, float]] = [
    ("ruidoso_medio", 7.5, 11.5, 12.0),
    ("ruidoso_largo", 13.0, 22.0, 18.0),
]
# IDs del catálogo activo (c1 y c3; sin c2).
CV_SLOT_IDS = (1, 3)


@dataclass
class PickedClip:
    bucket: str
    file_name: str
    entry_id: str
    sentence: str
    duration_sec: float
    sentence_id: str
    up_votes: int
    down_votes: int
    snr_db: float
    accents: str


def _resample_to_16k(data: np.ndarray, sr: int) -> np.ndarray:
    if sr == TARGET_SR:
        return data.astype(np.float32)
    n = int(len(data) * TARGET_SR / sr)
    x_old = np.linspace(0, 1, len(data), endpoint=False)
    x_new = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x_new, x_old, data).astype(np.float32)


def _save_wav(path: Path, array: np.ndarray, sr: int) -> None:
    if array.ndim > 1:
        array = array.mean(axis=1)
    array = _resample_to_16k(array, sr)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), array, TARGET_SR, subtype="PCM_16")


def _decode_audio_bytes(audio_bytes: bytes) -> tuple[np.ndarray, int]:
    data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
    return data, int(sr)


def estimate_snr_db(array: np.ndarray, sr: int) -> float | None:
    """SNR aproximado piso (percentil 15) vs voz (percentil 85). Menor = más ruido."""
    if array.ndim > 1:
        array = array.mean(axis=1)
    frame_len = max(int(0.025 * sr), 1)
    hop = max(int(0.010 * sr), 1)
    rms: list[float] = []
    for start in range(0, len(array) - frame_len, hop):
        frame = array[start : start + frame_len]
        rms.append(float(np.sqrt(np.mean(frame * frame))))
    if len(rms) < 8:
        return None
    vals = np.array(rms)
    floor = float(np.percentile(vals, 15))
    peak = float(np.percentile(vals, 85))
    if peak < 1e-7:
        return None
    return 20.0 * float(np.log10(peak / max(floor, 1e-9)))


def _pick_score(snr_db: float, duration: float, down: int) -> tuple[float, float, int]:
    """Menor tupla = más ruidoso; a igual SNR, prioriza mayor duración."""
    return (snr_db, -duration, -down)


def _load_stream():
    try:
        import datasets  # noqa: F401
    except ImportError as exc:
        raise SystemExit(
            "Falta el paquete 'datasets'. Instalá con:\n  pip install datasets"
        ) from exc

    print(f"Conectando a {DATASET_ID} (train, streaming)...")
    stream = load_dataset(DATASET_ID, split="train", streaming=True)
    return stream.cast_column("audio", Audio(decode=False))


def _sentence_id(row: dict) -> str:
    return str(row.get("sentence_id") or "")


def _other_sentence_ids(best: dict, *, exclude: str) -> set[str]:
    return {_sentence_id(item[3]) for key, item in best.items() if key != exclude}


def _download_clips(*, force: bool, count: int, max_scan: int) -> list[PickedClip]:
    if count < 1 or count > len(DURATION_BUCKETS):
        raise ValueError(f"count debe estar entre 1 y {len(DURATION_BUCKETS)}")

    existing = sorted(OUTPUT_DIR.glob("c*_cv_noisy.wav"))
    if existing and not force:
        print(
            f"Ya existen {len(existing)} archivos c*_cv_noisy.wav. "
            "Usá --force para reemplazar."
        )
        return []

    buckets = DURATION_BUCKETS[:count]
    stream = _load_stream()
    # bucket -> (pick_score, duration, snr_db, row)
    best: dict[str, tuple[tuple[float, float, int], float, float, dict]] = {}
    scanned_noisy = 0

    for idx, row in enumerate(stream):
        if idx >= max_scan:
            break

        sentence = (row.get("sentence") or "").strip()
        if len(sentence) < MIN_SENTENCE_LEN:
            continue

        audio = row.get("audio") or {}
        audio_bytes = audio.get("bytes")
        if not audio_bytes:
            continue

        array, sr = _decode_audio_bytes(audio_bytes)
        duration = len(array) / sr
        snr_db = estimate_snr_db(array, sr)
        if snr_db is None:
            continue

        down = int(row.get("down_votes") or 0)

        for bucket_name, lo, hi, max_snr in buckets:
            if not (lo <= duration < hi) or snr_db > max_snr:
                continue
            scanned_noisy += 1
            score = _pick_score(snr_db, duration, down)
            if _sentence_id(row) in _other_sentence_ids(best, exclude=bucket_name):
                continue
            prev = best.get(bucket_name)
            if prev is None or score < prev[0]:
                best[bucket_name] = (score, duration, snr_db, row)

    missing = [name for name, _, _, _ in buckets if name not in best]
    if missing:
        print(f"  Fallback para buckets vacíos: {', '.join(missing)}...")
        stream2 = _load_stream()
        fallback_limits = {name: max_snr for name, _, _, max_snr in buckets}
        for idx, row in enumerate(stream2):
            if idx >= max_scan:
                break
            if not missing:
                break
            sentence = (row.get("sentence") or "").strip()
            if len(sentence) < MIN_SENTENCE_LEN:
                continue
            audio_bytes = (row.get("audio") or {}).get("bytes")
            if not audio_bytes:
                continue
            array, sr = _decode_audio_bytes(audio_bytes)
            duration = len(array) / sr
            if duration < 7.0:
                continue
            snr_db = estimate_snr_db(array, sr)
            if snr_db is None:
                continue
            down = int(row.get("down_votes") or 0)
            for bucket_name in list(missing):
                max_snr = fallback_limits[bucket_name]
                if snr_db > max_snr:
                    continue
                min_dur = 9.0 if bucket_name == "muy_largo" else 7.5
                if duration < min_dur:
                    continue
                if _sentence_id(row) in _other_sentence_ids(best, exclude=bucket_name):
                    continue
                score = _pick_score(snr_db, duration, down)
                prev = best.get(bucket_name)
                if prev is None or score < prev[0]:
                    best[bucket_name] = (score, duration, snr_db, row)
            missing = [name for name, _, _, _ in buckets if name not in best]

    missing = [name for name, _, _, _ in buckets if name not in best]
    if missing:
        raise RuntimeError(
            f"No se llenaron buckets tras {max_scan} filas (candidatos ruidosos: {scanned_noisy}). "
            f"Faltan: {', '.join(missing)}. Probá --max-scan 40000."
        )

    picked: list[PickedClip] = []
    for slot_idx, (bucket_name, _, _, max_snr_bucket) in enumerate(buckets):
        slot = CV_SLOT_IDS[slot_idx]
        _, duration, snr_db, row = best[bucket_name]
        file_name = f"{CV_FILE_PREFIX}{slot}_cv_noisy.wav"
        array, sr = _decode_audio_bytes(row["audio"]["bytes"])
        _save_wav(OUTPUT_DIR / file_name, array, sr)

        clip = PickedClip(
            bucket=bucket_name,
            file_name=file_name,
            entry_id=f"{CV_FILE_PREFIX}{slot}_cv_noisy",
            sentence=(row.get("sentence") or "").strip(),
            duration_sec=round(duration, 2),
            sentence_id=_sentence_id(row),
            up_votes=int(row.get("up_votes") or 0),
            down_votes=int(row.get("down_votes") or 0),
            snr_db=round(snr_db, 1),
            accents=str(row.get("accents") or ""),
        )
        picked.append(clip)
        print(
            f"  [{slot_idx + 1}/{count}] {bucket_name} ({duration:.1f}s, "
            f"SNR≈{clip.snr_db} dB, umbral≤{max_snr_bucket} dB, "
            f"up={clip.up_votes}, down={clip.down_votes}) -> {file_name}"
        )
        print(f"       {clip.sentence[:90]}{'...' if len(clip.sentence) > 90 else ''}")

    print(f"  (Candidatos ruidosos revisados en stream: {scanned_noisy}+)")
    return picked


def _update_catalog(clips: list[PickedClip]) -> None:
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    samples = [
        s
        for s in data.get("samples", [])
        if s.get("source") != CV_SOURCE and not str(s.get("id", "")).startswith("c")
    ]

    for clip in clips:
        samples.append(
            {
                "id": clip.entry_id,
                "file": clip.file_name,
                "language": "es",
                "source": CV_SOURCE,
                "reference_text": clip.sentence,
                "duration_sec": clip.duration_sec,
                "common_voice_sentence_id": clip.sentence_id,
                "up_votes": clip.up_votes,
                "down_votes": clip.down_votes,
                "snr_db_est": clip.snr_db,
                "accents": clip.accents or None,
                "notes": (
                    f"Common Voice 23.0 (es), espejo HF {DATASET_ID}. "
                    f"Seleccionado por SNR estimado ≈{clip.snr_db} dB y duración "
                    f"{clip.duration_sec}s (ruido de fondo audible). CC0."
                ),
            }
        )

    data["samples"] = samples
    sys.path.insert(0, str(PROJECT_ROOT))
    from common.audio_samples import CATALOG_DOC

    data["_doc"] = CATALOG_DOC
    REFERENCE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"OK catálogo: {REFERENCE_FILE.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descargar clips Common Voice (es) con ruido de fondo audible."
    )
    parser.add_argument("--force", action="store_true", help="Reemplazar c*_cv_noisy.wav.")
    parser.add_argument(
        "--count", type=int, default=2, help=f"Clips a descargar (1–{len(DURATION_BUCKETS)})."
    )
    parser.add_argument("--max-scan", type=int, default=MAX_SCAN, help="Filas máximas a revisar.")
    args = parser.parse_args()
    clips = _download_clips(force=args.force, count=args.count, max_scan=args.max_scan)
    if not clips:
        return
    _update_catalog(clips)
    print("\nListo. Escuchá los WAV en data/test_audio/ y luego:")
    print("  python -m benchmarks.stt.run_all 5")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelado.")
