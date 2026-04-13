from urllib.parse import quote


def generate_whatsapp_url(phone: str, member_name: str, expiry_date: str, template: str) -> str:
    """Generate a wa.me URL with a personalized message."""
    # Strip formatting characters, keep only digits (drop leading +)
    clean_phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    if clean_phone.startswith('+'):
        clean_phone = clean_phone[1:]

    message = template.format(
        nombre=member_name,
        fecha=expiry_date,
        gimnasio='Gym-Tenaz'
    )

    encoded_message = quote(message)
    return f"https://wa.me/{clean_phone}?text={encoded_message}"
