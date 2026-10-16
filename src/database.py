import sqlite3
from pathlib import Path
import pandas as pd

COLUMNS = ["id", "vendor", "invoice_number", "expense_date", "amount", "currency",
           "category", "description", "document_name", "source_path", "review_status",
           "extracted_text", "created_at"]

def _connect(db_path):
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    with _connect(db_path) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor TEXT NOT NULL,
            invoice_number TEXT DEFAULT '',
            expense_date TEXT NOT NULL,
            amount REAL NOT NULL DEFAULT 0,
            currency TEXT NOT NULL DEFAULT 'INR',
            category TEXT NOT NULL DEFAULT 'Other',
            description TEXT DEFAULT '',
            document_name TEXT DEFAULT '',
            source_path TEXT DEFAULT '',
            review_status TEXT NOT NULL DEFAULT 'needs_review',
            extracted_text TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_date ON expenses(expense_date)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_expenses_vendor ON expenses(vendor)")

def add_expense(db_path, record):
    fields = ["vendor","invoice_number","expense_date","amount","currency","category","description",
              "document_name","source_path","review_status","extracted_text"]
    values = [record.get(k, "") for k in fields]
    with _connect(db_path) as conn:
        conn.execute(f"INSERT INTO expenses ({','.join(fields)}) VALUES ({','.join(['?']*len(fields))})", values)

def list_expenses(db_path):
    with _connect(db_path) as conn:
        rows = conn.execute("SELECT * FROM expenses ORDER BY expense_date DESC, id DESC").fetchall()
    return pd.DataFrame([dict(row) for row in rows], columns=COLUMNS)

def update_expense(db_path, expense_id, updates):
    allowed = {"vendor","category","amount","expense_date","review_status"}
    clean = {k:v for k,v in updates.items() if k in allowed}
    if not clean:
        return
    assignments = ", ".join(f"{k}=?" for k in clean)
    with _connect(db_path) as conn:
        conn.execute(f"UPDATE expenses SET {assignments} WHERE id=?", [*clean.values(), expense_id])

def delete_expense(db_path, expense_id):
    with _connect(db_path) as conn:
        conn.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
