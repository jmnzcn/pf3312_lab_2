from common.audio_samples import (
    EXPECTED_STT_IDS,
    catalog_fingerprint,
    load_catalog_data,
    validate_catalog,
    verify_wav_checksums,
)


def test_catalog_has_14_expected_ids():
    warnings = validate_catalog(require_wavs=False)
    assert not warnings, warnings
    assert len(EXPECTED_STT_IDS) == 14


def test_catalog_fingerprint_stable():
    fp1 = catalog_fingerprint()
    fp2 = catalog_fingerprint()
    assert fp1 == fp2
    assert len(fp1) == 16


def test_catalog_wav_checksums_when_present():
    samples = load_catalog_data().get("samples", [])
    if not all(entry.get("sha256") for entry in samples):
        return
    issues = verify_wav_checksums()
    assert not issues, issues
