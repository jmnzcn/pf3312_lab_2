"""Utilidades para leer cancellation_details del Azure Speech SDK."""
from __future__ import annotations

import azure.cognitiveservices.speech as speechsdk


def _cancellation_details(
    result: speechsdk.SpeechRecognitionResult | speechsdk.SpeechSynthesisResult,
):
    """Compatibilidad entre versiones del SDK (propiedad vs constructor)."""
    details = getattr(result, "cancellation_details", None)
    if details is not None:
        return details
    if getattr(result, "reason", None) != speechsdk.ResultReason.Canceled:
        return None
    try:
        if isinstance(result, speechsdk.SpeechSynthesisResult):
            return speechsdk.SpeechSynthesisCancellationDetails(result=result)
        return speechsdk.CancellationDetails(result)
    except Exception:
        return None


def cancellation_message(
    result: speechsdk.SpeechRecognitionResult | speechsdk.SpeechSynthesisResult,
    *,
    prefix: str,
) -> str:
    """Arma un mensaje con reason, error_code y error_details de Azure."""
    reason = getattr(result, "reason", None)
    details = _cancellation_details(result)
    if details is None:
        return f"{prefix} · reason={reason} (sin cancellation_details)"

    parts = [prefix, f"reason={details.reason}"]
    code = getattr(details, "error_code", None) or getattr(details, "code", None)
    if code is not None and str(code) not in ("CancellationErrorCode.NoError", "NoError"):
        parts.append(f"code={code}")
    error_details = getattr(details, "error_details", None) or ""
    if error_details:
        parts.append(f"details={error_details}")
    return " · ".join(parts)


def speech_result_error(
    result: speechsdk.SpeechRecognitionResult | speechsdk.SpeechSynthesisResult,
    *,
    label: str,
) -> str:
    """Mensaje de error para un resultado que no completó con éxito."""
    reason = getattr(result, "reason", None)
    if reason == speechsdk.ResultReason.Canceled:
        return cancellation_message(result, prefix=f"{label} canceled")
    return f"{label} failed · reason={reason}"
