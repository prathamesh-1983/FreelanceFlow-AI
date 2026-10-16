from src.validators import validate_fields, normalize_fields

def test_normalize_amount_and_category():
    fields = normalize_fields({"amount": "1,180.00", "category": "Unknown"})
    assert fields["amount"] == 1180.0
    assert fields["category"] == "Other"

def test_valid_record():
    record = {"vendor":"Test Vendor","expense_date":"2026-10-10","amount":100}
    assert validate_fields(record) == []

def test_invalid_date():
    record = {"vendor":"Test Vendor","expense_date":"10/10/2026","amount":100}
    assert any("YYYY-MM-DD" in error for error in validate_fields(record))
