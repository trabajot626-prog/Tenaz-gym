"""Tests for the payment cut-date algorithm."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from datetime import date
from utils.payment_calculator import calculate_expiry, calculate_multi_month_expiry


class TestCalculateExpiry:
    def test_20_dec_2025(self):
        """20/12/2025 → 18/01/2026 (18 is closest diff=2, but 18 < 20 so move to Jan)"""
        result = calculate_expiry(date(2025, 12, 20))
        assert result == date(2026, 1, 18)

    def test_24_dec_2025(self):
        """24/12/2025 → 28/12/2025 (28 is closest diff=4, not yet passed)"""
        result = calculate_expiry(date(2025, 12, 24))
        assert result == date(2025, 12, 28)

    def test_08_dec_2025(self):
        """08/12/2025 → 08/12/2025 (exactly on cut day, stays same day)"""
        result = calculate_expiry(date(2025, 12, 8))
        assert result == date(2025, 12, 8)

    def test_13_dec_2025(self):
        """13/12/2025 → 18/12/2025 (tie between 8 and 18 both diff=5, pick larger: 18)"""
        result = calculate_expiry(date(2025, 12, 13))
        assert result == date(2025, 12, 18)

    def test_18_jan_2026_on_cut_day(self):
        """18/01/2026 is itself a cut day → returns 18/01/2026"""
        result = calculate_expiry(date(2026, 1, 18))
        assert result == date(2026, 1, 18)

    def test_day_before_cut_8(self):
        """07/01/2026 → 08/01/2026 (8 is closest, not yet passed)"""
        result = calculate_expiry(date(2026, 1, 7))
        assert result == date(2026, 1, 8)

    def test_day_after_cut_8(self):
        """09/01/2026: diff to 8=1 (best), but 8 < 9 so move to next month → 08/02/2026"""
        result = calculate_expiry(date(2026, 1, 9))
        assert result == date(2026, 2, 8)

    def test_29_dec_passes_28(self):
        """29/12/2025: diff to 28=1 (best), but 28 < 29 so move to next month → 28/01/2026"""
        result = calculate_expiry(date(2025, 12, 29))
        assert result == date(2026, 1, 28)

    def test_28_dec_on_cut_day(self):
        """28/12/2025 → 28/12/2025 (exactly on 28, stays)"""
        result = calculate_expiry(date(2025, 12, 28))
        assert result == date(2025, 12, 28)

    def test_year_rollover_december(self):
        """30/12/2025: diff to 28=2 (best), but 28 < 30 so move to next month → 28/01/2026"""
        result = calculate_expiry(date(2025, 12, 30))
        assert result == date(2026, 1, 28)

    def test_day_1(self):
        """01/01/2026 → 08/01/2026 (8 is closest, not yet passed)"""
        result = calculate_expiry(date(2026, 1, 1))
        assert result == date(2026, 1, 8)


class TestMultiMonthExpiry:
    def test_18_jan_plus_2_months(self):
        """18/01/2026 + 2 months → 18/03/2026"""
        result = calculate_multi_month_expiry(date(2026, 1, 18), 2)
        assert result == date(2026, 3, 18)

    def test_18_jan_plus_3_months(self):
        """18/01/2026 + 3 months → 18/04/2026"""
        result = calculate_multi_month_expiry(date(2026, 1, 18), 3)
        assert result == date(2026, 4, 18)

    def test_1_month(self):
        """1 month == single calculate_expiry"""
        d = date(2025, 12, 24)
        assert calculate_multi_month_expiry(d, 1) == calculate_expiry(d)

    def test_12_months_from_jan_8(self):
        """12 months from 08/01/2026 → 08/01/2027"""
        result = calculate_multi_month_expiry(date(2026, 1, 8), 12)
        assert result == date(2027, 1, 8)

    def test_chained_from_srs_example(self):
        """20/12/2025 → 18/01/2026 → 18/02/2026 (2 months)"""
        result = calculate_multi_month_expiry(date(2025, 12, 20), 2)
        assert result == date(2026, 2, 18)
