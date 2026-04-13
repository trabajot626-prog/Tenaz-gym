import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    ENABLE_AUTOLOGIN = os.environ.get('ENABLE_AUTOLOGIN', 'false').lower() == 'true'
    ALLOWED_ORIGIN = os.environ.get('ALLOWED_ORIGIN', '*')
    DATA_PATH = os.environ.get('DATA_PATH', 'gym_data.json')
    PORT = int(os.environ.get('PORT', 5000))
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'static/photos')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'gym123')
    WA_TEMPLATE = os.environ.get(
        'WA_TEMPLATE',
        'Hola {nombre}, te informamos que tu membresía en Gym-Tenaz venció el {fecha}. '
        'Para renovarla contáctanos o visítanos. ¡Te esperamos! 💪'
    )
