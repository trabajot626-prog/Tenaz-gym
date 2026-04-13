import csv
import io
import os
from datetime import date
from flask import Blueprint, request, jsonify, send_file, current_app
from PIL import Image, UnidentifiedImageError
from utils.data_manager import load_data, save_data, next_id
from utils.validations import validate_member_data
from utils.whatsapp_helper import generate_whatsapp_url

members_bp = Blueprint('members', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@members_bp.route('/api/members', methods=['GET'])
def list_members():
    data = load_data()
    members = data.get('members', [])

    search = request.args.get('search', '').lower().strip()
    if search:
        members = [
            m for m in members
            if search in m.get('name', '').lower()
            or search in m.get('last_name', '').lower()
            or search in m.get('id_number', '').lower()
            or search in m.get('phone', '').lower()
        ]

    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    total = len(members)
    start = (page - 1) * per_page
    end = start + per_page
    paged = members[start:end]

    # Attach plan name
    plans = {p['id']: p for p in data.get('plans', [])}
    for m in paged:
        plan = plans.get(m.get('plan_id'))
        m['plan_name'] = plan['name'] if plan else None

    return jsonify({
        'success': True,
        'data': paged,
        'pagination': {'page': page, 'per_page': per_page, 'total': total, 'pages': -(-total // per_page)}
    })


@members_bp.route('/api/members', methods=['POST'])
def create_member():
    body = request.get_json(silent=True) or {}
    data = load_data()
    members = data.get('members', [])

    errors = validate_member_data(body, members)
    if errors:
        return jsonify({'success': False, 'error': '; '.join(errors)}), 400

    new_member = {
        'id': next_id(members),
        'name': body.get('name', '').strip(),
        'last_name': body.get('last_name', '').strip(),
        'id_number': str(body.get('id_number', '')).strip(),
        'phone': body.get('phone', '').strip(),
        'email': body.get('email', '').strip(),
        'registration_date': body.get('registration_date', str(date.today())),
        'expiry_date': body.get('expiry_date', None),
        'plan_id': int(body.get('plan_id')),
        'photo_path': None
    }
    members.append(new_member)
    data['members'] = members
    save_data(data)
    return jsonify({'success': True, 'data': new_member}), 201


@members_bp.route('/api/members/<int:member_id>', methods=['GET'])
def get_member(member_id):
    data = load_data()
    member = next((m for m in data.get('members', []) if m['id'] == member_id), None)
    if not member:
        return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404

    plans = {p['id']: p for p in data.get('plans', [])}
    plan = plans.get(member.get('plan_id'))
    member['plan_name'] = plan['name'] if plan else None
    member['plan_price'] = plan['price'] if plan else None

    # Payment history for this member
    payments = [p for p in data.get('payments', []) if p['member_id'] == member_id]
    member['payments'] = sorted(payments, key=lambda x: x['date'], reverse=True)

    return jsonify({'success': True, 'data': member})


@members_bp.route('/api/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    body = request.get_json(silent=True) or {}
    data = load_data()
    members = data.get('members', [])
    idx = next((i for i, m in enumerate(members) if m['id'] == member_id), None)
    if idx is None:
        return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404

    errors = validate_member_data(body, members, member_id=member_id)
    if errors:
        return jsonify({'success': False, 'error': '; '.join(errors)}), 400

    member = members[idx]
    member['name'] = body.get('name', member['name']).strip()
    member['last_name'] = body.get('last_name', member['last_name']).strip()
    member['id_number'] = str(body.get('id_number', member['id_number'])).strip()
    member['phone'] = body.get('phone', member['phone']).strip()
    member['email'] = body.get('email', member.get('email', '')).strip()
    member['plan_id'] = int(body.get('plan_id', member['plan_id']))
    if 'expiry_date' in body:
        member['expiry_date'] = body['expiry_date']

    data['members'] = members
    save_data(data)
    return jsonify({'success': True, 'data': member})


@members_bp.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    data = load_data()
    members = data.get('members', [])
    member = next((m for m in members if m['id'] == member_id), None)
    if not member:
        return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404

    data['members'] = [m for m in members if m['id'] != member_id]
    # Remove payments associated
    data['payments'] = [p for p in data.get('payments', []) if p['member_id'] != member_id]
    save_data(data)
    return jsonify({'success': True, 'data': {'message': 'Miembro eliminado'}})


@members_bp.route('/api/members/<int:member_id>/photo', methods=['POST'])
def upload_photo(member_id):
    data = load_data()
    members = data.get('members', [])
    idx = next((i for i, m in enumerate(members) if m['id'] == member_id), None)
    if idx is None:
        return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404

    if 'photo' not in request.files:
        return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400

    file = request.files['photo']
    if not file or file.filename == '':
        return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400

    # Read the file bytes and detect the image format using Pillow.
    # The extension is mapped from PIL's format string via explicit string
    # literals so no user-provided data flows into the saved path.
    file_bytes = file.read()
    try:
        with Image.open(io.BytesIO(file_bytes)) as img:
            detected = img.format
    except (UnidentifiedImageError, Exception):
        return jsonify({'success': False, 'error': 'Archivo de imagen inválido'}), 400

    # Use explicit branches so the filename is assembled from string constants
    # (not from user-derived values), breaking any user-data → path data flow.
    if detected == 'JPEG':
        filename = f"member_{member_id}.jpg"
    elif detected == 'PNG':
        filename = f"member_{member_id}.png"
    elif detected == 'GIF':
        filename = f"member_{member_id}.gif"
    elif detected == 'WEBP':
        filename = f"member_{member_id}.webp"
    else:
        return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/photos')
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    with open(filepath, 'wb') as fh:
        fh.write(file_bytes)

    members[idx]['photo_path'] = f"/static/photos/{filename}"
    data['members'] = members
    save_data(data)
    return jsonify({'success': True, 'data': {'photo_path': members[idx]['photo_path']}})


@members_bp.route('/api/members/export/csv', methods=['GET'])
def export_csv():
    data = load_data()
    members = data.get('members', [])
    plans = {p['id']: p for p in data.get('plans', [])}

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Nombre', 'Apellido', 'Cédula', 'Teléfono', 'Email', 'Plan', 'Registro', 'Vencimiento'])
    for m in members:
        plan = plans.get(m.get('plan_id'))
        writer.writerow([
            m['id'], m.get('name'), m.get('last_name'), m.get('id_number'),
            m.get('phone'), m.get('email'),
            plan['name'] if plan else '',
            m.get('registration_date'), m.get('expiry_date')
        ])

    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name='miembros.csv'
    )


@members_bp.route('/api/members/<int:member_id>/whatsapp', methods=['GET'])
def get_whatsapp(member_id):
    data = load_data()
    member = next((m for m in data.get('members', []) if m['id'] == member_id), None)
    if not member:
        return jsonify({'success': False, 'error': 'Miembro no encontrado'}), 404

    template = data.get('settings', {}).get('whatsapp_template', current_app.config['WA_TEMPLATE'])
    full_name = f"{member.get('name', '')} {member.get('last_name', '')}".strip()
    expiry = member.get('expiry_date', 'N/A')
    url = generate_whatsapp_url(member.get('phone', ''), full_name, expiry, template)
    return jsonify({'success': True, 'data': {'url': url}})
