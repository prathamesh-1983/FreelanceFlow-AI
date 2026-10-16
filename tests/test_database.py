from src.database import init_db, add_expense, list_expenses, update_expense, delete_expense

def test_database_crud(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    record = {"vendor":"Test Shop","invoice_number":"A-1","expense_date":"2026-10-10",
              "amount":50,"currency":"INR","category":"Other","description":"Test",
              "document_name":"","source_path":"","review_status":"approved","extracted_text":""}
    add_expense(db, record)
    df = list_expenses(db)
    assert len(df) == 1
    assert df.iloc[0]["vendor"] == "Test Shop"
    update_expense(db, int(df.iloc[0]["id"]), {"vendor":"Updated"})
    assert list_expenses(db).iloc[0]["vendor"] == "Updated"
    delete_expense(db, int(df.iloc[0]["id"]))
    assert list_expenses(db).empty
