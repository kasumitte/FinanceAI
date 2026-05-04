import csv
from src.database import save_transaction
from src.models import CSVRow, TransactionRaw
from pydantic import ValidationError
from asyncpg import Pool
import logging
from pathlib import Path

def read_csv(filepath: Path):
    rows = [] 
    with open(filepath, 'r', newline='', encoding='utf-8') as f:
        # Define the 'dialect' of the file
        sample = f.read(1024)
        f.seek(0)
        sniffer = csv.Sniffer()
        dialect = sniffer.sniff(sample) 
        reader = csv.DictReader(f, dialect=dialect)
        
        for row in reader:
            rows.append(row)      
    
    return rows

async def import_transactions(conn_pool: Pool, filepath: Path):
    logging.info("Reading file...")
    csv_rows = read_csv(filepath)
    
    error_count = 0
    for line in csv_rows:
        try:
            # Normalize the given data firstly for better formatting
            deposits = line.get("Deposits") or line.get("deposits") or "0"
            withdrawls = line.get("Withdrawls") or line.get("withdrawls") or "0"
            
            if float(deposits.replace(",", "")) > 0:
                amount = deposits
            elif float(withdrawls.replace(",", "")) > 0:
                amount = withdrawls
            else:
                amount = line.get("amount") or line.get("Amount") or line.get("Balance") or line.get("balance") or "0"
            
            normalized = {
                "date": line.get("date") or line.get("Date"),
                "description": line.get("Description") or line.get("description"),
                "amount": amount
            }
            csv_data_raw = CSVRow.model_validate(normalized)
            valid_csv = TransactionRaw.model_validate(csv_data_raw.model_dump())
            
            await save_transaction(conn_pool, valid_csv.description, valid_csv.amount, valid_csv.date)    
        
        except ValidationError as e:
            logging.error(f"Validation error occurred while reading: [{line}]")
            logging.error(f"Error: {e.errors()}")
            error_count += 1
            continue
    
    return True if error_count == 0 else False
