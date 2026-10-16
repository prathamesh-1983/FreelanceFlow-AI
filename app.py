from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

from src.database import init_db, add_expense, list_expenses, delete_expense, update_expense
from src.document_parser import extract_text
from src.ai_extractor import extract_invoice_fields, ollama_status
from src.validators import normalize_fields, validate_fields
from src.analytics import monthly_summary, category_summary
from src.reports import expenses_to_csv

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "freelanceflow.db"

st.set_page_config(page_title="FreelanceFlow AI", page_icon="🧾", layout="wide")
init_db(DB_PATH)

st.markdown("""
<style>
.block-container {padding-top: 1.5rem; max-width: 1400px;}
.hero {padding: 1.25rem 1.5rem; border-radius: 16px; background: linear-gradient(120deg,#14213d,#243b64); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin:0;}
.hero p {color:#e4eaf5; margin:.35rem 0 0 0;}
.small-note {color:#6b7280;font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="hero"><h1>🧾 FreelanceFlow AI</h1><p>Private, local-first invoice and receipt organizer powered by open-weight AI.</p></div>', unsafe_allow_html=True)
st.caption("Privacy note: files are processed by this app and, when enabled, your locally running Ollama model. Review the settings and model configuration before using sensitive documents.")

with st.sidebar:
    st.title("FreelanceFlow")
    page = st.radio("Navigation", ["Dashboard", "Upload & Extract", "Expenses", "Reports", "Settings"])
    st.divider()
    st.caption("Local-first MVP • Python + Streamlit + SQLite + Ollama")

if page == "Dashboard":
    df = list_expenses(DB_PATH)
    st.subheader("Overview")
    if df.empty:
        st.info("No expenses yet. Open **Upload & Extract** to add your first receipt or invoice, or use **Expenses** to enter a record manually.")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total expenses", "0")
        col2.metric("Recorded amount", "0.00")
        col3.metric("Categories", "0")
        col4.metric("Needs review", "0")
    else:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        total = float(df["amount"].sum())
        categories = int(df["category"].nunique())
        needs_review = int((df["review_status"] != "approved").sum())
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Expense records", f"{len(df):,}")
        c2.metric("Recorded total", f"{total:,.2f}")
        c3.metric("Categories", categories)
        c4.metric("Needs review", needs_review)
        left, right = st.columns(2)
        with left:
            st.markdown("#### Spending by category")
            cat = category_summary(df)
            if not cat.empty:
                fig = px.pie(cat, names="category", values="amount", hole=.45)
                st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("#### Monthly spending")
            monthly = monthly_summary(df)
            if not monthly.empty:
                fig = px.bar(monthly, x="month", y="amount", labels={"month":"Month","amount":"Amount"})
                st.plotly_chart(fig, use_container_width=True)
        st.markdown("#### Recent records")
        st.dataframe(df.head(10), use_container_width=True, hide_index=True)

elif page == "Upload & Extract":
    st.subheader("Upload a receipt or invoice")
    st.write("Supported: PDF, PNG, JPG, JPEG, and TXT. Scanned image OCR requires Tesseract installed on your computer.")
    uploaded = st.file_uploader("Choose a document", type=["pdf", "png", "jpg", "jpeg", "txt"])
    use_ai = st.checkbox("Use local Ollama AI to extract fields", value=True)
    if uploaded:
        safe_name = Path(uploaded.name).name
        stored_path = UPLOAD_DIR / safe_name
        # Avoid overwriting existing uploads.
        if stored_path.exists():
            stored_path = UPLOAD_DIR / f"{stored_path.stem}_{abs(hash(uploaded.getvalue())) % 100000}{stored_path.suffix}"
        stored_path.write_bytes(uploaded.getvalue())
        st.success(f"File received: {uploaded.name}")
        with st.spinner("Extracting document text..."):
            text, parser_note = extract_text(stored_path)
        if parser_note:
            st.warning(parser_note)
        with st.expander("View extracted text"):
            st.text_area("Document text", value=text, height=180)
        if not text.strip():
            st.error("No text could be extracted. For image scans, install Tesseract OCR and try again, or enter the record manually.")
        else:
            if use_ai:
                with st.spinner("Asking the local model to extract fields..."):
                    fields, ai_note = extract_invoice_fields(text)
                if ai_note:
                    st.warning(ai_note)
            else:
                fields = {}
            defaults = normalize_fields(fields, uploaded.name)
            st.markdown("#### Review extracted details")
            st.caption("AI output may be wrong. Confirm all fields, especially dates, currency, tax, and totals, before saving.")
            with st.form("expense_form"):
                a, b, c = st.columns(3)
                vendor = a.text_input("Vendor / merchant", defaults["vendor"])
                invoice_number = b.text_input("Invoice number", defaults["invoice_number"])
                expense_date = c.text_input("Date (YYYY-MM-DD)", defaults["expense_date"])
                d, e, f = st.columns(3)
                amount = d.number_input("Total amount", min_value=0.0, value=float(defaults["amount"]), step=1.0, format="%.2f")
                currency = e.text_input("Currency", defaults["currency"])
                category = f.selectbox("Category", ["Software", "Office supplies", "Travel", "Meals", "Utilities", "Marketing", "Professional services", "Equipment", "Other"],
                                       index=["Software", "Office supplies", "Travel", "Meals", "Utilities", "Marketing", "Professional services", "Equipment", "Other"].index(defaults["category"]) if defaults["category"] in ["Software", "Office supplies", "Travel", "Meals", "Utilities", "Marketing", "Professional services", "Equipment", "Other"] else 8)
                description = st.text_area("Notes / description", defaults["description"])
                submitted = st.form_submit_button("Save expense", type="primary")
            if submitted:
                record = {
                    "vendor": vendor.strip() or "Unknown vendor",
                    "invoice_number": invoice_number.strip(),
                    "expense_date": expense_date.strip(),
                    "amount": float(amount),
                    "currency": currency.strip().upper() or "USD",
                    "category": category,
                    "description": description.strip(),
                    "document_name": uploaded.name,
                    "source_path": str(stored_path.relative_to(APP_DIR)),
                    "review_status": "approved",
                    "extracted_text": text,
                }
                errors = validate_fields(record)
                if errors:
                    st.error("Please fix these issues: " + "; ".join(errors))
                else:
                    add_expense(DB_PATH, record)
                    st.success("Expense saved successfully.")
                    st.balloons()

elif page == "Expenses":
    st.subheader("Expense records")
    df = list_expenses(DB_PATH)
    with st.expander("Add record manually"):
        with st.form("manual_expense"):
            a,b,c = st.columns(3)
            vendor = a.text_input("Vendor", "")
            invoice_number = b.text_input("Invoice number", "")
            expense_date = c.text_input("Date (YYYY-MM-DD)", "")
            d,e,f = st.columns(3)
            amount = d.number_input("Amount", min_value=0.0, value=0.0, step=1.0)
            currency = e.text_input("Currency", "INR")
            category = f.selectbox("Category", ["Software","Office supplies","Travel","Meals","Utilities","Marketing","Professional services","Equipment","Other"])
            description = st.text_input("Description", "")
            manual_submit = st.form_submit_button("Add expense")
        if manual_submit:
            record = {"vendor":vendor.strip() or "Unknown vendor","invoice_number":invoice_number.strip(),
                      "expense_date":expense_date.strip(),"amount":float(amount),"currency":currency.strip().upper() or "INR",
                      "category":category,"description":description.strip(),"document_name":"","source_path":"",
                      "review_status":"approved","extracted_text":""}
            errors = validate_fields(record)
            if errors:
                st.error("; ".join(errors))
            else:
                add_expense(DB_PATH, record)
                st.success("Record added.")
                st.rerun()
    df = list_expenses(DB_PATH)
    if df.empty:
        st.info("No records yet.")
    else:
        search = st.text_input("Search vendor, invoice, category, or description")
        if search:
            mask = df.astype(str).apply(lambda col: col.str.contains(search, case=False, na=False)).any(axis=1)
            df = df[mask]
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("#### Edit or delete a record")
        ids = df["id"].tolist()
        if ids:
            selected_id = st.selectbox("Select record ID", ids)
            selected = df[df["id"] == selected_id].iloc[0]
            with st.form("edit_record"):
                a,b = st.columns(2)
                edit_vendor = a.text_input("Vendor", str(selected["vendor"]))
                edit_category = b.text_input("Category", str(selected["category"]))
                c,d = st.columns(2)
                edit_amount = c.number_input("Amount", min_value=0.0, value=float(selected["amount"]), step=1.0)
                edit_date = d.text_input("Date (YYYY-MM-DD)", str(selected["expense_date"]))
                edit_status = st.selectbox("Review status", ["approved","needs_review"], index=0 if selected["review_status"]=="approved" else 1)
                save_edit = st.form_submit_button("Save changes")
            if save_edit:
                errors = validate_fields({"vendor":edit_vendor,"expense_date":edit_date,"amount":edit_amount})
                if errors:
                    st.error("; ".join(errors))
                else:
                    update_expense(DB_PATH, int(selected_id), {"vendor":edit_vendor,"category":edit_category,"amount":float(edit_amount),"expense_date":edit_date,"review_status":edit_status})
                    st.success("Updated.")
                    st.rerun()
            if st.button("Delete selected record", type="secondary"):
                delete_expense(DB_PATH, int(selected_id))
                st.success("Deleted.")
                st.rerun()

elif page == "Reports":
    st.subheader("Reports & export")
    df = list_expenses(DB_PATH)
    if df.empty:
        st.info("Add records before generating a report.")
    else:
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        st.metric("Total recorded amount", f"{df['amount'].sum():,.2f}")
        st.dataframe(category_summary(df), use_container_width=True, hide_index=True)
        csv_bytes = expenses_to_csv(df)
        st.download_button("Download all expenses as CSV", data=csv_bytes, file_name="freelanceflow_expenses.csv", mime="text/csv")
        st.download_button("Download monthly summary as CSV", data=monthly_summary(df).to_csv(index=False).encode("utf-8"), file_name="monthly_summary.csv", mime="text/csv")

elif page == "Settings":
    st.subheader("Settings & diagnostics")
    st.markdown("#### Local AI status")
    status, message = ollama_status()
    if status:
        st.success(message)
    else:
        st.warning(message)
    st.markdown("#### Privacy and data")
    st.write(f"Database: `{DB_PATH}`")
    st.write(f"Uploaded files: `{UPLOAD_DIR}`")
    st.write("This MVP stores records in a local SQLite database. Uploaded files remain in the local uploads folder until you remove them.")
    st.markdown("#### Setup model")
    st.code("ollama pull qwen2.5:3b\nollama run qwen2.5:3b")
    st.markdown("#### Known limitations")
    st.write("- AI extraction can make mistakes; review every field before saving.")
    st.write("- OCR quality depends on scan quality and local Tesseract installation.")
    st.write("- This is an expense organizer, not tax, accounting, or investment advice.")
