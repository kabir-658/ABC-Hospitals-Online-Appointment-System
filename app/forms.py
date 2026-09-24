import re

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def validate_registration(full_name, email, password):
    errors = []
    if not full_name or len(full_name.strip()) < 2:
        errors.append("Full name must contain at least 2 characters.")
    if not email or not EMAIL_RE.match(email.strip()):
        errors.append("Enter a valid email address.")
    if not password or len(password) < 6:
        errors.append("Password must contain at least 6 characters.")
    return errors


def validate_login(email, password):
    errors = []
    if not email or not EMAIL_RE.match(email.strip()):
        errors.append("Enter a valid email address.")
    if not password:
        errors.append("Password is required.")
    return errors


def validate_appointment(doctor_id, appointment_date, appointment_time):
    errors = []
    if not doctor_id:
        errors.append("Please select a doctor.")
    if not appointment_date:
        errors.append("Please select an appointment date.")
    if not appointment_time:
        errors.append("Please select an appointment time.")
    return errors
