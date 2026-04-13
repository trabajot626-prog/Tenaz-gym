from flask import Blueprint, request, session, jsonify, current_app
from utils.data_manager import load_data, save_data

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    body = request.get_json(silent=True) or {}
    username = body.get('username', '').strip()
    password = body.get('password', '').strip()

    data = load_data()
    settings = data.get('settings', {})
    valid_user = settings.get('username', 'admin')
    valid_pass = settings.get('password', 'gym123')

    if username == valid_user and password == valid_pass:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'success': True, 'data': {'username': username}})
    return jsonify({'success': False, 'error': 'Usuario o contraseña incorrectos'}), 401


@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'data': {'message': 'Sesión cerrada'}})


@auth_bp.route('/api/auth/status', methods=['GET'])
def status():
    if session.get('logged_in'):
        return jsonify({'success': True, 'data': {'logged_in': True, 'username': session.get('username')}})
    return jsonify({'success': True, 'data': {'logged_in': False}}), 200


@auth_bp.route('/api/auth/autologin', methods=['GET'])
def autologin():
    if not current_app.config.get('ENABLE_AUTOLOGIN'):
        return jsonify({'success': False, 'error': 'Autologin not enabled'}), 403
    data = load_data()
    settings = data.get('settings', {})
    session['logged_in'] = True
    session['username'] = settings.get('username', 'admin')
    return jsonify({'success': True, 'data': {'username': session['username']}})
