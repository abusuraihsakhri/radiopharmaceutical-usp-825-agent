"""
Pytest configuration and shared fixtures for radiopharmaceutical-usp-825-agent.
"""
import os
import pytest


@pytest.fixture(autouse=True)
def _set_audit_secret_key(monkeypatch):
    """Ensure AUDIT_SECRET_KEY is set for all tests to avoid SecurityException."""
    monkeypatch.setenv("AUDIT_SECRET_KEY", "test-audit-secret-key-2026-pytest")
