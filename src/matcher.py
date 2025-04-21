import pandas as pd
from rapidfuzz import fuzz
from dateutil.parser import parse
from datetime import timedelta
import numpy as np
from src.utils import clean_text, load_config

config = load_config()

AMOUNT_TOL = config['amount_tolerance']
DATE_DIFF = config['allowed_date_diff_days']
SIM_THRESHOLD = config['similarity_threshold']

def match_transactions(bank_df, ledger_df):
    
    matched = []
    unmatched_bank = []
    
    unmatched_ledger = ledger_df.copy()
    
    bank_matched_indices = set()
    
    for idx_bank, bank_row in bank_df.iterrows():
        match_found = False
        best_match_idx = None
        best_match_score = float('inf')
        best_match_reason = "No match found"
        
        for idx_ledger, ledger_row in unmatched_ledger.iterrows():
            amount_diff = abs(bank_row['Amount'] - ledger_row['Amount'])
            amount_close = amount_diff <= AMOUNT_TOL
            
            date_diff = abs((bank_row['Date'] - ledger_row['Date']).days)
            date_close = date_diff <= DATE_DIFF
            
            desc_sim = fuzz.token_sort_ratio(
                clean_text(bank_row['Description']), 
                clean_text(ledger_row['Description'])
            )
            desc_match = desc_sim >= SIM_THRESHOLD
            
            if amount_close and date_close and desc_match:
                bank_data = bank_row.to_dict()
                ledger_data = ledger_row.to_dict()
                
                if isinstance(bank_data['Date'], pd.Timestamp):
                    bank_data['Date'] = bank_data['Date'].strftime('%Y-%m-%d')
                if isinstance(ledger_data['Date'], pd.Timestamp):
                    ledger_data['Date'] = ledger_data['Date'].strftime('%Y-%m-%d')
                
                matched.append({
                    "bank": bank_data,
                    "ledger": ledger_data,
                    "confidence": desc_sim
                })
                
                best_match_idx = idx_ledger
                match_found = True
                bank_matched_indices.add(idx_bank)
                break
            
            match_score = amount_diff * 2 + date_diff + (100 - desc_sim) * 0.5
            
            if match_score < best_match_score:
                best_match_score = match_score
                best_match_idx = idx_ledger
                
                reasons = []
                if not amount_close:
                    reasons.append(f"Amount differs: Bank {bank_row['Amount']:.2f}, Ledger {ledger_row['Amount']:.2f}")
                if not date_close:
                    reasons.append(f"Date differs by {date_diff} days")
                if not desc_match:
                    reasons.append(f"Description similarity {desc_sim:.0f}% below threshold {SIM_THRESHOLD}%")
                
                best_match_reason = "; ".join(reasons)
        
        if match_found and best_match_idx is not None:
            unmatched_ledger = unmatched_ledger.drop(best_match_idx)
        
        if not match_found:
            bank_row_dict = bank_row.to_dict()
            if isinstance(bank_row_dict['Date'], pd.Timestamp):
                bank_row_dict['Date'] = bank_row_dict['Date'].strftime('%Y-%m-%d')
            bank_row_dict["reason"] = best_match_reason
            unmatched_bank.append(bank_row_dict)
    
    unmatched_ledger_dicts = []
    for idx_ledger, ledger_row in unmatched_ledger.iterrows():
        best_reason = "No similar bank transaction found"
        best_match_score = float('inf')
        
        for idx_bank, bank_row in bank_df.iterrows():
            if idx_bank in bank_matched_indices:
                continue
            
            amount_diff = abs(bank_row['Amount'] - ledger_row['Amount'])
            date_diff = abs((bank_row['Date'] - ledger_row['Date']).days)
            desc_sim = fuzz.token_sort_ratio(
                clean_text(bank_row['Description']), 
                clean_text(ledger_row['Description'])
            )
            
            match_score = amount_diff * 2 + date_diff + (100 - desc_sim) * 0.5
            
            if match_score < best_match_score:
                best_match_score = best_match_score
                
                if amount_diff <= AMOUNT_TOL * 5 or date_diff <= DATE_DIFF * 2 or desc_sim >= 50:
                    reasons = []
                    if amount_diff > AMOUNT_TOL:
                        reasons.append(f"Amount differs: Ledger {ledger_row['Amount']:.2f}, Bank {bank_row['Amount']:.2f}")
                    if date_diff > DATE_DIFF:
                        reasons.append(f"Date differs by {date_diff} days")
                    if desc_sim < SIM_THRESHOLD:
                        reasons.append(f"Description similarity {desc_sim:.0f}% below threshold {SIM_THRESHOLD}%")
                    
                    best_reason = "; ".join(reasons) if reasons else "Close match exists but didn't meet all criteria"
        
        row_dict = ledger_row.to_dict()
        if isinstance(row_dict['Date'], pd.Timestamp):
            row_dict['Date'] = row_dict['Date'].strftime('%Y-%m-%d')
        row_dict["reason"] = best_reason
        unmatched_ledger_dicts.append(row_dict)
    
    return matched, unmatched_bank, unmatched_ledger_dicts