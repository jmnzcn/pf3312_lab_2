"""Valida prerequisitos del proyecto antes de correr benchmarks o análisis."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.audio_samples import (
    EXPECTED_STT_IDS,
    TEST_AUDIO_DIR,
    load_audio_samples,
    validate_catalog,
    verify_wav_checksums,
)


def main() -> int:
    print("Bootstrap — validación del entorno\n")
    issues = 0

    py = sys.version_info
    print(f"Python {py.major}.{py.minor}.{py.micro} ({sys.executable})")
    if py < (3, 11):
        print("[WARN] Se recomienda Python 3.11+")
        issues += 1

    env_file = ROOT / ".env"
    if not env_file.exists():
        print("[WARN] Falta .env (copiá .env.example y agregá API keys)")
        issues += 1
    else:
        print("OK .env presente (local; no debe subirse a Git)")

    git_dir = ROOT / ".git"
    if git_dir.is_dir():
        import subprocess

        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", ".env"],
            cwd=ROOT,
            capture_output=True,
        )
        if tracked.returncode == 0:
            print("[ERROR] .env está en el índice de Git — quitálo antes del push:")
            print("        git rm --cached .env")
            issues += 1
        secrets_tracked = subprocess.run(
            ["git", "ls-files", "secrets"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if secrets_tracked.stdout.strip():
            print("[ERROR] Hay archivos en secrets/ trackeados por Git")
            issues += 1

    catalog_warnings = validate_catalog(require_wavs=False)
    if catalog_warnings:
        for w in catalog_warnings:
            print(f"[WARN] Catálogo: {w}")
            issues += 1
    else:
        print(f"OK catálogo STT ({len(EXPECTED_STT_IDS)} IDs esperados)")

    samples = load_audio_samples()
    present = [s for s in samples if s.exists()]
    print(f"Audios WAV en disco: {len(present)}/{len(samples)}")
    if len(present) < len(samples):
        missing = [s.id for s in samples if not s.exists()]
        print(f"[INFO] Faltan: {', '.join(missing[:6])}{'...' if len(missing) > 6 else ''}")
        print("       Regenerálos con scripts en data/test_audio/README.md")
    elif present:
        checksum_issues = verify_wav_checksums()
        if checksum_issues:
            for w in checksum_issues:
                print(f"[WARN] Audio: {w}")
                issues += 1
        else:
            print("OK checksums SHA-256 de audios STT")

    for sub in ("results", "data"):
        (ROOT / sub).mkdir(exist_ok=True)
    print(f"OK carpetas {TEST_AUDIO_DIR.relative_to(ROOT)} y results/")

    print("\nRutas recomendadas:")
    print("  Solo análisis (CSVs ya en results/):  python scripts/run_analysis.py")
    print("  Benchmark completo:                    python -m run_all 5")
    print("  STT con catálogo actual:               python -m benchmarks.stt.run_all 5")
    print("  E2E:                                   python -m benchmarks.pipeline.run_e2e 5")

    if issues:
        print(f"\n{issues} advertencia(s). Revisá antes del informe final.")
        return 1
    print("\nEntorno listo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
