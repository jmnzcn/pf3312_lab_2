"""Benchmark TTS local con Piper (offline, sin GPU). Ver models/piper/."""
from __future__ import annotations

import os
import shutil
import subprocess
import time
from pathlib import Path

from dotenv import load_dotenv

from common.audio_samples import TTS_TEXTS
from common.base import Benchmark, BenchmarkResult
from common.benchmark_errors import mark_tts_output, provider_error
from common.metrics import elapsed_ms


load_dotenv()

OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "results" / "tts_outputs"


class PiperBenchmark(Benchmark):
    category = "tts"
    provider = "piper"
    deployment = "local"

    def __init__(self) -> None:
        project_root = Path(__file__).resolve().parent.parent.parent
        default_model = project_root / "models" / "piper" / "es_ES-davefx-medium.onnx"
        self.model_path = Path(os.getenv("PIPER_MODEL_PATH", str(default_model)))
        if not self.model_path.is_absolute():
            self.model_path = (project_root / self.model_path).resolve()
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Modelo Piper no encontrado: {self.model_path}. "
                "Ver instrucciones en el header de este archivo."
            )
        self.model = self.model_path.stem

        default_bin = project_root / "tools" / "piper" / "piper" / "piper.exe"
        piper_bin = os.getenv("PIPER_BIN") or shutil.which("piper") or shutil.which("piper.exe")
        self.piper_bin = str(Path(piper_bin) if piper_bin else default_bin)
        if not Path(self.piper_bin).exists():
            raise RuntimeError(
                f"Binario piper no encontrado: {self.piper_bin}. "
                "Instalá Piper en tools/piper/ o definí PIPER_BIN en .env."
            )
        # Piper busca espeak-ng-data en el directorio del ejecutable
        self.piper_cwd = Path(os.getenv("PIPER_CWD", Path(self.piper_bin).parent))
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    def run_single(self, test_input: dict, run_id: int) -> BenchmarkResult:
        text = test_input["text"]
        out_file = OUTPUT_DIR / f"{self.provider}_{test_input['id']}_run{run_id}.wav"

        start = time.perf_counter()
        proc = subprocess.run(
            [
                self.piper_bin,
                "-m",
                str(self.model_path),
                "-f",
                str(out_file),
            ],
            input=text,
            text=True,
            capture_output=True,
            timeout=120,
            cwd=str(self.piper_cwd),
        )
        total_ms = elapsed_ms(start)
        if proc.returncode != 0:
            stderr = proc.stderr.strip()[:200]
            raise RuntimeError(
                provider_error("piper", f"exit={proc.returncode} · stderr={stderr}", stage="tts")
            )

        result = BenchmarkResult(
            category=self.category,
            provider=self.provider,
            model=self.model,
            deployment=self.deployment,
            test_id=test_input["id"],
            run_id=run_id,
            latency_ms=total_ms,
            input_size=len(text),
            output_size=out_file.stat().st_size,
            input_unit="chars",
            output_unit="bytes",
            cost_usd=0.0,
            output_preview=str(out_file.name),
        )
        return mark_tts_output(result, out_file)


if __name__ == "__main__":
    from common.cli import run_benchmark_main

    run_benchmark_main(category="tts", factory=PiperBenchmark, test_inputs=TTS_TEXTS)
