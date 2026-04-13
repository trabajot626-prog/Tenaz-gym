import re


def validate_email(email):
    """Basic email format validation. Returns (bool, error_message)."""
    if not email:
        return True, None  # email is optional
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, None
    return False, "Formato de email inválido"


def validate_phone(phone):
    """
    Phone must start with + followed by 7-15 digits.
    Returns (bool, error_message).
    """
    if not phone:
        return False, "El teléfono es requerido"
    pattern = r'^\+\d{7,15}$'
    clean = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if re.match(pattern, clean):
        return True, None
    return False, "El teléfono debe comenzar con + y tener entre 7 y 15 dígitos (ej: +573001234567)"


def validate_id_number(id_number, members, exclude_id=None):
    """
    Check that the id_number is unique among members.
    If exclude_id is given, skip that member (for updates).
    Returns (bool, error_message).
    """
    if not id_number:
        return False, "El número de identificación es requerido"
    for m in members:
        if m['id_number'] == str(id_number) and m['id'] != exclude_id:
            return False, f"El número de identificación '{id_number}' ya está registrado"
    return True, None


def validate_member_data(data, members, member_id=None):
    """
    Validate all member fields. Returns list of error strings.
    member_id is used to exclude current member during updates.
    """
    errors = []

    if not data.get('name', '').strip():
        errors.append("El nombre es requerido")
    if not data.get('last_name', '').strip():
        errors.append("El apellido es requerido")

    ok, err = validate_id_number(data.get('id_number', ''), members, exclude_id=member_id)
    if not ok:
        errors.append(err)

    ok, err = validate_phone(data.get('phone', ''))
    if not ok:
        errors.append(err)

    ok, err = validate_email(data.get('email', ''))
    if not ok:
        errors.append(err)

    if not data.get('plan_id'):
        errors.append("El plan es requerido")

    return errors


def validate_payment_data(data):
    """Validate payment creation fields. Returns list of error strings."""
    errors = []

    if not data.get('member_id'):
        errors.append("El miembro es requerido")

    if not data.get('date'):
        errors.append("La fecha de pago es requerida")

    try:
        amount = float(data.get('amount', 0))
        if amount <= 0:
            errors.append("El monto debe ser mayor a cero")
    except (TypeError, ValueError):
        errors.append("El monto es inválido")

    try:
        months = int(data.get('months', 1))
        if months < 1 or months > 12:
            errors.append("Los meses deben estar entre 1 y 12")
    except (TypeError, ValueError):
        errors.append("El número de meses es inválido")

    return errors
