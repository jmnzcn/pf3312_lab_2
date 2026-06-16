"""IC95, outliers y comparaciones para la sección de rigor empírico."""
from __future__ import annotations

import math
from typing import Any

import pandas as pd

# Tabla t de Student (α=0.05); evita depender de scipy
_T_975: dict[int, float] = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
    15: 2.131,
    20: 2.086,
    25: 2.060,
    30: 2.042,
    40: 2.021,
    50: 2.009,
    60: 2.000,
}


def t_critical_975(df: int) -> float:
    if df <= 0:
        return float("nan")
    if df in _T_975:
        return _T_975[df]
    if df >= 120:
        return 1.980
    keys = sorted(_T_975)
    lower = max(k for k in keys if k <= df)
    upper_keys = [k for k in keys if k >= df]
    if upper_keys:
        upper = min(upper_keys)
        if lower == upper:
            return _T_975[lower]
        t_lo, t_hi = _T_975[lower], _T_975[upper]
        w = (df - lower) / (upper - lower)
        return t_lo + w * (t_hi - t_lo)
    # Interpolación entre el último valor tabulado y la aproximación normal
    t_lo = _T_975[keys[-1]]
    w = (df - keys[-1]) / (120 - keys[-1])
    return t_lo + w * (1.980 - t_lo)


def mean_ci95(series: pd.Series) -> dict[str, float | int]:
    """IC 95% de la media (t de Student), CV% y desviación estándar muestral."""
    clean = series.dropna().astype(float)
    n = int(len(clean))
    if n == 0:
        return {
            "n": 0,
            "mean": float("nan"),
            "std": float("nan"),
            "cv_pct": float("nan"),
            "ci_low": float("nan"),
            "ci_high": float("nan"),
            "sem": float("nan"),
        }
    mean = float(clean.mean())
    std = float(clean.std(ddof=1)) if n > 1 else 0.0
    sem = std / math.sqrt(n) if n > 0 else float("nan")
    margin = t_critical_975(n - 1) * sem if n > 1 else 0.0
    cv_pct = (std / mean * 100.0) if mean else float("nan")
    return {
        "n": n,
        "mean": mean,
        "std": std,
        "cv_pct": cv_pct,
        "ci_low": mean - margin,
        "ci_high": mean + margin,
        "sem": sem,
    }


def ci_overlap(low1: float, high1: float, low2: float, high2: float) -> bool:
    """Indica si dos intervalos de confianza se solapan."""
    if any(math.isnan(x) for x in (low1, high1, low2, high2)):
        return True
    return not (high1 < low2 or high2 < low1)


def detect_outliers_iqr(
    values: pd.Series,
    labels: pd.Series | None = None,
) -> list[dict[str, Any]]:
    """Detecta valores atípicos con la regla IQR × 1.5."""
    clean = values.dropna().astype(float)
    if len(clean) < 4:
        return []
    q1 = float(clean.quantile(0.25))
    q3 = float(clean.quantile(0.75))
    iqr = q3 - q1
    if iqr == 0:
        return []
    lo_fence = q1 - 1.5 * iqr
    hi_fence = q3 + 1.5 * iqr
    mask = (values < lo_fence) | (values > hi_fence)
    rows: list[dict[str, Any]] = []
    for idx in values.index[mask & values.notna()]:
        rows.append(
            {
                "label": str(labels.loc[idx]) if labels is not None else str(idx),
                "value": float(values.loc[idx]),
                "fence_low": lo_fence,
                "fence_high": hi_fence,
            }
        )
    return rows


def summarize_metric_by_provider(
    df: pd.DataFrame,
    metric_col: str,
    *,
    label_cols: list[str] | None = None,
) -> pd.DataFrame:
    """Resume n, media, desvío, CV% e IC95% por proveedor."""
    if df.empty or metric_col not in df.columns:
        return pd.DataFrame()
    label_cols = label_cols or ["test_id", "run_id"]
    rows: list[dict[str, Any]] = []
    for provider, grp in df.groupby("provider"):
        stats = mean_ci95(grp[metric_col])
        rows.append(
            {
                "provider": provider,
                "n": stats["n"],
                "mean": round(stats["mean"], 2),
                "std": round(stats["std"], 2),
                "cv_pct": round(stats["cv_pct"], 1) if stats["cv_pct"] == stats["cv_pct"] else None,
                "ci95_low": round(stats["ci_low"], 2),
                "ci95_high": round(stats["ci_high"], 2),
            }
        )
    out = pd.DataFrame(rows)
    if not out.empty:
        out = out.sort_values("mean")
    return out
