from openai import AsyncOpenAI, AuthenticationError, RateLimitError
from asyncpg import Pool
import logging
import json
from pydantic import ValidationError
from src.models import AI_Categorizer_Response
from src.database import get_transactions_withoutCat, update_TransactionCategory
from src.utils.server_utils import async_retry
from decimal import Decimal 

system_promt = """
You are a financial transaction categorizer. You will receive a list of bank transactions and must categorize each one.
Available categories: food, transport, entertainment, health, shopping, utilities, travel, education, other.

Rules:
- Return ONLY a JSON array, no explanations or markdown
- Each object must have exactly two fields: "transaction_id" and "category"
- Use only categories from the list above
- If unclear use "other"

Example output:
[{"transaction_id": 1, "category": "food"},
{"transaction_id": 2, "category": "transport"}]
"""

def serialize_row(row):
    result = {}
    for k, v in dict(row).items():
        if hasattr(v, "isoformat"):
            result[k] = v.isoformat()
        elif isinstance(v, Decimal):
            result[k] = float(v)
        else:
            result[k] = v
    return result

@async_retry(retries=3, delay=4)
async def get_AIResponse(client: AsyncOpenAI, conn_pool: Pool):
    try:
        transactions = await get_transactions_withoutCat(conn_pool)
        resp = await client.chat.completions.create(
            model="llama-3.3-70b-versatile", messages=[
                {"role": "system", "content": system_promt},
                {"role": "user", "content": json.dumps([serialize_row(row) for row in transactions])} # type: ignore
        ]
    )
        content = resp.choices[0].message.content
        if not content:
            raise ValueError("Empty response from AI")
        
        resp_content = json.loads(content)    
        
        for row in resp_content:
            cat = AI_Categorizer_Response.model_validate(row)
            await update_TransactionCategory(conn_pool, cat.category, cat.transaction_id) 
        
    except RateLimitError:
        logging.error("Rate limit exceeded")
        raise
    except AuthenticationError:
        logging.error("AI Authentication error occurred")
        raise
    except ValidationError as e:
        for error in e.errors():
            logging.error(f"[{error['type']}]: [{error['msg']}]")
        raise
    except Exception as e:
        logging.error(f"LLM Error: [{e}]")
        raise
    
