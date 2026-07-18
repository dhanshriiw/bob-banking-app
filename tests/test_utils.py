"""
tests/test_utils.py — Unit tests for utils.py (validate_amount).
No database or Flask context required.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "BACKEND"))

from utils import validate_amount


class TestValidateAmount:
    # ── Valid inputs ──────────────────────────────────────────────
    def test_valid_integer_string(self):
        amount, error = validate_amount("100")
        assert amount == 100.0
        assert error is None

    def test_valid_decimal_string(self):
        amount, error = validate_amount("250.75")
        assert amount == 250.75
        assert error is None

    def test_valid_with_whitespace(self):
        amount, error = validate_amount("  500.00  ")
        assert amount == 500.00
        assert error is None

    def test_rounds_to_two_decimal_places(self):
        amount, error = validate_amount("99.999")
        assert amount == 100.00
        assert error is None

    # ── Invalid inputs ────────────────────────────────────────────
    def test_empty_string_returns_error(self):
        amount, error = validate_amount("")
        assert amount is None
        assert "required" in error.lower()

    def test_whitespace_only_returns_error(self):
        amount, error = validate_amount("   ")
        assert amount is None
        assert error is not None

    def test_non_numeric_returns_error(self):
        amount, error = validate_amount("abc")
        assert amount is None
        assert "valid number" in error.lower()

    def test_zero_returns_error(self):
        amount, error = validate_amount("0")
        assert amount is None
        assert "greater than zero" in error.lower()

    def test_negative_returns_error(self):
        amount, error = validate_amount("-50")
        assert amount is None
        assert "greater than zero" in error.lower()

    def test_exceeds_max_limit_returns_error(self):
        amount, error = validate_amount("9999999")
        assert amount is None
        assert "maximum" in error.lower()

    def test_none_input_returns_error(self):
        amount, error = validate_amount(None)
        assert amount is None
        assert error is not None
