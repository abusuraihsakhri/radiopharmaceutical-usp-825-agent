"""
Security & edge case tests for radiopharmaceutical-usp-825-agent.
"""
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from agents.base import (
    AuditTrail,
    AuditLogger,
    PHIGuard,
    SecurityException,
)
from agents.models import SystemTaskPayload, UrgencyLevel


class TestAuditTrailSecurity:
    """Tests for HMAC-SHA256 audit trail security."""

    def test_audit_trail_requires_secret_key(self, monkeypatch):
        """AuditTrail must not accept empty/missing secret key."""
        monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)
        with pytest.raises(SecurityException, match="AUDIT_SECRET_KEY"):
            AuditTrail(secret_key="")

    def test_audit_trail_rejects_short_key(self, monkeypatch):
        """AuditTrail must reject keys shorter than 16 characters."""
        monkeypatch.delenv("AUDIT_SECRET_KEY", raising=False)
        with pytest.raises(SecurityException, match="at least 16"):
            AuditTrail(secret_key="short")

    def test_audit_trail_accepts_valid_key(self):
        """AuditTrail initializes with a valid key."""
        trail = AuditTrail(secret_key="valid-test-key-1234567890")
        assert len(trail.logs) == 0

    def test_audit_integrity_detects_tampering(self):
        """verify_integrity detects modified audit entries."""
        trail = AuditTrail(secret_key="tamper-test-key-1234567890")
        trail.log("test_actor", "tier1", "TEST_EVENT", {"data": "original"})

        # Tamper with the stored log
        trail.logs[0]["actor"] = "attacker"
        assert trail.verify_integrity() is False

    def test_audit_chain_integrity(self):
        """verify_integrity validates full chain of entries."""
        trail = AuditTrail(secret_key="chain-test-key-1234567890")
        trail.log("actor1", "tier1", "EVENT_A", {"x": 1})
        trail.log("actor2", "tier2", "EVENT_B", {"y": 2})
        trail.log("actor3", "tier1", "EVENT_C", {"z": 3})
        assert trail.verify_integrity() is True

    def test_audit_log_blocks_phi(self):
        """AuditLogger blocks PHI in log details."""
        trail = AuditTrail(secret_key="phi-block-test-key-1234567890")
        with pytest.raises(SecurityException):
            trail.log("actor", "tier", "EVENT", {"note": "Patient MRN-12345678"})


class TestPHIGuard:
    """Tests for PHI outbound guard."""

    def test_detects_mrn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("MRN-12345678 specimen analysis")

    def test_detects_ssn(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("SSN 123-45-6789 detected")

    def test_detects_phone(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Contact: 555-123-4567")

    def test_detects_email(self):
        with pytest.raises(SecurityException):
            PHIGuard.assert_no_phi("Send to patient@hospital.com")

    def test_allows_clean_text(self):
        PHIGuard.assert_no_phi("Specimen KEY-001 analysis complete. Metric nominal.")

    def test_handles_empty_string(self):
        PHIGuard.assert_no_phi("")

    def test_handles_none(self):
        PHIGuard.assert_no_phi(None)

    def test_redact_phi(self):
        result = PHIGuard.redact_phi("Patient John Doe, MRN-994827, phone 555-123-4567")
        assert "REDACTED_IDENTIFIER" in result
        assert "MRN" not in result
        assert "555" not in result


class TestInputValidation:
    """Tests for input validation on SystemTaskPayload."""

    def test_valid_payload(self):
        p = SystemTaskPayload(task_id="TASK-001", target_identifier="KEY-01", primary_metric=25.0)
        assert p.task_id == "TASK-001"

    def test_rejects_path_traversal_in_task_id(self):
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="../../../etc/passwd", target_identifier="KEY-01", primary_metric=1.0)

    def test_rejects_special_chars_in_target(self):
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="TASK-001", target_identifier="KEY;rm -rf /", primary_metric=1.0)

    def test_rejects_extreme_metric_values(self):
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="TASK-001", target_identifier="KEY-01", primary_metric=1e15)

    def test_rejects_long_identifier(self):
        with pytest.raises(Exception):
            SystemTaskPayload(task_id="A" * 200, target_identifier="KEY-01", primary_metric=1.0)

    def test_accepts_valid_identifiers(self):
        p = SystemTaskPayload(
            task_id="TASK_2026-001.v2",
            target_identifier="TARGET.BIO_01",
            primary_metric=-5.0,
            secondary_metric=999999.0,
        )
        assert p.primary_metric == -5.0
        assert p.secondary_metric == 999999.0
