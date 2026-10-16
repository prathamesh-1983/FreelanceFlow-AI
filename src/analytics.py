import pandas as pd

def category_summary(df):
    if df.empty or "category" not in df.columns:
        return pd.DataFrame(columns=["category","amount"])
    work = df.copy()
    work["amount"] = pd.to_numeric(work["amount"], errors="coerce").fillna(0)
    return work.groupby("category", dropna=False, as_index=False)["amount"].sum().sort_values("amount", ascending=False)

def monthly_summary(df):
    if df.empty or "expense_date" not in df.columns:
        return pd.DataFrame(columns=["month","amount"])
    work = df.copy()
    work["expense_date"] = pd.to_datetime(work["expense_date"], errors="coerce")
    work["amount"] = pd.to_numeric(work["amount"], errors="coerce").fillna(0)
    work = work.dropna(subset=["expense_date"])
    if work.empty:
        return pd.DataFrame(columns=["month","amount"])
    work["month"] = work["expense_date"].dt.to_period("M").astype(str)
    return work.groupby("month", as_index=False)["amount"].sum().sort_values("month")
