# Reconciliation-Logic-MVP

Reconciliation Logic MVP ---> Match transactions between bank statements and ledger records using amount, date, and description similarity.

Features:

- Fuzzy match on descriptions (RapidFuzz), 
- Amount & date tolerance-based matching,
- Clear unmatched reasons.

Setup:

- git clone Reconciliation-Logic-MVP
- cd Reconciliation-Logic-MVP
- python3 -m venv Reconciliation-Logic-MVP
- source Reconciliation-Logic-MVP/bin/activate
- pip install -r requirements.txt
- streamlit run ui.py  #run this cmd to get the url on the browser.

Output:

- csv files in output dir for match and umatch,
- matched: list of matched records,
- unmatched_bank: bank entries with mismatch reasons,
- unmatched_ledger: ledger entries with mismatch reason.
