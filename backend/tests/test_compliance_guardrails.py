import pytest
from app.core.guardrails import compliance_guardrails, EnterpriseComplianceGuardrails


def test_ssn_detection_and_masking():
    text = "The user SSN is 123-45-6789 and needs processing."
    result = compliance_guardrails.inspect_and_sanitize(text)
    assert result.has_pii is True
    assert "123-45-6789" not in result.sanitized_text
    assert "[MASKED_SSN_***-**-6789]" in result.sanitized_text
    assert any(f.category == "PII_SSN" for f in result.findings)


def test_credit_card_luhn_detection_and_masking():
    # Valid Visa card sample (test number passing Luhn)
    valid_cc = "4532-0150-1234-5671"
    text = f"Payment charged to {valid_cc} immediately."
    result = compliance_guardrails.inspect_and_sanitize(text)
    assert result.has_pii is True
    assert valid_cc not in result.sanitized_text
    assert "[MASKED_CARD_****-****-****-5671]" in result.sanitized_text
    assert any(f.category == "PCI_PAYMENT_CARD" for f in result.findings)


def test_credit_card_invalid_luhn_ignored():
    # Random 16 digits that fail Luhn
    fake_digits = "1234-5678-9012-3456"
    text = f"Tracking identifier is {fake_digits}."
    result = compliance_guardrails.inspect_and_sanitize(text)
    # Shouldn't be masked as card if Luhn fails
    assert not any(f.category == "PCI_PAYMENT_CARD" for f in result.findings)


def test_api_key_and_secret_token_redaction():
    text = "Please authenticate using sk-abc1234567890abcdef1234567890 to access cloud API."
    result = compliance_guardrails.inspect_and_sanitize(text)
    assert result.has_credentials is True
    assert result.is_safe is False  # Flagged unsafe because critical credentials present
    assert "sk-abc1234567890abcdef1234567890" not in result.sanitized_text
    assert "[REDACTED_OPENAI_API_KEY]" in result.sanitized_text


def test_phone_number_masking():
    text = "Call customer support at +1 (555) 234-5678 for details."
    result = compliance_guardrails.inspect_and_sanitize(text)
    assert result.has_pii is True
    assert "555" not in result.sanitized_text
    assert "[MASKED_PHONE_***-***-5678]" in result.sanitized_text


def test_clean_text_remains_unchanged():
    text = "What is the return policy window for defective items?"
    result = compliance_guardrails.inspect_and_sanitize(text)
    assert result.is_safe is True
    assert result.has_pii is False
    assert result.has_credentials is False
    assert result.sanitized_text == text
    assert len(result.findings) == 0
