import streamlit as st
import pandas as pd
from src.matcher import match_transactions
from src.utils import preprocess
from dateutil.parser import parse as parse_date

REQUIRED_COLUMNS = {"Date", "Amount", "Description"}

st.title("🔍 Reconciliation Tool")

REQUIRED_COLUMNS = {"Date", "Amount", "Description"}

def validate_csv(file, name):
    if not file.name.endswith('.csv'):
        st.error(f"❗ {name} file must be a CSV.")
        return None

    try:
        df = pd.read_csv(file)
    except Exception as e:
        st.error(f"❗ Failed to read {name} file: {e}")
        return None

    col_map = {}
    for col in df.columns:
        lower_col = col.lower()
        if 'date' in lower_col:
            col_map[col] = 'Date'
        elif 'amount' in lower_col:
            col_map[col] = 'Amount'
        elif 'description' in lower_col:
            col_map[col] = 'Description'
    df = df.rename(columns=col_map)

    if not REQUIRED_COLUMNS.issubset(set(df.columns)):
        missing = REQUIRED_COLUMNS - set(df.columns)
        st.error(f"❗ {name} file is missing required columns: {', '.join(missing)}")
        return None
    try:
        df['Date'] = df['Date'].apply(lambda x: parse_date(str(x), dayfirst=True))
    except Exception as e:
        st.error(f"❗ Failed to parse dates in {name} file: {e}")
        return None
    
    return df

bank_file = st.file_uploader("📥 Upload Bank Transactions CSV", type=['csv'])
ledger_file = st.file_uploader("📥 Upload Ledger Transactions CSV", type=['csv'])

if bank_file and ledger_file:
    bank_df = validate_csv(bank_file, "Bank")
    ledger_df = validate_csv(ledger_file, "Ledger")

    if bank_df is not None and ledger_df is not None:
        bank_df = preprocess(bank_df)
        ledger_df = preprocess(ledger_df)

        matched, unmatched_bank, unmatched_ledger = match_transactions(bank_df, ledger_df)

        st.subheader("✅ Matched Transactions")
        st.dataframe(pd.DataFrame(matched))

        st.subheader("❌ Unmatched Bank Transactions")
        st.dataframe(pd.DataFrame(unmatched_bank))

        st.subheader("❌ Unmatched Ledger Transactions")
        st.dataframe(pd.DataFrame(unmatched_ledger))