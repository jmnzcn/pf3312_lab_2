import pandas as pd

from analysis.aggregate import stt_wer_narrative


def test_stt_wer_narrative_mentions_sources():
    wer_src = pd.DataFrame(
        [
            {"provider": "deepgram", "audio_source": "fleurs_human", "wer_prom": 0.03, "llamadas": 25},
            {"provider": "deepgram", "audio_source": "synthetic_piper", "wer_prom": 0.15, "llamadas": 25},
            {"provider": "deepgram", "audio_source": "common_voice_noisy", "wer_prom": 0.08, "llamadas": 15},
        ]
    )
    text = stt_wer_narrative(wer_src)
    assert "FLEURS" in text
    assert "Piper" in text
    assert "Common Voice" in text
