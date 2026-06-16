import pandas as pd

from analysis.empirical_stats import (
    ci_overlap,
    detect_outliers_iqr,
    mean_ci95,
    t_critical_975,
)


def test_t_critical_975_known_values():
    assert abs(t_critical_975(4) - 2.776) < 0.001
    assert t_critical_975(120) >= 1.96


def test_mean_ci95_basic():
    s = pd.Series([100.0, 110.0, 90.0, 105.0, 95.0])
    stats = mean_ci95(s)
    assert stats["n"] == 5
    assert 95 <= stats["mean"] <= 105
    assert stats["ci_low"] < stats["mean"] < stats["ci_high"]


def test_ci_overlap():
    assert ci_overlap(10, 20, 15, 25)
    assert not ci_overlap(10, 15, 20, 30)


def test_detect_outliers_iqr():
    s = pd.Series([1, 2, 2, 3, 3, 3, 4, 4, 5, 100])
    hits = detect_outliers_iqr(s)
    assert len(hits) == 1
    assert hits[0]["value"] == 100
