from datetime import date, timedelta
from flask import Blueprint, jsonify, current_app
from utils.data_manager import load_data
from utils.whatsapp_helper import generate_whatsapp_url

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
def get_dashboard():
    data = load_data()
    members = data.get('members', [])
    payments = data.get('payments', [])

    today = date.today()
    first_day = today.replace(day=1)

    # Count active members (expiry >= today)
    active_count = sum(
        1 for m in members
        if m.get('expiry_date') and date.fromisoformat(m['expiry_date']) >= today
    )

    # Monthly income: payments made this calendar month
    monthly_income = sum(
        p['amount'] for p in payments
        if p.get('date') and date.fromisoformat(p['date']) >= first_day
    )

    # Expiring soon: within next 7 days
    cutoff = today + timedelta(days=7)
    expiring_soon = sum(
        1 for m in members
        if m.get('expiry_date') and today <= date.fromisoformat(m['expiry_date']) <= cutoff
    )

    return jsonify({
        'success': True,
        'data': {
            'total_members': len(members),
            'active_members': active_count,
            'monthly_income': monthly_income,
            'expiring_soon': expiring_soon
        }
    })


@dashboard_bp.route('/api/dashboard/expiring', methods=['GET'])
def get_expiring():
    data = load_data()
    members = data.get('members', [])
    today = date.today()
    cutoff = today + timedelta(days=7)
    template = data.get('settings', {}).get('whatsapp_template', current_app.config['WA_TEMPLATE'])

    expiring = []
    for m in members:
        exp = m.get('expiry_date')
        if exp and today <= date.fromisoformat(exp) <= cutoff:
            full_name = f"{m.get('name', '')} {m.get('last_name', '')}".strip()
            wa_url = generate_whatsapp_url(m.get('phone', ''), full_name, exp, template)
            expiring.append({**m, 'whatsapp_url': wa_url})

    expiring.sort(key=lambda x: x['expiry_date'])
    return jsonify({'success': True, 'data': expiring})
