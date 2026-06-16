from types import SimpleNamespace

import azure.cognitiveservices.speech as speechsdk

from common.azure_speech import cancellation_message, speech_result_error


def test_cancellation_message_includes_error_code_and_details():
    details = SimpleNamespace(
        reason=speechsdk.CancellationReason.Error,
        error_code=speechsdk.CancellationErrorCode.TooManyRequests,
        error_details="Rate exceeded",
    )
    result = SimpleNamespace(
        reason=speechsdk.ResultReason.Canceled,
        cancellation_details=details,
    )
    msg = cancellation_message(result, prefix="Azure TTS canceled")
    assert "Azure TTS canceled" in msg
    assert "TooManyRequests" in msg
    assert "Rate exceeded" in msg


def test_cancellation_message_stt_uses_code_property():
    details = SimpleNamespace(
        reason=speechsdk.CancellationReason.Error,
        code=speechsdk.CancellationErrorCode.ConnectionFailure,
        error_details="WebSocket closed",
    )
    result = SimpleNamespace(
        reason=speechsdk.ResultReason.Canceled,
        cancellation_details=details,
    )
    msg = cancellation_message(result, prefix="Azure STT canceled")
    assert "ConnectionFailure" in msg
    assert "WebSocket closed" in msg


def test_speech_result_error_for_canceled():
    result = SimpleNamespace(reason=speechsdk.ResultReason.Canceled, cancellation_details=None)
    out = speech_result_error(result, label="Azure STT")
    assert out.startswith("Azure STT canceled")
