import os
from flask import Flask, session, jsonify, send_from_directory, request
from flask_cors import CORS
from config import Config
from routes.auth import auth_bp
from routes.members import members_bp
from routes.plans import plans_bp
from routes.payments import payments_bp
from routes.dashboard import dashboard_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
app.config['ENABLE_AUTOLOGIN'] = Config.ENABLE_AUTOLOGIN
app.config['WA_TEMPLATE'] = Config.WA_TEMPLATE

# CORS — allow credentials from the configured origin
allowed_origin = Config.ALLOWED_ORIGIN
if allowed_origin == '*':
    CORS(app, supports_credentials=True, origins='*')
else:
    CORS(app, supports_credentials=True, origins=[allowed_origin])

# Public endpoints that do NOT require login
PUBLIC_ENDPOINTS = {'auth.login', 'auth.logout', 'auth.status', 'auth.autologin', 'health'}


@app.before_request
def require_login():
    endpoint = request.endpoint or ''
    if endpoint in PUBLIC_ENDPOINTS:
        return None
    if not session.get('logged_in'):
        return jsonify({'success': False, 'error': 'No autenticado'}), 401


# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(members_bp)
app.register_blueprint(plans_bp)
app.register_blueprint(payments_bp)
app.register_blueprint(dashboard_bp)


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'success': True, 'data': {'status': 'ok'}})


@app.route('/static/photos/<path:filename>')
def serve_photo(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


if __name__ == '__main__':
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    app.run(host='0.0.0.0', port=Config.PORT, debug=False)
