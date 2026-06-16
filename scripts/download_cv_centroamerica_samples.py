"""Descarga voz centroamericana desde Common Voice 23.0 (r1, r2)."""
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
sys.path.insert(0, str(PROJECT_ROOT))

REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "test_audio"
TARGET_SR = 16_000
DATASET_ID = "bookbot/common_voice_23_0_es"
CV_SOURCE = "common_voice_central_america"
ACCENT_NEEDLE = "américa central"
GAP_SEC = 0.35
MAX_SCAN = 40_000
REGION_IDS = {"r1_cv_centroamerica", "r2_cv_centroamerica_largo"}


@dataclass
class Candidate:
    duration: float
    snr_db: float
    score: tuple[float, float, int]
    row: dict
    stream_index: int


@dataclass
class BuiltClip:
    entry_id: str
    file_name: str
    reference_text: str
    duration_sec: float
    notes: str
    extra: dict


def _is_central_america(accent: str) -> bool:
    low = accent.lower().replace("america", "américa")
    return ACCENT_NEEDLE in low


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


def _save_wav(path: Path, array: np.ndarray) -> float:
    if array.ndim > 1:
        array = array.mean(axis=1)
    array = _resample_to_16k(array, TARGET_SR)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), array, TARGET_SR, subtype="PCM_16")
    return len(array) / TARGET_SR


def _silence(seconds: float) -> np.ndarray:
    return np.zeros(int(seconds * TARGET_SR), dtype=np.float32)


def _concat_audio(parts: list[np.ndarray], gap_sec: float = GAP_SEC) -> np.ndarray:
    chunks: list[np.ndarray] = []
    gap = _silence(gap_sec)
    for idx, part in enumerate(parts):
        chunks.append(part)
        if idx < len(parts) - 1:
            chunks.append(gap)
    return np.concatenate(chunks)


def _estimate_snr_db(array: np.ndarray, sr: int) -> float | None:
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


def _sentence_id(row: dict) -> str:
    return str(row.get("sentence_id") or "")


def _pick_score(duration: float, snr_db: float, up: int, down: int) -> tuple[float, float, int]:
    return (duration, snr_db, up - down)


def _scan_candidates(*, max_scan: int) -> list[Candidate]:
    print(f"Escaneando {DATASET_ID} (acento América central, ≤{max_scan} filas)...")
    stream = load_dataset(DATASET_ID, split="train", streaming=True)
    stream = stream.cast_column("audio", Audio(decode=False))

    candidates: list[Candidate] = []
    for idx, row in enumerate(stream):
        if idx >= max_scan:
            break
        accent = (row.get("accents") or "").strip()
        if not _is_central_america(accent):
            continue
        sentence = (row.get("sentence") or "").strip()
        if len(sentence) < 12:
            continue
        audio_bytes = (row.get("audio") or {}).get("bytes")
        if not audio_bytes:
            continue

        array, sr = _decode_audio_bytes(audio_bytes)
        duration = len(array) / sr
        if duration < 6.5:
            continue
        snr_db = _estimate_snr_db(array, sr)
        if snr_db is None or snr_db < 16.0:
            continue
        up = int(row.get("up_votes") or 0)
        down = int(row.get("down_votes") or 0)
        if up < 2:
            continue

        candidates.append(
            Candidate(
                duration=duration,
                snr_db=snr_db,
                score=_pick_score(duration, snr_db, up, down),
                row=row,
                stream_index=idx,
            )
        )

    if not candidates:
        raise RuntimeError(
            "No se encontraron clips América central con SNR≥16 y up_votes≥2. "
            "Probá --max-scan 60000."
        )
    candidates.sort(key=lambda c: c.score, reverse=True)
    print(f"  Candidatos válidos: {len(candidates)}")
    return candidates


def _candidate_to_arrays(
    picks: list[Candidate],
) -> tuple[list[np.ndarray], list[str], list[str]]:
    arrays: list[np.ndarray] = []
    sentences: list[str] = []
    sentence_ids: list[str] = []
    for pick in picks:
        audio_bytes = pick.row["audio"]["bytes"]
        array, sr = _decode_audio_bytes(audio_bytes)
        if array.ndim > 1:
            array = array.mean(axis=1)
        arrays.append(_resample_to_16k(array, sr))
        sentences.append((pick.row.get("sentence") or "").strip())
        sentence_ids.append(_sentence_id(pick.row))
    return arrays, sentences, sentence_ids


def _build_single(candidates: list[Candidate]) -> BuiltClip:
    pick = candidates[0]
    arrays, sentences, sentence_ids = _candidate_to_arrays([pick])
    out = OUTPUT_DIR / "r1_cv_centroamerica.wav"
    duration = _save_wav(out, arrays[0])
    accent = (pick.row.get("accents") or "").strip()

    return BuiltClip(
        entry_id="r1_cv_centroamerica",
        file_name=out.name,
        reference_text=sentences[0],
        duration_sec=round(duration, 2),
        notes=(
            "Common Voice 23.0 (es), acento autodeclarado América central "
            f"(proxy centroamericano / es-CR; SNR≈{pick.snr_db:.1f} dB). "
            "No sustituye grabación costarricense del investigador. CC0."
        ),
        extra={
            "language": "es",
            "source": CV_SOURCE,
            "accents": accent,
            "common_voice_sentence_id": sentence_ids[0],
            "up_votes": int(pick.row.get("up_votes") or 0),
            "down_votes": int(pick.row.get("down_votes") or 0),
            "snr_db_est": round(pick.snr_db, 1),
        },
    )


def _build_long(candidates: list[Candidate], *, min_total_sec: float) -> BuiltClip:
    used_ids: set[str] = set()
    picks: list[Candidate] = []

    for cand in candidates:
        sid = _sentence_id(cand.row)
        if sid in used_ids:
            continue
        picks.append(cand)
        used_ids.add(sid)
        total = sum(p.duration for p in picks) + max(0, len(picks) - 1) * GAP_SEC
        if len(picks) >= 3 and total >= min_total_sec:
            break
        if len(picks) >= 4:
            break

    total = sum(p.duration for p in picks) + max(0, len(picks) - 1) * GAP_SEC
    if len(picks) < 3 or total < min_total_sec:
        raise RuntimeError(
            f"No alcanzaron {min_total_sec:.0f}s con clips América central "
            f"(solo {len(picks)} clips, ~{total:.1f}s)."
        )

    arrays, sentences, sentence_ids = _candidate_to_arrays(picks)
    merged = _concat_audio(arrays)
    out = OUTPUT_DIR / "r2_cv_centroamerica_largo.wav"
    duration = _save_wav(out, merged)
    accent = (picks[0].row.get("accents") or "").strip()

    return BuiltClip(
        entry_id="r2_cv_centroamerica_largo",
        file_name=out.name,
        reference_text=" ".join(sentences),
        duration_sec=round(duration, 2),
        notes=(
            f"Concatenación de {len(picks)} clips CV América central "
            f"(pausa {GAP_SEC}s). Proxy de voz humana centroamericana larga "
            f"(~{duration:.0f}s); CV no publica frases únicas >11s en este acento. CC0."
        ),
        extra={
            "language": "es",
            "source": CV_SOURCE,
            "accents": accent,
            "common_voice_sentence_ids": sentence_ids,
            "parts_count": len(picks),
            "snr_db_est_avg": round(
                sum(p.snr_db for p in picks) / len(picks), 1
            ),
        },
    )


def _clip_to_entry(clip: BuiltClip) -> dict:
    entry = {
        "id": clip.entry_id,
        "file": clip.file_name,
        "reference_text": clip.reference_text,
        "duration_sec": clip.duration_sec,
        "notes": clip.notes,
    }
    entry.update(clip.extra)
    return entry


def _update_catalog(clips: list[BuiltClip]) -> None:
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    samples = [s for s in data.get("samples", []) if s.get("id") not in REGION_IDS]
    samples.extend(_clip_to_entry(c) for c in clips)
    data["samples"] = samples
    sys.path.insert(0, str(PROJECT_ROOT))
    from common.audio_samples import CATALOG_DOC

    data["_doc"] = CATALOG_DOC
    REFERENCE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK catálogo: {REFERENCE_FILE.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Descargar clips Common Voice con acento América central (proxy CR)."
    )
    parser.add_argument("--force", action="store_true", help="Reemplazar r1/r2 existentes.")
    parser.add_argument("--max-scan", type=int, default=MAX_SCAN)
    parser.add_argument(
        "--min-total-sec",
        type=float,
        default=30.0,
        help="Duración mínima objetivo para r2_cv_centroamerica_largo.",
    )
    args = parser.parse_args()

    existing = [OUTPUT_DIR / "r1_cv_centroamerica.wav", OUTPUT_DIR / "r2_cv_centroamerica_largo.wav"]
    if any(p.exists() for p in existing) and not args.force:
        print("Ya existen r1/r2. Usá --force para reemplazar.")
        return

    candidates = _scan_candidates(max_scan=args.max_scan)

    print("1/2 Mejor clip suelto (r1_cv_centroamerica)...")
    r1 = _build_single(candidates)
    print(f"     {r1.duration_sec}s — {r1.reference_text[:80]}...")

    print("2/2 Concatenación larga (r2_cv_centroamerica_largo)...")
    r2 = _build_long(candidates, min_total_sec=args.min_total_sec)
    print(f"     {r2.duration_sec}s — {r2.extra['parts_count']} partes")

    _update_catalog([r1, r2])
    print("\nListo. Siguiente paso:")
    print("  python -m benchmarks.stt.run_all 5")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelado.")
