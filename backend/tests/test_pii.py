"""Faz 4.14 (1 Ağustos 2026) — PII maskeleme motoru (app/pii.py) birim testleri."""

from __future__ import annotations

import re

from app.pii import (
    _tckn_checksum_valid,
    mask_email,
    mask_iban,
    mask_phone,
    mask_rows,
    mask_tckn,
    mask_text,
)

# Gerçek algoritmayla üretilmiş GEÇERLİ bir test-TCKN'i (resmi checksum kurallarına uyar,
# gerçek bir kişiye ait DEĞİL — yalnızca matematiksel olarak geçerli).
_VALID_TCKN = "10000000146"


def test_tckn_checksum_validates_known_good_value():
    assert _tckn_checksum_valid(_VALID_TCKN)


def test_tckn_checksum_rejects_random_11_digit_number():
    # Rastgele bir 11 haneli sayı (ör. bir sipariş/parti numarası) checksum'ı SAĞLAMAZ —
    # bu yüzden maskelenmemeli (false-positive önleme).
    assert not _tckn_checksum_valid("12345678901")
    assert not _tckn_checksum_valid("99999999999")


def test_mask_tckn_only_masks_checksum_valid_numbers():
    text = f"TCKN: {_VALID_TCKN}, sipariş no: 12345678901"
    masked = mask_tckn(text)
    assert _VALID_TCKN not in masked
    assert "100" in masked and "46" in masked  # baş/son korunur
    assert "12345678901" in masked  # geçersiz checksum → DOKUNULMAZ


def test_mask_email():
    masked = mask_email("iletişim: ahmet.yilmaz@example.com")
    assert "ahmet.yilmaz@example.com" not in masked
    assert "@example.com" in masked
    assert masked.count("*") > 0


def test_mask_phone_various_formats():
    for raw in ["05321234567", "0532 123 45 67", "+90 532 123 45 67", "532-123-45-67"]:
        masked = mask_phone(raw)
        original_digits = re.sub(r"\D", "", raw)
        digits_in_masked = "".join(c for c in masked if c.isdigit())
        assert len(digits_in_masked) < len(original_digits)
        assert "*" in masked


def test_mask_iban():
    iban = "TR330006100519786457841326"
    masked = mask_iban(iban)
    assert iban not in masked
    assert masked.startswith("TR33")
    assert masked.endswith("1326")
    assert "*" in masked


def test_mask_text_combines_all_filters():
    text = f"TCKN {_VALID_TCKN} e-posta ayse@firma.com telefon 05551234567"
    masked = mask_text(text)
    assert _VALID_TCKN not in masked
    assert "ayse@firma.com" not in masked
    assert "05551234567" not in masked


def test_mask_rows_flags_when_pii_found_and_leaves_numbers_untouched():
    rows = [
        {"ad_soyad": "Test Kişi", "tc_kimlik": _VALID_TCKN, "brut_maas": 45000.0,
         "personel_kodu": "P01"},
        {"ad_soyad": "Test Kişi 2", "tc_kimlik": "12345678901", "brut_maas": 30000.0,
         "personel_kodu": "P02"},
    ]
    masked, found = mask_rows(rows)
    assert found is True
    assert masked[0]["tc_kimlik"] != _VALID_TCKN
    assert masked[0]["brut_maas"] == 45000.0  # sayısal ölçüye DOKUNULMADI
    assert masked[1]["tc_kimlik"] == "12345678901"  # geçersiz checksum → dokunulmadı


def test_mask_rows_no_pii_found():
    rows = [{"makine": "M1", "oee": 0.72}]
    masked, found = mask_rows(rows)
    assert found is False
    assert masked == rows
