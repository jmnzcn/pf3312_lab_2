from analysis.evaluate_llm_quality import (
    _valid_p3_json,
    evaluate_json_prompt,
)

VALID_JSON = (
    '{"agentes":['
    '{"nombre":"A","estilo":"realista","rol":"asistente","expresiones":["sonrisa"]},'
    '{"nombre":"B","estilo":"cartoon","rol":"guia","expresiones":["alegre"]},'
    '{"nombre":"C","estilo":"caricaturesco","rol":"tutor","expresiones":["serio"]}'
    "]}"
)

INVALID_ARRAY_ROOT = (
    '[{"nombre":"A","estilo":"realista","rol":"x","expresiones":["a"]},'
    '{"nombre":"B","estilo":"cartoon","rol":"y","expresiones":["b"]}]'
)


def test_valid_p3_json_accepts_full_payload():
    assert _valid_p3_json(VALID_JSON)


def test_valid_p3_json_rejects_array_with_two_agents():
    assert not _valid_p3_json(INVALID_ARRAY_ROOT)


def test_evaluate_json_prompt_uses_output_text():
    records = [
        {
            "provider": "openai",
            "test_id": "p3_json_estricto",
            "error": None,
            "output_text": VALID_JSON,
            "output_preview": '{"agentes":[{"nombre":"trunc',
            "output_size": 200,
        },
        {
            "provider": "google",
            "test_id": "p3_json_estricto",
            "error": None,
            "output_text": "",
            "output_preview": '{"agentes":[{"nombre":"A","estilo":"realista","rol":"x","expresiones":["a"]}',
            "output_size": 50,
        },
    ]
    rows = {r["provider"]: r for r in evaluate_json_prompt(records)}
    assert rows["openai"]["json_valido"] == 1
    assert rows["openai"]["tasa_json"] == 1.0
    assert rows["google"]["json_valido"] == 0
