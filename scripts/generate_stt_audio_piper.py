"""Genera WAV de STT con Piper para entradas marcadas como synthetic_piper.

Uso:
    python scripts/generate_stt_audio_piper.py

Solo procesa muestras con "source": "synthetic_piper" en reference_transcriptions.json.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import soundfile as sf


PROJECT_ROOT = Path(__file__).resolve().parent.parent
REFERENCE_FILE = PROJECT_ROOT / "data" / "reference_transcriptions.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "test_audio"
TARGET_SR = 16_000


def _piper_paths() -> tuple[Path, Path, Path]:
    from common.piper_config import get_piper_paths

    return get_piper_paths()


def synthesize(piper_bin: Path, cwd: Path, model: Path, text: str, out_wav: Path) -> None:
    tmp = out_wav.with_suffix(".piper_tmp.wav")
    proc = subprocess.run(
        [str(piper_bin), "-m", str(model), "-f", str(tmp)],
        input=text,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=120,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip()[:300] or "Piper falló")
    data, sr = sf.read(str(tmp), dtype="float32")
    if data.ndim > 1:
        data = data.mean(axis=1)
    if sr != TARGET_SR:
        import numpy as np

        duration = len(data) / sr
        n = int(duration * TARGET_SR)
        x_old = np.linspace(0, 1, len(data), endpoint=False)
        x_new = np.linspace(0, 1, n, endpoint=False)
        data = np.interp(x_new, x_old, data).astype(np.float32)
        sr = TARGET_SR
    sf.write(str(out_wav), data, sr, subtype="PCM_16")
    tmp.unlink(missing_ok=True)


def main() -> None:
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    piper_bin, cwd, model = _piper_paths()
    if not piper_bin.exists():
        sys.exit(f"No se encontró Piper: {piper_bin}")
    if not model.exists():
        sys.exit(f"No se encontró el modelo: {model}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    done = 0
    for entry in data.get("samples", []):
        if entry.get("source") != "synthetic_piper":
            continue
        out = OUTPUT_DIR / entry["file"]
        print(f"  {entry['id']} -> {out.name}")
        synthesize(piper_bin, cwd, model, entry["reference_text"], out)
        done += 1

    print(f"OK: {done} archivos en {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
