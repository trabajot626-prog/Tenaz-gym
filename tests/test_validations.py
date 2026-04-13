"""Tests for validation utilities."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from utils.validations import (
    validate_email, validate_phone, validate_id_number,
    validate_member_data, validate_payment_data
)


class TestValidateEmail:
    def test_valid_email(self):
        ok, err = validate_email('user@example.com')
        assert ok is True
        assert err is None

    def test_valid_email_subdomain(self):
        ok, err = validate_email('user@mail.example.co')
        assert ok is True

    def test_invalid_email_no_at(self):
        ok, err = validate_email('userexample.com')
        assert ok is False
        assert err is not None

    def test_invalid_email_no_dot(self):
        ok, err = validate_email('user@example')
        assert ok is False

    def test_empty_email_is_optional(self):
        ok, err = validate_email('')
        assert ok is True  # email is optional

    def test_none_email(self):
        ok, err = validate_email(None)
        assert ok is True


class TestValidatePhone:
    def test_valid_colombian_phone(self):
        ok, err = validate_phone('+573001234567')
        assert ok is True
        assert err is None

    def test_valid_phone_with_spaces(self):
        ok, err = validate_phone('+57 300 123 4567')
        assert ok is True

    def test_valid_short_phone(self):
        ok, err = validate_phone('+1234567')
        assert ok is True

    def test_missing_plus(self):
        ok, err = validate_phone('573001234567')
        assert ok is False
        assert err is not None

    def test_too_short(self):
        ok, err = validate_phone('+12345')
        assert ok is False

    def test_too_long(self):
        ok, err = validate_phone('+12345678901234567')
        assert ok is False

    def test_empty_phone(self):
        ok, err = validate_phone('')
        assert ok is False

    def test_none_phone(self):
        ok, err = validate_phone(None)
        assert ok is False

    def test_phone_with_letters(self):
        ok, err = validate_phone('+57abc1234567')
        assert ok is False


class TestValidateIdNumber:
    def test_unique_id(self):
        members = [{'id': 1, 'id_number': '111'}]
        ok, err = validate_id_number('222', members)
        assert ok is True

    def test_duplicate_id(self):
        members = [{'id': 1, 'id_number': '111'}]
        ok, err = validate_id_number('111', members)
        assert ok is False
        assert err is not None

    def test_exclude_self_on_update(self):
        members = [{'id': 1, 'id_number': '111'}]
        ok, err = validate_id_number('111', members, exclude_id=1)
        assert ok is True

    def test_empty_id(self):
        ok, err = validate_id_number('', [])
        assert ok is False

    def test_none_id(self):
        ok, err = validate_id_number(None, [])
        assert ok is False


class TestValidateMemberData:
    def _valid_data(self):
        return {
            'name': 'Juan',
            'last_name': 'García',
            'id_number': '123',
            'phone': '+573001234567',
            'email': 'juan@example.com',
            'plan_id': 1
        }

    def test_valid_member(self):
        errors = validate_member_data(self._valid_data(), [])
        assert errors == []

    def test_missing_name(self):
        data = self._valid_data()
        data['name'] = ''
        errors = validate_member_data(data, [])
        assert any('nombre' in e.lower() for e in errors)

    def test_missing_last_name(self):
        data = self._valid_data()
        data['last_name'] = ''
        errors = validate_member_data(data, [])
        assert any('apellido' in e.lower() for e in errors)

    def test_missing_plan(self):
        data = self._valid_data()
        data['plan_id'] = None
        errors = validate_member_data(data, [])
        assert any('plan' in e.lower() for e in errors)

    def test_invalid_phone(self):
        data = self._valid_data()
        data['phone'] = 'notaphone'
        errors = validate_member_data(data, [])
        assert len(errors) > 0

    def test_duplicate_id_number(self):
        existing = [{'id': 99, 'id_number': '123'}]
        errors = validate_member_data(self._valid_data(), existing)
        assert any('identificación' in e.lower() for e in errors)


class TestValidatePaymentData:
    def test_valid_payment(self):
        data = {'member_id': 1, 'date': '2026-01-01', 'amount': 50000, 'months': 1}
        errors = validate_payment_data(data)
        assert errors == []

    def test_missing_member(self):
        data = {'date': '2026-01-01', 'amount': 50000, 'months': 1}
        errors = validate_payment_data(data)
        assert any('miembro' in e.lower() for e in errors)

    def test_zero_amount(self):
        data = {'member_id': 1, 'date': '2026-01-01', 'amount': 0, 'months': 1}
        errors = validate_payment_data(data)
        assert any('monto' in e.lower() for e in errors)

    def test_invalid_months(self):
        data = {'member_id': 1, 'date': '2026-01-01', 'amount': 50000, 'months': 13}
        errors = validate_payment_data(data)
        assert any('meses' in e.lower() for e in errors)

    def test_months_zero(self):
        data = {'member_id': 1, 'date': '2026-01-01', 'amount': 50000, 'months': 0}
        errors = validate_payment_data(data)
        assert any('meses' in e.lower() for e in errors)
