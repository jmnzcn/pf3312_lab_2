"""Calcula o verifica sha256 de los WAV STT en reference_transcriptions.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.audio_samples import (  # noqa: E402
    REFERENCE_FILE,
    TEST_AUDIO_DIR,
    verify_wav_checksums,
    wav_sha256,
)


def write_checksums() -> int:
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))
    updated = 0
    for entry in data.get("samples", []):
        wav = TEST_AUDIO_DIR / entry.get("file", "")
        if not wav.exists():
            print(f"[SKIP] Falta {wav.name} ({entry.get('id')})")
            continue
        entry["sha256"] = wav_sha256(wav)
        updated += 1
    REFERENCE_FILE.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"OK sha256 actualizado en {updated} entradas → {REFERENCE_FILE.relative_to(ROOT)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true", help="Escribir sha256 al catálogo JSON")
    group.add_argument("--verify", action="store_true", help="Verificar WAV vs. catálogo")
    args = parser.parse_args()

    if args.write:
        return write_checksums()

    issues = verify_wav_checksums()
    if issues:
        for msg in issues:
            print(f"[ERROR] {msg}")
        print(f"\nFALLÓ · {len(issues)} problema(s). Ejecutá --write si regeneraste audios.")
        return 1
    print(f"OK {REFERENCE_FILE.relative_to(ROOT)} · checksums coinciden")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
