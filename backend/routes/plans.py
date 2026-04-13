import csv
import io
from flask import Blueprint, request, jsonify, send_file
from utils.data_manager import load_data, save_data, next_id

plans_bp = Blueprint('plans', __name__)


@plans_bp.route('/api/plans', methods=['GET'])
def list_plans():
    data = load_data()
    plans = data.get('plans', [])
    members = data.get('members', [])
    for p in plans:
        p['member_count'] = sum(1 for m in members if m.get('plan_id') == p['id'])
    return jsonify({'success': True, 'data': plans})


@plans_bp.route('/api/plans', methods=['POST'])
def create_plan():
    body = request.get_json(silent=True) or {}
    errors = []
    if not body.get('name', '').strip():
        errors.append("El nombre del plan es requerido")
    try:
        price = float(body.get('price', 0))
        if price < 0:
            errors.append("El precio no puede ser negativo")
    except (TypeError, ValueError):
        errors.append("El precio es inválido")
        price = 0

    if errors:
        return jsonify({'success': False, 'error': '; '.join(errors)}), 400

    data = load_data()
    plans = data.get('plans', [])
    new_plan = {
        'id': next_id(plans),
        'name': body['name'].strip(),
        'price': price,
        'duration_days': int(body.get('duration_days', 30))
    }
    plans.append(new_plan)
    data['plans'] = plans
    save_data(data)
    return jsonify({'success': True, 'data': new_plan}), 201


@plans_bp.route('/api/plans/<int:plan_id>', methods=['GET'])
def get_plan(plan_id):
    data = load_data()
    plan = next((p for p in data.get('plans', []) if p['id'] == plan_id), None)
    if not plan:
        return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404
    return jsonify({'success': True, 'data': plan})


@plans_bp.route('/api/plans/<int:plan_id>', methods=['PUT'])
def update_plan(plan_id):
    body = request.get_json(silent=True) or {}
    data = load_data()
    plans = data.get('plans', [])
    idx = next((i for i, p in enumerate(plans) if p['id'] == plan_id), None)
    if idx is None:
        return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404

    plan = plans[idx]
    if 'name' in body and body['name'].strip():
        plan['name'] = body['name'].strip()
    if 'price' in body:
        try:
            plan['price'] = float(body['price'])
        except (TypeError, ValueError):
            return jsonify({'success': False, 'error': 'El precio es inválido'}), 400
    if 'duration_days' in body:
        try:
            plan['duration_days'] = int(body['duration_days'])
        except (TypeError, ValueError):
            pass

    data['plans'] = plans
    save_data(data)
    return jsonify({'success': True, 'data': plan})


@plans_bp.route('/api/plans/<int:plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    data = load_data()
    plans = data.get('plans', [])
    plan = next((p for p in plans if p['id'] == plan_id), None)
    if not plan:
        return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404

    # Check for active members in this plan
    active = [m for m in data.get('members', []) if m.get('plan_id') == plan_id]
    if active:
        return jsonify({
            'success': False,
            'error': f"No se puede eliminar: {len(active)} miembro(s) están en este plan"
        }), 400

    data['plans'] = [p for p in plans if p['id'] != plan_id]
    save_data(data)
    return jsonify({'success': True, 'data': {'message': 'Plan eliminado'}})


@plans_bp.route('/api/plans/<int:plan_id>/members', methods=['GET'])
def plan_members(plan_id):
    data = load_data()
    plan = next((p for p in data.get('plans', []) if p['id'] == plan_id), None)
    if not plan:
        return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404

    members = [m for m in data.get('members', []) if m.get('plan_id') == plan_id]
    return jsonify({'success': True, 'data': members})


@plans_bp.route('/api/plans/<int:plan_id>/export/csv', methods=['GET'])
def export_plan_csv(plan_id):
    data = load_data()
    plan = next((p for p in data.get('plans', []) if p['id'] == plan_id), None)
    if not plan:
        return jsonify({'success': False, 'error': 'Plan no encontrado'}), 404

    members = [m for m in data.get('members', []) if m.get('plan_id') == plan_id]
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Apellido', 'Cédula', 'Teléfono', 'Email', 'Registro', 'Vencimiento'])
    for m in members:
        writer.writerow([
            m['id'], m.get('name'), m.get('last_name'), m.get('id_number'),
            m.get('phone'), m.get('email'), m.get('registration_date'), m.get('expiry_date')
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'plan_{plan_id}_miembros.csv'
    )
