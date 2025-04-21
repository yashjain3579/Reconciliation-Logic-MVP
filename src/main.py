import pandas as pd
from src.matcher import match_transactions
from src.utils import preprocess

bank_df = pd.read_csv('data/bank_transactions.csv')
ledger_df = pd.read_csv('data/ledger_transactions.csv')


bank_df = preprocess(bank_df)
ledger_df = preprocess(ledger_df)

matched, unmatched_bank, unmatched_ledger = match_transactions(bank_df, ledger_df)

# Save outputs
matched_out = []
for m in matched:
    out = {
        'bank_date': m['bank']['Date'],
        'bank_amount': m['bank']['Amount'],
        'bank_desc': m['bank']['Description'],
        'ledger_date': m['ledger']['Date'],
        'ledger_amount': m['ledger']['Amount'],
        'ledger_desc': m['ledger']['Description'],
        'confidence': m['confidence']
    }
    matched_out.append(out)

pd.DataFrame(matched_out).to_csv('../output/matched.csv', index=False)
pd.DataFrame(unmatched_bank).to_csv('../output/unmatched_bank.csv', index=False)
pd.DataFrame(unmatched_ledger).to_csv('../output/unmatched_ledger.csv', index=False)