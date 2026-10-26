"""Input validation for patient records."""
import re
from datetime import datetime, date

EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9\-]+(\.[A-Za-z0-9\-]+)*\.[A-Za-z]{2,}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,99}$")

# Plausible physiological limits (reject typos / impossible values)
LIMITS = {
    "glucose": (20, 600, "mg/dL"),
    "haemoglobin": (3, 25, "g/dL"),
    "cholesterol": (50, 600, "mg/dL"),
}


def parse_dob(text):
    """Accept dd/mm/yyyy (also dd.mm.yyyy or dd-mm-yyyy). Return (date, error)."""
    text = (text or "").strip()
    m = re.fullmatch(r"(\d{1,2})[/.\-](\d{1,2})[/.\-](\d{4})", text)
    if not m:
        return None, "Date of birth must be in dd/mm/yyyy format."
    d, mo, y = map(int, m.groups())
    try:
        dob = date(y, mo, d)
    except ValueError:
        return None, f"'{text}' is not a real calendar date (day {d} does not exist in month {mo})."
    if dob > date.today():
        return None, "Date of birth cannot be in the future."
    if y < 1900:
        return None, "Date of birth is too far in the past."
    return dob, None


def parse_number(label, text):
    key = label.lower()
    lo, hi, unit = LIMITS[key]
    try:
        value = float(str(text).strip())
    except (TypeError, ValueError):
        return None, f"{label} must be a number."
    if value != value or value in (float("inf"), float("-inf")):
        return None, f"{label} must be a number."
    if not lo <= value <= hi:
        return None, f"{label} must be between {lo} and {hi} {unit}."
    return value, None


def validate_patient(form):
    """Return (clean_dict, errors_list)."""
    errors = []
    clean = {}

    name = (form.get("full_name") or "").strip()
    if not NAME_RE.match(name):
        errors.append("Full name must contain letters only (spaces, . ' - allowed), 2+ characters.")
    clean["full_name"] = name

    dob, err = parse_dob(form.get("dob"))
    if err:
        errors.append(err)
    else:
        clean["dob"] = dob.strftime("%d/%m/%Y")

    email = (form.get("email") or "").strip()
    if not EMAIL_RE.match(email):
        errors.append("Email address is not valid (expected name@domain.tld).")
    clean["email"] = email.lower()

    for field, label in (("glucose", "Glucose"), ("haemoglobin", "Haemoglobin"), ("cholesterol", "Cholesterol")):
        val, err = parse_number(label, form.get(field))
        if err:
            errors.append(err)
        else:
            clean[field] = val

    return clean, errors
