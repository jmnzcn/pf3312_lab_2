from common.rates import (
    AZURE_STT_USD_PER_MIN,
    DEEPGRAM_NOVA3_USD_PER_MIN,
    LLM_PRICING_ROWS,
    OPENAI_GPT4O_INPUT_PER_M,
    STT_PRICING_ROWS,
    TTS_PRICING_ROWS,
)


def test_llm_pricing_matches_constants():
    openai = next(r for r in LLM_PRICING_ROWS if r["proveedor"] == "openai")
    assert openai["usd_input_M_tokens"] == OPENAI_GPT4O_INPUT_PER_M


def test_stt_pricing_matches_constants():
    deepgram = next(r for r in STT_PRICING_ROWS if r["proveedor"] == "deepgram")
    assert deepgram["usd_minuto"] == DEEPGRAM_NOVA3_USD_PER_MIN
    azure = next(r for r in STT_PRICING_ROWS if r["proveedor"] == "azure")
    assert azure["usd_minuto"] == AZURE_STT_USD_PER_MIN


def test_pricing_tables_have_five_providers_each():
    assert len(LLM_PRICING_ROWS) == 5
    assert len(STT_PRICING_ROWS) == 5
    assert len(TTS_PRICING_ROWS) == 5
