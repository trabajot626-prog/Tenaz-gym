import json
import os
import shutil
from config import Config

DEFAULT_DATA = {
    "members": [],
    "plans": [
        {"id": 1, "name": "Mensual", "price": 50000, "duration_days": 30},
        {"id": 2, "name": "Trimestral", "price": 130000, "duration_days": 90}
    ],
    "payments": [],
    "settings": {
        "username": "admin",
        "password": "gym123",
        "whatsapp_template": (
            "Hola {nombre}, te informamos que tu membresía en Gym-Tenaz venció el {fecha}. "
            "Para renovarla contáctanos o visítanos. ¡Te esperamos! 💪"
        ),
        "gym_name": "Gym-Tenaz"
    }
}


def load_data():
    path = Config.DATA_PATH
    if not os.path.exists(path):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Ensure all top-level keys exist
        for key in DEFAULT_DATA:
            if key not in data:
                data[key] = DEFAULT_DATA[key]
        return data
    except (json.JSONDecodeError, IOError):
        save_data(DEFAULT_DATA)
        return DEFAULT_DATA.copy()


def save_data(data):
    path = Config.DATA_PATH
    # Create directory if needed
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    # Backup existing file before overwrite
    if os.path.exists(path):
        backup_path = path.replace('.json', '_backup.json')
        shutil.copy2(path, backup_path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def next_id(collection):
    """Return the next auto-increment ID for a collection list."""
    if not collection:
        return 1
    return max(item['id'] for item in collection) + 1
