"""Captura RAM/CPU/GPU y la anexa al manifiesto de corrida."""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.run_context import MANIFEST_PATH, load_manifest


def _gpu_info() -> list[dict]:
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.used,driver_version",
                "--format=csv,noheader,nounits",
            ],
            text=True,
            timeout=10,
        )
    except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        return []
    rows = []
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) >= 4:
            rows.append(
                {
                    "name": parts[0],
                    "vram_total_mb": float(parts[1]),
                    "vram_used_mb": float(parts[2]),
                    "driver": parts[3],
                }
            )
    return rows


def capture() -> dict:
    import psutil

    vm = psutil.virtual_memory()
    payload = {
        "platform": platform.platform(),
        "cpu_count": psutil.cpu_count(logical=True),
        "ram_total_gb": round(vm.total / (1024**3), 2),
        "ram_available_gb": round(vm.available / (1024**3), 2),
        "gpus": _gpu_info(),
        "local_models": {
            "ollama": "llama3.2:3b",
            "faster_whisper": "large-v3 int8_float16",
            "piper": "es_ES-davefx-medium",
        },
    }
    return payload


def main() -> None:
    snap = capture()
    out = ROOT / "results" / "hardware_snapshot.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snap, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = load_manifest()
    if manifest:
        manifest["hardware"] = snap
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"OK {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
