from analysis.dimensions_catalog import QUALITATIVE, service_ids, validate_qualitative_catalog
from common.benchmark_registry import BENCHMARK_REGISTRY


def test_qualitative_catalog_aligned_with_registry():
    validate_qualitative_catalog()
    assert len(QUALITATIVE) == len(BENCHMARK_REGISTRY) == 15


def test_qualitative_service_ids_follow_registry_order():
    assert service_ids() == [f"{s.category}/{s.provider}" for s in BENCHMARK_REGISTRY]
