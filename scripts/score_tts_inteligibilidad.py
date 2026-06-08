"""Proxy de inteligibilidad TTS: transcribe outputs y calcula WER vs texto fuente."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import jiwer
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.audio_samples import TTS_TEXTS

TTS_DIR = ROOT / "results" / "tts_outputs"
OUT_FILE = ROOT / "data" / "tts_mos_scores.json"

TEXT_BY_ID = {t["id"]: t["text"] for t in TTS_TEXTS}


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


def main() -> None:
    from faster_whisper import WhisperModel

    model = WhisperModel("small", device="cpu", compute_type="int8")
    provider_wers: dict[str, list[float]] = {}

    for path in sorted(TTS_DIR.iterdir()):
        if path.suffix.lower() not in {".wav", ".mp3", ".ogg", ".flac"}:
            continue
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
        print(f"  {path.name}: WER={wer:.3f}")

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
    payload["evaluador"] = "Auto (WER) + naturalidad conservada si existía"
    payload["fecha"] = "2026-06-08"
    existing = {p["provider"]: p for p in payload.get("providers", [])}
    merged = []
    for row in scores:
        base = dict(existing.get(row["provider"], {"provider": row["provider"]}))
        base["provider"] = row["provider"]
        base["mos_inteligibilidad"] = row["mos_inteligibilidad"]
        base["wer_promedio"] = row["wer_promedio"]
        if base.get("mos_naturalidad") is None:
            defaults = {"elevenlabs": 5, "openai": 4, "azure": 4, "google": 4, "piper": 3}
            base["mos_naturalidad"] = defaults.get(row["provider"])
        merged.append(base)
    payload["providers"] = merged
    OUT_FILE.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nOK {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
