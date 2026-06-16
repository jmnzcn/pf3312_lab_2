"""run_batch_id compartido entre runners y CSV."""
from __future__ import annotations

import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from common.paths import manifest_path, project_root

PROJECT_ROOT = project_root()

_current_batch_id: str | None = None


def start_run_batch(*, runs_per_input: int = 5, note: str = "", force: bool = False) -> str:
    """Inicia una corrida y persiste manifiesto en results/run_manifest.json."""
    global _current_batch_id
    if _current_batch_id is not None and not force:
        return _current_batch_id
    _current_batch_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest: dict[str, Any] = {
        "run_batch_id": _current_batch_id,
        "started_at": _current_batch_id,
        "runs_per_input": runs_per_input,
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "note": note,
    }
    try:
        from common.audio_samples import catalog_fingerprint, load_catalog_data

        manifest["catalog_fingerprint"] = catalog_fingerprint()
        manifest["stt_sample_count"] = len(load_catalog_data().get("samples", []))
    except Exception:
        pass
    path = manifest_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return _current_batch_id


def ensure_run_batch(*, runs_per_input: int = 5, note: str = "") -> str:
    """Reutiliza el batch activo o crea uno nuevo (pipeline run_all + sub-runners)."""
    global _current_batch_id
    path = manifest_path()
    existing = current_batch_id()
    if existing:
        _current_batch_id = existing
        if path.exists():
            manifest = load_manifest()
            if note:
                manifest["note"] = note
            if "e2e" not in note.lower():
                manifest["runs_per_input"] = runs_per_input
            path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
        return existing
    return start_run_batch(runs_per_input=runs_per_input, note=note)


def current_batch_id() -> str | None:
    path = manifest_path()
    if _current_batch_id:
        return _current_batch_id
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("run_batch_id")
    return None


def load_manifest() -> dict[str, Any]:
    path = manifest_path()
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
