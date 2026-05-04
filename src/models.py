from pydantic import BaseModel, field_validator
from datetime import date, datetime
from typing import Union

class TransactionRaw(BaseModel):
    """ Transactions validation from csv for db """
    date: date
    description: str
    amount: float
    category: str | None = None      # before categorization
  
    @field_validator("amount")
    @classmethod
    def valid_amount(cls, v: float):
        if v <= 0:
            raise ValueError("Amount cant be less than or equal to 0")
        return v
        
class CSVRow(BaseModel):
    """ Handling data types which come from csv file """
    date: str
    description: str
    amount: str
    
    @field_validator("amount", mode="before")
    @classmethod
    def handle_types_of_csv(cls, v: Union[str, float, int]):
        if isinstance(v, str):
            # Remove spaces and comma's with dot's to properly turn it to float type
            v = v.replace("\xa0", "").replace(" ", "").replace(",", "")
        return v
    
    @field_validator("date", mode="before")
    @classmethod
    def handle_date(cls, v: str):
        # Try different types of date
        for fmt in ["%Y-%m-%d", "%d-%b-%Y", "%d/%m/%Y", "%m/%d/%Y"]:
            try:
                return datetime.strptime(v, fmt).date().isoformat()
            except ValueError:
                continue
        raise ValueError(f"Cannot parse date: {v}")
            
class AI_Categorizer_Response(BaseModel):
    """ Handle AI response """
    transaction_id: int
    category: str
