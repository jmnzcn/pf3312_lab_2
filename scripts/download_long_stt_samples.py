"""Agrega audios STT largos (l1–l4) al catálogo: FLEURS, Piper, CV y ruido."""
from __future__ import annotations

import argparse
import io
import json
import subprocess
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
CV_DATASET_ID = "bookbot/common_voice_23_0_es"
GAP_SEC = 0.35

LONG_PREFIX = "l"
FLEURS_CONCAT_PARTS = ("g2_fleurs", "g4_fleurs")

LONG_PIPER_TEXT = (
    "El tutor de voz del laboratorio escucha al estudiante por el micrófono del laptop, "
    "muestra en pantalla lo que entendió y responde con audio generado. "
    "Si la red falla, la aplicación puede cambiar a un modo local que tarda más "
    "pero no envía datos afuera. "
    "En las pruebas del curso se midió el tiempo de cada paso por separado y también "
    "el turno completo, porque sumar latencias aisladas no siempre coincide con lo "
    "que siente el usuario en la sala. "
    "Por eso en el protocolo de benchmark también se registró el costo por clase de "
    "quince minutos y se comparó el error de transcripción entre grabaciones de "
    "sala y archivos sintéticos."
)

LONG_SOURCES = {
    "l1_fleurs_largo",
    "l2_piper_largo",
    "l3_cv_largo",
    "l4_noisy_largo",
}


@dataclass
class BuiltClip:
    entry_id: str
    file_name: str
    source: str
    reference_text: str
    duration_sec: float
    language: str
    notes: str
    extra: dict


def _load_catalog() -> dict:
    return json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))


def _entry_by_id(data: dict, entry_id: str) -> dict | None:
    for sample in data.get("samples", []):
        if sample.get("id") == entry_id:
            return sample
    return None


def _resample_to_16k(data: np.ndarray, sr: int) -> np.ndarray:
    if sr == TARGET_SR:
        return data.astype(np.float32)
    n = int(len(data) * TARGET_SR / sr)
    x_old = np.linspace(0, 1, len(data), endpoint=False)
    x_new = np.linspace(0, 1, n, endpoint=False)
    return np.interp(x_new, x_old, data).astype(np.float32)


def _read_wav_mono(path: Path) -> np.ndarray:
    data, sr = sf.read(str(path), dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    return _resample_to_16k(data, sr)


def _save_wav(path: Path, array: np.ndarray) -> float:
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), array, TARGET_SR, subtype="PCM_16")
    return len(array) / TARGET_SR


def _silence(seconds: float) -> np.ndarray:
    return np.zeros(int(seconds * TARGET_SR), dtype=np.float32)


def _concat_audio(parts: list[np.ndarray], gap_sec: float = GAP_SEC) -> np.ndarray:
    if not parts:
        raise ValueError("Sin fragmentos de audio")
    chunks: list[np.ndarray] = []
    gap = _silence(gap_sec)
    for idx, part in enumerate(parts):
        chunks.append(part)
        if idx < len(parts) - 1:
            chunks.append(gap)
    return np.concatenate(chunks)


def _synthesize_piper(text: str, out_wav: Path) -> None:
    from common.piper_config import get_piper_paths

    piper_bin, cwd, model = get_piper_paths()
    if not piper_bin.exists():
        raise FileNotFoundError(f"No se encontró Piper: {piper_bin}")
    if not model.exists():
        raise FileNotFoundError(f"No se encontró el modelo Piper: {model}")

    tmp = out_wav.with_suffix(".piper_tmp.wav")
    proc = subprocess.run(
        [str(piper_bin), "-m", str(model), "-f", str(tmp)],
        input=text,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=180,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:300] or "Piper falló")

    data = _read_wav_mono(tmp)
    _save_wav(out_wav, data)
    tmp.unlink(missing_ok=True)


def _decode_duration(audio_bytes: bytes) -> float:
    with sf.SoundFile(io.BytesIO(audio_bytes)) as handle:
        return len(handle) / handle.samplerate


def _decode_audio_bytes(audio_bytes: bytes) -> tuple[np.ndarray, int]:
    data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
    return data, int(sr)


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


def _pink_noise(n: int, rng: np.random.Generator) -> np.ndarray:
    white = rng.standard_normal(n)
    spectrum = np.fft.rfft(white)
    freqs = np.arange(len(spectrum)) + 1.0
    spectrum /= np.sqrt(freqs)
    noise = np.fft.irfft(spectrum, n=n)
    noise /= max(np.max(np.abs(noise)), 1e-9)
    return noise.astype(np.float32)


def _mix_at_snr(signal: np.ndarray, noise: np.ndarray, snr_db: float) -> np.ndarray:
    sig_rms = float(np.sqrt(np.mean(signal * signal)))
    noise_rms = float(np.sqrt(np.mean(noise * noise)))
    if noise_rms < 1e-9:
        return signal
    target_noise_rms = sig_rms / (10 ** (snr_db / 20.0))
    scaled = noise * (target_noise_rms / noise_rms)
    mixed = signal + scaled
    peak = float(np.max(np.abs(mixed)))
    if peak > 0.98:
        mixed *= 0.98 / peak
    return mixed.astype(np.float32)


def _clip_from_catalog_entry(entry: dict) -> BuiltClip:
    return BuiltClip(
        entry_id=entry["id"],
        file_name=entry["file"],
        source=entry["source"],
        reference_text=entry["reference_text"],
        duration_sec=float(entry["duration_sec"]),
        language=entry.get("language", "Spanish"),
        notes=entry.get("notes", ""),
        extra={
            k: v
            for k, v in entry.items()
            if k
            not in {
                "id",
                "file",
                "language",
                "source",
                "reference_text",
                "duration_sec",
                "notes",
            }
        },
    )


def build_fleurs_concat(data: dict) -> BuiltClip:
    parts_audio: list[np.ndarray] = []
    sentences: list[str] = []
    fleurs_ids: list[int] = []

    for part_id in FLEURS_CONCAT_PARTS:
        entry = _entry_by_id(data, part_id)
        if entry is None:
            raise FileNotFoundError(
                f"Falta {part_id} en el catálogo. Corré primero "
                "scripts/download_common_voice_samples.py"
            )
        wav = OUTPUT_DIR / entry["file"]
        if not wav.exists():
            raise FileNotFoundError(f"No existe {wav}")
        parts_audio.append(_read_wav_mono(wav))
        sentences.append(entry["reference_text"].strip())
        if entry.get("fleurs_id") is not None:
            fleurs_ids.append(int(entry["fleurs_id"]))

    merged = _concat_audio(parts_audio)
    out = OUTPUT_DIR / "l1_fleurs_largo.wav"
    duration = _save_wav(out, merged)
    if duration < 25.0:
        raise RuntimeError(f"l1_fleurs_largo quedó corto ({duration:.1f}s)")

    return BuiltClip(
        entry_id="l1_fleurs_largo",
        file_name=out.name,
        source="fleurs_human_concat",
        reference_text=" ".join(sentences),
        duration_sec=round(duration, 2),
        language="Spanish",
        notes=(
            "Concatenación de g2+g4 (FLEURS es_419) con pausa de 0,35 s. "
            "Voz humana leída; cubre turno largo (~30–40 s) no disponible como "
            "frase única en FLEURS. CC BY 4.0."
        ),
        extra={"fleurs_ids": fleurs_ids, "parts": list(FLEURS_CONCAT_PARTS)},
    )


def build_piper_long() -> BuiltClip:
    out = OUTPUT_DIR / "l2_piper_largo.wav"
    _synthesize_piper(LONG_PIPER_TEXT, out)
    duration = _decode_duration(out.read_bytes())
    if duration < 30.0:
        raise RuntimeError(f"l2_piper_largo quedó corto ({duration:.1f}s)")

    return BuiltClip(
        entry_id="l2_piper_largo",
        file_name=out.name,
        source="synthetic_piper_long",
        reference_text=LONG_PIPER_TEXT,
        duration_sec=round(duration, 2),
        language="es-CR",
        notes=(
            "Monólogo sintético Piper (es_ES-davefx-medium) para probar STT en "
            "párrafos de ~35–45 s. Misma limitación de sesgo que a1–a5."
        ),
        extra={},
    )


def scan_cv_longest(*, max_scan: int, min_duration: float) -> BuiltClip | None:
    print(f"Buscando CV limpio largo (≥{min_duration:.0f}s, scan≤{max_scan})...")
    stream = load_dataset(CV_DATASET_ID, split="train", streaming=True)
    stream = stream.cast_column("audio", Audio(decode=False))

    best: tuple[tuple[float, int, int], float, dict] | None = None
    for idx, row in enumerate(stream):
        if idx >= max_scan:
            break
        sentence = (row.get("sentence") or "").strip()
        if len(sentence) < 20:
            continue
        audio_bytes = (row.get("audio") or {}).get("bytes")
        if not audio_bytes:
            continue
        duration = _decode_duration(audio_bytes)
        if duration < min_duration:
            continue
        up = int(row.get("up_votes") or 0)
        down = int(row.get("down_votes") or 0)
        array, sr = _decode_audio_bytes(audio_bytes)
        snr = _estimate_snr_db(array, sr)
        if snr is None or snr < 18.0:
            continue
        score = (duration, up - down, -down)
        if best is None or score > best[0]:
            best = (score, duration, row)

    if best is None:
        print("  No se encontró CV limpio ≥ umbral; se omite l3_cv_largo.")
        return None

    _, duration, row = best
    out = OUTPUT_DIR / "l3_cv_largo.wav"
    array, sr = _decode_audio_bytes(row["audio"]["bytes"])
    if array.ndim > 1:
        array = array.mean(axis=1)
    duration = _save_wav(out, _resample_to_16k(array, sr))
    sentence = (row.get("sentence") or "").strip()

    return BuiltClip(
        entry_id="l3_cv_largo",
        file_name=out.name,
        source="common_voice_long",
        reference_text=sentence,
        duration_sec=round(duration, 2),
        language="es",
        notes=(
            f"Common Voice 23.0 (es), clip limpio más largo encontrado "
            f"(SNR estimado alto, duración {duration:.1f}s). CC0."
        ),
        extra={
            "common_voice_sentence_id": str(row.get("sentence_id") or ""),
            "up_votes": int(row.get("up_votes") or 0),
            "down_votes": int(row.get("down_votes") or 0),
            "snr_db_est": round(_estimate_snr_db(array, sr) or 0.0, 1),
            "accents": row.get("accents"),
        },
    )


def build_noisy_long(
    base_wav: Path,
    *,
    reference_text: str,
    snr_db: float,
    seed: int,
) -> BuiltClip:
    signal = _read_wav_mono(base_wav)
    rng = np.random.default_rng(seed)
    noise = _pink_noise(len(signal), rng)
    mixed = _mix_at_snr(signal, noise, snr_db)
    out = OUTPUT_DIR / "l4_noisy_largo.wav"
    duration = _save_wav(out, mixed)

    return BuiltClip(
        entry_id="l4_noisy_largo",
        file_name=out.name,
        source="synthetic_noisy_long",
        reference_text=reference_text,
        duration_sec=round(duration, 2),
        language="Spanish",
        notes=(
            f"Mezcla sintética sobre l1_fleurs_largo: ruido rosa a SNR objetivo "
            f"{snr_db:.0f} dB (semilla {seed}). Complementa CV noisy en turnos largos."
        ),
        extra={"snr_db_target": snr_db, "base_id": "l1_fleurs_largo", "noise_type": "pink"},
    )


def _clip_to_entry(clip: BuiltClip) -> dict:
    entry = {
        "id": clip.entry_id,
        "file": clip.file_name,
        "language": clip.language,
        "source": clip.source,
        "reference_text": clip.reference_text,
        "duration_sec": clip.duration_sec,
        "notes": clip.notes,
    }
    entry.update(clip.extra)
    return entry


def _update_catalog(clips: list[BuiltClip]) -> None:
    data = _load_catalog()
    samples = [s for s in data.get("samples", []) if s.get("id") not in LONG_SOURCES]
    samples.extend(_clip_to_entry(c) for c in clips)
    data["samples"] = samples
    from common.audio_samples import CATALOG_DOC

    data["_doc"] = CATALOG_DOC
    REFERENCE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK catálogo: {REFERENCE_FILE.relative_to(PROJECT_ROOT)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generar audios STT largos (l1–l4).")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reconstruir l1/l2/l4 aunque ya existan (l1 pasa a g2+g4 de dos segmentos).",
    )
    parser.add_argument(
        "--skip-cv-scan",
        action="store_true",
        help="No buscar l3_cv_largo en Common Voice (más rápido).",
    )
    parser.add_argument("--max-scan", type=int, default=25_000, help="Filas CV a revisar.")
    parser.add_argument(
        "--min-cv-duration",
        type=float,
        default=18.0,
        help="Duración mínima para l3_cv_largo.",
    )
    parser.add_argument("--snr-db", type=float, default=14.0, help="SNR para l4_noisy_largo.")
    args = parser.parse_args()

    data = _load_catalog()
    clips: list[BuiltClip] = []

    l1_path = OUTPUT_DIR / "l1_fleurs_largo.wav"
    l1_entry = _entry_by_id(data, "l1_fleurs_largo")
    if l1_path.exists() and l1_entry and not args.force:
        print("1/4 l1_fleurs_largo ya existe; omitiendo (--force para reconstruir g2+g4).")
        l1 = _clip_from_catalog_entry(l1_entry)
        print(f"     {l1.duration_sec}s -> {l1.file_name}")
    else:
        print("1/4 Concatenando FLEURS (l1_fleurs_largo)...")
        l1 = build_fleurs_concat(data)
        print(f"     {l1.duration_sec}s -> {l1.file_name}")
    clips.append(l1)

    l2_path = OUTPUT_DIR / "l2_piper_largo.wav"
    if l2_path.exists() and not args.force:
        l2_entry = _entry_by_id(data, "l2_piper_largo")
        if l2_entry:
            print("2/4 l2_piper_largo ya existe; omitiendo.")
            l2 = _clip_from_catalog_entry(l2_entry)
            print(f"     {l2.duration_sec}s -> {l2.file_name}")
        else:
            print("2/4 Sintetizando Piper largo (l2_piper_largo)...")
            l2 = build_piper_long()
            print(f"     {l2.duration_sec}s -> {l2.file_name}")
    else:
        print("2/4 Sintetizando Piper largo (l2_piper_largo)...")
        l2 = build_piper_long()
        print(f"     {l2.duration_sec}s -> {l2.file_name}")
    clips.append(l2)

    if not args.skip_cv_scan:
        print("3/4 Escaneando Common Voice (l3_cv_largo)...")
        l3 = scan_cv_longest(max_scan=args.max_scan, min_duration=args.min_cv_duration)
        if l3 is not None:
            clips.append(l3)
            print(f"     {l3.duration_sec}s -> {l3.file_name}")
    else:
        print("3/4 CV scan omitido (--skip-cv-scan).")

    l4_path = OUTPUT_DIR / "l4_noisy_largo.wav"
    if l4_path.exists() and not args.force:
        l4_entry = _entry_by_id(data, "l4_noisy_largo")
        if l4_entry:
            print(f"4/4 l4_noisy_largo ya existe; omitiendo.")
            l4 = _clip_from_catalog_entry(l4_entry)
            print(f"     {l4.duration_sec}s -> {l4.file_name}")
        else:
            print(f"4/4 Mezclando ruido largo (l4_noisy_largo, SNR {args.snr_db:.0f} dB)...")
            l4 = build_noisy_long(
                OUTPUT_DIR / l1.file_name,
                reference_text=l1.reference_text,
                snr_db=args.snr_db,
                seed=42,
            )
            print(f"     {l4.duration_sec}s -> {l4.file_name}")
    else:
        print(f"4/4 Mezclando ruido largo (l4_noisy_largo, SNR {args.snr_db:.0f} dB)...")
        l4 = build_noisy_long(
            OUTPUT_DIR / l1.file_name,
            reference_text=l1.reference_text,
            snr_db=args.snr_db,
            seed=42,
        )
        print(f"     {l4.duration_sec}s -> {l4.file_name}")
    clips.append(l4)

    _update_catalog(clips)
    print("\nListo. Siguiente paso:")
    print("  python -m benchmarks.stt.run_all 5")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit("\nCancelado.")
