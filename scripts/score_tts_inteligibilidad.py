"""Recalcula MOS de inteligibilidad TTS (WER round-trip con STT)."""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import jiwer
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.audio_samples import TTS_TEXTS

TTS_DIR = ROOT / "results" / "tts_outputs"
OUT_FILE = ROOT / "data" / "tts_mos_scores.json"
NOTAS_FILE = ROOT / "data" / "tts_mos_notas.json"

TEXT_BY_ID = {t["id"]: t["text"] for t in TTS_TEXTS}
AUDIO_SUFFIXES = {".wav", ".mp3", ".ogg", ".flac"}


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sáéíóúñü]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _load_audio(path: Path):
    import numpy as np

    data, sr = sf.read(str(path), dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != 16_000:
        n = int(len(data) * 16_000 / sr)
        data = np.interp(
            np.linspace(0, 1, n),
            np.linspace(0, 1, len(data)),
            data,
        ).astype(np.float32)
        sr = 16_000
    return data, sr


def wer_to_mos(wer: float) -> int:
    if wer <= 0.05:
        return 5
    if wer <= 0.10:
        return 4
    if wer <= 0.20:
        return 3
    if wer <= 0.35:
        return 2
    return 1


def _benchmark_audio_files() -> list[Path]:
    """Solo audios del benchmark TTS (t1-t5), no los de pipeline E2E."""
    if not TTS_DIR.is_dir():
        return []
    out: list[Path] = []
    for p in TTS_DIR.iterdir():
        if p.suffix.lower() not in AUDIO_SUFFIXES:
            continue
        parts = p.stem.split("_")
        if len(parts) < 4:
            continue
        text_id = "_".join(parts[1:-1])
        if text_id in TEXT_BY_ID:
            out.append(p)
    return sorted(out)


def _needs_recompute(*, force: bool) -> bool:
    if force or not OUT_FILE.exists():
        return True
    newest_audio = max((p.stat().st_mtime for p in _benchmark_audio_files()), default=0.0)
    if newest_audio <= 0:
        return False
    return OUT_FILE.stat().st_mtime < newest_audio


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recalcula MOS de inteligibilidad TTS (Whisper CPU, lento)."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recalcular aunque tts_mos_scores.json esté al día.",
    )
    args = parser.parse_args()

    files = _benchmark_audio_files()
    if not files:
        print(
            f"[WARN] No hay audios en {TTS_DIR.relative_to(ROOT)}. "
            "Corré primero el benchmark TTS: python -m benchmarks.tts.run_all 5"
        )
        raise SystemExit(0)

    if not OUT_FILE.exists() and not args.force:
        print(
            f"[WARN] No existe {OUT_FILE.relative_to(ROOT)}; la Sección 3.0.5 del informe "
            "no tendrá tabla MOS hasta que lo generes."
        )
        print("       python scripts/score_tts_inteligibilidad.py --force")
        return

    if _needs_recompute(force=False) and not args.force:
        print(
            f"[WARN] Hay audios TTS más nuevos que {OUT_FILE.relative_to(ROOT)}. "
            "El informe seguirá usando los MOS guardados (inteligibilidad puede estar desactualizada)."
        )
        print("       Para recalcular con Whisper (lento): python scripts/run_analysis.py --with-optional")
        return

    if not _needs_recompute(force=args.force):
        print(
            f"OK {OUT_FILE.relative_to(ROOT)} (sin cambios en TTS; "
            "usá --force para recalcular)"
        )
        return

    print(
        f"[INFO] Transcribiendo {len(files)} audios de benchmark TTS (t1-t5) con faster-whisper (CPU). "
        "Puede tardar varios minutos; la primera carga del modelo también tarda."
    )
    t0 = time.perf_counter()
    from faster_whisper import WhisperModel

    model = WhisperModel("small", device="cpu", compute_type="int8")
    print(f"[INFO] Modelo cargado en {time.perf_counter() - t0:.1f} s. Procesando…")
    provider_wers: dict[str, list[float]] = {}

    for i, path in enumerate(files, 1):
        parts = path.stem.split("_")
        if len(parts) < 4:
            continue
        provider = parts[0]
        text_id = "_".join(parts[1:-1])  # t1_saludo_corto
        if text_id not in TEXT_BY_ID:
            continue
        ref = _normalize(TEXT_BY_ID[text_id])
        audio, sr = _load_audio(path)
        segments, _ = model.transcribe(audio, language="es", beam_size=1)
        hyp = _normalize(" ".join(s.text for s in segments))
        wer = jiwer.wer(ref, hyp) if ref else 1.0
        provider_wers.setdefault(provider, []).append(wer)
        if i == 1 or i % 25 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] {path.name}: WER={wer:.3f}")

    scores = []
    for prov in sorted(provider_wers):
        avg = sum(provider_wers[prov]) / len(provider_wers[prov])
        scores.append(
            {
                "provider": prov,
                "mos_inteligibilidad": wer_to_mos(avg),
                "mos_naturalidad": None,
                "wer_promedio": round(avg, 4),
                "muestras": len(provider_wers[prov]),
            }
        )

    payload = json.loads(OUT_FILE.read_text(encoding="utf-8")) if OUT_FILE.exists() else {}
    for prov_row in payload.get("providers", []):
        prov_row.pop("nota", None)
    if not payload.get("evaluador") or "Auto" in str(payload.get("evaluador", "")):
        payload["evaluador"] = "Ney Fred Jiménez Campos (B03230)"
    if not payload.get("metodo"):
        payload["metodo"] = (
            "Inteligibilidad vía WER (STT sobre audio sintetizado). "
            "Naturalidad: escucha de t2_oracion_media_run1 por proveedor, escala 1-5."
        )
    payload.setdefault("fecha", "2026-06-08")
    existing = {p["provider"]: p for p in payload.get("providers", [])}
    merged = []
    for row in scores:
        base = dict(existing.get(row["provider"], {"provider": row["provider"]}))
        base.pop("nota", None)
        base["provider"] = row["provider"]
        base["wer_promedio"] = row["wer_promedio"]
        if base.get("mos_inteligibilidad") is None:
            base["mos_inteligibilidad"] = row["mos_inteligibilidad"]
        if base.get("mos_naturalidad") is None:
            defaults = {"elevenlabs": 5, "openai": 4, "azure": 4, "google": 4, "piper": 3}
            base["mos_naturalidad"] = defaults.get(row["provider"])
        merged.append(base)
    payload["providers"] = merged
    OUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    elapsed = time.perf_counter() - t0
    print(f"\nOK {OUT_FILE.relative_to(ROOT)} ({elapsed:.0f} s, {len(files)} audios)")


if __name__ == "__main__":
    main()
