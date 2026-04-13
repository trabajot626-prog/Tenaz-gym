"""Integration tests for CRUD operations via Flask test client."""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

import pytest


class TestAuth:
    def test_login_success(self, client):
        res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'gym123'})
        data = res.get_json()
        assert res.status_code == 200
        assert data['success'] is True

    def test_login_wrong_password(self, client):
        res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'wrong'})
        data = res.get_json()
        assert res.status_code == 401
        assert data['success'] is False

    def test_status_unauthenticated(self, client):
        res = client.get('/api/auth/status')
        data = res.get_json()
        assert data['data']['logged_in'] is False

    def test_status_authenticated(self, auth_client):
        res = auth_client.get('/api/auth/status')
        data = res.get_json()
        assert data['data']['logged_in'] is True

    def test_health(self, client):
        res = client.get('/api/health')
        assert res.status_code == 200
        assert res.get_json()['success'] is True


class TestMemberCRUD:
    VALID_MEMBER = {
        'name': 'Juan',
        'last_name': 'García',
        'id_number': '123456',
        'phone': '+573001234567',
        'email': 'juan@example.com',
        'plan_id': 1,
        'registration_date': '2026-01-01'
    }

    def test_create_member(self, auth_client):
        res = auth_client.post('/api/members', json=self.VALID_MEMBER)
        data = res.get_json()
        assert res.status_code == 201
        assert data['success'] is True
        assert data['data']['name'] == 'Juan'
        assert data['data']['id'] == 1

    def test_list_members(self, auth_client):
        auth_client.post('/api/members', json=self.VALID_MEMBER)
        res = auth_client.get('/api/members')
        data = res.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1

    def test_get_member(self, auth_client):
        auth_client.post('/api/members', json=self.VALID_MEMBER)
        res = auth_client.get('/api/members/1')
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['id'] == 1

    def test_update_member(self, auth_client):
        auth_client.post('/api/members', json=self.VALID_MEMBER)
        res = auth_client.put('/api/members/1', json={**self.VALID_MEMBER, 'name': 'Carlos'})
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['name'] == 'Carlos'

    def test_delete_member(self, auth_client):
        auth_client.post('/api/members', json=self.VALID_MEMBER)
        res = auth_client.delete('/api/members/1')
        assert res.get_json()['success'] is True
        res2 = auth_client.get('/api/members/1')
        assert res2.status_code == 404

    def test_member_requires_auth(self, client):
        res = client.get('/api/members')
        assert res.status_code == 401

    def test_duplicate_id_number_rejected(self, auth_client):
        auth_client.post('/api/members', json=self.VALID_MEMBER)
        res = auth_client.post('/api/members', json={**self.VALID_MEMBER, 'id_number': '123456'})
        data = res.get_json()
        assert res.status_code == 400
        assert data['success'] is False

    def test_search_members(self, auth_client):
        auth_client.post('/api/members', json=self.VALID_MEMBER)
        auth_client.post('/api/members', json={
            **self.VALID_MEMBER, 'name': 'Pedro', 'id_number': '999'
        })
        res = auth_client.get('/api/members?search=pedro')
        data = res.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'Pedro'


class TestPlanCRUD:
    VALID_PLAN = {'name': 'Mensual', 'price': 50000, 'duration_days': 30}

    def test_list_plans(self, auth_client):
        res = auth_client.get('/api/plans')
        data = res.get_json()
        assert data['success'] is True
        # Default plans are pre-seeded
        assert len(data['data']) >= 2

    def test_create_plan(self, auth_client):
        res = auth_client.post('/api/plans', json={'name': 'Semestral', 'price': 250000, 'duration_days': 180})
        data = res.get_json()
        assert res.status_code == 201
        assert data['success'] is True
        assert data['data']['name'] == 'Semestral'

    def test_update_plan(self, auth_client):
        # Update the first default plan (id=1)
        res = auth_client.put('/api/plans/1', json={'price': 60000})
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['price'] == 60000

    def test_delete_plan_with_members_fails(self, auth_client):
        # Create member using plan 1
        auth_client.post('/api/members', json={
            'name': 'Ana', 'last_name': 'López', 'id_number': '111',
            'phone': '+573009876543', 'plan_id': 1
        })
        res = auth_client.delete('/api/plans/1')
        data = res.get_json()
        assert res.status_code == 400
        assert data['success'] is False

    def test_delete_plan_no_members_ok(self, auth_client):
        # Create a plan with no members then delete it
        cr = auth_client.post('/api/plans', json={'name': 'Temp', 'price': 10000, 'duration_days': 7})
        new_id = cr.get_json()['data']['id']
        res = auth_client.delete(f'/api/plans/{new_id}')
        assert res.get_json()['success'] is True


class TestPaymentCRUD:
    def setup_member(self, auth_client):
        auth_client.post('/api/members', json={
            'name': 'Luis', 'last_name': 'Pérez',
            'id_number': '555', 'phone': '+573005551234',
            'plan_id': 1, 'registration_date': '2025-12-01'
        })

    def test_create_payment_updates_expiry(self, auth_client):
        self.setup_member(auth_client)
        res = auth_client.post('/api/payments', json={
            'member_id': 1,
            'date': '2025-12-24',
            'amount': 50000,
            'months': 1,
            'description': 'Pago mensual'
        })
        data = res.get_json()
        assert res.status_code == 201
        assert data['success'] is True
        assert data['data']['months'] == 1

        # Verify member's expiry_date was updated
        member_res = auth_client.get('/api/members/1')
        member = member_res.get_json()['data']
        # 24/12/2025 → 28/12/2025
        assert member['expiry_date'] == '2025-12-28'

    def test_create_multi_month_payment(self, auth_client):
        self.setup_member(auth_client)
        res = auth_client.post('/api/payments', json={
            'member_id': 1,
            'date': '2026-01-18',
            'amount': 150000,
            'months': 3
        })
        assert res.status_code == 201
        # 18/01/2026 + 3 months → 18/04/2026
        member_res = auth_client.get('/api/members/1')
        assert member_res.get_json()['data']['expiry_date'] == '2026-04-18'

    def test_list_payments(self, auth_client):
        self.setup_member(auth_client)
        auth_client.post('/api/payments', json={
            'member_id': 1, 'date': '2026-01-01', 'amount': 50000, 'months': 1
        })
        res = auth_client.get('/api/payments')
        data = res.get_json()
        assert data['success'] is True
        assert len(data['data']) == 1

    def test_filter_payments_by_member(self, auth_client):
        self.setup_member(auth_client)
        auth_client.post('/api/payments', json={
            'member_id': 1, 'date': '2026-01-01', 'amount': 50000, 'months': 1
        })
        res = auth_client.get('/api/payments?member_id=1')
        data = res.get_json()
        assert all(p['member_id'] == 1 for p in data['data'])

    def test_delete_payment(self, auth_client):
        self.setup_member(auth_client)
        auth_client.post('/api/payments', json={
            'member_id': 1, 'date': '2026-01-01', 'amount': 50000, 'months': 1
        })
        res = auth_client.delete('/api/payments/1')
        assert res.get_json()['success'] is True

    def test_aligned_date_endpoint(self, auth_client):
        self.setup_member(auth_client)
        # Set an expiry date
        auth_client.put('/api/members/1', json={
            'name': 'Luis', 'last_name': 'Pérez', 'id_number': '555',
            'phone': '+573005551234', 'plan_id': 1,
            'expiry_date': '2026-02-08'
        })
        res = auth_client.get('/api/payments/member/1/aligned-date')
        data = res.get_json()
        assert data['success'] is True
        assert data['data']['aligned_date'] == '2026-02-08'


class TestDashboard:
    def test_dashboard_kpis(self, auth_client):
        res = auth_client.get('/api/dashboard')
        data = res.get_json()
        assert data['success'] is True
        assert 'total_members' in data['data']
        assert 'active_members' in data['data']
        assert 'monthly_income' in data['data']
        assert 'expiring_soon' in data['data']

    def test_dashboard_expiring(self, auth_client):
        res = auth_client.get('/api/dashboard/expiring')
        data = res.get_json()
        assert data['success'] is True
        assert isinstance(data['data'], list)
