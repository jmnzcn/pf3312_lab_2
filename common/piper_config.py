"""Rutas y binario de Piper TTS (Windows + Linux)."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_piper_paths() -> tuple[Path, Path, Path]:
    """Devuelve (piper_bin, piper_cwd, model_path)."""
    load_dotenv(PROJECT_ROOT / ".env")
    model = Path(
        os.getenv(
            "PIPER_MODEL_PATH",
            PROJECT_ROOT / "models" / "piper" / "es_ES-davefx-medium.onnx",
        )
    )
    if not model.is_absolute():
        model = (PROJECT_ROOT / model).resolve()

    bin_env = os.getenv("PIPER_BIN")
    if bin_env:
        piper_bin = Path(bin_env)
    else:
        found = shutil.which("piper") or shutil.which("piper.exe")
        piper_bin = Path(found) if found else PROJECT_ROOT / "tools" / "piper" / "piper" / "piper.exe"

    cwd = Path(os.getenv("PIPER_CWD", piper_bin.parent))
    return piper_bin, cwd, model
