import re
import yaml
import pandas as pd
from dateutil.parser import parse

def normalize_columns(df):
    col_map = {}
    for col in df.columns:
        lower_col = col.lower()
        if 'amount' in lower_col:
            col_map[col] = 'Amount'
        elif 'date' in lower_col:
            col_map[col] = 'Date'
        elif 'description' in lower_col:
            col_map[col] = 'Description'
        elif 'id' in lower_col:
            col_map[col] = 'Transaction ID'
    df = df.rename(columns=col_map)

    # Ensure required columns exist
    required_cols = ['Amount', 'Date', 'Description']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: '{col}' in the uploaded file.")
    return df


def clean_text(text):
    return re.sub(r'[^a-zA-Z0-9 ]', '', str(text)).lower().strip()

def load_config(path='src/config.yaml'):
    with open(path, 'r') as file:
        return yaml.safe_load(file)

def preprocess(df):
    df['Amount'] = df['Amount'].astype(float)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Description'] = df['Description'].astype(str)
    return df