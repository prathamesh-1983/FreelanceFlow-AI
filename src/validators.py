from datetime import datetime

ALLOWED_CATEGORIES = ["Software", "Office supplies", "Travel", "Meals", "Utilities",
                      "Marketing", "Professional services", "Equipment", "Other"]

def normalize_fields(fields, filename=""):
    fields = fields or {}
    category = str(fields.get("category", "Other")).strip()
    if category not in ALLOWED_CATEGORIES:
        category = "Other"
    amount = fields.get("amount", 0)
    try:
        amount = float(str(amount).replace(",", "").replace("$", "").replace("₹", "").strip() or 0)
        if amount < 0:
            amount = 0
    except (ValueError, TypeError):
        amount = 0
    date = str(fields.get("expense_date", "") or "").strip()
    # Do not guess an ambiguous date; let the user correct it.
    return {
        "vendor": str(fields.get("vendor", "") or "").strip(),
        "invoice_number": str(fields.get("invoice_number", "") or "").strip(),
        "expense_date": date,
        "amount": amount,
        "currency": str(fields.get("currency", "INR") or "INR").strip().upper(),
        "category": category,
        "description": str(fields.get("description", "") or filename).strip(),
    }

def validate_fields(record):
    errors = []
    date = str(record.get("expense_date", "")).strip()
    if not date:
        errors.append("Date is required in YYYY-MM-DD format")
    else:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            errors.append("Date must use YYYY-MM-DD format")
    try:
        amount = float(record.get("amount", 0))
        if amount < 0:
            errors.append("Amount cannot be negative")
    except (ValueError, TypeError):
        errors.append("Amount must be numeric")
    if not str(record.get("vendor", "")).strip():
        errors.append("Vendor is required")
    return errors
