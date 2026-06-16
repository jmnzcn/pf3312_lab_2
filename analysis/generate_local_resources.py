"""Tabla de RAM/CPU/GPU para modelos locales (dimensión 3)."""
from __future__ import annotations

import json
from pathlib import Path

from tabulate import tabulate

from common.paths import docs_dir, project_root, results_dir

PROJECT_ROOT = project_root()
OUT_DIR = docs_dir() / "dimensiones_datos"
SNAP = results_dir() / "hardware_snapshot.json"

# TDP de referencia (W) para estimar consumo en dimensión 3
GPU_TDP_W: dict[str, float] = {
    "Quadro P2000": 75.0,
    "NVIDIA Quadro P2000": 75.0,
}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    lines = ["# Recursos locales: escalabilidad (dimensión 3)", ""]
    if not SNAP.exists():
        lines.append("*Ejecutar `python scripts/capture_hardware.py` tras la corrida.*")
    else:
        snap = json.loads(SNAP.read_text(encoding="utf-8"))
        lines.append(
            f"- **Plataforma:** {snap.get('platform', 'n/d')}\n"
            f"- **CPU lógicos:** {snap.get('cpu_count', 'n/d')}\n"
            f"- **RAM total:** {snap.get('ram_total_gb', 'n/d')} GB "
            f"(disponible al capturar: {snap.get('ram_available_gb', 'n/d')} GB)"
        )
        gpus = snap.get("gpus") or []
        if gpus:
            lines.append("\n| GPU | VRAM total (MB) | VRAM usada (MB) | Driver |")
            lines.append("|-----|-----------------|-----------------|--------|")
            for g in gpus:
                lines.append(
                    f"| {g['name']} | {g['vram_total_mb']:.0f} | "
                    f"{g['vram_used_mb']:.0f} | {g['driver']} |"
                )
        else:
            lines.append("\n*Sin GPU NVIDIA detectada en la captura.*")
        if gpus:
            g0 = gpus[0]
            tdp = GPU_TDP_W.get(g0["name"], 75.0)
            lines.append(
                f"\n**Energía (estimada):** TDP referencia GPU ~{tdp:.0f} W "
                f"({g0['name']}). En inferencia local sostenida (faster-whisper/Ollama) "
                f"el consumo del sistema se acerca a carga GPU+CPU; no se midió wattímetro "
                f"en esta corrida; valor indicativo para comparar nube ($/llamada) vs. "
                f"estación de trabajo."
            )
        models = snap.get("local_models") or {}
        if models:
            lines.append("\n## Modelos locales evaluados\n")
            rows = [{"componente": k, "modelo": v} for k, v in models.items()]
            lines.append(tabulate(rows, headers="keys", tablefmt="github", showindex=False))
        lines.append(
            "\n*Costo API de modelos locales: $0. A cambio: latencia mayor y "
            "consumo de VRAM/RAM en esta estación de trabajo.*"
        )
    out = OUT_DIR / "recursos_locales.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"OK {out.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
