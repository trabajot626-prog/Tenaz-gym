from datetime import date
from flask import Blueprint, request, jsonify
from utils.data_manager import load_data, save_data, next_id
from utils.validations import validate_payment_data
from utils.payment_calculator import calculate_multi_month_expiry

payments_bp = Blueprint('payments', __name__)


@payments_bp.route('/api/payments', methods=['GET'])
def list_payments():
    data = load_data()
    payments = data.get('payments', [])
    members_map = {m['id']: m for m in data.get('members', [])}

    member_id = request.args.get('member_id')
    if member_id:
        try:
            member_id = int(member_id)
            payments = [p for p in payments if p['member_id'] == member_id]
        except ValueError:
            pass

    # Attach member name to each payment
    result = []
    for p in sorted(payments, key=lambda x: x['date'], reverse=True):
        entry = dict(p)
        m = members_map.get(p['member_id'])
        entry['member_name'] = f"{m['name']} {m['last_name']}" if m else 'Desconocido'
        result.append(entry)

    return jsonify({'success': True, 'data': result})


@payments_bp.route('/api/payments', methods=['POST'])
def create_payment():
    body = request.get_json(silent=True) or {}
    errors = validate_payment_data(body)
    if errors:
        return jsonify({'success': False, 'error': '; '.join(errors)}), 400

    data = load_data()
    members = data.get('members', [])
    payments = data.get('payments', [])

    member_id = int(body['member_id'])
    member = next((m for m in members if m['id'] == member_id), None)
    if not member:
        return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404

    payment_date_str = body['date']
    try:
        payment_date = date.fromisoformat(payment_date_str)
    except ValueError:
        return jsonify({'success': False, 'error': 'Fecha de pago inválida'}), 400

    months = int(body.get('months', 1))
    amount = float(body['amount'])

    # Calculate new expiry date iteratively
    new_expiry = calculate_multi_month_expiry(payment_date, months)

    # The aligned payment date is the first cycle's expiry
    aligned = calculate_multi_month_expiry(payment_date, 1)

    new_payment = {
        'id': next_id(payments),
        'member_id': member_id,
        'amount': amount,
        'date': payment_date_str,
        'description': body.get('description', f"Pago {months} mes(es)"),
        'months': months,
        'aligned_payment_date': str(aligned)
    }
    payments.append(new_payment)

    # Update member expiry_date
    for m in members:
        if m['id'] == member_id:
            m['expiry_date'] = str(new_expiry)
            break

    data['payments'] = payments
    data['members'] = members
    save_data(data)
    return jsonify({'success': True, 'data': new_payment}), 201


@payments_bp.route('/api/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    data = load_data()
    payments = data.get('payments', [])
    payment = next((p for p in payments if p['id'] == payment_id), None)
    if not payment:
        return jsonify({'success': False, 'error': 'Pago no encontrado'}), 404

    data['payments'] = [p for p in payments if p['id'] != payment_id]
    save_data(data)
    return jsonify({'success': True, 'data': {'message': 'Pago eliminado'}})


@payments_bp.route('/api/payments/member/<int:member_id>/aligned-date', methods=['GET'])
def get_aligned_date(member_id):
    """Return the current expiry_date for the member to pre-fill the payment date field."""
    data = load_data()
    member = next((m for m in data.get('members', []) if m['id'] == member_id), None)
    if not member:
        return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404

    expiry = member.get('expiry_date') or str(date.today())
    return jsonify({'success': True, 'data': {'aligned_date': expiry}})
