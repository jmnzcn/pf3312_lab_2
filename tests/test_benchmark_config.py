from common.benchmark_config import (
    category_row_count,
    llm_input_count,
    stt_input_count,
    tts_input_count,
)


def test_input_counts_match_protocol():
    assert llm_input_count() == 5
    assert tts_input_count() == 5
    assert stt_input_count() == 14


def test_category_row_count_default_runs():
    assert category_row_count("llm") == 25
    assert category_row_count("tts") == 25
    assert category_row_count("stt") == 70
