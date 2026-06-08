from common.metrics import compute_wer


def test_wer_identical():
    assert compute_wer("hola mundo", "hola mundo") == 0.0


def test_wer_partial():
    wer = compute_wer("hola mundo", "hola")
    assert 0.0 < wer < 1.0
