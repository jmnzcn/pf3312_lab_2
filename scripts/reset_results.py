"""Archiva CSV de results/ para empezar una corrida limpia."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from common.results import archive_results_csv
from common.run_context import start_run_batch


def main() -> None:
    moved = archive_results_csv()
    if not moved:
        print("No había CSV que archivar.")
    else:
        for p in moved:
            print(f"Archivado: {p.relative_to(ROOT)}")
    bid = start_run_batch(note="post-reset", force=True)
    print(f"Nueva corrida: {bid}")


if __name__ == "__main__":
    main()
