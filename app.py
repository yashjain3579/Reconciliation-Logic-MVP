from fastapi import FastAPI, UploadFile, File
import pandas as pd
from src.matcher import match_transactions
from src.utils import preprocess

app = FastAPI()

@app.post("/reconcile")
async def reconcile(bank: UploadFile = File(...), ledger: UploadFile = File(...)):
    bank_df = pd.read_csv(bank.file)
    ledger_df = pd.read_csv(ledger.file)

    bank_df = preprocess(bank_df)
    ledger_df = preprocess(ledger_df)

    matched, unmatched_bank, unmatched_ledger = match_transactions(bank_df, ledger_df)
    return {
        "matched": matched,
        "unmatched_bank": unmatched_bank,
        "unmatched_ledger": unmatched_ledger
    }