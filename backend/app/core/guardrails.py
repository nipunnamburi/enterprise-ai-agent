import re
from typing import List
from pydantic import BaseModel, Field


class ComplianceFinding(BaseModel):
    category: str
    match_preview: str
    risk_level: str  # low, medium, high, critical
    action_taken: str  # masked, redacted, flagged


class GuardrailInspectionResult(BaseModel):
    is_safe: bool = True
    original_text: str
    sanitized_text: str
    findings: List[ComplianceFinding] = Field(default_factory=list)
    has_pii: bool = False
    has_credentials: bool = False
    has_prompt_injection: bool = False


class EnterpriseComplianceGuardrails:
    """Enterprise-grade compliance, PII masking, and prompt-injection guardrails.

    Detects and sanitizes:
    - Prompt injection / jailbreak attempts
    - US Social Security Numbers (SSN)
    - Payment Card Numbers (Credit / Debit via Luhn check + regex)
    - API Keys / Secret Tokens (Bearer tokens, OpenAI keys, AWS keys, GitHub tokens)
    - Email Addresses (optional masking)
    - Phone Numbers
    """

    SSN_PATTERN = re.compile(r"\b(?!000|666|9\d{2})\d{3}[- ]?(?!00)\d{2}[- ]?(?!0000)\d{4}\b")
    CC_PATTERN = re.compile(r"\b(?:\d{4}[- ]?){3}\d{4}\b|\b\d{15,16}\b")
    API_KEY_PATTERNS = [
        (re.compile(r"\bsk-[a-zA-Z0-9]{20,50}\b"), "OpenAI API Key"),
        (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS Access Key"),
        (re.compile(r"\bghp_[a-zA-Z0-9]{36}\b"), "GitHub Personal Access Token"),
        (re.compile(r"\bBearer\s+eyJ[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{20,}\.[a-zA-Z0-9_-]{10,}\b"), "Bearer JWT Token"),
    ]
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})\b")

    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions", re.IGNORECASE),
        re.compile(r"(reveal|show|print|leak)\s+(your\s+)?(system\s+prompt|instructions|secrets)", re.IGNORECASE),
        re.compile(r"\b(jailbreak|DAN\s+mode|bypass\s+safety|override\s+guardrails)\b", re.IGNORECASE),
        re.compile(r"<\s*/?\s*system\s*>", re.IGNORECASE),
    ]

    @staticmethod
    def _luhn_checksum(card_number_str: str) -> bool:
        digits = [int(c) for c in re.sub(r"\D", "", card_number_str)]
        if len(digits) < 13 or len(digits) > 19:
            return False
        total = 0
        for i, digit in enumerate(digits[::-1]):
            if i % 2 == 1:
                doubled = digit * 2
                total += doubled - 9 if doubled > 9 else doubled
            else:
                total += digit
        return total % 10 == 0

    def inspect_and_sanitize(
        self,
        text: str,
        mask_emails: bool = False,
        mask_phones: bool = True,
        redact_credentials: bool = True,
        mask_ssn_cc: bool = True,
        screen_injection: bool = True,
    ) -> GuardrailInspectionResult:
        """Inspect input/output text against compliance and security policies."""
        if not text:
            return GuardrailInspectionResult(original_text="", sanitized_text="")

        sanitized = text
        findings: List[ComplianceFinding] = []
        has_pii = False
        has_credentials = False
        has_prompt_injection = False

        # 0. Screen for prompt injection patterns
        if screen_injection:
            for pattern in self.INJECTION_PATTERNS:
                match = pattern.search(sanitized)
                if match:
                    has_prompt_injection = True
                    findings.append(ComplianceFinding(
                        category="PROMPT_INJECTION",
                        match_preview=match.group(0)[:40],
                        risk_level="critical",
                        action_taken="flagged",
                    ))

        # 1. Detect & Redact API Keys / Credentials
        if redact_credentials:
            for pattern, key_type in self.API_KEY_PATTERNS:
                for match in pattern.findall(sanitized):
                    has_credentials = True
                    match_str = match if isinstance(match, str) else match[0]
                    preview = f"{match_str[:4]}...{match_str[-3:]}" if len(match_str) > 7 else "[SECRET]"
                    findings.append(ComplianceFinding(
                        category="CREDENTIALS",
                        match_preview=preview,
                        risk_level="critical",
                        action_taken="redacted",
                    ))
                    sanitized = sanitized.replace(match_str, f"[REDACTED_{key_type.upper().replace(' ', '_')}]")

        # 2. Detect & Mask SSNs
        if mask_ssn_cc:
            for match in self.SSN_PATTERN.findall(sanitized):
                has_pii = True
                clean_ssn = re.sub(r"\D", "", match)
                if len(clean_ssn) == 9:
                    findings.append(ComplianceFinding(
                        category="PII_SSN",
                        match_preview=f"***-**-{clean_ssn[-4:]}",
                        risk_level="high",
                        action_taken="masked",
                    ))
                    sanitized = sanitized.replace(match, f"[MASKED_SSN_***-**-{clean_ssn[-4:]}]")

        # 3. Detect & Mask Credit Card Numbers
        if mask_ssn_cc:
            for candidate in self.CC_PATTERN.findall(sanitized):
                clean_card = re.sub(r"\D", "", candidate)
                if self._luhn_checksum(clean_card):
                    has_pii = True
                    findings.append(ComplianceFinding(
                        category="PCI_PAYMENT_CARD",
                        match_preview=f"****-****-****-{clean_card[-4:]}",
                        risk_level="critical",
                        action_taken="masked",
                    ))
                    sanitized = sanitized.replace(candidate, f"[MASKED_CARD_****-****-****-{clean_card[-4:]}]")

        # 4. Detect & Mask Phone Numbers
        if mask_phones:
            for match_obj in self.PHONE_PATTERN.finditer(sanitized):
                full_phone = match_obj.group(0)
                digits = re.sub(r"\D", "", full_phone)
                if 10 <= len(digits) <= 15:
                    has_pii = True
                    masked = f"[MASKED_PHONE_***-***-{digits[-4:]}]"
                    findings.append(ComplianceFinding(
                        category="PII_PHONE",
                        match_preview=f"***-***-{digits[-4:]}",
                        risk_level="medium",
                        action_taken="masked",
                    ))
                    sanitized = sanitized.replace(full_phone, masked)

        # 5. Mask Emails if requested
        if mask_emails:
            for email in self.EMAIL_PATTERN.findall(sanitized):
                has_pii = True
                name, domain = email.split("@", 1)
                masked_email = f"{name[:2]}***@{domain}"
                findings.append(ComplianceFinding(
                    category="PII_EMAIL",
                    match_preview=masked_email,
                    risk_level="low",
                    action_taken="masked",
                ))
                sanitized = sanitized.replace(email, f"[MASKED_EMAIL_{masked_email}]")

        is_safe = not (has_credentials or has_prompt_injection)

        return GuardrailInspectionResult(
            is_safe=is_safe,
            original_text=text,
            sanitized_text=sanitized,
            findings=findings,
            has_pii=has_pii,
            has_credentials=has_credentials,
            has_prompt_injection=has_prompt_injection,
        )


compliance_guardrails = EnterpriseComplianceGuardrails()
